/**
 * Hàng đợi hiển thị hiệu ứng máy chữ (Typewriter queue) cho transcript trực tiếp.
 */

export class TypewriterQueue {
  private onEmitWord: (word: string) => void;
  private speedMs: number;

  constructor(onEmitWord: (word: string) => void, speedMs: number = 60) {
    this.onEmitWord = onEmitWord;
    this.speedMs = speedMs;
  }

  enqueue(text: string): void {
    /**
     * TODO: Tách từ trong chuỗi text và đẩy vào hàng đợi nhả chữ dần dần.
     */
  }

  clear(): void {
    /**
     * TODO: Làm rỗng hàng đợi.
     */
  }
}
