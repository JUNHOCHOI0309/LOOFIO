import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.opportunities.low_demand import OpportunityDraft
from app.schemas.opportunities import Opportunity, OpportunityDetector


class OpportunityStoreUnavailable(RuntimeError):
    """Raised when opportunity persistence cannot reach the database."""


class OpportunityBusinessNotFound(RuntimeError):
    """Raised without disclosing whether another tenant owns a business."""


class OpportunityStore(Protocol):
    def refresh_low_demand(self, *, tenant_id: str, business_id: str, drafts: list[OpportunityDraft]) -> list[Opportunity]: ...
    def list_opportunities(self, *, tenant_id: str, business_id: str) -> list[Opportunity]: ...
    def get_opportunity(self, *, tenant_id: str, opportunity_id: str) -> Opportunity: ...


class PostgresOpportunityStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def refresh_low_demand(self, *, tenant_id: str, business_id: str, drafts: list[OpportunityDraft]) -> list[Opportunity]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            self._assert_business(cursor, tenant_id, business_id)
            refreshed: list[Opportunity] = []
            for draft in drafts:
                cursor.execute(
                    "INSERT INTO opportunities (tenant_id, business_id, opportunity_type, detector_code, detector_version, natural_key, segment, observation, estimate, score, confidence, limitations) "
                    "VALUES (%s, %s, 'LOW_DEMAND_SLOT', %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (tenant_id, business_id, detector_code, detector_version, natural_key) DO UPDATE SET "
                    "segment = EXCLUDED.segment, observation = EXCLUDED.observation, estimate = EXCLUDED.estimate, score = EXCLUDED.score, confidence = EXCLUDED.confidence, limitations = EXCLUDED.limitations, "
                    "last_detected_at = now(), updated_at = now() WHERE opportunities.status = 'open' "
                    "RETURNING *",
                    (
                        tenant_id, business_id, draft.detector_code, draft.detector_version, draft.natural_key, Json(draft.segment), Json(draft.observation.model_dump()),
                        Json(draft.estimate.model_dump()) if draft.estimate else None, draft.score, draft.confidence, Json(draft.limitations),
                    ),
                )
                row = cursor.fetchone()
                if not row:
                    cursor.execute(
                    "SELECT * FROM opportunities WHERE tenant_id = %s AND business_id = %s AND detector_code = %s "
                    "AND detector_version = %s AND natural_key = %s",
                    (tenant_id, business_id, draft.detector_code, draft.detector_version, draft.natural_key),
                    )
                    row = cursor.fetchone()
                opportunity = _opportunity_from_row(row)
                refreshed.append(opportunity)
                for evidence_type, payload in draft.evidence:
                    evidence_hash = hashlib.sha256(
                        json.dumps({"type": evidence_type, "payload": payload}, ensure_ascii=False, sort_keys=True).encode("utf-8")
                    ).hexdigest()
                    cursor.execute(
                        "INSERT INTO opportunity_evidence (opportunity_id, evidence_hash, evidence_type, payload) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (opportunity_id, evidence_hash) DO NOTHING",
                        (opportunity.id, evidence_hash, evidence_type, Json(payload)),
                    )
        return refreshed

    def list_opportunities(self, *, tenant_id: str, business_id: str) -> list[Opportunity]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            self._assert_business(cursor, tenant_id, business_id)
            cursor.execute(
                "SELECT * FROM opportunities WHERE tenant_id = %s AND business_id = %s ORDER BY score DESC, last_detected_at DESC",
                (tenant_id, business_id),
            )
            return [_opportunity_from_row(row) for row in cursor.fetchall()]

    def get_opportunity(self, *, tenant_id: str, opportunity_id: str) -> Opportunity:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM opportunities WHERE id = %s AND tenant_id = %s",
                (opportunity_id, tenant_id),
            )
            row = cursor.fetchone()
            if not row:
                raise OpportunityBusinessNotFound("해당 기회에 접근할 수 없습니다.")
            return _opportunity_from_row(row)

    def _assert_business(self, cursor, tenant_id: str, business_id: str) -> None:
        cursor.execute("SELECT 1 FROM businesses WHERE id = %s AND tenant_id = %s", (business_id, tenant_id))
        if not cursor.fetchone():
            raise OpportunityBusinessNotFound("해당 병원에 접근할 수 없습니다.")

    def _connection(self):
        if not self.database_url:
            raise OpportunityStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise OpportunityStoreUnavailable("기회 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryOpportunityStore:
    opportunities: dict[tuple[str, str, str, str, str], Opportunity]

    def __init__(self) -> None:
        self.opportunities = {}

    def refresh_low_demand(self, *, tenant_id: str, business_id: str, drafts: list[OpportunityDraft]) -> list[Opportunity]:
        now = datetime.now(timezone.utc)
        results: list[Opportunity] = []
        for draft in drafts:
            key = (tenant_id, business_id, draft.detector_code, draft.detector_version, draft.natural_key)
            existing = self.opportunities.get(key)
            opportunity = Opportunity(
                id=existing.id if existing else str(uuid4()), type="LOW_DEMAND_SLOT", status=existing.status if existing else "open",
                segment=draft.segment, observation=draft.observation, estimate=draft.estimate, score=draft.score, confidence=draft.confidence,
                limitations=draft.limitations, detector=OpportunityDetector(code=draft.detector_code, version=draft.detector_version),
                first_detected_at=existing.first_detected_at if existing else now, last_detected_at=now,
            )
            if not existing or existing.status == "open":
                self.opportunities[key] = opportunity
            results.append(self.opportunities.get(key, opportunity))
        return results

    def list_opportunities(self, *, tenant_id: str, business_id: str) -> list[Opportunity]:
        return sorted(
            [item for (item_tenant, item_business, _, _, _), item in self.opportunities.items() if item_tenant == tenant_id and item_business == business_id],
            key=lambda item: item.score,
            reverse=True,
        )

    def get_opportunity(self, *, tenant_id: str, opportunity_id: str) -> Opportunity:
        for (item_tenant, _, _, _, _), opportunity in self.opportunities.items():
            if item_tenant == tenant_id and opportunity.id == opportunity_id:
                return opportunity
        raise OpportunityBusinessNotFound("해당 기회에 접근할 수 없습니다.")

def _opportunity_from_row(row: dict) -> Opportunity:
    return Opportunity(
        id=str(row["id"]), type=row["opportunity_type"], status=row["status"], segment=row["segment"], observation=row["observation"],
        estimate=row["estimate"], score=float(row["score"]), confidence=float(row["confidence"]), limitations=row["limitations"],
        detector=OpportunityDetector(code=row["detector_code"], version=row["detector_version"]),
        first_detected_at=row["first_detected_at"], last_detected_at=row["last_detected_at"],
    )
