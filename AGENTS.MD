# AGENTS.MD — CareerLens AI Agent Harness & Quality Contract

> **MANDATORY INSTRUCTION FOR ALL AI CODING AGENTS**:
> Before reading or writing any code in this repository, you **MUST** read this entire document and review the files in the [`context/`](./context/README.md) directory.
> Every modification must respect the architectural invariants, dual-pipeline guarantees, and testing gates detailed herein.

---

## 1. Prime Directive: TypeSafe System One Architecture

CareerLens AI **does NOT** use generative prompt-and-pray LLMs (e.g. asking a model *"Evaluate this resume and return a match score"*). 
All decision-making is grounded in **TypeSafe System One primitives**:

1. **`Choice`**: Categorical selection over explicit candidate mappings.
2. **`Score`**: Ordered rating along fixed numeric scales (e.g. 0 to 6 for Seniority).
3. **`Noul`**: Binary truth judgments (`True` / `False`) for hard eligibility requirements.

```
       Versioned Rubric in Code (`app/jev/rubric.py`)
                             ↓
       Atomic Typed Questions (`Choice`, `Score`, `Noul`)
                             ↓
       Calibrated Probabilities & Continuous Scores
                             ↓
       Deterministic Logic Gates & Hard Veto Aggregation
```

### Invariant Rules
- **NEVER** introduce single-prompt whole-resume generative evaluators.
- **NEVER** embed the rubric inside prompt strings; rubrics belong in versioned Python dictionaries (`RESUME_RUBRIC_V1`).
- **NEVER** allow a candidate who failed a mandatory requirement (`Noul == False`) to pass screening or receive an unvetoed passing score.
- **NEVER** break the dual-pipeline design. Both `typesafe` and `laya_local` must remain fully supported.

---

## 2. Dual-Pipeline Contract

Every screening invocation supports selectable execution via the `pipeline` parameter:

| Pipeline | Identifier | Underlying Engine | Target Environment |
| :--- | :--- | :--- | :--- |
| **Pipeline 1** | `typesafe` | `typesafe_sdk.TypeSafeClient` (`app.jev.client`) | Official TypeSafe SDK, System One cloud API |
| **Pipeline 2** | `laya_local` | `app.laya.client.LayaClient` | Offline, air-gapped on-premise, zero-cost edge inference |

- Both pipelines must accept identical questions and return identical schema models.
- If `typesafe` encounters connection errors, it must fail over cleanly to `laya_local`.

---

## 3. Pre-Change Checklist (Triggered Before Any Modifications)

Before modifying any file in `backend/app/`:

1. **Inspect Context**:
   - Read [`context/ARCHITECTURE.md`](./context/ARCHITECTURE.md) to understand module responsibilities.
   - Read [`context/JEV_PIPELINES.md`](./context/JEV_PIPELINES.md) if modifying pipeline orchestration.
   - Read [`context/PRIMITIVES_AND_RUBRIC.md`](./context/PRIMITIVES_AND_RUBRIC.md) if altering scoring or questions.
2. **Identify Target Subsystem**:
   - `app/parser/`: Spatial column splitting, PDF parsing, text layout.
   - `app/extraction/`: Entity extraction, timeline calculations, JD normalization.
   - `app/jev/`: TypeSafe primitives, LangChain adapter, confidence evaluation, rubric.
   - `app/evaluation/`: Continuous seniority gap $\Delta S$, requirement matching, composite weights.
   - `app/report/`: Response serialization for frontend contracts.
   - `app/services/`: Pipeline orchestrators.
3. **Check Contract Impact**:
   - Ensure `EnterpriseBulkScreenResponse` schema in `app/api/schemas.py` remains 100% backward-compatible with the frontend (`careerlensai-frontend`).

---

## 4. Testing & Verification Harness

All changes must pass the automated test suite before declaring any task complete.

### Running the Test Suite (Dockerized Environment)
Because backend dependencies are containerized, run tests using:

```bash
# 1. Copy latest test suite to container
docker cp backend/tests careerlensai-backend:/tmp/tests

# 2. Execute pytest inside container with PYTHONPATH set
docker exec -e PYTHONPATH=/app careerlensai-backend pytest /tmp/tests -v -o cache_dir=/tmp/.pytest_cache
```

### Running Specific Tests
```bash
# Test TypeSafe architecture and primitives
docker exec -e PYTHONPATH=/app careerlensai-backend pytest /tmp/tests/test_typesafe_architecture.py -v -o cache_dir=/tmp/.pytest_cache

# Test Enterprise bulk screening endpoints
docker exec -e PYTHONPATH=/app careerlensai-backend pytest /tmp/tests/test_enterprise_routes.py -v -o cache_dir=/tmp/.pytest_cache

# Test PDF parsers and spatial layouts
docker exec -e PYTHONPATH=/app careerlensai-backend pytest /tmp/tests/test_deterministic_parser.py -v -o cache_dir=/tmp/.pytest_cache
```

---

## 5. Delivery & Quality Gates

An agent **MAY NOT** consider work complete unless:
1. All automated tests (34+ tests across the test suite) pass with **0 failures**.
2. Both pipelines (`typesafe` and `laya_local`) are verified functional.
3. Logging is present at key decision boundaries (`app.api`, `app.services`, `app.evaluation`, `app.extraction`).
4. No secrets or API credentials are hardcoded into source files.
5. All Pydantic models follow V2 standards (`model_dump()`, typed dict unions).
