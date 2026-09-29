"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Sliders,
  ShieldAlert,
  ShieldCheck,
  Plus,
  Trash2,
  Lock,
  Save,
  CheckCircle2,
  Layers,
  Sparkles,
} from "lucide-react";
import { EvaluationQuestionItem, JobRequisition } from "@/lib/types";

interface RecruiterQuestionStudioProps {
  isOpen: boolean;
  onClose: () => void;
  requisition: JobRequisition | null;
  onSaveQuestions: (updatedQuestions: Record<string, EvaluationQuestionItem>) => Promise<void>;
  isSaving: boolean;
}

export const RecruiterQuestionStudio: React.FC<RecruiterQuestionStudioProps> = ({
  isOpen,
  onClose,
  requisition,
  onSaveQuestions,
  isSaving,
}) => {
  const [questions, setQuestions] = useState<Record<string, EvaluationQuestionItem>>({});
  const [activeFilter, setActiveFilter] = useState<"all" | "gates" | "scoring">("all");
  const [newQuestionName, setNewQuestionName] = useState("");
  const [newQuestionType, setNewQuestionType] = useState<"noul" | "score" | "choice">("noul");
  const [newQuestionInstructions, setNewQuestionInstructions] = useState("");
  const [newQuestionMandatory, setNewQuestionMandatory] = useState(true);
  const [isAddingNew, setIsAddingNew] = useState(false);

  useEffect(() => {
    if (requisition?.questions) {
      setQuestions(JSON.parse(JSON.stringify(requisition.questions)));
    }
  }, [requisition]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen && !isSaving) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isSaving, onClose]);

  if (!isOpen || !requisition) return null;

  const questionEntries = Object.entries(questions);
  const mandatoryGatesCount = questionEntries.filter(([_, q]) => q.is_mandatory).length;
  const scoringQuestionsCount = questionEntries.filter(([_, q]) => !q.is_mandatory).length;

  const filteredEntries = questionEntries.filter(([_, q]) => {
    if (activeFilter === "gates") return q.is_mandatory;
    if (activeFilter === "scoring") return !q.is_mandatory;
    return true;
  });

  const handleToggleMandatory = (key: string) => {
    setQuestions((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        is_mandatory: !prev[key].is_mandatory,
        primitive: !prev[key].is_mandatory ? "Noul" : "Score",
        type: !prev[key].is_mandatory ? "noul" : "score",
      },
    }));
  };

  const handleUpdateInstruction = (key: string, instructions: string) => {
    setQuestions((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        instructions,
      },
    }));
  };

  const handleDeleteQuestion = (key: string) => {
    setQuestions((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  };

  const handleAddNewQuestion = () => {
    if (!newQuestionName.trim() || !newQuestionInstructions.trim()) return;

    const key = newQuestionName.toLowerCase().replace(/[^a-z0-9_]/g, "_");
    const primitive =
      newQuestionType === "noul" ? "Noul" : newQuestionType === "score" ? "Score" : "Choice";
    const scale =
      newQuestionType === "noul"
        ? "Binary Truth Judgment P(True) in [0.0, 1.0]"
        : newQuestionType === "score"
        ? "Continuous Normalized Rating [0.0, 1.0]"
        : "Categorical Alignment Levels";

    setQuestions((prev) => ({
      ...prev,
      [key]: {
        name: newQuestionName.trim(),
        type: newQuestionType,
        primitive,
        scale,
        instructions: newQuestionInstructions.trim(),
        is_mandatory: newQuestionMandatory,
        category: "Custom Recruiter Criteria",
      },
    }));

    setNewQuestionName("");
    setNewQuestionInstructions("");
    setIsAddingNew(false);
  };

  const handleSaveAndConfirm = async () => {
    await onSaveQuestions(questions);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/70 backdrop-blur-md animate-in fade-in duration-150"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white rounded-2xl border border-slate-200/90 shadow-2xl max-w-4xl w-full flex flex-col max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/75 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-600 text-white flex items-center justify-center shadow-xs">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                Recruiter Criteria & Rubric Studio
                {requisition.is_reviewed && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Locked & Verified
                  </span>
                )}
              </h2>
              <p className="text-[11px] text-slate-500">
                Review, calibrate prompts, and configure mandatory dealbreaker gates
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter bar */}
        <div className="px-6 py-2.5 border-b border-slate-100 bg-white flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-1.5 bg-slate-100 p-0.5 rounded-lg">
            <button
              onClick={() => setActiveFilter("all")}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                activeFilter === "all"
                  ? "bg-white text-slate-900 shadow-2xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              All Criteria ({questionEntries.length})
            </button>
            <button
              onClick={() => setActiveFilter("gates")}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                activeFilter === "gates"
                  ? "bg-white text-rose-700 shadow-2xs"
                  : "text-slate-500 hover:text-rose-700"
              }`}
            >
              <ShieldAlert className="w-3 h-3 text-rose-600" />
              Hard Gates ({mandatoryGatesCount})
            </button>
            <button
              onClick={() => setActiveFilter("scoring")}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                activeFilter === "scoring"
                  ? "bg-white text-indigo-700 shadow-2xs"
                  : "text-slate-500 hover:text-indigo-700"
              }`}
            >
              <Layers className="w-3 h-3 text-indigo-600" />
              Scoring ({scoringQuestionsCount})
            </button>
          </div>

          <button
            type="button"
            onClick={() => setIsAddingNew(!isAddingNew)}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-indigo-200 bg-indigo-50/50 hover:bg-indigo-100/60 text-indigo-700 text-xs font-semibold transition-colors cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Custom Criterion</span>
          </button>
        </div>

        {/* Scrollable Questions List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3.5">
          {/* Add New Question Form */}
          {isAddingNew && (
            <div className="p-4 rounded-xl border-2 border-dashed border-indigo-300 bg-indigo-50/30 space-y-3 animate-in fade-in duration-150">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-900">Define New Evaluation Criterion</span>
                <button
                  type="button"
                  onClick={() => setIsAddingNew(false)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">
                    Criterion Name
                  </label>
                  <input
                    type="text"
                    value={newQuestionName}
                    onChange={(e) => setNewQuestionName(e.target.value)}
                    placeholder="e.g. Active Clinical License"
                    className="w-full px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-900 font-medium"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 mb-1">
                    Evaluation Primitive
                  </label>
                  <select
                    value={newQuestionType}
                    onChange={(e) => setNewQuestionType(e.target.value as any)}
                    className="w-full px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-900 font-medium"
                  >
                    <option value="noul">Noul (Binary Pass/Fail Gate)</option>
                    <option value="score">Score (Continuous Rating 0.0 - 1.0)</option>
                    <option value="choice">Choice (Categorical Fit Levels)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Evaluator Prompt / Instructions
                </label>
                <textarea
                  value={newQuestionInstructions}
                  onChange={(e) => setNewQuestionInstructions(e.target.value)}
                  rows={2}
                  placeholder="Does the candidate have verified work evidence of..."
                  className="w-full px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-900 font-mono text-[11px]"
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700">
                  <input
                    type="checkbox"
                    checked={newQuestionMandatory}
                    onChange={(e) => setNewQuestionMandatory(e.target.checked)}
                    className="rounded text-rose-600 focus:ring-rose-500 w-4 h-4"
                  />
                  <span>Mandatory Hard Gate (Instant Veto / Disqualification)</span>
                </label>

                <button
                  type="button"
                  onClick={handleAddNewQuestion}
                  disabled={!newQuestionName.trim() || !newQuestionInstructions.trim()}
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-all disabled:opacity-50 cursor-pointer"
                >
                  Append Criterion
                </button>
              </div>
            </div>
          )}

          {/* List of Questions */}
          {filteredEntries.map(([key, item]) => {
            const isMandatory = item.is_mandatory;
            const primitiveBadgeClass =
              item.primitive === "Noul"
                ? "bg-purple-50 text-purple-700 border-purple-200"
                : item.primitive === "Score"
                ? "bg-blue-50 text-blue-700 border-blue-200"
                : "bg-emerald-50 text-emerald-700 border-emerald-200";

            return (
              <div
                key={key}
                className={`p-3.5 rounded-xl border transition-all ${
                  isMandatory
                    ? "border-rose-200/90 bg-rose-50/20"
                    : "border-slate-200 hover:border-slate-300 bg-white"
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2.5">
                    {isMandatory ? (
                      <div className="w-7 h-7 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center shrink-0">
                        <ShieldAlert className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
                        <Layers className="w-4 h-4" />
                      </div>
                    )}

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs text-slate-900">
                          {item.name || key}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.2 rounded-full border ${primitiveBadgeClass}`}
                        >
                          {item.primitive || item.type.toUpperCase()}
                        </span>
                        {item.category && (
                          <span className="text-[10px] text-slate-400 font-medium">
                            · {item.category}
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Scale: {item.scale}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Mandatory Switch */}
                    <button
                      type="button"
                      onClick={() => handleToggleMandatory(key)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all cursor-pointer flex items-center gap-1.5 ${
                        isMandatory
                          ? "bg-rose-600 text-white border-rose-600 shadow-xs"
                          : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {isMandatory ? (
                        <>
                          <ShieldAlert className="w-3 h-3" />
                          <span>Dealbreaker Gate</span>
                        </>
                      ) : (
                        <>
                          <ShieldCheck className="w-3 h-3 text-slate-400" />
                          <span>Weighted Score</span>
                        </>
                      )}
                    </button>

                    <button
                      type="button"
                      onClick={() => handleDeleteQuestion(key)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                      title="Remove criterion"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="mt-2">
                  <textarea
                    value={item.instructions}
                    onChange={(e) => handleUpdateInstruction(key, e.target.value)}
                    rows={2}
                    className="w-full px-3 py-1.5 text-xs bg-slate-50/70 border border-slate-200 rounded-lg text-slate-800 font-mono text-[11px] leading-relaxed focus:bg-white focus:outline-hidden focus:border-indigo-500 transition-colors"
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-100 bg-slate-50/75 flex items-center justify-between shrink-0">
          <div className="text-xs text-slate-500 font-medium">
            <strong className="text-rose-700">{mandatoryGatesCount}</strong> dealbreaker gates ·{" "}
            <strong>{scoringQuestionsCount}</strong> continuous criteria
          </div>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={handleSaveAndConfirm}
              disabled={isSaving || questionEntries.length === 0}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition-all disabled:opacity-50 cursor-pointer"
            >
              {isSaving ? (
                <>
                  <Save className="w-3.5 h-3.5 animate-spin" />
                  <span>Locking Criteria...</span>
                </>
              ) : (
                <>
                  <Lock className="w-3.5 h-3.5" />
                  <span>Confirm & Lock Criteria</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
