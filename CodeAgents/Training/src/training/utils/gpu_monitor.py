"""
Module: gpu_monitor.py
Purpose: Real-time GPU telemetry capture for training orchestration.

Provides lightweight helpers that snapshot device utilization so training
commands can record structural metrics (tokens, GPU activity, etc.) for
comparison runs prior to merging.

Agent: GPT-5.1 Codex
Created: 2025-12-03T06:45:00Z
Operation: [CREATE]
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import pynvml as NVML  # type: ignore
except Exception:  # pragma: no cover - pynvml optional
    NVML = None


@dataclass(frozen=True)
class GpuDeviceReading:
    """
    [CREATE] Snapshot of a single GPU device.

    Attributes:
        index (int): Device index as reported by NVML.
        name (str): Human-readable card identifier.
        utilization (float): Percent of SM utilization (0-100).
        memory_used_mb (float): Memory currently allocated in MB.
        memory_total_mb (float): Total memory available in MB.

    Agent: GPT-5.1 Codex
    Timestamp: 2025-12-03T06:45:00Z
    """

    index: int
    name: str
    utilization: float
    memory_used_mb: float
    memory_total_mb: float


@dataclass(frozen=True)
class GpuSnapshot:
    """
    [CREATE] Aggregate GPU telemetry reading.

    Attributes:
        timestamp (str): ISO-8601 timestamp for snapshot collection.
        devices (list[GpuDeviceReading]): Per-device readings.

    Agent: GPT-5.1 Codex
    Timestamp: 2025-12-03T06:45:00Z
    """

    timestamp: str
    devices: List[GpuDeviceReading]


class GpuMonitor:
    """
    [CREATE] Helper for capturing GPU telemetry with NVML.

    Design Pattern:
        Facade over NVML bindings that produces structured telemetry.

    Thread Safety:
        Not thread-safe. NVML handles are module-level and should be accessed
        from a single thread per process.

    Agent: GPT-5.1 Codex
    Timestamp: 2025-12-03T06:45:00Z
    """

    def __init__(self) -> None:
        """
        [CREATE] Initialize GPU monitor and NVML context when available.

        Raises:
            RuntimeError: If NVML initialization fails in an unexpected manner.
        """
        self._available = False
        if NVML is None:
            return

        try:
            NVML.nvmlInit()
            self._available = True
        except Exception as exc:  # pragma: no cover - best effort
            raise RuntimeError(f"Failed to initialize NVML: {exc}") from exc

    def is_available(self) -> bool:
        """
        [CREATE] Determine if GPU monitoring is supported.

        Returns:
            bool: True when NVML is initialized and GPUs are present.
        """
        return self._available

    def capture_snapshot(self) -> Optional[GpuSnapshot]:
        """
        [CREATE] Capture real-time GPU telemetry.

        Returns:
            Optional[GpuSnapshot]: Snapshot if NVML is available; otherwise None.

        Raises:
            RuntimeError: If NVML encounters an unexpected error mid-capture.
        """
        if not self._available:
            return None

        assert NVML is not None

        try:
            device_count = NVML.nvmlDeviceGetCount()
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Unable to list GPU devices: {exc}") from exc

        devices: List[GpuDeviceReading] = []
        for index in range(device_count):
            handle = NVML.nvmlDeviceGetHandleByIndex(index)
            raw_name = NVML.nvmlDeviceGetName(handle)
            name = raw_name.decode("utf-8") if isinstance(raw_name, bytes) else str(raw_name)
            util = NVML.nvmlDeviceGetUtilizationRates(handle)
            memory = NVML.nvmlDeviceGetMemoryInfo(handle)
            devices.append(
                GpuDeviceReading(
                    index=index,
                    name=name,
                    utilization=float(util.gpu),
                    memory_used_mb=float(memory.used) / (1024 * 1024),
                    memory_total_mb=float(memory.total) / (1024 * 1024),
                )
            )

        snapshot = GpuSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            devices=devices,
        )
        return snapshot

    def summarize_snapshot(self, snapshot: Optional[GpuSnapshot]) -> Dict[str, Any]:
        """
        [CREATE] Convert a snapshot into aggregate metrics.

        Args:
            snapshot (Optional[GpuSnapshot]): Snapshot to summarize.

        Returns:
            Dict[str, Any]: Aggregated metrics with defaults when unavailable.

        Complexity:
            Time: O(n) where n equals number of GPU devices.
            Space: O(1) additional memory.
        """
        if snapshot is None or not snapshot.devices:
            return {
                "gpu_devices": 0,
                "gpu_utilization_avg": 0.0,
                "gpu_memory_used_mb": 0.0,
            }

        utilization = [device.utilization for device in snapshot.devices]
        memory = [device.memory_used_mb for device in snapshot.devices]

        return {
            "gpu_devices": len(snapshot.devices),
            "gpu_utilization_avg": sum(utilization) / len(utilization),
            "gpu_memory_used_mb": sum(memory) / len(memory),
        }

    def structured_snapshot(self) -> Dict[str, Any]:
        """
        [CREATE] Produce structured telemetry for downstream reporting.

        Returns:
            Dict[str, Any]: JSON-serializable representation of GPU state.
        """
        snapshot = self.capture_snapshot()
        if snapshot is None:
            return {"available": False, "devices": []}

        devices_payload = [
            {
                "index": device.index,
                "name": device.name,
                "utilization": device.utilization,
                "memory_used_mb": device.memory_used_mb,
                "memory_total_mb": device.memory_total_mb,
            }
            for device in snapshot.devices
        ]

        return {
            "available": True,
            "timestamp": snapshot.timestamp,
            "devices": devices_payload,
            **self.summarize_snapshot(snapshot),
        }
