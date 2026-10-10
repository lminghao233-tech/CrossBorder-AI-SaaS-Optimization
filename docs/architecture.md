# Architecture and trust boundary

## Request path

```text
request
  -> validation + typed PII masking
  -> deterministic prompt-injection inspection
  -> multilingual intent and risk classification
  -> risk-first model route
  -> hybrid retrieval
       BM25 sparse score
       + dense vector score
       + intent/language metadata filter
  -> policy-controlled tool
       routine: simulated domain tool
       high-risk/high-value: human-review queue only
  -> citation validation
  -> grounded answer + machine-readable trace
```

## Trust boundary

The router, tool allow-list, human-review requirement and citation validator run
in local deterministic code. The optional live model receives a masked evidence
packet after these controls. Its output is presentation data: it cannot change
the route, execute an unregistered tool or add an un-retrieved citation.

This separation is the central engineering decision. Model quality can improve
without coupling release safety to a prompt or provider.

## Retrieval

`HybridRetriever` combines BM25 with dense cosine similarity. The default
`HashingEmbeddingProvider` is a reproducible offline feature baseline and is not
described as a semantic foundation model. `OpenAIEmbeddingProvider` implements
the same interface for live semantic embeddings. This makes retrieval behavior
testable in CI and replaceable in production.

Each result contains document ID, source, combined score, sparse score and dense
score. The response citation validator accepts only document IDs in the actual
retrieval set.

## Agent orchestration

The offline `SupportAgent` is manager-style orchestration with four visible
steps: input guardrail, route/risk tool, knowledge search and a domain or human
review tool. `core.live_agent` adds OpenAI Agents SDK handoffs for routine and
risk specialists, while keeping the offline result as an immutable envelope.

## Evaluation layers

- Routing evaluation: intent accuracy, high-risk recall and modeled cost.
- Retrieval evaluation: expected source recall@3.
- Grounding evaluation: all citations belong to retrieved context.
- Safety evaluation: high-risk review invariants and injection flagging.
- Unit/API tests: validation, PII boundaries, tool selection and HTTP schema.

## Production evolution

Replace the local dense encoder with a managed embedding model and vector store;
add tenant-scoped document ACLs, OpenTelemetry spans, prompt/version registry,
online quality monitoring, feedback labeling and a reviewed action service. The
deterministic policy layer remains authoritative.
