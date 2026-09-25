"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { EnterpriseBulkScreener } from "@/components/enterprise/EnterpriseBulkScreener";
import { checkBackendHealth } from "@/lib/api";
import {
  Sparkles,
  Users,
  Cpu,
  Layers,
  Scale,
  ShieldCheck,
  CheckCircle2,
  TrendingUp,
} from "lucide-react";

export default function EnterpriseDashboard() {
  const [backendStatus, setBackendStatus] = useState<"online" | "offline" | "checking">("checking");
  const [resetKey, setResetKey] = useState<number>(0);

  useEffect(() => {
    checkBackendHealth().then((res) => {
      setBackendStatus(res.status === "healthy" || res.status === "ok" ? "online" : "offline");
    });
  }, []);

  const handleReset = () => {
    setResetKey((prev) => prev + 1);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Header backendStatus={backendStatus} onReset={handleReset} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-10">
        {/* Enterprise Executive Intro */}
        <div className="text-center max-w-3xl mx-auto space-y-3.5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-xs font-bold uppercase tracking-wider shadow-2xs">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Enterprise Talent Pipeline Screener</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-tight">
            High-Speed Candidate Screening Powered by{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-blue-600">
              ConvAI Laya
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-2xl mx-auto">
            Screen up to 20 candidate resumes in parallel. Automatically determine JD seniority,
            dynamically trigger calibrated evaluation weights, and rank talent with mathematical transparency.
          </p>

          {/* 4 Feature Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-left">
            <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                <Cpu className="w-4 h-4 text-indigo-600" />
                <span>Seniority Classifier</span>
              </div>
              <p className="text-[11px] text-slate-500">Junior, Mid-Level, or Senior tier auto-detected from JD</p>
            </div>

            <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                <Scale className="w-4 h-4 text-blue-600" />
                <span>Dynamic Weights</span>
              </div>
              <p className="text-[11px] text-slate-500">Role-specific parameter weights triggered per tier</p>
            </div>

            <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                <Layers className="w-4 h-4 text-purple-600" />
                <span>5-Dimension Matrix</span>
              </div>
              <p className="text-[11px] text-slate-500">Tech, Experience, Domain, Education, and Evidence</p>
            </div>

            <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>High-Hit Penalty</span>
              </div>
              <p className="text-[11px] text-slate-500">Calibrated deduction for low high-match frequency</p>
            </div>
          </div>
        </div>

        {/* Bulk Screener Workspace */}
        <EnterpriseBulkScreener key={resetKey} />
      </main>

      {/* Enterprise Platform Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-slate-800">CareerLens AI</span>
            <span>•</span>
            <span>Enterprise Talent Intelligence Platform</span>
          </div>
          <div className="text-slate-400">
            Powered by ConvAI Innovations Laya • Sub-second deterministic inference
          </div>
        </div>
      </footer>
    </div>
  );
}
