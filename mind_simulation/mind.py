"""Inner parliament — LangGraph orchestrator."""

from __future__ import annotations

import queue
import re
from langchain_core.language_models.chat_models import BaseChatModel
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

    def __init__(self, agents: list[SubPersonality], llm: BaseChatModel) -> None:
        self._chat_history: list[BaseMessage] = []
        self._callbacks = get_callbacks()
        self.sub_personalities = {a.name.lower(): a.name for a in agents}
        self.debate = Debate(agents)
        self.judge = Judge(llm)
        self.display = Display([a.name for a in agents])
        self._graph = self._build_graph()

    @classmethod
    def from_definitions(cls, definitions: list[tuple[str, str]]) -> Mind:
        """Create a Mind from (name, description) pairs — used by the web UI."""
        llm = build_chat_model()
        agents = [SubPersonality(name, llm, description=desc) for name, desc in definitions]
        return cls(agents, llm)

    @classmethod
    def from_defaults(cls) -> Mind:
        """Create a Mind from the default personality prompt files — used by the CLI."""
        llm = build_chat_model()
        raw = scan_folder(settings.personalities_dir)
        agents = [SubPersonality(name.capitalize(), llm, description=path.read_text().strip())
                  for name, path in raw.items()]
        return cls(agents, llm)

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

    def _initial_state(self, user_input: str) -> dict:
        return {
            "user_input": user_input,
            "chat_history": self._chat_history,
            "all_rounds": [],
            "verdict": None,
            "final_answer": "",
            "round_num": 0,
        }

    def respond(self, user_input: str) -> tuple[list[list[Position]], Verdict, str]:
        """Run the debate graph. Returns (all_rounds, verdict, final_answer)."""
        final_state = self._graph.invoke(
            self._initial_state(user_input),
            config={"callbacks": self._callbacks},
        )
        verdict = final_state["verdict"]
        final_answer = final_state["final_answer"]
        self._update_history(user_input, verdict, final_answer)
        return final_state["all_rounds"], verdict, final_answer

    def stream_respond(self, user_input: str, q: queue.Queue) -> None:
        """Stream the debate graph into a queue. Puts (kind, data) tuples; kind is 'chunk', 'error', or 'done'."""
        pending_verdict: Verdict | None = None
        pending_answer = ""
        try:
            for chunk in self._graph.stream(
                self._initial_state(user_input),
                config={"callbacks": self._callbacks},
                stream_mode="updates",
            ):
                node, update = next(iter(chunk.items()))
                if node in ("judge", "speak_final"):
                    v = update.get("verdict")
                    if v:
                        pending_verdict = v
                if node == "speak_final":
                    pending_answer = update.get("final_answer", "")
                q.put(("chunk", chunk))
            if pending_verdict:
                self._update_history(user_input, pending_verdict, pending_answer)
        except Exception as exc:
            q.put(("error", str(exc)))
        finally:
            q.put(("done", None))

    def direct_respond(self, name: str, user_input: str) -> str:
        """Ask one agent to reply directly, bypassing the debate."""
        agent = next(a for a in self.debate.agents if a.name == name)
        return agent.speak_directly(user_input, self._chat_history)

    def detect_personality(self, text: str) -> str | None:
        match = re.match(r"@(\w+)", text.strip())
        if match:
            tag = match.group(1).lower()
            if tag in self.sub_personalities:
                return self.sub_personalities[tag]
            else:
                raise Exception(f"Personality {tag} not found.")


def main() -> None:
    mind = Mind.from_defaults()

    print("\nMind Simulation  —  type your message, or 'quit' to exit.")
    print(f"Tip: start with @<personality name> to speak to one directly. "
          f"The crowd is {', '.join(mind.sub_personalities.values())}")
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
        try:
            name = mind.detect_personality(user_input)
            if name:
                answer = mind.direct_respond(name, user_input)
                mind.display.print_direct(name, answer)
            else:
                all_rounds, verdict, final_answer = mind.respond(user_input)
                mind.display.print_debate(all_rounds, verdict, final_answer)
        except Exception as e:
            print(f"\n[error] {e}\n")
