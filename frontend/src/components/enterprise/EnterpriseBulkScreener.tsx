"use client";

import React, { useState, useRef } from "react";
import { bulkScreenEnterpriseResumes } from "@/lib/api";
import {
  EnterpriseCandidate,
  EnterpriseScreeningResponse,
  ParameterEvaluation,
} from "@/lib/types";
import { PdfViewerModal } from "@/components/PdfViewerModal";
import {
  Upload,
  FileText,
  X,
  Sparkles,
  Zap,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Trophy,
  Users,
  Timer,
  BarChart3,
  Cpu,
  Award,
  Activity,
  Layers,
  Search,
  ArrowRight,
  Loader2,
  AlertCircle,
  Briefcase,
  ChevronDown,
  ChevronUp,
  Eye,
  GraduationCap,
  Scale,
  UserCheck,
  Building,
  Mail,
  Phone,
  FileSpreadsheet,
} from "lucide-react";

const SAMPLE_ROLE = "Senior Full-Stack AI Engineer";
const SAMPLE_JD = `Senior Full-Stack AI Engineer
Company: CloudScale AI
Location: San Francisco, CA / Remote

Requirements:
- 5+ years of experience building scalable backend microservices and high-performance APIs.
- Proficient in Python, FastAPI, TypeScript, React, and Next.js.
- Strong hands-on experience with PostgreSQL, Redis, Docker, and Kubernetes.
- Experience with AI application frameworks, vector databases, and deterministic scoring pipelines.
- Demonstrated ownership of distributed cloud systems handling high concurrent throughput.
- Bachelor's or Master's degree in Computer Science or equivalent practical experience.`;

