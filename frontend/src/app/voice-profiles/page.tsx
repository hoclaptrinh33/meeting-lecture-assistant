"use client";

import React from "react";
import { Mic } from "lucide-react";

export default function VoiceProfilesPage() {
  /**
   * TODO: Triển khai quản lý hồ sơ giọng nói:
   * - Form đăng ký: Tên người nói + File ghi âm mẫu (10s - 60s)
   * - Gọi POST /api/voice-profiles
   * - Danh sách hồ sơ đã lưu (GET /api/voice-profiles)
   * - Xóa hồ sơ (DELETE /api/voice-profiles/{id})
   */
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Hồ sơ giọng nói (Voice Profiles)</h1>
        <p className="text-sm text-gray-500 mt-1">
          Lưu trữ mẫu đặc trưng giọng nói để tự động nhận dạng và gán tên thành viên sau bước Diarization.
        </p>
      </div>

      <div className="bg-white p-8 rounded-xl border border-gray-100 shadow-sm text-center text-gray-400 text-sm flex flex-col items-center gap-2">
        <Mic className="w-8 h-8 text-gray-300" />
        <span>Khung hồ sơ giọng nói - TODO: Triển khai form upload mẫu giọng và danh sách profile.</span>
      </div>
    </div>
  );
}
