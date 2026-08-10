import type {
  ClarificationItem,
  DiagnosisResult,
  InterviewState,
  Report,
  ReportMeta,
  ResumeParseResult,
} from "../types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(BASE + path, init);
  if (!response.ok) {
    let message = "请求失败，请稍后重试。";
    try {
      const data = (await response.json()) as {
        detail?: string;
        error?: string;
      };
      if (typeof data.detail === "string" && data.detail) {
        message = data.detail;
      } else if (typeof data.error === "string" && data.error) {
        message = data.error;
      }
    } catch {
      /* 忽略解析失败，使用默认提示 */
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

function json(method: string, body: unknown): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  jobs: () => request<{ labels: string[] }>("/jobs"),

  parseText: (text: string) =>
    request<ResumeParseResult>("/resume/parse", {
      method: "POST",
      body: new URLSearchParams({ text }),
    }),

  parseFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ResumeParseResult>("/resume/parse", {
      method: "POST",
      body: form,
    });
  },

  clarify: (resume_text: string) =>
    request<{ items: ClarificationItem[] }>(
      "/resume/clarify",
      json("POST", { resume_text }),
    ),

  diagnose: (payload: {
    resume_text: string;
    items: ClarificationItem[];
    market_notes: string;
    target_job: string;
    target_location: string;
  }) => request<DiagnosisResult>("/resume/diagnose", json("POST", payload)),

  startInterview: (payload: {
    job_label: string;
    num_questions: number;
    resume_text: string;
  }) => request<InterviewState>("/interview/start", json("POST", payload)),

  answer: (state: InterviewState, answer: string) =>
    request<InterviewState>(
      "/interview/answer",
      json("POST", { state, answer }),
    ),

  followupAnswer: (state: InterviewState, answer: string) =>
    request<InterviewState>(
      "/interview/followup-answer",
      json("POST", { state, answer }),
    ),

  followup: (state: InterviewState) =>
    request<InterviewState>("/interview/followup", json("POST", { state })),

  next: (state: InterviewState) =>
    request<InterviewState>("/interview/next", json("POST", { state })),

  finish: (state: InterviewState) =>
    request<InterviewState>("/interview/finish", json("POST", { state })),

  generateReport: (state: InterviewState) =>
    request<Report>("/reports/generate", json("POST", { state })),

  listReports: () => request<{ reports: ReportMeta[] }>("/reports"),

  loadReport: (id: string) => request<Report>(`/reports/${id}`),

  deleteReport: (id: string) =>
    request<{ ok: boolean }>(`/reports/${id}`, { method: "DELETE" }),
};
