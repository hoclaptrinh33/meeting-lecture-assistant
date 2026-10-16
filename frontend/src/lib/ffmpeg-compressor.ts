/**
 * Trình nén âm thanh phía client sử dụng FFmpeg.wasm để chuyển đổi file sang Opus 16kHz mono 32kb/s.
 * Giúp tiết kiệm băng thông và tăng tốc độ tải lên.
 */

export interface CompressionProgress {
  ratio: number;
}

export class ClientFfmpegCompressor {
  private static isSupported(): boolean {
    return typeof window !== "undefined" && typeof SharedArrayBuffer !== "undefined";
  }

  static async compressToOpus(
    file: File,
    onProgress?: (p: CompressionProgress) => void
  ): Promise<File> {
    if (!this.isSupported()) {
      // Nếu trình duyệt không hỗ trợ SharedArrayBuffer, fallback tải file gốc
      return file;
    }

    try {
      const { FFmpeg } = await import("@ffmpeg/ffmpeg");
      const { fetchFile } = await import("@ffmpeg/util");

      const ffmpeg = new FFmpeg();

      ffmpeg.on("progress", ({ progress }) => {
        if (onProgress) {
          onProgress({ ratio: progress });
        }
      });

      await ffmpeg.load();

      const inputName = `input_${file.name}`;
      const outputName = "output.opus";

      await ffmpeg.writeFile(inputName, await fetchFile(file));

      // Lệnh nén chuẩn: mono, 16000Hz, 32k bitrate, định dạng ogg container với codec libopus
      await ffmpeg.exec([
        "-i", inputName,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "libopus",
        "-b:a", "32k",
        "-f", "ogg",
        outputName,
      ]);

      const data = await ffmpeg.readFile(outputName);
      const blob = new Blob([data as any], { type: "audio/ogg; codecs=opus" });

      const newFileName = file.name.replace(/\.[^/.]+$/, "") + ".opus";
      return new File([blob], newFileName, { type: "audio/ogg" });
    } catch (err) {
      console.warn("FFmpeg.wasm nén thất bại, fallback sang tải file gốc:", err);
      return file;
    }
  }
}
