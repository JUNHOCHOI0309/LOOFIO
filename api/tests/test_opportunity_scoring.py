from app.analytics.scoring.opportunity_score import SCORE_VERSION, score_opportunity


def test_opportunity_score_uses_documented_weights() -> None:
    score = score_opportunity(
        impact_ratio=0.5,
        confidence_ratio=0.75,
        persistence_ratio=0.25,
        actionability_ratio=1.0,
    )

    assert score.version == SCORE_VERSION
    assert score.impact == 17.5
    assert score.confidence == 22.5
    assert score.persistence == 5.0
    assert score.actionability == 15.0
    assert score.total == 60.0
    assert score.total == sum((score.impact, score.confidence, score.persistence, score.actionability))


def test_opportunity_score_clamps_inputs_to_component_bounds() -> None:
    maximum = score_opportunity(
        impact_ratio=2.0,
        confidence_ratio=1.5,
        persistence_ratio=3.0,
        actionability_ratio=4.0,
    )
    minimum = score_opportunity(
        impact_ratio=-1.0,
        confidence_ratio=-0.5,
        persistence_ratio=-2.0,
        actionability_ratio=-3.0,
    )

    assert maximum.total == 100.0
    assert maximum.breakdown() == {
        "impact": 35.0,
        "confidence": 30.0,
        "persistence": 20.0,
        "actionability": 15.0,
        "total": 100.0,
    }
    assert minimum.total == 0.0
