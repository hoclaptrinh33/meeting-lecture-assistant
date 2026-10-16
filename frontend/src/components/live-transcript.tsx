"use client";

import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, ScreenShare, StopCircle, Radio, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { LiveAudioCapture } from "@/lib/live-capture";
import { TypewriterQueue } from "@/lib/typewriter-queue";

interface LiveTranscriptProps {
  onSessionFinalized: (jobId: string) => void;
}

export function LiveTranscript({ onSessionFinalized }: LiveTranscriptProps) {
  const [capturing, setCapturing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [liveLines, setLiveLines] = useState<string[]>([]);
  const [currentBuffer, setCurrentBuffer] = useState("");
  const [audioSource, setAudioSource] = useState<"mic" | "display">("mic");
  const [title, setTitle] = useState("Cuộc họp trực tiếp");
  const [connectionStatus, setConnectionStatus] = useState<string>("Sẵn sàng");

  const captureRef = useRef<LiveAudioCapture | null>(null);
  const typewriterRef = useRef<TypewriterQueue | null>(null);

  useEffect(() => {
    typewriterRef.current = new TypewriterQueue((word) => {
      setCurrentBuffer((prev) => (prev ? `${prev} ${word}` : word));
    });

    return () => {
      if (captureRef.current) {
        captureRef.current.stopCapture();
      }
    };
  }, []);

  const startSession = async () => {
    try {
      setConnectionStatus("Đang yêu cầu cấp quyền GPU...");
      const res = await api.createLiveSession({
        title,
        vocabulary: "",
      });

      setSessionId(res.session_id);
      setConnectionStatus("Đang kết nối truyền âm thanh...");

      captureRef.current = new LiveAudioCapture();
      await captureRef.current.startCapture(
        audioSource,
        res.session_id,
        res.ws_ticket,
        (status) => {
          if (status === "connected") {
            setCapturing(true);
            setConnectionStatus("Đang ghi âm & nhận dạng nháp...");
          } else if (status === "disconnected") {
            setConnectionStatus("Mất kết nối");
          } else if (status === "error") {
            setConnectionStatus("Lỗi kết nối");
          }
        }
      );
    } catch (err: any) {
      alert("Khởi tạo phiên thất bại: " + (err.message || err));
      setConnectionStatus("Sẵn sàng");
    }
  };

  const stopSession = async () => {
    if (!sessionId) return;
    try {
      setConnectionStatus("Đang dừng và tổng hợp bản chuẩn pass 2...");
      if (captureRef.current) {
        captureRef.current.stopCapture();
      }
      setCapturing(false);

      const res = await api.stopLiveSession(sessionId);
      if (res.job_id) {
        onSessionFinalized(res.job_id);
      }
    } catch (err: any) {
      alert("Dừng phiên thất bại: " + err.message);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 shadow-sm space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Radio className="w-5 h-5 text-red-500 animate-pulse" />
            <span>Chế độ nghe trực tiếp (PT2 - Pha kép)</span>
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Nhận dạng nháp thời gian thực bằng Whisper Small, tự động tổng hợp bản chuẩn Large-v3-Turbo & Diarization khi kết thúc.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full">
            Trạng thái: {connectionStatus}
          </span>

          {!capturing ? (
            <button
              onClick={startSession}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium text-sm rounded-lg flex items-center gap-2 shadow-sm transition-colors"
            >
              <Mic className="w-4 h-4" />
              <span>Bắt đầu nghe</span>
            </button>
          ) : (
            <button
              onClick={stopSession}
              className="px-4 py-2 bg-gray-900 hover:bg-black text-white font-medium text-sm rounded-lg flex items-center gap-2 shadow-sm transition-colors"
            >
              <StopCircle className="w-4 h-4 text-red-400" />
              <span>Dừng phiên</span>
            </button>
          )}
        </div>
      </div>

      {!capturing && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề phiên nghe</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nguồn âm thanh</label>
            <div className="flex gap-4 mt-2">
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="radio"
                  name="audioSource"
                  value="mic"
                  checked={audioSource === "mic"}
                  onChange={() => setAudioSource("mic")}
                  className="text-blue-600"
                />
                <Mic className="w-4 h-4" />
                <span>Microphone</span>
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="radio"
                  name="audioSource"
                  value="display"
                  checked={audioSource === "display"}
                  onChange={() => setAudioSource("display")}
                  className="text-blue-600"
                />
                <ScreenShare className="w-4 h-4" />
                <span>Âm thanh tab trình duyệt / Màn hình</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Live transcript typewriter display */}
      <div className="min-h-[280px] max-h-[460px] overflow-y-auto bg-gray-50 rounded-xl p-5 border border-gray-200 font-sans space-y-3">
        {liveLines.map((line, idx) => (
          <p key={idx} className="text-gray-700 text-sm leading-relaxed">
            {line}
          </p>
        ))}

        {currentBuffer && (
          <p className="text-gray-900 font-medium text-sm leading-relaxed">
            {currentBuffer}
            <span className="inline-block w-1.5 h-4 ml-1 bg-blue-600 animate-pulse" />
          </p>
        )}

        {!currentBuffer && liveLines.length === 0 && (
          <div className="text-center py-20 text-gray-400 text-sm">
            {capturing ? "Đang lắng nghe âm thanh..." : "Nhấn 'Bắt đầu nghe' để tiến hành thu âm và nhận dạng trực tiếp."}
          </div>
        )}
      </div>
    </div>
  );
}
