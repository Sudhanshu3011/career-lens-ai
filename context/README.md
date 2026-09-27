# CareerLens AI - System Context & Living Documentation

Welcome to the definitive architecture, design, and operational context documentation for **CareerLens AI**.

CareerLens AI is an enterprise-grade, privacy-first technical candidate screening and resume intelligence platform powered by deterministic parsers and non-autoregressive machine learning decision models ([ConvAI Innovations Laya](https://huggingface.co/convaiinnovations/laya)).

---

## 🧭 Documentation Map (What, How, When, Where, Which)

This directory follows **Living Docs Governance** standards, where every operational, architectural, and mathematical fact has exactly one authoritative owner:

| Document                                   | Core Question             | Focus & Scope                                                                                                                                                                             |
| ------------------------------------------ | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [**ARCHITECTURE.md**](./ARCHITECTURE.md)   | **WHICH** architecture?   | Clean Architecture / DDD layer responsibilities, module boundaries, separation of concerns, and facades.                                                                                  |
| [**PIPELINE.md**](./PIPELINE.md)           | **HOW** does it evaluate? | End-to-end evaluation flow: layout-aware PDF parsing, deterministic skill extraction, ground-truth prompt anchoring, calibrated expected quality scoring math, and transparent telemetry. |
| [**TAXONOMY.md**](./TAXONOMY.md)           | **WHAT** does it know?    | 14 IT engineering domains, 450+ canonical technical skills, symbol-aware boundary matching, and 17 role affinity profiles.                                                                |
| [**API_REFERENCE.md**](./API_REFERENCE.md) | **WHERE** do I call it?   | Complete FastAPI contract: request formats, responses, OpenAPI schemas, error handling, and `laya_telemetry` inspection payloads.                                                         |
| [**OPERATIONS.md**](./OPERATIONS.md)       | **WHEN & HOW** to deploy? | Docker orchestration, PyTorch CPU concurrency limits, Hugging Face weight caching, container health checks, and troubleshooting.                                                          |

---

## 🏛️ Codebase Directory Structure

```text
career-lens-ai/
├── backend/
│   ├── app/
│   │   ├── api/                     # Interface Layer: FastAPI HTTP endpoints & Pydantic V2 DTOs
│   │   │   ├── enterprise_routes.py # Bulk candidate screening & report export
│   │   │   ├── routes.py            # Single resume analysis & feedback
│   │   │   ├── session_routes.py    # Candidate arena showcase & interactive sessions
│   │   │   └── schemas.py           # Shared request & response schemas
│   │   ├── core/                    # Core Infrastructure & Facades
│   │   │   ├── config.py            # Environment configuration & pydantic-settings
│   │   │   ├── decision_engine.py   # Backward-compatibility facade for Laya decision logic
│   │   │   └── logger.py            # Centralized logging configuration
│   │   ├── domain/                  # Domain Layer: Business rules & algorithmic core
│   │   │   ├── scoring/             # Match scoring, calibrated math, and composite evaluation
│   │   │   │   ├── calibrated_scorer.py   # Bias-free expected quality math & penalty logic
│   │   │   │   ├── candidate_evaluator.py # End-to-end multi-dimensional match coordinator
│   │   │   │   └── candidate_scorer.py    # 50/50 composite fit score (Skills + Laya ML)
│   │   │   └── seniority/           # Seniority classification & role weights
│   │   │       └── classifier.py    # JD & candidate seniority classifier with memoization
│   │   ├── infrastructure/          # Infrastructure Layer: External integrations & models
│   │   │   ├── ml/                  # Machine learning models & inference
│   │   │   │   ├── laya_client.py         # Thread-safe Laya Router singleton with thread capping
│   │   │   │   ├── prompt_templates.py    # Ground-truth anchored prompt builders
│   │   │   │   └── heuristic_fallback.py  # Deterministic offline scoring fallback
│   │   │   └── telemetry/           # Observability & inspection pipeline
│   │   │       └── laya_telemetry.py      # Telemetry capture for auditability
│   │   ├── parsers/                 # Parsing Layer: High-speed zero-LLM extractors
│   │   │   ├── resume_parser.py     # Layout-aware PDF & plain-text resume section parser
│   │   │   └── skill_extractor.py   # Symbol-aware 450+ IT skill extractor & role affinities
│   │   ├── services/                # Application Service Layer: Workflow orchestration
│   │   │   ├── enterprise_screening_service.py # Concurrent bulk screening & ranking
│   │   │   ├── screening_service.py # Service alias for bulk screening
│   │   │   ├── analysis_service.py  # Single resume evaluation workflow
│   │   │   └── session_service.py   # Interactive session management
│   │   ├── tools/                   # Backward-compatibility shims for legacy callers
│   │   │   ├── candidate_scorer.py
│   │   │   ├── deterministic_parser.py
│   │   │   ├── tech_keyword_extractor.py
│   │   │   └── pdf_extractor.py
│   │   ├── data/                    # Static taxonomies & skill dictionaries
│   │   │   └── tech_skills_db.py    # 14 domains, 450+ skills, 17 role profiles
│   │   └── main.py                  # FastAPI application entrypoint
│   └── tests/                       # Comprehensive pytest suite
├── frontend/                        # Next.js 14 / React frontend
├── context/                         # Living documentation repository (You are here)
└── docker-compose.yml               # Multi-container orchestration
```
