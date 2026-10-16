"use client";

import React, { use } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { AiActionPanel } from "@/components/ai-action-panel";
import { SpeakerList } from "@/components/speaker-list";
import { TranscriptLayout } from "@/components/transcript-layout";
import { AudioPlayerBar } from "@/components/audio-player-bar";

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const jobId = resolvedParams.id;

  /**
   * TODO: Triển khai không gian làm việc chi tiết của Job:
   * 1. Gọi api.getJob(jobId)
   * 2. Nếu job chưa xong: kết nối SSE (/api/jobs/{id}/events) theo dõi stage progress
   * 3. Khi job ready: tải transcript (api.getTranscript) và lấy media token phát audio
   * 4. Gắn kết AiActionPanel, SpeakerList, TranscriptLayout và AudioPlayerBar
   */
  return (
    <div className="space-y-6 pb-24">
      <div className="flex items-center gap-4">
        <Link href="/jobs" className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chi tiết công việc</h1>
          <p className="text-xs text-gray-400 mt-0.5">Mã job: {jobId}</p>
        </div>
      </div>

      <AiActionPanel jobId={jobId} />
      <SpeakerList jobId={jobId} />
      <TranscriptLayout jobId={jobId} />
      <AudioPlayerBar />
    </div>
  );
}
