"""Risk-first model router with a CLI demonstration."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from .classifier import Classification, IntentClassifier
from .pii_masker import mask_pii


@dataclass(frozen=True)
class RouteRequest:
    text: str
    amount_usd: float = 0.0
    request_id: str = "demo-request"


@dataclass(frozen=True)
class RouteDecision:
    request_id: str
    intent: str
    risk: str
    confidence: float
    language: str
    route: str
    model: str
    reason: str
    require_human_review: bool
    masked_text: str
    matched_keywords: tuple[str, ...]


class CostRouter:
    def __init__(
        self,
        classifier: IntentClassifier | None = None,
        *,
        high_amount_usd: float = 1_000.0,
        min_confidence: float = 0.60,
    ) -> None:
        self.classifier = classifier or IntentClassifier()
        self.high_amount_usd = high_amount_usd
        self.min_confidence = min_confidence

    def route(self, request: RouteRequest) -> RouteDecision:
        if not request.text.strip():
            raise ValueError("text must not be empty")
        if request.amount_usd < 0:
            raise ValueError("amount_usd must be non-negative")

        masked = mask_pii(request.text)
        result: Classification = self.classifier.classify(masked.text)

        if request.amount_usd >= self.high_amount_usd:
            route, reason, review = "premium", "high-amount-hard-rule", True
        elif result.risk == "high":
            route, reason, review = "premium", "high-risk-intent", True
        elif result.confidence < self.min_confidence:
            route, reason, review = "premium", "low-confidence-fallback", False
        else:
            route, reason, review = "economy", "routine-high-confidence", False

        return RouteDecision(
            request_id=request.request_id,
            intent=result.intent,
            risk=result.risk,
            confidence=result.confidence,
            language=result.language,
            route=route,
            model=f"{route}-model",
            reason=reason,
            require_human_review=review,
            masked_text=masked.text,
            matched_keywords=result.matched_keywords,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a support request")
    parser.add_argument("--text", "--test-input", dest="text", required=True)
    parser.add_argument("--amount-usd", type=float, default=0.0)
    args = parser.parse_args()
    decision = CostRouter().route(RouteRequest(args.text, args.amount_usd))
    print(json.dumps(asdict(decision), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

