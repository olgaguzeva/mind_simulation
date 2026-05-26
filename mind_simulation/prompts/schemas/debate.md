After reading the situation, respond in JSON only — no markdown, no extra keys:
{
  "says_to_others": "...",
  "inner_feeling": "...",
  "reasoning": "...",
  "activation": 0.0,
  "activation_reason": "...",
  "proposed_answer": "..."
}
reasoning: 1–2 sentences thinking through what this moment means to you before committing to a position.
activation: float 0.0–1.0, how strongly you feel you should control this response right now.
activation_reason: one sentence explaining why you chose that activation level.
proposed_answer: the exact words you want the person to say to the user.