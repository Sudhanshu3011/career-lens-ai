# CareerLens AI System Architecture

This document provides the definitive guide to the **CareerLens AI** architecture, detailing the **WHAT**, **WHY**, **HOW**, **WHEN**, and **WHERE** of the platform.

---

## 1. WHAT: System Overview & Architecture

CareerLens AI is an enterprise resume evaluation and candidate ranking system built on **TypeSafe System One** decision primitives. It eliminates generative hallucination and arbitrary scoring by decomposing candidate evaluation into small, atomic, typed questions.

### High-Level Architectural Diagram

```
                         ┌──────────────────────────┐
                         │       INPUT LAYER        │
                         │                          │
                         │  Job Description (JD)    │
                         │  Resume PDF Multipart    │
                         └────────────┬─────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                │                                           │
                ▼                                           ▼
       ┌─────────────────┐                         ┌─────────────────┐
       │  JD Normalizer  │                         │  Resume Parser  │
       │ Deterministic + │                         │ Deterministic   │
       │ Decision Extract│                         │ PDF / Layout    │
       └────────┬────────┘                         └────────┬────────┘
                │                                           │
                ▼                                           ▼
       ┌─────────────────┐                         ┌────────────────────┐
       │  JobProfile     │                         │ Resume Blocks      │
       │  Representation │                         │ + Candidates       │
       └────────┬────────┘                         └─────────┬──────────┘
                │                                            │
                └──────────────────┬─────────────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │  DECISION ENGINES    │
                         │                      │
                         │  Choice (Category)   │
                         │  Score  (Ordered)    │
                         │  Noul   (Binary)     │
                         │                      │
                         │  [app/jev/] (Jev)    │
                         │  [app/laya/] (Laya)  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ DECISION AGGREGATOR  │
                         │                      │
                         │ Rubric + Weights     │
                         │ Probability / Conf   │
                         │ Hard Veto Gates      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ FINAL RESUME REPORT  │
                         │                      │
                         │ JD Seniority         │
                         │ Resume Seniority     │
                         │ Technical Fit        │
                         │ Experience Fit       │
                         │ Domain Fit           │
                         │ Education Fit        │
                         │ Evidence Quality     │
                         │ Missing Requirements │
                         │ Review Flags         │
                         └──────────────────────┘
```

### Core Abstractions (`app/models/domain/`)

1. **`JobProfile` (`app/models/domain/job.py`)**:
   - Structured representation of JD requirements.
   - Contains: `title`, `role_family`, `seniority_score` (0.0 to 6.0), `seniority_label`, `min_years_experience`, `hard_requirements`, `preferred_skills`, `domains`, `education_level`.
2. **`CandidateProfile` (`app/models/domain/candidate.py`)**:
   - Structured representation of the applicant.
   - Contains: `identity`, `total_years_experience`, `timeline`, `blocks` (`ResumeBlock` with spatial coordinates and section candidate types), `skills_found`.
3. **`Evidence` & `EvidenceAssessment` (`app/models/domain/evidence.py`)**:
   - Concrete text snippets with layout context, confidence, and strength levels (`none`, `weak`, `indirect`, `moderate`, `strong`, `very_strong`).
4. **`DecisionState` & `CompositeScore` (`app/models/domain/decision.py`)**:
   - Aggregated multi-dimensional scores, hard requirement veto status, and telemetry tracking.

---

## 2. WHY: Architectural Rationale

### Why System One Primitives Beat Large Generative Prompts

Traditional LLM resume evaluators submit 10 pages of text into a prompt:

> _"Read this resume and JD. Return a JSON object with match percentage 0-100 and strengths/weaknesses."_

This approach fails in production for four critical reasons:

1. **Uncalibrated Hallucinations**: Generative LLMs hallucinate numbers. A candidate scored at 88% might score 64% on the next token seed.
2. **Lack of Invariant Enforcement**: An LLM cannot guarantee that a candidate missing a strict requirement (e.g., Active Top Secret Clearance or Valid Medical License) is rejected. It averages everything together into a vague score.
3. **Prompt Coupling**: When the rubric is embedded inside a 2,000-word prompt, any modification to a criteria description can trigger unpredictable regression across unrelated evaluations.
4. **Opacity**: You cannot audit _why_ the score was 73%.

### CareerLens AI Solves This With TypeSafe Principles

