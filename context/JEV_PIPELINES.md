# Dual Pipeline Specification: TypeSafe Python SDK vs Laya Local

CareerLens AI features a dual-engine architecture that cleanly bifurcates execution between the official **TypeSafe Python SDK (`typesafe-sdk`)** and a lightweight, self-contained **Laya Local** router.

---

## 1. Complete Separation of Jev and Laya

Jev and Laya are maintained in **completely separate packages** with zero cross-dependencies:

- **`app/jev/client.py`**: Houses `JevClient` powered by the official `typesafe_sdk.TypeSafeClient`. It calls `client.system_one(state=..., questions=...)` with `Choice`, `Score`, and `Noul`. It does **not** import `laya`.
- **`app/laya/client.py`**: Houses `LayaClient` and directly invokes the local `laya.Router`. It does **not** import `typesafe_sdk`.
- **Shared Calling Convention**: Both clients accept the exact same input signature:
  ```python
  predict(state: Dict[str, Any] | str, questions: Dict[str, Any]) -> Dict[str, Any]
  ```

| Feature | Pipeline 1: `typesafe` (TypeSafe SDK) | Pipeline 2: `laya_local` (Laya) |
| :--- | :--- | :--- |
| **Package** | `app.jev` | `app.laya` |
| **Backend Engine** | `TypeSafeClient` (`typesafe-sdk`) | `LayaClient` / `laya.Router` |
| **Execution Pattern** | `client.system_one(state=..., questions={...})` | Direct router prediction via `laya_client.predict(...)` |
| **Dependency Mode** | Online / `TYPESAFE_API_KEY` / Cloud System One | 100% Offline / Local cached weights / Air-gapped |
| **Response Format** | `response.answers[...]` (`ChoiceAnswer`, `ScoreAnswer`, `NoulAnswer`) | Native dictionary mapping to parsed primitive results |
| **API Parameter** | `pipeline="typesafe"` (Default) | `pipeline="laya_local"` |

---

## 2. Pipeline 1: `typesafe` (Official TypeSafe SDK)

Using the official `typesafe-sdk`:

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

# Initialize client (reads TYPESAFE_API_KEY from environment)
client = TypeSafeClient()

ticket = (
    "Senior Backend Engineer with 7 years of Python, FastAPI, and Kubernetes experience. "
    "Led deployment of distributed payment microservices."
)

response = client.system_one(
    state=ticket,
    questions={
        "is_backend_fit": Noul(
            instructions="Does the candidate have substantial backend microservices experience?",
        ),
        "seniority_level": Score(
            instructions="Assess the candidate's seniority level based on track record.",
            criteria=[
                "Intern / Student",
                "Junior (0-2 years)",
                "Mid-level (2-5 years)",
                "Senior (5-8 years)",
                "Lead / Staff (8-12 years)",
                "Principal (12+ years)",
            ],
        ),
        "primary_stack": Choice(
            instructions="Which stack domain best characterizes this candidate?",
            criteria={
                "backend": "Python, Go, Java, microservices, databases",
                "frontend": "React, TypeScript, CSS, web performance",
                "data_ai": "PyTorch, data pipelines, LLM infrastructure",
            },
        ),
    },
)

# Access typed answers directly
print(response.answers["is_backend_fit"].noul)           # 1.0 (probability of yes)
print(response.answers["seniority_level"].score)        # 3.0 (Score level)
print(response.answers["primary_stack"].choice)         # "backend"
print(response.answers["primary_stack"].confidence)     # e.g. 0.94
```

---

## 3. Pipeline 2: `laya_local` (Laya)

```python
from app.laya.client import laya_client
from typesafe_sdk import Choice, Score, Noul

# Call Laya with the exact same questions and state
state = "Senior Backend Engineer with 7 years of Python, FastAPI, and Kubernetes experience."
questions = {
    "is_backend_fit": Noul(instructions="Does the candidate have substantial backend microservices experience?"),
    "seniority_level": Score(
        instructions="Assess the candidate's seniority level based on track record.",
        criteria=["Intern", "Junior", "Mid", "Senior", "Lead", "Principal"],
    ),
    "primary_stack": Choice(
        instructions="Which stack domain best characterizes this candidate?",
        criteria={"backend": "Python, Go, microservices", "frontend": "React, TypeScript"},
    ),
}

answers = laya_client.predict(state=state, questions=questions)
print(answers["is_backend_fit"]["noul"])
print(answers["seniority_level"]["score"])
print(answers["primary_stack"]["choice"])
```

---

## 4. API Usage & Pipeline Selection

### Via Multipart HTTP Request (`/api/v1/enterprise/bulk-screen`)

```bash
# Using TypeSafe Python SDK (Default)
curl -X POST "http://localhost:8000/api/v1/enterprise/bulk-screen" \
  -F "job_description=$(cat jd.txt)" \
  -F "pipeline=typesafe" \
  -F "resumes=@candidate1.pdf" \
  -F "resumes=@candidate2.pdf"

# Using Laya Local
curl -X POST "http://localhost:8000/api/v1/enterprise/bulk-screen" \
  -F "job_description=$(cat jd.txt)" \
  -F "pipeline=laya_local" \
  -F "resumes=@candidate1.pdf" \
  -F "resumes=@candidate2.pdf"
```
