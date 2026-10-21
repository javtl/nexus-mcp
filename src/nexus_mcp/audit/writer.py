from __future__ import annotations

import json
import sys
import threading
from pathlib import Path


class JsonlAuditWriter:
    def __init__(self, path, echo_stdout: bool = False) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()
        self._echo = echo_stdout

    def write(self, event) -> None:
        line = json.dumps(event.to_dict(), ensure_ascii=False, default=str)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
            if self._echo:
                print("AUDIT " + line, file=sys.stdout, flush=True)