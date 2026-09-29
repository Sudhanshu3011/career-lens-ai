/**
 * CareerLens AI - Enterprise Recruitment & Speculative Evaluation Types
 * Type definitions matching the canonical FastAPI backend contracts.
 */

export interface EvaluationQuestionItem {
  name: string;
  type: "choice" | "score" | "noul";
  primitive: "Choice" | "Score" | "Noul";
  scale: string;
  instructions: string;
  is_mandatory: boolean;
  category?: string;
}

export interface JobRequisition {
  job_id: string;
  role_title: string;
  jd_hash: string;
  is_reviewed: boolean;
  blueprint: Record<string, any>;
  questions: Record<string, EvaluationQuestionItem>;
  cached?: boolean;
  message?: string;
  created_at?: string;
  updated_at?: string;
}

export type JobAnalyzeResponse = JobRequisition;

export interface JobQuestionsUpdateResponse {
  job_id: string;
  is_reviewed: boolean;
  total_questions: number;
  mandatory_gates_count: number;
  questions: Record<string, EvaluationQuestionItem>;
}

export interface WorkExperienceItem {
  employer: string;
  role_title: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  responsibilities_and_achievements: string[];
  tools_and_methods: string[];
}

export interface EducationItem {
  institution: string;
  degree_name: string;
  field_of_study?: string;
  graduation_year?: number;
}

export interface ProjectItem {
  title: string;
  description?: string;
  technologies: string[];
  responsibilities_and_outcomes: string[];
  link?: string;
}

export interface ResumeParsedSections {
  candidate_name: string;
  email?: string;
  phone?: string;
  location?: string;
  portfolio_links: string[];
  professional_summary: string;
  work_experience: WorkExperienceItem[];
  projects?: ProjectItem[];
  core_competencies: string[];
  competencies_by_category?: Record<string, string[]>;
  education: EducationItem[];
  certifications_and_licenses: string[];
  raw_text?: string;
}

export interface ResumeUploadItem {
  resume_id: string;
  filename: string;
  file_hash: string;
  file_size_bytes: number;
  status: "cached" | "queued" | "parsing" | "completed" | "failed";
  eta_seconds?: number;
  message?: string;
  error_message?: string;
}

export interface ResumeUploadBatchResponse {
  total_uploaded: number;
  cached_count: number;
  queued_count: number;
  resumes: ResumeUploadItem[];
}

export interface ResumeDetailResponse {
  resume_id: string;
  filename: string;
  file_hash: string;
  file_size_bytes: number;
  status: string;
  parsed_sections?: ResumeParsedSections;
  raw_text?: string;
  portfolio_links: string[];
  error_message?: string;
}

export interface CandidateEvaluationItem {
  evaluation_id: string;
  job_id: string;
  resume_id: string;
  candidate_name: string;
  pipeline: string;
  fit_score: number;
  verdict: "ADVANCE" | "HOLD" | "REJECT" | string;
  status: string;
  breakdown: {
    competency_depth?: number;
    seniority_fit?: number;
    experience_duration?: number;
    domain_alignment?: number;
    evidence_quality?: number;
    education_credentials?: number;
    raw_weighted_total?: number;
    [key: string]: number | undefined;
  };
  portfolio_links?: string[];
  projects?: ProjectItem[];
  error_message?: string;
  // UI client augmentations
  pdfBlobUrl?: string;
  parsedSections?: ResumeParsedSections;
}

export interface JobEvaluationSummaryResponse {
  job_id: string;
  total_evaluated: number;
  top_candidates: CandidateEvaluationItem[];
  evaluations: CandidateEvaluationItem[];
}
