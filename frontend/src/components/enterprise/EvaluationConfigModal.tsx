"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Sliders,
  ShieldAlert,
  CheckCircle2,
  Plus,
  Trash2,
  HelpCircle,
  Eye,
  Loader2,
} from "lucide-react";
import { previewJobRequirements } from "@/lib/api";

export interface RequirementConfigItem {
  name: string;
  category: string;
  is_hard_requirement: boolean;
  suggested_gate_question?: string;
  suggested_direct_question?: string;
  suggested_strength_question?: string;
}

interface EvaluationConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobRole: string;
  jobDescription: string;
  pipeline: "typesafe" | "laya_local";
  weights: {
    technical: number;
    experience: number;
    domain: number;
    evidence: number;
    education: number;
  };
  onSaveWeights: (weights: any) => void;
  approvedRequirements: RequirementConfigItem[];
  onSaveRequirements: (reqs: RequirementConfigItem[]) => void;
}

export const EvaluationConfigModal: React.FC<EvaluationConfigModalProps> = ({
  isOpen,
  onClose,
  jobRole,
  jobDescription,
  pipeline,
  weights,
  onSaveWeights,
  approvedRequirements,
  onSaveRequirements,
}) => {
  const [localWeights, setLocalWeights] = useState(weights);
  const [requirements, setRequirements] = useState<RequirementConfigItem[]>(approvedRequirements);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewMeta, setPreviewMeta] = useState<any>(null);
  const [newSkillName, setNewSkillName] = useState("");
  const [activeTab, setActiveTab] = useState<"requirements" | "weights">("requirements");

  useEffect(() => {
    if (isOpen) {
      setLocalWeights(weights);
      if (approvedRequirements.length > 0) {
        setRequirements(approvedRequirements);
      } else {
        fetchPreview();
      }
    }
  }, [isOpen, jobRole, jobDescription]);

  const fetchPreview = async () => {
    if (!jobDescription || jobDescription.length < 20) return;
    setIsLoadingPreview(true);
    try {
      const data = await previewJobRequirements(jobRole, jobDescription, pipeline);
      setPreviewMeta(data);
      if (data.suggested_requirements && data.suggested_requirements.length > 0) {
        setRequirements(data.suggested_requirements);
      }
    } catch (err) {
      console.warn("Could not fetch JD preview:", err);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  if (!isOpen) return null;

  const toggleHardGate = (index: number) => {
    setRequirements((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, is_hard_requirement: !item.is_hard_requirement } : item
      )
    );
  };

  const removeRequirement = (index: number) => {
    setRequirements((prev) => prev.filter((_, i) => i !== index));
  };

  const addCustomRequirement = () => {
    const trimmed = newSkillName.trim();
    if (!trimmed) return;
    if (requirements.some((r) => r.name.toLowerCase() === trimmed.toLowerCase())) return;

    setRequirements((prev) => [
      ...prev,
      {
        name: trimmed,
        category: "Custom",
        is_hard_requirement: false,
        suggested_gate_question: `Does candidate provide verified evidence satisfying '${trimmed}'?`,
        suggested_direct_question: `Is there direct production or practical evidence using '${trimmed}'?`,
        suggested_strength_question: `Rate depth and strength of competency in '${trimmed}' (0-5).`,
      },
    ]);
    setNewSkillName("");
  };

  const handleSave = () => {
    onSaveWeights(localWeights);
    onSaveRequirements(requirements);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-blue-600" />
              Evaluation & Scoring Configuration
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Review and approve the exact evaluation criteria, hard gates, and weights.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex border-b border-slate-200 px-6 gap-6 text-xs font-semibold bg-white">
          <button
            onClick={() => setActiveTab("requirements")}
            className={`py-3 border-b-2 transition-all ${
              activeTab === "requirements"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Evaluated Requirements & Hard Gates ({requirements.length})
          </button>
          <button
            onClick={() => setActiveTab("weights")}
            className={`py-3 border-b-2 transition-all ${
              activeTab === "weights"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Dimension Weights & Rubric
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-5">
          {activeTab === "requirements" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">
                  Select which criteria Jev/Laya evaluates. Check <strong>Hard Gate</strong> for mandatory dealbreakers.
                </span>
                {isLoadingPreview && (
                  <div className="flex items-center gap-1.5 text-xs text-blue-600">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Analyzing JD...</span>
                  </div>
                )}
              </div>

              {/* Requirement Items List */}
              <div className="space-y-2 border border-slate-200 rounded-xl p-3 bg-slate-50/50 max-h-72 overflow-y-auto">
                {requirements.map((item, idx) => (
                  <div
                    key={item.name}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-white border border-slate-200/80 shadow-2xs hover:border-slate-300 transition-all text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-slate-900">{item.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                        {item.category || "Skill"}
                      </span>
                    </div>

                    <div className="flex items-center gap-4">
                      {/* Hard Gate Toggle */}
                      <label className="flex items-center gap-1.5 cursor-pointer select-none">
                        <input
                          type="checkbox"
                          checked={item.is_hard_requirement}
                          onChange={() => toggleHardGate(idx)}
                          className="rounded border-slate-300 text-rose-600 focus:ring-rose-500 h-3.5 w-3.5"
                        />
                        <span
                          className={`text-xs ${
                            item.is_hard_requirement
                              ? "font-bold text-rose-700"
                              : "text-slate-500"
                          }`}
                        >
                          Mandatory Gate
                        </span>
                      </label>

                      {/* Remove Button */}
                      <button
                        onClick={() => removeRequirement(idx)}
                        className="text-slate-400 hover:text-rose-600 transition-colors p-1"
                        title="Remove requirement"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}

                {requirements.length === 0 && !isLoadingPreview && (
                  <div className="text-center py-6 text-xs text-slate-400">
                    No requirements detected yet. Add one below or enter a Job Description.
                  </div>
                )}
              </div>

              {/* Add Custom Requirement Input */}
              <div className="flex gap-2 pt-1">
                <input
                  type="text"
                  placeholder="Add custom requirement (e.g. PyTorch, Microservices, B.Tech)"
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && addCustomRequirement()}
                  className="flex-1 px-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
                <button
                  onClick={addCustomRequirement}
                  className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Add
                </button>
              </div>
            </div>
          )}

          {activeTab === "weights" && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500">
                Adjust the mathematical contribution weights for candidate evaluation (must sum to 100%).
              </div>

              <div className="space-y-3">
                {[
                  { key: "technical", label: "Technical Competencies", desc: "Skills, frameworks, libraries, tools" },
                  { key: "experience", label: "Experience Alignment", desc: "Years, title responsibilities, scope" },
                  { key: "domain", label: "Domain Relevance", desc: "Industry/domain alignment" },
                  { key: "evidence", label: "Evidence Quality", desc: "Verifiable project proof vs keyword fluff" },
                  { key: "education", label: "Education Credentials", desc: "Degree, university accreditation" },
                ].map((dim) => (
                  <div key={dim.key} className="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white">
                    <div>
                      <div className="text-xs font-semibold text-slate-900">{dim.label}</div>
                      <div className="text-[11px] text-slate-500">{dim.desc}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min={0}
                        max={100}
                        step={5}
                        value={localWeights[dim.key as keyof typeof localWeights]}
                        onChange={(e) =>
                          setLocalWeights({
                            ...localWeights,
                            [dim.key]: parseInt(e.target.value) || 0,
                          })
                        }
                        className="w-16 px-2 py-1 text-center font-bold text-xs border border-slate-200 rounded-md focus:outline-none focus:border-blue-500"
                      />
                      <span className="text-xs font-bold text-slate-500">%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-3.5 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
          <button
            onClick={fetchPreview}
            disabled={isLoadingPreview}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1.5"
          >
            {isLoadingPreview ? "Re-analyzing..." : "Re-extract from JD"}
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-5 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-xs transition-colors"
            >
              Save & Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
