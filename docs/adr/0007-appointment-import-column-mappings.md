# ADR 0007 — 병원별 Appointment CSV 열 매핑

## Status

Accepted

## Context

병원마다 예약 시스템과 CSV 내보내기 형식이 달라 표준 `Hospital Appointment v1` 헤더만 요구하면 업로드 부담이 커진다. 반면 추측한 열을 그대로 저장하면 날짜·상태·금액의 의미가 잘못되어 Observation과 Opportunity가 오염될 수 있다.

## Decision

- CSV 업로드 전에 헤더를 분석하는 `inspect` endpoint를 제공한다.
- 결정론적이고 제한된 alias 목록으로만 열 매핑을 제안한다. 전화번호·이메일 등 개인정보 열은 alias 목록에 넣지 않는다.
- 사용자는 필수 표준 필드(`appointment_id`, `visit_start_at`, `offering_name`, `status`)를 확인하고, 필요한 경우 외부 상태값을 내부 상태값으로 명시적으로 연결한다.
- 확인된 매핑은 tenant/business 범위의 이름 있는 `appointment_import_mappings` 프로필에 저장하고 이후 preview/import에서 `mapping_id`로 재사용한다.
- 매핑된 행만 기존 Appointment normalizer로 전달한다. 원본 이력에는 계속 allowlist된 표준 필드만 보관한다.

## Consequences

- 표준 Hospital v1 파일은 mapping 없이 이전 방식과 호환된다.
- 병원별 파일 차이를 흡수하지만 정규화 계약, Tenant 격리, idempotency, 개인정보 최소화 규칙은 유지한다.
- 동일 이름 프로필을 다시 저장하면 해당 tenant/business 안에서만 갱신된다.

## Rollback

Migration은 additive다. 새 endpoint를 중단해도 기존 표준 CSV import에는 영향이 없으며, 저장된 매핑은 삭제하지 않고 읽기 경로만 비활성화할 수 있다.
