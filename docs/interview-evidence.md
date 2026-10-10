# Interview evidence and honest claim boundaries

## Reproducible claims

- A runnable multilingual agent workflow with hybrid RAG, explicit tool trace,
  risk-aware model routing and a human-in-the-loop gate.
- BM25 plus dense-vector retrieval with interchangeable offline/OpenAI embedding
  providers and source-level citation validation.
- Prompt-injection detection and PII masking before any optional provider call.
- An optional OpenAI Agents SDK path with specialist handoffs; the default path
  needs no API key.
- A 600-record deterministic synthetic routing benchmark and a separate
  six-case retrieval/grounding/safety evaluation.
- FastAPI, CLI, Docker and GitHub Actions with automated tests.

## Claims that would be misleading

- The synthetic tickets are not real company or customer traffic.
- The offline hashing encoder is not a trained semantic embedding model.
- A six-case retrieval evaluation is not production RAG accuracy.
- Tool outputs are simulations and do not access real orders or issue refunds.
- The optional live adapter does not prove a hosted production deployment.

## Strong interview walkthrough

Start with the trust boundary: deterministic code controls masking, risk, tools
and citations. Then run one routine and one legal request and compare their
traces. Show the retrieved sparse/dense scores, explain why live providers are
adapters, and finish by running both evaluation commands. This demonstrates
agent engineering, not only prompt writing.
