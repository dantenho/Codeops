Deployment Guide
================

This document describes the recommended ways to run the Agent Workflow App locally or in CI/CD.

Prerequisites
-------------

- **Node.js**: Install via `nvm` (`nvm install 20 && nvm use 20`).
- **Python**: Use `uv` for dependency management (`uv venv && uv pip install -r requirements.txt`).
- **Docker** (optional): Required for the Compose workflow.

Environment variables:

Variable | Purpose | Default
-------- | ------- | -------
`APP_API_BASE_URL` | Public URL exposed by Flask backend | `http://127.0.0.1:5000`
`VITE_API_BASE_URL` | Frontend request base URL | Derived from window location or `.env`
`APP_ALLOW_ORIGINS` | Comma-separated CORS origins | `http://localhost:5173`

Local Development (manual)
--------------------------

```bash
# Backend
cd backend
uv venv
uv pip install -r requirements.txt
uv run flask --app app run --debug --port 5000

# Frontend
cd frontend
nvm use 20
npm install
npm run dev -- --port 5173
```

Visit `http://localhost:5173`. The frontend proxies API calls to `http://localhost:5000` (configurable via `VITE_API_BASE_URL`).

Docker Compose
--------------

```bash
cd infrastructure
docker compose up --build
```

Services:

- `workflow-backend`: Flask API served via Gunicorn on port 8000.
- `workflow-frontend`: Vite build served via nginx on port 4173.

CI/CD Notes
-----------

1. Run `npm run test` inside `frontend/` and `uv run pytest` in `backend/`.
2. Archive the `frontend/dist` artifacts or publish via GitHub Pages.
3. Deploy the backend to any Flask-compatible host (Render, Railway, Fly) or container registry.

Future Enhancements
-------------------

- Automate database migrations once persistent storage is introduced.
- Add GitHub Actions workflow that enforces telemetry schema tests and skeleton checklist linting.
- Provide infrastructure IaC scripts (Terraform) for cloud deployment.
