"""Grounded support-agent workflow with tools, RAG, routing and guardrails."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from typing import Any

from .cost_router import CostRouter, RouteRequest
from .guardrails import inspect_untrusted_text, validate_citations
from .rag import HybridRetriever, SearchHit


@dataclass(frozen=True)
class SupportRequest:
    text: str
    amount_usd: float = 0.0
    request_id: str = "demo-agent-request"
    customer_tier: str = "standard"


@dataclass(frozen=True)
class ToolCall:
    tool: str
    status: str
    output: dict[str, Any]


@dataclass(frozen=True)
class AgentAnswer:
    request_id: str
    answer: str
    intent: str
    language: str
    route: str
    model: str
    action: str
    require_human_review: bool
    grounded: bool
    citations: tuple[str, ...]
    retrieved_sources: tuple[dict[str, Any], ...]
    guardrail_flags: tuple[str, ...]
    tool_calls: tuple[ToolCall, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SupportAgent:
    """Manager-style workflow whose high-impact policy stays deterministic."""

    def __init__(
        self,
        *,
        router: CostRouter | None = None,
        retriever: HybridRetriever | None = None,
    ) -> None:
        self.router = router or CostRouter()
        self.retriever = retriever or HybridRetriever()

    @staticmethod
    def _run_tool(intent: str, masked_text: str, review: bool) -> ToolCall:
        if review:
            return ToolCall(
                "create_human_review_case",
                "approval-required",
                {"queue": "risk-and-compliance", "automated_action": False},
            )
        if intent == "logistics":
            return ToolCall(
                "lookup_shipment",
                "simulated",
                {"status": "in-transit", "input": masked_text, "live_order_access": False},
            )
        if intent == "refund":
            return ToolCall(
                "check_refund_policy",
                "simulated",
                {"eligible_for_manual_check": True, "automatic_refund": False},
            )
        if intent == "account":
            return ToolCall(
                "start_account_recovery",
                "simulated",
                {"signed_link_required": True, "credential_collection": False},
            )
        return ToolCall("search_knowledge", "completed", {"automated_action": False})

    @staticmethod
    def _answer_text(language: str, intent: str, review: bool, hits: list[SearchHit]) -> str:
        references = " ".join(hit.citation() for hit in hits)
        if review:
            templates = {
                "zh": f"该请求涉及高风险事项，已停止自动处理并转交授权人员审核。请勿在聊天中提交额外敏感信息。依据：{references}",
                "ko": f"고위험 요청이므로 자동 처리를 중단하고 권한 있는 담당자 검토로 이관했습니다. 추가 민감 정보를 채팅에 보내지 마세요. 근거: {references}",
                "en": f"This is a high-risk request. Automated action is stopped and an authorized human review is required. Do not send additional sensitive data in chat. Sources: {references}",
            }
            return templates.get(language, templates["en"])
        labels = {
            "logistics": "shipment tracking",
            "refund": "refund review",
            "account": "secure account recovery",
            "product": "market-specific inventory",
            "unknown": "support request",
        }
        topic = labels.get(intent, "support request")
        templates = {
            "zh": f"我已按{topic}流程检查该请求。请按引用知识中的安全步骤继续；当前工具结果仅为演示，不代表真实订单操作。依据：{references}",
            "ko": f"{topic} 절차에 따라 요청을 확인했습니다. 인용된 안전 절차를 따라 주세요. 현재 도구 결과는 데모이며 실제 주문 작업이 아닙니다. 근거: {references}",
            "en": f"I checked this request using the {topic} workflow. Follow the cited safe next steps; the tool result is a demo and does not represent a live account action. Sources: {references}",
        }
        return templates.get(language, templates["en"])

    def resolve(self, request: SupportRequest) -> AgentAnswer:
        guardrail = inspect_untrusted_text(request.text)
        decision = self.router.route(
            RouteRequest(request.text, request.amount_usd, request.request_id)
        )
        query = f"{decision.intent} {decision.masked_text}"
        hits = self.retriever.search(
            query,
            intent=decision.intent,
            language=decision.language,
            top_k=3,
        )
        tool_call = self._run_tool(
            decision.intent, decision.masked_text, decision.require_human_review
        )
        action = "human-review" if decision.require_human_review else "respond"
        citations = tuple(hit.doc_id for hit in hits)
        validate_citations(citations, (hit.doc_id for hit in hits))
        answer = self._answer_text(
            decision.language, decision.intent, decision.require_human_review, hits
        )
        return AgentAnswer(
            request_id=request.request_id,
            answer=answer,
            intent=decision.intent,
            language=decision.language,
            route=decision.route,
            model=decision.model,
            action=action,
            require_human_review=decision.require_human_review,
            grounded=bool(citations),
            citations=citations,
            retrieved_sources=tuple(
                {
                    "doc_id": hit.doc_id,
                    "title": hit.title,
                    "source": hit.source,
                    "score": hit.score,
                    "sparse_score": hit.sparse_score,
                    "dense_score": hit.dense_score,
                }
                for hit in hits
            ),
            guardrail_flags=guardrail.flags,
            tool_calls=(
                ToolCall(
                    "inspect_prompt_injection",
                    "passed" if guardrail.passed else "flagged",
                    {"flags": list(guardrail.flags)},
                ),
                ToolCall(
                    "route_model_and_risk",
                    "completed",
                    {"reason": decision.reason, "confidence": decision.confidence},
                ),
                ToolCall(
                    "hybrid_knowledge_search",
                    "completed",
                    {"embedding_provider": self.retriever.embedder.name, "hits": len(hits)},
                ),
                tool_call,
            ),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the grounded support agent")
    parser.add_argument("--text", required=True)
    parser.add_argument("--amount-usd", type=float, default=0.0)
    parser.add_argument("--request-id", default="demo-agent-request")
    args = parser.parse_args()
    answer = SupportAgent().resolve(
        SupportRequest(args.text, args.amount_usd, args.request_id)
    )
    print(json.dumps(answer.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
