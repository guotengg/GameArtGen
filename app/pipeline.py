from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app import config
from app.image_generator import get_image_generator, image_to_base64_png
from app.prompt_enhancer import enhance_prompt_with_rag
from app.rag import StyleKnowledgeBase


class GameArtPipeline:
    def __init__(self) -> None:
        self.kb = StyleKnowledgeBase.from_json(config.KNOWLEDGE_FILE)
        self.image_generator = get_image_generator()
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def generate(self, user_input: str, negative_prompt: str | None = None) -> dict:
        if not user_input or not user_input.strip():
            raise ValueError("description is required")

        sources = self.kb.retrieve(user_input, top_k=config.TOP_K)
        enhanced = enhance_prompt_with_rag(user_input, sources)
        image = self.image_generator.generate(
            prompt=enhanced,
            negative_prompt=negative_prompt or config.DEFAULT_NEGATIVE_PROMPT,
        )
        image_b64 = image_to_base64_png(image)

        result = {
            "description": user_input,
            "enhanced_prompt": enhanced,
            "sources": [s["style"] for s in sources],
            "backend": getattr(self.image_generator, "backend", "unknown"),
            "model_id": getattr(self.image_generator, "model_id", "unknown"),
            "device": getattr(self.image_generator, "device", "unknown"),
            "image": image_b64,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_jsonl(config.HISTORY_FILE, result)
        return result

    def list_history(self, limit: int = 20) -> list[dict]:
        if not config.HISTORY_FILE.exists():
            return []
        lines = config.HISTORY_FILE.read_text(encoding="utf-8").splitlines()
        items = [json.loads(line) for line in lines if line.strip()]
        return list(reversed(items[-limit:]))

    def save_feedback(self, enhanced_prompt: str, vote: str) -> None:
        payload = {
            "enhanced_prompt": enhanced_prompt,
            "vote": vote,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_jsonl(config.FEEDBACK_FILE, payload)

    @staticmethod
    def _append_jsonl(file_path: Path, obj: dict) -> None:
        with file_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
