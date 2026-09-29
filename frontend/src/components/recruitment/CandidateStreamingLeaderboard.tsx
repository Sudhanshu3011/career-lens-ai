"use client";

import React, { useState } from "react";
import {
  Trophy,
  Play,
  Loader2,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Eye,
  FileText,
  Layers,
  ArrowUpDown,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  ExternalLink,
  FolderGit2,
} from "lucide-react";
import { CandidateEvaluationItem, JobRequisition } from "@/lib/types";

interface CandidateStreamingLeaderboardProps {
  requisition: JobRequisition | null;
  evaluations: CandidateEvaluationItem[];
  isStreaming: boolean;
  onStartStreaming: () => void;
  canEvaluate: boolean;
  evaluationCount: number;
  totalUploads: number;
  onInspectCandidate: (candidate: CandidateEvaluationItem) => void;
  onViewPdf?: (candidateName: string) => void;
  activeEngine: "laya" | "jev";
}

export const CandidateStreamingLeaderboard: React.FC<CandidateStreamingLeaderboardProps> = ({
  requisition,
  evaluations,
  isStreaming,
  onStartStreaming,
  canEvaluate,
  evaluationCount,
  totalUploads,
  onInspectCandidate,
  onViewPdf,
  activeEngine,
}) => {
  const [filterVerdict, setFilterVerdict] = useState<"ALL" | "ADVANCE" | "HOLD" | "REJECT">("ALL");
  const [sortBy, setSortBy] = useState<"score_desc" | "score_asc">("score_desc");

  const filtered = evaluations
    .filter((c) => {
      if (filterVerdict === "ALL") return true;
      return c.verdict?.toUpperCase() === filterVerdict;
    })
    .sort((a, b) => {
      if (sortBy === "score_desc") return b.fit_score - a.fit_score;
      return a.fit_score - b.fit_score;
    });

  const advanceCount = evaluations.filter((e) => e.verdict?.toUpperCase() === "ADVANCE").length;
  const holdCount = evaluations.filter((e) => e.verdict?.toUpperCase() === "HOLD").length;
  const rejectCount = evaluations.filter((e) => e.verdict?.toUpperCase() === "REJECT").length;
  const avgScore =
    evaluations.length > 0
      ? (evaluations.reduce((sum, e) => sum + e.fit_score, 0) / evaluations.length).toFixed(1)
      : "0";

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card hover:shadow-card-hover transition-all overflow-hidden flex flex-col">
      {/* Header Bar */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/60">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <Trophy className="w-4 h-4 text-emerald-600" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              3. Screening Stream & Candidate Rankings
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200/80">
                {activeEngine.toUpperCase()}
              </span>
            </h2>
          </div>
        </div>

        {/* Primary Evaluation Stream Trigger Button */}
        <div>
          <button
            type="button"
            onClick={onStartStreaming}
            disabled={!canEvaluate || isStreaming}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer ${
              canEvaluate && !isStreaming
                ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-500/20 hover:shadow-md"
                : "bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200"
            }`}
            title={
              !requisition?.is_reviewed
                ? "Recruiter must confirm questions in Studio first"
                : totalUploads === 0
                ? "Please upload resume PDFs first"
                : "Begin real-time evaluation"
            }
          >
            {isStreaming ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Screening ({evaluations.length}/{totalUploads})...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>
                  {evaluations.length > 0 ? "Re-Run Real-Time Stream" : "Start Live Screening Stream"}
                </span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Streaming Active Notification Bar */}
      {isStreaming && (
        <div className="px-5 py-2.5 bg-gradient-to-r from-indigo-50 to-blue-50 border-b border-indigo-100 flex items-center justify-between text-xs text-indigo-900 animate-pulse">
          <div className="flex items-center gap-2 font-medium">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />
            <span>
              Evaluating resumes with memory throttle (max 2 concurrent)... Yielding candidates as each completes.
            </span>
          </div>
          <span className="font-mono font-bold text-indigo-700">
            {evaluations.length} / {totalUploads} evaluated
          </span>
        </div>
      )}

      {/* KPI Stats Strip */}
      {evaluations.length > 0 && (
        <div className="p-4 border-b border-slate-100 bg-slate-50/40 space-y-3">
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="bg-white p-2 rounded-xl border border-slate-200/80 shadow-2xs">
              <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Evaluated
              </div>
              <div className="text-base font-bold text-slate-900 mt-0.5 tabular-nums">
                {evaluations.length} / {totalUploads}
              </div>
            </div>

            <div className="bg-white p-2 rounded-xl border border-slate-200/80 shadow-2xs">
              <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Avg Fit
              </div>
              <div className="text-base font-bold text-indigo-600 mt-0.5 tabular-nums">
                {avgScore}%
              </div>
            </div>

            <div className="bg-white p-2 rounded-xl border border-slate-200/80 shadow-2xs">
              <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Advance
              </div>
              <div className="text-base font-bold text-emerald-600 mt-0.5 tabular-nums">
                {advanceCount}
              </div>
            </div>

            <div className="bg-white p-2 rounded-xl border border-slate-200/80 shadow-2xs">
              <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                Hold / Reject
              </div>
              <div className="text-base font-bold text-slate-700 mt-0.5 tabular-nums">
                {holdCount} / {rejectCount}
              </div>
            </div>
          </div>

          {/* Filter & Sort Controls */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-[11px] font-semibold">
              <button
                type="button"
                onClick={() => setFilterVerdict("ALL")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  filterVerdict === "ALL"
                    ? "bg-white text-slate-900 shadow-2xs"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                All ({evaluations.length})
              </button>
              <button
                type="button"
                onClick={() => setFilterVerdict("ADVANCE")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  filterVerdict === "ADVANCE"
                    ? "bg-white text-emerald-700 shadow-2xs font-bold"
                    : "text-slate-500 hover:text-emerald-700"
                }`}
              >
                Advance ({advanceCount})
              </button>
              <button
                type="button"
                onClick={() => setFilterVerdict("HOLD")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  filterVerdict === "HOLD"
                    ? "bg-white text-amber-700 shadow-2xs font-bold"
                    : "text-slate-500 hover:text-amber-700"
                }`}
              >
                Hold ({holdCount})
              </button>
              <button
                type="button"
                onClick={() => setFilterVerdict("REJECT")}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  filterVerdict === "REJECT"
                    ? "bg-white text-rose-700 shadow-2xs font-bold"
                    : "text-slate-500 hover:text-rose-700"
                }`}
              >
                Reject ({rejectCount})
              </button>
            </div>

            <button
              type="button"
              onClick={() =>
                setSortBy((prev) => (prev === "score_desc" ? "score_asc" : "score_desc"))
              }
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 bg-white text-slate-700 text-[11px] font-medium cursor-pointer"
            >
              <ArrowUpDown className="w-3 h-3 text-slate-400" />
              <span>{sortBy === "score_desc" ? "Highest Score" : "Lowest Score"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Candidate Cards Roster */}
      <div className="p-4 flex-1 overflow-y-auto">
        {evaluations.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-slate-200/80 rounded-2xl flex flex-col items-center justify-center">
            <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center mb-2">
              <Trophy className="w-5 h-5 text-slate-400" />
            </div>
            <h3 className="text-xs font-bold text-slate-700">No Candidate Evaluations Active</h3>
            <p className="text-[11px] text-slate-400 mt-0.5 max-w-xs">
              {!requisition
                ? "Synthesize job criteria to start."
                : !requisition.is_reviewed
                ? "Confirm criteria in Question Studio to unlock evaluation."
                : totalUploads === 0
                ? "Upload candidate PDFs to begin."
                : "Click 'Start Live Screening Stream' above."}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((candidate, idx) => {
              const rank = idx + 1;
              const isAdvance = candidate.verdict?.toUpperCase() === "ADVANCE";
              const isHold = candidate.verdict?.toUpperCase() === "HOLD";
              const isReject = candidate.verdict?.toUpperCase() === "REJECT";

              const scoreBg =
                candidate.fit_score >= 80
                  ? "bg-emerald-500"
                  : candidate.fit_score >= 60
                  ? "bg-amber-500"
                  : "bg-rose-500";

              return (
                <div
                  key={candidate.evaluation_id || candidate.resume_id}
                  className="p-3.5 rounded-xl border border-slate-200/90 hover:border-indigo-300 bg-white shadow-2xs hover:shadow-card transition-all animate-in fade-in slide-in-from-top-2 duration-150"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    {/* Rank & Candidate Identity */}
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                          rank === 1
                            ? "bg-amber-100 text-amber-900 border border-amber-300"
                            : rank === 2
                            ? "bg-slate-200 text-slate-700"
                            : rank === 3
                            ? "bg-amber-50 text-amber-800"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        #{rank}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs font-bold text-slate-900">
                            {candidate.candidate_name || "Candidate"}
                          </h4>

                          {isAdvance && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.2 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              ADVANCE
                            </span>
                          )}
                          {isHold && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.2 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                              <AlertCircle className="w-3 h-3 text-amber-600" />
                              HOLD
                            </span>
                          )}
                          {isReject && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.2 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                              <XCircle className="w-3 h-3 text-rose-600" />
                              REJECT
                            </span>
                          )}
                        </div>

                        <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                          ID: {candidate.resume_id.slice(0, 8)}... · {candidate.pipeline.toUpperCase()}
                        </div>
                      </div>
                    </div>

                    {/* Fit Score Progress Bar */}
                    <div className="flex items-center gap-3 min-w-[140px] sm:min-w-[180px]">
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-[11px] mb-1">
                          <span className="font-semibold text-slate-500">Fit</span>
                          <span className="font-bold text-slate-900 tabular-nums">
                            {candidate.fit_score}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${scoreBg}`}
                            style={{ width: `${Math.min(100, Math.max(0, candidate.fit_score))}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => onInspectCandidate(candidate)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-[11px] font-semibold transition-colors cursor-pointer shadow-xs"
                      >
                        <Eye className="w-3 h-3 text-indigo-400" />
                        <span>Inspect Dossier</span>
                      </button>

                      {onViewPdf && (
                        <button
                          type="button"
                          onClick={() => onViewPdf(candidate.candidate_name)}
                          className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                          title="View PDF"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Error Notification Banner if parsing/evaluation had issues */}
                  {candidate.error_message && (
                    <div className="mt-2.5 p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold">Evaluation/Extraction Notice: </span>
                        <span>{candidate.error_message}</span>
                      </div>
                    </div>
                  )}

                  {/* External Links Box (GitHub, LinkedIn, Portfolio URLs) */}
                  {candidate.portfolio_links && candidate.portfolio_links.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Links:</span>
                      {candidate.portfolio_links.map((link, lIdx) => {
                        const isGitHub = link.toLowerCase().includes("github");
                        const isLinkedIn = link.toLowerCase().includes("linkedin");
                        const label = isGitHub ? "GitHub" : isLinkedIn ? "LinkedIn" : "Portfolio";
                        return (
                          <a
                            key={lIdx}
                            href={link.startsWith("http") ? link : `https://${link}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-50/80 hover:bg-indigo-100 text-indigo-700 border border-indigo-200/80 transition-colors"
                          >
                            <ExternalLink className="w-2.5 h-2.5" />
                            <span>{label}</span>
                          </a>
                        );
                      })}
                    </div>
                  )}

                  {/* Extracted Projects Snippet Box */}
                  {candidate.projects && candidate.projects.length > 0 && (
                    <div className="mt-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/70">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                        <FolderGit2 className="w-3 h-3 text-indigo-600" />
                        <span>Key Projects & Technical Initiatives ({candidate.projects.length})</span>
                      </div>
                      <div className="space-y-1.5">
                        {candidate.projects.slice(0, 2).map((proj, pIdx) => (
                          <div key={pIdx} className="text-[11px] text-slate-700">
                            <div className="flex flex-wrap items-center gap-1.5">
                              <span className="font-bold text-slate-900">{proj.title}</span>
                              {proj.technologies && proj.technologies.slice(0, 4).map((t, tIdx) => (
                                <span key={tIdx} className="px-1.5 py-0.2 rounded bg-white border border-slate-200 text-slate-600 text-[9px] font-mono">
                                  {t}
                                </span>
                              ))}
                            </div>
                            {proj.responsibilities_and_outcomes && proj.responsibilities_and_outcomes[0] && (
                              <p className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">
                                • {proj.responsibilities_and_outcomes[0]}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Multi-Dimensional Calibrated Score Chips */}
                  {candidate.breakdown && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-[10px]">
                      {candidate.breakdown.competency_depth !== undefined && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700 font-mono tabular-nums">
                          Comp: {candidate.breakdown.competency_depth}%
                        </span>
                      )}
                      {candidate.breakdown.seniority_fit !== undefined && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700 font-mono tabular-nums">
                          Senior: {candidate.breakdown.seniority_fit}%
                        </span>
                      )}
                      {candidate.breakdown.experience_duration !== undefined && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700 font-mono tabular-nums">
                          Dur: {candidate.breakdown.experience_duration}%
                        </span>
                      )}
                      {candidate.breakdown.domain_alignment !== undefined && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700 font-mono tabular-nums">
                          Domain: {candidate.breakdown.domain_alignment}%
                        </span>
                      )}
                      {candidate.breakdown.evidence_quality !== undefined && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700 font-mono tabular-nums">
                          Evid: {candidate.breakdown.evidence_quality}%
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
