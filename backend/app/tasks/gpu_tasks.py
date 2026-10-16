import datetime
import uuid
from typing import Any, Dict

from app.core.database import SessionLocal
from app.core.redis import sync_redis_client
from app.models import Job, JobEvent, Segment, SpeakerAlias, VoiceProfile, Word
from app.services.audio_processor import AudioProcessor
from app.services.diarization import DiarizationService
from app.services.gpu_lock import GpuLock
from app.services.speaker_align import SpeakerAligner
from app.services.stt_engine import SttEngine
from app.services.vad_chunker import VadChunker
from app.services.voice_profile import VoiceProfileService
from app.worker import celery_app


def emit_job_event(db, job_id: uuid.UUID, event_type: str, payload: Dict[str, Any]) -> None:
    """Ghi event vào DB và phát ra Redis channel."""
    # Lấy sequence tiếp theo
    last_seq = db.query(JobEvent.seq).filter(JobEvent.job_id == job_id).order_by(JobEvent.seq.desc()).first()
    seq = (last_seq[0] + 1) if last_seq else 1

    event = JobEvent(
        job_id=job_id,
        seq=seq,
        event_type=event_type,
        payload=payload,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(event)
    db.commit()

    # Phát qua pub/sub
    channel = f"job:{str(job_id)}:events"
    import json
    msg = json.dumps({"seq": seq, "event": event_type, "data": payload})
    sync_redis_client.publish(channel, msg)


@celery_app.task(bind=True, name="app.tasks.transcribe_upload", max_retries=100)
def transcribe_upload(self, job_id_str: str):
    """Xử lý toàn bộ pipeline cho job tải file (PT1)."""
    job_id = uuid.UUID(job_id_str)
    db = SessionLocal()
    gpu_lock = GpuLock(owner_id=job_id_str)

    # 1. Thử lấy khóa GPU
    if not gpu_lock.acquire():
        # Trả lại slot Celery ngay và thử lại sau 5 giây
        db.close()
        raise self.retry(countdown=5)

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or job.status == "cancelled":
            gpu_lock.release()
            db.close()
            return

        # 2. Preprocessing
        job.status = "preprocessing"
        job.started_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        emit_job_event(db, job_id, "stage_changed", {"stage": "preprocessing", "percent": 10})

        # Chuẩn hóa âm thanh
        opus_path = AudioProcessor.normalize_to_canonical_opus(job.audio_path, job_id_str)
        job.audio_path = opus_path
        f32_path, pcm_data = AudioProcessor.create_pcm_f32_memmap(opus_path, job_id_str)
        duration_s = len(pcm_data) / 16000.0
        job.duration_ms = int(duration_s * 1000)
        db.commit()

        # 3. Transcribing
        job.status = "transcribing"
        db.commit()
        emit_job_event(db, job_id, "stage_changed", {"stage": "transcribing", "percent": 30})

        stt = SttEngine()
        # VAD & chunking
        chunks = VadChunker.chunk_audio([], duration_s)
        position = 0

        for chunk in chunks:
            chunk_audio = pcm_data[chunk.start_sample:chunk.end_sample]
            seg_results = stt.transcribe_audio_chunk(
                chunk_audio,
                time_offset_s=chunk.start_s,
                vocabulary=job.vocabulary,
            )
            for item in seg_results:
                segment_id = uuid.uuid4()
                segment = Segment(
                    id=segment_id,
                    job_id=job_id,
                    pass_number=2,
                    position=position,
                    start_ms=item["start_ms"],
                    end_ms=item["end_ms"],
                    text_raw=item["text_raw"],
                )
                db.add(segment)

                word_records = []
                for w_idx, w in enumerate(item.get("words", [])):
                    w_rec = Word(
                        id=uuid.uuid4(),
                        segment_id=segment_id,
                        position=w_idx,
                        text=w["text"],
                        start_ms=w["start_ms"],
                        end_ms=w["end_ms"],
                    )
                    word_records.append(w_rec)
                    db.add(w_rec)

                db.commit()
                emit_job_event(db, job_id, "segment_added", {
                    "pass": 2,
                    "position": position,
                    "start_ms": item["start_ms"],
                    "end_ms": item["end_ms"],
                    "text_raw": item["text_raw"],
                    "words": [{"text": w["text"], "start_ms": w["start_ms"], "end_ms": w["end_ms"]} for w in item.get("words", [])],
                })
                position += 1

        # 4. Giải phóng Whisper khỏi VRAM trước khi chạy Diarization!
        stt.unload_model()

        # 5. Diarizing
        job.status = "diarizing"
        db.commit()
        emit_job_event(db, job_id, "stage_changed", {"stage": "diarizing", "percent": 75})

        diarizer = DiarizationService()
        diar_result = diarizer.diarize_audio(opus_path, num_speakers=job.num_speakers)
        job.diarization_device = diar_result.get("device")
        if diar_result.get("warning"):
            warnings = list(job.warnings or [])
            warnings.append({"code": "diarization_warning", "message": diar_result["warning"]})
            job.warnings = warnings
            emit_job_event(db, job_id, "warning", {"code": "diarization_warning", "message": diar_result["warning"]})
        db.commit()

        # 6. Align speaker labels
        turns = diar_result.get("turns", [])
        if turns:
            segments_db = db.query(Segment).filter(Segment.job_id == job_id, Segment.pass_number == 2).order_by(Segment.position).all()
            for s in segments_db:
                words_db = db.query(Word).filter(Word.segment_id == s.id).order_by(Word.position).all()
                seg_dict = {
                    "start_ms": s.start_ms,
                    "end_ms": s.end_ms,
                    "words": [{"start_ms": w.start_ms, "end_ms": w.end_ms} for w in words_db],
                }
                aligned = SpeakerAligner.align_words_and_segments([seg_dict], turns)[0]
                s.speaker_label = aligned.get("speaker_label")
                for w_rec, w_align in zip(words_db, aligned.get("words", [])):
                    w_rec.speaker_label = w_align.get("speaker_label")
                db.commit()

                emit_job_event(db, job_id, "words_updated", {
                    "pass": 2,
                    "position": s.position,
                    "words": [{"position": w.position, "text": w.text, "start_ms": w.start_ms, "end_ms": w.end_ms, "speaker_label": w.speaker_label} for w in words_db],
                })
                if s.speaker_label:
                    emit_job_event(db, job_id, "speaker_assigned", {
                        "pass": 2,
                        "position": s.position,
                        "speaker_label": s.speaker_label,
                    })

        # 7. Match voice profiles
        user_profiles = db.query(VoiceProfile).filter(VoiceProfile.user_id == job.user_id, VoiceProfile.status == "ready").all()
        # Create default speaker aliases
        speakers = db.query(Segment.speaker_label).filter(Segment.job_id == job_id).distinct().all()
        for spk in speakers:
            lbl = spk[0]
            if lbl:
                alias = SpeakerAlias(
                    job_id=job_id,
                    speaker_label=lbl,
                    display_name=f"Người nói {lbl.replace('SPEAKER_', '')}",
                    source="manual",
                )
                db.merge(alias)
        db.commit()

        # 8. Hoàn tất job
        AudioProcessor.cleanup_temp_f32(job_id_str)
        job.status = "ready"
        job.finished_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        emit_job_event(db, job_id, "finished", {"duration_ms": job.duration_ms, "status": "ready"})

    except Exception as e:
        AudioProcessor.cleanup_temp_f32(job_id_str)
        if job:
            job.status = "failed"
            job.error_code = "processing_error"
            job.error_message = str(e)
            job.finished_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            emit_job_event(db, job_id, "error", {"code": "processing_error", "message": str(e)})
        raise e
    finally:
        gpu_lock.release()
        db.close()


@celery_app.task(bind=True, name="app.tasks.run_live_session")
def run_live_session(self, session_id_str: str):
    """Xử lý phiên nghe trực tiếp PT2."""
    pass


@celery_app.task(bind=True, name="app.tasks.enroll_voice")
def enroll_voice(self, profile_id_str: str):
    """Trích xuất voice embedding và đăng ký hồ sơ giọng nói."""
    pass
