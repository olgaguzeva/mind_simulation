from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from mind_simulation.models.personality_position import Position
from mind_simulation.models.judge_verdict import Verdict


class DebateState(TypedDict):
    user_input: str
    chat_history: list[BaseMessage]
    all_rounds: Annotated[list[list[Position]], operator.add]
    verdict: Verdict | None
    final_answer: str
    round_num: int
