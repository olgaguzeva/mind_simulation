from pydantic import BaseModel, Field


class Position(BaseModel):
    name: str
    says_to_others: str = ""
    inner_feeling: str = ""
    reasoning: str = ""
    activation: float = Field(default=0.5, ge=0.0, le=1.0)
    activation_reason: str = ""
    proposed_answer: str = ""
