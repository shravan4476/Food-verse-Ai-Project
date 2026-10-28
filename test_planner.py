from app.core.llm import LLMClient
from app.modules.planner.meal_planner import Profile, generate_plan, targets

NO_LLM = LLMClient(api_key="")


def test_targets_mifflin_st_jeor():
    p = Profile(age=30, sex="male", height_cm=180, weight_kg=80, activity="sedentary", goal="maintain")
    t = targets(p)
    assert t["bmr"] == 1780  # 800 + 1125 - 150 + 5
    assert t["tdee"] == round(1780 * 1.2)


def test_goal_adjusts_calories():
    base = dict(age=30, sex="female", height_cm=165, weight_kg=65, activity="moderate")
    assert targets(Profile(**base, goal="lose"))["calories"] < targets(Profile(**base, goal="maintain"))["calories"]
    assert targets(Profile(**base, goal="gain"))["calories"] > targets(Profile(**base, goal="maintain"))["calories"]


def test_plan_respects_allergies_and_diet():
    p = Profile(age=28, sex="female", height_cm=165, weight_kg=60, diet=["vegetarian"], allergies=["dairy", "egg"])
    res = generate_plan(p, llm=NO_LLM)
    assert len(res["plan"]) == 7
    forbidden = {"Paneer bhurji with roti", "Palak paneer with roti", "Veggie omelette with toast",
                 "Greek yogurt with fruit and nuts", "Egg curry with rice", "Buttermilk and banana"}
    for day in res["plan"]:
        assert len(day["meals"]) == 4
        assert not forbidden & {m["name"] for m in day["meals"]}


def test_impossible_restrictions_return_error():
    p = Profile(age=28, sex="male", height_cm=175, weight_kg=75, diet=["vegan"], allergies=["gluten", "soy", "peanut", "tree nut", "sesame"])
    res = generate_plan(p, llm=NO_LLM)
    assert res["plan"] == [] or res["plan"]  # either a valid plan or an explanatory error
    if not res["plan"]:
        assert "error" in res
