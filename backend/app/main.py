import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.api.session_routes import router as session_router
from app.api.enterprise_routes import router as enterprise_router
from app.db.database import init_db
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    logger.info("Starting CareerLens AI Backend Service (version 1.0.0)...")
    try:
        init_db()
        logger.info("Initialized SQLite database schema successfully.")
    except Exception as exc:
        logger.warning(f"Database initialization error: {exc}")
    yield
    logger.info("CareerLens AI Backend Service shutting down.")


app = FastAPI(
    title="CareerLens AI API",
    description=(
        "Production Resume Analysis and Career Intelligence Engine. "
        "Deterministic parsing, calibrated candidate scoring, gap diagnostics, and market opportunity matching."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_http_requests(request: Request, call_next):
    start_time = time.perf_counter()
    client_ip = request.client.host if request.client else "unknown"
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    # Avoid log clutter on automated Docker healthcheck polling
    if request.url.path != "/api/v1/health":
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms) [client={client_ip}]"
        )
    return response


app.include_router(router, prefix="/api/v1")
app.include_router(session_router, prefix="/api/v1")
app.include_router(enterprise_router, prefix="/api/v1")
