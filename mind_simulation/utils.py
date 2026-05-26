from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from mind_simulation.models.personality_position import Position

_log = logging.getLogger(__name__)


def parse_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    _log.warning("could not parse JSON from LLM output: %.200s", text)
    return {}


def render_transcript(all_rounds: list[list[Position]]) -> str:
    lines: list[str] = []
    for i, positions in enumerate(all_rounds, 1):
        lines.append(f"  Round {i}:")
        for p in positions:
            lines.append(f"    {p.name} (activation {p.activation:.2f}): {p.says_to_others}")
    return "\n".join(lines)


def scan_folder(folder: Path, pattern: str = "*.md") -> dict[str, Path]:
    return {p.stem.lower(): p for p in folder.glob(pattern)}
