"use client";

import React from "react";
import Link from "next/link";
import { Plus } from "lucide-react";

export default function JobsPage() {
  /**
   * TODO: Triển khai danh sách công việc:
   * - Gọi api.listJobs()
   * - Render danh sách job kèm badge trạng thái (queued, transcribing, ready, failed...)
   * - Phân trang cursor
   */
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Danh sách việc (Jobs)</h1>
          <p className="text-sm text-gray-500 mt-1">Quản lý và tra cứu các bản ghi âm và phiên họp</p>
        </div>

        <Link
          href="/jobs/new"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-lg flex items-center gap-2 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Tải file mới</span>
        </Link>
      </div>

      <div className="bg-white p-8 rounded-xl border border-gray-100 shadow-sm text-center text-gray-400 text-sm">
        Khung danh sách công việc - TODO: Triển khai gọi api.listJobs() và render bảng danh sách.
      </div>
    </div>
  );
}
