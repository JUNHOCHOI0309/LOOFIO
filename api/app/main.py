from fastapi import FastAPI

from app.api.routes.imports import router as imports_router

app = FastAPI(
    title="LOOFIO API",
    version="0.1.0",
    description="LOOFIO Hospital MVP API. API contracts are served under /api/v1.",
)

app.include_router(imports_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a dependency-free readiness response for local development."""
    return {"status": "ok", "service": "loofio-api"}
