import io

import numpy as np
from PIL import Image

from app.modules.freshness.detector import FreshnessDetector


def _png(arr) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr.astype("uint8")).save(buf, format="PNG")
    return buf.getvalue()


def test_bright_red_image_is_fresh():
    arr = np.zeros((64, 64, 3)); arr[..., 0] = 220; arr[..., 1] = 40; arr[..., 2] = 40
    r = FreshnessDetector().analyze(_png(arr))
    assert r["label"] == "fresh" and r["freshness_score"] >= 75


def test_dark_brown_image_scores_low():
    arr = np.zeros((64, 64, 3)); arr[..., 0] = 70; arr[..., 1] = 40; arr[..., 2] = 15
    r = FreshnessDetector().analyze(_png(arr))
    assert r["label"] != "fresh" and r["freshness_score"] < 75
    assert r["reasons"]


def test_custom_model_hook():
    arr = np.full((32, 32, 3), 128)
    r = FreshnessDetector(model=lambda img: 12.0).analyze(_png(arr))
    assert r["method"] == "custom_model" and r["label"] == "likely_spoiled"
