"use client";

import React, { useEffect, useState } from "react";
import { Mic, Trash2, Plus, Volume2, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";

interface VoiceProfile {
  id: string;
  display_name: string;
  status: string;
  duration_ms?: number;
  created_at: string;
}

export default function VoiceProfilesPage() {
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchProfiles = async () => {
    try {
      const data = await api.listVoiceProfiles();
      setProfiles(data || []);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name.trim()) {
      setError("Vui lòng nhập tên người nói và chọn file mẫu giọng.");
      return;
    }

    try {
      setCreating(true);
      setError(null);
      const fd = new FormData();
      fd.append("name", name.trim());
      fd.append("file", file);

      await api.createVoiceProfile(fd);
      setName("");
      setFile(null);
      await fetchProfiles();
    } catch (err: any) {
      setError(err.message || "Tạo hồ sơ giọng thất bại.");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Bạn có chắc muốn xóa mẫu giọng này?")) return;
    try {
      await api.deleteVoiceProfile(id);
      setProfiles((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      alert("Xóa thất bại: " + err.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Hồ sơ giọng nói (Voice Profiles)</h1>
        <p className="text-sm text-gray-500 mt-1">
          Lưu trữ mẫu đặc trưng giọng nói (voice embedding) để tự động nhận dạng và gán tên thành viên sau bước Diarization.
        </p>
      </div>

      {/* Form add profile */}
      <form onSubmit={handleCreate} className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
          <Plus className="w-5 h-5 text-blue-600" />
          <span>Thêm hồ sơ giọng mới</span>
        </h3>

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Tên người nói / Thành viên</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ví dụ: Nguyễn Văn A (Trưởng nhóm)"
              className="w-full px-3 py-2 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">File ghi âm mẫu (10s – 60s)</label>
            <input
              type="file"
              accept="audio/*"
              onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-xs text-gray-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={creating || !file || !name.trim()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium text-xs rounded-lg flex items-center gap-2 transition-colors"
        >
          {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
          <span>Trích xuất & Đăng ký giọng</span>
        </button>
      </form>

      {/* Profiles list */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100 font-semibold text-sm text-gray-800">
          Danh sách hồ sơ đã lưu
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {profiles.map((p) => (
              <div key={p.id} className="p-4 flex items-center justify-between hover:bg-gray-50/50">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-gray-900 text-sm">{p.display_name}</span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        p.status === "ready"
                          ? "bg-green-50 text-green-700"
                          : p.status === "processing"
                          ? "bg-yellow-50 text-yellow-700"
                          : "bg-red-50 text-red-700"
                      }`}
                    >
                      {p.status === "ready" ? "Sẵn sàng" : p.status === "processing" ? "Đang xử lý" : "Lỗi"}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">
                    Mã hồ sơ: {p.id} • Tạo ngày: {new Date(p.created_at).toLocaleDateString("vi-VN")}
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(p.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Xóa hồ sơ"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}

            {profiles.length === 0 && (
              <div className="text-center py-12 text-gray-400 text-xs">
                Chưa có hồ sơ giọng nào được lưu.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
