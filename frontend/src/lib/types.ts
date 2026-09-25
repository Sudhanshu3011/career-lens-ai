export interface DecisionBreakdown {
  technical_requirements: number;
  experience_requirements: number;
  domain_alignment: number;
  education_alignment: number;
  evidence_strength: number;
}

export interface ParameterEvaluation {
  p_high: number;
  p_mid: number;
  p_low: number;
  selected_prob: number;
  weight: number;
  weighted_score: number;
  is_high_hit: boolean;
  percentage: number;
}

export interface CandidateInspection {
  summary?: string;
  experience?: string;
  education?: string;
  skills?: string;
  contact_info?: Record<string, any>;
}

export interface EnterpriseCandidate {
  candidate_id: string;
  name: string;
  filename: string;
  rank?: number;
  is_top_3?: boolean;
  is_top_5?: boolean;
  fit_score: number;
  raw_score?: number;
  decision: "SELECT" | "BORDERLINE" | "REJECT" | string;
  seniority_tier?: "beginner" | "mid_level" | "senior" | string;
  seniority_label?: string;
  target_seniority_tier?: string;
  target_seniority_label?: string;
  candidate_seniority_tier?: string;
  candidate_seniority_label?: string;
  seniority_alignment?: "ALIGNED" | "GAP" | "EXCEEDS" | string;
  role_weights?: Record<string, number>;
  high_hits_count?: number;
  raw_weighted_probability?: number;
  penalty_applied?: number;
  total_weighted_probability?: number;
  breakdown: DecisionBreakdown;
  parameter_evaluations?: Record<string, ParameterEvaluation>;
  skills: string[];
  tools: string[];
  domains: string[];
  decision_reason: string;
  technical_overlap?: {
    matched_skills?: string[];
    missing_jd_skills?: string[];
    missing_skills?: string[];
    candidate_bonus_skills?: string[];
    skill_overlap_percentage?: number;
  };
  inspection?: CandidateInspection;
}

export interface EnterpriseScreeningResponse {
  success: boolean;
  job_role: string;
  seniority_tier?: string;
  seniority_label?: string;
  role_weights?: Record<string, number>;
  total_evaluated: number;
  top_3_shortlisted?: number;
  top_5_shortlisted: number;
  selected_candidates_count: number;
  average_fit_score: number;
  latency_seconds: number;
  candidates: EnterpriseCandidate[];
}

export interface SelectionRule {
  rule_name: string;
  dimension: string;
  threshold: number;
  candidate_value: number;
  status: "PASS" | "BORDERLINE" | "FAIL";
  description: string;
  weight: string;
}

export interface RejectionFlag {
  code: string;
  label: string;
  severity: "CRITICAL" | "HIGH" | "MODERATE" | "LOW";
  explanation: string;
}

export interface LayaExplainability {
  decision_model: string;
  formula: string;
  latency_benchmark: string;
  hallucination_rate: string;
  calibration_confidence: string;
}

export interface LayaSelectionMatrix {
  verdict: "SELECTED" | "REVIEW" | "REJECTED";
  verdict_label: string;
  verdict_tone: "positive" | "warning" | "negative";
  summary_rationale: string;
  rules: SelectionRule[];
  rejection_flags: RejectionFlag[];
  explainability: LayaExplainability;
}

export interface LayaDecisionData {
  breakdown: DecisionBreakdown;
  overall_decision: string;
  confidence: number;
  final_score: number;
  selection_matrix: LayaSelectionMatrix;
  source: string;
}

export interface ScoreEvaluation {
  llm_score: number;
  overall_decision: string;
  confidence: number;
  breakdown: DecisionBreakdown;
  missing_skills: string[];
  explanation: string;
  diagnostic_triggered: boolean;
  source: string;
  selection_matrix?: LayaSelectionMatrix;
}

export interface QuickApplyDecision {
  verdict: "Strong Apply" | "Good Match" | "Reach Role" | "Low Fit" | string;
  fit_score: number;
  confidence: number;
  highlights: string[];
}

export type ShouldIApplyDecision = QuickApplyDecision;

export interface RecommendedJob {
  title?: string;
  company?: string;
  location?: string;
  via?: string;
  posted_at?: string;
  link?: string;
  apply_options?: Array<{ title: string; link: string }>;
  thumbnail?: string;
  description?: string;
  quick_apply?: QuickApplyDecision;
  should_i_apply?: QuickApplyDecision;
}

export interface SkillsAnalysis {
  technical_skills: string[];
  tools_and_platforms: string[];
  domains: string[];
  matched_skills?: string[];
  missing_skills?: string[];
}

export interface ParsedWorkExperience {
  company: string;
  role: string;
  duration?: string;
  bullet_points: string[];
}

export interface ParsedEducation {
  institution: string;
  degree: string;
  year?: string;
}

export interface ParsedPersonalInfo {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
}

export interface ParsedSections {
  personal_info?: ParsedPersonalInfo;
  summary?: string;
  work_experience?: ParsedWorkExperience[];
  education?: ParsedEducation[];
  skills?: string[];
  certifications?: string[];
  projects?: Array<{
    title: string;
    description: string;
    technologies?: string[];
  }>;
}

export interface ParsedResume {
  candidate_name?: string;
  summary?: string;
  experience?: string;
  education?: string;
  skills?: string;
  projects?: string;
  certifications?: string;
}

export interface SessionStepData {
  parsed_sections: ParsedSections | null;
  skills_data: SkillsAnalysis | null;
  laya_decision: LayaDecisionData | null;
  feedback_data: {
    feedback: string[];
    diagnostic_reason?: string;
    rejection_flags?: RejectionFlag[];
  } | null;
  jobs_data: RecommendedJob[] | null;
}

export interface SessionDetail {
  session_id: string;
  status: string;
  current_step: number;
  resume_filename: string;
  job_description?: string;
  created_at: string;
  updated_at?: string | null;
  error_message?: string | null;
  steps_data: SessionStepData;
}

export interface SessionSummary {
  session_id: string;
  status: string;
  current_step: number;
  resume_filename: string;
  created_at: string;
  has_decision: boolean;
}

export interface AnalysisData {
  parsed_resume: any;
  skills_analysis: SkillsAnalysis;
  decision_breakdown: DecisionBreakdown;
  scores: ScoreEvaluation;
  feedback: string[];
  recommended_jobs: RecommendedJob[];
  best_job_recommendation?: RecommendedJob | null;
}

export interface ResumeAnalysisResponse {
  success: boolean;
  data: AnalysisData;
}

export interface QuickApplyRequest {
  candidate_skills: {
    technical_skills: string[];
    tools_and_platforms?: string[];
    domains?: string[];
  };
  job_title: string;
  job_company?: string;
  job_location?: string;
  job_description?: string;
}

export type ShouldIApplyRequest = QuickApplyRequest;

export interface QuickApplyResponse {
  success: boolean;
  job_title: string;
  decision: QuickApplyDecision;
}

export type ShouldIApplyResponse = QuickApplyResponse;

export interface CandidateItem {
  id: string;
  name: string;
  title: string;
  skills: string[];
  experience_text: string;
  summary?: string;
}

export interface ScreeningResult {
  candidate_id: string;
  name: string;
  title: string;
  skills: string[];
  summary?: string;
  latency_ms: number;
  decision: LayaDecisionData;
}

export interface BatchScreeningResponse {
  total_screened: number;
  total_latency_ms: number;
  average_latency_ms: number;
  results: ScreeningResult[];
}

