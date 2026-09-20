"""Deterministic synthetic multilingual benchmark data.

This module does not contain or imitate identifiable customer records. The
templates represent common support intents and are explicitly synthetic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


ROUTINE = ("logistics", "account", "product", "refund")
HIGH_RISK = ("legal_dispute", "tax_compliance")
LANGUAGES = ("en", "zh", "ko")

DIRECT: dict[str, dict[str, str]] = {
    "logistics": {
        "en": "Where is my parcel for order ORD-{n:05d}?",
        "zh": "请查询订单 ORD-{n:05d} 的物流和包裹位置。",
        "ko": "주문 ORD-{n:05d}의 배송 위치를 확인해 주세요.",
    },
    "account": {
        "en": "I cannot login and need a password reset.",
        "zh": "我无法登录账户，需要重置密码。",
        "ko": "로그인할 수 없어 비밀번호 재설정이 필요합니다.",
    },
    "product": {
        "en": "Is the blue color in size M still in stock?",
        "zh": "蓝色 M 码还有库存吗？",
        "ko": "파란색 M 사이즈 재고가 있나요?",
    },
    "refund": {
        "en": "Please check my refund status and return label.",
        "zh": "请查询退款进度和退货标签。",
        "ko": "환불 상태와 반품 라벨을 확인해 주세요.",
    },
    "legal_dispute": {
        "en": "We face a contract breach and possible lawsuit.",
        "zh": "该订单涉及合同违约和潜在诉讼。",
        "ko": "계약 위반과 소송 가능성이 있습니다.",
    },
    "tax_compliance": {
        "en": "We need help with a VAT audit and tax compliance.",
        "zh": "我们需要处理增值税审计和税务合规。",
        "ko": "부가세 감사와 세무 준수 검토가 필요합니다.",
    },
}

AMBIGUOUS = {
    "en": "Please help me handle this request as soon as possible.",
    "zh": "请尽快帮我处理一下这个问题。",
    "ko": "이 문제를 가능한 한 빨리 처리해 주세요.",
}


@dataclass(frozen=True)
class SyntheticTicket:
    ticket_id: str
    language: str
    text: str
    expected_intent: str
    expected_risk: str
    amount_usd: float
    input_tokens: int = 120
    output_tokens: int = 180
    synthetic: bool = True


def generate_tickets(count: int = 600) -> list[SyntheticTicket]:
    if count <= 0:
        raise ValueError("count must be positive")

    tickets: list[SyntheticTicket] = []
    # 88% routine / 12% high risk. Every tenth sample is deliberately
    # ambiguous, which tests conservative low-confidence fallback behavior.
    routine_cutoff = round(count * 0.88)
    for i in range(count):
        language = LANGUAGES[i % len(LANGUAGES)]
        high = i >= routine_cutoff
        intents = HIGH_RISK if high else ROUTINE
        intent = intents[i % len(intents)]
        ambiguous = i % 10 == 0
        text = AMBIGUOUS[language] if ambiguous else DIRECT[intent][language].format(n=i)
        tickets.append(
            SyntheticTicket(
                ticket_id=f"SYN-{i + 1:04d}",
                language=language,
                text=text,
                expected_intent=intent,
                expected_risk="high" if high else "routine",
                amount_usd=2_500.0 if high and i % 3 == 0 else 50.0,
            )
        )
    return tickets


def write_json(path: Path, count: int = 600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(item) for item in generate_tickets(count)], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

