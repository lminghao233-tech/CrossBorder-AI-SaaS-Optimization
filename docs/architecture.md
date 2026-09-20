# Architecture

```text
Request
  -> input validation
  -> typed PII masking
  -> multilingual keyword classification
  -> risk-first policy
       high amount / high risk / low confidence -> premium route
       routine and high confidence             -> economy route
  -> provider adapter boundary (not included in this offline demo)
  -> metrics and feedback
```

## Why deterministic rules first

The demo separates classification from policy. A classifier can be wrong; hard
business risk rules still take precedence. Unknown or low-confidence requests
fall back to the premium route rather than being forced onto the cheaper route.

## Scope

This repository demonstrates routing decisions and a modeled cost benchmark. It
does not call live model providers, does not contain production customer data,
and does not claim production accuracy. Provider SDKs can be added behind an
adapter without changing the policy interface.

