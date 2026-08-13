import json
import logging
import time
import uuid
from datetime import datetime, timezone
from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

HTTP_REQUESTS = Counter("campuspulse_assistant_http_requests_total", "Assistant HTTP requests", ["method", "path", "status"])
HTTP_LATENCY = Histogram("campuspulse_assistant_http_request_duration_seconds", "Assistant HTTP latency", ["method", "path"])
LLM_REQUESTS = Counter("campuspulse_assistant_generation_total", "Assistant generation attempts", ["backend", "outcome"])
LLM_LATENCY = Histogram("campuspulse_assistant_generation_duration_seconds", "Assistant generation latency", ["backend"])
GUARDRAIL_EVENTS = Counter("campuspulse_assistant_guardrail_total", "Assistant guardrail events", ["type"])


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service = service_name
        self.log = logging.getLogger(service_name)

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        route = getattr(request.scope.get("route"), "path", request.url.path)
        HTTP_REQUESTS.labels(request.method, route, str(response.status_code)).inc()
        HTTP_LATENCY.labels(request.method, route).observe(duration)
        response.headers["X-Request-ID"] = rid
        self.log.info(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(), "level": "INFO", "service": self.service,
            "request_id": rid, "method": request.method, "path": request.url.path,
            "status_code": response.status_code, "duration_ms": round(duration * 1000, 2),
        }))
        return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
