/**
 * Module nén âm thanh phía client sử dụng FFmpeg.wasm sang Opus 16kHz mono 32kb/s.
 */

export interface CompressionProgress {
  ratio: number;
}

export class ClientFfmpegCompressor {
  static async compressToOpus(
    file: File,
    onProgress?: (p: CompressionProgress) => void
  ): Promise<File> {
    /**
     * TODO: Kiểm tra hỗ trợ SharedArrayBuffer.
     * Nếu hỗ trợ: tải @ffmpeg/ffmpeg, ghi file ảo và thực thi ffmpeg -i input -vn -ac 1 -ar 16000 -c:a libopus -b:a 32k -f ogg output.opus
     * Nếu không hỗ trợ: trả về file gốc.
     */
    return file;
  }
}
