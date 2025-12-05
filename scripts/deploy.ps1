#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deployment script for Digital Content Farm

.DESCRIPTION
    Supports multiple deployment modes: dev, prod, gpu-test, lint

.PARAMETER Mode
    Deployment mode: dev, prod, gpu-test, lint, test

.EXAMPLE
    .\scripts\deploy.ps1 -Mode dev
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod", "gpu-test", "lint", "test")]
    [string]$Mode
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

switch ($Mode) {
    "dev" {
        Write-Status "Starting development environment..."
        docker-compose up --build
    }

    "prod" {
        Write-Status "Starting production environment..."
        docker-compose -f docker-compose.yml up -d --build
        Write-Status "Services started in background"
        docker-compose ps
    }

    "gpu-test" {
        Write-Status "Testing GPU availability..."
        docker-compose run --rm orchestrator python -c @"
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"@
    }

    "lint" {
        Write-Status "Running linting checks..."
        python -m ruff check . --fix
        python -m ruff format .
        Write-Status "Linting complete"
    }

    "test" {
        Write-Status "Running test suite..."
        python -m pytest tests/ -v --tb=short --cov=nodes --cov-report=term-missing
    }
}
