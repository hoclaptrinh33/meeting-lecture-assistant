/**
 * API client giao tiếp với backend FastAPI qua Caddy reverse proxy (/api)
 */

const BASE_URL = "/api";

export interface ApiError {
  code: string;
  message: string;
  fields?: Record<string, string>;
}

class ApiClient {
  private accessToken: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.accessToken = localStorage.getItem("access_token");
    }
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("access_token", token);
      } else {
        localStorage.removeItem("access_token");
      }
    }
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers = new Headers(options.headers || {});

    if (this.accessToken && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${this.accessToken}`);
    }

    if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json; charset=utf-8");
    }

    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      let errPayload: { error?: ApiError } = {};
      try {
        errPayload = await res.json();
      } catch {
        // ignore
      }
      const error: ApiError = errPayload.error || {
        code: "http_error",
        message: `Yêu cầu thất bại với mã lỗi HTTP ${res.status}.`,
      };
      throw error;
    }

    if (res.status === 204) {
      return null as T;
    }

    return res.json();
  }

  // Auth
  async register(data: any) {
    return this.request<any>("/auth/register", { method: "POST", body: JSON.stringify(data) });
  }

  async login(data: any) {
    return this.request<any>("/auth/login", { method: "POST", body: JSON.stringify(data) });
  }

  async refresh(refreshToken: string) {
    return this.request<any>("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
  }

  async logout(refreshToken: string) {
    return this.request<void>("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
  }

  async getMe() {
    return this.request<any>("/auth/me", { method: "GET" });
  }

  // Jobs
  async createJob(formData: FormData) {
    return this.request<any>("/jobs", { method: "POST", body: formData });
  }

  async listJobs(limit = 20, cursor?: string) {
    const q = new URLSearchParams({ limit: limit.toString() });
    if (cursor) q.append("cursor", cursor);
    return this.request<any>(`/jobs?${q.toString()}`, { method: "GET" });
  }

  async getJob(jobId: string) {
    return this.request<any>(`/jobs/${jobId}`, { method: "GET" });
  }

  async deleteJob(jobId: string) {
    return this.request<void>(`/jobs/${jobId}`, { method: "DELETE" });
  }

  async cancelJob(jobId: string) {
    return this.request<any>(`/jobs/${jobId}/cancel`, { method: "POST" });
  }

  async getTranscript(jobId: string, pass = 2) {
    return this.request<any>(`/jobs/${jobId}/transcript?pass=${pass}`, { method: "GET" });
  }

  async patchSegment(jobId: string, position: number, textEdited: string, pass = 2) {
    return this.request<any>(`/jobs/${jobId}/segments/${position}?pass=${pass}`, {
      method: "PATCH",
      body: JSON.stringify({ text_edited: textEdited }),
    });
  }

  async patchSpeaker(jobId: string, speakerLabel: string, displayName: string) {
    return this.request<any>(`/jobs/${jobId}/speakers/${encodeURIComponent(speakerLabel)}`, {
      method: "PATCH",
      body: JSON.stringify({ display_name: displayName }),
    });
  }

  async createHighlight(jobId: string, data: any) {
    return this.request<any>(`/jobs/${jobId}/highlights`, { method: "POST", body: JSON.stringify(data) });
  }

  async deleteHighlight(jobId: string, highlightId: string) {
    return this.request<void>(`/jobs/${jobId}/highlights/${highlightId}`, { method: "DELETE" });
  }

  async createActionItem(jobId: string, data: any) {
    return this.request<any>(`/jobs/${jobId}/action-items`, { method: "POST", body: JSON.stringify(data) });
  }

  async deleteActionItem(jobId: string, itemId: string) {
    return this.request<void>(`/jobs/${jobId}/action-items/${itemId}`, { method: "DELETE" });
  }

  async getMediaToken(jobId: string) {
    return this.request<any>(`/jobs/${jobId}/media-token`, { method: "POST" });
  }

  async exportJob(jobId: string, data: any) {
    const url = `${BASE_URL}/jobs/${jobId}/exports`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(this.accessToken ? { Authorization: `Bearer ${this.accessToken}` } : {}),
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Xuất tài liệu thất bại");
    return res.blob();
  }

  // LLM
  async cleanTranscript(jobId: string) {
    return this.request<any>(`/jobs/${jobId}/llm/clean`, { method: "POST" });
  }

  async summarizeTranscript(jobId: string, template: "meeting" | "lecture") {
    return this.request<any>(`/jobs/${jobId}/llm/summarize`, {
      method: "POST",
      body: JSON.stringify({ template }),
    });
  }

  async getLlmStatus(jobId: string, task: "clean" | "summarize") {
    return this.request<any>(`/jobs/${jobId}/llm/${task}`, { method: "GET" });
  }

  // Live
  async createLiveSession(data: any) {
    return this.request<any>("/live/sessions", { method: "POST", body: JSON.stringify(data) });
  }

  async stopLiveSession(sessionId: string) {
    return this.request<any>(`/live/sessions/${sessionId}/stop`, { method: "POST" });
  }

  async getLiveSession(sessionId: string) {
    return this.request<any>(`/live/sessions/${sessionId}`, { method: "GET" });
  }

  // Voice Profiles
  async listVoiceProfiles() {
    return this.request<any[]>("/voice-profiles", { method: "GET" });
  }

  async createVoiceProfile(formData: FormData) {
    return this.request<any>("/voice-profiles", { method: "POST", body: formData });
  }

  async deleteVoiceProfile(profileId: string) {
    return this.request<void>(`/voice-profiles/${profileId}`, { method: "DELETE" });
  }
}

export const api = new ApiClient();
