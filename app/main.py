import os
import socket
import time

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)


APP_NAME = "student-app"

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)

APP_ENVIRONMENT = os.getenv(
    "APP_ENVIRONMENT",
    "dev",
)


# ---------------------------------------------------------
# Prometheus Metrics
# ---------------------------------------------------------

HTTP_REQUESTS = Counter(
    "student_app_http_requests_total",
    "Total number of HTTP requests received",
    [
        "method",
        "path",
        "status_code",
    ],
)


HTTP_REQUEST_DURATION = Histogram(
    "student_app_http_request_duration_seconds",
    "HTTP request duration in seconds",
    [
        "method",
        "path",
    ],
)


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="Student GitOps Application",
    description=(
        "Cloud-native FastAPI application deployed "
        "to Amazon EKS using GitOps."
    ),
    version=APP_VERSION,
)


# ---------------------------------------------------------
# Prometheus Middleware
# ---------------------------------------------------------

@app.middleware("http")
async def prometheus_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    status_code = 500

    try:
        response = await call_next(request)

        status_code = response.status_code

        return response

    finally:
        duration = time.perf_counter() - start_time

        HTTP_REQUESTS.labels(
            method=request.method,
            path=request.url.path,
            status_code=str(status_code),
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)


# ---------------------------------------------------------
# Home Endpoint
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "application": APP_NAME,
        "message": "Student GitOps Application is running",
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "hostname": socket.gethostname(),
    }


# ---------------------------------------------------------
# Liveness Endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }


# ---------------------------------------------------------
# Readiness Endpoint
# ---------------------------------------------------------

@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "application": APP_NAME,
    }


# ---------------------------------------------------------
# Prometheus Metrics Endpoint
# ---------------------------------------------------------

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )