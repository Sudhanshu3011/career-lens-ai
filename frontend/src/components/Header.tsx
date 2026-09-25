"use client";

import React from "react";
import {
  Sparkles,
  Users,
  Cpu,
  Layers,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
} from "lucide-react";

interface HeaderProps {
  backendStatus?: "online" | "offline" | "checking";
  onReset?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  backendStatus = "online",
  onReset,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-2xs transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        {/* Brand Logo & Recruiter Platform Name */}
        <div
          className="flex items-center space-x-3 cursor-pointer select-none group"
          onClick={() => {
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
          title="CareerLens Enterprise"
        >
          <div className="h-10 w-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/25 group-hover:scale-105 transition-all">
            <Users className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-slate-900 text-lg sm:text-xl tracking-tight font-sans">
                CareerLens
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200">
                Enterprise
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Calibrated Bulk Resume Screener
            </p>
          </div>
        </div>

        {/* Center Features / Pipeline Attributes */}
        <div className="hidden md:flex items-center gap-4 text-xs font-semibold text-slate-600">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            <span>ConvAI Laya Router</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <Layers className="w-3.5 h-3.5 text-blue-600" />
            <span>5-Parameter Weighted Matrix</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>Seniority Calibration</span>
          </div>
        </div>

        {/* Right Status & Quick Actions */}
        <div className="flex items-center gap-3">
          {/* Laya Engine Status */}
          <div
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${
              backendStatus === "online"
                ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                : backendStatus === "checking"
                ? "bg-amber-50 text-amber-800 border-amber-200"
                : "bg-rose-50 text-rose-800 border-rose-200"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online"
                  ? "bg-emerald-500 animate-pulse"
                  : backendStatus === "checking"
                  ? "bg-amber-500 animate-pulse"
                  : "bg-rose-500"
              }`}
            />
            <span className="capitalize">{backendStatus === "online" ? "Laya Online" : backendStatus}</span>
          </div>

          {/* New Screening Session CTA */}
          {onReset && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-100 text-xs font-bold text-slate-700 transition active:scale-98"
              title="Reset screening form"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
