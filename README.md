# Mind Simulation

## Introduction
Mind Simulation is an experimental project exploring what happens when multiple AI agents behave as different inner sub-personalities of a single mind.  
The idea was inspired by the Internal Family Systems (IFS) approach, which views the mind as a collection of different “parts” or inner personalities, each with its own emotions, motivations, and perspective.  
Instead of generating a single response directly, the system creates an internal discussion between multiple personalities that may agree, disagree, challenge each other, or form temporary alliances before producing a final answer.

The default setup includes three core personalities:
- Inner Child — emotional, curious, creative, vulnerable, impulsive.
- Inner Critic — cautious, analytical, judgmental, protective, realistic.
- Adult / Self — balanced, reflective, calm, and focused on integration.

## Disclaimer
The project is not intended to diagnose, replace therapy, or define objective psychological truth.  
It is a playground for self-reflection, emotional exploration, journaling, dialogue simulation, and experimentation.
Watching multiple AI personalities discuss your thoughts, doubts, fears, or decisions can sometimes feel creepy. At the same time, the process can also be insightful, entertaining, and unexpectedly helpful for reflection.

## The personalities

| Personality      | Character |
|------------------|-----------|
| **Inner Child**  | emotional, curious, creative, vulnerable, impulsive. |
| **Inner Critic** | cautious, analytical, judgmental, protective, realistic. |
| **Adult / Self** | balanced, reflective, calm, and focused on integration. |

Each personality is defined in `mind_simulation/prompts/sub_personalities/<name>.md`.

You can customize the personalities by editing their prompts and adjusting their traits, behavior, communication style, or emotional tendencies.  
Personalities can also be renamed, removed, or extended by modifying the corresponding prompt files.

Some additional personalities you may want to include:

| Personality | Character |
|-------------|-----------|
| **Protector / Guardian** | boundaries, defense, survival instincts. |
| **Dreamer / Visionary** | imagination, purpose, future possibilities. |
| **Caregiver / Nurturer** | compassion, soothing, emotional support. |
| **Performer / Achiever** | ambition, productivity, external validation. |
| **Rebel** | autonomy, resistance, authenticity, disruption of control. |
| **Observer** | detached awareness, mindfulness, meta-reflection. |

## How it works
From the outside, the application behaves like a normal chat: the user asks a question and receives a response.
Internally, however, the personalities debate the question before deciding who gets to answer.

For every message you send:

1. **Debate rounds** — all three personalities react to your input and speak to each other. Each subsequent round they read the full transcript and revise their position.
2. **Judge** — after every round a neutral judge LLM call reads the transcript and decides whether one voice has clearly taken control (activation gap, concessions, coalition) or whether the debate should continue.
3. **Winner speaks** — the judge declares a winner and explains why. That personality delivers the final reply in its own natural voice.

The debate stops either:
when the Judge detects a clear winner,
or after a maximum of 6 rounds.
The full internal discussion and Judge reasoning are visible before the final response.

Each personality exposes:
- `activation` (0–1) — how strongly it feels it should control the response right now
- `to others` — what it says to the other voices in the parliament
- `feels` — its internal emotional state
- `would say` — the answer it wants to give the user

You can also directly address a personality by mentioning it with @.  
Example:  
```text
@Child what are you afraid of here?
```

## Setup

Python 3.14 is required.

```bash
python3.14 -m venv venv
source ./venv/bin/activate
pip install -e .
```

### Environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Free key at [console.groq.com](https://console.groq.com) |
| `MIND_MODEL` | No | LLM model name (default: `llama-3.3-70b-versatile`) |
| `MIND_TEMPERATURE` | No | Sampling temperature (default: `0.2`) |
| `MIND_MAX_ROUNDS` | No | Max debate rounds (default: `6`) |
| `LANGFUSE_PUBLIC_KEY` | No | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | No | Langfuse project secret key |
| `LANGFUSE_HOST` | No | Langfuse server URL (default: `http://localhost:3000`) |

The app loads `.env` automatically on startup — no need to `export` anything manually.

## Observability (optional)

Mind Parliament can trace every debate to [Langfuse](https://langfuse.com) — you see each LLM call, its input/output, latency, and token usage in one timeline.

### Start Langfuse locally

Docker is required.

```bash
docker compose up -d
```

Then open `http://localhost:3000`. On first visit Langfuse asks you to create an account — use any email and password, it's your local instance. Once logged in, create a project and copy the API keys from **Project Settings → API Keys**.

### Configure

```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=http://localhost:3000
```

Tracing is opt-in — if `LANGFUSE_PUBLIC_KEY` is not set the app runs normally without it.

## Run

```bash
mind-simulation
```

Or without installing:

```bash
python main.py
```

## Example session

```
You: I got a promotion offer but I'm not sure I should take it.

────────────────────────────────────────────────────────────────
  inner parliament
────────────────────────────────────────────────────────────────

  ── round 1 ──

  [Teacher]  ████████░░░░  0.82
    to others : We cannot take this. More responsibilities means more chances to fail.
    feels     : anxious, scanning for danger
    would say : Thank you, but I need more time to think.

  [Child]  ██████░░░░░░  0.71
    to others : What if they expect too much and I disappoint everyone?
    feels     : terrified of being seen and found lacking
    would say : I'm not ready for that yet.

  [Self]  █████░░░░░░░  0.48
    to others : This is exactly what we've been working toward. Don't let fear decide.
    feels     : calm but outnumbered
    would say : Yes, I'd love to. When do we start?

  ── round 2 ──

  [Teacher]  █████████░░░  0.88
    to others : Child, you feel it too — this is too much exposure. Self, you're reckless.
    feels     : righteous, closing ranks
    would say : I appreciate the offer, but I need more time.

  [Child]  ███████░░░░░  0.74
    to others : Teacher is right. What if we fail in front of everyone?
    feels     : retreating, looking for cover
    would say : Maybe later, when I'm more ready.

  [Self]  ████░░░░░░░░  0.39
    to others : You're both choosing fear again. This is a pattern, not wisdom.
    feels     : frustrated but losing ground
    would say : I'd love to take it. Let's talk about what support I'd need.

  judge after round 2: Teacher and Child have formed a coalition with activations of
  0.88 and 0.74, while Self has dropped to 0.39 and is not gaining traction.
  The avoidance voices clearly dominate.

────────────────────────────────────────────────────────────────
  Teacher speaks
────────────────────────────────────────────────────────────────

Thank you so much — I'm genuinely flattered. I just want to make sure I can
do it properly, so I'd like a few days to think it over if that's alright.
```

## Project structure

```
main.py                                   entry point
mind_simulation/
  mind.py                                 Mind class + CLI loop
  debate.py                               Debate class (runs rounds, speaks final)
  display.py                              terminal rendering with colours
  config.py                               settings (model, temperature, max_rounds)
  llm.py                                  Groq model factory
  tracing.py                              Langfuse callback setup (opt-in)
  utils.py                                parse_json, render_transcript, scan_folder
  agents/
    judge_agent.py                        Judge class
    sub_personality_agent.py             SubPersonality class
  models/
    debate_state.py                       LangGraph state schema
    judge_verdict.py                      Verdict model
    personality_position.py              Position model
  prompts/
    sub_personality.md                    shared personality framing template
    judge.md                              judge instructions
    sub_personalities/
      child.md                            Child description
      self.md                             Self description
      teacher.md                          Teacher description
    schemas/
      debate.md                           debate-round response schema
      final.md                            final-answer response schema
      direct.md                           direct-reply response schema
docker-compose.yml                        Langfuse + Postgres for local observability
pyproject.toml
```
