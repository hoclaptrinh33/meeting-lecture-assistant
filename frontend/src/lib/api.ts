/**
 * API client khung sườn giao tiếp với backend FastAPI (/api).
 */

const BASE_URL = "/api";

export interface ApiError {
  code: string;
  message: string;
  fields?: Record<string, string>;
}

class ApiClient {
  private accessToken: string | null = null;

  setAccessToken(token: string | null) {
    this.accessToken = token;
    // TODO: Quản lý lưu trữ token (localStorage/cookie)
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // TODO: Triển khai fetch chuẩn, thêm header Authorization và xử lý mã lỗi ApiError
    const res = await fetch(`${BASE_URL}${endpoint}`, options);
    return res.json();
  }

  // Auth endpoints
  async register(data: any): Promise<any> {
    return this.request("/auth/register", { method: "POST", body: JSON.stringify(data) });
  }

  async login(data: any): Promise<any> {
    return this.request("/auth/login", { method: "POST", body: JSON.stringify(data) });
  }

  async refresh(refreshToken: string): Promise<any> {
    return this.request("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
  }

  async logout(refreshToken: string): Promise<void> {
    return this.request("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
  }

  async getMe(): Promise<any> {
    return this.request("/auth/me", { method: "GET" });
  }

  // Jobs endpoints
  async createJob(formData: FormData): Promise<any> {
    return this.request("/jobs", { method: "POST", body: formData });
  }

  async listJobs(limit = 20, cursor?: string): Promise<any> {
    const q = new URLSearchParams({ limit: limit.toString() });
    if (cursor) q.append("cursor", cursor);
    return this.request(`/jobs?${q.toString()}`, { method: "GET" });
  }

  async getJob(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}`, { method: "GET" });
  }

  async deleteJob(jobId: string): Promise<void> {
    return this.request(`/jobs/${jobId}`, { method: "DELETE" });
  }

  async cancelJob(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}/cancel`, { method: "POST" });
  }

  async getTranscript(jobId: string, pass = 2): Promise<any> {
    return this.request(`/jobs/${jobId}/transcript?pass=${pass}`, { method: "GET" });
  }

  async patchSegment(jobId: string, position: number, textEdited: string, pass = 2): Promise<any> {
    return this.request(`/jobs/${jobId}/segments/${position}?pass=${pass}`, {
      method: "PATCH",
      body: JSON.stringify({ text_edited: textEdited }),
    });
  }

  async patchSpeaker(jobId: string, speakerLabel: string, displayName: string): Promise<any> {
    return this.request(`/jobs/${jobId}/speakers/${encodeURIComponent(speakerLabel)}`, {
      method: "PATCH",
      body: JSON.stringify({ display_name: displayName }),
    });
  }

  async createHighlight(jobId: string, data: any): Promise<any> {
    return this.request(`/jobs/${jobId}/highlights`, { method: "POST", body: JSON.stringify(data) });
  }

  async deleteHighlight(jobId: string, highlightId: string): Promise<void> {
    return this.request(`/jobs/${jobId}/highlights/${highlightId}`, { method: "DELETE" });
  }

  async createActionItem(jobId: string, data: any): Promise<any> {
    return this.request(`/jobs/${jobId}/action-items`, { method: "POST", body: JSON.stringify(data) });
  }

  async deleteActionItem(jobId: string, itemId: string): Promise<void> {
    return this.request(`/jobs/${jobId}/action-items/${itemId}`, { method: "DELETE" });
  }

  async getMediaToken(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}/media-token`, { method: "POST" });
  }

  async exportJob(jobId: string, data: any): Promise<Blob> {
    // TODO: Gọi POST /jobs/{jobId}/exports và trả blob
    return new Blob();
  }

  // LLM endpoints
  async cleanTranscript(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}/llm/clean`, { method: "POST" });
  }

  async summarizeTranscript(jobId: string, template: "meeting" | "lecture"): Promise<any> {
    return this.request(`/jobs/${jobId}/llm/summarize`, {
      method: "POST",
      body: JSON.stringify({ template }),
    });
  }

  async getLlmStatus(jobId: string, task: "clean" | "summarize"): Promise<any> {
    return this.request(`/jobs/${jobId}/llm/${task}`, { method: "GET" });
  }

  // Live endpoints
  async createLiveSession(data: any): Promise<any> {
    return this.request("/live/sessions", { method: "POST", body: JSON.stringify(data) });
  }

  async stopLiveSession(sessionId: string): Promise<any> {
    return this.request(`/live/sessions/${sessionId}/stop`, { method: "POST" });
  }

  async getLiveSession(sessionId: string): Promise<any> {
    return this.request(`/live/sessions/${sessionId}`, { method: "GET" });
  }

  // Voice profiles endpoints
  async listVoiceProfiles(): Promise<any[]> {
    return this.request("/voice-profiles", { method: "GET" });
  }

  async createVoiceProfile(formData: FormData): Promise<any> {
    return this.request("/voice-profiles", { method: "POST", body: formData });
  }

  async deleteVoiceProfile(profileId: string): Promise<void> {
    return this.request(`/voice-profiles/${profileId}`, { method: "DELETE" });
  }
}

export const api = new ApiClient();
