"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  User,
  Briefcase,
  GraduationCap,
  Award,
  Layers,
  FileText,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Copy,
  Check,
  Sparkles,
  FolderGit2,
} from "lucide-react";
import {
  CandidateEvaluationItem,
  JobRequisition,
  ResumeParsedSections,
} from "@/lib/types";
import { getResumeDetail } from "@/lib/api";

interface ParsedCandidateDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  candidate: CandidateEvaluationItem | null;
  requisition: JobRequisition | null;
  onViewPdf?: (candidateName: string) => void;
}

export const ParsedCandidateDrawer: React.FC<ParsedCandidateDrawerProps> = ({
  isOpen,
  onClose,
  candidate,
  requisition,
  onViewPdf,
}) => {
  const [activeTab, setActiveTab] = useState<"parsed" | "scoring" | "raw">("parsed");
  const [parsedSections, setParsedSections] = useState<ResumeParsedSections | null>(null);
  const [rawText, setRawText] = useState<string>("");
  const [isLoadingDetails, setIsLoadingDetails] = useState<boolean>(false);
  const [copiedRaw, setCopiedRaw] = useState(false);

  useEffect(() => {
    if (!candidate || !isOpen) {
      setParsedSections(null);
      setRawText("");
      return;
    }

    if (candidate.parsedSections) {
      setParsedSections(candidate.parsedSections);
      if (candidate.parsedSections.raw_text) setRawText(candidate.parsedSections.raw_text);
      return;
    }

    setIsLoadingDetails(true);
    getResumeDetail(candidate.resume_id)
      .then((detail) => {
        if (detail.parsed_sections) {
          setParsedSections(detail.parsed_sections);
        }
        if (detail.raw_text) {
          setRawText(detail.raw_text);
        }
      })
      .catch((err) => {
        console.error("Failed to load parsed resume detail:", err);
      })
      .finally(() => {
        setIsLoadingDetails(false);
      });
  }, [candidate, isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !candidate) return null;

  const isAdvance = candidate.verdict?.toUpperCase() === "ADVANCE";
  const isHold = candidate.verdict?.toUpperCase() === "HOLD";
  const isReject = candidate.verdict?.toUpperCase() === "REJECT";

  const handleCopyRaw = () => {
    if (!rawText) return;
    navigator.clipboard.writeText(rawText);
    setCopiedRaw(true);
    setTimeout(() => setCopiedRaw(false), 2000);
  };

  const questionsList = requisition?.questions ? Object.values(requisition.questions) : [];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-end bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white w-full max-w-3xl h-full shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-right duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Drawer */}
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/75 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 text-white font-bold text-sm flex items-center justify-center shadow-xs">
              {candidate.candidate_name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .slice(0, 2)
                .toUpperCase() || "CA"}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">{candidate.candidate_name}</h3>
                {isAdvance && (
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    ● ADVANCE
                  </span>
                )}
                {isHold && (
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                    ● HOLD
                  </span>
                )}
                {isReject && (
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                    ● REJECT
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-mono">
                ID: {candidate.resume_id} · Pipeline: {candidate.pipeline.toUpperCase()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onViewPdf && (
              <button
                type="button"
                onClick={() => onViewPdf(candidate.candidate_name)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold cursor-pointer"
              >
                <FileText className="w-3.5 h-3.5 text-slate-500" />
                <span>Original PDF</span>
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-slate-200 bg-white flex items-center gap-6 shrink-0">
          <button
            type="button"
            onClick={() => setActiveTab("parsed")}
            className={`py-3 text-xs font-semibold border-b-2 transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "parsed"
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <User className="w-4 h-4" />
            <span>Parsed Resume (6 Sections)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("scoring")}
            className={`py-3 text-xs font-semibold border-b-2 transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "scoring"
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Scoring & Gate Audit</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("raw")}
            className={`py-3 text-xs font-semibold border-b-2 transition-all cursor-pointer flex items-center gap-2 ${
              activeTab === "raw"
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Raw Text</span>
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {isLoadingDetails ? (
            <div className="text-center py-20 text-slate-400 text-xs">
              <Sparkles className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600" />
              Loading candidate dossier...
            </div>
          ) : activeTab === "parsed" ? (
            <div className="space-y-5">
              {/* Contact Info */}
              <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-wrap items-center gap-4 text-xs">
                {parsedSections?.email && (
                  <div className="flex items-center gap-1.5 text-slate-700">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    <span>{parsedSections.email}</span>
                  </div>
                )}
                {parsedSections?.phone && (
                  <div className="flex items-center gap-1.5 text-slate-700">
                    <Phone className="w-3.5 h-3.5 text-slate-400" />
                    <span>{parsedSections.phone}</span>
                  </div>
                )}
                {parsedSections?.location && (
                  <div className="flex items-center gap-1.5 text-slate-700">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{parsedSections.location}</span>
                  </div>
                )}
                {parsedSections?.portfolio_links && parsedSections.portfolio_links.length > 0 && (
                  <div className="flex items-center gap-2 ml-auto">
                    {parsedSections.portfolio_links.map((link, idx) => (
                      <a
                        key={idx}
                        href={link.startsWith("http") ? link : `https://${link}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-indigo-600 hover:underline font-medium"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>Portfolio Link</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>

              {/* 1. Summary */}
              {parsedSections?.professional_summary && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-indigo-600" />
                    1. Professional Summary
                  </h4>
                  <p className="text-xs text-slate-700 leading-relaxed bg-white p-3 rounded-xl border border-slate-200">
                    {parsedSections.professional_summary}
                  </p>
                </div>
              )}

              {/* 2. Work Experience */}
              <div>
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
                  2. Work Experience Timeline
                </h4>
                {parsedSections?.work_experience && parsedSections.work_experience.length > 0 ? (
                  <div className="space-y-2.5">
                    {parsedSections.work_experience.map((exp, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-white">
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                          <div>
                            <span className="font-bold text-xs text-slate-900">{exp.role_title}</span>
                            <span className="text-xs text-slate-500"> @ {exp.employer}</span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                            {exp.start_date || "Start"} — {exp.is_current ? "Present" : exp.end_date || "End"}
                          </span>
                        </div>

                        {exp.responsibilities_and_achievements && (
                          <ul className="list-disc list-inside text-xs text-slate-600 space-y-1 mt-2 pl-1">
                            {exp.responsibilities_and_achievements.map((item, i) => (
                              <li key={i} className="leading-relaxed">
                                {item}
                              </li>
                            ))}
                          </ul>
                        )}

                        {exp.tools_and_methods && exp.tools_and_methods.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1 mt-2.5 pt-2 border-t border-slate-100">
                            <span className="text-[10px] font-semibold text-slate-400">Tools:</span>
                            {exp.tools_and_methods.map((tool, i) => (
                              <span
                                key={i}
                                className="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 font-mono"
                              >
                                {tool}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 p-3 border border-dashed rounded-xl">
                    No work experience parsed.
                  </div>
                )}
              </div>

              {/* Projects & Technical Initiatives */}
              {parsedSections?.projects && parsedSections.projects.length > 0 && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                    <FolderGit2 className="w-3.5 h-3.5 text-indigo-600" />
                    Key Projects & Technical Deliverables ({parsedSections.projects.length})
                  </h4>
                  <div className="space-y-2.5">
                    {parsedSections.projects.map((proj, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl border border-slate-200 bg-white">
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                          <div className="font-bold text-xs text-slate-900 flex items-center gap-2">
                            <span>{proj.title}</span>
                            {proj.link && (
                              <a
                                href={proj.link.startsWith("http") ? proj.link : `https://${proj.link}`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-0.5 text-[10px] text-indigo-600 hover:underline font-normal"
                              >
                                <ExternalLink className="w-2.5 h-2.5" />
                                <span>Link</span>
                              </a>
                            )}
                          </div>
                        </div>

                        {proj.description && (
                          <p className="text-xs text-slate-600 leading-relaxed mb-2">
                            {proj.description}
                          </p>
                        )}

                        {proj.responsibilities_and_outcomes && proj.responsibilities_and_outcomes.length > 0 && (
                          <ul className="list-disc list-inside text-xs text-slate-600 space-y-1 pl-1">
                            {proj.responsibilities_and_outcomes.map((item, i) => (
                              <li key={i} className="leading-relaxed">
                                {item}
                              </li>
                            ))}
                          </ul>
                        )}

                        {proj.technologies && proj.technologies.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1 mt-2.5 pt-2 border-t border-slate-100">
                            <span className="text-[10px] font-semibold text-slate-400">Tech:</span>
                            {proj.technologies.map((t, i) => (
                              <span
                                key={i}
                                className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-50/70 text-indigo-700 font-mono border border-indigo-100"
                              >
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 3. Core Competencies */}
              <div>
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-indigo-600" />
                  3. Core Competencies & Skills
                </h4>
                {parsedSections?.competencies_by_category &&
                Object.keys(parsedSections.competencies_by_category).length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {Object.entries(parsedSections.competencies_by_category).map(([cat, skills]) => (
                      <div key={cat} className="p-3 rounded-xl border border-slate-200 bg-white">
                        <div className="text-[11px] font-bold text-slate-700 mb-1 capitalize">
                          {cat}
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {skills.map((s, i) => (
                            <span
                              key={i}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-mono"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-1.5 p-3 rounded-xl border border-slate-200 bg-white">
                    {(parsedSections?.core_competencies || []).map((comp, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 font-medium"
                      >
                        {comp}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* 4. Education & Credentials */}
              <div>
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                  <GraduationCap className="w-3.5 h-3.5 text-indigo-600" />
                  4. Education & Degrees
                </h4>
                <div className="space-y-2">
                  {(parsedSections?.education || []).map((edu, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-slate-200 bg-white flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-bold text-slate-900">{edu.degree_name}</div>
                        <div className="text-slate-500 font-medium">
                          {edu.institution} {edu.field_of_study ? `· ${edu.field_of_study}` : ""}
                        </div>
                      </div>
                      {edu.graduation_year && (
                        <span className="text-[10px] font-mono text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                          {edu.graduation_year}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* 5. Licenses */}
              {parsedSections?.certifications_and_licenses &&
                parsedSections.certifications_and_licenses.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-indigo-600" />
                      5. Certifications & Licenses
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {parsedSections.certifications_and_licenses.map((cert, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold"
                        >
                          <Award className="w-3 h-3 text-emerald-600" />
                          {cert}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
            </div>
          ) : activeTab === "scoring" ? (
            /* Scoring & Diagnostics */
            <div className="space-y-5">
              {/* Total Fit Score */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Total Calibrated Fit Score
                  </div>
                  <div className="text-3xl font-extrabold text-slate-900 mt-0.5 tabular-nums">
                    {candidate.fit_score}%
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                    Decision Verdict
                  </div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">
                    {candidate.verdict}
                  </div>
                </div>
              </div>

              {/* Dimensions */}
              {candidate.breakdown && (
                <div>
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-indigo-600" />
                    Multi-Dimensional Breakdown
                  </h4>
                  <div className="grid grid-cols-2 gap-2.5">
                    {Object.entries(candidate.breakdown).map(([dim, val]) => {
                      if (dim === "raw_weighted_total" || val === undefined) return null;
                      const formattedName = dim
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (c) => c.toUpperCase());
                      return (
                        <div key={dim} className="p-3 rounded-xl border border-slate-200 bg-white">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="font-semibold text-slate-700">{formattedName}</span>
                            <span className="font-bold text-slate-900 font-mono tabular-nums">
                              {val}%
                            </span>
                          </div>
                          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-indigo-600 rounded-full"
                              style={{ width: `${Math.min(100, Math.max(0, val))}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Hard Gates Audit */}
              <div>
                <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
                  Criteria & Hard Gate Audit
                </h4>

                <div className="space-y-2">
                  {questionsList.map((q, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border text-xs ${
                        q.is_mandatory
                          ? "border-rose-200/80 bg-rose-50/20"
                          : "border-slate-200 bg-white"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900">{q.name}</span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                            {q.primitive}
                          </span>
                        </div>
                        {q.is_mandatory && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 font-bold">
                            Mandatory Gate
                          </span>
                        )}
                      </div>
                      <p className="text-slate-600 font-mono text-[11px] leading-relaxed">
                        {q.instructions}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Raw Text */
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700">
                  Extracted Raw Text ({rawText.length} characters)
                </span>
                <button
                  type="button"
                  onClick={handleCopyRaw}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium cursor-pointer"
                >
                  {copiedRaw ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-500" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>

              <pre className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 font-mono text-xs whitespace-pre-wrap leading-relaxed max-h-[550px] overflow-y-auto">
                {rawText || "No raw text available."}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
