# CareerLens AI Backend

FastAPI multi-agent career intelligence backend powered by LangGraph, LangChain, Groq, OpenRouter, and Laya Decision Engine.

## Requirements
- Python 3.13+
- uv package manager

## Local Development
```bash
# Sync dependencies with uv
uv sync

# Run backend service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

