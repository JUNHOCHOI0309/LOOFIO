# ADR 0004: LowDemandSlot detector v1

## Status

Accepted — 2026-08-13

## Decision

`low-demand-slot-v1` groups tenant- and business-scoped Appointment observations by business-local `weekday × two-hour slot`.

- Minimum observation: 8 distinct ISO weeks in the requested data window.
- Demand for a slot: appointment count divided by observed weeks.
- Comparison: median weekly demand of the other observed slots on the same weekday.
- Candidate rule: `demand_index <= 0.65`.

The detector returns only candidates and its limitations. It does not create an Opportunity record, estimate revenue, or generate a Recommendation.

## Consequences

- Without business hours and capacity, slots with no observed appointments cannot be classified as empty operating slots; they are excluded from comparison.
- Cancellations and no-shows remain appointment-demand observations in this version. Cancellation quality is handled by the separate CancellationHotspot detector.
- Any change to the calculation or threshold requires a new detector version.
