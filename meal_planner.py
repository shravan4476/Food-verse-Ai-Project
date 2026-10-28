"""Epic 5 - personalized meal planner: BMR -> TDEE -> targets -> 7-day plan from the recipe catalog."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from app.config import DATA_DIR
from app.core.llm import LLMClient

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
GOAL_ADJ = {"lose": -0.20, "maintain": 0.0, "gain": 0.15}
MACRO_SPLIT = {  # protein, carbs, fat as fraction of calories
    "lose": (0.30, 0.40, 0.30),
    "maintain": (0.25, 0.50, 0.25),
    "gain": (0.25, 0.50, 0.25),
}
MEAL_SHARE = {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class Profile:
    age: int
    sex: str  # "male" | "female"
    height_cm: float
    weight_kg: float
    activity: str = "moderate"
    goal: str = "maintain"
    diet: list[str] = field(default_factory=list)  # tags required, e.g. ["vegetarian"]
    allergies: list[str] = field(default_factory=list)  # allergens to avoid, e.g. ["dairy"]


def bmr(p: Profile) -> float:
    """Mifflin-St Jeor equation."""
    base = 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age
    return base + (5 if p.sex.lower() == "male" else -161)


def targets(p: Profile) -> dict:
    tdee = bmr(p) * ACTIVITY.get(p.activity, 1.55)
    cal = tdee * (1 + GOAL_ADJ.get(p.goal, 0.0))
    cal = max(cal, 1200 if p.sex.lower() != "male" else 1500)  # safety floor
    pr, cr, fr = MACRO_SPLIT.get(p.goal, MACRO_SPLIT["maintain"])
    return {
        "bmr": round(bmr(p)),
        "tdee": round(tdee),
        "calories": round(cal),
        "protein_g": round(cal * pr / 4),
        "carbs_g": round(cal * cr / 4),
        "fat_g": round(cal * fr / 9),
    }


def _catalog() -> list[dict]:
    with open(DATA_DIR / "recipes.json", encoding="utf-8") as f:
        return json.load(f)


def eligible(recipes: list[dict], p: Profile) -> list[dict]:
    allergies = {a.lower() for a in p.allergies}
    diet = {d.lower() for d in p.diet}
    out = []
    for r in recipes:
        if allergies & {a.lower() for a in r["allergens"]}:
            continue
        if diet and not diet <= {t.lower() for t in r["tags"]}:
            continue
        out.append(r)
    return out


def generate_plan(p: Profile, llm: LLMClient | None = None) -> dict:
    t = targets(p)
    pool = eligible(_catalog(), p)
    by_meal = {m: [r for r in pool if r["meal"] == m] for m in MEAL_SHARE}
    missing = [m for m, rs in by_meal.items() if not rs]
    if missing:
        return {
            "targets": t,
            "plan": [],
            "error": f"No recipes match your restrictions for: {', '.join(missing)}. Expand data/recipes.json.",
        }

    plan, used = [], {m: 0 for m in MEAL_SHARE}
    for day in DAYS:
        meals, total = [], 0
        for m, share in MEAL_SHARE.items():
            goal_cal = t["calories"] * share
            # prefer recipes closest to the calorie goal; rotate to avoid repeats
            ranked = sorted(by_meal[m], key=lambda r: (abs(r["calories"] - goal_cal) + 40 * ((used.get(r["name"], 0)))))
            pick = ranked[0]
            used[pick["name"]] = used.get(pick["name"], 0) + 1
            meals.append({"meal": m, **{k: pick[k] for k in ("name", "calories", "protein_g", "carbs_g", "fat_g", "ingredients")}})
            total += pick["calories"]
        plan.append(
            {
                "day": day,
                "meals": meals,
                "total_calories": total,
                "protein_g": sum(x["protein_g"] for x in meals),
                "carbs_g": sum(x["carbs_g"] for x in meals),
                "fat_g": sum(x["fat_g"] for x in meals),
                "vs_target_pct": round(100 * total / t["calories"], 1),
            }
        )

    summary = (llm or LLMClient()).complete(
        "You are a supportive nutrition coach. Be brief and non-judgemental; you are not a doctor.",
        f"Targets: {t}. Goal: {p.goal}. Restrictions: {p.diet + p.allergies}. "
        "Write 3 sentences explaining this plan and one tip.",
    )
    return {
        "targets": t,
        "plan": plan,
        "summary": summary
        or f"Daily target is about {t['calories']} kcal ({t['protein_g']} g protein, {t['carbs_g']} g carbs, "
        f"{t['fat_g']} g fat) for your goal to {p.goal} weight.",
        "disclaimer": "General guidance, not medical advice. Consult a professional for medical conditions.",
    }
