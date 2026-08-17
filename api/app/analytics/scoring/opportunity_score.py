from dataclasses import dataclass


SCORE_VERSION = "opportunity-score-v1"


@dataclass(frozen=True)
class OpportunityScore:
    version: str
    impact: float
    confidence: float
    persistence: float
    actionability: float
    total: float

    def breakdown(self) -> dict[str, float]:
        return {
            "impact": self.impact,
            "confidence": self.confidence,
            "persistence": self.persistence,
            "actionability": self.actionability,
            "total": self.total,
        }


def score_opportunity(
    *,
    impact_ratio: float,
    confidence_ratio: float,
    persistence_ratio: float,
    actionability_ratio: float,
) -> OpportunityScore:
    """Convert normalized, detector-owned factors into the 100-point priority score."""
    impact = round(_unit(impact_ratio) * 35, 2)
    confidence = round(_unit(confidence_ratio) * 30, 2)
    persistence = round(_unit(persistence_ratio) * 20, 2)
    actionability = round(_unit(actionability_ratio) * 15, 2)
    return OpportunityScore(
        version=SCORE_VERSION,
        impact=impact,
        confidence=confidence,
        persistence=persistence,
        actionability=actionability,
        total=round(impact + confidence + persistence + actionability, 2),
    )


def _unit(value: float) -> float:
    return min(1.0, max(0.0, value))
