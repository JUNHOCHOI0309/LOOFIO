# ADR 0003: Appointment observation metrics v1

## Status

Accepted — 2026-08-13

## Decision

`appointment-observation-v1` calculates these deterministic observations from tenant- and business-scoped Appointment rows:

- appointment, completed, cancelled, and no-show counts
- cancellation rate: `cancelled_count / appointment_count`
- actual revenue: sum of `paid_amount` only where status is `completed`
- average completed revenue: actual revenue divided by completed rows that have `paid_amount`
- daily counts and weekday × two-hour local-time buckets

All bucketing uses the business timezone. The API returns zero rates for an empty data set and does not infer missing revenue.

## Non-goals

- Occupancy and booking rates are not calculated without capacity, business-hours, and available-slot data.
- No estimate, Opportunity score, recommendation, or AI-generated value is returned by this metric endpoint.
- Metric results are computed on read in this iteration; no historical metric snapshot table is introduced.

## Consequences

The metric version is returned in every response. Any future meaning change requires a new version rather than reinterpreting historical values.
