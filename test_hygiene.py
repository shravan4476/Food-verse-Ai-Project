from app.modules.hygiene.monitor import evaluate


def test_full_compliance():
    full = {"gloves", "hairnet", "apron", "mask"}
    r = evaluate([(0, full), (2, full)])
    assert r.compliance_score == 100.0 and r.violations == []


def test_violations_and_per_item_scores():
    full = {"gloves", "hairnet", "apron", "mask"}
    r = evaluate([(0, full), (2, {"apron", "mask"}), (4, full), (6, full)])
    assert r.compliance_score == 75.0
    assert r.violations == [{"timestamp_s": 2.0, "missing": ["gloves", "hairnet"]}]
    assert r.per_item_compliance["gloves"] == 75.0 and r.per_item_compliance["apron"] == 100.0


def test_no_frames_and_unconfigured_detector():
    assert evaluate([]).frames_analyzed == 0
    r = evaluate([(0, set())], detector_configured=False)
    assert r.compliance_score == 0.0 and "No PPE detector" in r.note
