"use client";

import React, { useState } from "react";
import { Users, Edit2, Check, X } from "lucide-react";
import { api } from "@/lib/api";

interface SpeakerItem {
  speaker_label: string;
  display_name: string;
  source: string;
}

interface SpeakerListProps {
  jobId: string;
  speakers: SpeakerItem[];
  onSpeakerUpdated: (label: string, newName: string) => void;
}

export function SpeakerList({ jobId, speakers, onSpeakerUpdated }: SpeakerListProps) {
  const [editingLabel, setEditingLabel] = useState<string | null>(null);
  const [nameInput, setNameInput] = useState("");

  const startEdit = (spk: SpeakerItem) => {
    setEditingLabel(spk.speaker_label);
    setNameInput(spk.display_name);
  };

  const cancelEdit = () => {
    setEditingLabel(null);
    setNameInput("");
  };

  const saveEdit = async (label: string) => {
    if (!nameInput.trim()) return;
    try {
      await api.patchSpeaker(jobId, label, nameInput.trim());
      onSpeakerUpdated(label, nameInput.trim());
      setEditingLabel(null);
    } catch (err) {
      console.error("Cập nhật tên người nói thất bại:", err);
    }
  };

  if (!speakers || speakers.length === 0) {
    return null;
  }

  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Users className="w-4 h-4 text-gray-500" />
        <h3 className="text-sm font-semibold text-gray-800">Danh sách người nói</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {speakers.map((spk) => {
          const isEditing = editingLabel === spk.speaker_label;

          return (
            <div
              key={spk.speaker_label}
              className="flex items-center gap-2 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-lg text-sm"
            >
              {isEditing ? (
                <>
                  <input
                    type="text"
                    value={nameInput}
                    onChange={(e) => setNameInput(e.target.value)}
                    className="px-2 py-0.5 border rounded outline-none text-xs w-32"
                    autoFocus
                  />
                  <button
                    onClick={() => saveEdit(spk.speaker_label)}
                    className="text-green-600 hover:text-green-700"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={cancelEdit} className="text-gray-400 hover:text-gray-600">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </>
              ) : (
                <>
                  <span className="font-medium text-gray-700">{spk.display_name}</span>
                  <span className="text-xs text-gray-400 font-mono">({spk.speaker_label})</span>
                  <button
                    onClick={() => startEdit(spk)}
                    className="text-gray-400 hover:text-blue-600 ml-1"
                    title="Đổi tên hiển thị"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
