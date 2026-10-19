"""Append-only JSONL audit writer (ADR-009)."""

from __future__ import annotations

import json
import threading
from pathlib import Path

from .models import AuditEvent


class JsonlAuditWriter:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()

    def write(self, event: AuditEvent) -> None:
        line = json.dumps(event.to_dict(), ensure_ascii=False, default=str)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")