"use client";

import React, { useRef, useState } from "react";
import {
  Upload,
  FileText,
  Database,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Eye,
  Trash2,
  FolderOpen,
  RefreshCw,
} from "lucide-react";
import { ResumeUploadItem } from "@/lib/types";

interface ResumeUploadManagerProps {
  uploadedResumes: ResumeUploadItem[];
  onUploadFiles: (files: File[]) => Promise<void>;
  isUploading: boolean;
  onInspectResume: (resumeId: string) => void;
  onRemoveResume: (resumeId: string) => void;
  onReparseResume?: (resumeId: string) => Promise<void>;
  fileObjectsMap: Map<string, File>;
}

export const ResumeUploadManager: React.FC<ResumeUploadManagerProps> = ({
  uploadedResumes,
  onUploadFiles,
  isUploading,
  onInspectResume,
  onRemoveResume,
  onReparseResume,
  fileObjectsMap,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [reparsingIds, setReparsingIds] = useState<Set<string>>(new Set());


  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const validFiles = Array.from(e.dataTransfer.files).filter((f) =>
        f.name.toLowerCase().endsWith(".pdf")
      );
      if (validFiles.length > 0) {
        onUploadFiles(validFiles);
      }
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const validFiles = Array.from(e.target.files).filter((f) =>
        f.name.toLowerCase().endsWith(".pdf")
      );
      if (validFiles.length > 0) {
        onUploadFiles(validFiles);
      }
    }
  };

  const cachedCount = uploadedResumes.filter((r) => r.status === "cached").length;
  const queuedCount = uploadedResumes.filter((r) => r.status === "queued" || r.status === "parsing").length;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card hover:shadow-card-hover transition-all overflow-hidden flex flex-col">
      {/* Header bar */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Upload className="w-4 h-4 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              2. Candidate Ingestion & Cryptographic Cache
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px]">
          {cachedCount > 0 && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <Database className="w-3 h-3 text-emerald-600" />
              {cachedCount} Cached (0s)
            </span>
          )}
          {queuedCount > 0 && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-semibold bg-amber-50 text-amber-700 border border-amber-200">
              <Clock className="w-3 h-3 text-amber-600 animate-spin" />
              {queuedCount} Queued
            </span>
          )}
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Compact Dropzone Surface */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-4 sm:p-5 text-center cursor-pointer transition-all flex flex-col items-center justify-center ${
            isDragOver
              ? "border-indigo-500 bg-indigo-50/50 shadow-inner"
              : "border-slate-200 hover:border-indigo-400 hover:bg-slate-50/70"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
              <FolderOpen className="w-5 h-5 text-indigo-600" />
            </div>
            <div className="text-left">
              <div className="text-xs font-bold text-slate-800">
                {isUploading ? "Verifying SHA-256 Hashes..." : "Drop Candidate Resumes (PDF)"}
              </div>
              <p className="text-[11px] text-slate-500">
                Instantly matches against database cache (0s latency) · 1 req/min queue on new files
              </p>
            </div>
          </div>
        </div>

        {/* Uploaded Resumes Roster */}
        {uploadedResumes.length > 0 && (
          <div className="border border-slate-200/80 rounded-xl overflow-hidden shadow-2xs">
            <div className="bg-slate-50/90 px-3.5 py-2 border-b border-slate-200 flex items-center justify-between text-[11px] font-bold text-slate-600 uppercase tracking-wider">
              <span>Ingested Resumes ({uploadedResumes.length})</span>
              <span>Status</span>
            </div>

            <div className="divide-y divide-slate-100 max-h-56 overflow-y-auto">
              {uploadedResumes.map((resume) => {
                const isCached = resume.status === "cached";
                const isCompleted = resume.status === "completed";
                const isQueued = resume.status === "queued" || resume.status === "parsing";
                const isFailed = resume.status === "failed";

                return (
                  <div
                    key={resume.resume_id}
                    className="px-3.5 py-2.5 hover:bg-slate-50/60 transition-colors text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5 min-w-0 pr-2">
                        <FileText className={`w-4 h-4 shrink-0 ${isFailed ? "text-rose-500" : "text-slate-400"}`} />
                        <div className="truncate">
                          <div className={`font-semibold truncate ${isFailed ? "text-rose-900" : "text-slate-800"}`}>
                            {resume.filename}
                          </div>
                          <div className="text-[10px] text-slate-400 font-mono">
                            {(resume.file_size_bytes / 1024).toFixed(1)} KB
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {isCached && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            <Database className="w-3 h-3 text-emerald-600" />
                            Cached
                          </span>
                        )}

                        {isCompleted && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                            <CheckCircle2 className="w-3 h-3 text-blue-600" />
                            Parsed
                          </span>
                        )}

                        {isQueued && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                            <Clock className="w-3 h-3 text-amber-600 animate-spin" />
                            {resume.eta_seconds ? `~${resume.eta_seconds}s` : "Parsing"}
                          </span>
                        )}

                        {isFailed && (
                          <span
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200"
                            title={resume.error_message || "Parsing or extraction failed"}
                          >
                            <XCircle className="w-3 h-3 text-rose-600" />
                            Failed
                          </span>
                        )}

                        {isFailed && onReparseResume && (
                          <button
                            type="button"
                            onClick={async () => {
                              setReparsingIds((prev) => new Set(prev).add(resume.resume_id));
                              try {
                                await onReparseResume(resume.resume_id);
                              } finally {
                                setReparsingIds((prev) => {
                                  const next = new Set(prev);
                                  next.delete(resume.resume_id);
                                  return next;
                                });
                              }
                            }}
                            disabled={reparsingIds.has(resume.resume_id)}
                            className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors cursor-pointer disabled:opacity-50"
                            title="Re-parse with high-precision model"
                          >
                            <RefreshCw className={`w-3 h-3 ${reparsingIds.has(resume.resume_id) ? "animate-spin" : ""}`} />
                            Re-parse
                          </button>
                        )}

                        {!isFailed && (
                          <button
                            type="button"
                            onClick={() => onInspectResume(resume.resume_id)}
                            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                            title="Inspect 6 Canonical Sections"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() => onRemoveResume(resume.resume_id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                          title="Remove from queue"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {isFailed && (
                      <div className="mt-2 p-2.5 rounded-lg bg-rose-50/80 border border-rose-200 text-rose-700 text-[11px] flex items-center justify-between gap-2">
                        <div className="flex items-start gap-1.5 min-w-0">
                          <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-semibold">Incomplete or Disrupted Parse: </span>
                            <span>{resume.error_message || "Parsing did not complete successfully. Incomplete data was discarded to ensure accuracy."}</span>
                          </div>
                        </div>
                        {onReparseResume && (
                          <button
                            type="button"
                            onClick={async () => {
                              setReparsingIds((prev) => new Set(prev).add(resume.resume_id));
                              try {
                                await onReparseResume(resume.resume_id);
                              } finally {
                                setReparsingIds((prev) => {
                                  const next = new Set(prev);
                                  next.delete(resume.resume_id);
                                  return next;
                                });
                              }
                            }}
                            disabled={reparsingIds.has(resume.resume_id)}
                            className="shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-rose-600 text-white hover:bg-rose-700 transition-colors cursor-pointer shadow-xs disabled:opacity-50"
                          >
                            <RefreshCw className={`w-3 h-3 ${reparsingIds.has(resume.resume_id) ? "animate-spin" : ""}`} />
                            Parse Again
                          </button>
                        )}
                      </div>
                    )}

                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
