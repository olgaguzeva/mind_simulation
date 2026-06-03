"""FastAPI web application for Mind Simulation."""
from __future__ import annotations

import asyncio
import json
import queue
import random
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from mind_simulation.mind import Mind
from mind_simulation.utils import scan_folder
from mind_simulation.config import settings

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR.parent / "assets"

app = FastAPI(title="Mind Simulation")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

_sessions: dict[str, Mind] = {}

PALETTE = ["#f59e0b", "#06b6d4", "#f87171", "#34d399", "#60a5fa", "#f472b6"]


class PersonalityIn(BaseModel):
    name: str
    description: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty")
        return v


class StartRequest(BaseModel):
    personalities: list[PersonalityIn]


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
async def landing():
    return HTMLResponse((BASE_DIR / "templates" / "landing.html").read_text())


@app.get("/app")
async def app_view():
    return HTMLResponse((BASE_DIR / "templates" / "app.html").read_text())



@app.get("/api/defaults")
async def get_defaults():
    raw = scan_folder(settings.personalities_dir)
    return [
        {"name": stem.capitalize(), "description": path.read_text().strip()}
        for stem, path in sorted(raw.items())
    ]


@app.post("/api/start")
async def start_session(body: StartRequest):
    if not body.personalities:
        raise HTTPException(400, "At least one personality is required.")
    if len(body.personalities) > 6:
        raise HTTPException(400, "Maximum 6 personalities.")

    session_id = str(uuid.uuid4())
    _sessions[session_id] = Mind.from_definitions([(p.name, p.description) for p in body.personalities])

    colors = random.sample(PALETTE, min(len(body.personalities), len(PALETTE)))
    personality_colors = {p.name: c for p, c in zip(body.personalities, colors)}

    return {"session_id": session_id, "personality_colors": personality_colors}


@app.post("/api/chat/stream")
async def chat_stream(body: ChatRequest):
    mind = _sessions.get(body.session_id)
    if not mind:
        raise HTTPException(404, "Session not found. Please start a new session.")
    msg = body.message.strip()
    if not msg:
        raise HTTPException(400, "Message cannot be empty.")

    try:
        personality = mind.detect_personality(msg)
    except Exception as exc:
        raise HTTPException(400, str(exc))
    generator = _generate_direct_sse(mind, msg, personality) if personality else _generate_sse(mind, msg)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _generate_direct_sse(mind: Mind, user_input: str, personality: str):
    loop = asyncio.get_running_loop()
    try:
        answer = await loop.run_in_executor(None, mind.direct_respond, personality, user_input)
        yield f"data: {json.dumps({'type': 'direct', 'winner': personality, 'answer': answer})}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


async def _generate_sse(mind: Mind, user_input: str):
    q: queue.Queue = queue.Queue()
    threading.Thread(target=mind.stream_respond, args=(user_input, q), daemon=True).start()

    loop = asyncio.get_running_loop()

    while True:
        kind, data = await loop.run_in_executor(None, q.get)

        if kind == "done":
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        if kind == "error":
            yield f"data: {json.dumps({'type': 'error', 'message': data})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        node, update = next(iter(data.items()))

        if node == "debate_round":
            rounds = update.get("all_rounds", [[]])
            positions = rounds[0] if rounds else []
            round_num = update.get("round_num", 0)
            yield f"data: {json.dumps({'type': 'round', 'round_num': round_num, 'positions': [p.model_dump() for p in positions]})}\n\n"

        elif node == "judge":
            verdict = update.get("verdict")
            if verdict:
                yield f"data: {json.dumps({'type': 'verdict', 'decision': verdict.decision, 'reason': verdict.reason, 'winner': verdict.winner})}\n\n"

        elif node == "speak_final":
            answer = update.get("final_answer", "")
            verdict = update.get("verdict")
            yield f"data: {json.dumps({'type': 'final', 'winner': verdict.winner if verdict else None, 'answer': answer})}\n\n"
