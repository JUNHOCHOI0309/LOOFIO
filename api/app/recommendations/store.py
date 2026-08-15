from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.recommendations.low_demand import RecommendationDraft
from app.schemas.recommendations import Recommendation, RecommendationDecision, RecommendationDecisionRequest


class RecommendationStoreUnavailable(RuntimeError):
    """Raised when recommendation persistence cannot reach the database."""


class RecommendationNotFound(RuntimeError):
    """Raised without disclosing a recommendation outside the active tenant."""


class RecommendationStore(Protocol):
    def create_or_get_draft(self, *, tenant_id: str, opportunity_id: str, draft: RecommendationDraft) -> Recommendation: ...
    def list_for_opportunity(self, *, tenant_id: str, opportunity_id: str) -> list[Recommendation]: ...
    def record_decision(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: RecommendationDecisionRequest) -> Recommendation: ...


class PostgresRecommendationStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def create_or_get_draft(self, *, tenant_id: str, opportunity_id: str, draft: RecommendationDraft) -> Recommendation:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "INSERT INTO recommendations (tenant_id, business_id, opportunity_id, recommendation_version, hypothesis, action_type, channel, target_segment, expected_effect, confidence, explanation, limitations) "
                "SELECT %s, o.business_id, o.id, %s, %s, %s, %s, %s, %s, %s, %s, %s FROM opportunities o "
                "WHERE o.id = %s AND o.tenant_id = %s "
                "ON CONFLICT (opportunity_id, recommendation_version) DO UPDATE SET updated_at = now() "
                "RETURNING *",
                (
                    tenant_id, draft.version, draft.hypothesis, draft.action_type, draft.channel,
                    Json(draft.target_segment), Json(draft.expected_effect.model_dump()) if draft.expected_effect else None,
                    draft.confidence, draft.explanation, Json(draft.limitations), opportunity_id, tenant_id,
                ),
            )
            row = cursor.fetchone()
            if not row:
                raise RecommendationNotFound("해당 기회에 접근할 수 없습니다.")
            return _recommendation_from_row(row)

    def list_for_opportunity(self, *, tenant_id: str, opportunity_id: str) -> list[Recommendation]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT r.*, d.id AS decision_id, d.decision, d.reason_code, d.reason_text, d.modified_payload, d.decided_by_user_id, d.created_at AS decided_at "
                "FROM recommendations r "
                "LEFT JOIN LATERAL (SELECT * FROM recommendation_decisions WHERE recommendation_id = r.id ORDER BY created_at DESC LIMIT 1) d ON true "
                "WHERE r.tenant_id = %s AND r.opportunity_id = %s ORDER BY r.created_at ASC",
                (tenant_id, opportunity_id),
            )
            return [_recommendation_from_row(row) for row in cursor.fetchall()]

    def record_decision(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: RecommendationDecisionRequest) -> Recommendation:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "UPDATE recommendations SET status = %s, updated_at = now() WHERE id = %s AND tenant_id = %s RETURNING *",
                (payload.decision, recommendation_id, tenant_id),
            )
            row = cursor.fetchone()
            if not row:
                raise RecommendationNotFound("해당 추천에 접근할 수 없습니다.")
            cursor.execute(
                "INSERT INTO recommendation_decisions (tenant_id, business_id, recommendation_id, decision, reason_code, reason_text, modified_payload, decided_by_user_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, decision, reason_code, reason_text, modified_payload, decided_by_user_id, created_at AS decided_at",
                (tenant_id, row["business_id"], recommendation_id, payload.decision, payload.reason_code, payload.reason_text,
                 Json(payload.modified_payload.model_dump()) if payload.modified_payload else None, user_id),
            )
            row["decision_id"] = cursor.fetchone()["id"]
            row["decision"] = payload.decision
            row["reason_code"] = payload.reason_code
            row["reason_text"] = payload.reason_text
            row["modified_payload"] = payload.modified_payload.model_dump() if payload.modified_payload else None
            row["decided_by_user_id"] = user_id
            row["decided_at"] = datetime.now(timezone.utc)
            return _recommendation_from_row(row)

    def _connection(self):
        if not self.database_url:
            raise RecommendationStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise RecommendationStoreUnavailable("추천 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryRecommendationStore:
    recommendations: dict[str, Recommendation]
    by_opportunity_version: dict[tuple[str, str], str]
    tenants: dict[str, str]

    def __init__(self) -> None:
        self.recommendations = {}
        self.by_opportunity_version = {}
        self.tenants = {}

    def create_or_get_draft(self, *, tenant_id: str, opportunity_id: str, draft: RecommendationDraft) -> Recommendation:
        key = (opportunity_id, draft.version)
        existing_id = self.by_opportunity_version.get(key)
        if existing_id:
            return self.recommendations[existing_id]
        recommendation = Recommendation(
            id=str(uuid4()), opportunity_id=opportunity_id, version=draft.version, status="draft",
            hypothesis=draft.hypothesis, action_type=draft.action_type, channel=draft.channel, target_segment=draft.target_segment,
            expected_effect=draft.expected_effect, confidence=draft.confidence, explanation=draft.explanation,
            limitations=draft.limitations, created_at=datetime.now(timezone.utc),
        )
        self.recommendations[recommendation.id] = recommendation
        self.by_opportunity_version[key] = recommendation.id
        self.tenants[recommendation.id] = tenant_id
        return recommendation

    def list_for_opportunity(self, *, tenant_id: str, opportunity_id: str) -> list[Recommendation]:
        return [item for item in self.recommendations.values() if item.opportunity_id == opportunity_id and self.tenants[item.id] == tenant_id]

    def record_decision(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: RecommendationDecisionRequest) -> Recommendation:
        recommendation = self.recommendations.get(recommendation_id)
        if not recommendation or self.tenants.get(recommendation_id) != tenant_id:
            raise RecommendationNotFound("해당 추천에 접근할 수 없습니다.")
        decision = RecommendationDecision(
            id=str(uuid4()), decision=payload.decision, reason_code=payload.reason_code, reason_text=payload.reason_text,
            modified_payload=payload.modified_payload, decided_by_user_id=user_id, decided_at=datetime.now(timezone.utc),
        )
        updated = recommendation.model_copy(update={"status": payload.decision, "latest_decision": decision})
        self.recommendations[recommendation_id] = updated
        return updated


def _recommendation_from_row(row: dict) -> Recommendation:
    latest_decision = None
    if row.get("decision_id"):
        latest_decision = RecommendationDecision(
            id=str(row["decision_id"]), decision=row["decision"], reason_code=row["reason_code"], reason_text=row["reason_text"],
            modified_payload=row["modified_payload"], decided_by_user_id=str(row["decided_by_user_id"]), decided_at=row["decided_at"],
        )
    return Recommendation(
        id=str(row["id"]), opportunity_id=str(row["opportunity_id"]), version=row["recommendation_version"], status=row["status"],
        hypothesis=row["hypothesis"], action_type=row["action_type"], channel=row["channel"], target_segment=row["target_segment"],
        expected_effect=row["expected_effect"], confidence=float(row["confidence"]), explanation=row["explanation"],
        limitations=row["limitations"], created_at=row["created_at"], latest_decision=latest_decision,
    )
