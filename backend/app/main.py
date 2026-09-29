import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.router import api_router
from app.core.database import init_db
from app.core.logger import get_logger
from fastapi.openapi.utils import get_openapi

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


@app.get("/", tags=["Root"])
def root():
    """Service status and quick links."""
    return {
        "service": "CareerLens AI API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "frontend": "http://localhost:3000",
    }


app.include_router(api_router, prefix="/api/v1")


def custom_openapi():
    """Ensure Swagger UI renders file upload inputs for OpenAPI 3.1 UploadFile arrays."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    for schema_def in schema.get("components", {}).get("schemas", {}).values():
        for prop_name, prop in schema_def.get("properties", {}).items():
            if prop.get("type") == "array" and "items" in prop:
                if (
                    prop_name == "resumes"
                    or prop["items"].get("contentMediaType")
                    == "application/octet-stream"
                ):
                    prop["items"]["format"] = "binary"
            elif (
                prop.get("contentMediaType") == "application/octet-stream"
                or prop_name == "resume"
            ):
                prop["format"] = "binary"
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
