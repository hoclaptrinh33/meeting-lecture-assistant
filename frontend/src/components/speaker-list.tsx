"use client";

import React from "react";
import { Users } from "lucide-react";

interface SpeakerItem {
  speaker_label: string;
  display_name: string;
  source: string;
}

interface SpeakerListProps {
  jobId: string;
  speakers?: SpeakerItem[];
  onSpeakerUpdated?: (label: string, newName: string) => void;
}

export function SpeakerList({ jobId, speakers, onSpeakerUpdated }: SpeakerListProps) {
  /**
   * TODO: Triển khai danh sách người nói:
   * - Hiển thị nhãn SPEAKER_XX và display_name
   * - Đổi tên trực tiếp và gọi PATCH /api/jobs/{job_id}/speakers/{speaker_label}
   */
  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm mb-6 flex items-center gap-2 text-sm text-gray-500">
      <Users className="w-4 h-4 text-gray-400" />
      <span>Khung danh sách người nói (SpeakerList) - TODO: Gắn danh sách và đổi tên</span>
    </div>
  );
}
