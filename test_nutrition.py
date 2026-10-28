from app.modules.food_recognition.nutrition import estimate, normalize


def test_known_food_default_serving():
    r = estimate("pizza")
    assert r["found"] and r["grams"] == 200
    assert r["calories"] == 532.0  # 266 kcal/100g * 2


def test_portion_scaling_and_label_normalisation():
    r = estimate("French_Fries", 50)
    assert r["found"] and r["calories"] == 156.0
    assert normalize("Apple_Pie") == "apple pie"


def test_unknown_food():
    assert estimate("moon cheese")["found"] is False
