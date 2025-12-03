# Agent Workflow App

React + Flask reference implementation that turns the telemetry, skeleton, and annotation insights from the Agents.MD workspace into an actionable workflow manager. The project ships with sample data, API documentation, and deployment assets so it can be pushed directly to GitHub.

## Repository layout

Path | Purpose
---- | -------
`frontend/` | Vite + React TypeScript UI (workflow board, telemetry dashboard, skeleton checklist, config panel).
`backend/` | Flask API exposing workflow, telemetry, and skeleton-validation services (uses UV-friendly layout).
`docs/` | Analysis summary plus deployment notes.
`data/` | Seed JSON describing baseline workflows and telemetry events.
`infrastructure/` | Optional Docker Compose for local orchestration.

## Getting started

```bash
# Backend (PowerShell/Unix)
cd backend
uv venv
uv pip install -r requirements.txt  # UV is recommended per Agents.MD
uv run flask --app app run --debug

# Frontend
cd frontend
nvm use 20
npm install
npm run dev
```

Set `VITE_API_BASE_URL` (frontend) or `APP_API_BASE_URL` (backend) if the services run on non-default ports.

## Key features

- **Workflow board** tuned to telemetry/skeleton/RAG initiatives mentioned in the original logs.
- **Telemetry dashboard** mirroring metrics emitted by `DeepSeekR1TELEMETRIC.txt`.
- **Skeleton completeness checklist** based on `skeleton-generator/scripts/complete_skeleton_generator.py`.
- **RAG seeding tracker** and **configuration panel** capturing `.cursor`/`.claude` expectations.
- **Sample data + tests** so GitHub reviewers can evaluate functionality quickly.

## Deployment

See `docs/deployment.md` for Docker Compose and manual deployment instructions. The repo is ready for GitHub actions or third‑party CI workflows once pushed.
