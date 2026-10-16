import datetime
import uuid

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Job, LlmRun, Segment
from app.services.exporter import format_ms_to_clock
from app.services.llm_client import LlmClient
from app.worker import celery_app


@celery_app.task(bind=True, name="app.tasks.run_llm")
def run_llm(self, run_id_str: str):
    """Xử lý các tác vụ LLM (clean transcript, summarize) trên hàng IO."""
    run_id = uuid.UUID(run_id_str)
    db = SessionLocal()

    try:
        run = db.query(LlmRun).filter(LlmRun.id == run_id).first()
        if not run:
            return

        run.status = "running"
        run.model_name = settings.LLM_MODEL
        db.commit()

        job_id = run.job_id
        segments = (
            db.query(Segment)
            .filter(Segment.job_id == job_id, Segment.pass_number == 2)
            .order_by(Segment.position)
            .all()
        )

        client = LlmClient()

        if run.task == "clean":
            raw_data = [{"position": s.position, "text_raw": s.text_raw} for s in segments]
            cleaned_items = client.clean_transcript(raw_data)
            cleaned_map = {item["position"]: item["text_cleaned"] for item in cleaned_items}

            for s in segments:
                if s.position in cleaned_map:
                    s.text_cleaned = cleaned_map[s.position]

            run.status = "done"
            run.finished_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

        elif run.task == "summarize":
            # Ghép chuỗi transcript có mốc thời gian
            lines = []
            for s in segments:
                clock = format_ms_to_clock(s.start_ms)
                spk = s.speaker_label or "Người nói"
                text = s.text_edited or s.text_cleaned or s.text_raw
                lines.append(f"[{clock}] {spk}: {text}")

            transcript_full = "\n".join(lines)
            template = run.template or "meeting"
            summary_res = client.summarize_transcript(transcript_full, template=template)

            run.result = summary_res
            run.status = "done"
            run.finished_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

    except Exception as e:
        if run:
            run.status = "failed"
            run.error_code = "llm_error"
            run.error_message = str(e)
            run.finished_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
        raise e
    finally:
        db.close()
