#!/bin/bash
# Deployment script for Digital Content Farm
# Supports: dev, prod, gpu-test, lint, test modes

set -e

MODE=$1

function status() {
    echo -e "\033[36m>>> $1\033[0m"
}

case $MODE in
    "dev")
        status "Starting development environment..."
        docker-compose up --build
        ;;

    "prod")
        status "Starting production environment..."
        docker-compose -f docker-compose.yml up -d --build
        status "Services started in background"
        docker-compose ps
        ;;

    "gpu-test")
        status "Testing GPU availability..."
        docker-compose run --rm orchestrator python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"
        ;;

    "lint")
        status "Running linting checks..."
        python -m ruff check . --fix
        python -m ruff format .
        status "Linting complete"
        ;;

    "test")
        status "Running test suite..."
        python -m pytest tests/ -v --tb=short --cov=nodes --cov-report=term-missing
        ;;

    *)
        echo "Usage: $0 {dev|prod|gpu-test|lint|test}"
        echo ""
        echo "Modes:"
        echo "  dev      - Start development environment with logs"
        echo "  prod     - Start production environment (background)"
        echo "  gpu-test - Test GPU availability in Docker"
        echo "  lint     - Run Ruff linting and formatting"
        echo "  test     - Run pytest test suite with coverage"
        exit 1
        ;;
esac
