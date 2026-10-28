"""Central configuration, read from environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

BACKEND = os.getenv("FOODVERSE_BACKEND", "dummy").lower()  # "hf" or "dummy"
HF_MODEL = os.getenv("FOODVERSE_HF_MODEL", "nateraw/food")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
HYGIENE_YOLO_WEIGHTS = os.getenv("HYGIENE_YOLO_WEIGHTS", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
