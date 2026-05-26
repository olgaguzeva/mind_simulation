from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from mind_simulation.config import settings
from mind_simulation.utils import parse_json, render_transcript

from mind_simulation.models.judge_verdict import Verdict
from mind_simulation.models.debate_state import DebateState


class Judge:
    def __init__(self, llm: BaseChatModel) -> None:
        self.name = "Judge"
        self._llm = llm
        self._system = (settings.prompts_dir / f"{self.name.lower()}.md").read_text().strip()

    def evaluate(self, state: DebateState) -> dict:
        history_block = "Debate transcript:\n" + render_transcript(state["all_rounds"])
        if state["round_num"] >= settings.max_rounds:
            history_block += "\n\nThis is the final round. You MUST choose a winner and provide a summary."
        system = self._system + "\n\n" + history_block
        raw = self._llm.invoke([SystemMessage(content=system), HumanMessage(content=state["user_input"])]).content
        data = parse_json(raw)
        return {"verdict": Verdict.model_validate(data)}