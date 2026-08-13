from uuid import uuid4

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(
    *,
    code: str,
    message: str,
    request_id: str | None = None,
    details: list[object] | None = None,
    status_code: int,
) -> JSONResponse:
    """Build the stable API v1 error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
                "request_id": request_id or str(uuid4()),
            }
        },
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        code="VALIDATION_ERROR",
        message="요청을 처리할 수 없습니다.",
        request_id=request.headers.get("X-Request-ID"),
        details=exc.errors(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and {"code", "message"}.issubset(detail):
        code = detail["code"]
        message = detail["message"]
        details = detail.get("details", [])
    else:
        code = _code_for_status(exc.status_code)
        message = str(detail)
        details = []
    return error_response(
        code=code,
        message=message,
        request_id=request.headers.get("X-Request-ID"),
        details=details,
        status_code=exc.status_code,
    )


def _code_for_status(status_code: int) -> str:
    return {
        status.HTTP_400_BAD_REQUEST: "VALIDATION_ERROR",
        status.HTTP_401_UNAUTHORIZED: "AUTHENTICATION_REQUIRED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
    }.get(status_code, "INTERNAL_ERROR")
