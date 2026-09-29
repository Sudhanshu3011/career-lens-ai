"use client";

import React from "react";
import {
  UserCheck,
  Briefcase,
  Users,
  FileText,
  SlidersHorizontal,
  Settings,
  HelpCircle,
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
    { name: "Candidate Screening", icon: UserCheck, badge: "Live" },
    { name: "Job Requisitions", icon: Briefcase },
    { name: "Candidates", icon: Users },
    { name: "Evaluation Reports", icon: FileText },
    { name: "Criteria Studio", icon: SlidersHorizontal },
    { name: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-14 sm:w-16 bg-white border-r border-slate-200/80 flex flex-col justify-between py-4 shrink-0 min-h-[calc(100vh-3.5rem)] select-none">
      {/* Top Menu Links */}
      <div className="space-y-1.5 flex flex-col items-center">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.name === activeTab;
          return (
            <button
              key={item.name}
              onClick={() => onSelectTab?.(item.name)}
              className={`w-10 h-10 sm:w-11 sm:h-11 rounded-xl flex items-center justify-center relative transition-all group cursor-pointer ${
                isActive
                  ? "bg-indigo-50 text-indigo-600 shadow-xs font-semibold"
                  : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
              }`}
              title={item.name}
            >
              <Icon className="w-5 h-5" />
              {isActive && (
                <span className="absolute left-0 top-2 bottom-2 w-1 bg-indigo-600 rounded-r-full" />
              )}
              {/* Tooltip on hover */}
              <span className="absolute left-full ml-2.5 px-2 py-1 bg-slate-900 text-white text-[11px] font-medium rounded-md whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-md">
                {item.name}
              </span>
            </button>
          );
        })}
      </div>

      {/* Bottom Help */}
      <div className="flex flex-col items-center">
        <button
          className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          title="Documentation & Guides"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
};
