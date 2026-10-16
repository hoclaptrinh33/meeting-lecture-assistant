"use client";

import React from "react";
import { FileText } from "lucide-react";

interface WordItem {
  position: number;
  text: string;
  start_ms: number;
  end_ms: number;
  speaker_label?: string;
}

interface SegmentItem {
  id: string;
  pass: number;
  position: number;
  start_ms: number;
  end_ms: number;
  text_raw: string;
  text_cleaned?: string;
  text_edited?: string;
  speaker_label?: string;
  words?: WordItem[];
}

interface TranscriptLayoutProps {
  jobId: string;
  segments?: SegmentItem[];
  speakersMap?: Record<string, string>;
  currentTime?: number;
  onSeek?: (timeMs: number) => void;
  onSegmentUpdated?: (position: number, newText: string) => void;
}

export function TranscriptLayout({
  jobId,
  segments,
  speakersMap,
  currentTime,
  onSeek,
  onSegmentUpdated,
}: TranscriptLayoutProps) {
  /**
   * TODO: Triển khai khung hiển thị transcript:
   * - Danh sách câu hội thoại (SegmentItem) kèm mốc thời gian
   * - Highlight câu/từ đang phát theo currentTime
   * - Chuyển đổi hiển thị giữa text_raw, text_cleaned, text_edited
   * - Cho phép sửa câu (PATCH /api/jobs/{job_id}/segments/{position})
   * - Bắt sự kiện bôi đen chữ để hiện SelectionToolbar
   */
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2 text-gray-800 font-bold text-lg">
        <FileText className="w-5 h-5 text-blue-600" />
        <span>Văn bản nhận dạng (TranscriptLayout)</span>
      </div>
      <p className="text-sm text-gray-500">
        Khung hiển thị transcript - TODO: Render danh sách câu, từ và đồng bộ trình phát âm thanh.
      </p>
    </div>
  );
}
