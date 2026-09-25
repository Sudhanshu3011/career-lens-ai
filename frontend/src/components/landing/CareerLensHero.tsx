"use client";

import React, { useRef, useState } from "react";
import { LaptopMockup } from "./LaptopMockup";
import {
  FileText,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Users,
  Zap,
  CheckCircle2,
} from "lucide-react";

interface CareerLensHeroProps {
  onFileSelected: (file: File) => void;
  onStartAnalysis: () => void;
  onOpenEnterprise: () => void;
}

export const CareerLensHero: React.FC<CareerLensHeroProps> = ({
  onFileSelected,
  onStartAnalysis,
  onOpenEnterprise,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      onFileSelected(droppedFile);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-[#f8faff] via-white to-white text-[#050038] pt-12 pb-16 px-4 sm:px-6 lg:px-8 text-center border-b border-slate-100">
      {/* Subtle Ambient Background Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[450px] bg-gradient-to-br from-blue-100/50 via-indigo-50/40 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-20 right-10 w-[350px] h-[350px] bg-[#ffd02f]/10 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="relative max-w-5xl mx-auto space-y-7">
        {/* Main H1 Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-[#050038] tracking-tight leading-[1.12] max-w-4xl mx-auto font-sans">
          Deterministic Talent Decisions.{" "}
          <span className="text-[#4262ff] underline decoration-[#ffd02f] decoration-wavy decoration-from-font">
            Zero Hallucinations.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg lg:text-xl text-slate-600 max-w-3xl mx-auto font-normal leading-relaxed">
          Powered by <strong>intelligent decision models</strong>, CareerLens AI grades candidate resumes against calibrated probability vectors in sub-seconds. Designed for both high-ambition job seekers and enterprise hiring teams.
        </p>

        {/* Prominent Upload Dropzone */}
        <div className="max-w-xl mx-auto pt-2">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`cursor-pointer rounded-3xl border-2 border-dashed transition-all duration-200 p-8 sm:p-10 flex flex-col items-center justify-center space-y-3.5 shadow-xl shadow-blue-500/5 bg-white ${
              isDragging
                ? "border-[#4262ff] bg-blue-50/50 scale-[1.02]"
                : "border-slate-300 hover:border-[#4262ff] hover:bg-slate-50/80"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileChange}
            />

            {/* Document Icon */}
            <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200/70 flex items-center justify-center text-[#4262ff] shadow-sm">
              <FileText className="w-8 h-8 text-[#4262ff]" />
            </div>

            <div className="space-y-1 text-center">
              <h3 className="text-base sm:text-lg font-bold text-[#050038] tracking-tight">
                Drop your resume here or click to browse
              </h3>
              <p className="text-xs text-slate-500 font-normal">
                Supported formats: PDF, DOCX (Max 10MB)
              </p>
            </div>

            <div className="flex items-center gap-3 text-xs text-slate-500 pt-1 font-medium">
              <span className="flex items-center gap-1.5 text-emerald-700">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> 100% Private & Confidential
              </span>
              <span>&bull;</span>
              <span className="text-[#4262ff]">Sub-Second Deterministic Evaluation</span>
            </div>
          </div>

          {/* Quick Action Two-Mode Buttons */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3.5">
            <button
              type="button"
              onClick={onStartAnalysis}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-[#4262ff] hover:bg-[#3151eb] text-white font-bold text-xs sm:text-sm tracking-wide shadow-md shadow-blue-500/25 hover:shadow-blue-500/40 transition-all active:scale-98"
            >
              <span>Scan Candidate Resume</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={onOpenEnterprise}
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm tracking-wide shadow-md transition-all active:scale-98"
            >
              <Users className="w-4 h-4 text-emerald-400" />
              <span>Enterprise Bulk Screener</span>
            </button>
          </div>
        </div>

        {/* Laptop Mockup Component */}
        <LaptopMockup />
      </div>
    </section>
  );
};
