from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.schemas.actions import (
    Action,
    ActionCreateResult,
    ActionStatusEvent,
    CreateManualActionRequest,
    UpdateActionStatusRequest,
)


ACTION_VERSION = "manual-action-v1"
ALLOWED_TRANSITIONS = {
    "planned": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


class ActionStoreUnavailable(RuntimeError):
    """Raised when Action persistence cannot reach the database."""


class ActionNotFound(RuntimeError):
    """Raised without disclosing an Action outside the active tenant."""


class ActionRecommendationNotApproved(RuntimeError):
    """Raised when a Recommendation has not been explicitly approved."""


class ActionInvalidTransition(RuntimeError):
    """Raised when an Action attempts an irreversible invalid state transition."""


class ActionStore(Protocol):
    def create_or_get_manual_action(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: CreateManualActionRequest) -> ActionCreateResult: ...
    def list_for_recommendation(self, *, tenant_id: str, recommendation_id: str) -> list[Action]: ...
    def get_action(self, *, tenant_id: str, action_id: str) -> Action: ...
    def update_status(self, *, tenant_id: str, action_id: str, user_id: str, payload: UpdateActionStatusRequest) -> Action: ...


class PostgresActionStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def create_or_get_manual_action(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: CreateManualActionRequest) -> ActionCreateResult:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT id, business_id, status, action_type, channel FROM recommendations WHERE id = %s AND tenant_id = %s",
                (recommendation_id, tenant_id),
            )
            recommendation = cursor.fetchone()
            if not recommendation:
                raise ActionNotFound("해당 추천에 접근할 수 없습니다.")
            if recommendation["status"] != "approved":
                raise ActionRecommendationNotApproved("승인된 Recommendation에서만 Action 초안을 만들 수 있습니다.")
            cursor.execute(
                "INSERT INTO actions (tenant_id, business_id, recommendation_id, action_version, action_type, channel, title, execution_notes, planned_start_at, planned_end_at, planned_budget, created_by_user_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (recommendation_id, action_version) DO NOTHING RETURNING *",
                (
                    tenant_id, recommendation["business_id"], recommendation_id, ACTION_VERSION, recommendation["action_type"], recommendation["channel"],
                    payload.title.strip(), payload.execution_notes, payload.planned_start_at, payload.planned_end_at,
                    Json(payload.planned_budget.model_dump(mode="json")) if payload.planned_budget else None, user_id,
                ),
            )
            row = cursor.fetchone()
            replayed = row is None
            if replayed:
                cursor.execute(
                    "SELECT * FROM actions WHERE recommendation_id = %s AND action_version = %s AND tenant_id = %s",
                    (recommendation_id, ACTION_VERSION, tenant_id),
                )
                row = cursor.fetchone()
            if not row:
                raise ActionNotFound("Action 초안을 찾을 수 없습니다.")
            if not replayed:
                cursor.execute(
                    "INSERT INTO action_status_events (tenant_id, business_id, action_id, status, note, changed_by_user_id) VALUES (%s, %s, %s, 'planned', NULL, %s)",
                    (tenant_id, row["business_id"], row["id"], user_id),
                )
            return ActionCreateResult(action=self._action_with_events(cursor, row), replayed=replayed)

    def list_for_recommendation(self, *, tenant_id: str, recommendation_id: str) -> list[Action]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM actions WHERE tenant_id = %s AND recommendation_id = %s ORDER BY created_at ASC",
                (tenant_id, recommendation_id),
            )
            return [self._action_with_events(cursor, row) for row in cursor.fetchall()]

    def get_action(self, *, tenant_id: str, action_id: str) -> Action:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM actions WHERE id = %s AND tenant_id = %s", (action_id, tenant_id))
            row = cursor.fetchone()
            if not row:
                raise ActionNotFound("해당 Action에 접근할 수 없습니다.")
            return self._action_with_events(cursor, row)

    def update_status(self, *, tenant_id: str, action_id: str, user_id: str, payload: UpdateActionStatusRequest) -> Action:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM actions WHERE id = %s AND tenant_id = %s FOR UPDATE", (action_id, tenant_id))
            row = cursor.fetchone()
            if not row:
                raise ActionNotFound("해당 Action에 접근할 수 없습니다.")
            if payload.status == row["status"]:
                return self._action_with_events(cursor, row)
            if payload.status not in ALLOWED_TRANSITIONS[row["status"]]:
                raise ActionInvalidTransition(f"{row['status']} 상태에서 {payload.status} 상태로 변경할 수 없습니다.")
            timestamp_column = {"in_progress": "started_at", "completed": "completed_at", "cancelled": "cancelled_at"}[payload.status]
            cursor.execute(
                f"UPDATE actions SET status = %s, {timestamp_column} = COALESCE({timestamp_column}, now()), updated_at = now() WHERE id = %s RETURNING *",
                (payload.status, action_id),
            )
            updated = cursor.fetchone()
            cursor.execute(
                "INSERT INTO action_status_events (tenant_id, business_id, action_id, status, note, changed_by_user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (tenant_id, updated["business_id"], action_id, payload.status, payload.note, user_id),
            )
            return self._action_with_events(cursor, updated)

    def _action_with_events(self, cursor, row: dict) -> Action:
        cursor.execute(
            "SELECT * FROM action_status_events WHERE action_id = %s ORDER BY created_at ASC",
            (row["id"],),
        )
        return _action_from_row(row, cursor.fetchall())

    def _connection(self):
        if not self.database_url:
            raise ActionStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise ActionStoreUnavailable("Action 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryActionStore:
    actions: dict[str, Action]
    by_recommendation: dict[tuple[str, str], str]
    tenant_by_action: dict[str, str]
    recommendation_statuses: dict[str, str]
    recommendation_types: dict[str, tuple[str, str]]
    tenant_by_recommendation: dict[str, str]

    def __init__(self) -> None:
        self.actions = {}
        self.by_recommendation = {}
        self.tenant_by_action = {}
        self.recommendation_statuses = {}
        self.recommendation_types = {}
        self.tenant_by_recommendation = {}

    def register_recommendation(self, *, tenant_id: str, recommendation_id: str, status: str, action_type: str, channel: str) -> None:
        self.recommendation_statuses[recommendation_id] = status
        self.recommendation_types[recommendation_id] = (action_type, channel)
        self.tenant_by_recommendation[recommendation_id] = tenant_id

    def create_or_get_manual_action(self, *, tenant_id: str, recommendation_id: str, user_id: str, payload: CreateManualActionRequest) -> ActionCreateResult:
        if recommendation_id not in self.recommendation_statuses or self.tenant_by_recommendation.get(recommendation_id) != tenant_id:
            raise ActionNotFound("해당 추천에 접근할 수 없습니다.")
        if self.recommendation_statuses[recommendation_id] != "approved":
            raise ActionRecommendationNotApproved("승인된 Recommendation에서만 Action 초안을 만들 수 있습니다.")
        key = (tenant_id, recommendation_id)
        existing_id = self.by_recommendation.get(key)
        if existing_id:
            return ActionCreateResult(action=self.actions[existing_id], replayed=True)
        now = datetime.now(timezone.utc)
        action_type, channel = self.recommendation_types[recommendation_id]
        event = ActionStatusEvent(id=str(uuid4()), status="planned", changed_by_user_id=user_id, created_at=now)
        action = Action(
            id=str(uuid4()), business_id="business-default", recommendation_id=recommendation_id, version=ACTION_VERSION, status="planned", action_type=action_type,
            channel=channel, title=payload.title.strip(), execution_notes=payload.execution_notes, planned_start_at=payload.planned_start_at,
            planned_end_at=payload.planned_end_at, planned_budget=payload.planned_budget, created_by_user_id=user_id,
            created_at=now, updated_at=now, status_events=[event],
        )
        self.actions[action.id] = action
        self.by_recommendation[key] = action.id
        self.tenant_by_action[action.id] = tenant_id
        return ActionCreateResult(action=action)

    def list_for_recommendation(self, *, tenant_id: str, recommendation_id: str) -> list[Action]:
        return [item for item in self.actions.values() if item.recommendation_id == recommendation_id and self.tenant_by_action[item.id] == tenant_id]

    def get_action(self, *, tenant_id: str, action_id: str) -> Action:
        action = self.actions.get(action_id)
        if not action or self.tenant_by_action.get(action_id) != tenant_id:
            raise ActionNotFound("해당 Action에 접근할 수 없습니다.")
        return action

    def update_status(self, *, tenant_id: str, action_id: str, user_id: str, payload: UpdateActionStatusRequest) -> Action:
        action = self.get_action(tenant_id=tenant_id, action_id=action_id)
        if payload.status == action.status:
            return action
        if payload.status not in ALLOWED_TRANSITIONS[action.status]:
            raise ActionInvalidTransition(f"{action.status} 상태에서 {payload.status} 상태로 변경할 수 없습니다.")
        now = datetime.now(timezone.utc)
        event = ActionStatusEvent(id=str(uuid4()), status=payload.status, note=payload.note, changed_by_user_id=user_id, created_at=now)
        updates: dict[str, object] = {"status": payload.status, "updated_at": now, "status_events": [*action.status_events, event]}
        if payload.status == "in_progress": updates["started_at"] = action.started_at or now
        if payload.status == "completed": updates["completed_at"] = action.completed_at or now
        if payload.status == "cancelled": updates["cancelled_at"] = action.cancelled_at or now
        updated = action.model_copy(update=updates)
        self.actions[action_id] = updated
        return updated


def _action_from_row(row: dict, event_rows: list[dict]) -> Action:
    return Action(
        id=str(row["id"]), business_id=str(row["business_id"]), recommendation_id=str(row["recommendation_id"]), version=row["action_version"], status=row["status"],
        action_type=row["action_type"], channel=row["channel"], title=row["title"], execution_notes=row["execution_notes"],
        planned_start_at=row["planned_start_at"], planned_end_at=row["planned_end_at"], planned_budget=row["planned_budget"],
        created_by_user_id=str(row["created_by_user_id"]), started_at=row["started_at"], completed_at=row["completed_at"],
        cancelled_at=row["cancelled_at"], created_at=row["created_at"], updated_at=row["updated_at"],
        status_events=[
            ActionStatusEvent(id=str(event["id"]), status=event["status"], note=event["note"],
                              changed_by_user_id=str(event["changed_by_user_id"]), created_at=event["created_at"])
            for event in event_rows
        ],
    )
