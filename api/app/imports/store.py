from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json

from app.imports.appointments import NormalizedAppointment
from app.schemas.imports import AppointmentImportResult


class ImportStoreUnavailable(RuntimeError):
    """Raised when appointment import persistence cannot reach the database."""


class BusinessNotFoundForTenant(RuntimeError):
    """Raised without exposing whether another tenant owns the requested business."""


class ImportIdempotencyConflict(RuntimeError):
    """Raised when the same idempotency key is reused for different file content."""


class MultipleLocationsRequireMapping(RuntimeError):
    """Raised until a business has an explicit external-location mapping."""


class AppointmentImportStore(Protocol):
    def persist_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        source_filename: str,
        idempotency_key: str,
        raw_csv: bytes,
        rows: list[NormalizedAppointment],
    ) -> AppointmentImportResult: ...

    def get_import(self, *, tenant_id: str, business_id: str, import_id: str) -> AppointmentImportResult | None: ...


class PostgresAppointmentImportStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def persist_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        source_filename: str,
        idempotency_key: str,
        raw_csv: bytes,
        rows: list[NormalizedAppointment],
    ) -> AppointmentImportResult:
        content_sha256 = sha256(raw_csv).hexdigest()
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            location_id = self._single_location_id(cursor, tenant_id, business_id)
            cursor.execute(
                "SELECT id, content_sha256, total_rows, imported_rows, duplicate_rows, invalid_rows, status "
                "FROM import_jobs WHERE tenant_id = %s AND business_id = %s AND idempotency_key = %s",
                (tenant_id, business_id, idempotency_key),
            )
            existing = cursor.fetchone()
            if existing:
                if existing["content_sha256"] != content_sha256:
                    raise ImportIdempotencyConflict("동일 Idempotency-Key에는 같은 파일만 사용할 수 있습니다.")
                return _result_from_row(existing, business_id=business_id, replayed=True)

            cursor.execute(
                "INSERT INTO import_jobs (tenant_id, business_id, source_system, source_filename, status, idempotency_key, content_sha256, total_rows) "
                "VALUES (%s, %s, %s, %s, 'processing', %s, %s, %s) RETURNING id",
                (tenant_id, business_id, "csv", source_filename, idempotency_key, content_sha256, len(rows)),
            )
            import_id = str(cursor.fetchone()["id"])
            imported_rows = 0
            duplicate_rows = 0
            for row in rows:
                customer_id = self._upsert_customer(cursor, tenant_id, business_id, row)
                offering_id = self._find_or_create_offering(cursor, tenant_id, business_id, row)
                cursor.execute(
                    "INSERT INTO appointments (tenant_id, business_id, location_id, customer_id, offering_id, import_job_id, source_system, source_record_id, "
                    "visit_start_at, visit_end_at, offering_name, status, paid_amount) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (tenant_id, business_id, source_system, source_record_id) DO NOTHING RETURNING id",
                    (
                        tenant_id, business_id, location_id, customer_id, offering_id, import_id, row.source_system,
                        row.source_record_id, row.visit_start_at, row.visit_end_at, row.offering_name, row.status, row.paid_amount,
                    ),
                )
                outcome = "imported" if cursor.fetchone() else "duplicate"
                if outcome == "imported":
                    imported_rows += 1
                else:
                    duplicate_rows += 1
                cursor.execute(
                    "INSERT INTO import_rows (tenant_id, business_id, import_job_id, row_number, raw_payload, normalized_payload, outcome) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (tenant_id, business_id, import_id, row.row_number, Json(row.raw_payload), Json(row.normalized_payload()), outcome),
                )

            cursor.execute(
                "UPDATE import_jobs SET status = 'completed', imported_rows = %s, duplicate_rows = %s, completed_at = now() WHERE id = %s",
                (imported_rows, duplicate_rows, import_id),
            )
        return AppointmentImportResult(
            import_id=import_id,
            business_id=business_id,
            total_rows=len(rows),
            imported_rows=imported_rows,
            duplicate_rows=duplicate_rows,
            invalid_rows=0,
            status="completed",
        )

    def get_import(self, *, tenant_id: str, business_id: str, import_id: str) -> AppointmentImportResult | None:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            self._single_location_id(cursor, tenant_id, business_id)
            cursor.execute(
                "SELECT id, total_rows, imported_rows, duplicate_rows, invalid_rows, status FROM import_jobs "
                "WHERE id = %s AND tenant_id = %s AND business_id = %s",
                (import_id, tenant_id, business_id),
            )
            row = cursor.fetchone()
            return _result_from_row(row, business_id=business_id) if row else None

    def _single_location_id(self, cursor, tenant_id: str, business_id: str) -> str:
        cursor.execute("SELECT id FROM businesses WHERE id = %s AND tenant_id = %s", (business_id, tenant_id))
        if not cursor.fetchone():
            raise BusinessNotFoundForTenant("해당 병원에 접근할 수 없습니다.")
        cursor.execute(
            "SELECT id FROM locations WHERE tenant_id = %s AND business_id = %s ORDER BY created_at ASC",
            (tenant_id, business_id),
        )
        locations = cursor.fetchall()
        if len(locations) != 1:
            raise MultipleLocationsRequireMapping("여러 지점에는 외부 location_key 매핑이 필요합니다.")
        return str(locations[0]["id"])

    def _upsert_customer(self, cursor, tenant_id: str, business_id: str, row: NormalizedAppointment) -> str | None:
        if not row.customer_token:
            return None
        cursor.execute(
            "INSERT INTO customers (tenant_id, business_id, external_customer_token, first_seen_at, last_seen_at) "
            "VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT (tenant_id, business_id, external_customer_token) DO UPDATE SET "
            "first_seen_at = CASE WHEN customers.first_seen_at IS NULL OR EXCLUDED.first_seen_at < customers.first_seen_at THEN EXCLUDED.first_seen_at ELSE customers.first_seen_at END, "
            "last_seen_at = CASE WHEN customers.last_seen_at IS NULL OR EXCLUDED.last_seen_at > customers.last_seen_at THEN EXCLUDED.last_seen_at ELSE customers.last_seen_at END "
            "RETURNING id",
            (tenant_id, business_id, row.customer_token, row.visit_start_at, row.visit_start_at),
        )
        return str(cursor.fetchone()["id"])

    def _find_or_create_offering(self, cursor, tenant_id: str, business_id: str, row: NormalizedAppointment) -> str:
        cursor.execute(
            "SELECT id FROM offerings WHERE tenant_id = %s AND business_id = %s AND name = %s ORDER BY created_at ASC LIMIT 1",
            (tenant_id, business_id, row.offering_name),
        )
        existing = cursor.fetchone()
        if existing:
            return str(existing["id"])
        duration_minutes = None
        if row.visit_end_at:
            duration_minutes = int((row.visit_end_at - row.visit_start_at).total_seconds() / 60)
        cursor.execute(
            "INSERT INTO offerings (tenant_id, business_id, name, list_price, duration_minutes) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (tenant_id, business_id, row.offering_name, row.listed_price, duration_minutes),
        )
        return str(cursor.fetchone()["id"])

    def _connection(self):
        if not self.database_url:
            raise ImportStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise ImportStoreUnavailable("예약 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryAppointmentImportStore:
    business_locations: dict[tuple[str, str], list[str]]
    imports: dict[tuple[str, str, str], tuple[str, str, AppointmentImportResult]]
    source_records: set[tuple[str, str, str, str]]

    def __init__(self) -> None:
        self.business_locations = {}
        self.imports = {}
        self.source_records = set()

    def register_business(self, *, tenant_id: str, business_id: str, location_id: str = "location-1") -> None:
        self.business_locations[(tenant_id, business_id)] = [location_id]

    def persist_appointments(
        self,
        *,
        tenant_id: str,
        business_id: str,
        source_filename: str,
        idempotency_key: str,
        raw_csv: bytes,
        rows: list[NormalizedAppointment],
    ) -> AppointmentImportResult:
        locations = self.business_locations.get((tenant_id, business_id))
        if not locations:
            raise BusinessNotFoundForTenant("해당 병원에 접근할 수 없습니다.")
        if len(locations) != 1:
            raise MultipleLocationsRequireMapping("여러 지점에는 외부 location_key 매핑이 필요합니다.")
        key = (tenant_id, business_id, idempotency_key)
        content_sha256 = sha256(raw_csv).hexdigest()
        existing = self.imports.get(key)
        if existing:
            _, existing_hash, result = existing
            if existing_hash != content_sha256:
                raise ImportIdempotencyConflict("동일 Idempotency-Key에는 같은 파일만 사용할 수 있습니다.")
            return result.model_copy(update={"replayed": True})
        imported_rows = 0
        duplicate_rows = 0
        for row in rows:
            source_key = (tenant_id, business_id, row.source_system, row.source_record_id)
            if source_key in self.source_records:
                duplicate_rows += 1
            else:
                self.source_records.add(source_key)
                imported_rows += 1
        result = AppointmentImportResult(
            import_id=str(uuid4()), business_id=business_id, total_rows=len(rows), imported_rows=imported_rows,
            duplicate_rows=duplicate_rows, invalid_rows=0, status="completed",
        )
        self.imports[key] = (result.import_id, content_sha256, result)
        return result

    def get_import(self, *, tenant_id: str, business_id: str, import_id: str) -> AppointmentImportResult | None:
        if (tenant_id, business_id) not in self.business_locations:
            raise BusinessNotFoundForTenant("해당 병원에 접근할 수 없습니다.")
        for stored_import_id, _, result in self.imports.values():
            if stored_import_id == import_id and result.business_id == business_id:
                return result
        return None


def _result_from_row(row: dict, *, business_id: str, replayed: bool = False) -> AppointmentImportResult:
    return AppointmentImportResult(
        import_id=str(row["id"]),
        business_id=business_id,
        total_rows=row["total_rows"],
        imported_rows=row["imported_rows"],
        duplicate_rows=row["duplicate_rows"],
        invalid_rows=row["invalid_rows"],
        status=row["status"],
        replayed=replayed,
    )
