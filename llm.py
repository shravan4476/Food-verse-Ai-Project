"""Optional LLM reasoning layer. Returns None when no API key is configured so callers can fall back."""
from __future__ import annotations

from app import config


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key if api_key is not None else config.ANTHROPIC_API_KEY
        self.model = model or config.ANTHROPIC_MODEL

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def complete(self, system: str, prompt: str, max_tokens: int = 800) -> str | None:
        if not self.available:
            return None
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            msg = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        except Exception:  # network/auth errors must never break the app
            return None
