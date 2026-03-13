from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_FILE = DATA_DIR / "style_knowledge.json"
HISTORY_FILE = DATA_DIR / "history.jsonl"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"

TOP_K = int(os.getenv("GAG_TOP_K", "3"))
USE_SD = os.getenv("GAG_USE_SD", "1") == "1"
SD_STRICT = os.getenv("GAG_SD_STRICT", "0") == "1"
SD_MODEL_ID = os.getenv("GAG_SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
SD_STEPS = int(os.getenv("GAG_SD_STEPS", "30"))
SD_GUIDANCE = float(os.getenv("GAG_SD_GUIDANCE", "7.5"))
DEFAULT_NEGATIVE_PROMPT = os.getenv(
    "GAG_NEGATIVE_PROMPT", "blurry, low quality, ugly, deformed"
)
