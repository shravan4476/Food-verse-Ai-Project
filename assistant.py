"""Epic 4 - smart cooking assistant: ingredient-based suggestions and step-by-step guidance with timers."""
from __future__ import annotations

import json
import re

from app.config import DATA_DIR
from app.core.llm import LLMClient

SYSTEM = (
    "You are a careful cooking assistant. Be concise, give safe cooking temperatures and times, "
    "and mention allergens when relevant."
)


def _recipes() -> list[dict]:
    with open(DATA_DIR / "recipes.json", encoding="utf-8") as f:
        return json.load(f)


def suggest_recipes(ingredients: list[str], limit: int = 5) -> list[dict]:
    """Rank catalog recipes by ingredient overlap."""
    have = {i.strip().lower() for i in ingredients if i.strip()}
    scored = []
    for r in _recipes():
        needed = [i.lower() for i in r["ingredients"]]
        hits = [n for n in needed if any(h in n or n in h for h in have)]
        if hits:
            scored.append(
                {
                    "name": r["name"],
                    "match": round(len(hits) / len(needed), 2),
                    "have": hits,
                    "missing": [n for n in needed if n not in hits],
                    "calories": r["calories"],
                }
            )
    scored.sort(key=lambda x: (-x["match"], x["missing"].__len__()))
    return scored[:limit]


def _fallback_steps(dish: str) -> list[dict]:
    return [
        {"step": 1, "instruction": f"Wash hands and prep all ingredients for {dish}.", "timer_seconds": None},
        {"step": 2, "instruction": "Heat oil in a pan over medium heat.", "timer_seconds": 120},
        {"step": 3, "instruction": "Cook aromatics (onion, garlic, spices) until fragrant.", "timer_seconds": 180},
        {"step": 4, "instruction": "Add main ingredients and cook until done; check internal temperature for meat (74 C / 165 F for poultry).", "timer_seconds": 600},
        {"step": 5, "instruction": "Season, rest for a minute, and serve.", "timer_seconds": 60},
    ]


def guide(dish: str, servings: int = 2, llm: LLMClient | None = None) -> dict:
    llm = llm or LLMClient()
    text = llm.complete(
        SYSTEM,
        f"Give numbered cooking steps for {dish} ({servings} servings). One step per line, "
        "and end a line with '[timer: N min]' when the step needs timing.",
    )
    if not text:
        return {"dish": dish, "source": "fallback", "steps": _fallback_steps(dish)}

    steps = []
    for line in text.splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s*(.+)$", line)
        if not m:
            continue
        t = re.search(r"\[timer:\s*(\d+)\s*min\]", m.group(2), re.I)
        steps.append(
            {
                "step": int(m.group(1)),
                "instruction": re.sub(r"\s*\[timer:.*?\]", "", m.group(2), flags=re.I).strip(),
                "timer_seconds": int(t.group(1)) * 60 if t else None,
            }
        )
    return {"dish": dish, "source": "llm", "steps": steps or _fallback_steps(dish)}
