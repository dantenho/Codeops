# Digital Content Farm - Production Dockerfile
# Multi-stage build with GPU support

# Base image with CUDA
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    python3.12-venv \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser

# Builder stage
FROM base AS builder

WORKDIR /app

# Copy dependency files
COPY packages/core/pyproject.toml packages/core/
COPY packages/memory/pyproject.toml packages/memory/
COPY packages/orchestrator/pyproject.toml packages/orchestrator/

# Create virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -e packages/core

# Runtime stage
FROM base AS runtime

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 8188

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import torch; print('GPU:', torch.cuda.is_available())" || exit 1

# Default command
CMD ["python3", "-m", "packages.orchestrator.src.codeops.orchestrator.graph"]
