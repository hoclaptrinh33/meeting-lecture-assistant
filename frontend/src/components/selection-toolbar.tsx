"use client";

import React from "react";
import { HighlightingIcon, CheckSquare, Sparkles } from "lucide-react";

interface SelectionToolbarProps {
  position: { top: number; left: number } | null;
  onHighlight: () => void;
  onCreateActionItem: () => void;
}

export function SelectionToolbar({ position, onHighlight, onCreateActionItem }: SelectionToolbarProps) {
  if (!position) return null;

  return (
    <div
      style={{ top: `${position.top}px`, left: `${position.left}px` }}
      className="fixed z-50 transform -translate-x-1/2 -translate-y-full mb-2 bg-gray-900 text-white rounded-lg shadow-xl px-2 py-1 flex items-center gap-1 text-xs"
    >
      <button
        onClick={onHighlight}
        className="px-2 py-1.5 hover:bg-gray-800 rounded flex items-center gap-1.5 transition-colors"
      >
        <span>Đánh dấu</span>
      </button>

      <div className="w-px h-3 bg-gray-700" />

      <button
        onClick={onCreateActionItem}
        className="px-2 py-1.5 hover:bg-gray-800 rounded flex items-center gap-1.5 transition-colors"
      >
        <CheckSquare className="w-3.5 h-3.5 text-blue-400" />
        <span>Giao việc</span>
      </button>
    </div>
  );
}
