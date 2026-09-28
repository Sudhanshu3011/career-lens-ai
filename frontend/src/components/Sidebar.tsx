"use client";

import React from "react";
import {
  LayoutDashboard,
  UserCheck,
  Briefcase,
  Users,
  FileText,
  SlidersHorizontal,
  Settings,
  Sparkles,
} from "lucide-react";

interface SidebarProps {
  activeTab?: string;
  onSelectTab?: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab = "Candidate Screening",
  onSelectTab,
}) => {
  const menuItems = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Candidate Screening", icon: UserCheck },
    { name: "Job Requisitions", icon: Briefcase },
    { name: "Candidates", icon: Users },
    { name: "Evaluation Reports", icon: FileText },
    { name: "Templates", icon: SlidersHorizontal },
    { name: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between py-6 shrink-0 min-h-[calc(100vh-4rem)]">
      {/* Top Menu Links */}
      <div className="space-y-1 px-3">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.name === activeTab;
          return (
            <button
              key={item.name}
              onClick={() => onSelectTab?.(item.name)}
              className={`w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? "bg-blue-50 text-blue-600 font-semibold"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <Icon
                className={`w-4 h-4 ${
                  isActive ? "text-blue-600" : "text-slate-400"
                }`}
              />
              <span>{item.name}</span>
            </button>
          );
        })}
      </div>

      {/* Bottom Footer Badge */}
      <div className="px-4 pt-6 border-t border-slate-100">
        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50/80 border border-slate-200/60">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center shrink-0">
            <Sparkles className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="overflow-hidden">
            <h4 className="text-xs font-bold text-slate-900 tracking-tight leading-tight">
              CareerLens AI
            </h4>
            <p className="text-[10px] text-slate-500 font-medium truncate">
              Enterprise Talent Intelligence Platform
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};
