# CareerLens AI Architecture & Engineering Context

Welcome to the **CareerLens AI** technical documentation repository. This directory contains the exhaustive architectural blueprints, decision rationales, mathematical formulas, pipeline specifications, and runtime maps for CareerLens AI.

---

## Documentation Index

| Document | Primary Focus | Key Questions Answered |
| :--- | :--- | :--- |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | **Core Architecture & Philosophy** | **HOW**, **WHY**, **WHAT**, **WHEN**, **WHERE** of the entire system |
| **[JEV_PIPELINES.md](./JEV_PIPELINES.md)** | **Dual-Pipeline Execution** | Pipeline 1 (`typesafe_langchain`) vs Pipeline 2 (`laya_local`), switching & contracts |
| **[PRIMITIVES_AND_RUBRIC.md](./PRIMITIVES_AND_RUBRIC.md)** | **TypeSafe Primitives & Rubric** | Mathematical definitions of `Choice`, `Score`, `Noul`, and `RESUME_RUBRIC_V1` |
| **[DATA_FLOW.md](./DATA_FLOW.md)** | **Data Lifecycles & State Transitions** | End-to-end trace from raw PDF bytes to final candidate report |

---

## Quick Orientation: Architectural Tenet

CareerLens AI departs completely from legacy "prompt-and-pray" LLM applications. Instead of supplying an entire resume and job description to an LLM with instructions like `"Score this candidate 0-100"`, CareerLens AI decomposes decision-making into **small, atomic, typed questions** powered by **TypeSafe System One primitives**:

```
                       ┌──────────────────────────────┐
                       │ Versioned Rubric (Code Only) │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  Atomic Typed Questions      │
                       │  (Choice, Score, Noul)       │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  Calibrated Probabilities &  │
                       │  Ordered Continuous Scores   │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │  Deterministic Logic Gates   │
                       │  & Transparent Aggregation   │
                       └──────────────────────────────┘
```

1. **Rubrics live in code**, completely independent of prompt engineering.
2. **Models emit typed probabilities and ordered levels**, not narrative opinions.
3. **Hard requirements act as binary vetoes**, preventing disqualified candidates from slipping through.
4. **All operations support dual execution**:
   - `app/jev/`: TypeSafe Jev client and LangChain adapter.
   - `app/laya/`: Standalone ConvAI Laya System One router.
   Both consume the **exact same question definitions and state**.
5. **No bulky monolithic decision engines**: All logic is bifurcated into modular domain libraries (`app/parser/`, `app/extraction/`, `app/evaluation/`, `app/report/`, `app/services/`).

