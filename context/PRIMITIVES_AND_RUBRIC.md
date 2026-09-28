# TypeSafe Decision Primitives & Resume Evaluation Rubric

This document defines the mathematical foundations of the TypeSafe System One decision primitives and specifies the versioned rubric (`RESUME_RUBRIC_V1`) used across CareerLens AI.

---

## 1. TypeSafe Decision Primitives

TypeSafe decomposes complex AI behavior into small, typed decisions. Instead of text generation, the model computes categorical distributions over structured spaces.

### 1.1 `Choice` (Categorical Classification)
- **Concept**: Selects exactly one label from a discrete, unordered set of options.
- **Criteria**: A dictionary mapping each valid option string to a precise disambiguation description.
- **Output**:
  - `choice: str` (the selected key)
  - `confidence: float` (probability mass assigned to the winner, $P(\text{winner}) \in [0.0, 1.0]$)
- **Primary Use in CareerLens AI**:
  - Identifying **Role Family** (`software_engineering`, `data_ai`, `devops_cloud`, etc.)
  - Identifying **Domain Focus** (`fintech`, `healthcare`, `ecommerce`, `saas_enterprise`, etc.)
  - Classifying **Education Degree** (`bachelors`, `masters`, `doctorate`, etc.)
  - Classifying **Resume Text Blocks** (`technical`, `experience`, `education`, etc.)

### 1.2 `Score` (Ordered Rating)
- **Concept**: Evaluates candidate evidence along an **ordered scale** with strictly ascending severity or competence.
- **Criteria**: An ordered list of strings describing each level from lowest ($0$) to highest ($N-1$).
- **Output**:
  - `score: int` (zero-based index of the chosen level)
  - `confidence: float` (confidence in the assigned position)
- **Primary Use in CareerLens AI**:
  - **Seniority Assessment** ($0$ = intern, $1$ = junior, $2$ = mid, $3$ = senior, $4$ = lead, $5$ = staff, $6$ = principal)
  - **Evidence Strength** ($0$ = none, $1$ = weak, $2$ = indirect, $3$ = moderate, $4$ = strong, $5$ = very_strong)
  - **Competency Rating** for technical skills.

### 1.3 `Noul` (Binary Truth Judgment)
- **Concept**: Evaluates whether a specific assertion is demonstrably true or false given the evidence.
- **Output**:
  - `noul: bool` (`True` or `False`)
  - `confidence: float` ($P(\text{decision}) \in [0.0, 1.0]$)
- **Primary Use in CareerLens AI**:
  - **Hard Requirement Veto Gates** (e.g., *"Does the candidate hold an active TS/SCI clearance?"* -> `False` triggers immediate disqualification).
  - **Core Eligibility Checks** (e.g., degree requirements, specific required licensing).

---

## 2. Versioned Evaluation Rubric (`RESUME_RUBRIC_V1`)

The rubric exists in code at `app/jev/rubric.py` and is versioned independently of prompts or model weights.

```python
RESUME_RUBRIC_V1 = {
    "version": "1.0",

    # 7-level ordered scale (0 to 6)
    "seniority": {
        "levels": [
            "intern",        # 0: Intern, student, working toward degree
            "junior",        # 1: 0-2 years, entry-level, needs guidance
            "mid",           # 2: 2-5 years, independent execution
            "senior",        # 3: 5-8 years, deep expertise, technical leadership
            "lead",          # 4: 8-12 years, team leadership, architectural authority
            "staff",         # 5: 12-15 years, cross-org impact, strategic direction
            "principal",     # 6: 15+ years, company-wide or industry-level authority
        ],
        "scale": {"min": 0, "max": 6},
    },

    # Section candidates for layout-aware block parsing
    "sections": [
        "technical",
        "experience",
        "domain",
        "education",
        "projects",
        "certifications",
        "other",
    ],

    # 6-level ordered scale for evidence quality
    "evidence_strength": [
        "none",          # 0: No mention in resume
        "weak",          # 1: Listed merely in a keyword list
        "indirect",      # 2: Mentioned in unrelated project or side context
        "moderate",      # 3: Used in commercial work without metrics
        "strong",        # 4: Significant commercial work with concrete impact
        "very_strong",   # 5: Core architectural responsibility with verifiable metrics
    ],

    # 5-level scale for skill relevance
    "skill_relevance": [
        "irrelevant",    # 0: Unrelated to the role
        "related",       # 1: Adjacent domain
        "useful",        # 2: Good to have
        "important",     # 3: Core capability
        "critical",      # 4: Essential foundation
    ],

    # Role taxonomy
    "role_families": [
        "software_engineering",
        "data_ai",
        "devops_cloud",
        "product",
        "design",
        "management",
        "general_tech",
    ],

    # Domain taxonomy
    "domains": [
        "fintech",
        "healthcare",
        "ecommerce",
        "saas_enterprise",
        "cybersecurity",
        "ai_ml",
        "general",
    ],
}
```

---

## 3. Hard Requirement Veto Mechanics

When a JD specifies mandatory qualifications (e.g. `"Must have 5+ years of production Golang"` or `"Active PMP certification required"`):

```
       Candidate Evidence
               │
               ▼
       ┌───────────────┐
       │ Noul Question │
       └───────┬───────┘
               │
       ┌───────┴───────┐
       ▼               ▼
     True            False
       │               │
  Pass Gate       Hard Veto Triggered
                       │
                       ▼
                 - Candidate is flagged: `HARD_REQUIREMENT_FAILED`
                 - Final score capped at 35.0 (Disqualified)
                 - Status marked as `REJECTED` or `NEEDS_REVIEW`
```