| Capability               | Generative LLM Approach                      | CareerLens AI TypeSafe Approach                                                         |
| :----------------------- | :------------------------------------------- | :-------------------------------------------------------------------------------------- |
| **Rubric Storage**       | Embedded inside large prompt strings         | Versioned in Python code (`RESUME_RUBRIC_V1`), zero prompt coupling                     |
| **Seniority Evaluation** | Guessed as string ("Senior")                 | Ordered 7-level continuous score `[0.0, 6.0]` with explicit distance $\Delta S$         |
| **Hard Requirements**    | Mixed into average score                     | Binary `Noul` questions acting as deterministic vetoes                                  |
| **Model Nature**         | Autoregressive text generation               | Direct distribution over discrete outcomes (Non-autoregressive / Calibrated classifier) |
| **Auditability**         | Prose explanation (post-hoc rationalization) | Exact probability distribution, raw evidence snippets, and sub-score breakdown          |

---

## 3. HOW: Engineering Mechanisms

### 3.1 PDF Layout & Block Parsing (`app/parser/`)

- Uses `pdfplumber` for spatial character extraction.
- **Column Detection**: Analyzes horizontal word distributions to detect multi-column layouts and prevents text from adjacent columns from bleeding together.
- **Block Building**: Segments text into semantic blocks (`ResumeBlock`), assigning candidate classifications (`technical`, `experience`, `education`, `projects`, etc.) before question evaluation.

### 3.2 Stage 1: JD Structured Extraction (`app/extraction/jd_extractor.py`)

Executes parallel atomic questions:

1. `role_family`: **Choice** over `software_engineering`, `data_ai`, `devops_cloud`, `product`, `design`, `management`, `general_tech`.
2. `seniority_score`: **Score** over 7 ordered levels (`intern`, `junior`, `mid`, `senior`, `lead`, `staff`, `principal`).
3. `education_level`: **Choice** over `high_school`, `associates`, `bachelors`, `masters`, `doctorate`, `unspecified`.
4. `domain_focus`: **Choice** over `fintech`, `healthcare`, `ecommerce`, `saas_enterprise`, `cybersecurity`, `ai_ml`, `general`.

### 3.3 Stage 2: Candidate Seniority Analysis (`app/evaluation/seniority_evaluator.py`)

The applicant's seniority is evaluated on the exact same 7-level ordered scale `[0, 6]` as the JD:
$$\Delta S = S_{\text{resume}} - S_{\text{JD}}$$

- If $\Delta S = 0$: Perfect alignment ($100\%$ fit).
- If $\Delta S > 0$: Candidate exceeds seniority requirement (minor soft penalty if overqualified, or capped at 100%).
- If $\Delta S < 0$: Candidate lacks seniority. Penalty scaled quadratically:
  $$\text{Penalty} = \min(1.0, (|\Delta S| / 2.5)^{1.5})$$
  $$\text{SeniorityFit} = \max(0.0, 1.0 - \text{Penalty}) \times 100$$

### 3.4 Stage 3: Requirement Vetting & Evidence Slicing (`app/evaluation/requirement_matcher.py`)

For each requirement in the JD:

1. Deterministic text matchers and semantic search slice relevant `Evidence` blocks from the resume.
2. If `requirement.is_mandatory = True`:
   - Evaluated via **Noul** (`is_met`).
   - If `noul == False` with high confidence, `HardRequirementGate.is_passed = False`, triggering an **immediate veto**.
3. Competency / skill level is evaluated via **Score** (`none`, `weak`, `indirect`, `moderate`, `strong`, `very_strong`).

### 3.5 Stage 4: Transparent Composite Scoring (`app/evaluation/composite_score.py`)

Final candidate fit is computed by a weighted deterministic formula:
$$\text{RawScore} = 0.25 \times \text{Tech} + 0.20 \times \text{Seniority} + 0.20 \times \text{Exp} + 0.15 \times \text{Domain} + 0.15 \times \text{Reqs} + 0.05 \times \text{Edu}$$

**The Hard Veto Override:**

```python
if hard_requirements_veto:
    final_score = min(raw_score, 35.0)  # Capped below passing threshold
    review_flags.append("HARD_REQUIREMENT_FAILED")
```

### 3.6 Complete Separation of Jev and Laya

- **`app/jev/client.py`**: Pure TypeSafe Jev System One Client. Zero dependencies on Laya.
- **`app/laya/client.py`**: Pure ConvAI Laya System One Router. Zero dependencies on Jev.
- Both clients implement the identical API:
  `predict(state: Dict[str, Any] | str, questions: Dict[str, Any]) -> Dict[str, Any]`
  allowing callers to supply the exact same state and questions.

---

## 4. WHEN: Pipeline Selection & Runtime Modes

CareerLens AI provides **two distinct pipelines** selectable on every evaluation:

