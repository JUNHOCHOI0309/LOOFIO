import os
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware

from app.api.errors import http_exception_handler, request_validation_exception_handler
from app.api.routes.auth import router as auth_router
from app.api.routes.actions import router as actions_router
from app.api.routes.businesses import router as businesses_router
from app.api.routes.cause_analyses import router as cause_analyses_router
from app.api.routes.detectors import router as detectors_router
from app.api.routes.imports import router as imports_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.results import router as results_router
from app.auth.store import PostgresAuthStore
from app.actions.store import PostgresActionStore
from app.imports.store import PostgresAppointmentImportStore
from app.metrics.store import PostgresAppointmentMetricStore
from app.opportunities.store import PostgresOpportunityStore
from app.recommendations.store import PostgresRecommendationStore
from app.results.store import PostgresResultStore

app = FastAPI(
    title="LOOFIO API",
    version="0.1.0",
    description="LOOFIO Hospital MVP API. API contracts are served under /api/v1.",
)
app.state.auth_store = PostgresAuthStore(os.getenv("DATABASE_URL"))
app.state.import_store = PostgresAppointmentImportStore(os.getenv("DATABASE_URL"))
app.state.metric_store = PostgresAppointmentMetricStore(os.getenv("DATABASE_URL"))
app.state.opportunity_store = PostgresOpportunityStore(os.getenv("DATABASE_URL"))
app.state.recommendation_store = PostgresRecommendationStore(os.getenv("DATABASE_URL"))
app.state.action_store = PostgresActionStore(os.getenv("DATABASE_URL"))
app.state.result_store = PostgresResultStore(os.getenv("DATABASE_URL"))

configured_session_secret = os.getenv("SESSION_SECRET")
secure_session_cookie = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
app.add_middleware(
    SessionMiddleware,
    secret_key=configured_session_secret or secrets.token_urlsafe(32),
    https_only=secure_session_cookie,
    same_site="lax",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("APP_ORIGIN", "http://localhost:3000")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key", "X-Request-ID"],
    allow_credentials=True,
)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(actions_router, prefix="/api/v1")
app.include_router(businesses_router, prefix="/api/v1")
app.include_router(cause_analyses_router, prefix="/api/v1")
app.include_router(detectors_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(opportunities_router, prefix="/api/v1")
app.include_router(results_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a dependency-free readiness response for local development."""
    return {"status": "ok", "service": "loofio-api"}
