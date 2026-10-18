"""Application settings read from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    public_url: str | None


def load_settings() -> Settings:
    return Settings(
        host=os.environ.get("NEXUS_HOST", "127.0.0.1"),
        port=int(os.environ.get("NEXUS_PORT", "8000")),
        public_url=os.environ.get("NEXUS_PUBLIC_URL") or None,
    )