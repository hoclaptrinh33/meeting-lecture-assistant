"use client";

import React from "react";
import { Upload } from "lucide-react";

interface AudioUploaderProps {
  onUploaded?: (jobId: string) => void;
}

export function AudioUploader({ onUploaded }: AudioUploaderProps) {
  /**
   * TODO: Triển khai form upload file:
   * - Kéo thả file audio/video
   * - Nhập tiêu đề, từ vựng chuyên ngành, số người nói
   * - Nén Opus qua ClientFfmpegCompressor
   * - Gọi api.createJob
   */
  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-xl border border-dashed border-gray-300 text-center space-y-4">
      <Upload className="w-12 h-12 text-gray-400 mx-auto" />
      <div>
        <h3 className="font-bold text-gray-900 text-lg">Khung tải lên file ghi âm (AudioUploader)</h3>
        <p className="text-sm text-gray-500 mt-1">TODO: Gắn logic chọn file, nén Opus và POST /api/jobs</p>
      </div>
    </div>
  );
}
