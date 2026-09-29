/**
 * CareerLens AI - Unified Frontend API Client
 * Clean HTTP and Server-Sent Events (SSE) client for backend communication.
 */

import {
  CandidateEvaluationItem,
  EvaluationQuestionItem,
  JobAnalyzeResponse,
  JobEvaluationSummaryResponse,
  JobQuestionsUpdateResponse,
  JobRequisition,
  ResumeDetailResponse,
  ResumeUploadBatchResponse,
  ResumeUploadItem,
} from "./types";

/**
 * Resolves the backend API base URL dynamically.
 */
export function getApiBase(): string {
  if (typeof window !== "undefined" && window.location) {
    const protocol = window.location.protocol || "http:";
    const hostname = window.location.hostname;
    if (hostname) {
      return `${protocol}//${hostname}:8000/api/v1`;
    }
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";
}

/**
 * Health check
 */
export async function checkBackendHealth(): Promise<{
  status: string;
  service: string;
  version?: string;
  pipeline?: string;
}> {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/health`, { cache: "no-store" });
    if (!res.ok) throw new Error("Backend unreachable");
    return await res.json();
  } catch {
    return { status: "offline", service: "careerlens-enterprise" };
  }
}

/**
 * 1. Analyze Job Requisition & Generate Dynamic Questions
 */
export async function analyzeJob(
  roleTitle: string,
  jobDescription: string
): Promise<JobRequisition> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/jobs/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      role_title: roleTitle,
      job_description: jobDescription,
    }),
  });

  if (!res.ok) {
    let errorMsg = `Server error ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorMsg = errJson.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * 2. Get Job Requisition
 */
export async function getJob(jobId: string): Promise<JobRequisition> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/jobs/${jobId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load job ${jobId}`);
  return await res.json();
}

/**
 * 3. Update / Review Questions (Mandatory Precondition Gate)
 */
export async function updateJobQuestions(
  jobId: string,
  questions: Record<string, EvaluationQuestionItem>
): Promise<{
  job_id: string;
  is_reviewed: boolean;
  total_questions: number;
  mandatory_gates_count: number;
  questions: Record<string, EvaluationQuestionItem>;
}> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/jobs/${jobId}/questions`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ questions }),
  });

  if (!res.ok) {
    let errorMsg = `Server error ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * 4. Upload Resumes (Deduplication + Rate-Limited Queue)
 */
export async function uploadResumes(files: File[]): Promise<ResumeUploadBatchResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/resumes/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = `Upload failed (${res.status})`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * 5. Get Granular Parsed Resume Details (6 Canonical Sections)
 */
export async function getResumeDetail(resumeId: string): Promise<ResumeDetailResponse> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/resumes/${resumeId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch resume details for ${resumeId}`);
  return await res.json();
}

/**
 * 5b. Re-parse Failed or Disrupted Resume
 */
export async function reparseResume(resumeId: string): Promise<ResumeUploadItem> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/resumes/${resumeId}/reparse`, {
    method: "POST",
  });
  if (!res.ok) {
    let errorMsg = `Re-parse request failed (${res.status})`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {}
    throw new Error(errorMsg);
  }
  return await res.json();
}


/**
 * 6. Synchronous Candidate Evaluation
 */
export async function evaluateCandidatesSync(
  jobId: string,
  resumeIds: string[],
  pipeline: "laya" | "jev" = "laya"
): Promise<JobEvaluationSummaryResponse> {
  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/jobs/${jobId}/evaluations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_ids: resumeIds,
      pipeline,
    }),
  });

  if (!res.ok) {
    let errorMsg = `Evaluation failed (${res.status})`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * 7. Real-Time Incremental Streaming Evaluation (SSE)
 * Yields candidates immediately as each individual inference completes.
 */
export async function streamCandidateEvaluations(
  jobId: string,
  resumeIds: string[],
  pipeline: "laya" | "jev" = "laya",
  onCandidateEvaluated: (candidate: CandidateEvaluationItem) => void,
  onCompleted: (summary: any) => void,
  onError: (error: string) => void
): Promise<void> {
  const apiBase = getApiBase();
  try {
    const res = await fetch(`${apiBase}/jobs/${jobId}/evaluations/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_ids: resumeIds,
        pipeline,
      }),
    });

    if (!res.ok) {
      let errorMsg = `Streaming evaluation failed (${res.status})`;
      try {
        const err = await res.json();
        if (err.detail) errorMsg = err.detail;
      } catch {}
      onError(errorMsg);
      return;
    }

    if (!res.body) {
      onError("Streaming response body is null");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const block of lines) {
        if (!block.trim()) continue;
        const blockLines = block.split("\n");
        let eventType = "";
        let dataPayload = "";

        for (const line of blockLines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim();
          } else if (line.startsWith("data:")) {
            dataPayload = line.replace("data:", "").trim();
          }
        }

        if (eventType === "candidate_evaluated" && dataPayload) {
          try {
            const parsed = JSON.parse(dataPayload);
            if (parsed.evaluation) {
              onCandidateEvaluated(parsed.evaluation);
            }
          } catch (e) {
            console.error("Failed to parse candidate_evaluated payload", e);
          }
        } else if (eventType === "completed" && dataPayload) {
          try {
            const parsed = JSON.parse(dataPayload);
            onCompleted(parsed);
          } catch (e) {
            console.error("Failed to parse completed payload", e);
          }
        }
      }
    }
  } catch (err: any) {
    onError(err.message || "Network error during streaming evaluation.");
  }
}
