-- Composer Database Schema
-- Created: 2025-12-03T18-49-33Z
-- Agent: Composer

-- Example table structure
CREATE TABLE IF NOT EXISTS agent_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_timestamp
ON agent_operations(agent_id, timestamp);
