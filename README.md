# CareerLens AI

Enterprise multi-agent resume analysis and job matching platform powered by **FastAPI + LangGraph + Laya Decision Engine** (Backend) and **Next.js + Tailwind CSS** (Frontend).

---

## Architecture Overview

```
                          ┌──────────────────────────┐
                          │   Frontend (Next.js 14)  │
                          │   Port: 3000             │
                          └─────────────┬────────────┘
                                        │ HTTP / REST
                                        ▼
                          ┌──────────────────────────┐
                          │   Backend (FastAPI)      │
                          │   Port: 8000             │
                          └─────────────┬────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   [ LangGraph Engine ]       [ Laya Decision Engine ]   [ SQLite Sessions ]
   • ParserAgent              • Fast Non-Autoregressive  • Session history
   • SkillsAgent                Calibrated Decisions     • Candidate profiles
   • ScoringAgent             • Enterprise Bulk Screener • Audit trail
   • FeedbackAgent
   • JobFetcher (SerpApi)
```

---

## Directory Structure

```
resume-analyser/
├── backend/                         # FastAPI multi-agent backend
│   ├── app/                         # Application package
│   │   ├── agents/                  # Multi-agent implementations
│   │   ├── api/                     # REST API routers & schemas
│   │   ├── core/                    # Settings, loggers, load balancer
│   │   ├── db/                      # SQLAlchemy models & SQLite setup
│   │   ├── graph/                   # LangGraph state machine & workflow
│   │   ├── prompts/                 # Agent YAML prompts
│   │   ├── services/                # Session & business services
│   │   ├── tools/                   # PDF extractor & job search
│   │   └── main.py                  # ASGI FastAPI application
│   ├── data/                        # Persistent SQLite storage
│   ├── .dockerignore                # Backend container exclusions
│   ├── .env.example                 # Backend environment template
│   ├── Dockerfile                   # Multi-stage production build using uv
│   ├── pyproject.toml               # Python package & dependency metadata
│   └── uv.lock                      # Deterministic lockfile
│
├── frontend/                        # Next.js 14 Web Application
│   ├── src/
│   │   ├── app/                     # Next.js App Router (pages & layouts)
│   │   ├── components/              # UI components (Upload, Screener, etc.)
│   │   └── lib/                     # API client & TypeScript interfaces
│   ├── public/                      # Static assets
│   ├── .dockerignore                # Frontend container exclusions
│   ├── .env.example                 # Frontend environment template
│   ├── Dockerfile                   # Multi-stage standalone Next.js build
│   ├── next.config.mjs              # Standalone output configuration
│   └── package.json                 # Node.js dependencies & scripts
│
├── docker-compose.yml               # Unified production orchestration
├── .env.example                     # Root environment template
└── README.md
```

---

## Quick Start with Docker (Recommended)

Both services are fully containerized using **multi-stage builds**, running unprivileged users, and utilizing **`uv`** for reproducible Python dependencies (no `pip install` in containers).

### 1. Configure Environment

Copy the root environment template:
```bash
cp backend/.env.example backend/.env
```
Ensure your API keys (`GROQ_API_KEY`, `OPENROUTER_API_KEY`, `SERPAPI_API_KEY`) are filled in `backend/.env`.

### 2. Build & Launch

```bash
docker compose up --build -d
```

### 3. Access Services

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Stop Services

```bash
docker compose down
```

---

## Local Development (Without Docker)

### Backend (using `uv`)

1. Install [`uv`](https://docs.astral.sh/uv/):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Navigate to `backend/` and sync dependencies:
   ```bash
   cd backend
   uv sync
   ```
3. Configure `backend/.env` from `backend/.env.example`.
4. Run the backend development server:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend

1. Navigate to `frontend/` and install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Configure `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000).

---

## Verification & Health Check

Verify backend health:
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "careerlens-ai",
  "decision_model": "Laya (ConvAI Innovations)"
}
```
