"use client";

import React from "react";
import Link from "next/link";

export default function RegisterPage() {
  /**
   * TODO: Triển khai trang đăng ký tài khoản:
   * - Form display_name, email, password
   * - Gọi api.register({ email, display_name, password })
   * - Lưu access token và chuyển hướng tới /jobs
   */
  return (
    <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl border border-gray-100 shadow-sm space-y-4">
      <h1 className="text-2xl font-bold text-gray-900 text-center">Đăng ký tài khoản</h1>
      <p className="text-sm text-gray-500 text-center">Khung đăng ký - TODO: Triển khai form tạo tài khoản</p>
      <div className="text-center text-xs text-gray-500 pt-4">
        Đã có tài khoản?{" "}
        <Link href="/login" className="text-blue-600 hover:underline font-medium">
          Đăng nhập
        </Link>
      </div>
    </div>
  );
}
