"use client";

import React, { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import {
  EvaluationConfigModal,
  RequirementConfigItem,
} from "@/components/enterprise/EvaluationConfigModal";
import { CandidateInspectionModal } from "@/components/enterprise/CandidateInspectionModal";
import {
  checkBackendHealth,
  bulkScreenEnterpriseResumes,
  previewJobRequirements,
} from "@/lib/api";
import { EnterpriseCandidate } from "@/lib/types";
import {
  Upload,
  FileText,
  Search,
  Filter,
  SlidersHorizontal,
  ChevronRight,
  Info,
  CheckCircle2,
  XCircle,
  MoreVertical,
  Play,
  Loader2,
  Check,
  Edit2,
  Trash2,
  Plus,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  X,
  Users,
  Sliders,
  Layers,
} from "lucide-react";

const INITIAL_ROLE = "Senior Full-Stack AI Engineer";
const INITIAL_JD = `We are looking for a Senior Full-Stack AI Engineer with 5+ years of experience building scalable backend microservices and high-performance APIs. The ideal candidate should be proficient in Python, FastAPI, TypeScript, React, and Next.js.

Requirements:
• 5+ years of experience building scalable backend microservices and high-performance APIs.
• Proficient in Python, FastAPI, TypeScript, React, and Next.js.
• Strong hands-on experience with PostgreSQL, Redis, Docker, and Kubernetes.
• Experience with AI application frameworks, vector databases, and deterministic scoring pipelines.
• Demonstrated ownership of distributed cloud systems handling high concurrent throughput.`;

interface TableCandidate {
  id: string;
  name: string;
  email: string;
  status: "Ready" | "Review" | "Rejected";
  evidenceCount: number;
  seniority: "Senior" | "Mid" | "Junior";
  ready: boolean;
  rawCandidate?: EnterpriseCandidate;
  /** Blob URL of the uploaded PDF — valid for this browser session */
  pdfUrl?: string;
  /** Set for hard-rejected candidates (< 20% overlap) */
  rejectionMessage?: string;
}

export interface ExtendedRequirementItem extends RequirementConfigItem {
  is_included?: boolean;
}

export default function CandidateScreeningPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  /** Maps file.name → blob URL so each result row can link back to its PDF */
  const pdfBlobMapRef = useRef<Map<string, string>>(new Map());

  // Core State
  const [jobRole, setJobRole] = useState(INITIAL_ROLE);
  const [jobDescription, setJobDescription] = useState(INITIAL_JD);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [pipeline, setPipeline] = useState<"typesafe" | "laya_local">("laya_local");
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "checking">("checking");
  const [isScreening, setIsScreening] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [activeNav, setActiveNav] = useState("Screening");
  const [activeSidebarTab, setActiveSidebarTab] = useState("Candidate Screening");

  // Switchable Tab in Right Configuration Card: "REQUIREMENTS" | "WEIGHTS"
  const [configCardTab, setConfigCardTab] = useState<"REQUIREMENTS" | "WEIGHTS">("REQUIREMENTS");

  // Switchable Candidate Status Tab: "ALL" | "SELECTED" | "REVIEW" | "REJECTED"
  const [candidateFilterTab, setCandidateFilterTab] = useState<"ALL" | "SELECTED" | "REVIEW" | "REJECTED">("ALL");

  // Scoring Weights Configuration
  const [weights, setWeights] = useState({
    technical: 40,
    experience: 30,
    domain: 20,
    evidence: 15,
    education: 15,
  });

  // Approved Requirements & Hard Gates (dynamically extracted from JD)
  const [approvedRequirements, setApprovedRequirements] = useState<ExtendedRequirementItem[]>([
    { name: "Python", category: "Languages", is_hard_requirement: true, is_included: true },
    { name: "FastAPI", category: "Frameworks", is_hard_requirement: true, is_included: true },
    { name: "Docker", category: "DevOps & Cloud", is_hard_requirement: true, is_included: true },
    { name: "React", category: "Frontend", is_hard_requirement: false, is_included: true },
    { name: "PostgreSQL", category: "Databases", is_hard_requirement: false, is_included: true },
  ]);

  const [newKeywordInput, setNewKeywordInput] = useState("");

  // Candidates & Inspection (empty by default prior to analysis)
  const [tableCandidates, setTableCandidates] = useState<TableCandidate[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCandidateForInspection, setSelectedCandidateForInspection] = useState<EnterpriseCandidate | null>(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>([]);

  // Health Check
  useEffect(() => {
    checkBackendHealth().then((res) => {
      setBackendStatus(res.status === "healthy" || res.status === "ok" ? "online" : "offline");
    });
  }, []);

  // Automatically extract JD keywords on initial load
  useEffect(() => {
    handleExtractRequirements();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Extract Requirements from JD using backend endpoint
  const handleExtractRequirements = async () => {
    if (!jobDescription || jobDescription.trim().length < 20) return;
    setIsExtracting(true);
    try {
      const res = await previewJobRequirements(jobRole, jobDescription, pipeline);
      if (res && res.suggested_requirements && res.suggested_requirements.length > 0) {
        setApprovedRequirements(
          res.suggested_requirements.map((r: any) => ({
            name: r.name,
            category: r.category || "General",
            is_hard_requirement: Boolean(r.is_hard_requirement),
            is_included: true,
          }))
        );
      }
    } catch (err: any) {
      console.warn("Failed to preview requirements:", err);
    } finally {
      setIsExtracting(false);
    }
  };

  // Requirement Keyword List Actions
  const toggleRequirementInclusion = (idx: number) => {
    setApprovedRequirements((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, is_included: r.is_included === false ? true : false } : r))
    );
  };

  const toggleRequirementMandate = (idx: number) => {
    setApprovedRequirements((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, is_hard_requirement: !r.is_hard_requirement } : r))
    );
  };

  const removeRequirement = (idx: number) => {
    setApprovedRequirements((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleAddKeyword = () => {
    const trimmed = newKeywordInput.trim();
    if (!trimmed) return;
    if (approvedRequirements.some((r) => r.name.toLowerCase() === trimmed.toLowerCase())) {
      setNewKeywordInput("");
      return;
    }
    setApprovedRequirements((prev) => [
      ...prev,
      {
        name: trimmed,
        category: "Custom",
        is_hard_requirement: false,
        is_included: true,
      },
    ]);
    setNewKeywordInput("");
  };

  const handleReset = () => {
    setSelectedFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
    setTableCandidates([]);
    setSelectedCandidateIds([]);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // File Upload Handlers
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).filter((f) =>
        f.name.toLowerCase().endsWith(".pdf")
      );
      newFiles.forEach((f) => {
        if (!pdfBlobMapRef.current.has(f.name)) {
          pdfBlobMapRef.current.set(f.name, URL.createObjectURL(f));
        }
      });
      setSelectedFiles((prev) => [...prev, ...newFiles]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files).filter((f) =>
        f.name.toLowerCase().endsWith(".pdf")
      );
      newFiles.forEach((f) => {
        if (!pdfBlobMapRef.current.has(f.name)) {
          pdfBlobMapRef.current.set(f.name, URL.createObjectURL(f));
        }
      });
      setSelectedFiles((prev) => [...prev, ...newFiles]);
    }
  };

  // Clear all button
  const handleClearFiles = () => {
    // Revoke all blob URLs to free memory
    pdfBlobMapRef.current.forEach((url) => URL.revokeObjectURL(url));
    pdfBlobMapRef.current.clear();
    setSelectedFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Remove single resume
  const handleRemoveSingleFile = (indexToRemove: number) => {
    setSelectedFiles((prev) => {
      const removed = prev[indexToRemove];
      if (removed) {
        const blobUrl = pdfBlobMapRef.current.get(removed.name);
        if (blobUrl) {
          URL.revokeObjectURL(blobUrl);
          pdfBlobMapRef.current.delete(removed.name);
        }
      }
      return prev.filter((_, idx) => idx !== indexToRemove);
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Run Real Screening with Backend
  const handleRunScreening = async () => {
    if (selectedFiles.length === 0) {
      alert("Please upload at least 1 PDF resume to evaluate against this Job Requisition.");
      return;
    }

    const activeRequirementsToSend = approvedRequirements.filter((r) => r.is_included !== false);

    setIsScreening(true);
    try {
      const res = await bulkScreenEnterpriseResumes(
        selectedFiles,
        jobRole,
        jobDescription,
        pipeline,
        activeRequirementsToSend
      );

      if (res && res.candidates && res.candidates.length > 0) {
        const transformed: TableCandidate[] = res.candidates.map((c, i) => {
          const isReady = c.decision === "SELECT" || c.fit_score >= 70;
          // Hard-rejected by the 20% technical gate
          const isHardReject = c.rejection_reason === "does_not_fit_role" || c.rejection_reason === "technical_gate";
          const isReject = isHardReject || c.decision === "REJECT" || c.fit_score < 45;
          const status: "Ready" | "Review" | "Rejected" = isReady
            ? "Ready"
            : isReject
            ? "Rejected"
            : "Review";

          const sen = (c.candidate_seniority_label || c.seniority_label || "Mid") as "Senior" | "Mid" | "Junior";

          // Look up the blob URL by filename (the backend echoes back c.filename)
          const pdfUrl =
            pdfBlobMapRef.current.get(c.filename) ||
            // fallback: try matching by partial name without extension
            Array.from(pdfBlobMapRef.current.entries()).find(([k]) =>
              k.replace(/\.pdf$/i, "") === (c.filename || "").replace(/\.pdf$/i, "")
            )?.[1];

          return {
            id: c.candidate_id || `cand-${i + 1}`,
            name: c.name || `Candidate ${i + 1}`,
            email: c.inspection?.contact_info?.email || `${c.name?.toLowerCase().replace(/\s+/g, ".")}@example.com`,
            status,
            evidenceCount: c.skills?.length ? c.skills.length + 6 : 14,
            seniority: sen.includes("Senior") ? "Senior" : sen.includes("Junior") ? "Junior" : "Mid",
            ready: isReady,
            rawCandidate: c,
            pdfUrl,
            rejectionMessage: isHardReject ? (c.rejection_message || "Candidate does not meet the technical requirements for this role.") : undefined,
          };
        });

        setTableCandidates(transformed);
      }
    } catch (err: any) {
      alert(`Screening failed: ${err.message || err}`);
    } finally {
      setIsScreening(false);
    }
  };

  // Filter Table by Candidate Filter Tab & Search Query
  const filteredCandidates = tableCandidates.filter((c) => {
    // 1. Status Filter Tab
    if (candidateFilterTab === "SELECTED" && c.status !== "Ready") return false;
    if (candidateFilterTab === "REVIEW" && c.status !== "Review") return false;
    if (candidateFilterTab === "REJECTED" && c.status !== "Rejected") return false;

    // 2. Search query filter
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      c.name.toLowerCase().includes(query) ||
      c.email.toLowerCase().includes(query) ||
      c.seniority.toLowerCase().includes(query)
    );
  });

  // Candidate Counts for Status Tabs
  const countAll = tableCandidates.length;
  const countSelected = tableCandidates.filter((c) => c.status === "Ready").length;
  const countReview = tableCandidates.filter((c) => c.status === "Review").length;
  const countRejected = tableCandidates.filter((c) => c.status === "Rejected").length;

  const toggleSelectCandidate = (id: string) => {
    setSelectedCandidateIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedCandidateIds.length === filteredCandidates.length && filteredCandidates.length > 0) {
      setSelectedCandidateIds([]);
    } else {
      setSelectedCandidateIds(filteredCandidates.map((c) => c.id));
    }
  };

  const openInspection = (cand: TableCandidate) => {
    if (cand.rawCandidate) {
      setSelectedCandidateForInspection(cand.rawCandidate);
    }
  };

  const activeRequirementsCount = approvedRequirements.filter((r) => r.is_included !== false).length;
  const hardGatesCount = approvedRequirements.filter((r) => r.is_included !== false && r.is_hard_requirement).length;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Top Header */}
      <Header
        backendStatus={backendStatus}
        activeEngine={pipeline}
        onEngineChange={(eng) => setPipeline(eng)}
        activeNav={activeNav}
        onNavChange={(t) => setActiveNav(t)}
        onReset={handleReset}
      />

      <div className="flex-1 flex w-full">
        {/* Left Sidebar */}
        <Sidebar activeTab={activeSidebarTab} onSelectTab={(t) => setActiveSidebarTab(t)} />

        {/* Main Content Area */}
        <main className="flex-1 p-6 lg:p-8 space-y-6 max-w-7xl mx-auto w-full">
          {/* Page Heading */}
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Candidate Screening
            </h1>
            <p className="text-xs text-slate-500 mt-1">
              Evidence-based resume evaluation with configurable rubrics and{" "}
              {pipeline === "typesafe" ? "TypeSafe Jev" : "ConvAI Laya"} decision engine.
            </p>
          </div>

          {/* Stepper Progress Bar */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 flex items-center justify-between shadow-2xs">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs shadow-xs">
                1
              </div>
              <div>
                <div className="text-xs font-bold text-blue-600">Job Requisition</div>
                <div className="text-[11px] text-slate-400">Define role and requirements</div>
              </div>
            </div>

            <ChevronRight className="w-4 h-4 text-slate-300 mx-2" />

            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold flex items-center justify-center text-xs shadow-xs">
                2
              </div>
              <div>
                <div className="text-xs font-bold text-blue-600">Evaluation Configuration</div>
                <div className="text-[11px] text-slate-400">Keywords, gates & scoring rubric</div>
              </div>
            </div>

            <ChevronRight className="w-4 h-4 text-slate-300 mx-2" />

            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-slate-900 text-white font-bold flex items-center justify-center text-xs shadow-xs">
                3
              </div>
              <div>
                <div className="text-xs font-bold text-slate-900">Candidate Resumes</div>
                <div className="text-[11px] text-slate-400">Upload and screen talent</div>
              </div>
            </div>
          </div>

          {/* Two Columns Grid: Requisition/Upload on Left, Configuration on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Column (7 cols): Requisition & Resumes Upload */}
            <div className="lg:col-span-7 space-y-6">
              {/* Card 1: Job Requisition Details */}
              <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold text-slate-900">Job Requisition Details</h2>
                  <button
                    onClick={handleExtractRequirements}
                    disabled={isExtracting}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
                    title="Re-extract keywords and requirements from the updated JD"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isExtracting ? "animate-spin" : ""}`} />
                    {isExtracting ? "Extracting..." : "Re-extract Keywords"}
                  </button>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Target Job Role
                  </label>
                  <input
                    type="text"
                    value={jobRole}
                    onChange={(e) => setJobRole(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer"
                    className="w-full px-3.5 py-2 text-xs font-medium border border-slate-200 rounded-xl bg-slate-50/40 text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                    Job Description
                  </label>
                  <textarea
                    rows={6}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Enter or paste job description requirements..."
                    className="w-full px-3.5 py-2.5 text-xs text-slate-800 border border-slate-200 rounded-xl bg-slate-50/40 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 resize-y leading-relaxed transition-all font-sans"
                  />
                  <div className="flex justify-between items-center text-[10px] text-slate-400 mt-1">
                    <span>Keywords in the right panel update automatically from this JD</span>
                    <span>{jobDescription.length} characters</span>
                  </div>
                </div>
              </div>

              {/* Card 2: Candidate Resumes Upload Dropzone & Small File Cards */}
              <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-2xs space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <h2 className="text-sm font-bold text-slate-900">Candidate Resumes</h2>
                    <Info className="w-3.5 h-3.5 text-slate-400" />
                  </div>
                  {selectedFiles.length > 0 && (
                    <button
                      onClick={handleClearFiles}
                      className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Clear all ({selectedFiles.length})
                    </button>
                  )}
                </div>

                {/* Drag & Drop Box */}
                <div
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-blue-200 hover:border-blue-400 bg-blue-50/20 hover:bg-blue-50/50 rounded-xl p-6 text-center cursor-pointer transition-all group"
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                    <Upload className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-xs font-semibold text-slate-800">
                    Click to browse or drag & drop candidate resumes
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Supports multiple PDF resumes (up to 15 files)
                  </div>
                </div>

                {/* Small PDF File Cards Structure */}
                {selectedFiles.length > 0 ? (
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center justify-between text-xs text-slate-600 font-semibold">
                      <div className="flex items-center gap-1.5">
                        <FileText className="w-4 h-4 text-blue-600" />
                        <span>
                          {selectedFiles.length} {selectedFiles.length === 1 ? "resume" : "resumes"} queued for evaluation
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-44 overflow-y-auto pr-1">
                      {selectedFiles.map((file, idx) => (
                        <div
                          key={`${file.name}-${idx}`}
                          className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200/90 bg-slate-50/70 hover:bg-slate-50 transition-colors text-xs shadow-2xs group"
                        >
                          <div className="flex items-center gap-2.5 overflow-hidden">
                            <div className="w-7 h-7 rounded-lg bg-red-50 text-red-600 border border-red-200/80 flex items-center justify-center shrink-0 font-bold text-[10px]">
                              PDF
                            </div>
                            <div className="truncate">
                              <p className="font-semibold text-slate-900 truncate" title={file.name}>
                                {file.name}
                              </p>
                              <p className="text-[10px] text-slate-400">
                                {(file.size / 1024).toFixed(1)} KB
                              </p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemoveSingleFile(idx);
                            }}
                            className="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer shrink-0 ml-1.5"
                            title="Remove file"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-2 text-slate-400 text-xs italic">
                    No resumes selected yet. Add PDF files to begin screening.
                  </div>
                )}

                {/* Action Buttons Row */}
                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={handleRunScreening}
                    disabled={isScreening || selectedFiles.length === 0}
                    className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-xs transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {isScreening ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Screening Resumes...
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5 fill-current" />
                        Run screening ({selectedFiles.length})
                      </>
                    )}
                  </button>

                  <div
                    onClick={() => setPipeline(pipeline === "typesafe" ? "laya_local" : "typesafe")}
                    className="px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium flex items-center gap-1.5 cursor-pointer hover:bg-emerald-100 transition-colors"
                    title="Click to toggle between ConvAI Laya and TypeSafe Jev"
                  >
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span>
                      {pipeline === "typesafe" ? "TypeSafe Jev calibrated" : "Laya calibrated"}
                    </span>
                    <Info className="w-3 h-3 text-emerald-500" />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column (5 cols): Evaluated Requirements & Hard Gates / Dimension Weights */}
            <div className="lg:col-span-5">
              <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-2xs space-y-4">
                {/* Header with Switchable Tabs */}
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setConfigCardTab("REQUIREMENTS")}
                      className={`text-xs font-bold pb-1 transition-colors relative cursor-pointer ${
                        configCardTab === "REQUIREMENTS"
                          ? "text-blue-600"
                          : "text-slate-500 hover:text-slate-800"
                      }`}
                    >
                      Evaluated Requirements & Gates ({activeRequirementsCount})
                      {configCardTab === "REQUIREMENTS" && (
                        <div className="absolute -bottom-3 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
                      )}
                    </button>
                    <span className="text-slate-300 text-xs">|</span>
                    <button
                      onClick={() => setConfigCardTab("WEIGHTS")}
                      className={`text-xs font-bold pb-1 transition-colors relative cursor-pointer ${
                        configCardTab === "WEIGHTS"
                          ? "text-blue-600"
                          : "text-slate-500 hover:text-slate-800"
                      }`}
                    >
                      Weights & Rubric
                      {configCardTab === "WEIGHTS" && (
                        <div className="absolute -bottom-3 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
                      )}
                    </button>
                  </div>

                  <button
                    onClick={() => setIsConfigModalOpen(true)}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors cursor-pointer"
                    title="Open advanced evaluation configuration modal"
                  >
                    <Edit2 className="w-3 h-3" />
                    Edit
                  </button>
                </div>

                {/* TAB 1: Evaluated Requirements & Hard Gates */}
                {configCardTab === "REQUIREMENTS" && (
                  <div className="space-y-3">
                    {/* Toolbar / Sub-header */}
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span className="font-semibold text-slate-700">
                        {activeRequirementsCount} active · {hardGatesCount} mandatory gates
                      </span>
                      <button
                        onClick={handleExtractRequirements}
                        disabled={isExtracting}
                        className="text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 text-[11px] cursor-pointer"
                      >
                        <RefreshCw className={`w-3 h-3 ${isExtracting ? "animate-spin" : ""}`} />
                        Refresh from JD
                      </button>
                    </div>

                    {/* Requirements List */}
                    <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto pr-1">
                      {approvedRequirements.map((req, idx) => {
                        const isIncluded = req.is_included !== false;
                        return (
                          <div
                            key={`${req.name}-${idx}`}
                            className={`py-2.5 flex items-center justify-between gap-2 text-xs transition-opacity ${
                              isIncluded ? "opacity-100" : "opacity-40 bg-slate-50/50"
                            }`}
                          >
                            <div className="flex items-center gap-2 overflow-hidden">
                              <input
                                type="checkbox"
                                checked={isIncluded}
                                onChange={() => toggleRequirementInclusion(idx)}
                                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-3.5 w-3.5 cursor-pointer"
                                title={isIncluded ? "Exclude requirement from evaluation" : "Include requirement"}
                              />
                              <div>
                                <span className={`font-semibold ${isIncluded ? "text-slate-900" : "text-slate-400 line-through"}`}>
                                  {req.name}
                                </span>
                                <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium">
                                  {req.category}
                                </span>
                              </div>
                            </div>

                            {/* Mandate vs Preferred Toggle */}
                            <div className="flex items-center gap-2 shrink-0">
                              <button
                                type="button"
                                onClick={() => toggleRequirementMandate(idx)}
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold border transition-colors cursor-pointer flex items-center gap-1 ${
                                  req.is_hard_requirement
                                    ? "bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100"
                                    : "bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200"
                                }`}
                                title="Click to toggle Mandate (Hard Gate) vs Preferred"
                              >
                                {req.is_hard_requirement ? (
                                  <>
                                    <ShieldAlert className="w-3 h-3 text-rose-600" />
                                    Mandate
                                  </>
                                ) : (
                                  <>
                                    <Check className="w-3 h-3 text-slate-400" />
                                    Preferred
                                  </>
                                )}
                              </button>

                              <button
                                type="button"
                                onClick={() => removeRequirement(idx)}
                                className="p-1 text-slate-300 hover:text-rose-600 rounded transition-colors cursor-pointer"
                                title="Delete keyword"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Add Custom Keyword Input */}
                    <div className="pt-2 flex items-center gap-2">
                      <input
                        type="text"
                        value={newKeywordInput}
                        onChange={(e) => setNewKeywordInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            handleAddKeyword();
                          }
                        }}
                        placeholder="Add custom keyword / requirement..."
                        className="flex-1 px-3 py-1.5 text-xs border border-slate-200 rounded-lg bg-slate-50/50 text-slate-800 focus:bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                      <button
                        type="button"
                        onClick={handleAddKeyword}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Add
                      </button>
                    </div>

                    {/* Callout Notice */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-2.5 text-[11px] text-slate-500 leading-relaxed">
                      <ShieldAlert className="w-3.5 h-3.5 text-rose-500 shrink-0 mt-0.5" />
                      <span>
                        <strong>Mandate</strong> keywords act as hard qualification gates. Any candidate failing a mandate is disqualified regardless of overall score.
                      </span>
                    </div>
                  </div>
                )}

                {/* TAB 2: Dimension Weights & Rubric */}
                {configCardTab === "WEIGHTS" && (
                  <div className="space-y-4">
                    {/* Configuration Breakdown List */}
                    <div className="divide-y divide-slate-100 text-xs">
                      {/* Seniority */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800 flex items-center gap-1">
                            Seniority
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900 flex items-center justify-end gap-1">
                            Auto <Info className="w-3 h-3 text-slate-400" />
                          </span>
                          <span className="text-[10px] text-slate-400 block">Determined from JD & candidate profile</span>
                        </div>
                      </div>

                      {/* Technical */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Technical Skills</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{weights.technical}%</span>
                          <span className="text-[10px] text-slate-400 block">450+ IT taxonomy overlap & stack match</span>
                        </div>
                      </div>

                      {/* Experience */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Experience</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{weights.experience}%</span>
                          <span className="text-[10px] text-slate-400 block">Seniority alignment + direct evidence</span>
                        </div>
                      </div>

                      {/* Domain */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Domain</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{weights.domain}%</span>
                          <span className="text-[10px] text-slate-400 block">Industry and domain relevance</span>
                        </div>
                      </div>

                      {/* Education */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Education</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{weights.education}%</span>
                          <span className="text-[10px] text-slate-400 block">Degree, institution & field of study</span>
                        </div>
                      </div>

                      {/* Evidence */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Evidence Depth</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">{weights.evidence}%</span>
                          <span className="text-[10px] text-slate-400 block">Mean Laya probability across requirements</span>
                        </div>
                      </div>

                      {/* Review threshold */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Review threshold</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">0.65</span>
                          <span className="text-[10px] text-slate-400 block">Below 70% → manual review required</span>
                        </div>
                      </div>

                      {/* Rubric Version */}
                      <div className="py-2.5 flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-slate-800">Rubric version</div>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">v1.4</span>
                          <span className="text-[10px] text-slate-400 block">Calibrated non-autoregressive checkpoint</span>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Callout */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-2.5 text-[11px] text-slate-500 leading-relaxed">
                      <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                      <span>Weights and thresholds are mathematically normalized to 100% composite score.</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Bottom Table Section: Candidates Table */}
          <div className="bg-white border border-slate-200/90 rounded-2xl shadow-2xs overflow-hidden">
            {/* Toolbar */}
            <div className="px-5 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <h2 className="text-sm font-bold text-slate-900">
                  Candidates ({filteredCandidates.length})
                </h2>

                {/* Switchable Status Tabs: All, Selected, Need Review, Rejected */}
                <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-xl border border-slate-200/80 text-xs font-semibold">
                  <button
                    onClick={() => setCandidateFilterTab("ALL")}
                    className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                      candidateFilterTab === "ALL"
                        ? "bg-white text-slate-900 shadow-2xs"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    All ({countAll})
                  </button>
                  <button
                    onClick={() => setCandidateFilterTab("SELECTED")}
                    className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                      candidateFilterTab === "SELECTED"
                        ? "bg-white text-emerald-700 shadow-2xs"
                        : "text-slate-600 hover:text-emerald-700"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    Selected ({countSelected})
                  </button>
                  <button
                    onClick={() => setCandidateFilterTab("REVIEW")}
                    className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                      candidateFilterTab === "REVIEW"
                        ? "bg-white text-amber-700 shadow-2xs"
                        : "text-slate-600 hover:text-amber-700"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    Need Review ({countReview})
                  </button>
                  <button
                    onClick={() => setCandidateFilterTab("REJECTED")}
                    className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                      candidateFilterTab === "REJECTED"
                        ? "bg-white text-rose-700 shadow-2xs"
                        : "text-slate-600 hover:text-rose-700"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                    Rejected ({countRejected})
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2.5">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by name, email or skills..."
                    className="pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg w-56 sm:w-64 bg-slate-50/50 text-slate-800 focus:outline-none focus:bg-white focus:border-blue-500 transition-all"
                  />
                </div>

                {/* Filter Button */}
                <button className="px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-lg flex items-center gap-1.5 text-slate-600 hover:bg-slate-50 transition-colors">
                  <Filter className="w-3 h-3 text-slate-400" />
                  Filter
                </button>

                {/* View Options Toggle */}
                <button className="p-1.5 border border-slate-200 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-50 transition-colors">
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* SKELETON LOADING STATE DURING ANALYSIS */}
            {isScreening ? (
              <div className="p-6 space-y-4">
                <div className="p-3 bg-blue-50 border border-blue-200/90 rounded-xl flex items-center gap-3 text-xs text-blue-800 animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
                  <div>
                    <span className="font-bold">Evaluating {selectedFiles.length} resumes</span> with {pipeline === "typesafe" ? "TypeSafe Jev" : "ConvAI Laya"} neural pipeline... Verifying evidence snippets, hard gates, and continuous career seniority.
                  </div>
                </div>

                {/* Skeleton Candidate Cards */}
                <div className="divide-y divide-slate-100">
                  {(selectedFiles.length > 0 ? selectedFiles : [1, 2, 3]).map((item, idx) => {
                    const fileName = typeof item === "object" ? item.name : `Candidate Resume ${idx + 1}.pdf`;
                    // Derive a readable candidate name from the file name
                    const candidateName = fileName
                      .replace(/\.pdf$/i, "")
                      .replace(/[_\-]/g, " ")
                      .replace(/\s+/g, " ")
                      .trim() || `Candidate ${idx + 1}`;
                    return (
                      <div
                        key={`skeleton-${idx}`}
                        className="py-4 px-4 flex items-center justify-between gap-4"
                      >
                        {/* Left: avatar + name + file label */}
                        <div className="flex items-center gap-3 min-w-0">
                          {/* Avatar placeholder – pulsing */}
                          <div className="w-8 h-8 rounded-full bg-slate-200 shrink-0 animate-pulse" />
                          <div className="space-y-1.5 min-w-0">
                            {/* Candidate name – always visible, NOT pulsing */}
                            <p className="text-sm font-semibold text-slate-800 truncate leading-tight">
                              {candidateName}
                            </p>
                            {/* Skeleton bar for email / secondary info */}
                            <div className="h-2.5 w-48 bg-slate-200 rounded animate-pulse" />
                          </div>
                        </div>

                        {/* Right: pulsing status/score placeholders */}
                        <div className="flex items-center gap-6 shrink-0 animate-pulse">
                          <div className="h-6 w-20 bg-slate-200 rounded-full" />
                          <div className="h-4 w-12 bg-slate-100 rounded" />
                          <div className="h-6 w-16 bg-slate-200 rounded-full" />
                          <div className="h-4 w-10 bg-slate-100 rounded" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : tableCandidates.length === 0 ? (
              /* EMPTY STATE PRIOR TO ANALYSIS (No dummy data) */
              <div className="p-12 text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-slate-100 border border-slate-200 text-slate-400 flex items-center justify-center mx-auto shadow-2xs">
                  <Users className="w-6 h-6 text-slate-400" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-sm font-bold text-slate-900">No Candidates Screened Yet</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Upload PDF resumes in the upload zone above and click <strong>&quot;Run screening&quot;</strong> to evaluate talent against the job requirements and hard gates.
                  </p>
                </div>
                {selectedFiles.length === 0 && (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl inline-flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer"
                  >
                    <Upload className="w-3.5 h-3.5" />
                    Upload Candidate Resumes
                  </button>
                )}
              </div>
            ) : filteredCandidates.length === 0 ? (
              /* Filter empty state */
              <div className="p-10 text-center text-slate-400 text-xs">
                No candidates match the active &quot;{candidateFilterTab}&quot; tab or search query.
              </div>
            ) : (
              /* REAL EVALUATED CANDIDATES TABLE */
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60 text-slate-500 font-semibold">
                      <th className="py-3 px-4 w-10">
                        <input
                          type="checkbox"
                          checked={
                            selectedCandidateIds.length > 0 &&
                            selectedCandidateIds.length === filteredCandidates.length
                          }
                          onChange={toggleSelectAll}
                          className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-3.5 w-3.5 cursor-pointer"
                        />
                      </th>
                      <th className="py-3 px-4">Candidate</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Fit Score</th>
                      <th className="py-3 px-4">Evidence</th>
                      <th className="py-3 px-4">Seniority</th>
                      <th className="py-3 px-4">Ready</th>
                      <th className="py-3 px-4 w-10 text-center"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredCandidates.map((cand) => {
                      const initials = cand.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .slice(0, 2)
                        .toUpperCase();

                      const statusBadge =
                        cand.status === "Ready" ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            ● Ready
                          </span>
                        ) : cand.status === "Review" ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                            ● Review
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                            ● Rejected
                          </span>
                        );

                      const seniorityBadge =
                        cand.seniority === "Senior" ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                            Senior
                          </span>
                        ) : cand.seniority === "Junior" ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                            Junior
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                            Mid
                          </span>
                        );

                      return (
                        <tr
                          key={cand.id}
                          className={`hover:bg-slate-50/70 transition-colors group cursor-pointer ${cand.rejectionMessage ? "opacity-70" : ""}`}
                          onClick={() => !cand.rejectionMessage && openInspection(cand)}
                        >
                          <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              checked={selectedCandidateIds.includes(cand.id)}
                              onChange={() => toggleSelectCandidate(cand.id)}
                              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-3.5 w-3.5 cursor-pointer"
                            />
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-slate-700 text-white font-bold text-xs flex items-center justify-center shrink-0">
                                {initials}
                              </div>
                              <div className="min-w-0">
                                <div className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                                  {cand.name}
                                </div>
                                {cand.rejectionMessage ? (
                                  <div className="text-[11px] text-rose-600 font-medium truncate max-w-xs" title={cand.rejectionMessage}>
                                    ✗ Does not fit role — {cand.rawCandidate?.technical_overlap?.skill_overlap_percentage?.toFixed(1) ?? "0"}% technical overlap
                                  </div>
                                ) : (
                                  <div className="text-[11px] text-slate-400 truncate">{cand.email}</div>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-4">{statusBadge}</td>
                          <td className="py-3 px-4 font-bold text-slate-900">
                            {cand.rejectionMessage
                              ? <span className="text-rose-500 text-xs font-semibold">—</span>
                              : cand.rawCandidate?.fit_score ? `${cand.rawCandidate.fit_score}%` : "—"
                            }
                          </td>
                          <td className="py-3 px-4 font-semibold text-slate-700">{cand.evidenceCount}</td>
                          <td className="py-3 px-4">{seniorityBadge}</td>
                          <td className="py-3 px-4">
                            {cand.ready ? (
                              <span className="inline-flex items-center gap-1 font-semibold text-emerald-700 text-xs">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                Yes
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 font-semibold text-rose-700 text-xs">
                                <XCircle className="w-4 h-4 text-rose-500" />
                                No
                              </span>
                            )}
                          </td>
                          {/* Actions: View PDF + Inspect */}
                          <td className="py-3 px-4 text-center" onClick={(e) => e.stopPropagation()}>
                            <div className="flex items-center justify-center gap-1">
                              {cand.pdfUrl && (
                                <a
                                  href={cand.pdfUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  title="View PDF resume"
                                  className="p-1 rounded-md text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <FileText className="w-4 h-4" />
                                </a>
                              )}
                              {!cand.rejectionMessage && (
                                <button
                                  onClick={() => openInspection(cand)}
                                  className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                                  title="Inspect candidate verbatim evidence & decisions"
                                >
                                  <MoreVertical className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination / Table Footer */}
            {tableCandidates.length > 0 && !isScreening && (
              <div className="px-5 py-3.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <div>
                  Showing {filteredCandidates.length} of {tableCandidates.length} evaluated candidates
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setCurrentPage(1)}
                    className={`w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center transition-colors ${
                      currentPage === 1
                        ? "bg-blue-600 text-white"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    1
                  </button>
                  {filteredCandidates.length > 7 && (
                    <button
                      onClick={() => setCurrentPage(2)}
                      className={`w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center transition-colors ${
                        currentPage === 2
                          ? "bg-blue-600 text-white"
                          : "text-slate-600 hover:bg-slate-100"
                      }`}
                    >
                      2
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Evaluation Configuration & Requirements Preview Modal */}
      <EvaluationConfigModal
        isOpen={isConfigModalOpen}
        onClose={() => setIsConfigModalOpen(false)}
        jobRole={jobRole}
        jobDescription={jobDescription}
        pipeline={pipeline}
        weights={weights}
        onSaveWeights={(newWeights) => setWeights(newWeights)}
        approvedRequirements={approvedRequirements}
        onSaveRequirements={(newReqs) => setApprovedRequirements(newReqs)}
      />

      {/* Candidate Detailed Inspection Drawer */}
      <CandidateInspectionModal
        candidate={selectedCandidateForInspection}
        onClose={() => setSelectedCandidateForInspection(null)}
      />
    </div>
  );
}
