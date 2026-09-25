"use client";

import React from "react";
import {
  CheckCircle2,
  AlertCircle,
  Cpu,
  Layers,
  Sparkles,
  Zap,
  ArrowRight,
  ExternalLink,
  Search,
  Scale,
  ShieldCheck,
  FileCheck,
  TrendingUp,
  Briefcase,
} from "lucide-react";

interface CareerLensFeaturesProps {
  onStartAnalysis: () => void;
  onOpenEnterprise: () => void;
}

export const CareerLensFeatures: React.FC<CareerLensFeaturesProps> = ({
  onStartAnalysis,
  onOpenEnterprise,
}) => {
  return (
    <section id="about" className="bg-[#f8f9fc] text-slate-900 py-20 px-4 sm:px-6 lg:px-8 space-y-24 border-b border-slate-200 scroll-mt-20">
      <div className="max-w-6xl mx-auto space-y-24">
        {/* ── ROW 1: Improve Your Resume Score (Left graphic, Right text) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Graphic */}
          <div className="lg:col-span-6 order-2 lg:order-1">
            <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 space-y-4 relative overflow-hidden">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-blue-50 text-[#4262ff] border border-blue-200/60">
                    <FileCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Parsed Document Architecture</h4>
                    <span className="text-[11px] text-slate-500 font-medium">Standardized ATS Schema</span>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200">
                  98% ATS Readability
                </span>
              </div>

              {/* Extraction items */}
              <div className="space-y-2.5 text-xs">
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Contact & Identity</span>
                    <span className="text-slate-900 font-semibold">Alex Rivera &bull; alex@example.com</span>
                  </div>
                  <span className="text-emerald-700 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Extracted
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Experience Timeline</span>
                    <span className="text-slate-900 font-semibold">6.5 Years &bull; Senior Full-Stack Engineer</span>
                  </div>
                  <span className="text-emerald-700 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Verified
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Categorized Skills</span>
                    <span className="text-slate-900 font-semibold">18 Tech Skills &bull; 6 Architectural Domains</span>
                  </div>
                  <span className="text-emerald-700 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Indexed
                  </span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500">
                <span>0 Parsing Errors Detected</span>
                <span className="text-[#4262ff] font-semibold">Structured JSON Schema</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-6 space-y-5 order-1 lg:order-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#4262ff] bg-blue-50 px-3.5 py-1.5 rounded-full border border-blue-200">
              INSTANT ATS & RECRUITER FEEDBACK
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-[#050038] tracking-tight leading-tight font-sans">
              Improve your resume score
            </h2>
            <h3 className="text-lg font-semibold text-slate-700">
              Get actionable steps to optimize your resume for recruiters
            </h3>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
              75% of resumes are dropped by Applicant Tracking Systems (ATS) before reaching human eyes. Our engine extracts sections, dates, and credentials into typed JSON schema, grading formatting, keyword density, and structural readability.
            </p>

            <ul className="space-y-3 text-xs sm:text-sm text-slate-700">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Deterministic ATS section extraction and schema standardization</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Identification of parsing roadblocks, complex tables, and unreadable fonts</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Instant score boost recommendations with prioritized impact levels</span>
              </li>
            </ul>

            <div className="pt-2">
              <button
                type="button"
                onClick={onStartAnalysis}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-[#4262ff] hover:bg-[#3151eb] text-white font-bold text-xs sm:text-sm tracking-wide shadow-md shadow-blue-500/20 transition-all active:scale-98"
              >
                <span>Score my resume</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* ── ROW 2: Targeted to Your Job Description (Left text, Right graphic) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Content */}
          <div className="lg:col-span-6 space-y-5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#4262ff] bg-blue-50 px-3.5 py-1.5 rounded-full border border-blue-200">
              ROLE-SPECIFIC TARGETING
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-[#050038] tracking-tight leading-tight font-sans">
              Targeted to your job description
            </h2>
            <h3 className="text-lg font-semibold text-slate-700">
              Never send an un-tailored resume again
            </h3>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
              Compare your resume directly against any job description. The engine extracts the vacancy's core competencies, tools, and seniority requirements, instantly identifying critical keyword gaps and strengths.
            </p>

            <ul className="space-y-3 text-xs sm:text-sm text-slate-700">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Side-by-side skill matrix: Matched vs. Missing core requirements</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Domain alignment check: Cloud, architecture, and vertical overlap</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Tailored advice on incorporating high-frequency vacancy keywords</span>
              </li>
            </ul>

            <div className="pt-2">
              <button
                type="button"
                onClick={onStartAnalysis}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-[#4262ff] hover:bg-[#3151eb] text-white font-bold text-xs sm:text-sm tracking-wide shadow-md shadow-blue-500/20 transition-all active:scale-98"
              >
                <span>Tailor to Job Description</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Graphic */}
          <div className="lg:col-span-6">
            <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">Target Job Comparison</h4>
                  <span className="text-[11px] text-slate-500 font-medium">Senior Cloud AI Engineer</span>
                </div>
                <span className="px-3 py-1 rounded-full bg-blue-50 text-[#4262ff] text-xs font-bold border border-blue-200">
                  91% Role Overlap
                </span>
              </div>

              {/* Matched Skills */}
              <div className="space-y-2">
                <span className="text-[11px] text-emerald-700 font-bold uppercase tracking-wider block">
                  Matched Core Requirements (12/14)
                </span>
                <div className="flex flex-wrap gap-1.5 text-xs">
                  {["Python", "FastAPI", "PostgreSQL", "Docker", "LangChain", "Redis", "REST APIs", "CI/CD"].map(
                    (s) => (
                      <span
                        key={s}
                        className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 font-semibold border border-emerald-200"
                      >
                        ✓ {s}
                      </span>
                    )
                  )}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <span className="text-[11px] text-amber-800 font-bold uppercase tracking-wider block">
                  High-Priority Missing Keywords (2)
                </span>
                <div className="flex flex-wrap gap-1.5 text-xs">
                  {["Kubernetes (K8s)", "Terraform IaC"].map((s) => (
                    <span
                      key={s}
                      className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 font-semibold border border-amber-200"
                    >
                      ⚠ {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── ROW 3: Powered by ConvAI Laya Decision Engine (Left graphic, Right text) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Graphic */}
          <div className="lg:col-span-6 order-2 lg:order-1">
            <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-blue-50 text-[#4262ff] shadow-xs border border-blue-200">
                    <Scale className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Deterministic Decision Matrix</h4>
                    <span className="text-[11px] text-slate-500 font-medium">Calibrated Competency Classifier</span>
                  </div>
                </div>
                <span className="px-3 py-1 rounded-full bg-[#ffd02f] text-[#050038] text-xs font-black">
                  0.28s Inference
                </span>
              </div>

              {/* Probability Vector Bands */}
              <div className="space-y-3.5 text-xs">
                <div>
                  <div className="flex justify-between text-slate-700 mb-1 font-medium">
                    <span>Selection Probability: <strong className="text-slate-900">High</strong></span>
                    <span className="text-emerald-700 font-bold">88.4%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full w-[88.4%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-slate-700 mb-1 font-medium">
                    <span>Borderline Margin: <strong className="text-slate-900">Medium</strong></span>
                    <span className="text-amber-700 font-bold">8.6%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-amber-400 h-full rounded-full w-[8.6%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-slate-700 mb-1 font-medium">
                    <span>Rejection Probability: <strong className="text-slate-900">Low</strong></span>
                    <span className="text-rose-600 font-bold">3.0%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-rose-500 h-full rounded-full w-[3.0%]" />
                  </div>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-blue-50/80 border border-blue-200/80 text-xs text-blue-900 font-medium">
                <strong>Decision Output:</strong> Candidate qualifies for immediate technical interview stage. Zero hallucinations detected.
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-6 space-y-5 order-1 lg:order-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#4262ff] bg-blue-50 px-3.5 py-1.5 rounded-full border border-blue-200">
              DETERMINISTIC EVALUATION ENGINE
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-[#050038] tracking-tight leading-tight font-sans">
              Powered by Deterministic Fit Engine
            </h2>
            <h3 className="text-lg font-semibold text-slate-700">
              Zero hallucinations, 10x faster deterministic grading
            </h3>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
              Evaluates candidate profiles across closed mathematical benchmark spaces with calibrated entropy thresholds, eliminating scoring drift and hallucination.
            </p>

            <ul className="space-y-3 text-xs sm:text-sm text-slate-700">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Sub-second inference: 0.2s - 0.4s lightning-fast evaluation</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Deterministic rubric: 4 weighted dimensions with explicit pass/fail cutoffs</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-[#4262ff] shrink-0" />
                <span>Calibrated entropy confidence score providing audit-grade explainability</span>
              </li>
            </ul>

            <div className="pt-2 flex items-center gap-3">
              <button
                type="button"
                onClick={onOpenEnterprise}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all active:scale-98"
              >
                <Zap className="w-4 h-4 text-[#ffd02f] fill-[#ffd02f]" />
                <span>Enterprise Bulk Screener</span>
              </button>
            </div>
          </div>
        </div>

        {/* ── ROW 4: Bullet Analysis & Top Recommended Jobs (Left text, Right graphic) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Content */}
          <div className="lg:col-span-6 space-y-5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#4262ff] bg-blue-50 px-3.5 py-1.5 rounded-full border border-blue-200">
              ACTIONABLE BULLETS & LIVE JOBS
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-[#050038] tracking-tight leading-tight font-sans">
              Line-by-line bullet analysis & Top Recommended Jobs
            </h2>
            <h3 className="text-lg font-semibold text-slate-700">
              Transform weak bullets & discover live matching vacancies
            </h3>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
              Recruiters spend an average of 6 seconds per resume. Our line-by-line analyzer ensures your bullets start with powerful action verbs and quantifiable deliverables. Then, our SerpApi integration matches your profile to live job postings with clickable apply links!
            </p>

            <ul className="space-y-3 text-xs sm:text-sm text-slate-700">
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Action verb power rating and metrics quantification checker</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Live Google Jobs / SerpApi market opportunities with direct apply links</span>
              </li>
              <li className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Instant strategic match probability check for every job opening</span>
              </li>
            </ul>

            <div className="pt-2">
              <button
                type="button"
                onClick={onStartAnalysis}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-[#4262ff] hover:bg-[#3151eb] text-white font-bold text-xs sm:text-sm tracking-wide shadow-md shadow-blue-500/20 transition-all active:scale-98"
              >
                <span>Score Candidate Resume</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Graphic: Live Recommended Jobs */}
          <div className="lg:col-span-6">
            <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/50 space-y-3.5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-[#4262ff]" />
                  <h4 className="text-sm font-bold text-slate-900">Live Market Recommendations</h4>
                </div>
                <span className="text-xs text-slate-500 font-mono">Ranked by Compatibility</span>
              </div>

              {/* Job 1 */}
              <div className="p-4 rounded-2xl bg-blue-50/50 border border-blue-200/80 space-y-2 hover:border-[#4262ff] transition">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-[#4262ff] text-white">
                    #1 Match &bull; High Alignment
                  </span>
                  <span className="text-xs font-bold text-emerald-700">94% Fit</span>
                </div>
                <div>
                  <h5 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    Senior AI / Full-Stack Platform Engineer
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                  </h5>
                  <p className="text-xs text-slate-500">Stripe &bull; San Francisco, CA (Remote)</p>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <div className="flex gap-1.5 text-[10px]">
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-700 font-medium">FastAPI</span>
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-700 font-medium">Python</span>
                    <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-700 font-medium">Docker</span>
                  </div>
                  <a
                    href="https://stripe.com/jobs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-bold text-[#4262ff] hover:text-[#3151eb] flex items-center gap-1"
                  >
                    Apply Now <ArrowRight className="w-3 h-3" />
                  </a>
                </div>
              </div>

              {/* Job 2 */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-slate-500">#2 Ranked Opportunity</span>
                  <span className="text-xs font-bold text-[#4262ff]">89% Fit</span>
                </div>
                <h5 className="text-xs font-bold text-slate-800">Staff Backend Systems Architect</h5>
                <p className="text-[11px] text-slate-500">Datadog &bull; New York, NY</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
