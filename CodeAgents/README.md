# 🗂️ CodeAgents Telemetry Database

This directory contains the structured telemetry data for all AI agents operating in this workspace.

## 📂 Directory Structure

```
CodeAgents/
├── schemas/                # JSON Schemas for validation
│   ├── operation_schema.json
│   └── error_schema.json
├── GrokIA/                 # Agent-specific directories
│   ├── logs/               # Operation logs
│   ├── errors/             # Error reports
│   └── analysis/           # Analysis outputs
├── GeminiFlash25/
├── GeminiPro25/
├── GeminiPro30/
├── Jules/
├── ClaudeCode/
└── Composer/
```

## 📝 File Naming Convention

All telemetry files MUST follow this naming convention:

```
{TYPE}_{TIMESTAMP}_{SHORT_HASH}.json
```

**Examples:**
- `log_2025-12-03T14-30-00_a1b2c3.json`
- `error_2025-12-03T14-30-00_d4e5f6.json`

## 📊 Schemas

### Operation Log
See `schemas/operation_schema.json` for the full schema.
Required fields: `agent`, `timestamp`, `operation`, `target`, `status`.

### Error Log
See `schemas/error_schema.json` for the full schema.
Required fields: `agent`, `timestamp`, `error_type`, `message`, `severity`.

---
*Managed by Agents.MD Protocol v3.0*