### 1. `typesafe` (Default Enterprise Mode)

- **Engine**: Official TypeSafe Python SDK (`typesafe_sdk.TypeSafeClient`).
- **Use Case**: Cloud-native production deployments with `TYPESAFE_API_KEY` configured, calling Jev System One models.
- **How to invoke**:

  ```python
  from app.services.typesafe_pipeline import evaluate_candidate_typesafe

  record = evaluate_candidate_typesafe(pdf_bytes, filename, job_profile, idx, pipeline_mode="typesafe")
  ```

### 2. `laya_local` (Edge / Air-Gapped Mode)

- **Engine**: Direct embedded non-autoregressive Laya router (`app.laya.client.LayaClient`).
- **Use Case**: Completely air-gapped environments, on-premise hardware without internet, or local zero-cost inference using cached model weights (`Laya/Laya-8B` or fallback classifier).
- **How to invoke**:
  ```python
  record = evaluate_candidate_typesafe(pdf_bytes, filename, job_profile, idx, pipeline_mode="laya_local")
  ```

---

### 5. WHERE: Component & Directory Blueprint

```
backend/
├── app/
│   ├── api/                      # Versioned HTTP Endpoints & Routers
│   │   ├── dependencies.py       # API dependency injection (get_db, etc.)
│   │   └── v1/
│   │       ├── router.py         # Unified v1 APIRouter
│   │       └── endpoints/
│   │           ├── enterprise.py # Bulk resume upload & screening API
│   │           ├── sessions.py   # Multi-step session & arena screening API
│   │           └── analysis.py   # Health and single-resume deterministic analysis
│   ├── core/                     # Foundational Infrastructure & Settings
│   │   ├── config.py             # App settings (Pydantic V2)
│   │   ├── database.py           # Engine, connection pooling, & sessionmaker
│   │   ├── logger.py             # Structured logging setup
│   │   └── validators.py         # PDF magic bytes, MIME, & size validator
│   ├── models/                   # Explicit DB vs Domain Separation
│   │   ├── db/
│   │   │   └── session.py        # AnalysisSession SQLAlchemy ORM entity
│   │   └── domain/
│   │       ├── candidate.py      # Candidate profile & ResumeBlock models
│   │       ├── decision.py       # Hard gates, assessments & scores
│   │       ├── evidence.py       # Evidence snippets & assessments
│   │       └── job.py            # Structured JobProfile & requirements
│   ├── schemas/                  # Decoupled Pydantic V2 DTO Schemas
│   │   ├── enterprise.py         # Enterprise bulk screening DTOs
│   │   ├── session.py            # Step-by-step sessions DTOs
│   │   └── analysis.py           # Resume analysis DTOs
│   ├── repositories/             # Persistence & Data Access Layer
│   │   └── session_repository.py # Repository pattern for session persistence
│   ├── services/                 # Business Orchestration Services
│   │   ├── analysis_service.py   # Single-resume analysis orchestrator
│   │   ├── enterprise_service.py # Batch candidate screening orchestrator
│   │   ├── session_service.py    # Multi-step session coordinator
│   │   └── typesafe_pipeline.py  # Dual-pipeline coordinator
│   ├── engines/                  # Computational & Deterministic Engines
│   │   ├── parser/               # Spatial PDF parsing & layout extraction
│   │   │   ├── pdf_parser.py
│   │   │   ├── layout_analyzer.py
│   │   │   └── block_builder.py
│   │   ├── extraction/           # Keyword ontology & JD entity extraction
│   │   │   ├── tech_keywords.py
│   │   │   ├── jd_extractor.py
│   │   │   ├── entity_extractor.py
│   │   │   └── evidence_builder.py
│   │   ├── jev/                  # Pure TypeSafe Jev System One Client & Rubric
│   │   │   ├── client.py
│   │   │   ├── questions.py
│   │   │   ├── confidence.py
│   │   │   └── rubric.py
│   │   ├── laya/                 # ConvAI Local Laya Client
│   │   │   └── client.py
│   │   └── evaluation/           # Pure continuous scoring & logic gates
│   │       ├── seniority_evaluator.py
│   │       ├── requirement_matcher.py
│   │       ├── candidate_scorer.py
│   │       └── composite_score.py
│   ├── utils/                    # Shared Utilities & Serializers
│   │   └── report_builder.py     # Schema serializer for frontend UI
│   └── main.py                   # Application entrypoint & lifespan
├── tests/                        # Automated Pytest Suite (47 tests)
└── pyproject.toml                # Dependencies & package configuration
```
