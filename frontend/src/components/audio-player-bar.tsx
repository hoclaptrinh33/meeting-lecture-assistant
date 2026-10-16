"use client";

import React from "react";
import { Play } from "lucide-react";

interface AudioPlayerBarProps {
  audioUrl?: string;
  currentTime?: number;
  onTimeUpdate?: (timeMs: number) => void;
  onSeek?: (timeMs: number) => void;
}

export function AudioPlayerBar({ audioUrl, currentTime, onTimeUpdate, onSeek }: AudioPlayerBarProps) {
  /**
   * TODO: Triển khai thanh phát âm thanh:
   * - Thẻ <audio> phát file từ media token
   * - Nút Play/Pause, tua 5s, thanh scrubber
   * - Tùy chỉnh tốc độ phát (1x, 1.25x, 1.5x)
   * - Đồng bộ mốc currentTime với transcript
   */
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-3 shadow-lg z-30">
      <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <Play className="w-4 h-4 text-blue-600" />
          <span>Khung phát âm thanh (AudioPlayerBar) - TODO: Gắn player audio</span>
        </div>
      </div>
    </div>
  );
}
