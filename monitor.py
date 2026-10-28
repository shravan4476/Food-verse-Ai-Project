"""Epic 4 - restaurant hygiene monitoring: frame sampling, pluggable PPE detector, rules engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

from app import config

DEFAULT_REQUIRED = ("gloves", "hairnet", "apron", "mask")


class PPEDetector(Protocol):
    def detect(self, frame) -> set[str]:
        """Return the set of PPE labels present in the frame (e.g. {'gloves', 'apron'})."""


class NullDetector:
    """Used when no weights are configured: reports nothing so the UI can explain why."""

    configured = False

    def detect(self, frame) -> set[str]:
        return set()


class YoloDetector:
    configured = True

    def __init__(self, weights: str, conf: float = 0.4):
        try:
            from ultralytics import YOLO
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("Install ultralytics to use YOLO weights: pip install ultralytics") from e
        self.model = YOLO(weights)
        self.conf = conf

    def detect(self, frame) -> set[str]:  # pragma: no cover - needs weights
        res = self.model.predict(frame, conf=self.conf, verbose=False)[0]
        return {res.names[int(c)].lower() for c in res.boxes.cls}


def default_detector() -> PPEDetector:
    if config.HYGIENE_YOLO_WEIGHTS:
        return YoloDetector(config.HYGIENE_YOLO_WEIGHTS)
    return NullDetector()


@dataclass
class HygieneReport:
    compliance_score: float
    frames_analyzed: int
    per_item_compliance: dict
    violations: list = field(default_factory=list)
    detector_configured: bool = True
    note: str = ""


def evaluate(
    detections: Iterable[tuple[float, set[str]]],
    required: tuple[str, ...] = DEFAULT_REQUIRED,
    detector_configured: bool = True,
) -> HygieneReport:
    """Rules engine. `detections` is an iterable of (timestamp_seconds, set_of_ppe_labels)."""
    detections = list(detections)
    n = len(detections)
    if n == 0:
        return HygieneReport(0.0, 0, {r: 0.0 for r in required}, [], detector_configured, "No frames analyzed.")

    counts = {r: 0 for r in required}
    violations = []
    fully_compliant = 0
    for ts, present in detections:
        missing = [r for r in required if r not in present]
        for r in required:
            if r in present:
                counts[r] += 1
        if missing:
            violations.append({"timestamp_s": round(ts, 1), "missing": missing})
        else:
            fully_compliant += 1

    note = "" if detector_configured else (
        "No PPE detector configured (set HYGIENE_YOLO_WEIGHTS); score is not meaningful."
    )
    return HygieneReport(
        compliance_score=round(100.0 * fully_compliant / n, 1),
        frames_analyzed=n,
        per_item_compliance={r: round(100.0 * counts[r] / n, 1) for r in required},
        violations=violations,
        detector_configured=detector_configured,
        note=note,
    )


def sample_video(path: str, every_seconds: float = 2.0, max_frames: int = 120):
    """Yield (timestamp_s, frame_bgr) sampled from a video file. Requires OpenCV."""
    try:
        import cv2
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("OpenCV not installed. Run `pip install -r requirements.txt`.") from e
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(int(fps * every_seconds), 1)
    idx = yielded = 0
    while yielded < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            yield idx / fps, frame
            yielded += 1
        idx += 1
    cap.release()


def analyze_video(path: str, detector: PPEDetector | None = None, required=DEFAULT_REQUIRED,
                  every_seconds: float = 2.0) -> HygieneReport:
    detector = detector or default_detector()
    dets = ((ts, detector.detect(frame)) for ts, frame in sample_video(path, every_seconds))
    return evaluate(dets, required, getattr(detector, "configured", True))
