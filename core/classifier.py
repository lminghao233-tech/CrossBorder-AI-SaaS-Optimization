"""Transparent multilingual intent classification for the portfolio demo."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "intent_keywords.json"


@dataclass(frozen=True)
class Classification:
    intent: str
    risk: str
    confidence: float
    language: str
    matched_keywords: tuple[str, ...]


def detect_language(text: str) -> str:
    if re.search(r"[가-힣]", text):
        return "ko"
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    return "en"


class IntentClassifier:
    def __init__(self, config_path: Path | None = None) -> None:
        path = config_path or CONFIG_PATH
        self.config = json.loads(path.read_text(encoding="utf-8"))

    def classify(self, text: str) -> Classification:
        normalized = text.casefold()
        candidates: list[tuple[int, int, str, dict, tuple[str, ...]]] = []
        risk_rank = {"routine": 0, "complex": 1, "high": 2}

        for intent, spec in self.config["intents"].items():
            matched = tuple(k for k in spec["keywords"] if k.casefold() in normalized)
            if matched:
                candidates.append(
                    (len(matched), risk_rank[spec["risk"]], intent, spec, matched)
                )

        if not candidates:
            return Classification(
                intent="unknown",
                risk="complex",
                confidence=0.35,
                language=detect_language(text),
                matched_keywords=(),
            )

        # More keyword evidence wins; equal evidence is resolved conservatively.
        candidates.sort(reverse=True)
        score, _, intent, spec, matched = candidates[0]
        tied = [item for item in candidates if item[0] == score]
        if len(tied) > 1:
            tied.sort(key=lambda item: item[1], reverse=True)
            score, _, intent, spec, matched = tied[0]
            confidence = 0.62
        else:
            confidence = min(0.96, 0.78 + 0.08 * (score - 1))

        return Classification(
            intent=intent,
            risk=spec["risk"],
            confidence=round(confidence, 2),
            language=detect_language(text),
            matched_keywords=matched,
        )

