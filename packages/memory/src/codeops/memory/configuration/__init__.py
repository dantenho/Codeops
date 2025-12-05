"""Configuration layer - Dependency injection and settings."""
from .dependency_injection import DependencyContainer
from .settings import MemorySettings, settings

__all__ = ["DependencyContainer", "MemorySettings", "settings"]
