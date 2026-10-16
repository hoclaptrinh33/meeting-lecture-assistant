/**
 * Hàng đợi hiển thị hiệu ứng máy chữ (Typewriter queue) cho transcript trực tiếp và SSE.
 * Giúp hiển thị từ một cách mượt mà và thích ứng với tốc độ truyền mạng.
 */

export class TypewriterQueue {
  private queue: string[] = [];
  private isRunning: boolean = false;
  private onEmitWord: (word: string) => void;
  private speedMs: number;

  constructor(onEmitWord: (word: string) => void, speedMs: number = 60) {
    this.onEmitWord = onEmitWord;
    this.speedMs = speedMs;
  }

  enqueue(text: string): void {
    const words = text.split(" ").filter((w) => w.length > 0);
    this.queue.push(...words);
    if (!this.isRunning) {
      this.processQueue();
    }
  }

  private processQueue(): void {
    if (this.queue.length === 0) {
      this.isRunning = false;
      return;
    }

    this.isRunning = true;
    const word = this.queue.shift();
    if (word) {
      this.onEmitWord(word);
    }

    // Tự động tăng tốc độ nếu hàng đợi bị ứ đọng nhiều từ
    const adaptiveDelay = this.queue.length > 10 ? Math.max(15, this.speedMs / 2) : this.speedMs;

    setTimeout(() => {
      this.processQueue();
    }, adaptiveDelay);
  }

  clear(): void {
    this.queue = [];
    this.isRunning = false;
  }
}
