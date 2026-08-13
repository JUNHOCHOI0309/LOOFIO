from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

import psycopg
from psycopg.rows import dict_row

from app.metrics.appointments import AppointmentMetricRow


class MetricStoreUnavailable(RuntimeError):
    """Raised when metric reads cannot reach the database."""


class MetricBusinessNotFound(RuntimeError):
    """Raised without revealing whether a business belongs to another tenant."""


class AppointmentMetricStore(Protocol):
    def read_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[AppointmentMetricRow]: ...


class PostgresAppointmentMetricStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def read_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[AppointmentMetricRow]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT timezone FROM businesses WHERE id = %s AND tenant_id = %s", (business_id, tenant_id))
            business = cursor.fetchone()
            if not business:
                raise MetricBusinessNotFound("해당 병원에 접근할 수 없습니다.")
            clauses = ["a.tenant_id = %s", "a.business_id = %s"]
            parameters: list[object] = [tenant_id, business_id]
            if start_at:
                clauses.append("a.visit_start_at >= %s")
                parameters.append(start_at)
            if end_at:
                clauses.append("a.visit_start_at <= %s")
                parameters.append(end_at)
            cursor.execute(
                "SELECT a.visit_start_at AT TIME ZONE %s AS local_visit_start_at, a.status, a.paid_amount "
                "FROM appointments a WHERE " + " AND ".join(clauses) + " ORDER BY a.visit_start_at ASC",
                [business["timezone"], *parameters],
            )
            return [
                AppointmentMetricRow(
                    visit_start_at=row["local_visit_start_at"], status=row["status"], paid_amount=_decimal_or_none(row["paid_amount"])
                )
                for row in cursor.fetchall()
            ]

    def _connection(self):
        if not self.database_url:
            raise MetricStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise MetricStoreUnavailable("지표 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryAppointmentMetricStore:
    rows: dict[tuple[str, str], list[AppointmentMetricRow]]

    def __init__(self) -> None:
        self.rows = {}

    def register_rows(self, *, tenant_id: str, business_id: str, rows: list[AppointmentMetricRow]) -> None:
        self.rows[(tenant_id, business_id)] = rows

    def read_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[AppointmentMetricRow]:
        rows = self.rows.get((tenant_id, business_id))
        if rows is None:
            raise MetricBusinessNotFound("해당 병원에 접근할 수 없습니다.")
        return [
            row for row in rows
            if (start_at is None or row.visit_start_at >= start_at) and (end_at is None or row.visit_start_at <= end_at)
        ]


def _decimal_or_none(value: object) -> Decimal | None:
    return Decimal(str(value)) if value is not None else None
