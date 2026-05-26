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
You: should I play the video game or do the dishes?

────────────────────────────────────────────────────────────────
  Inner crowd
────────────────────────────────────────────────────────────────

  ── round 1 ──

  [Child]  ██████████░░  0.80
    to others  : I really want to play the video game, it looks so much fun
    feels      : excitement and a little bit of guilt
    would say  : Can I please play the video game for a little bit and then I'll do the dishes, I promise

  [Critic]  ██████████░░  0.80
    to others  : Let's think this through, doing the dishes needs to be done and putting it off will only make it worse, but playing the video game can be a nice break
    feels      : anxiety about the dishes piling up and guilt about procrastinating
    would say  : I should do the dishes first, it's not the most exciting task, but it's the responsible thing to do and it'll be better to get it out of the way

  [Self]  ████████░░░░  0.70
    to others  : Let's take a moment to consider what needs to be done and what we really want to do.
    feels      : a sense of responsibility mixed with a desire to relax
    would say  : Why don't I do the dishes first and then reward myself with some time playing the video game?

  ── round 2 ──

  [Child]  ███████████░  0.90
    to others  : I don't want to do the dishes, it's so boring and I was really looking forward to playing the game
    feels      : excitement and a little bit of fear that I'll get in trouble for not doing the dishes
    would say  : can't I just play the game for a little bit and then do the dishes later?

  [Critic]  ███████████░  0.90
    to others  : Let's not forget about the dishes, they're not going to do themselves and it's only going to get worse if we put it off
    feels      : a sense of unease and responsibility
    would say  : Let's do the dishes first, it's not going to take that long and then we can play the video game without feeling guilty or worried about the mess

  [Self]  ██████████░░  0.85
    to others  : Let's weigh the importance of both tasks and consider how they align with our current needs and priorities.
    feels      : A sense of balance and responsibility, with a hint of temptation to indulge in the video game.
    would say  : Why don't we do the dishes first and then reward ourselves with some time playing the video game, that way we can feel responsible and also have some fun.

  ── round 3 ──

  [Child]  ███████████░  0.95
    to others  : I really don't want to do the dishes, it's so boring and I was really looking forward to playing the game
    feels      : I feel frustrated and disappointed that I might have to put off playing the game
    would say  : Can't I just play the game for a little while and then do the dishes later, please?

  [Critic]  ███████████░  0.95
    to others  : Let's not rush into playing the game, we need to consider the consequences of leaving the dishes undone
    feels      : Anxiety about the potential mess and stress of delaying the dishes
    would say  : Let's do the dishes first, it's a responsible thing to do and will save us from more trouble later

  [Self]  ███████████░  0.92
    to others  : Let's find a balance between responsibility and enjoyment, perhaps we can do the dishes first and then play the video game as a reward
    feels      : A sense of calm and fairness, trying to mediate between the desire for fun and the need for responsibility
    would say  : Why don't we compromise and do the dishes first, then we can play the video game without feeling guilty or overwhelmed by the mess?

  Judge after round 3: Self's activation is high and its suggestion to find a balance between responsibility and enjoyment has addressed the key tension between the Child's desire to play and the need to do the dishes.

────────────────────────────────────────────────────────────────
  Self speaks
────────────────────────────────────────────────────────────────

Let's do the dishes first, it's not the most exciting task, but getting it out of the way will actually make playing the video game more enjoyable, and we can do it without feeling guilty or worried about the mess. Plus, it's a good way to clear our head and make some space before diving into the game. Once the dishes are done, we can fully focus on having fun and relaxing with the game.
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
