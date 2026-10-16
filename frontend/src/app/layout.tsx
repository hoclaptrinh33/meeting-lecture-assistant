import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trợ lý cuộc họp & bài giảng tiếng Việt",
  description: "Chuyển âm thanh thành văn bản tiếng Việt có mốc thời gian, tên người nói và biên bản hậu kỳ.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className="min-h-screen flex flex-col">
        {/* Top Navbar */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
                  STT
                </div>
                <span className="font-bold text-gray-900 text-lg">Trợ lý cuộc họp</span>
              </Link>

              <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
                <Link href="/jobs" className="hover:text-blue-600 transition-colors">
                  Danh sách việc
                </Link>
                <Link href="/jobs/new" className="hover:text-blue-600 transition-colors">
                  Tải file mới (PT1)
                </Link>
                <Link href="/live" className="hover:text-blue-600 transition-colors">
                  Nghe trực tiếp (PT2)
                </Link>
                <Link href="/voice-profiles" className="hover:text-blue-600 transition-colors">
                  Hồ sơ giọng
                </Link>
              </nav>
            </div>

            <div className="flex items-center gap-3 text-sm">
              <Link
                href="/login"
                className="px-3.5 py-1.5 text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Đăng nhập
              </Link>
              <Link
                href="/register"
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                Đăng ký
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
