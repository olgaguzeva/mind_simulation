"""Sub-personality agent definitions for the Mind Parliament."""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from mind_simulation.models.personality_position import Position
from mind_simulation.utils import parse_json
from mind_simulation.config import settings


class SubPersonality:
    """One psychological sub-personality with its own identity and voice."""

    def __init__(self, name: str, llm: BaseChatModel, prompt_path: Path) -> None:
        self.name = name
        self._llm = llm
        template = PromptTemplate.from_file(settings.prompts_dir / "sub_personality.md")
        description = prompt_path.read_text().strip()
        self._system = template.format(personality_description=description)
        self._debate = (settings.prompts_schemas_dir / "debate.md").read_text().strip()
        self._final = (settings.prompts_schemas_dir / "final.md").read_text().strip()
        self._direct = (settings.prompts_schemas_dir / "direct.md").read_text().strip()

    def debate(self, user_input: str, history: str, round_num: int, chat_history: list[BaseMessage] | None = None) -> Position:
        history_block = f"Debate so far:\n{history}\n\n" if history else ""
        system = self._system + "\n\n" + history_block + f"This is round {round_num}.\n\n" + self._debate
        messages = [SystemMessage(content=system)] + (chat_history or []) + [HumanMessage(content=user_input)]
        raw = self._llm.invoke(messages).content
        data = parse_json(raw)
        return Position.model_validate({"name": self.name, **data})

    def speak_final(self, user_input: str, proposed_answer: str, history: str, chat_history: list[BaseMessage] | None = None) -> str:
        system = (
            self._system + "\n\n"
            + f"Debate history:\n{history}\n\n"
            + f"In the debate, you proposed: {proposed_answer}\n\n"
            + self._final
        )
        messages = [SystemMessage(content=system)] + (chat_history or []) + [HumanMessage(content=user_input)]
        return self._llm.invoke(messages).content.strip()

    def speak_directly(self, user_input: str, chat_history: list[BaseMessage] | None = None) -> str:
        system = self._system + "\n\n" + self._direct
        messages = [SystemMessage(content=system)] + (chat_history or []) + [HumanMessage(content=user_input)]
        return self._llm.invoke(messages).content.strip()
