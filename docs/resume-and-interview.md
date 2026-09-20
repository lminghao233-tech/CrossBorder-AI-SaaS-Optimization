# Resume wording and interview pitch

## Resume-ready wording

**CrossBorder AI Cost & Risk Router | Portfolio reconstruction**

- Built a Python multilingual routing prototype that classifies Chinese,
  English and Korean support requests, masks common PII and applies risk-first
  policy for economy/premium model tiers.
- Created a deterministic 600-record synthetic benchmark. It reproduced 90.00%
  intent accuracy, 79.17% economy routing, 100.00% premium routing for high-risk
  samples and 31.67% modeled cost reduction versus a premium-only baseline.
- Added 28 automated tests, 97% package branch coverage, CLI, versioned keyword
  configuration, benchmark artifacts and GitHub Actions.

The phrase **synthetic benchmark** must remain in the resume or project
description. These metrics are not production K-Trade traffic.

## 90-second pitch

"The business problem was that routine logistics and account questions do not
need the same model tier as legal, tax or high-value disputes. I separated
classification from policy: the classifier identifies intent and confidence,
while hard rules make high amount, high risk and low confidence choose the
premium route. Before routing, the system masks common PII. Because employer
data cannot be published, I rebuilt the evaluation with 600 deterministic
synthetic Chinese, English and Korean tickets. The benchmark is intentionally
reproducible: 79.17% reached the economy route, all expected high-risk samples
remained on premium, and the fixed price model produced 31.67% savings. It is a
portfolio MVP, and production still needs real authorized replay, provider
adapters, tenant auth, rate limits and observability."