export const EnterpriseBulkScreener: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [jobRole, setJobRole] = useState(SAMPLE_ROLE);
  const [jobDescription, setJobDescription] = useState(SAMPLE_JD);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<EnterpriseScreeningResponse | null>(null);
  const [filter, setFilter] = useState<"all" | "top3" | "top5" | "selected" | "rejected">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedCand, setExpandedCand] = useState<string | null>(null);
  const [activeTabByCand, setActiveTabByCand] = useState<Record<string, "laya" | "skills" | "resume">>({});

  // PDF Preview Modal State
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  const handleOpenPreview = (candidateFilename?: string) => {
    if (!candidateFilename) {
      if (files.length > 0) {
        setPreviewFile(files[0]);
        setPreviewModalOpen(true);
      }
      return;
    }
    const cleanTarget = candidateFilename.toLowerCase().trim();
    const matched =
      files.find((f) => f.name.toLowerCase().trim() === cleanTarget) ||
      files.find((f) => f.name.toLowerCase().includes(cleanTarget)) ||
      files.find((f) => cleanTarget.includes(f.name.toLowerCase())) ||
      files[0] ||
      null;
    setPreviewFile(matched);
    setPreviewModalOpen(true);
  };

  const handleFileSelect = (newFiles: FileList | null) => {
    if (!newFiles) return;
    const added: File[] = [];
    for (let i = 0; i < newFiles.length; i++) {
      const f = newFiles[i];
      if (f.name.toLowerCase().endsWith(".pdf")) {
        added.push(f);
      }
    }

    if (files.length + added.length > 20) {
      setError(`Maximum 20 resumes allowed. You currently have ${files.length} and tried to add ${added.length}.`);
      return;
    }

    setError(null);
    setFiles((prev) => [...prev, ...added]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAllFiles = () => {
    setFiles([]);
    setResults(null);
    setError(null);
  };

  const handleScreen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobRole.trim()) {
      setError("Please specify the target Job Role title.");
      return;
    }
    if (jobDescription.trim().length < 20) {
      setError("Please provide a job description of at least 20 characters.");
      return;
    }
    if (files.length === 0) {
      setError("Please upload at least 1 PDF resume to screen.");
      return;
    }
    if (files.length > 20) {
      setError(`Maximum 20 resumes allowed per screening batch. You have ${files.length}.`);
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await bulkScreenEnterpriseResumes(files, jobRole, jobDescription);
      setResults(response);
    } catch (err: any) {
      setError(err.message || "Bulk screening failed.");
    } finally {
      setLoading(false);
    }
  };

  const filteredCandidates = (results?.candidates || []).filter((cand) => {
    // 1. Filter by category
    if (filter === "top3") {
      if (!cand.is_top_3 && (cand.rank === undefined || cand.rank > 3)) return false;
    } else if (filter === "top5") {
      if (!cand.is_top_5 && (cand.rank === undefined || cand.rank > 5)) return false;
    } else if (filter === "selected") {
      if (cand.decision !== "SELECT") return false;
    } else if (filter === "rejected") {
      if (cand.decision !== "REJECT") return false;
    }

    // 2. Filter by search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = cand.name.toLowerCase().includes(q);
      const matchFile = cand.filename.toLowerCase().includes(q);
      const matchSkill = (cand.skills || []).some((s) => s.toLowerCase().includes(q));
      if (!matchName && !matchFile && !matchSkill) return false;
    }

    return true;
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Requisition Banner: Recruiter Operations */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="p-3 rounded-2xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                Enterprise Bulk Candidate Screener
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-bold border border-indigo-200">
                Laya Calibrated
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              Screen and rank candidate batches against job requirements with 5-parameter calibrated probability scoring
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 border border-slate-200">
            {files.length}/20 Resumes Selected
          </span>
        </div>
      </div>

      {/* Form & Upload Controls */}
      <form onSubmit={handleScreen} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Job Role & Job Description */}
          <div className="lg:col-span-6 bg-white border border-slate-200 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center justify-between">
                <span>Target Job Role <span className="text-rose-500">*</span></span>
                <span className="text-[11px] text-slate-400 font-normal">Requisition Title</span>
              </label>
              <input
                type="text"
                value={jobRole}
                onChange={(e) => setJobRole(e.target.value)}
                placeholder="e.g. Senior Backend Engineer"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-800">
                  Target Job Description <span className="text-rose-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => {
                    setJobRole(SAMPLE_ROLE);
                    setJobDescription(SAMPLE_JD);
                  }}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold transition"
                >
                  Load Sample AI Role
                </button>
              </div>
              <textarea
                rows={9}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the target job description requirements, responsibilities, and required qualifications..."
                className="w-full p-3.5 rounded-xl border border-slate-300 text-xs sm:text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 leading-relaxed transition"
              />
            </div>
          </div>

          {/* Right Column: Multi-PDF Dropzone */}
          <div className="lg:col-span-6 bg-white border border-slate-200 rounded-3xl p-6 sm:p-7 shadow-xs space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-800">
                  Candidate Resumes (PDF Only) <span className="text-rose-500">*</span>
                </label>
                {files.length > 0 && (
                  <button
                    type="button"
                    onClick={clearAllFiles}
                    className="text-xs text-rose-600 hover:text-rose-800 font-semibold flex items-center gap-1 transition"
                  >
                    Clear All ({files.length})
                  </button>
                )}
              </div>

              {/* Drag and Drop Zone */}
              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  handleFileSelect(e.dataTransfer.files);
                }}
                className="border-2 border-dashed border-slate-300 hover:border-indigo-500 rounded-2xl p-6 text-center cursor-pointer transition bg-slate-50/60 hover:bg-indigo-50/20 space-y-2"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  multiple
                  onChange={(e) => handleFileSelect(e.target.files)}
                  className="hidden"
                />
                <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mx-auto">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs sm:text-sm font-bold text-slate-800">
                    Click to browse or drag & drop candidate PDFs
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Select 1 to 20 PDF resumes for simultaneous screening
                  </p>
                </div>
              </div>

              {/* Selected Files Badge List */}
              {files.length > 0 && (
                <div className="space-y-2 pt-1 max-h-56 overflow-y-auto pr-1">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center justify-between">
                    <span>Uploaded Resumes ({files.length}):</span>
                    <span className="text-emerald-600 font-semibold">Ready for Evaluation</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-slate-50 text-xs text-slate-800"
                      >
                        <div className="flex items-center gap-2 truncate pr-2">
                          <FileText className="w-4 h-4 text-rose-500 shrink-0" />
                          <span className="truncate font-medium">{file.name}</span>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setPreviewFile(file);
                              setPreviewModalOpen(true);
                            }}
                            className="p-1 text-slate-400 hover:text-indigo-600 rounded transition"
                            title="Preview PDF"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeFile(idx);
                            }}
                            className="p-1 text-slate-400 hover:text-rose-600 rounded transition"
                            title="Remove resume"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || files.length === 0 || !jobRole.trim() || jobDescription.length < 20}
              className="w-full py-4 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-2xl text-sm font-bold flex items-center justify-center gap-2 transition shadow-md"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Evaluating {files.length} Candidates in Parallel...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-emerald-400 fill-emerald-400" />
                  <span>Screen {files.length} Candidates & Rank Pipeline</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* SKELETON DISPLAY WHILE EVALUATING */}
      {loading && (
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <span className="text-sm font-bold text-slate-900">
                Evaluating {files.length} Candidate Resumes with Laya Router...
              </span>
            </div>
            <span className="text-xs text-slate-500 font-medium">
              Assessing technical match, experience, domain, education, and evidence
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="bg-white border border-slate-200 rounded-2xl p-5 sm:p-6 shadow-xs space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-slate-200 animate-pulse flex items-center justify-center font-bold text-xs text-slate-500">
                      #{idx + 1}
                    </div>
                    <div className="space-y-1.5">
                      <div className="h-4 w-48 bg-slate-200 rounded-md animate-pulse" />
                      <div className="h-3 w-36 bg-slate-100 rounded-md flex items-center gap-1.5 animate-pulse">
                        <FileText className="w-3 h-3 text-slate-300 inline" />
                        <span className="text-[11px] text-slate-400 truncate">{file.name}</span>
                      </div>
                    </div>
                  </div>
                  <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 border border-indigo-100 text-xs font-semibold text-indigo-700">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                    <span>Scoring Parameters...</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  {["Technical", "Experience", "Domain", "Education", "Evidence"].map((label, n) => (
                    <div key={n} className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-slate-400">{label}</span>
                        <div className="h-2.5 w-6 bg-slate-200 rounded animate-pulse" />
                      </div>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full w-2/3 bg-indigo-200 rounded-full animate-pulse" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RESULTS DISPLAY */}
      {results && (
        <div className="space-y-6 pt-4">
          {/* Seniority Tier & Role Weights Banner */}
          <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-3xl p-6 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-widest px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 font-bold">
                  Target Requisition Classified
                </span>
                <span className="text-xs font-bold text-amber-300">
                  {results.seniority_label || "Mid-Level Tier"}
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                {results.job_role}
              </h2>
              <p className="text-xs text-slate-300 max-w-xl">
                Laya detected the required professional depth and calibrated parameter weights dynamically for this seniority tier.
              </p>
            </div>

            {results.role_weights && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10 shrink-0">
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-300 block mb-2 font-bold">
                  Active Parameter Weights
                </span>
                <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 text-center text-xs">
                  {Object.entries(results.role_weights).map(([k, w]) => (
                    <div key={k} className="bg-white/10 rounded-xl px-2.5 py-1.5">
                      <span className="text-[10px] text-slate-300 block capitalize">{k}</span>
                      <span className="font-bold text-white font-mono">{((w as number) * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Summary Metrics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <span className="text-xs font-semibold text-slate-500 block">Total Evaluated</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-black text-slate-900">{results.total_evaluated}</span>
                <span className="text-xs text-slate-400 font-medium">candidates</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <span className="text-xs font-semibold text-slate-500 block">Top 3 Shortlisted</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-black text-amber-600">
                  {results.top_3_shortlisted ?? results.candidates.filter((c) => Boolean(c.is_top_3 || (c.rank !== undefined && c.rank <= 3))).length}
                </span>
                <span className="text-xs text-amber-600 font-semibold">candidates</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <span className="text-xs font-semibold text-slate-500 block">Average Match Score</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-black text-slate-900">{results.average_fit_score}%</span>
                <span className="text-xs text-slate-400 font-medium">overall</span>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs">
              <span className="text-xs font-semibold text-slate-500 block">Screening Latency</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-black text-emerald-600">{results.latency_seconds}s</span>
                <span className="text-xs text-emerald-600 font-semibold">total</span>
              </div>
            </div>
          </div>

          {/* Filter Bar, Search & Candidate Count */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Filter:
              </span>
              <div className="flex flex-wrap items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setFilter("all")}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition ${
                    filter === "all"
                      ? "bg-slate-900 text-white"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  All ({results.candidates.length})
                </button>
                <button
                  type="button"
                  onClick={() => setFilter("top3")}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                    filter === "top3"
                      ? "bg-amber-600 text-white"
                      : "bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100"
                  }`}
                >
                  <Trophy className="w-3 h-3" />
                  Top 3 Shortlist ({results.candidates.filter((c) => Boolean(c.is_top_3 || (c.rank !== undefined && c.rank <= 3))).length})
                </button>
                <button
                  type="button"
                  onClick={() => setFilter("top5")}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                    filter === "top5"
                      ? "bg-indigo-600 text-white"
                      : "bg-indigo-50 text-indigo-800 border border-indigo-200 hover:bg-indigo-100"
                  }`}
                >
                  Top 5 ({results.candidates.filter((c) => Boolean(c.is_top_5 || (c.rank !== undefined && c.rank <= 5))).length})
                </button>
                <button
                  type="button"
                  onClick={() => setFilter("selected")}
                  className={`px-3 py-1 rounded-xl text-xs font-bold transition ${
                    filter === "selected"
                      ? "bg-emerald-600 text-white"
                      : "bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100"
                  }`}
                >
                  Selected ({results.candidates.filter((c) => c.decision === "SELECT").length})
                </button>
              </div>
            </div>

            {/* Quick Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search candidate name or skill..."
                className="pl-8 pr-3 py-1 rounded-xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-48 sm:w-60"
              />
            </div>
          </div>

          {/* Candidate Pipeline Cards */}
          <div className="grid grid-cols-1 gap-4">
            {filteredCandidates.map((cand, idx) => {
              const displayRank = cand.rank ?? (idx + 1);
              const isTop3 = Boolean(cand.is_top_3 || displayRank <= 3);
              const isRank1 = displayRank === 1;
              const isRank2 = displayRank === 2;
              const isRank3 = displayRank === 3;
              const isExpanded = expandedCand === cand.candidate_id;
              const currentTab = activeTabByCand[cand.candidate_id] || "laya";

              const breakdown = cand.breakdown || {
                technical_requirements: 0,
                experience_requirements: 0,
                domain_alignment: 0,
                education_alignment: 0,
                evidence_strength: 0,
              };

              const techScore = breakdown.technical_requirements ?? 0;
              const expScore = breakdown.experience_requirements ?? 0;
              const domainScore = breakdown.domain_alignment ?? 0;
              const eduScore = breakdown.education_alignment ?? 0;
              const evidenceScore = breakdown.evidence_strength ?? 0;

              const candidateSkills = cand.skills || [];
              const candidateTools = cand.tools || [];
              const hasSkillsOrTools = candidateSkills.length > 0 || candidateTools.length > 0;

              const techOverlap = cand.technical_overlap;
              const matchedSkills = techOverlap?.matched_skills || [];
              const missingSkills = techOverlap?.missing_jd_skills || techOverlap?.missing_skills || [];
              const hasOverlapData = Boolean(techOverlap && (matchedSkills.length > 0 || missingSkills.length > 0));

              return (
                <div
                  key={cand.candidate_id || `candidate-${idx}`}
                  className={`bg-white rounded-3xl border transition-all duration-200 shadow-xs ${
                    isRank1
                      ? "border-amber-300 ring-2 ring-amber-400/20 bg-amber-50/10"
                      : isRank2
                      ? "border-slate-300 ring-1 ring-slate-300 bg-slate-50/10"
                      : isRank3
                      ? "border-orange-300 ring-1 ring-orange-300/30 bg-orange-50/10"
                      : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="p-5 sm:p-6 space-y-4">
                    {/* Header Row */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-3">
                        {/* Rank Badge */}
                        <div
                          className={`w-10 h-10 rounded-2xl flex items-center justify-center font-black text-sm shrink-0 shadow-2xs ${
                            isRank1
                              ? "bg-gradient-to-br from-amber-400 to-amber-600 text-white ring-2 ring-amber-300"
                              : isRank2
                              ? "bg-gradient-to-br from-slate-400 to-slate-600 text-white ring-2 ring-slate-300"
                              : isRank3
                              ? "bg-gradient-to-br from-amber-700 to-orange-700 text-white ring-2 ring-orange-300"
                              : "bg-slate-100 text-slate-700 border border-slate-200"
                          }`}
                        >
                          #{displayRank}
                        </div>

                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-slate-900">{cand.name || "Candidate"}</h3>
                            {isTop3 && (
                              <span
                                className={`inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                                  isRank1
                                    ? "bg-amber-100 text-amber-900 border border-amber-300"
                                    : isRank2
                                    ? "bg-slate-100 text-slate-900 border border-slate-300"
                                    : "bg-orange-100 text-orange-900 border border-orange-300"
                                }`}
                              >
                                <Trophy className="w-3 h-3 text-amber-600" />
                                {isRank1 ? "Rank #1" : isRank2 ? "Rank #2" : "Rank #3"}
                              </span>
                            )}
                            {(cand.candidate_seniority_label || cand.seniority_label) && (
                              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                                Candidate: {cand.candidate_seniority_label || cand.seniority_label}
                              </span>
                            )}
                            {cand.seniority_alignment === "GAP" && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200">
                                Seniority Gap vs Target
                              </span>
                            )}
                            {cand.seniority_alignment === "ALIGNED" && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                                ✓ Seniority Aligned
                              </span>
                            )}
                            {cand.seniority_alignment === "EXCEEDS" && (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                                Exceeds Target Seniority
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                            <FileText className="w-3.5 h-3.5 text-slate-400" />
                            <span className="truncate max-w-xs">{cand.filename || "Resume PDF"}</span>
                          </p>
                        </div>
                      </div>

                      {/* Right Metric Group: High Hits, Penalty, Score, Decision, View PDF */}
                      <div className="flex flex-wrap items-center gap-3 self-end sm:self-center">
                        {/* High Hits Counter Badge */}
                        <div className="text-right px-2.5 py-1 bg-slate-50 rounded-xl border border-slate-200/80">
                          <span className="text-[10px] font-bold text-slate-400 block uppercase">
                            High Hits
                          </span>
                          <span className="text-xs font-bold text-indigo-700">
                            {cand.high_hits_count ?? 0}/5 Dims
                          </span>
                        </div>

                        {/* Penalty Badge if applied */}
                        {(cand.penalty_applied ?? 0) > 0 && (
                          <div className="text-right px-2.5 py-1 bg-rose-50 rounded-xl border border-rose-200">
                            <span className="text-[10px] font-bold text-rose-500 block uppercase">
                              Penalty
                            </span>
                            <span className="text-xs font-bold text-rose-700">
                              -{((cand.penalty_applied ?? 0) * 100).toFixed(0)}%
                            </span>
                          </div>
                        )}

                        {/* Fit Score */}
                        <div className="text-right">
                          <span className="text-[10px] font-bold text-slate-400 block uppercase">
                            Fit Score
                          </span>
                          <span className="text-xl font-black text-slate-900">
                            {cand.fit_score ?? 0}%
                          </span>
                        </div>

                        {/* Verdict Badge */}
                        <span
                          className={`text-xs font-bold px-3 py-1.5 rounded-xl uppercase tracking-wider ${
                            cand.decision === "SELECT"
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                              : cand.decision === "BORDERLINE"
                              ? "bg-amber-100 text-amber-800 border border-amber-300"
                              : "bg-rose-100 text-rose-800 border border-rose-300"
                          }`}
                        >
                          {cand.decision || "BORDERLINE"}
                        </span>

                        <button
                          type="button"
                          onClick={() => handleOpenPreview(cand.filename)}
                          className="px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-xs font-semibold text-slate-700 flex items-center gap-1.5 transition shadow-2xs"
                        >
                          <Eye className="w-3.5 h-3.5 text-indigo-600" />
                          <span>PDF</span>
                        </button>
                      </div>
                    </div>

                    {/* 5-Parameter Progress Bars */}
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 pt-1">
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <div className="text-[10px] font-bold text-slate-500 flex items-center justify-between">
                          <span className="flex items-center gap-1"><Cpu className="w-3 h-3 text-blue-600" /> Technical</span>
                          <span className="text-slate-900 font-bold">{techScore}%</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-blue-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(0, techScore))}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <div className="text-[10px] font-bold text-slate-500 flex items-center justify-between">
                          <span className="flex items-center gap-1"><Award className="w-3 h-3 text-indigo-600" /> Experience</span>
                          <span className="text-slate-900 font-bold">{expScore}%</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(0, expScore))}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <div className="text-[10px] font-bold text-slate-500 flex items-center justify-between">
                          <span className="flex items-center gap-1"><Activity className="w-3 h-3 text-purple-600" /> Domain</span>
                          <span className="text-slate-900 font-bold">{domainScore}%</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-purple-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(0, domainScore))}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <div className="text-[10px] font-bold text-slate-500 flex items-center justify-between">
                          <span className="flex items-center gap-1"><GraduationCap className="w-3 h-3 text-amber-600" /> Education</span>
                          <span className="text-slate-900 font-bold">{eduScore}%</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-amber-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(0, eduScore))}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100 col-span-2 sm:col-span-1">
                        <div className="text-[10px] font-bold text-slate-500 flex items-center justify-between">
                          <span className="flex items-center gap-1"><Sparkles className="w-3 h-3 text-emerald-600" /> Evidence</span>
                          <span className="text-slate-900 font-bold">{evidenceScore}%</span>
                        </div>
                        <div className="w-full bg-slate-200 h-1.5 rounded-full mt-1.5 overflow-hidden">
                          <div
                            className="bg-emerald-600 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(0, evidenceScore))}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Extracted Skills Chips */}
                    {hasSkillsOrTools && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {candidateSkills.map((s) => (
                          <span
                            key={s}
                            className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-medium border border-slate-200"
                          >
                            {s}
                          </span>
                        ))}
                        {candidateTools.map((t) => (
                          <span
                            key={t}
                            className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-[11px] font-medium border border-indigo-200"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Technical Overlap / JD Match Details */}
                    {hasOverlapData && (
                      <div className="space-y-1.5 pt-1">
                        <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 uppercase">
                          <span>JD Skill Match ({matchedSkills.length} matched):</span>
                          {techOverlap?.skill_overlap_percentage !== undefined && (
                            <span className="text-emerald-700 font-bold font-mono">
                              {techOverlap.skill_overlap_percentage}% Overlap
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {matchedSkills.map((s) => (
                            <span
                              key={s}
                              className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 text-[11px] font-semibold border border-emerald-200"
                            >
                              ✓ {s}
                            </span>
                          ))}
                          {missingSkills.map((s) => (
                            <span
                              key={s}
                              className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 text-[11px] font-semibold border border-rose-200"
                            >
                              ✗ {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Toggle Recruiter Deep-Dive Accordion */}
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() =>
                          setExpandedCand(isExpanded ? null : cand.candidate_id)
                        }
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 transition"
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="w-3.5 h-3.5" />
                            Hide Recruiter Decision Audit & Resume Inspection
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-3.5 h-3.5" />
                            View Recruiter Decision Audit & Resume Inspection
                          </>
                        )}
                      </button>
                    </div>

                    {/* EXPANDED SECTION: Recruiter Decision Audit */}
                    {isExpanded && (
                      <div className="space-y-4 pt-3 text-xs bg-slate-50 p-5 rounded-2xl border border-slate-200">
                        {/* Subtabs: Laya Decision Matrix | Skills & Gaps | Resume Inspection */}
                        <div className="flex items-center gap-2 border-b border-slate-200 pb-2.5">
                          <button
                            type="button"
                            onClick={() =>
                              setActiveTabByCand((prev) => ({ ...prev, [cand.candidate_id]: "laya" }))
                            }
                            className={`px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                              currentTab === "laya"
                                ? "bg-indigo-600 text-white"
                                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                            }`}
                          >
                            <Scale className="w-3.5 h-3.5" />
                            <span>Laya 5-Parameter Audit</span>
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              setActiveTabByCand((prev) => ({ ...prev, [cand.candidate_id]: "resume" }))
                            }
                            className={`px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                              currentTab === "resume"
                                ? "bg-indigo-600 text-white"
                                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                            }`}
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>Resume Sections</span>
                          </button>
                        </div>

                        {/* TAB 1: LAYA 5-PARAMETER AUDIT */}
                        {currentTab === "laya" && (
                          <div className="space-y-4">
                            {/* Recruiter Rationale */}
                            <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 space-y-1">
                              <span className="text-[11px] font-bold text-slate-900 block uppercase tracking-wider">
                                Recruiter Decision Rationale:
                              </span>
                              <p className="text-slate-700 leading-relaxed text-xs">
                                {cand.decision_reason}
                              </p>
                            </div>

                            {/* Parameter Evaluation Table */}
                            {cand.parameter_evaluations && Object.keys(cand.parameter_evaluations).length > 0 ? (
                              <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse bg-white rounded-xl overflow-hidden border border-slate-200">
                                  <thead>
                                    <tr className="bg-slate-100/80 text-[10px] uppercase font-bold text-slate-600 border-b border-slate-200">
                                      <th className="p-2.5">Parameter</th>
                                      <th className="p-2.5">Weight</th>
                                      <th className="p-2.5 text-center">P(High)</th>
                                      <th className="p-2.5 text-center">P(Mid)</th>
                                      <th className="p-2.5 text-center">P(Low)</th>
                                      <th className="p-2.5 text-center">Selected</th>
                                      <th className="p-2.5 text-center">Contribution</th>
                                      <th className="p-2.5 text-center">High Hit?</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                                    {Object.entries(cand.parameter_evaluations).map(([param, ev]) => (
                                      <tr key={param} className="hover:bg-slate-50/60">
                                        <td className="p-2.5 font-bold font-sans capitalize text-slate-800">
                                          {param}
                                        </td>
                                        <td className="p-2.5 text-slate-600">
                                          {((ev.weight ?? 0) * 100).toFixed(0)}%
                                        </td>
                                        <td className="p-2.5 text-center text-slate-700">
                                          {(ev.p_high ?? 0).toFixed(3)}
                                        </td>
                                        <td className="p-2.5 text-center text-slate-700">
                                          {(ev.p_mid ?? 0).toFixed(3)}
                                        </td>
                                        <td className="p-2.5 text-center text-slate-700">
                                          {(ev.p_low ?? 0).toFixed(3)}
                                        </td>
                                        <td className="p-2.5 text-center font-bold text-indigo-700">
                                          {(ev.selected_prob ?? 0).toFixed(3)}
                                        </td>
                                        <td className="p-2.5 text-center font-bold text-slate-900">
                                          {(ev.weighted_score ?? 0).toFixed(4)}
                                        </td>
                                        <td className="p-2.5 text-center">
                                          {ev.is_high_hit ? (
                                            <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-sans font-bold">
                                              YES
                                            </span>
                                          ) : (
                                            <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 text-[10px] font-sans font-bold">
                                              NO
                                            </span>
                                          )}
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            ) : null}

                            {/* Scoring Formula Explainer */}
                            <div className="bg-indigo-50/60 border border-indigo-100 rounded-xl p-3 text-[11px] text-indigo-900 space-y-1">
                              <span className="font-bold block">Scoring Formula Audit:</span>
                              <p className="font-mono text-[10px] text-indigo-800">
                                S_raw = ∑ [max(P(high), P(mid)) × Weight] = {(cand.raw_weighted_probability ?? 0).toFixed(4)} | Penalty = max(0, (3 - {cand.high_hits_count ?? 0}) × 0.02) = -{(cand.penalty_applied ?? 0).toFixed(4)}
                              </p>
                              <p className="font-mono text-[10px] font-bold text-indigo-950">
                                Total Weighted Probability = {(cand.total_weighted_probability ?? 0).toFixed(4)} ➔ Fit Score: {cand.fit_score ?? 0}%
                              </p>
                            </div>
                          </div>
                        )}

                        {/* TAB 2: RESUME SECTIONS INSPECTION */}
                        {currentTab === "resume" && (
                          <div className="space-y-3">
                            {cand.inspection ? (
                              <div className="space-y-3">
                                {cand.inspection.summary && (
                                  <div className="bg-white p-3.5 rounded-xl border border-slate-200">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                                      Professional Summary
                                    </span>
                                    <p className="text-slate-800 whitespace-pre-line leading-relaxed text-xs">
                                      {cand.inspection.summary}
                                    </p>
                                  </div>
                                )}

                                {cand.inspection.experience && (
                                  <div className="bg-white p-3.5 rounded-xl border border-slate-200">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                                      Experience Section
                                    </span>
                                    <p className="text-slate-800 whitespace-pre-line leading-relaxed text-xs max-h-48 overflow-y-auto">
                                      {cand.inspection.experience}
                                    </p>
                                  </div>
                                )}

                                {cand.inspection.education && (
                                  <div className="bg-white p-3.5 rounded-xl border border-slate-200">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                                      Education Credentials
                                    </span>
                                    <p className="text-slate-800 whitespace-pre-line leading-relaxed text-xs">
                                      {cand.inspection.education}
                                    </p>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="bg-white p-4 rounded-xl border border-slate-200 text-slate-500 text-center">
                                Direct resume sections unavailable. Click "PDF" in header to view raw document.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Shared PDF Viewer Modal */}
      <PdfViewerModal
        isOpen={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        file={previewFile}
        title={previewFile?.name}
      />
    </div>
  );
};
