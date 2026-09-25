import {
  EnterpriseScreeningResponse,
} from "./types";

/**
 * Resolves the backend API base URL dynamically:
 * - If running in browser (client-side), automatically extracts window.location.hostname
 *   (e.g., "192.168.24.52" or "localhost") and connects to that same host on port 8000.
 *   This ensures seamless compatibility when accessed from any device on the LAN.
 * - In non-browser/SSR execution, falls back to process.env.NEXT_PUBLIC_API_BASE_URL.
 */
export function getApiBase(): string {
  if (typeof window !== "undefined" && window.location) {
    const protocol = window.location.protocol || "http:";
    const hostname = window.location.hostname;
    if (hostname) {
      return `${protocol}//${hostname}:8000/api/v1`;
    }
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://192.168.24.52:8000/api/v1";
}

/**
 * Enterprise Health Check
 * Verifies backend and Laya decision pipeline status.
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
 * Enterprise Bulk Candidate Resume Screener
 * Evaluates a batch of candidate PDF resumes against a target job requisition using the
 * zero-hallucination calibrated ConvAI Laya scoring pipeline.
 */
export async function bulkScreenEnterpriseResumes(
  files: File[],
  jobRole: string,
  jobDescription: string
): Promise<EnterpriseScreeningResponse> {
  const formData = new FormData();
  formData.append("job_role", jobRole);
  formData.append("job_description", jobDescription);
  for (const file of files) {
    formData.append("resumes", file);
  }

  const apiBase = getApiBase();
  const res = await fetch(`${apiBase}/enterprise/bulk-screen`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = `Server returned ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorMsg = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}
