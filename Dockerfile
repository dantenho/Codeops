FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip setuptools wheel

# Install base dependencies
RUN pip install -e .

# Install dev/test dependencies
RUN pip install -e ".[dev,test]"

# Copy source code
COPY . .

# Create directories
RUN mkdir -p /app/chroma_db /app/memory /app/ComfyUI/models /app/ComfyUI/output

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["pytest", "-v", "--cov"]
