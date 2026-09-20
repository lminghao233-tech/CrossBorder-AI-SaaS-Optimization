"""Reproducible benchmark for classification, routing and modeled cost."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .cost_router import CostRouter, RouteRequest
from .synthetic_data import generate_tickets, write_json


@dataclass(frozen=True)
class Price:
    input_per_million: float
    output_per_million: float


# Modeled prices are stable benchmark assumptions, not current vendor quotes.
PRICES = {
    "economy": Price(1.50, 6.00),
    "premium": Price(2.50, 10.00),
}


def request_cost(price: Price, input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * price.input_per_million
        + output_tokens * price.output_per_million
    ) / 1_000_000


def run_benchmark(count: int = 600) -> dict[str, float | int | str]:
    router = CostRouter()
    tickets = generate_tickets(count)
    correct = 0
    economy = 0
    high_risk_premium = 0
    high_risk_total = 0
    baseline_cost = 0.0
    routed_cost = 0.0

    for ticket in tickets:
        decision = router.route(
            RouteRequest(ticket.text, ticket.amount_usd, ticket.ticket_id)
        )
        correct += decision.intent == ticket.expected_intent
        economy += decision.route == "economy"
        if ticket.expected_risk == "high":
            high_risk_total += 1
            high_risk_premium += decision.route == "premium"

        baseline_cost += request_cost(
            PRICES["premium"], ticket.input_tokens, ticket.output_tokens
        )
        routed_cost += request_cost(
            PRICES[decision.route], ticket.input_tokens, ticket.output_tokens
        )

    return {
        "benchmark": "deterministic-synthetic-v1",
        "sample_count": count,
        "languages": 3,
        "intent_accuracy": round(correct / count, 4),
        "economy_route_rate": round(economy / count, 4),
        "high_risk_premium_recall": round(high_risk_premium / high_risk_total, 4),
        "baseline_cost_usd": round(baseline_cost, 6),
        "routed_cost_usd": round(routed_cost, 6),
        "modeled_cost_reduction": round((baseline_cost - routed_cost) / baseline_cost, 4),
        "price_note": "Modeled fixed prices; not current vendor quotes",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic benchmark")
    parser.add_argument("--count", type=int, default=600)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dataset-output", type=Path)
    args = parser.parse_args()
    result = run_benchmark(args.count)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.dataset_output:
        write_json(args.dataset_output, args.count)


if __name__ == "__main__":
    main()

