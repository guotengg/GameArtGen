from __future__ import annotations

from app.rag import merge_keywords


def enhance_prompt_with_rag(user_input: str, style_docs: list[dict]) -> str:
    base = user_input.strip()
    if not base:
        return ""

    styles = [d["style"] for d in style_docs]
    keywords = merge_keywords([d.get("keywords", []) for d in style_docs], max_size=18)

    quality_tokens = [
        "highly detailed",
        "game concept art",
        "cinematic lighting",
        "sharp focus",
        "4k",
    ]

    parts = [base]
    if styles:
        parts.append(f"style inspired by {', '.join(styles)}")
    if keywords:
        parts.append(", ".join(keywords))
    parts.append(", ".join(quality_tokens))

    return ", ".join(parts)

