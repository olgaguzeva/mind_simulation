"""Language model selection for LangChain execution."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

from mind_simulation.config import settings


def build_chat_model(model: str = settings.model, temperature: float = settings.temperature) -> BaseChatModel:
    return ChatGroq(model=model, temperature=temperature, api_key=settings.groq_api_key)