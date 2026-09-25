"use client";

import React, { useEffect, useState } from "react";
import { X, Download, ExternalLink, FileText, AlertCircle } from "lucide-react";

interface PdfViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: File | null;
  title?: string;
}

export const PdfViewerModal: React.FC<PdfViewerModalProps> = ({
  isOpen,
  onClose,
  file,
  title,
}) => {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!file || !isOpen) {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        setObjectUrl(null);
      }
      return;
    }

    const url = URL.createObjectURL(file);
    setObjectUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file, isOpen]);

  // Handle ESC key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const fileName = file?.name || "Resume.pdf";
  const displayTitle = title || fileName;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/70 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white border border-slate-200 rounded-3xl shadow-2xl w-full max-w-5xl flex flex-col h-[85vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50/80 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-100 text-rose-600">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 truncate max-w-md">
                  {displayTitle}
                </h3>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-semibold">
                  PDF Preview
                </span>
              </div>
              <p className="text-xs text-slate-500 truncate max-w-sm mt-0.5">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : "Document viewer"}
              </p>
            </div>
          </div>

          {/* Action Controls */}
          <div className="flex items-center gap-2">
            {objectUrl && (
              <>
                <a
                  href={objectUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 text-xs font-semibold flex items-center gap-1.5 transition"
                  title="Open in new browser tab"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Open in Tab</span>
                </a>
                <a
                  href={objectUrl}
                  download={fileName}
                  className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-sm transition"
                  title="Download PDF"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Download</span>
                </a>
              </>
            )}
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
              aria-label="Close PDF viewer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body / PDF Frame */}
        <div className="flex-1 bg-slate-100 relative overflow-hidden flex flex-col items-center justify-center">
          {objectUrl ? (
            <object
              data={`${objectUrl}#toolbar=1&navpanes=0`}
              type="application/pdf"
              className="w-full h-full border-0"
              aria-label="PDF Document Preview"
            >
              <iframe
                src={`${objectUrl}#toolbar=1&navpanes=0`}
                className="w-full h-full border-0"
                title="PDF Document Preview"
              >
                <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-3 bg-white">
                  <FileText className="w-12 h-12 text-slate-400" />
                  <p className="text-sm text-slate-700 font-medium">
                    Inline PDF preview is not supported by your browser.
                  </p>
                  <a
                    href={objectUrl}
                    download={fileName}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download {fileName}
                  </a>
                </div>
              </iframe>
            </object>
          ) : (
            <div className="text-center p-8 space-y-3">
              <AlertCircle className="w-10 h-10 text-slate-400 mx-auto" />
              <p className="text-sm font-semibold text-slate-700">
                No PDF document available to preview.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
