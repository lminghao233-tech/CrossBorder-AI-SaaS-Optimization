"""Minimal deterministic PII masking used before routing or external calls."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MaskResult:
    text: str
    replacements: dict[str, str]


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{7,}\d)(?!\d)")),
    ("ORDER", re.compile(r"(?i)\b(?:order|订单|주문)\s*[#：:]?\s*[A-Z0-9-]{5,}\b")),
)


def mask_pii(text: str) -> MaskResult:
    """Replace supported PII with typed stable placeholders.

    The function intentionally keeps the mapping in memory only. Production
    deployments should add tenant-specific policies and secure lifecycle rules.
    """

    masked = text
    replacements: dict[str, str] = {}
    counters: dict[str, int] = {}

    for kind, pattern in _PATTERNS:
        def replace(match: re.Match[str], *, _kind: str = kind) -> str:
            value = match.group(0)
            if value.startswith("[") and value.endswith("]"):
                return value
            counters[_kind] = counters.get(_kind, 0) + 1
            placeholder = f"[{_kind}_{counters[_kind]}]"
            replacements[placeholder] = value
            return placeholder

        masked = pattern.sub(replace, masked)

    return MaskResult(text=masked, replacements=replacements)

