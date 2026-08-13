# ADR 0005: Low-demand Opportunity persistence and estimate v1

## Status

Accepted — 2026-08-13

## Decision

The deterministic LowDemandSlot detector can be refreshed into tenant- and business-scoped Opportunity records.

- A natural key of `weekday:start_hour` prevents duplicate open records for the same detector version and segment.
- Every Opportunity stores separate segment, Observation, optional Estimate, score, confidence, limitations, and detector metadata.
- Evidence payloads are append-only and deduplicated by content hash.
- The RevenueGap estimate is optional. When completed-payment samples exist, it uses the weekly booking gap, average completed `paid_amount`, 4.345 weeks/month, and an explicitly labeled 50–100% recovery scenario.
- The score and confidence are deterministic prioritization aids, not probabilities of revenue realization. Capacity absence caps confidence and is surfaced as a limitation.

## Consequences

- Refreshed data updates an open Opportunity but does not silently reopen a dismissed or resolved record.
- Estimates are never written into actual revenue fields and no Recommendation or Action is created.
- Any change to the estimate, score, confidence, or evidence semantics requires a new detector/opportunity version.
