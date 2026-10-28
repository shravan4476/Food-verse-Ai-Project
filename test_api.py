import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _img() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 30, 30)).save(buf, format="PNG")
    return buf.getvalue()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_recognize_dummy_backend():
    r = client.post("/api/food/recognize", files={"file": ("a.png", _img(), "image/png")})
    assert r.status_code == 200
    body = r.json()
    assert body["predictions"][0]["label"] == "pizza" and body["nutrition"]["found"]


def test_freshness_endpoint():
    r = client.post("/api/freshness/analyze", files={"file": ("a.png", _img(), "image/png")})
    assert r.status_code == 200 and "freshness_score" in r.json()


def test_planner_endpoint_and_validation():
    ok = client.post("/api/planner/generate", json={"age": 30, "sex": "male", "height_cm": 175, "weight_kg": 70})
    assert ok.status_code == 200 and len(ok.json()["plan"]) == 7
    bad = client.post("/api/planner/generate", json={"age": 5, "sex": "male", "height_cm": 175, "weight_kg": 70})
    assert bad.status_code == 422


def test_kitchen_endpoints():
    s = client.post("/api/kitchen/suggest", json={"ingredients": ["rice", "dal"]})
    assert s.status_code == 200 and s.json()["suggestions"]
    g = client.post("/api/kitchen/guide", json={"dish": "khichdi"})
    assert g.status_code == 200 and g.json()["steps"]


def test_empty_upload_rejected():
    r = client.post("/api/freshness/analyze", files={"file": ("a.png", b"", "image/png")})
    assert r.status_code == 400
