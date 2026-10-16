"use client";

import React from "react";
import Link from "next/link";

export default function LoginPage() {
  /**
   * TODO: Triển khai trang đăng nhập tài khoản:
   * - Form email + mật khẩu
   * - Gọi api.login({ email, password })
   * - Lưu access token và chuyển hướng tới /jobs
   */
  return (
    <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-gray-100 shadow-sm space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 text-center">Đăng nhập</h1>
      <p className="text-sm text-gray-500 text-center">Khung đăng nhập - TODO: Triển khai form xác thực</p>
      <div className="text-center text-xs text-gray-500 pt-4">
        Chưa có tài khoản?{" "}
        <Link href="/register" className="text-blue-600 hover:underline font-medium">
          Đăng ký ngay
        </Link>
      </div>
    </div>
  );
}
