import Link from "next/link";
import { Upload, Radio, Users, Sparkles, FileText, CheckCircle } from "lucide-react";

export default function HomePage() {
  return (
    <div className="space-y-12 py-6">
      {/* Hero section */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">
          Hệ thống trợ lý cuộc họp & bài giảng tiếng Việt
        </h1>
        <p className="text-lg text-gray-600 leading-relaxed">
          Tự động chuyển đổi âm thanh thành văn bản có mốc thời gian, tách biệt người nói bằng công nghệ nhận dạng giọng nói tiên tiến và trích xuất biên bản tự động với LLM.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            href="/jobs/new"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl shadow-sm flex items-center gap-2 transition-colors"
          >
            <Upload className="w-5 h-5" />
            <span>Tải file ghi âm (PT1)</span>
          </Link>

          <Link
            href="/live"
            className="px-6 py-3 bg-gray-900 hover:bg-black text-white font-medium rounded-xl shadow-sm flex items-center gap-2 transition-colors"
          >
            <Radio className="w-5 h-5 text-red-400" />
            <span>Nghe trực tiếp (PT2)</span>
          </Link>
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Upload className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-gray-900 text-lg">Xử lý file ghi âm sẵn</h3>
          <p className="text-sm text-gray-500 leading-relaxed">
            Nén Opus trực tiếp trên trình duyệt, nhận dạng chuẩn xác với Faster-Whisper Large-v3-Turbo và cắt câu thông minh qua Silero VAD.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-gray-900 text-lg">Phân đoạn người nói</h3>
          <p className="text-sm text-gray-500 leading-relaxed">
            Tích hợp Pyannote Diarization 3.1 gán nhãn từng từ, tự động nhận diện người quen qua hồ sơ so khớp vector giọng nói.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-gray-900 text-lg">Biên bản hậu kỳ LLM</h3>
          <p className="text-sm text-gray-500 leading-relaxed">
            Loại bỏ từ đệm vô nghĩa, tổng hợp mục tiêu cuộc họp, danh sách quyết định, phân công việc cần làm và xuất tài liệu Word, PDF, SRT.
          </p>
        </div>
      </div>
    </div>
  );
}
