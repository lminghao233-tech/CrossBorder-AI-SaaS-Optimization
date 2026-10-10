# Resume wording and interview pitch

## Resume-ready wording

**CrossBorder AI Support Agent | Python, FastAPI, Hybrid RAG, Agents SDK**

- Built a multilingual agent workflow for Chinese, English and Korean support,
  combining BM25+dense hybrid RAG, citation validation, domain tools and
  risk-aware economy/premium model routing.
- Designed deterministic PII, prompt-injection and human-approval guardrails so
  legal, tax and high-value requests cannot be auto-executed or downgraded by an
  LLM; added an optional OpenAI Agents SDK specialist-handoff path.
- Created reproducible synthetic routing and RAG/safety evaluations, FastAPI and
  CLI interfaces, Docker packaging, automated tests and GitHub Actions CI.

Keep the phrases **synthetic benchmark** and **controlled evaluation** near any
metrics. They are not production-traffic claims.

## 90-second pitch

"I wanted this to be an agent system rather than a chat wrapper. A request is
first validated and stripped of common PII, then deterministic code checks
prompt injection, classifies intent and applies a risk-first model route. The
agent retrieves multilingual policy through hybrid BM25 and dense search,
selects an allow-listed domain tool and returns only citations from the actual
retrieval set. Legal, tax and high-value cases cannot execute a business action;
they create a human-review decision instead. The default workflow is fully
offline, so every reviewer can run it and the CI does not depend on a paid API.
For a live demonstration I added OpenAI Agents SDK handoffs, but the model only
sees a masked, immutable policy envelope. I evaluate routing, retrieval recall,
citation validity and safety separately so failures are diagnosable."
