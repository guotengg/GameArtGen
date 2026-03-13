from __future__ import annotations

from app.rag import merge_keywords


def enhance_prompt_with_rag(user_input: str, style_docs: list[dict]) -> str:
    base = user_input.strip()
    if not base:
        return ""

    high_conf_styles = [d["style"] for d in style_docs if d.get("score", 0) >= 2.0]
    fallback_styles = [d["style"] for d in style_docs[:1]]
    styles = high_conf_styles or fallback_styles

    keyword_docs = [d for d in style_docs if d.get("score", 0) >= 1.0]
    if not keyword_docs and style_docs:
        keyword_docs = [style_docs[0]]
    keywords = merge_keywords([d.get("keywords", []) for d in keyword_docs], max_size=12)

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
