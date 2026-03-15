"""Request id middleware."""

from __future__ import annotations

import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

LOGGER = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request id to each request."""

    def __init__(self, app: ASGIApp, *, header_name: str = "X-Request-Id") -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Assign a request id and expose it in the response header."""
        request_id = request.headers.get(self._header_name, uuid4().hex)
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self._header_name] = request_id
        LOGGER.info(
            "request completed",
            extra={"request_id": request_id},
        )
        return response
