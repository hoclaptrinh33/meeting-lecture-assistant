"use client";

import React, { use, useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { AiActionPanel } from "@/components/ai-action-panel";
import { SpeakerList } from "@/components/speaker-list";
import { TranscriptLayout } from "@/components/transcript-layout";
import { AudioPlayerBar } from "@/components/audio-player-bar";
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const jobId = resolvedParams.id;
  const router = useRouter();

  const [job, setJob] = useState<any>(null);
  const [segments, setSegments] = useState<any[]>([]);
  const [speakers, setSpeakers] = useState<any[]>([]);
  const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [stageProgress, setStageProgress] = useState<{ stage: string; percent: number }>({
    stage: "Đang khởi tạo",
    percent: 0,
  });

  const loadJobData = async () => {
    try {
      const j = await api.getJob(jobId);
      setJob(j);

      if (j.status === "ready") {
        const t = await api.getTranscript(jobId);
        setSegments(t.segments || []);
        setSpeakers(t.speakers || []);

        try {
          const media = await api.getMediaToken(jobId);
          setAudioUrl(`/api/jobs/${jobId}/audio?token=${media.token}`);
        } catch {
          // ignore
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobData();

    // Lắng nghe SSE nếu job chưa kết thúc
    let eventSource: EventSource | null = null;
    if (job?.status && !["ready", "failed", "cancelled"].includes(job.status)) {
      eventSource = new EventSource(`/api/jobs/${jobId}/events`);

      eventSource.addEventListener("stage_changed", (e: any) => {
        try {
          const data = JSON.parse(e.data);
          setStageProgress({ stage: data.stage, percent: data.percent || 0 });
        } catch {}
      });

      eventSource.addEventListener("finished", () => {
        loadJobData();
        eventSource?.close();
      });

      eventSource.addEventListener("error", () => {
        loadJobData();
      });
    }

    return () => {
      if (eventSource) eventSource.close();
    };
  }, [jobId, job?.status]);

  const speakersMap = React.useMemo(() => {
    const map: Record<string, string> = {};
    for (const spk of speakers) {
      map[spk.speaker_label] = spk.display_name;
    }
    return map;
  }, [speakers]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-20 text-gray-500">
        <p>Không tìm thấy thông tin job này.</p>
        <Link href="/jobs" className="text-blue-600 font-medium hover:underline mt-2 inline-block">
          Quay lại danh sách
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-24">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/jobs" className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Mã job: {job.id} • Nguồn: {job.source === "upload" ? "Tải file" : "Nghe trực tiếp"}
          </p>
        </div>
      </div>

      {/* Processing State with SSE Progress */}
      {job.status !== "ready" && job.status !== "failed" && (
        <div className="bg-white p-8 rounded-xl border border-gray-100 shadow-sm text-center space-y-4">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600 mx-auto" />
          <div>
            <h3 className="font-bold text-gray-800 text-lg">Đang tiến hành xử lý âm thanh...</h3>
            <p className="text-sm text-gray-500 mt-1 capitalize">Giai đoạn: {stageProgress.stage}</p>
          </div>
          <div className="max-w-md mx-auto bg-gray-100 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(10, stageProgress.percent)}%` }}
            />
          </div>
        </div>
      )}

      {job.status === "failed" && (
        <div className="bg-red-50 p-6 rounded-xl border border-red-200 text-red-800 space-y-2">
          <div className="flex items-center gap-2 font-bold">
            <AlertCircle className="w-5 h-5" />
            <span>Xử lý job thất bại</span>
          </div>
          <p className="text-sm">{job.error_message || "Đã xảy ra lỗi không xác định trong quá trình nhận dạng."}</p>
        </div>
      )}

      {/* Ready Workspace */}
      {job.status === "ready" && (
        <>
          <AiActionPanel jobId={jobId} onRefreshTranscript={loadJobData} />

          <SpeakerList
            jobId={jobId}
            speakers={speakers}
            onSpeakerUpdated={(lbl, newName) => {
              setSpeakers((prev) =>
                prev.map((s) => (s.speaker_label === lbl ? { ...s, display_name: newName } : s))
              );
            }}
          />

          <TranscriptLayout
            jobId={jobId}
            segments={segments}
            speakersMap={speakersMap}
            currentTime={currentTime}
            onSeek={(t) => setCurrentTime(t)}
            onSegmentUpdated={(pos, text) => {
              setSegments((prev) =>
                prev.map((s) => (s.position === pos ? { ...s, text_edited: text } : s))
              );
            }}
          />

          {audioUrl && (
            <AudioPlayerBar
              audioUrl={audioUrl}
              currentTime={currentTime}
              onTimeUpdate={(t) => setCurrentTime(t)}
              onSeek={(t) => setCurrentTime(t)}
            />
          )}
        </>
      )}
    </div>
  );
}
