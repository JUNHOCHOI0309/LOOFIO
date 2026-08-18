from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from app.decisioning.cause_preview import CausePreviewApplication, CausePreviewInputError
from app.decisioning.causes.models import CAUSE_ANALYSIS_VERSION, CAUSE_PRIORITY_VERSION
from app.decisioning.strategies import analyze_low_demand_strategy
from app.decisioning.strategies.models import STRATEGY_ENGINE_VERSION, STRATEGY_PRIORITY_VERSION
from app.opportunities.store import OpportunityStore
from app.schemas.cause_analyses import CauseAnalysisPreviewRequest, PreviewMetadata
from app.schemas.strategy_runs import (
    STRATEGY_PREVIEW_CONTRACT_VERSION,
    StrategyPreviewRequest,
    StrategyPreviewResponse,
)


class StrategyPreviewInputError(ValueError):
    """Raised when a Strategy preview cannot be calculated safely."""


@dataclass(frozen=True)
class StrategyPreviewApplication:
    opportunity_store: OpportunityStore

    def preview(
        self,
        *,
        tenant_id: str,
        opportunity_id: str,
        payload: StrategyPreviewRequest,
    ) -> StrategyPreviewResponse:
        try:
            cause_preview = CausePreviewApplication(self.opportunity_store).preview(
                tenant_id=tenant_id,
                opportunity_id=opportunity_id,
                payload=CauseAnalysisPreviewRequest(
                    as_of=payload.as_of,
                    decision_context=payload.decision_context,
                ),
            )
            strategy_run = analyze_low_demand_strategy(
                cause_preview.decision_context,
                cause_preview.cause_analysis,
            )
        except (CausePreviewInputError, ValueError) as error:
            raise StrategyPreviewInputError("strategy preview input is invalid") from error

        input_hash = _input_hash(
            decision_context_hash=cause_preview.decision_context.context_hash,
            as_of=payload.as_of,
        )
        return StrategyPreviewResponse(
            preview=PreviewMetadata(
                preview_id=f"STRATEGY_PREVIEW_{input_hash[:24]}",
                input_hash=input_hash,
                generated_at=payload.as_of,
                as_of=payload.as_of,
                engine_versions={
                    "decision_context": cause_preview.decision_context.contract_version,
                    "cause_analysis": CAUSE_ANALYSIS_VERSION,
                    "cause_priority": CAUSE_PRIORITY_VERSION,
                    "strategy": STRATEGY_ENGINE_VERSION,
                    "strategy_priority": STRATEGY_PRIORITY_VERSION,
                },
            ),
            decision_context=cause_preview.decision_context,
            cause_analysis=cause_preview.cause_analysis,
            strategy_run=strategy_run,
        )


def _input_hash(*, decision_context_hash: str | None, as_of) -> str:
    payload = {
        "contract_version": STRATEGY_PREVIEW_CONTRACT_VERSION,
        "as_of": as_of.isoformat(),
        "decision_context_hash": decision_context_hash,
        "cause_analysis_version": CAUSE_ANALYSIS_VERSION,
        "cause_priority_version": CAUSE_PRIORITY_VERSION,
        "strategy_engine_version": STRATEGY_ENGINE_VERSION,
        "strategy_priority_version": STRATEGY_PRIORITY_VERSION,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
