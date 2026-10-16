"use client";

import React from "react";
import { Radio } from "lucide-react";

interface LiveTranscriptProps {
  onSessionFinalized?: (jobId: string) => void;
}

export function LiveTranscript({ onSessionFinalized }: LiveTranscriptProps) {
  /**
   * TODO: Triển khai giao diện thu âm trực tiếp (PT2):
   * - Nút bắt đầu / dừng phiên nghe (POST /api/live/sessions, POST /api/live/sessions/{id}/stop)
   * - Tùy chọn nguồn: Mic hoặc Tab/Màn hình
   * - LiveAudioCapture đẩy stream PCM float32 qua WebSocket
   * - TypewriterQueue hiển thị chữ nháp chạy thời gian thực
   */
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2 text-gray-900 font-bold text-lg">
        <Radio className="w-5 h-5 text-red-500" />
        <span>Thu âm trực tiếp (LiveTranscript)</span>
      </div>
      <p className="text-sm text-gray-500">
        Khung nghe trực tiếp PT2 - TODO: Gắn LiveAudioCapture và WebSocket PCM stream.
      </p>
    </div>
  );
}
