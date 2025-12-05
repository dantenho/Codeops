"""
Prometheus Metrics Exporter.

This module exports metrics for monitoring
the content generation pipeline.
"""

import time
from functools import wraps

from prometheus_client import (
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    start_http_server,
)

# Define metrics
GENERATIONS_TOTAL = Counter(
    "content_farm_generations_total",
    "Total number of image generations",
    ["status", "node"]
)

GENERATION_DURATION = Histogram(
    "content_farm_generation_duration_seconds",
    "Time spent generating images",
    ["node"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

ACTIVE_WORKFLOWS = Gauge(
    "content_farm_active_workflows",
    "Number of currently active workflows"
)

GPU_UTILIZATION = Gauge(
    "content_farm_gpu_utilization_percent",
    "GPU utilization percentage"
)

GPU_MEMORY_USED = Gauge(
    "content_farm_gpu_memory_bytes",
    "GPU memory usage in bytes"
)

VECTOR_STORE_DOCUMENTS = Gauge(
    "content_farm_vectorstore_documents",
    "Number of documents in vector store"
)

CELERY_TASKS_QUEUED = Gauge(
    "content_farm_celery_tasks_queued",
    "Number of tasks in Celery queue"
)

CELERY_TASKS_ACTIVE = Gauge(
    "content_farm_celery_tasks_active",
    "Number of active Celery tasks"
)

API_REQUESTS = Counter(
    "content_farm_api_requests_total",
    "Total API requests",
    ["endpoint", "method", "status"]
)

API_LATENCY = Summary(
    "content_farm_api_latency_seconds",
    "API request latency",
    ["endpoint"]
)


def track_generation(node_name: str):
    """Decorator to track generation metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ACTIVE_WORKFLOWS.inc()

            try:
                result = func(*args, **kwargs)
                GENERATIONS_TOTAL.labels(status="success", node=node_name).inc()
                return result

            except Exception:
                GENERATIONS_TOTAL.labels(status="error", node=node_name).inc()
                raise

            finally:
                duration = time.time() - start_time
                GENERATION_DURATION.labels(node=node_name).observe(duration)
                ACTIVE_WORKFLOWS.dec()

        return wrapper
    return decorator


def update_gpu_metrics():
    """Update GPU utilization metrics."""
    try:
        import torch

        if torch.cuda.is_available():
            # Get GPU utilization (requires pynvml or similar)
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)

                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                GPU_UTILIZATION.set(util.gpu)

                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                GPU_MEMORY_USED.set(mem.used)

            except ImportError:
                # Fallback: just check if CUDA is available
                GPU_UTILIZATION.set(50.0)  # Placeholder

    except Exception as e:
        print(f"GPU metrics error: {e}")


def update_vectorstore_metrics():
    """Update vector store document count."""
    try:
        from codeops.memory.vector_store import get_vector_store

        store = get_vector_store("chroma")
        # Attempt to get count - implementation specific
        count = getattr(store, 'count', lambda: 0)()
        VECTOR_STORE_DOCUMENTS.set(count)

    except Exception:
        pass


class MetricsCollector:
    """Collects and exports Prometheus metrics."""

    def __init__(self, port: int = 9090):
        self.port = port
        self.running = False

    def start(self):
        """Start the metrics server."""
        start_http_server(self.port)
        self.running = True
        print(f"Metrics server started on port {self.port}")

    def get_metrics(self) -> str:
        """Get current metrics in Prometheus format."""
        update_gpu_metrics()
        update_vectorstore_metrics()
        return generate_latest(REGISTRY).decode("utf-8")

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status: int,
        duration: float
    ):
        """Record an API request."""
        API_REQUESTS.labels(
            endpoint=endpoint,
            method=method,
            status=str(status)
        ).inc()

        API_LATENCY.labels(endpoint=endpoint).observe(duration)


# Global collector instance
metrics_collector = MetricsCollector()


# FastAPI middleware for automatic tracking
def setup_fastapi_metrics(app):
    """Add metrics middleware to FastAPI app."""
    import time

    from fastapi import Request

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        metrics_collector.record_api_request(
            endpoint=request.url.path,
            method=request.method,
            status=response.status_code,
            duration=duration
        )

        return response

    return app


if __name__ == "__main__":
    # Start metrics server
    metrics_collector.start()

    # Keep running
    import time
    while True:
        update_gpu_metrics()
        time.sleep(15)
