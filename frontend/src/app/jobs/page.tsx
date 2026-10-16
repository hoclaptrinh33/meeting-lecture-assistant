"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Clock, FileAudio, CheckCircle, AlertTriangle, XCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

interface JobSummary {
  id: string;
  title: string;
  source: string;
  status: string;
  duration_ms?: number;
  created_at: string;
}

const STATUS_BADGES: Record<string, { label: string; color: string }> = {
  queued: { label: "Đang chờ", color: "bg-yellow-50 text-yellow-700 border-yellow-200" },
  preprocessing: { label: "Tiền xử lý", color: "bg-blue-50 text-blue-700 border-blue-200" },
  transcribing: { label: "Đang nhận dạng", color: "bg-indigo-50 text-indigo-700 border-indigo-200" },
  diarizing: { label: "Phân tách người nói", color: "bg-purple-50 text-purple-700 border-purple-200" },
  ready: { label: "Hoàn tất", color: "bg-green-50 text-green-700 border-green-200" },
  failed: { label: "Thất bại", color: "bg-red-50 text-red-700 border-red-200" },
  cancelled: { label: "Đã hủy", color: "bg-gray-50 text-gray-700 border-gray-200" },
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = async () => {
    try {
      const res = await api.listJobs(50);
      setJobs(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatDuration = (ms?: number) => {
    if (!ms) return "--:--";
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}m ${sec}s`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Danh sách việc (Jobs)</h1>
          <p className="text-sm text-gray-500 mt-1">Quản lý và tra cứu các bản ghi âm và phiên họp đã xử lý</p>
        </div>

        <Link
          href="/jobs/new"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg flex items-center gap-2 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Tải file mới</span>
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-100">
            {jobs.map((job) => {
              const badge = STATUS_BADGES[job.status] || { label: job.status, color: "bg-gray-50 text-gray-600" };

              return (
                <Link
                  key={job.id}
                  href={`/jobs/${job.id}`}
                  className="p-5 flex items-center justify-between hover:bg-gray-50/80 transition-colors block"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-gray-900 text-base">{job.title}</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${badge.color}`}>
                        {badge.label}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Thời lượng: {formatDuration(job.duration_ms)}</span>
                      <span>•</span>
                      <span>Tạo lúc: {new Date(job.created_at).toLocaleString("vi-VN")}</span>
                      <span>•</span>
                      <span>Nguồn: {job.source === "upload" ? "Tải file" : "Nghe trực tiếp"}</span>
                    </div>
                  </div>

                  <span className="text-sm font-medium text-blue-600 hover:underline">Chi tiết →</span>
                </Link>
              );
            })}

            {jobs.length === 0 && (
              <div className="text-center py-16 text-gray-400 text-sm">
                Bạn chưa có job nào. Nhấn &quot;Tải file mới&quot; để bắt đầu.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
