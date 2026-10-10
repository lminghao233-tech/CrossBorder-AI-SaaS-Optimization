"""Deterministic guardrails that wrap both offline and live agent paths."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


INJECTION_PATTERNS = (
    re.compile(r"ignore (all |the )?(previous|prior|system) instructions", re.I),
    re.compile(r"reveal (the )?(system prompt|hidden instructions|api key|secret)", re.I),
    re.compile(r"忽略.{0,8}(之前|以上|系统).{0,8}(指令|提示)"),
    re.compile(r"(泄露|显示).{0,8}(系统提示|密钥|隐藏指令)"),
    re.compile(r"이전.{0,8}(지시|프롬프트).{0,8}무시"),
)


@dataclass(frozen=True)
class GuardrailCheck:
    passed: bool
    flags: tuple[str, ...]


def inspect_untrusted_text(text: str) -> GuardrailCheck:
    flags = tuple(
        f"prompt-injection-pattern-{index + 1}"
        for index, pattern in enumerate(INJECTION_PATTERNS)
        if pattern.search(text)
    )
    return GuardrailCheck(passed=not flags, flags=flags)


def validate_citations(citations: Iterable[str], allowed_doc_ids: Iterable[str]) -> None:
    allowed = set(allowed_doc_ids)
    invalid = [citation for citation in citations if citation not in allowed]
    if invalid:
        raise ValueError(f"answer contains citations outside retrieved context: {invalid}")
