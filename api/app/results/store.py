from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.schemas.results import ActionResult, ActionResultCreateResult, CreateActionResultRequest, RESULT_VERSION


class ResultStoreUnavailable(RuntimeError):
    pass


class ResultNotFound(RuntimeError):
    pass


class ResultActionNotCompleted(RuntimeError):
    pass


class ResultStore(Protocol):
    def create_or_get(self, *, tenant_id: str, action_id: str, user_id: str, payload: CreateActionResultRequest) -> ActionResultCreateResult: ...
    def get(self, *, tenant_id: str, action_id: str) -> ActionResult: ...


class PostgresResultStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def create_or_get(self, *, tenant_id: str, action_id: str, user_id: str, payload: CreateActionResultRequest) -> ActionResultCreateResult:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT id, status FROM actions WHERE id = %s AND tenant_id = %s FOR UPDATE", (action_id, tenant_id))
            action = cursor.fetchone()
            if not action:
                raise ResultNotFound("해당 Action에 접근할 수 없습니다.")
            if action["status"] != "completed":
                raise ResultActionNotCompleted("완료된 Action에만 결과를 기록할 수 있습니다.")
            cursor.execute(
                "INSERT INTO action_results (tenant_id, action_id, result_version, execution_summary, measurement_start_at, measurement_end_at, actual_spend, outcome_notes, recorded_by_user_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (action_id, result_version) DO NOTHING RETURNING *",
                (tenant_id, action_id, RESULT_VERSION, payload.execution_summary.strip(), payload.measurement_start_at,
                 payload.measurement_end_at, Json(payload.actual_spend.model_dump(mode="json")) if payload.actual_spend else None,
                 payload.outcome_notes, user_id),
            )
            row = cursor.fetchone()
            replayed = row is None
            if replayed:
                cursor.execute("SELECT * FROM action_results WHERE tenant_id = %s AND action_id = %s AND result_version = %s", (tenant_id, action_id, RESULT_VERSION))
                row = cursor.fetchone()
            if not row:
                raise ResultNotFound("Action 결과를 찾을 수 없습니다.")
            return ActionResultCreateResult(result=_result_from_row(row), replayed=replayed)

    def get(self, *, tenant_id: str, action_id: str) -> ActionResult:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM action_results WHERE tenant_id = %s AND action_id = %s AND result_version = %s", (tenant_id, action_id, RESULT_VERSION))
            row = cursor.fetchone()
            if not row:
                raise ResultNotFound("해당 Action 결과에 접근할 수 없습니다.")
            return _result_from_row(row)

    def _connection(self):
        if not self.database_url:
            raise ResultStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise ResultStoreUnavailable("Action 결과 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryResultStore:
    results: dict[tuple[str, str], ActionResult]
    completed_actions: dict[tuple[str, str], bool]

    def __init__(self) -> None:
        self.results = {}
        self.completed_actions = {}

    def register_action(self, *, tenant_id: str, action_id: str, completed: bool) -> None:
        self.completed_actions[(tenant_id, action_id)] = completed

    def create_or_get(self, *, tenant_id: str, action_id: str, user_id: str, payload: CreateActionResultRequest) -> ActionResultCreateResult:
        key = (tenant_id, action_id)
        if key not in self.completed_actions:
            raise ResultNotFound("해당 Action에 접근할 수 없습니다.")
        if not self.completed_actions[key]:
            raise ResultActionNotCompleted("완료된 Action에만 결과를 기록할 수 있습니다.")
        if key in self.results:
            return ActionResultCreateResult(result=self.results[key], replayed=True)
        now = datetime.now(timezone.utc)
        result = ActionResult(id=str(uuid4()), action_id=action_id, version=RESULT_VERSION, execution_summary=payload.execution_summary.strip(),
                              measurement_start_at=payload.measurement_start_at, measurement_end_at=payload.measurement_end_at,
                              actual_spend=payload.actual_spend, outcome_notes=payload.outcome_notes, recorded_by_user_id=user_id, recorded_at=now)
        self.results[key] = result
        return ActionResultCreateResult(result=result)

    def get(self, *, tenant_id: str, action_id: str) -> ActionResult:
        result = self.results.get((tenant_id, action_id))
        if not result:
            raise ResultNotFound("해당 Action 결과에 접근할 수 없습니다.")
        return result


def _result_from_row(row: dict) -> ActionResult:
    return ActionResult(id=str(row["id"]), action_id=str(row["action_id"]), version=row["result_version"], execution_summary=row["execution_summary"],
                        measurement_start_at=row["measurement_start_at"], measurement_end_at=row["measurement_end_at"],
                        actual_spend=row["actual_spend"], outcome_notes=row["outcome_notes"], recorded_by_user_id=str(row["recorded_by_user_id"]), recorded_at=row["recorded_at"])
