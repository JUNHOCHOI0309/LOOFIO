# ADR 0013 — DormantCustomer Detector v1

## Status

Accepted

## Context

Hospital MVP v0.3은 재방문 주기를 지난 고객을 관찰해야 한다. Appointment의 `customer_token`은 import 단계에서 평문 전화번호·이메일 매핑을 막고 최소 길이의 가명 토큰만 허용한다. Detector는 이 토큰과 완료 방문일만 사용한다.

## Decision

- `dormant-customer-v1`은 필수 `as_of_date`를 입력으로 받는다. 시스템 현재 시각을 숨은 입력으로 쓰지 않아 같은 데이터·기준일은 같은 결과를 낸다.
- `completed` 상태만 방문으로 취급하고, 같은 고객의 같은 날짜 다중 예약은 재방문 간격에서 하나의 방문으로 합친다.
- 기대 재방문 주기는 개인 간격 중앙값(최소 2개)을 우선한다. 부족하면 마지막 Offering의 고객군 간격 중앙값(최소 10개), 그다음 business 전체 고객군 중앙값(최소 30개)을 사용한다.
- 마지막 완료 방문 이후 날짜 경과일이 기대 주기의 1.3배 이상일 때만 후보를 반환한다.
- 응답에는 이미 검증된 가명 `customer_token`만 포함한다. 원문 연락처, 고객 메시지, Recommendation, Action, 외부 채널 실행을 만들지 않는다.

## Limitations

- 이탈, 치료 종료, 고객 의도, 재방문 가능성, 매출 손실을 판정하지 않는다.
- 임상 주기, 예약 가능 시간, 서비스 변경, 외부 요인을 보정하지 않는다.
- 가명 customer token이 없는 완료 예약과 기준일 이후 예약은 고객별 분석에서 제외한다.

## Self-review

- Opportunity Intelligence 관점: pure Metric DTO와 명시적 기준일만 사용하며, 기준 주기·표본 수·version·limitations를 반환한다.
- Data/Privacy 관점: import의 가명 토큰 검증을 그대로 사용하고 평문 고객 식별자·연락처를 새로 저장·전송·표시하지 않는다. 화면에는 토큰을 마스킹한다.

## Rollback

새 read-only endpoint와 Dashboard 카드만 비활성화하면 된다. 기존 Opportunity, Recommendation, Action, Result에는 영향을 주지 않는다.
