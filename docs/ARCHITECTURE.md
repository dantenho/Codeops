# Architecture Documentation

## Overview

CodeAgents follows a modular architecture with strict separation of concerns.

## Components

### 1. Frontend (Streamlit)

- **Location**: `frontend_prototype/`
- **Pattern**: Multi-page app with decoupled services.
- **State**: `st.session_state` for persistence.

### 2. Organizator (CrewAI)

- **Location**: `organizator/`
- **Pattern**: Configuration-driven agents (YAML).
- **Logic**: `src/crew.py` orchestrates agents defined in `config/`.

### 3. Nodes

- **Location**: `nodes/`
- **Purpose**: Independent modules for specific tasks (Image Gen, Training).

## Python Scheme (The Rules)

- **Clean Architecture**: Entities -> Use Cases -> Adapters.
- **Strict Typing**: All code must be typed.
- **Error Handling**: Custom exceptions and centralized handling.
