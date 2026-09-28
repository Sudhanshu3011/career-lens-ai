"use client";

import React from "react";
import {
  X,
  UserCheck,
  ShieldCheck,
  ShieldAlert,
  FileText,
  Briefcase,
  GraduationCap,
  Layers,
  Award,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { EnterpriseCandidate } from "@/lib/types";

interface CandidateInspectionModalProps {
  candidate: EnterpriseCandidate | null;
  onClose: () => void;
}

export const CandidateInspectionModal: React.FC<CandidateInspectionModalProps> = ({
  candidate,
  onClose,
}) => {
  if (!candidate) return null;

  const isSelected = candidate.decision === "SELECT" || candidate.decision === "Ready";
  const isRejected = candidate.decision === "REJECT" || candidate.decision === "Rejected";

  const statusLabel = isSelected ? "Ready" : isRejected ? "Rejected" : "Review";
  const statusColor = isSelected
    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
    : isRejected
    ? "bg-rose-50 text-rose-700 border-rose-200"
    : "bg-amber-50 text-amber-700 border-amber-200";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-3xl w-full overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-800 text-white font-bold text-sm flex items-center justify-center">
              {candidate.name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .slice(0, 2)
                .toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">{candidate.name}</h3>
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${statusColor}`}>
                  ● {statusLabel}
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {candidate.candidate_seniority_label || candidate.seniority_label || "Mid"}
                </span>
              </div>
              <p className="text-xs text-slate-500">{candidate.filename}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-xs text-slate-400 font-medium">Fit Score</div>
              <div className="text-xl font-black text-blue-600">{candidate.fit_score}%</div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Decision Reason Banner */}
          {candidate.decision_reason && (
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-700 leading-relaxed">
              <strong>Evaluation Note:</strong> {candidate.decision_reason}
            </div>
          )}

          {/* Dimension Breakdown */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-600" />
              Dimension Breakdown (0–100%)
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
              {[
                { label: "Technical", val: candidate.breakdown?.technical_requirements || 80 },
                { label: "Experience", val: candidate.breakdown?.experience_requirements || 75 },
                { label: "Domain", val: candidate.breakdown?.domain_alignment || 85 },
                { label: "Evidence", val: candidate.breakdown?.evidence_strength || 70 },
                { label: "Education", val: candidate.breakdown?.education_alignment || 90 },
              ].map((b) => (
                <div key={b.label} className="p-2.5 rounded-xl border border-slate-200 bg-white text-center">
                  <div className="text-[10px] text-slate-400 font-semibold uppercase">{b.label}</div>
                  <div className="text-base font-black text-slate-800 mt-0.5">{b.val}%</div>
                  <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden mt-1.5">
                    <div
                      className="bg-blue-600 h-full rounded-full"
                      style={{ width: `${Math.min(100, Math.max(5, b.val))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Technical Overlap */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Technical Skill Analysis
            </h4>
            <div className="space-y-2">
              <div className="text-xs">
                <span className="font-semibold text-slate-700">Matched Skills:</span>{" "}
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {(candidate.technical_overlap?.matched_skills?.length
                    ? candidate.technical_overlap.matched_skills
                    : candidate.skills.slice(0, 8)
                  ).map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-medium"
                    >
                      ✓ {s}
                    </span>
                  ))}
                </div>
              </div>

              {(candidate.technical_overlap?.missing_jd_skills?.length ||
                candidate.technical_overlap?.missing_skills?.length) && (
                <div className="text-xs pt-1">
                  <span className="font-semibold text-slate-700">Missing JD Skills:</span>{" "}
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {(
                      candidate.technical_overlap.missing_jd_skills ||
                      candidate.technical_overlap.missing_skills ||
                      []
                    ).map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-200 text-xs font-medium"
                      >
                        ✗ {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Resume Inspection Snippets */}
          {candidate.inspection && (
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-indigo-600" />
                Verified Resume Evidence Snippets
              </h4>

              {candidate.inspection.experience && (
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                  <span className="font-bold text-slate-800 block mb-1">Experience Block:</span>
                  <p className="text-slate-600 whitespace-pre-line leading-relaxed">
                    {candidate.inspection.experience.slice(0, 500)}...
                  </p>
                </div>
              )}

              {candidate.inspection.skills && (
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                  <span className="font-bold text-slate-800 block mb-1">Technical Skills Block:</span>
                  <p className="text-slate-600 leading-relaxed">{candidate.inspection.skills}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-100 flex justify-end bg-slate-50/50">
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-semibold bg-slate-800 hover:bg-slate-900 text-white rounded-lg transition-colors"
          >
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
};
