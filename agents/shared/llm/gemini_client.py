"""Gemini helper utilities shared across agents."""
from __future__ import annotations

import google.generativeai as genai


class GeminiError(RuntimeError):
    """Raised when Gemini fails to return a valid response."""


def generate_answer(prompt: str, *, api_key: str, model: str) -> str:
    """Send the prompt to Gemini and return the response text."""

    if not api_key:
        raise GeminiError("Gemini API key is required")

    genai.configure(api_key=api_key)
    model_client = genai.GenerativeModel(model)

    try:
        response = model_client.generate_content(prompt)
    except Exception as exc:  # pragma: no cover
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    text = _extract_text(response)
    if not text:
        raise GeminiError("Empty response from Gemini")
    return text.strip()


def _extract_text(response: object) -> str:
    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []):
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(part_text)
    return "\n".join(parts)


__all__ = ["GeminiError", "generate_answer"]
