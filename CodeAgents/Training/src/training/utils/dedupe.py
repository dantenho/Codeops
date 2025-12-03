"""
Module: dedupe.py
Purpose: File-level deduplication helpers for training assets.

Agent: GPT-5.1 Codex
Created: 2025-12-03T07:10:00Z
Operation: [CREATE]
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


@dataclass
class DuplicateGroup:
    hash: str
    files: List[Path]


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(root: Path, extensions: Sequence[str] | None = None) -> List[DuplicateGroup]:
    """
    Scan for duplicate files under root and group them by content hash.
    """
    if not root.exists():
        return []

    allowed_ext = {ext.lower() for ext in extensions} if extensions else None
    buckets: Dict[str, List[Path]] = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if allowed_ext and path.suffix.lower() not in allowed_ext:
            continue
        file_hash = _hash_file(path)
        buckets.setdefault(file_hash, []).append(path)

    duplicates = [DuplicateGroup(hash=h, files=paths) for h, paths in buckets.items() if len(paths) > 1]
    duplicates.sort(key=lambda group: len(group.files), reverse=True)
    return duplicates


def remove_duplicates(groups: Iterable[DuplicateGroup]) -> int:
    """
    Remove duplicate files, keeping the first occurrence in each group.
    Returns the number of files deleted.
    """
    removed = 0
    for group in groups:
        for path in group.files[1:]:
            if path.exists():
                path.unlink()
                removed += 1
    return removed
