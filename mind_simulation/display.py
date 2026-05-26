"""Terminal display helpers for Mind Parliament."""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mind_simulation.models.judge_verdict import Verdict
    from mind_simulation.models.personality_position import Position

_WIDTH = 64
_R    = "\033[0m"
_BOLD = "\033[1m"
_DIM  = "\033[2m"
_JUDGE_COLOR = "\033[35m"  # magenta reserved for judge

_PALETTE = ["\033[33m", "\033[36m", "\033[31m", "\033[32m", "\033[34m", "\033[37m"]


def _c(*codes_and_text: str) -> str:
    *codes, text = codes_and_text
    return "".join(codes) + text + _R


def _bar(activation: float, color: str) -> str:
    filled = round(activation * 12)
    return color + "█" * filled + _DIM + "░" * (12 - filled) + _R


def _sep(label: str = "") -> None:
    line = _c(_DIM, "─" * _WIDTH)
    if label:
        print(line)
        print(f"  {label}")
    print(line)


class Display:
    def __init__(self, agent_names: list[str]) -> None:
        colors = random.sample(_PALETTE, min(len(agent_names), len(_PALETTE)))
        self._colors: dict[str, str] = dict(zip(agent_names, colors))

    def _color(self, name: str) -> str:
        return self._colors.get(name, "")

    def print_direct(self, name: str, answer: str) -> None:
        color = self._color(name)
        print()
        _sep(_c(color, _BOLD, name))
        print()
        print(answer)
        print()

    def print_debate(self, all_rounds: list[list[Position]], verdict: Verdict, final_answer: str) -> None:
        print()
        _sep(_c(_BOLD, "Inner crowd"))

        for i, positions in enumerate(all_rounds, 1):
            print(_c(_DIM, f"\n  ── round {i} ──"))
            for p in sorted(positions, key=lambda x: x.activation, reverse=True):
                color = self._color(p.name)
                print(
                    f"\n  {_c(color, _BOLD, f'[{p.name}]')}"
                    f"  {_bar(p.activation, color)}"
                    f"  {_c(color, f'{p.activation:.2f}')}"
                )
                print(f"    {_c(_DIM, 'to others ')} : {p.says_to_others}")
                print(f"    {_c(_DIM, 'feels     ')} : {p.inner_feeling}")
                print(f"    {_c(_DIM, 'would say ')} : {_c(color, p.proposed_answer)}")

        print()
        print(f"  {_c(_JUDGE_COLOR, 'judge')} after round {len(all_rounds)}: {_c(_JUDGE_COLOR, verdict.reason)}")
        print()
        winner_color = self._color(verdict.winner or "")
        _sep(_c(winner_color, _BOLD, f"{verdict.winner} speaks"))
        print()
        print(final_answer)
        print()