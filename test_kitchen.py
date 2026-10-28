from app.core.llm import LLMClient
from app.modules.kitchen.assistant import guide, suggest_recipes


def test_suggest_ranks_by_overlap():
    s = suggest_recipes(["paneer", "spinach", "roti"])
    assert s and s[0]["name"] == "Palak paneer with roti"
    assert s[0]["match"] == 1.0


def test_suggest_no_match():
    assert suggest_recipes(["dragonfruit"]) == []


def test_guide_fallback_has_timers():
    g = guide("dal tadka", llm=LLMClient(api_key=""))
    assert g["source"] == "fallback" and len(g["steps"]) >= 4
    assert any(s["timer_seconds"] for s in g["steps"])
