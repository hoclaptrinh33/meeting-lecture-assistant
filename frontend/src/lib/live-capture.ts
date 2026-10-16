/**
 * Quản lý thu âm micro hoặc tab trình duyệt và truyền luồng PCM 16kHz float32 qua WebSocket.
 */

export class LiveAudioCapture {
  async startCapture(
    mode: "mic" | "display",
    sessionId: string,
    wsTicket: string,
    onStatusChange?: (status: "connected" | "disconnected" | "error") => void
  ): Promise<void> {
    /**
     * TODO:
     * 1. Lấy MediaStream từ getUserMedia hoặc getDisplayMedia
     * 2. Mở kết nối WebSocket tới /api/live/ws/{sessionId}?ticket={wsTicket}
     * 3. Thiết lập AudioContext 16000Hz và trích xuất mảng PCM float32 gửi qua WebSocket.
     */
  }

  stopCapture(): void {
    /**
     * TODO: Dừng processor, ngắt AudioContext, đóng track MediaStream và đóng WebSocket.
     */
  }
}
