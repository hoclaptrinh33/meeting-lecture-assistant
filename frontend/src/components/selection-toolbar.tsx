"use client";

import React from "react";

interface SelectionToolbarProps {
  position?: { top: number; left: number } | null;
  onHighlight?: () => void;
  onCreateActionItem?: () => void;
}

export function SelectionToolbar({ position, onHighlight, onCreateActionItem }: SelectionToolbarProps) {
  /**
   * TODO: Triển khai toolbar nổi khi người dùng bôi đen chữ trong transcript:
   * - Nút "Đánh dấu" (POST /api/jobs/{job_id}/highlights)
   * - Nút "Giao việc" (POST /api/jobs/{job_id}/action-items)
   */
  if (!position) return null;
  return null;
}
