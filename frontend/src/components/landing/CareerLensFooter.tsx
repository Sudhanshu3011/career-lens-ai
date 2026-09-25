"use client";

import React from "react";
import { Sparkles, ShieldCheck, ArrowRight, Zap, Users } from "lucide-react";

interface CareerLensFooterProps {
  onSelectPortal: (portal: "candidate" | "enterprise") => void;
  onOpenQuickApply: () => void;
}

export const CareerLensFooter: React.FC<CareerLensFooterProps> = ({
  onSelectPortal,
  onOpenQuickApply,
}) => {
  return (
    <footer className="bg-[#050038] text-slate-300 py-16 px-4 sm:px-6 lg:px-8 text-xs font-sans">
      <div className="max-w-6xl mx-auto space-y-16">
        {/* 1. Miro-Style Deep Navy Closing CTA Banner */}
        <div className="rounded-3xl bg-gradient-to-r from-[#0b0452] via-[#050038] to-[#120857] border border-blue-900/60 p-8 sm:p-12 text-center space-y-6 relative overflow-hidden shadow-2xl">
          <div className="absolute -top-24 -left-24 w-60 h-60 bg-[#4262ff]/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-60 h-60 bg-[#ffd02f]/15 rounded-full blur-3xl pointer-events-none" />

          <div className="relative space-y-3 max-w-2xl mx-auto">
            <span className="text-xs font-bold uppercase tracking-widest text-[#ffd02f] bg-[#ffd02f]/10 px-3.5 py-1.5 rounded-full border border-[#ffd02f]/30">
              JOIN THOUSANDS OF SUCCESSFUL APPLICANTS
            </span>
            <h3 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Ready to land your dream interview?
            </h3>
            <p className="text-sm text-slate-300 font-normal">
              Scan your resume with CareerLens AI in seconds. Get instant recruiter scores, ATS formatting checks, and live job matches.
            </p>
          </div>

          <div className="relative flex flex-wrap items-center justify-center gap-3.5 pt-2">
            <button
              type="button"
              onClick={() => onSelectPortal("candidate")}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-[#4262ff] hover:bg-[#3151eb] text-white font-bold text-xs sm:text-sm tracking-wide shadow-lg shadow-blue-500/30 transition-all active:scale-98"
            >
              <span>Scan Candidate Resume</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => onSelectPortal("enterprise")}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-white/10 hover:bg-white/20 text-white font-bold text-xs sm:text-sm tracking-wide border border-white/20 transition-all active:scale-98"
            >
              <Users className="w-4 h-4 text-emerald-400" />
              <span>Enterprise Screener</span>
            </button>
          </div>
        </div>

        {/* 2. Structured Footer Links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-4">
          {/* Brand Column */}
          <div className="col-span-2 space-y-4">
            <div className="flex items-center space-x-2.5">
              <div className="h-9 w-9 rounded-xl bg-[#4262ff] flex items-center justify-center text-white font-bold shadow-sm">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="font-extrabold text-white text-lg tracking-tight">
                CareerLens<span className="text-[#4262ff]">.ai</span>
              </span>
            </div>

            <p className="text-slate-400 max-w-sm leading-relaxed font-normal">
              Intelligent career intelligence and candidate evaluation platform powered by intelligent decision models. Instant candidate resume optimization and enterprise bulk candidate screening.
            </p>

            <div className="flex items-center gap-2 text-[11px] text-slate-400 pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Enterprise Grade Privacy &bull; Zero Data Reselling</span>
            </div>
          </div>

          {/* Column 2: Portals */}
          <div className="space-y-3">
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px]">
              Platform Portals
            </h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <button
                  type="button"
                  onClick={() => onSelectPortal("candidate")}
                  className="hover:text-white transition"
                >
                  Candidate Portal (Resume Scanner)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => onSelectPortal("enterprise")}
                  className="hover:text-white transition"
                >
                  Enterprise Portal (0/15)
                </button>
              </li>
              <li>
                <button
                  type="button"
                  onClick={onOpenQuickApply}
                  className="hover:text-white transition"
                >
                  Job Match Explorer
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: AI Intelligence */}
          <div className="space-y-3">
            <h4 className="font-bold text-white uppercase tracking-wider text-[11px]">
              AI Architecture
            </h4>
            <ul className="space-y-2 text-slate-400">
              <li>
                <span className="hover:text-white transition cursor-default">Deterministic Decision Models</span>
              </li>
              <li>
                <span className="hover:text-white transition cursor-default">Non-Autoregressive Vectors</span>
              </li>
              <li>
                <span className="hover:text-white transition cursor-default">Structured ATS Parser</span>
              </li>
              <li>
                <span className="hover:text-white transition cursor-default">Top Shortlist Ranking</span>
              </li>
              <li>
                <span className="hover:text-white transition cursor-default">SerpApi Live Google Jobs</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Copyright */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <div>
            &copy; {new Date().getFullYear()} CareerLens AI &bull; All rights reserved.
          </div>
          <div className="flex items-center gap-4">
            <span>Deterministic Talent Screening &bull; Non-Autoregressive Intelligence</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
