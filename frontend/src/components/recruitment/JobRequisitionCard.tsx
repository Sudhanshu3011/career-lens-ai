"use client";

import React, { useState } from "react";
import {
  Briefcase,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  Database,
  Sliders,
  ChevronRight,
  Code2,
  Stethoscope,
  TrendingUp,
  Boxes,
} from "lucide-react";
import { JobRequisition } from "@/lib/types";

interface JobPreset {
  title: string;
  industry: string;
  icon: React.ElementType;
  description: string;
}

const PRESETS: JobPreset[] = [
  {
    title: "Senior Full-Stack AI Engineer",
    industry: "Tech & AI",
    icon: Code2,
    description: `We are looking for a Senior Full-Stack AI Engineer with 5+ years of experience building scalable backend microservices and high-performance APIs. The ideal candidate should be proficient in Python, FastAPI, TypeScript, React, and Next.js.
Requirements:
• 5+ years of experience building scalable backend microservices and high-performance APIs.
• Proficient in Python, FastAPI, TypeScript, React, and Next.js.
• Strong hands-on experience with PostgreSQL, Redis, Docker, and Kubernetes.
• Experience with AI application frameworks, vector databases, and deterministic scoring pipelines.
• Demonstrated ownership of distributed cloud systems handling high concurrent throughput.`,
  },
  {
    title: "Critical Care ICU Charge Nurse",
    industry: "Healthcare",
    icon: Stethoscope,
    description: `Registered Nurse (RN) with minimum 4 years of acute care experience in an Intensive Care Unit (ICU). Must hold an active, unencumbered state RN license and current BLS/ACLS/CCRN certifications.
Requirements:
• 4+ years of professional bedside experience in Level I or II Trauma ICU.
• Active and unencumbered Registered Nurse (RN) State License.
• Valid certifications in ACLS, BLS, and CCRN.
• Demonstrated clinical competency in mechanical ventilator titration, hemodynamic monitoring, and rapid emergency intervention.
• Experience precepting junior clinical nursing staff.`,
  },
  {
    title: "Senior Quantitative Risk Analyst",
    industry: "Finance",
    icon: TrendingUp,
    description: `Senior Quantitative Risk Analyst responsible for credit risk modeling, stress testing, and Basel III regulatory capital calculations. Minimum 5 years in quantitative finance or investment banking.
Requirements:
• 5+ years of professional financial engineering or quantitative credit risk modeling.
• Strong mathematical foundation in Monte Carlo simulations, Value-at-Risk (VaR), and stress testing.
• Advanced proficiency in Python (NumPy, SciPy, Pandas), SQL, and statistical packages (R or MATLAB).
• Bachelor's or Master's degree in Financial Engineering, Quantitative Finance, Mathematics, or Physics.
• Familiarity with Federal Reserve CCAR/DFAST regulatory frameworks.`,
  },
  {
    title: "Supply Chain Operations Manager",
    industry: "Operations",
    icon: Boxes,
    description: `Experienced Supply Chain Manager to oversee global freight logistics, vendor procurement contracts, and multi-tier distribution networks across North America and APAC.
Requirements:
• 6+ years in end-to-end supply chain operations, demand planning, and warehouse management.
• Proven track record reducing logistics freight costs and customs turnaround times.
• Deep expertise in ERP systems (SAP S/4HANA or Oracle NetSuite) and advanced Excel/PowerBI analytics.
• Demonstrated leadership managing cross-functional procurement and warehouse teams.
• APICS CSCP or CPIM certification preferred.`,
  },
];

