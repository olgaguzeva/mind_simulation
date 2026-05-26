from __future__ import annotations

from mind_simulation.agents.sub_personality_agent import SubPersonality
from mind_simulation.models.judge_verdict import Verdict
from mind_simulation.models.debate_state import DebateState
from mind_simulation.utils import render_transcript


class Debate:
    def __init__(self, agents: list[SubPersonality]) -> None:
        self.agents = agents

    def run_round(self, state: DebateState) -> dict:
        round_num = state["round_num"] + 1
        history = render_transcript(state["all_rounds"])
        positions = [agent.debate(state["user_input"], history, round_num, state["chat_history"])
                     for agent in self.agents]
        return {"all_rounds": [positions], "round_num": round_num}

    def speak_final(self, state: DebateState) -> dict[str, object]:
        verdict = state["verdict"]
        all_rounds = state["all_rounds"]
        best_position = max(all_rounds[-1], key=lambda p: p.activation)
        winner_name = verdict.winner if verdict and verdict.winner else best_position.name
        winner_agent = next((a for a in self.agents if a.name == winner_name), None)
        if winner_agent is None:
            # judge returned a name that doesn't match any agent; fall back to highest activation
            winner_name = best_position.name
            winner_agent = next(a for a in self.agents if a.name == winner_name)
        winner_position = next((p for p in all_rounds[-1] if p.name == winner_name), best_position)
        final = winner_agent.speak_final(
            state["user_input"],
            winner_position.proposed_answer,
            render_transcript(all_rounds),
            state["chat_history"],
        )
        return {
            "final_answer": final,
            "verdict": Verdict(
                decision="stop",
                winner=winner_name,
                reason=verdict.reason if verdict else "",
                summary=verdict.summary if verdict else None,
            ),
        }
