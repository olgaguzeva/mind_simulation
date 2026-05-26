"""Inner parliament — LangGraph orchestrator."""

from __future__ import annotations

import re
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from mind_simulation.debate import Debate
from mind_simulation.agents.judge_agent import Judge
from mind_simulation.agents.sub_personality_agent import SubPersonality
from mind_simulation.config import settings
from mind_simulation.display import Display
from mind_simulation.tracing import get_callbacks
from mind_simulation.llm import build_chat_model
from mind_simulation.models.debate_state import DebateState
from mind_simulation.models.judge_verdict import Verdict
from mind_simulation.models.personality_position import Position
from mind_simulation.utils import scan_folder


class Mind:
    """Wires agents into a LangGraph debate graph and manages conversation history."""

    def __init__(self) -> None:
        llm = build_chat_model()
        self._chat_history: list[BaseMessage] = []
        self.sub_personalities = scan_folder(settings.personalities_dir)
        agents: list[SubPersonality] = [
            SubPersonality(name.capitalize(), llm, path)
            for name, path in self.sub_personalities.items()
        ]
        self.debate = Debate(agents)
        self.judge = Judge(llm)
        self.display = Display([a.name for a in agents])
        self._graph = self._build_graph()

    def _routing(self, state: DebateState) -> str:
        verdict = state["verdict"]
        if (verdict and verdict.decision == "stop" and verdict.winner) or state["round_num"] >= settings.max_rounds:
            return "speak_final"
        return "debate_round"

    def _build_graph(self):
        g = StateGraph(DebateState)
        g.add_node("debate_round", self.debate.run_round)
        g.add_node("judge", self.judge.evaluate)
        g.add_node("speak_final", self.debate.speak_final)
        g.set_entry_point("debate_round")
        g.add_edge("debate_round", "judge")
        g.add_conditional_edges("judge", self._routing, {"speak_final": "speak_final", "debate_round": "debate_round"})
        g.add_edge("speak_final", END)
        return g.compile()

    def _update_history(self, user_input: str, verdict: Verdict, final_answer: str) -> None:
        self._chat_history.append(HumanMessage(content=user_input))
        self._chat_history.append(AIMessage(content=f"[Debate: {verdict.summary or verdict.reason}]\n{final_answer}"))
        if len(self._chat_history) > settings.max_history:
            del self._chat_history[:-settings.max_history]

    def respond(self, user_input: str) -> tuple[list[list[Position]], Verdict, str]:
        """Run the debate graph. Returns (all_rounds, verdict, final_answer)."""
        final_state = self._graph.invoke(
            {
                "user_input": user_input,
                "chat_history": self._chat_history,
                "all_rounds": [],
                "verdict": None,
                "final_answer": "",
                "round_num": 0,
            },
            config={"callbacks": get_callbacks()},
        )
        verdict = final_state["verdict"]
        final_answer = final_state["final_answer"]
        self._update_history(user_input, verdict, final_answer)
        return final_state["all_rounds"], verdict, final_answer

    def direct_respond(self, name: str, user_input: str) -> str:
        """Ask one agent to reply directly, bypassing the debate."""
        agent = next(a for a in self.debate.agents if a.name == name)
        if not agent:
            raise Exception(f"Personality {name} not found.")
        return agent.speak_directly(user_input, self._chat_history)

    def detect_personality(self, text: str) -> str | None:
        match = re.match(r"@(\w+)", text.strip())
        if match:
            tag = match.group(1).lower()
            if tag in self.sub_personalities:
                return tag.capitalize()
        return None


def main() -> None:
    mind = Mind()
    print("\nMind Simulation  —  type your message, or 'quit' to exit.")
    print(f"Tip: start with @<personality name> to speak to one directly. "
          f"The crowd is {', '.join([p.capitalize() for p in mind.sub_personalities.keys()])}")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        name = mind.detect_personality(user_input)
        try:
            if name:
                answer = mind.direct_respond(name, user_input)
                mind.display.print_direct(name, answer)
            else:
                all_rounds, verdict, final_answer = mind.respond(user_input)
                mind.display.print_debate(all_rounds, verdict, final_answer)
        except Exception as e:
            print(f"\n[error] {e}")
            print()
