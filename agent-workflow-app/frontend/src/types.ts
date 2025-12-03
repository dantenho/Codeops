export type WorkflowCategory = "telemetry" | "skeleton" | "rag" | "communication";
export type WorkflowStatus = "planned" | "in_progress" | "blocked" | "done";

export interface Workflow {
  id: string;
  title: string;
  owner: string;
  category: WorkflowCategory;
  status: WorkflowStatus;
  priority: "low" | "medium" | "high";
  tags: string[];
  compliance?: Record<string, unknown>;
  metrics?: Record<string, number>;
  next_steps?: string[];
  blockers?: string[];
}

export interface TelemetryRecord {
  timestamp: string;
  operation: string;
  target: string;
  status: "SUCCESS" | "FAILURE" | "PARTIAL";
  duration_ms: number;
  context: Record<string, unknown>;
}

