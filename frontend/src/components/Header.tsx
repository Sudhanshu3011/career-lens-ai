"use client";

import React, { useState } from "react";
import {
  Bell,
  ChevronDown,
  Check,
  Cpu,
  Layers,
} from "lucide-react";

interface HeaderProps {
  backendStatus?: "online" | "offline" | "checking";
  activeEngine?: "typesafe" | "laya_local";
  onEngineChange?: (engine: "typesafe" | "laya_local") => void;
  activeNav?: string;
  onNavChange?: (tab: string) => void;
  onReset?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  backendStatus = "online",
  activeEngine = "laya_local",
  onEngineChange,
  activeNav = "Candidates",
  onNavChange,
  onReset,
}) => {
  const [engineDropdownOpen, setEngineDropdownOpen] = useState(false);

  const navItems = ["Jobs", "Candidates", "Screening", "Analytics", "Settings"];

  const engineLabel = activeEngine === "typesafe" ? "TypeSafe Jev" : "Laya";

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200/90 h-16 flex items-center px-6 justify-between select-none">
      {/* Left: Brand Logo */}
      <div
        onClick={onReset}
        className="flex items-center gap-3 cursor-pointer group"
        title="Reset & Return to top"
      >
        <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
          <svg
            className="w-5 h-5 text-white"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polygon points="12 2 19 8.5 19 15.5 12 22 5 15.5 5 8.5 12 2" />
            <circle cx="12" cy="12" r="3" fill="currentColor" />
          </svg>
        </div>
        <span className="font-bold text-xl tracking-tight text-slate-900 font-sans">
          CareerLens
        </span>
      </div>

      {/* Center: Navigation Tabs */}
      <nav className="hidden md:flex items-center gap-8 h-full">
        {navItems.map((item) => {
          const isActive = item === activeNav;
          return (
            <button
              key={item}
              onClick={() => onNavChange?.(item)}
              className={`h-full relative text-sm font-medium transition-colors flex items-center px-1 ${
                isActive
                  ? "text-blue-600 font-semibold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {item}
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-[2.5px] bg-blue-600 rounded-t-full" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Right: Engine Status Pill, Bell, Avatar */}
      <div className="flex items-center gap-4">
        {/* Decision Engine Toggle Pill */}
        <div className="relative">
          <button
            onClick={() => setEngineDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-200/90 bg-slate-50 hover:bg-slate-100 text-xs text-slate-700 font-medium transition-all shadow-2xs"
            title="Switch Decision Engine"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            <span>
              Decision Engine: <strong className="font-semibold text-slate-900">{engineLabel}</strong> · Online
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {engineDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-60 rounded-xl bg-white border border-slate-200 shadow-lg py-1.5 z-50 text-xs">
              <div className="px-3 py-1.5 border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                Active Decision Router
              </div>
              <button
                onClick={() => {
                  onEngineChange?.("laya_local");
                  setEngineDropdownOpen(false);
                }}
                className={`w-full px-3 py-2 text-left flex items-center justify-between hover:bg-slate-50 ${
                  activeEngine === "laya_local" ? "text-blue-600 font-semibold bg-blue-50/50" : "text-slate-700"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Cpu className="w-3.5 h-3.5 text-blue-600" />
                  <div>
                    <div>ConvAI Laya Router</div>
                    <div className="text-[10px] text-slate-400 font-normal">Local non-autoregressive</div>
                  </div>
                </div>
                {activeEngine === "laya_local" && <Check className="w-3.5 h-3.5 text-blue-600" />}
              </button>

              <button
                onClick={() => {
                  onEngineChange?.("typesafe");
                  setEngineDropdownOpen(false);
                }}
                className={`w-full px-3 py-2 text-left flex items-center justify-between hover:bg-slate-50 ${
                  activeEngine === "typesafe" ? "text-blue-600 font-semibold bg-blue-50/50" : "text-slate-700"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-indigo-600" />
                  <div>
                    <div>TypeSafe Jev SDK</div>
                    <div className="text-[10px] text-slate-400 font-normal">Official System One primitives</div>
                  </div>
                </div>
                {activeEngine === "typesafe" && <Check className="w-3.5 h-3.5 text-blue-600" />}
              </button>
            </div>
          )}
        </div>

        {/* Notification Bell */}
        <button
          className="relative p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-blue-600" />
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2.5 pl-1 cursor-pointer group">
          <div className="w-8 h-8 rounded-full bg-slate-700 text-white font-medium text-xs flex items-center justify-center">
            SS
          </div>
          <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-600 transition-colors hidden sm:inline-block">
            Sudhanshu
          </span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 hidden sm:inline-block" />
        </div>
      </div>
    </header>
  );
};
