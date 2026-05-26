from typing import Literal

from pydantic import BaseModel


class Verdict(BaseModel):
    decision: Literal["stop", "continue"] = "continue"
    winner: str | None = None
    reason: str = ""
    summary: str | None = None
