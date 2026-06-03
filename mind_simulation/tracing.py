from __future__ import annotations

import urllib.request
from mind_simulation.config import settings


def get_callbacks() -> list:
    if not settings.langfuse_public_key:
        return []
    try:
        urllib.request.urlopen(settings.langfuse_host, timeout=2)
    except Exception:
        print(f"Langfuse is not available at {settings.langfuse_host} — metrics will not be stored.")
        return []
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler
    Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
    return [CallbackHandler()]