interface JobRequisitionCardProps {
  jobRole: string;
  setJobRole: (val: string) => void;
  jobDescription: string;
  setJobDescription: (val: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  requisition: JobRequisition | null;
  onOpenQuestionStudio: () => void;
}

export const JobRequisitionCard: React.FC<JobRequisitionCardProps> = ({
  jobRole,
  setJobRole,
  jobDescription,
  setJobDescription,
  onAnalyze,
  isLoading,
  requisition,
  onOpenQuestionStudio,
}) => {
  const [selectedPresetIndex, setSelectedPresetIndex] = useState<number | null>(0);

  const handleSelectPreset = (index: number) => {
    setSelectedPresetIndex(index);
    setJobRole(PRESETS[index].title);
    setJobDescription(PRESETS[index].description);
  };

  const questionCount = requisition?.questions ? Object.keys(requisition.questions).length : 0;
  const mandatoryCount = requisition?.questions
    ? Object.values(requisition.questions).filter((q) => q.is_mandatory).length
    : 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card hover:shadow-card-hover transition-all overflow-hidden flex flex-col">
      {/* Header bar */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Briefcase className="w-4 h-4 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              1. Job Requisition & Criteria Blueprint
            </h2>
          </div>
        </div>

        {requisition && (
          <div className="flex items-center gap-2">
            {requisition.cached ? (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <Database className="w-3 h-3 text-emerald-600" />
                Cached DB (0s)
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                <Sparkles className="w-3 h-3 text-indigo-600" />
                Synthesized
              </span>
            )}
          </div>
        )}
      </div>

      <div className="p-5 space-y-4">
        {/* Universal Industry Presets */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Select Universal Domain Preset:
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {PRESETS.map((preset, idx) => {
              const isSelected = selectedPresetIndex === idx;
              const Icon = preset.icon;
              return (
                <button
                  key={preset.title}
                  type="button"
                  onClick={() => handleSelectPreset(idx)}
                  className={`text-left p-2.5 rounded-xl border text-xs transition-all cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? "border-indigo-600 bg-indigo-50/50 text-indigo-950 shadow-xs ring-1 ring-indigo-500/20"
                      : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/80 text-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                      {preset.industry}
                    </span>
                    <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-indigo-600" : "text-slate-400"}`} />
                  </div>
                  <div className="font-semibold text-xs leading-snug truncate w-full">
                    {preset.title}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Inputs */}
        <div className="space-y-3">
          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1">
              Target Job Title / Role
            </label>
            <input
              type="text"
              value={jobRole}
              onChange={(e) => {
                setJobRole(e.target.value);
                setSelectedPresetIndex(null);
              }}
              placeholder="e.g. Senior Full-Stack AI Engineer"
              className="w-full px-3.5 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-900 transition-all font-semibold shadow-xs"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider mb-1">
              Job Description & Candidate Qualifications
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => {
                setJobDescription(e.target.value);
                setSelectedPresetIndex(null);
              }}
              rows={4}
              placeholder="Paste job description with responsibilities, qualifications, and hard requirements..."
              className="w-full px-3.5 py-2 text-[11px] bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 text-slate-800 transition-all resize-y font-mono leading-relaxed"
            />
          </div>
        </div>

        {/* Action Button & Status Strip */}
        <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={onAnalyze}
            disabled={isLoading || !jobRole.trim() || !jobDescription.trim()}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-xs hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {isLoading ? (
              <>
                <Clock className="w-3.5 h-3.5 animate-spin" />
                <span>Synthesizing Criteria...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>{requisition ? "Re-Synthesize Criteria" : "Synthesize Criteria & Questions"}</span>
              </>
            )}
          </button>

          {requisition && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onOpenQuestionStudio}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <Sliders className="w-3.5 h-3.5 text-indigo-400" />
                <span>
                  Question Studio ({questionCount} Qs · {mandatoryCount} Gates)
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              </button>
            </div>
          )}
        </div>

        {/* Status Confirmation Pill */}
        {requisition && (
          <div className="pt-1">
            {requisition.is_reviewed ? (
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Criteria Confirmed & Locked · Candidate evaluation unlocked</span>
              </div>
            ) : (
              <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-amber-50 text-amber-900 border border-amber-200 text-xs font-semibold">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Review required in Question Studio before evaluating candidates</span>
                </div>
                <button
                  type="button"
                  onClick={onOpenQuestionStudio}
                  className="underline text-indigo-700 hover:text-indigo-900 cursor-pointer text-xs"
                >
                  Open Studio →
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
