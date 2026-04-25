"""Error handling middleware."""

from __future__ import annotations

import logging

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.app.common.errors import AuthenticationFailed, JobNotFound, ValidationError
from src.domain.exceptions import InvalidEntity, InvalidJobStateTransition, InvalidTimeout

LOGGER = logging.getLogger(__name__)

_EXCEPTION_TO_STATUS: dict[type[Exception], int] = {
    AuthenticationFailed: 401,
    JobNotFound: 404,
    ValidationError: 400,
    InvalidEntity: 400,
    InvalidTimeout: 400,
    InvalidJobStateTransition: 400,
}


def _status_for(exc: Exception) -> int:
    """Return the configured HTTP status for an exception."""
    for exc_type, status_code in _EXCEPTION_TO_STATUS.items():
        if isinstance(exc, exc_type):
            return status_code
    return 500


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Convert domain and application errors into HTTP responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Wrap request handling with exception translation."""
        try:
            return await call_next(request)
        except Exception as exc:
            status_code = _status_for(exc)
            if status_code < 500:
                return JSONResponse(status_code=status_code, content={"detail": str(exc)})

            request_id = getattr(request.state, "request_id", None) or "-"
            LOGGER.exception("unhandled exception", extra={"request_id": request_id})
            response = JSONResponse(
                status_code=500,
                content={"detail": "internal server error", "request_id": request_id},
            )
            settings = getattr(request.app.state, "settings", None)
            header_name = getattr(settings, "request_id_header_name", "X-Request-Id")
            response.headers[header_name] = request_id
            return response
