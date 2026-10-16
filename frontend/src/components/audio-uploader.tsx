"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileAudio, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { ClientFfmpegCompressor } from "@/lib/ffmpeg-compressor";

export function AudioUploader() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [vocabulary, setVocabulary] = useState("");
  const [numSpeakers, setNumSpeakers] = useState<number | "">("");
  const [compressClient, setCompressClient] = useState(true);
  const [loading, setLoading] = useState(false);
  const [compressProgress, setCompressProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!title) {
        setTitle(selected.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Vui lòng chọn một file âm thanh hoặc video.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let uploadFile = file;
      if (compressClient) {
        setCompressProgress(0);
        uploadFile = await ClientFfmpegCompressor.compressToOpus(file, ({ ratio }) => {
          setCompressProgress(Math.round(ratio * 100));
        });
        setCompressProgress(null);
      }

      const formData = new FormData();
      formData.append("file", uploadFile);
      if (title) formData.append("title", title);
      if (vocabulary) formData.append("vocabulary", vocabulary);
      if (numSpeakers !== "") formData.append("num_speakers", numSpeakers.toString());

      const res = await api.createJob(formData);
      router.push(`/jobs/${res.job_id}`);
    } catch (err: any) {
      setError(err.message || "Tải lên thất bại.");
    } finally {
      setLoading(false);
      setCompressProgress(null);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-sm border border-gray-100">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Tải lên file ghi âm / video</h2>
        <p className="text-sm text-gray-500 mt-1">Hỗ trợ các định dạng âm thanh và video phổ biến (MP3, WAV, M4A, MP4, MKV...). Tối đa 3 giờ.</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* File Dropzone */}
      <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors">
        <input
          type="file"
          id="audio-input"
          accept="audio/*,video/*,.opus,.mkv"
          onChange={handleFileChange}
          className="hidden"
        />
        <label htmlFor="audio-input" className="cursor-pointer flex flex-col items-center">
          <Upload className="w-12 h-12 text-gray-400 mb-3" />
          {file ? (
            <div className="flex items-center gap-2 text-blue-600 font-medium">
              <FileAudio className="w-5 h-5" />
              <span>{file.name}</span> ({(file.size / (1024 * 1024)).toFixed(1)} MB)
            </div>
          ) : (
            <>
              <span className="text-sm font-semibold text-gray-700">Nhấn để chọn file hoặc kéo thả vào đây</span>
              <span className="text-xs text-gray-500 mt-1">MP3, WAV, M4A, OGG, OPUS, MP4, WEBM</span>
            </>
          )}
        </label>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề cuộc họp / bài giảng</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ví dụ: Họp bàn giao đồ án KTPM"
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Số lượng người nói (ước tính)</label>
          <input
            type="number"
            min={1}
            max={20}
            value={numSpeakers}
            onChange={(e) => setNumSpeakers(e.target.value ? parseInt(e.target.value) : "")}
            placeholder="Để trống nếu tự động nhận diện"
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Từ điển thuật ngữ / Tên riêng đặc thù</label>
        <textarea
          rows={2}
          value={vocabulary}
          onChange={(e) => setVocabulary(e.target.value)}
          placeholder="Nhập các từ viết tắt hoặc danh từ riêng tiếng Việt/Anh cách nhau bằng dấu phẩy..."
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="compress-opt"
          checked={compressClient}
          onChange={(e) => setCompressClient(e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="compress-opt" className="text-sm text-gray-600">
          Nén âm thanh sang Opus trên trình duyệt trước khi tải lên (tiết kiệm băng thông)
        </label>
      </div>

      {compressProgress !== null && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Đang nén trên trình duyệt...</span>
            <span>{compressProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${compressProgress}%` }} />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !file}
        className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Đang xử lý tải lên...</span>
          </>
        ) : (
          <span>Bắt đầu nhận dạng</span>
        )}
      </button>
    </form>
  );
}
