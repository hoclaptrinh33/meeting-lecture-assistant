/**
 * Quản lý thu âm trực tiếp (PT2) từ microphone hoặc chia sẻ âm thanh tab/màn hình.
 * Chuyển đổi sang PCM 16kHz mono float32 và truyền qua WebSocket.
 */

export class LiveAudioCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private socket: WebSocket | null = null;
  private processor: ScriptProcessorNode | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;

  async startCapture(
    mode: "mic" | "display",
    sessionId: string,
    wsTicket: string,
    onStatusChange?: (status: "connected" | "disconnected" | "error") => void
  ): Promise<void> {
    // 1. Lấy luồng âm thanh
    if (mode === "mic") {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
    } else {
      this.mediaStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });
    }

    // 2. Khởi tạo WebSocket nối tới backend
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/live/ws/${sessionId}?ticket=${encodeURIComponent(wsTicket)}`;

    this.socket = new WebSocket(wsUrl);
    this.socket.binaryType = "arraybuffer";

    this.socket.onopen = () => {
      onStatusChange?.("connected");
      this.setupAudioPipeline();
    };

    this.socket.onerror = () => {
      onStatusChange?.("error");
    };

    this.socket.onclose = () => {
      onStatusChange?.("disconnected");
      this.stopCapture();
    };
  }

  private setupAudioPipeline(): void {
    if (!this.mediaStream) return;

    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
      sampleRate: 16000,
    });

    this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
    // Buffer size 4096 = ~0.25s âm thanh @ 16kHz
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

    this.processor.onaudioprocess = (e) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        const inputData = e.inputBuffer.getChannelData(0);
        // Gửi mảng float32 nhị phân trực tiếp
        this.socket.send(inputData.buffer);
      }
    };

    this.sourceNode.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
  }

  stopCapture(): void {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.sourceNode) {
      this.sourceNode.disconnect();
      this.sourceNode = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close();
      }
      this.socket = null;
    }
  }
}
