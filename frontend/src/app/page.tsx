"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { JobRequisitionCard } from "@/components/recruitment/JobRequisitionCard";
import { RecruiterQuestionStudio } from "@/components/recruitment/RecruiterQuestionStudio";
import { ResumeUploadManager } from "@/components/recruitment/ResumeUploadManager";
import { CandidateStreamingLeaderboard } from "@/components/recruitment/CandidateStreamingLeaderboard";
import { ParsedCandidateDrawer } from "@/components/recruitment/ParsedCandidateDrawer";
import { PdfViewerModal } from "@/components/PdfViewerModal";
import {
  analyzeJob,
  checkBackendHealth,
  getResumeDetail,
  reparseResume,
  streamCandidateEvaluations,
  updateJobQuestions,
  uploadResumes,
} from "@/lib/api";
import {
  CandidateEvaluationItem,
  EvaluationQuestionItem,
  JobRequisition,
  ResumeUploadItem,
} from "@/lib/types";
import { AlertCircle, CheckCircle2 } from "lucide-react";

const INITIAL_ROLE = "Senior Full-Stack AI Engineer";
const INITIAL_JD = `We are looking for a Senior Full-Stack AI Engineer with 5+ years of experience building scalable backend microservices and high-performance APIs. The ideal candidate should be proficient in Python, FastAPI, TypeScript, React, and Next.js.
Requirements:
• 5+ years of experience building scalable backend microservices and high-performance APIs.
• Proficient in Python, FastAPI, TypeScript, React, and Next.js.
• Strong hands-on experience with PostgreSQL, Redis, Docker, and Kubernetes.
• Experience with AI application frameworks, vector databases, and deterministic scoring pipelines.
• Demonstrated ownership of distributed cloud systems handling high concurrent throughput.`;

