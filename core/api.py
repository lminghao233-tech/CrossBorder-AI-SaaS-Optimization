"""FastAPI surface for the offline-safe support agent."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .agent import SupportAgent, SupportRequest


class ResolveRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8_000)
    amount_usd: float = Field(default=0.0, ge=0.0)
    request_id: str = Field(default="api-request", min_length=1, max_length=128)
    customer_tier: str = Field(default="standard", max_length=64)


app = FastAPI(title="CrossBorder AI Support Agent", version="0.2.0")
agent = SupportAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "offline-safe"}


@app.post("/v1/support/resolve")
def resolve(request: ResolveRequest) -> dict[str, Any]:
    return agent.resolve(
        SupportRequest(
            text=request.text,
            amount_usd=request.amount_usd,
            request_id=request.request_id,
            customer_tier=request.customer_tier,
        )
    ).to_dict()
