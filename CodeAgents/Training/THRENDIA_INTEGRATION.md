# Threndia ↔ Eudora-X Pylorix Integration

The Threndia initiative (`https://github.com/Eudora-IA/Threndia`) functions as the market-analysis & agent-training branch for EudoraX. This document explains how Threndia cooperates with Eudora-X Pylorix inside the Agent Training System (ATS).

---

## Scope & Responsibilities

| Pillar | Threndia Branch | Eudora-X Pylorix |
| --- | --- | --- |
| Market Intel | Crawl/web-scrape market & ecosystem updates; ingest partner APIs | Consume curated intel, validate signal quality, feed ATS activities |
| Training Content | Normalize intel into prompts, flashcards, and activity templates | Run market-analysis sessions, record reflections, emit telemetry |
| Telemetry | Produce AMES-compliant logs tagged `mutual_cooperation` | Store logs under `CodeAgents/EudoraX-Pylorix/*`, share aggregates |

---

## Configuration Checklist

1. Clone the Threndia repo alongside this workspace (recommended path: `../Threndia`).
2. Export required secrets before running ATS commands:
   - `THRENDIA_API_TOKEN`
   - `THRENDIA_SCRAPE_FREQ_MINUTES`
   - `THRENDIA_PARTNER_ENDPOINT`
3. Register the shared storage mount (defaults to `CodeAgents/Training/ThrendiaData/`).
4. Ensure `EudoraX-Pylorix` is listed in `config/agent_profiles.yaml` with:
   - `roles: ["market_analyst", "training_integrator"]`
   - `intel_sources` (array of REST/Graph endpoints)
   - `telemetry_namespace: "mutual_cooperation"`

> ⚠️ **Credential Storage:** Use OS keychains or Azure/Hashicorp vaults. Never commit secrets.

---

## Data Flow

1. **Harvest:** Threndia workers perform scraping/API pulls on a cadence (`THRENDIA_SCRAPE_FREQ_MINUTES`).
2. **Normalize:** Results are converted into structured intel packets (JSON) and written to `ThrendiaData/intel/*.json`.
3. **Ingest:** `training threndia-sync` loads packets, deduplicates items, and persists them via `ThrendiaService`.
4. **Train:** `training market-analysis --agent EudoraX-Pylorix` generates ATS activities informed by the latest intel.
5. **Telemetry:** Every ingestion + training run emits AMES-style logs to `CodeAgents/EudoraX-Pylorix/logs` and analysis artifacts under `.../analysis`.

---

## Telemetry Requirements

- File naming: `log_{timestamp}_{hash}.json`
- Operation identifiers:
  - `threndia_sync` – ingestion events
  - `market_analysis_session` – training sessions using Threndia intel
- Context payload must include:
  - `intel_batch_id`
  - `sources` (array of endpoints)
  - `mutual_cooperation: true`
- Store errors under `CodeAgents/EudoraX-Pylorix/errors/` using `error_schema.json`.

---

## Testing & Validation

1. Run `pytest tests/test_threndia_service.py`
2. Execute a dry-run sync:
   ```bash
   training threndia-sync --agent EudoraX-Pylorix --dry-run
   ```
3. Verify AMES logs appear with the `mutual_cooperation` flag.

---

*Maintained under Agents.MD protocol. Last updated: 2025-12-03.*
