import type { TelemetryRecord, Workflow } from "./types";

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:5000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
}

export const Api = {
  fetchWorkflows(): Promise<Workflow[]> {
    return request("/workflows");
  },
  createWorkflow(payload: Partial<Workflow>): Promise<Workflow> {
    return request("/workflows", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  fetchTelemetry(): Promise<TelemetryRecord[]> {
    return request("/telemetry");
  },
  fetchSkeletonSummary(): Promise<Record<string, unknown>> {
    return request("/skeleton/summary");
  },
};

