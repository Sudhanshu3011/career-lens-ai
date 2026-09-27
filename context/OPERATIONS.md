# Deployment & Operations Guide

## 🐳 Docker Deployment Architecture

CareerLens AI is packaged as a multi-container Docker Compose application:

- **`backend`**: FastAPI application running on Python 3.13, PyTorch, and Laya Router.
- **`frontend`**: Next.js 14 web application.

```yaml
# docker-compose.yml highlights
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - HF_HOME=/app/data/huggingface
      - HF_TOKEN=${HF_TOKEN}
    volumes:
      - ./backend/app:/app/app:ro
      - backend_data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

---

## ⚡ Concurrency & Resource Tuning

### 1. PyTorch CPU Thread Capping

In containerized environments (such as Docker Desktop on Windows/macOS), PyTorch defaults to spawning threads matching total host CPU logical cores (e.g. 16–32 threads). During batch candidate screening, this causes:

- Massive CPU spikes to 100%.
- Docker Engine thread starvation.
- Uvicorn worker crashes with `unexpected EOF`.

**Mitigation Applied in Code (`app.infrastructure.ml.laya_client`)**:

```python
import torch

if torch.get_num_threads() > 2:
    torch.set_num_threads(2)
if hasattr(torch, "set_num_interop_threads"):
    try:
        torch.set_num_interop_threads(2)
    except RuntimeError:
        pass
```

### 2. Async Semaphore Throttling

In `enterprise_screening_service.py`, concurrent resume evaluations are throttled by `MAX_CONCURRENT_CANDIDATE_EVALUATIONS = 2`:

```python
semaphore = asyncio.Semaphore(MAX_CONCURRENT_CANDIDATE_EVALUATIONS)
```

This guarantees that at most 2 candidates undergo simultaneous forward-pass inference, keeping total CPU usage smoothly below 50%.

### 3. Hugging Face Model Weight Caching

- Model: `convaiinnovations/laya` (~200MB).
- Persistent Cache Directory: `/app/data/huggingface`.
- Bound to named volume `backend_data:/app/data`.
- **Behavior**: Downloaded once on initial container startup; all subsequent runs and restarts load weights instantly from local disk (<1.5s).

---

## 🛠️ Operational Commands

### Start Services

```bash
docker compose up -d
```

### View Live Logs

```bash
docker compose logs -f backend
```

### Restart Backend After Code Changes

```bash
docker compose restart backend
```

### Run Automated Tests Inside Backend Container

```bash
docker compose exec backend pytest tests/
```

### Check Container Health

```bash
curl http://localhost:8000/api/v1/health
```

---

## 🚨 Troubleshooting Common Issues

| Symptom                               | Cause                                                | Solution                                                                                                    |
| ------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `unexpected EOF` / Container restarts | CPU core saturation from PyTorch threads             | Verify `torch.set_num_threads(2)` is active and `Semaphore(2)` is throttling batch calls.                   |
| Model weights re-downloading          | Volume `backend_data` not mounted or `HF_HOME` unset | Ensure `backend_data:/app/data` is declared in `docker-compose.yml`.                                        |
| Uncalibrated temperature warning      | Laya model checkpoint temperature clamping           | Benign warning emitted by `laya/router.py` when temperature is outside `[0.5, 5.0]`. Handled automatically. |
| Corrupt PDF uploads                   | Scanned images or unextractable text                 | Parser automatically falls back to text stream or safe reject record with clear error note.                 |
