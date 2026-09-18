"""FastAPI application factory and global configuration."""

from __future__ import annotations

import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.limiter import limiter

settings = get_settings()

app = FastAPI(
    title="LexAI API",
    description="AI-powered legal document analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    # Security: Only origins listed in settings are allowed. The list is
    # populated from CORS_ORIGINS env var so production deployments can
    # restrict to their specific frontend domain without code changes.
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiter ──────────────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Routers ───────────────────────────────────────────────────────────────────

from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")

# ── Startup event ─────────────────────────────────────────────────────────────


@app.on_event("startup")
async def on_startup() -> None:
    """Create required filesystem directories on application startup.

    Ensures UPLOAD_DIR and CHROMA_DIR exist so the application does not
    crash on first use when running in a fresh environment.
    """
    pathlib.Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)


# ── Health check ──────────────────────────────────────────────────────────────


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return a simple liveness probe response.

    Returns:
        Dictionary with ``status`` and ``service`` keys confirming the
        application is running.
    """
    return {"status": "ok", "service": "LexAI API"}


# ── Static frontend (production single-deploy) ────────────────────────────────

_frontend_dist = pathlib.Path(__file__).parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
