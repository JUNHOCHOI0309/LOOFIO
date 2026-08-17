import hashlib
from datetime import date

from app.analytics.detectors.cancellation_hotspots import detect_cancellation_hotspots
from app.analytics.detectors.dormant_customers import detect_dormant_customers
from app.analytics.detectors.service_demand_gaps import detect_service_demand_gaps
from app.analytics.scoring.opportunity_score import score_opportunity
from app.metrics.appointments import AppointmentMetricRow
from app.opportunities.low_demand import OpportunityDraft
from app.schemas.opportunities import OpportunityObservation


def build_other_detector_opportunity_drafts(rows: list[AppointmentMetricRow], *, as_of_date: date | None = None) -> list[OpportunityDraft]:
    drafts = [*_cancellation_drafts(rows), *_service_demand_drafts(rows)]
    if as_of_date:
        drafts.extend(_dormant_customer_drafts(rows, as_of_date=as_of_date))
    return drafts


def _cancellation_drafts(rows: list[AppointmentMetricRow]) -> list[OpportunityDraft]:
    detection = detect_cancellation_hotspots(rows)
    drafts: list[OpportunityDraft] = []
    for candidate in detection.candidates:
        segment = {"weekday": candidate.weekday, "start_hour": candidate.slot_start_hour, "end_hour": candidate.slot_start_hour + 2, "offering_name": candidate.offering_name}
        confidence = round(min(0.7, 0.35 + candidate.observed_weeks * 0.015 + candidate.appointment_count * 0.005), 3)
        drafts.append(OpportunityDraft(
            opportunity_type="CANCELLATION_HOTSPOT", detector_code="CANCELLATION_HOTSPOT", detector_version=detection.detector_version,
            natural_key=f"{candidate.weekday}:{candidate.slot_start_hour}:{candidate.offering_name}", segment=segment,
            observation=OpportunityObservation(kind="cancellation_hotspot", observed_weeks=candidate.observed_weeks, appointment_count=candidate.appointment_count, cancelled_count=candidate.cancelled_count, no_show_count=candidate.no_show_count, disruption_rate=candidate.disruption_rate, baseline_disruption_rate=candidate.baseline_disruption_rate, rate_multiple=candidate.rate_multiple),
            estimate=None,
            scoring=score_opportunity(
                impact_ratio=(candidate.disruption_rate - candidate.baseline_disruption_rate) / max(0.01, 1 - candidate.baseline_disruption_rate),
                confidence_ratio=confidence,
                persistence_ratio=candidate.observed_weeks / 12,
                actionability_ratio=0.9,
            ),
            confidence=confidence, limitations=detection.limitations,
            evidence=[("CANCELLATION_HOTSPOT_OBSERVATION", candidate.model_dump(mode="json"))],
        ))
    return drafts


def _service_demand_drafts(rows: list[AppointmentMetricRow]) -> list[OpportunityDraft]:
    detection = detect_service_demand_gaps(rows)
    drafts: list[OpportunityDraft] = []
    for candidate in detection.candidates:
        segment = {"weekday": candidate.weekday, "start_hour": candidate.slot_start_hour, "end_hour": candidate.slot_start_hour + 2, "offering_name": candidate.offering_name}
        confidence = round(min(0.7, 0.3 + candidate.observed_weeks * 0.015 + candidate.slot_appointment_count * 0.005), 3)
        drafts.append(OpportunityDraft(
            opportunity_type="SERVICE_DEMAND_GAP", detector_code="SERVICE_DEMAND_GAP", detector_version=detection.detector_version,
            natural_key=f"{candidate.weekday}:{candidate.slot_start_hour}:{candidate.offering_name}", segment=segment,
            observation=OpportunityObservation(kind="service_demand_gap", observed_weeks=candidate.observed_weeks, offering_appointment_count=candidate.offering_appointment_count, slot_appointment_count=candidate.slot_appointment_count, slot_offering_appointment_count=candidate.slot_offering_appointment_count, business_offering_share=candidate.business_offering_share, slot_offering_share=candidate.slot_offering_share, share_index=candidate.share_index),
            estimate=None,
            scoring=score_opportunity(
                impact_ratio=1 - candidate.share_index,
                confidence_ratio=confidence,
                persistence_ratio=candidate.observed_weeks / 12,
                actionability_ratio=0.8,
            ),
            confidence=confidence, limitations=detection.limitations,
            evidence=[("SERVICE_DEMAND_GAP_OBSERVATION", candidate.model_dump(mode="json"))],
        ))
    return drafts


def _dormant_customer_drafts(rows: list[AppointmentMetricRow], *, as_of_date: date) -> list[OpportunityDraft]:
    detection = detect_dormant_customers(rows, as_of_date=as_of_date)
    drafts: list[OpportunityDraft] = []
    for candidate in detection.candidates:
        token_hash = hashlib.sha256(candidate.customer_token.encode("utf-8")).hexdigest()
        customer_reference = f"{candidate.customer_token[:8]}…{candidate.customer_token[-4:]}"
        segment = {"customer_reference": customer_reference, "offering_name": candidate.latest_offering_name or "unknown"}
        confidence = round(min(0.7, 0.3 + candidate.reference_interval_count * 0.025), 3)
        drafts.append(OpportunityDraft(
            opportunity_type="DORMANT_CUSTOMER", detector_code="DORMANT_CUSTOMER", detector_version=detection.detector_version,
            natural_key=token_hash, segment=segment,
            observation=OpportunityObservation(kind="dormant_customer", customer_reference=customer_reference, last_completed_visit_date=candidate.last_completed_visit_date.isoformat(), days_since_last_completed_visit=candidate.days_since_last_completed_visit, expected_revisit_days=candidate.expected_revisit_days, overdue_ratio=candidate.overdue_ratio, baseline_source=candidate.baseline_source),
            estimate=None,
            scoring=score_opportunity(
                impact_ratio=(candidate.overdue_ratio - 1.3) / 0.7,
                confidence_ratio=confidence,
                persistence_ratio=candidate.reference_interval_count / 4,
                actionability_ratio=1.0,
            ),
            confidence=confidence, limitations=detection.limitations,
            evidence=[("DORMANT_CUSTOMER_OBSERVATION", {**candidate.model_dump(mode="json"), "customer_token_hash": token_hash, "customer_token": None})],
        ))
    return drafts
