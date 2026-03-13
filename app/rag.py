from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class StyleDoc:
    style: str
    description: str
    prompt_keywords: list[str]
    color_palette: str
    lighting: str
    composition: str

    def to_chunk(self) -> str:
        return (
            f"Style: {self.style}. "
            f"Description: {self.description}. "
            f"Keywords: {', '.join(self.prompt_keywords)}. "
            f"Color palette: {self.color_palette}. "
            f"Lighting: {self.lighting}. "
            f"Composition: {self.composition}."
        )


class StyleKnowledgeBase:
    def __init__(self, docs: list[StyleDoc]):
        self.docs = docs
        self._chunks = [d.to_chunk() for d in docs]
        self._token_sets = [self._tokenize(chunk) for chunk in self._chunks]

    @classmethod
    def from_json(cls, file_path: Path) -> "StyleKnowledgeBase":
        data = json.loads(file_path.read_text(encoding="utf-8"))
        docs = [StyleDoc(**item) for item in data]
        return cls(docs)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if not query.strip():
            return []

        query_tokens = self._tokenize(query)
        scored = []
        for doc, chunk_tokens in zip(self.docs, self._token_sets):
            overlap = len(query_tokens.intersection(chunk_tokens))
            # 轻量分数：词重叠 + 风格名匹配
            if doc.style.lower() in query.lower():
                overlap += 2
            scored.append((overlap, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = [doc for score, doc in scored if score > 0][:top_k]

        if not best:
            best = [doc for _, doc in scored[:top_k]]

        return [
            {
                "style": d.style,
                "chunk": d.to_chunk(),
                "keywords": d.prompt_keywords,
            }
            for d in best
        ]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z0-9_\-\u4e00-\u9fff]+", text.lower())
        return {w for w in words if len(w) > 1}


def merge_keywords(items: Iterable[list[str]], max_size: int = 20) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for group in items:
        for word in group:
            norm = word.strip().lower()
            if norm and norm not in seen:
                seen.add(norm)
                merged.append(norm)
            if len(merged) >= max_size:
                return merged
    return merged

