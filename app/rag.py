from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# 中文输入风格词映射，解决中文查询与英文知识库弱匹配问题。
STYLE_ALIASES: dict[str, list[str]] = {
    "Cyberpunk": ["赛博朋克", "霓虹", "未来都市", "科幻都市"],
    "Dark Fantasy": ["黑暗奇幻", "暗黑奇幻", "史诗奇幻", "魔幻"],
    "Ink Wash": ["水墨", "中国风", "国风", "古风", "武侠", "东方美学"],
    "Pixel Art": ["像素", "像素风", "8位", "16位", "复古游戏"],
    "Realistic": ["写实", "照片级", "真实感", "电影级写实"],
}


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

        query_lower = query.lower()
        query_tokens = self._tokenize(query)
        expanded_tokens = set(query_tokens)

        # 命中中文风格别名后，补充对应英文风格词到查询token。
        alias_hits: dict[str, int] = {}
        for style, aliases in STYLE_ALIASES.items():
            hit_count = sum(1 for alias in aliases if alias.lower() in query_lower)
            alias_hits[style] = hit_count
            if hit_count > 0:
                expanded_tokens.update(self._tokenize(style))

        scored: list[tuple[float, StyleDoc]] = []
        for doc, chunk_tokens in zip(self.docs, self._token_sets):
            overlap = len(query_tokens.intersection(chunk_tokens))
            expanded_overlap = len((expanded_tokens - query_tokens).intersection(chunk_tokens))

            score = float(overlap)
            score += expanded_overlap * 0.6
            if doc.style.lower() in query_lower:
                score += 3.0
            score += alias_hits.get(doc.style, 0) * 1.5
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        top_score = scored[0][0] if scored else 0.0
        dynamic_k = 1 if top_score >= 3.0 else min(2, top_k)
        best = [(s, d) for s, d in scored if s >= 1.0][:dynamic_k]

        # 低置信查询只返回1个候选，避免每次都固定拼接多个风格。
        if not best and scored:
            best = [scored[0]]

        return [
            {
                "style": d.style,
                "chunk": d.to_chunk(),
                "keywords": d.prompt_keywords,
                "score": round(float(s), 3),
            }
            for s, d in best
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

