from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.errors import http_exception_handler, request_validation_exception_handler
from app.api.routes.imports import router as imports_router

app = FastAPI(
    title="LOOFIO API",
    version="0.1.0",
    description="LOOFIO Hospital MVP API. API contracts are served under /api/v1.",
)

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(imports_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a dependency-free readiness response for local development."""
    return {"status": "ok", "service": "loofio-api"}