export default function Home() {
  // Navigation & Engine selection
  const [activeSidebarTab, setActiveSidebarTab] = useState("Candidate Screening");
  const [activeEngine, setActiveEngine] = useState<"laya" | "jev">("laya");
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "checking">("online");

  // Requisition State
  const [jobRole, setJobRole] = useState(INITIAL_ROLE);
  const [jobDescription, setJobDescription] = useState(INITIAL_JD);
  const [requisition, setRequisition] = useState<JobRequisition | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isQuestionStudioOpen, setIsQuestionStudioOpen] = useState(false);
  const [isSavingQuestions, setIsSavingQuestions] = useState(false);

  // Resume Upload State
  const [uploadedResumes, setUploadedResumes] = useState<ResumeUploadItem[]>([]);
  const [fileObjectsMap, setFileObjectsMap] = useState<Map<string, File>>(new Map());
  const [isUploading, setIsUploading] = useState(false);

  // Evaluation & SSE Stream State
  const [evaluations, setEvaluations] = useState<CandidateEvaluationItem[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Inspection Drawer State
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateEvaluationItem | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // PDF Viewer Modal
  const [pdfModalFile, setPdfModalFile] = useState<File | null>(null);
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);

  // Notification Toast Banner
  const [notification, setNotification] = useState<{
    type: "success" | "error" | "info";
    message: string;
  } | null>(null);

  const showNotification = (type: "success" | "error" | "info", message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((curr) => (curr?.message === message ? null : curr));
    }, 6000);
  };

  // Health check on mount
  useEffect(() => {
    checkBackendHealth()
      .then((health) => {
        if (health.status === "healthy" || health.status === "online") {
          setBackendStatus("online");
        } else {
          setBackendStatus("offline");
        }
      })
      .catch(() => setBackendStatus("offline"));
  }, []);

  // Poll status for queued/parsing resumes
  useEffect(() => {
    const pendingResumes = uploadedResumes.filter(
      (r) => r.status === "queued" || r.status === "parsing"
    );
    if (pendingResumes.length === 0) return;

    const intervalId = setInterval(async () => {
      for (const pending of pendingResumes) {
        try {
          const detail = await getResumeDetail(pending.resume_id);
          if (detail.status === "completed" || detail.status === "failed") {
            setUploadedResumes((prev) =>
              prev.map((r) =>
                r.resume_id === pending.resume_id
                  ? {
                      ...r,
                      status: detail.status as any,
                      error_message: detail.error_message,
                    }
                  : r
              )
            );
            if (detail.status === "completed") {
              showNotification(
                "success",
                `Resume '${detail.filename}' parsed and ready for evaluation!`
              );
            } else if (detail.status === "failed") {
              showNotification(
                "error",
                `Failed to parse '${detail.filename}': ${detail.error_message || "Document error"}`
              );
            }
          }
        } catch {
          // Ignore transient polling error
        }
      }
    }, 4000);

    return () => clearInterval(intervalId);
  }, [uploadedResumes]);

  // 1. Analyze Job Requisition
  const handleAnalyzeJob = async () => {
    if (!jobRole.trim() || !jobDescription.trim()) return;

    setIsAnalyzing(true);
    setNotification(null);

    try {
      const result = await analyzeJob(jobRole.trim(), jobDescription.trim());
      setRequisition(result);

      if (result.cached) {
        showNotification(
          "success",
          "Requisition criteria retrieved instantly from cache (SHA-256 matched)."
        );
      } else {
        showNotification(
          "success",
          `Synthesized ${Object.keys(result.questions || {}).length} universal criteria items from job requisition.`
        );
      }

      if (!result.is_reviewed) {
        setIsQuestionStudioOpen(true);
      }
    } catch (err: any) {
      showNotification("error", err.message || "Failed to analyze job description.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 2. Save & Lock Questions
  const handleSaveQuestions = async (updatedQuestions: Record<string, EvaluationQuestionItem>) => {
    if (!requisition) return;
    setIsSavingQuestions(true);

    try {
      const updated = await updateJobQuestions(requisition.job_id, updatedQuestions);
      setRequisition((prev) =>
        prev
          ? {
              ...prev,
              is_reviewed: updated.is_reviewed,
              questions: updated.questions,
            }
          : null
      );
      showNotification(
        "success",
        `Criteria locked successfully! ${updated.mandatory_gates_count} dealbreaker gates active. Candidate evaluation is now unlocked.`
      );
    } catch (err: any) {
      showNotification("error", err.message || "Failed to lock questions.");
    } finally {
      setIsSavingQuestions(false);
    }
  };

  // 3. Upload Resumes
  const handleUploadFiles = async (files: File[]) => {
    setIsUploading(true);
    try {
      const nextMap = new Map(fileObjectsMap);
      files.forEach((f) => nextMap.set(f.name, f));
      setFileObjectsMap(nextMap);

      const batchResponse = await uploadResumes(files);

      setUploadedResumes((prev) => {
        const existingIds = new Set(prev.map((r) => r.resume_id));
        const newItems = batchResponse.resumes.filter((r) => !existingIds.has(r.resume_id));
        return [...prev, ...newItems];
      });

      if (batchResponse.cached_count > 0) {
        showNotification(
          "success",
          `${batchResponse.cached_count} resumes recognized from DB cache (0s latency). ${batchResponse.queued_count} queued for rate-limited parsing.`
        );
      } else {
        showNotification(
          "info",
          `${batchResponse.total_uploaded} resumes added to parser queue.`
        );
      }
    } catch (err: any) {
      showNotification("error", err.message || "Failed to upload resume files.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveResume = (resumeId: string) => {
    setUploadedResumes((prev) => prev.filter((r) => r.resume_id !== resumeId));
    setEvaluations((prev) => prev.filter((e) => e.resume_id !== resumeId));
  };

  const handleReparseResume = async (resumeId: string) => {
    try {
      const resp = await reparseResume(resumeId);
      setUploadedResumes((prev) =>
        prev.map((r) =>
          r.resume_id === resumeId
            ? {
                ...r,
                status: "parsing",
                error_message: undefined,
                eta_seconds: resp.eta_seconds || 20,
              }
            : r
        )
      );
      showNotification(
        "info",
        "Re-parsing resume with high-precision model. Extraction will complete shortly."
      );
    } catch (err: any) {
      showNotification("error", err.message || "Failed to trigger re-parse.");
    }
  };


  // 4. Inspect Resume Directly
  const handleInspectResume = async (resumeId: string) => {
    try {
      const detail = await getResumeDetail(resumeId);
      const tempCandidate: CandidateEvaluationItem = {
        evaluation_id: `inspect_${resumeId}`,
        job_id: requisition?.job_id || "general",
        resume_id: resumeId,
        candidate_name:
          detail.parsed_sections?.candidate_name || detail.filename.replace(".pdf", ""),
        pipeline: activeEngine,
        fit_score: 0,
        verdict: "HOLD",
        status: "PARSED",
        breakdown: {},
        parsedSections: detail.parsed_sections,
      };

      setSelectedCandidate(tempCandidate);
      setIsDrawerOpen(true);
    } catch (err: any) {
      showNotification("error", err.message || "Failed to fetch parsed resume details.");
    }
  };

  // 5. Start Incremental Streaming Evaluation (SSE)
  const handleStartStreaming = () => {
    if (!requisition) {
      showNotification("error", "Please synthesize a job requisition first.");
      return;
    }
    if (!requisition.is_reviewed) {
      showNotification(
        "error",
        "Recruiter review required: Please confirm criteria in the Question Studio first."
      );
      setIsQuestionStudioOpen(true);
      return;
    }
    if (uploadedResumes.length === 0) {
      showNotification("error", "Please upload at least one candidate resume PDF.");
      return;
    }

    setIsStreaming(true);
    setEvaluations([]);

    const resumeIds = uploadedResumes.map((r) => r.resume_id);

    streamCandidateEvaluations(
      requisition.job_id,
      resumeIds,
      activeEngine,
      (newCandidate) => {
        setEvaluations((prev) => {
          const index = prev.findIndex((c) => c.resume_id === newCandidate.resume_id);
          if (index >= 0) {
            const next = [...prev];
            next[index] = newCandidate;
            return next;
          }
          return [...prev, newCandidate];
        });
      },
      (summary) => {
        setIsStreaming(false);
        showNotification(
          "success",
          `Screening stream completed! Evaluated ${summary.total_evaluated || resumeIds.length} candidates.`
        );
      },
      (error) => {
        setIsStreaming(false);
        showNotification("error", `Streaming error: ${error}`);
      }
    );
  };

  // Open PDF viewer modal
  const handleViewPdf = (candidateName: string) => {
    const entries = Array.from(fileObjectsMap.entries());
    for (const [filename, file] of entries) {
      if (
        filename.toLowerCase().includes(candidateName.toLowerCase().split(" ")[0]) ||
        candidateName.toLowerCase().includes(filename.replace(".pdf", "").toLowerCase())
      ) {
        setPdfModalFile(file);
        setIsPdfModalOpen(true);
        return;
      }
    }
    const firstFile = Array.from(fileObjectsMap.values())[0];
    if (firstFile) {
      setPdfModalFile(firstFile);
      setIsPdfModalOpen(true);
    } else {
      showNotification("info", "Original PDF binary not available in local browser session.");
    }
  };

  const canEvaluate = Boolean(
    requisition && requisition.is_reviewed && uploadedResumes.length > 0
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans antialiased text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* Top Application Command Header */}
      <Header
        backendStatus={backendStatus}
        activeEngine={activeEngine === "jev" ? "typesafe" : "laya_local"}
        onEngineChange={(eng) => setActiveEngine(eng === "typesafe" ? "jev" : "laya")}
      />

      {/* Main Workspace: Sidebar + 2-Column Split Layout */}
      <div className="flex-1 flex w-full">
        {/* Sleek Icon Rail Sidebar */}
        <Sidebar activeTab={activeSidebarTab} onSelectTab={setActiveSidebarTab} />

        {/* 2-Column Split Content Canvas */}
        <main className="flex-1 p-4 sm:p-6 min-w-0 max-w-[1600px] mx-auto w-full space-y-4">
          {/* Notification Alert Banner */}
          {notification && (
            <div
              className={`p-3.5 rounded-xl border flex items-center justify-between text-xs font-semibold animate-in fade-in slide-in-from-top-1 duration-150 shadow-2xs ${
                notification.type === "success"
                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                  : notification.type === "error"
                  ? "bg-rose-50 text-rose-800 border-rose-200"
                  : "bg-indigo-50 text-indigo-800 border-indigo-200"
              }`}
            >
              <div className="flex items-center gap-2">
                {notification.type === "success" ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 shrink-0" />
                )}
                <span>{notification.message}</span>
              </div>
              <button
                type="button"
                onClick={() => setNotification(null)}
                className="text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* Responsive 2-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left Column (5 of 12 cols): Job Requisition & Ingestion Dropzone */}
            <div className="lg:col-span-5 space-y-4">
              <JobRequisitionCard
                jobRole={jobRole}
                setJobRole={setJobRole}
                jobDescription={jobDescription}
                setJobDescription={setJobDescription}
                onAnalyze={handleAnalyzeJob}
                isLoading={isAnalyzing}
                requisition={requisition}
                onOpenQuestionStudio={() => setIsQuestionStudioOpen(true)}
              />

              <ResumeUploadManager
                uploadedResumes={uploadedResumes}
                onUploadFiles={handleUploadFiles}
                isUploading={isUploading}
                onInspectResume={handleInspectResume}
                onRemoveResume={handleRemoveResume}
                onReparseResume={handleReparseResume}
                fileObjectsMap={fileObjectsMap}
              />
            </div>

            {/* Right Column (7 of 12 cols): Real-Time Screening Leaderboard */}
            <div className="lg:col-span-7">
              <CandidateStreamingLeaderboard
                requisition={requisition}
                evaluations={evaluations}
                isStreaming={isStreaming}
                onStartStreaming={handleStartStreaming}
                canEvaluate={canEvaluate}
                evaluationCount={evaluations.length}
                totalUploads={uploadedResumes.length}
                onInspectCandidate={(cand) => {
                  setSelectedCandidate(cand);
                  setIsDrawerOpen(true);
                }}
                onViewPdf={handleViewPdf}
                activeEngine={activeEngine}
              />
            </div>
          </div>
        </main>
      </div>

      {/* Recruiter Question Studio Modal */}
      <RecruiterQuestionStudio
        isOpen={isQuestionStudioOpen}
        onClose={() => setIsQuestionStudioOpen(false)}
        requisition={requisition}
        onSaveQuestions={handleSaveQuestions}
        isSaving={isSavingQuestions}
      />

      {/* Candidate Dossier Slide-Over Drawer */}
      <ParsedCandidateDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        candidate={selectedCandidate}
        requisition={requisition}
        onViewPdf={handleViewPdf}
      />

      {/* Original PDF Document Viewer Modal */}
      <PdfViewerModal
        isOpen={isPdfModalOpen}
        onClose={() => setIsPdfModalOpen(false)}
        file={pdfModalFile}
        title={pdfModalFile?.name || "Candidate Resume PDF"}
      />
    </div>
  );
}
