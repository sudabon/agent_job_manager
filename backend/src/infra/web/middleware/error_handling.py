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
        except AuthenticationFailed as exc:
            return JSONResponse(status_code=401, content={"detail": str(exc)})
        except JobNotFound as exc:
            return JSONResponse(status_code=404, content={"detail": str(exc)})
        except (ValidationError, InvalidEntity, InvalidTimeout, InvalidJobStateTransition) as exc:
            return JSONResponse(status_code=400, content={"detail": str(exc)})
        except Exception as exc:
            request_id = getattr(request.state, "request_id", None)
            LOGGER.exception("unhandled exception", extra={"request_id": request_id})
            return JSONResponse(status_code=500, content={"detail": str(exc)})
