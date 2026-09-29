"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  Check,
  Cpu,
  Layers,
  Sparkles,
  ShieldCheck,
  Activity,
} from "lucide-react";

interface HeaderProps {
  backendStatus?: "online" | "offline" | "checking";
  activeEngine?: "typesafe" | "laya_local";
  onEngineChange?: (engine: "typesafe" | "laya_local") => void;
  onReset?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  backendStatus = "online",
  activeEngine = "laya_local",
  onEngineChange,
  onReset,
}) => {
  const [engineDropdownOpen, setEngineDropdownOpen] = useState(false);

  const engineLabel = activeEngine === "typesafe" ? "TypeSafe Jev SDK" : "ConvAI Laya Router";
  const engineShort = activeEngine === "typesafe" ? "Jev" : "Laya";

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80 h-14 flex items-center px-6 justify-between select-none shadow-xs">
      {/* Left: Brand Identity & Product Tag */}
      <div className="flex items-center gap-4">
        <div
          onClick={onReset}
          className="flex items-center gap-2.5 cursor-pointer group"
          title="Reset Workspace"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-600 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform text-white font-bold">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-slate-900 font-sans">
                CareerLens
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200/80 uppercase tracking-wider">
                Enterprise AI
              </span>
            </div>
          </div>
        </div>

        {/* Breadcrumb Context */}
        <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-200 text-xs text-slate-500">
          <span>Recruitment Suite</span>
          <span className="text-slate-300">/</span>
          <span className="font-semibold text-slate-800">Universal Talent Screener</span>
        </div>
      </div>

      {/* Right: Engine Switcher, Health & Profile */}
      <div className="flex items-center gap-3">
        {/* Backend Health Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-50 border border-slate-200 text-slate-600">
          <span
            className={`w-2 h-2 rounded-full ${
              backendStatus === "online" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
            }`}
          />
          <span>{backendStatus === "online" ? "API Live" : "API Offline"}</span>
        </div>

        {/* Decision Engine Dropdown */}
        <div className="relative">
          <button
            onClick={() => setEngineDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 text-xs text-slate-800 font-semibold transition-all shadow-xs cursor-pointer"
            title="Switch Decision Engine"
          >
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            <span>
              Engine: <strong className="text-indigo-600">{engineShort}</strong>
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {engineDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-64 rounded-xl bg-white border border-slate-200 shadow-xl py-1.5 z-50 text-xs animate-in fade-in slide-in-from-top-1 duration-150">
              <div className="px-3 py-1.5 border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                Active Inference Router
              </div>
              <button
                onClick={() => {
                  onEngineChange?.("laya_local");
                  setEngineDropdownOpen(false);
                }}
                className={`w-full px-3 py-2 text-left flex items-center justify-between hover:bg-slate-50 transition-colors ${
                  activeEngine === "laya_local"
                    ? "text-indigo-600 font-bold bg-indigo-50/50"
                    : "text-slate-700"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[10px]">
                    L
                  </div>
                  <div>
                    <div className="font-semibold text-slate-900">ConvAI Laya Router</div>
                    <div className="text-[10px] text-slate-400 font-normal">
                      Local non-autoregressive weights
                    </div>
                  </div>
                </div>
                {activeEngine === "laya_local" && <Check className="w-3.5 h-3.5 text-indigo-600" />}
              </button>

              <button
                onClick={() => {
                  onEngineChange?.("typesafe");
                  setEngineDropdownOpen(false);
                }}
                className={`w-full px-3 py-2 text-left flex items-center justify-between hover:bg-slate-50 transition-colors ${
                  activeEngine === "typesafe"
                    ? "text-indigo-600 font-bold bg-indigo-50/50"
                    : "text-slate-700"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-6 h-6 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-[10px]">
                    J
                  </div>
                  <div>
                    <div className="font-semibold text-slate-900">TypeSafe Jev SDK</div>
                    <div className="text-[10px] text-slate-400 font-normal">
                      System One continuous primitives
                    </div>
                  </div>
                </div>
                {activeEngine === "typesafe" && <Check className="w-3.5 h-3.5 text-indigo-600" />}
              </button>
            </div>
          )}
        </div>

        {/* User Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-7 h-7 rounded-lg bg-slate-900 text-white font-bold text-xs flex items-center justify-center shadow-xs">
            SS
          </div>
          <span className="text-xs font-semibold text-slate-700 hidden sm:inline-block">
            Recruiter
          </span>
        </div>
      </div>
    </header>
  );
};
