"use client";

import React, { useState } from "react";
import { Sparkles, FileText, Download, CheckCircle2, Clock, Loader2, BookOpen } from "lucide-react";
import { api } from "@/lib/api";

interface AiActionPanelProps {
  jobId: string;
  onRefreshTranscript: () => void;
}

export function AiActionPanel({ jobId, onRefreshTranscript }: AiActionPanelProps) {
  const [cleaning, setCleaning] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [summaryResult, setSummaryResult] = useState<any>(null);
  const [exportFormat, setExportFormat] = useState<"md" | "docx" | "pdf" | "srt" | "vtt">("docx");

  const handleClean = async () => {
    try {
      setCleaning(true);
      await api.cleanTranscript(jobId);
      // Polling hoặc đợi xong
      setTimeout(() => {
        onRefreshTranscript();
        setCleaning(false);
      }, 3000);
    } catch (err: any) {
      alert(err.message || "Làm sạch văn bản thất bại");
      setCleaning(false);
    }
  };

  const handleSummarize = async (template: "meeting" | "lecture") => {
    try {
      setSummarizing(true);
      await api.summarizeTranscript(jobId, template);
      // Chờ hoàn thành
      const interval = setInterval(async () => {
        try {
          const res = await api.getLlmStatus(jobId, "summarize");
          if (res.status === "done") {
            setSummaryResult({ template, data: res.result });
            clearInterval(interval);
            setSummarizing(false);
          } else if (res.status === "failed") {
            alert(res.error_message || "Tóm tắt thất bại");
            clearInterval(interval);
            setSummarizing(false);
          }
        } catch {
          // ignore
        }
      }, 2000);
    } catch (err: any) {
      alert(err.message || "Gửi yêu cầu tóm tắt thất bại");
      setSummarizing(false);
    }
  };

  const handleExport = async () => {
    try {
      setExporting(true);
      const blob = await api.exportJob(jobId, { format: exportFormat, text: "auto", include_speakers: true });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `export_${jobId}.${exportFormat}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.message || "Xuất tài liệu thất bại");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span>Trợ lý hậu kỳ thông minh</span>
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">Sử dụng LLM để tinh chỉnh văn bản, tạo biên bản cuộc họp và xuất file.</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleClean}
            disabled={cleaning}
            className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-medium text-xs rounded-lg flex items-center gap-1.5 transition-colors"
          >
            {cleaning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            <span>Làm sạch văn bản</span>
          </button>

          <button
            onClick={() => handleSummarize("meeting")}
            disabled={summarizing}
            className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium text-xs rounded-lg flex items-center gap-1.5 transition-colors"
          >
            {summarizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
            <span>Biên bản cuộc họp</span>
          </button>

          <button
            onClick={() => handleSummarize("lecture")}
            disabled={summarizing}
            className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-medium text-xs rounded-lg flex items-center gap-1.5 transition-colors"
          >
            {summarizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <BookOpen className="w-4 h-4" />}
            <span>Ghi chú bài giảng</span>
          </button>

          {/* Export Dropdown & Button */}
          <div className="flex items-center gap-1 ml-auto">
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as any)}
              className="px-2 py-1.5 border border-gray-200 rounded-lg text-xs bg-gray-50 text-gray-700 outline-none"
            >
              <option value="docx">Word (.docx)</option>
              <option value="pdf">PDF (.pdf)</option>
              <option value="md">Markdown (.md)</option>
              <option value="srt">SubRip (.srt)</option>
              <option value="vtt">WebVTT (.vtt)</option>
            </select>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="px-3 py-1.5 bg-gray-900 hover:bg-black text-white font-medium text-xs rounded-lg flex items-center gap-1.5 transition-colors"
            >
              {exporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              <span>Xuất file</span>
            </button>
          </div>
        </div>
      </div>

      {/* Summary View */}
      {summaryResult && summaryResult.data && (
        <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 text-sm space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-gray-800">
              {summaryResult.template === "meeting" ? "Biên bản cuộc họp" : "Ghi chú bài giảng"}
            </h4>
          </div>

          {summaryResult.data.objective && (
            <div>
              <span className="font-semibold text-gray-700">Mục tiêu:</span>
              <p className="text-gray-600 mt-1">{summaryResult.data.objective}</p>
            </div>
          )}

          {summaryResult.data.overview && (
            <div>
              <span className="font-semibold text-gray-700">Tổng quan bài giảng:</span>
              <p className="text-gray-600 mt-1">{summaryResult.data.overview}</p>
            </div>
          )}

          {summaryResult.data.decisions && summaryResult.data.decisions.length > 0 && (
            <div>
              <span className="font-semibold text-gray-700">Quyết định quan trọng:</span>
              <ul className="list-disc pl-5 mt-1 space-y-1 text-gray-600">
                {summaryResult.data.decisions.map((d: any, idx: number) => (
                  <li key={idx}>
                    <span className="font-mono text-xs text-gray-400">[{d.timestamp}]</span> {d.text}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {summaryResult.data.actions && summaryResult.data.actions.length > 0 && (
            <div>
              <span className="font-semibold text-gray-700">Hành động cần làm:</span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {summaryResult.data.actions.map((a: any, idx: number) => (
                  <div key={idx} className="bg-white p-2.5 rounded border border-gray-200 text-xs">
                    <div className="font-medium text-gray-800">{a.task}</div>
                    <div className="text-gray-500 mt-1 flex justify-between">
                      <span>Phụ trách: {a.owner}</span>
                      <span>Hạn: {a.deadline}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {summaryResult.data.concepts && summaryResult.data.concepts.length > 0 && (
            <div>
              <span className="font-semibold text-gray-700">Khái niệm trọng tâm:</span>
              <div className="space-y-2 mt-2">
                {summaryResult.data.concepts.map((c: any, idx: number) => (
                  <div key={idx} className="bg-white p-2.5 rounded border border-gray-200 text-xs">
                    <span className="font-bold text-emerald-700">{c.term}: </span>
                    <span className="text-gray-600">{c.explanation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
