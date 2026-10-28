"""Epic 3 - explainable freshness / spoilage analysis from colour and texture cues.

This is a heuristic baseline. To use a trained CNN, assign a callable to `FreshnessDetector.model`
that takes a PIL image and returns a freshness score in [0, 100].
"""
from __future__ import annotations

import io
from typing import Callable, Optional

import numpy as np
from PIL import Image


class FreshnessDetector:
    def __init__(self, model: Optional[Callable[[Image.Image], float]] = None):
        self.model = model

    @staticmethod
    def _features(img: Image.Image) -> dict:
        img = img.convert("RGB")
        img.thumbnail((256, 256))
        hsv = np.asarray(img.convert("HSV"), dtype=np.float32) / 255.0
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        gray = np.asarray(img.convert("L"), dtype=np.float32) / 255.0

        dark = float(np.mean(v < 0.25))  # dark patches / rot
        # brown/orange-dark hues (~15-45 degrees) with low-mid brightness indicate browning
        hue_deg = h * 360.0
        browning = float(np.mean((hue_deg > 15) & (hue_deg < 45) & (v < 0.55) & (s > 0.25)))
        dullness = float(1.0 - np.clip(np.mean(s) / 0.6, 0, 1))  # low saturation = dull
        gx = np.abs(np.diff(gray, axis=1)).mean()
        gy = np.abs(np.diff(gray, axis=0)).mean()
        texture_noise = float(np.clip((gx + gy) / 0.12, 0, 1))
        return {"dark": dark, "browning": browning, "dullness": dullness, "texture_noise": texture_noise}

    def analyze(self, image_bytes: bytes) -> dict:
        img = Image.open(io.BytesIO(image_bytes))
        f = self._features(img)
        reasons: list[str] = []

        if self.model is not None:
            score = float(np.clip(self.model(img), 0, 100))
            method = "custom_model"
        else:
            penalty = 100 * (0.9 * f["dark"] + 0.9 * f["browning"] + 0.25 * f["dullness"] + 0.15 * f["texture_noise"])
            score = float(np.clip(100 - penalty, 0, 100))
            method = "colour_texture_heuristic"

        if f["dark"] > 0.08:
            reasons.append(f"Dark patches cover about {f['dark']*100:.0f}% of the image (possible rot or mould).")
        if f["browning"] > 0.10:
            reasons.append(f"Browning detected in about {f['browning']*100:.0f}% of the image.")
        if f["dullness"] > 0.6:
            reasons.append("Colours look dull / desaturated, which can indicate ageing.")
        if f["texture_noise"] > 0.6:
            reasons.append("Irregular surface texture (wrinkling or spots).")
        if not reasons:
            reasons.append("No visible spoilage cues found.")

        if score >= 75:
            label, advice = "fresh", "Looks fresh."
        elif score >= 45:
            label, advice = "use_soon", "Showing signs of ageing; use soon and check smell/texture."
        else:
            label, advice = "likely_spoiled", "Likely spoiled; discard if it smells off or feels slimy."

        return {
            "freshness_score": round(score, 1),
            "label": label,
            "advice": advice,
            "reasons": reasons,
            "method": method,
            "features": {k: round(v, 3) for k, v in f.items()},
            "disclaimer": "Visual estimate only, not a food-safety certification. When in doubt, throw it out.",
        }
