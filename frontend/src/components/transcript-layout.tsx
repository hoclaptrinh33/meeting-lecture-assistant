"use client";

import React, { useState } from "react";
import { Clock, Edit3, Check, X, Bookmark, CheckSquare } from "lucide-react";
import { api } from "@/lib/api";
import { SelectionToolbar } from "@/components/selection-toolbar";

interface WordItem {
  position: number;
  text: string;
  start_ms: int;
  end_ms: int;
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
  segments: SegmentItem[];
  speakersMap: Record<string, string>;
  currentTime: number;
  onSeek: (timeMs: number) => void;
  onSegmentUpdated: (position: number, newText: string) => void;
}

export function TranscriptLayout({
  jobId,
  segments,
  speakersMap,
  currentTime,
  onSeek,
  onSegmentUpdated,
}: TranscriptLayoutProps) {
  const [viewMode, setViewMode] = useState<"auto" | "raw" | "cleaned">("auto");
  const [editingPos, setEditingPos] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [selectionPos, setSelectionPos] = useState<{ top: number; left: number } | null>(null);
  const [selectedRange, setSelectedRange] = useState<{ text: string; segment: SegmentItem } | null>(null);

  const formatClock = (ms: number) => {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
  };

  const getText = (s: SegmentItem) => {
    if (viewMode === "raw") return s.text_raw;
    if (viewMode === "cleaned") return s.text_cleaned || s.text_raw;
    return s.text_edited || s.text_cleaned || s.text_raw;
  };

  const handleTextSelection = (segment: SegmentItem) => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.toString().trim()) {
      setSelectionPos(null);
      setSelectedRange(null);
      return;
    }

    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    setSelectionPos({
      top: rect.top + window.scrollY,
      left: rect.left + rect.width / 2 + window.scrollX,
    });
    setSelectedRange({
      text: sel.toString().trim(),
      segment,
    });
  };

  const handleHighlight = async () => {
    if (!selectedRange) return;
    try {
      await api.createHighlight(jobId, {
        segment_id: selectedRange.segment.id,
        quote: selectedRange.text,
        start_ms: selectedRange.segment.start_ms,
        end_ms: selectedRange.segment.end_ms,
      });
      setSelectionPos(null);
      alert("Đã thêm đánh dấu thành công!");
    } catch (err: any) {
      alert("Lỗi đánh dấu: " + err.message);
    }
  };

  const handleCreateActionItem = async () => {
    if (!selectedRange) return;
    const task = prompt("Nội dung việc cần làm:", selectedRange.text);
    if (!task) return;
    const owner = prompt("Người phụ trách (tùy chọn):", "");
    const deadline = prompt("Hạn hoàn thành (tùy chọn):", "");

    try {
      await api.createActionItem(jobId, {
        segment_id: selectedRange.segment.id,
        task,
        owner: owner || "",
        deadline: deadline || "",
        start_ms: selectedRange.segment.start_ms,
      });
      setSelectionPos(null);
      alert("Đã tạo việc cần làm!");
    } catch (err: any) {
      alert("Lỗi tạo việc: " + err.message);
    }
  };

  const startEdit = (s: SegmentItem) => {
    setEditingPos(s.position);
    setEditText(getText(s));
  };

  const saveEdit = async (s: SegmentItem) => {
    try {
      await api.patchSegment(jobId, s.position, editText);
      onSegmentUpdated(s.position, editText);
      setEditingPos(null);
    } catch (err: any) {
      alert("Lỗi lưu sửa đổi: " + err.message);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm relative">
      <SelectionToolbar
        position={selectionPos}
        onHighlight={handleHighlight}
        onCreateActionItem={handleCreateActionItem}
      />

      {/* Header & View toggle */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-100 mb-6">
        <h2 className="text-lg font-bold text-gray-900">Văn bản nhận dạng (Transcript)</h2>
        <div className="flex items-center bg-gray-100 p-1 rounded-lg text-xs">
          <button
            onClick={() => setViewMode("auto")}
            className={`px-3 py-1 rounded-md font-medium transition-colors ${
              viewMode === "auto" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
            }`}
          >
            Bản chuẩn
          </button>
          <button
            onClick={() => setViewMode("cleaned")}
            className={`px-3 py-1 rounded-md font-medium transition-colors ${
              viewMode === "cleaned" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
            }`}
          >
            Đã làm sạch
          </button>
          <button
            onClick={() => setViewMode("raw")}
            className={`px-3 py-1 rounded-md font-medium transition-colors ${
              viewMode === "raw" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
            }`}
          >
            Gốc (Raw)
          </button>
        </div>
      </div>

      {/* Segments stream */}
      <div className="space-y-6">
        {segments.map((seg) => {
          const isCurrent = currentTime >= seg.start_ms && currentTime <= seg.end_ms;
          const speakerName = (seg.speaker_label && speakersMap[seg.speaker_label]) || seg.speaker_label || "Người nói";
          const isEditing = editingPos === seg.position;

          return (
            <div
              key={seg.id || seg.position}
              className={`p-4 rounded-xl border transition-all ${
                isCurrent
                  ? "border-blue-300 bg-blue-50/40 shadow-sm"
                  : "border-gray-100 hover:border-gray-200 bg-white"
              }`}
              onMouseUp={() => handleTextSelection(seg)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-gray-800">{speakerName}</span>
                  <button
                    onClick={() => onSeek(seg.start_ms)}
                    className="flex items-center gap-1 font-mono text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 px-2 py-0.5 rounded transition-colors"
                  >
                    <Clock className="w-3 h-3" />
                    <span>{formatClock(seg.start_ms)}</span>
                  </button>
                </div>

                {!isEditing && (
                  <button
                    onClick={() => startEdit(seg)}
                    className="text-gray-400 hover:text-blue-600 p-1 rounded"
                    title="Chỉnh sửa câu"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {isEditing ? (
                <div className="space-y-2 mt-2">
                  <textarea
                    rows={2}
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    className="w-full p-2 border border-blue-400 rounded-lg text-sm focus:outline-none"
                    autoFocus
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setEditingPos(null)}
                      className="px-2.5 py-1 text-xs text-gray-600 hover:bg-gray-100 rounded"
                    >
                      Hủy
                    </button>
                    <button
                      onClick={() => saveEdit(seg)}
                      className="px-2.5 py-1 text-xs bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
                    >
                      Lưu
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-gray-700 leading-relaxed text-sm selection:bg-yellow-200">
                  {getText(seg)}
                </p>
              )}
            </div>
          );
        })}

        {segments.length === 0 && (
          <div className="text-center py-12 text-gray-400 text-sm">
            Chưa có đoạn hội thoại nào được ghi nhận.
          </div>
        )}
      </div>
    </div>
  );
}
