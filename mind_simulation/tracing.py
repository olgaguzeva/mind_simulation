from __future__ import annotations

from mind_simulation.config import settings


def get_callbacks() -> list:
    if not settings.langfuse_public_key:
        return []
    from langfuse import Langfuse
    from langfuse.langchain import CallbackHandler
    Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
    return [CallbackHandler()]
