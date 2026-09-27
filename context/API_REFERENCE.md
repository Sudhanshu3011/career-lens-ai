# API Reference & Data Contracts

## 🚀 Base URL

- Local Development: `http://localhost:8000`
- API Prefix: `/api/v1`

---

## 📌 Endpoints

### 1. Enterprise Bulk Screening

- **Endpoint**: `POST /api/v1/enterprise/bulk-screen`
- **Content-Type**: `multipart/form-data`
- **Description**: Concurrently screens and ranks a batch of up to 15 PDF resumes against a target job role and description.

#### Form Parameters:

| Field             | Type               | Required | Description                                  |
| ----------------- | ------------------ | -------- | -------------------------------------------- |
| `job_role`        | `string`           | Yes      | Target job title (e.g. `Senior AI Engineer`) |
| `job_description` | `string`           | Yes      | Complete job description text                |
| `resumes`         | `List[UploadFile]` | Yes      | 1 to 15 PDF resume files                     |

#### Response Schema (`EnterpriseBulkScreenResponse`):

```json
{
  "success": true,
  "job_role": "Senior AI Engineer",
  "seniority_tier": "senior",
  "seniority_label": "Senior / Lead",
  "role_weights": {
    "technical": 0.15,
    "experience": 0.35,
    "domain": 0.25,
    "education": 0.05,
    "evidence": 0.20
  },
  "total_evaluated": 2,
  "top_3_shortlisted": 2,
  "top_5_shortlisted": 2,
  "selected_candidates_count": 1,
  "average_fit_score": 62.5,
  "latency_seconds": 1.45,
  "candidates": [
    {
      "candidate_id": "cand-1",
      "name": "Akshat Surolia",
      "filename": "Akshat_Surolia_Resume.pdf",
      "fit_score": 84.5,
      "raw_score": 8.5,
      "decision": "SELECT",
      "rank": 1,
      "is_top_3": true,
      "is_top_5": true,
      "seniority_tier": "mid_level",
      "seniority_label": "Mid-Level",
      "target_seniority_tier": "senior",
      "target_seniority_label": "Senior / Lead",
      "seniority_alignment": "GAP",
      "high_hits_count": 3,
      "raw_weighted_probability": 0.852,
      "penalty_applied": 0.0,
      "total_weighted_probability": 0.852,
      "breakdown": {
        "technical_requirements": 88,
        "experience_requirements": 78,
        "domain_alignment": 85,
        "education_alignment": 70,
        "evidence_strength": 82
      },
      "skills": ["Python", "PyTorch", "FastAPI", "Docker"],
      "tools": ["Docker", "Git"],
      "domains": ["AI / Machine Learning", "Backend"],
      "decision_reason": "Candidate (Mid-Level) achieved 84.5% match for Senior / Lead requisition. Hit dominant High rating in 3/5 dimensions (No penalty applied). Strong alignment in Python, PyTorch, FastAPI.",
      "technical_overlap": {
        "matched_skills": ["Python", "PyTorch", "FastAPI"],
        "missing_jd_skills": ["Triton"],
        "candidate_bonus_skills": ["OpenCV", "Scikit-Learn"],
        "skill_overlap_percentage": 75.0
      },
      "inspection": {
        "summary": "...",
        "experience": "...",
        "education": "...",
        "skills": "...",
        "contact_info": {
          "email": "example@domain.com",
          "phone": "+1-234-567-8900",
          "links": ["https://linkedin.com/in/..."]
        },
        "laya_telemetry": {
          "prompt_context": "...",
          "questions": { ... },
          "raw_model_answers": { ... },
          "latency_ms": 138.4
        }
      },
      "laya_telemetry": { ... }
    }
  ]
}
```

---

### 2. Export Screening Report

- **Endpoint**: `POST /api/v1/enterprise/export-screening-report`
- **Content-Type**: `application/json`
- **Description**: Generates and downloads a complete CSV evaluation report of a screened batch.

---

### 3. Single Resume Analysis

- **Endpoint**: `POST /api/v1/analyze-resume`
- **Content-Type**: `multipart/form-data`
- **Description**: Deep single-candidate analysis with elevation roadmaps, strengths, and growth recommendations.

---

### 4. Health Check

- **Endpoint**: `GET /api/v1/health`
- **Response**:

```json
{
  "status": "healthy",
  "service": "CareerLens AI API",
  "version": "1.0.0"
}
```
