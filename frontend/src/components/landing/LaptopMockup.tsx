"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Sparkles,
  Briefcase,
  Layers,
  Cpu,
  Award,
  Activity,
  ChevronRight,
  Star,
  Zap,
} from "lucide-react";

export const LaptopMockup: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"split" | "score" | "jobs">("split");

  return (
    <div className="relative w-full max-w-5xl mx-auto pt-8 pb-4 select-none">
      {/* Subtle Glow Effect behind Laptop */}
      <div className="absolute inset-0 bg-gradient-to-t from-blue-400/15 via-[#ffd02f]/10 to-transparent blur-3xl -z-10 rounded-full scale-95 transform -translate-y-6" />

      {/* Laptop Screen Bezel */}
      <div className="relative mx-auto rounded-t-2xl sm:rounded-t-3xl bg-slate-900 p-2 sm:p-3 border-t border-x border-slate-700 shadow-[0_20px_50px_-10px_rgba(5,0,56,0.18)]">
        {/* Webcam / Notch Dot */}
        <div className="absolute top-1.5 sm:top-2 left-1/2 -translate-x-1/2 flex items-center gap-1.5 z-20">
          <div className="w-1.5 h-1.5 rounded-full bg-slate-700 border border-slate-600"></div>
          <div className="w-1 h-1 rounded-full bg-emerald-500/80 animate-pulse"></div>
        </div>

        {/* Laptop Display Screen (Crisp Modern Light UI) */}
        <div className="rounded-t-xl bg-slate-50 text-slate-900 overflow-hidden border border-slate-200 font-sans shadow-inner">
          {/* Top Browser Bar */}
          <div className="bg-white px-3 sm:px-4 py-2.5 border-b border-slate-200 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              </div>
              <div className="bg-slate-100 px-3 py-1 rounded-full text-[11px] text-slate-600 font-mono hidden sm:inline ml-2 border border-slate-200">
                https://careerlens.ai/review/session-992
              </div>
            </div>

            {/* View Switcher Tabs */}
            <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-[11px]">
              <button
                type="button"
                onClick={() => setActiveTab("split")}
                className={`px-2.5 py-1 rounded-md transition font-medium ${
                  activeTab === "split"
                    ? "bg-white text-[#050038] shadow-xs font-bold"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                Dual View
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("score")}
                className={`px-2.5 py-1 rounded-md transition font-medium ${
                  activeTab === "score"
                    ? "bg-white text-[#050038] shadow-xs font-bold"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                Resume & Bullets
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("jobs")}
                className={`px-2.5 py-1 rounded-md transition font-medium ${
                  activeTab === "jobs"
                    ? "bg-white text-[#050038] shadow-xs font-bold"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                Recommended Jobs
              </button>
            </div>
          </div>

          {/* Screen Content Dashboard */}
          <div className="p-3 sm:p-5 grid grid-cols-1 lg:grid-cols-12 gap-4 text-left bg-slate-50">
            {/* LEFT / MAIN COLUMN: Score Gauge, Dimension Bars & Bullets */}
            {(activeTab === "split" || activeTab === "score") && (
              <div
                className={`${
                  activeTab === "split" ? "lg:col-span-7" : "lg:col-span-12"
                } space-y-3.5`}
              >
                {/* Score Summary Card */}
                <div className="bg-white p-3.5 sm:p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="relative flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-black text-2xl shadow-sm">
                      84
                      <span className="text-[10px] absolute -bottom-1 font-semibold text-emerald-900 bg-emerald-100 px-1.5 rounded-full border border-emerald-300">
                        / 100
                      </span>
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-bold text-[#050038]">
                          Strong ATS & Recruiter Fit
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200">
                          Interview Ready
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Decision Engine: <strong className="text-slate-800">Selected</strong> (Confidence: 94.2%)
                      </p>
                    </div>
                  </div>

                  {/* Segmented Color Track */}
                  <div className="w-full sm:w-44 space-y-1">
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono font-medium">
                      <span>ATS Score</span>
                      <span className="text-emerald-700 font-bold">Top 10%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100 border border-slate-200 overflow-hidden flex">
                      <div className="w-[45%] bg-rose-400" />
                      <div className="w-[25%] bg-[#ffd02f]" />
                      <div className="w-[30%] bg-emerald-500 relative">
                        <div className="absolute right-1 top-0 bottom-0 w-1.5 bg-[#050038] rounded-full" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* 4 Dimension Meters Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                    <div className="text-[10px] text-slate-500 font-bold flex items-center gap-1">
                      <Cpu className="w-3 h-3 text-[#4262ff]" />
                      Technical
                    </div>
                    <div className="text-sm font-black text-[#050038] mt-1">88%</div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div className="bg-[#4262ff] h-full rounded-full w-[88%]" />
                    </div>
                  </div>

                  <div className="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                    <div className="text-[10px] text-slate-500 font-bold flex items-center gap-1">
                      <Award className="w-3 h-3 text-indigo-500" />
                      Experience
                    </div>
                    <div className="text-sm font-black text-[#050038] mt-1">82%</div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div className="bg-indigo-500 h-full rounded-full w-[82%]" />
                    </div>
                  </div>

                  <div className="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                    <div className="text-[10px] text-slate-500 font-bold flex items-center gap-1">
                      <Activity className="w-3 h-3 text-purple-500" />
                      Domain Fit
                    </div>
                    <div className="text-sm font-black text-[#050038] mt-1">78%</div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div className="bg-purple-500 h-full rounded-full w-[78%]" />
                    </div>
                  </div>

                  <div className="bg-white p-2.5 rounded-xl border border-slate-200 shadow-2xs">
                    <div className="text-[10px] text-slate-500 font-bold flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-emerald-500" />
                      Impact
                    </div>
                    <div className="text-sm font-black text-[#050038] mt-1">70%</div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div className="bg-emerald-500 h-full rounded-full w-[70%]" />
                    </div>
                  </div>
                </div>

                {/* Line-by-Line Bullet Review Preview */}
                <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-bold text-[#050038]">
                    <span>Line-by-Line Resume Bullet Audit</span>
                    <span className="text-[10px] text-[#4262ff] font-semibold">Recruiter Rubric</span>
                  </div>

                  <div className="space-y-2 text-xs">
                    {/* Bullet 1 - Strong */}
                    <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 space-y-1">
                      <div className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                        <span className="text-slate-800">
                          "Architected multi-agent RAG workflow with FastAPI & Redis, reducing query latency by <strong>42%</strong>."
                        </span>
                      </div>
                      <div className="flex gap-1.5 pl-5 text-[10px]">
                        <span className="text-emerald-800 font-semibold bg-emerald-100 px-1.5 py-0.5 rounded">
                          ✓ Strong Action Verb
                        </span>
                        <span className="text-emerald-800 font-semibold bg-emerald-100 px-1.5 py-0.5 rounded">
                          ✓ Quantified Metric (42%)
                        </span>
                      </div>
                    </div>

                    {/* Bullet 2 - Warning */}
                    <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 space-y-1">
                      <div className="flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-600 mt-0.5 shrink-0" />
                        <span className="text-slate-800">
                          "Helped manage databases and assisted team members in building microservices."
                        </span>
                      </div>
                      <div className="flex gap-1.5 pl-5 text-[10px]">
                        <span className="text-amber-800 font-semibold bg-amber-100 px-1.5 py-0.5 rounded">
                          ⚠ Passive Voice ("Helped")
                        </span>
                        <span className="text-amber-800 font-semibold bg-amber-100 px-1.5 py-0.5 rounded">
                          ⚠ Missing Quantified Scale
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* RIGHT COLUMN: Target Job Description Match & Top Recommended Job */}
            {(activeTab === "split" || activeTab === "jobs") && (
              <div
                className={`${
                  activeTab === "split" ? "lg:col-span-5" : "lg:col-span-12"
                } space-y-3.5`}
              >
                {/* Target Vacancy Card */}
                <div className="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-2xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                      <Briefcase className="w-3 h-3 text-[#4262ff]" />
                      Target Job Match
                    </span>
                    <span className="text-[10px] text-[#4262ff] font-bold bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                      91% Overlap
                    </span>
                  </div>
                  <div className="text-xs font-bold text-[#050038]">
                    Senior AI / Backend Engineer
                  </div>
                  <div className="flex flex-wrap gap-1 text-[10px]">
                    <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 font-medium border border-emerald-200">
                      ✓ Python
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 font-medium border border-emerald-200">
                      ✓ FastAPI
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 font-medium border border-emerald-200">
                      ✓ LangChain
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 font-medium border border-amber-200">
                      missing: Kubernetes
                    </span>
                  </div>
                </div>

                {/* Top Recommended Job Card with Link */}
                <div className="bg-white p-3.5 rounded-2xl border border-blue-200 shadow-sm space-y-2.5 relative overflow-hidden">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#4262ff] text-white flex items-center gap-1">
                        <Zap className="w-2.5 h-2.5 fill-white" /> #1 Recommended
                      </span>
                    </div>
                    <span className="text-xs font-bold text-emerald-700">
                      94% Raw Fit
                    </span>
                  </div>

                  <div>
                    <h4 className="text-xs sm:text-sm font-bold text-[#050038] flex items-center gap-1">
                      Senior Staff AI Platform Engineer
                      <ExternalLink className="w-3 h-3 text-slate-400" />
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Stripe &bull; San Francisco, CA (Hybrid / Remote)
                    </p>
                  </div>

                  <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed">
                    Build deterministic AI pipelines and orchestrate high-reliability data systems with mathematical precision.
                  </p>

                  <div className="pt-1 flex items-center justify-between">
                    <span className="text-[10px] text-emerald-800 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                      High Fit Match
                    </span>

                    <a
                      href="https://stripe.com/jobs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[11px] font-bold text-white bg-[#4262ff] hover:bg-[#3151eb] px-3 py-1 rounded-full transition shadow-xs"
                    >
                      Apply Link
                      <ChevronRight className="w-3 h-3" />
                    </a>
                  </div>
                </div>

                {/* Second Recommended Job Card */}
                <div className="bg-white p-3 rounded-2xl border border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-400">#2 Ranked Match</span>
                    <span className="text-[11px] font-bold text-[#4262ff]">89% Fit</span>
                  </div>
                  <h4 className="text-xs font-semibold text-slate-800">
                    Lead Backend Systems Architect
                  </h4>
                  <p className="text-[10px] text-slate-500">Datadog &bull; Remote</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Realistic Laptop Base & Trackpad Hinge */}
      <div className="relative mx-auto w-full max-w-[102%] -mt-1 sm:-mt-1.5 h-3 sm:h-4 bg-gradient-to-b from-slate-300 via-slate-400 to-slate-500 rounded-b-2xl shadow-xl flex items-center justify-center border-t border-slate-300">
        {/* Trackpad Thumb Indent */}
        <div className="w-20 sm:w-28 h-1 sm:h-1.5 bg-slate-400 rounded-full"></div>
      </div>
    </div>
  );
};
