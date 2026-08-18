from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.decisioning.causes import analyze_low_demand_slot
from app.decisioning.causes.models import CAUSE_ANALYSIS_VERSION, CAUSE_PRIORITY_VERSION
from app.decisioning.context import DecisionContextSnapshot, LowDemandObservation, OpportunityContext
from app.opportunities.store import OpportunityScope, OpportunityStore
from app.schemas.cause_analyses import (
    CAUSE_PREVIEW_CONTRACT_VERSION,
    CauseAnalysisPreviewRequest,
    CauseAnalysisPreviewResponse,
    PreviewMetadata,
)


class CausePreviewInputError(ValueError):
    """Raised when user-supplied context cannot form a safe preview snapshot."""


_SERVER_CONTROLLED_FIELDS = {
    "tenant_id",
    "business_id",
    "opportunity_id",
    "snapshot_id",
    "snapshot_at",
    "context_hash",
    "opportunity",
    "observation",
}


@dataclass(frozen=True)
class CausePreviewApplication:
    opportunity_store: OpportunityStore

    def preview(
        self,
        *,
        tenant_id: str,
        opportunity_id: str,
        payload: CauseAnalysisPreviewRequest,
    ) -> CauseAnalysisPreviewResponse:
        scope = self.opportunity_store.get_opportunity_with_scope(
            tenant_id=tenant_id, opportunity_id=opportunity_id
        )
        if scope.opportunity.type != "LOW_DEMAND_SLOT":
            raise CausePreviewInputError("Cause Analysis v1 supports LOW_DEMAND_SLOT only")

        snapshot = _bind_context(
            tenant_id=tenant_id,
            opportunity_scope=scope,
            as_of=payload.as_of,
            decision_context=payload.decision_context,
        )
        result = analyze_low_demand_slot(snapshot, as_of=payload.as_of)
        input_hash = _input_hash(snapshot=snapshot, as_of=payload.as_of)
        return CauseAnalysisPreviewResponse(
            preview=PreviewMetadata(
                preview_id=f"CAUSE_PREVIEW_{input_hash[:24]}",
                input_hash=input_hash,
                generated_at=payload.as_of,
                as_of=payload.as_of,
                engine_versions={
                    "decision_context": snapshot.contract_version,
                    "cause_analysis": CAUSE_ANALYSIS_VERSION,
                    "cause_priority": CAUSE_PRIORITY_VERSION,
                },
            ),
            decision_context=snapshot,
            cause_analysis=result,
        )


def _bind_context(
    *,
    tenant_id: str,
    opportunity_scope: OpportunityScope,
    as_of,
    decision_context: dict[str, Any],
) -> DecisionContextSnapshot:
    protected = sorted(_SERVER_CONTROLLED_FIELDS.intersection(decision_context))
    if protected:
        raise CausePreviewInputError(
            "decision_context cannot set server-controlled fields: " + ", ".join(protected)
        )

    opportunity = opportunity_scope.opportunity
    observation = opportunity.observation
    values = (
        observation.observed_weeks,
        observation.average_appointments_per_week,
        observation.comparison_median_per_week,
        observation.demand_index,
    )
    if any(value is None for value in values):
        raise CausePreviewInputError("stored LOW_DEMAND_SLOT opportunity has incomplete observation")

    context = deepcopy(decision_context)
    snapshot_seed = {
        "tenant_id": tenant_id,
        "business_id": opportunity_scope.business_id,
        "opportunity_id": opportunity.id,
        "as_of": as_of.isoformat(),
        "decision_context": context,
    }
    snapshot_id = "DCTX_PREVIEW_" + hashlib.sha256(
        json.dumps(snapshot_seed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:24]
    opportunity_context = OpportunityContext(
        opportunity_type="LOW_DEMAND_SLOT",
        detector_code=opportunity.detector.code,
        detector_version=opportunity.detector.version,
        evidence_refs=(f"OPPORTUNITY:{opportunity.id}:OBSERVATION",),
        limitations=tuple(opportunity.limitations),
    )
    bound = {
        **context,
        "tenant_id": tenant_id,
        "business_id": opportunity_scope.business_id,
        "opportunity_id": opportunity.id,
        "snapshot_id": snapshot_id,
        "snapshot_at": as_of,
        "opportunity": opportunity_context.model_dump(mode="json"),
        "observation": LowDemandObservation(
            observed_weeks=observation.observed_weeks,
            average_appointments_per_week=observation.average_appointments_per_week,
            comparison_median_per_week=observation.comparison_median_per_week,
            demand_index=observation.demand_index,
        ).model_dump(mode="json"),
    }
    try:
        return DecisionContextSnapshot.model_validate(bound)
    except ValidationError as error:
        raise CausePreviewInputError("decision_context is invalid") from error


def _input_hash(*, snapshot: DecisionContextSnapshot, as_of) -> str:
    payload = {
        "contract_version": CAUSE_PREVIEW_CONTRACT_VERSION,
        "as_of": as_of.isoformat(),
        "decision_context_hash": snapshot.context_hash,
        "cause_analysis_version": CAUSE_ANALYSIS_VERSION,
        "cause_priority_version": CAUSE_PRIORITY_VERSION,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
