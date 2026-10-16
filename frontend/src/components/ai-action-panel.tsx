"use client";

import React from "react";
import { Sparkles } from "lucide-react";

interface AiActionPanelProps {
  jobId: string;
  onRefreshTranscript?: () => void;
}

export function AiActionPanel({ jobId, onRefreshTranscript }: AiActionPanelProps) {
  /**
   * TODO: Triển khai bảng điều khiển AI hậu kỳ:
   * - Nút "Làm sạch văn bản" (POST /api/jobs/{job_id}/llm/clean)
   * - Nút "Tóm tắt cuộc họp" (POST /api/jobs/{job_id}/llm/summarize - template: meeting)
   * - Nút "Ghi chú bài giảng" (POST /api/jobs/{job_id}/llm/summarize - template: lecture)
   * - Nút "Xuất file" (POST /api/jobs/{job_id}/exports - md, docx, pdf, srt, vtt)
   */
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm mb-6 flex items-center justify-between text-sm text-gray-500">
      <div className="flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-indigo-500" />
        <span>Khung trợ lý hậu kỳ AI (AiActionPanel) - TODO: Gắn các nút Clean, Summarize, Export</span>
      </div>
    </div>
  );
}
