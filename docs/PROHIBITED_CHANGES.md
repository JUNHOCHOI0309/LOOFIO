# LOOFIO Prohibited Changes v1

현재 구현 범위와 미구현 안전 경계는 `CURRENT_IMPLEMENTATION_STATUS.md`를 함께 참조한다. 특히 실제 AI provider와 외부 채널은 아직 연결되지 않았으며, 이 문서의 승인·PII·자동화 금지 규칙을 충족하는 별도 설계 없이는 추가하지 않는다.

이 문서는 LOOFIO에서 **코드가 동작하더라도 허용하지 않는 변경**을 명시한다.

---

# 1. AI / Analytics

## 금지

- 원본 예약/매출 수천 건을 LLM에 직접 넣고 Opportunity를 찾게 하기
- LLM이 매출, ROI, 증감률, 취소율, 가동률을 최종 계산하기
- AI 설명이 deterministic 수치를 덮어쓰기
- Detector에 AI provider SDK를 import하기
- 데이터 부족을 숨기고 높은 Confidence로 표현하기
- Estimate를 실제 발생 매출로 표현하기
- 추천 효과를 보장값으로 표현하기

---

# 2. Data / Tenant

## 금지

- tenant scope 없는 repository query
- 다른 고객사의 데이터를 같은 AI/RAG context에 혼합
- tenant/business 구분 없는 cache key
- tenant 구분 없는 파일 저장 경로
- customer phone/email 평문을 내부 공통 customer key로 사용
- 고객 연락처/상담 원문을 필요성 검토 없이 외부 AI에 전달
- 다른 business의 customer를 자동으로 동일인으로 병합
- 공식 taxonomy 원본을 LOOFIO 해석값으로 덮어쓰기

---

# 3. Database

## 금지

- 운영 DB에서 migration 없이 직접 schema 수정
- 데이터 손실 가능성이 있는 컬럼/테이블 즉시 삭제
- Detector/Metric 의미를 바꾸고 version을 유지
- 핵심 필드를 편의상 모두 JSONB로 이동
- source lineage를 제거하는 정규화
- 실제 매출과 추정 매출을 같은 컬럼 의미로 사용

---

# 4. API

## 금지

- `/api/v1` 필드 삭제/타입 변경을 조용히 배포
- status/enum 의미를 기존 client와 다르게 변경
- client가 DB table 구조를 알아야만 사용할 수 있는 API
- stack trace/secret/token 반환
- authorization을 frontend에만 의존
- 외부 실행 POST에 중복 방지 고려 없이 side effect 수행

---

# 5. Architecture

## 금지

- UI에서 DB 직접 접근
- Domain에서 외부 provider SDK 직접 호출
- Metric/Detector에서 HTTP 호출
- Connector에서 Opportunity 판단
- Connector에서 Incrementality 계산
- AI text를 Measurement의 source of truth로 사용
- 순환 dependency를 DI container로 숨기기
- `utils/common`에 비즈니스 규칙을 무분별하게 이동

---

# 6. Product Safety

MVP에서 사용자 승인 없이 금지:

- 광고비 증액/집행
- 고객 메시지 발송
- 게시물 발행
- 쿠폰 활성화
- 리뷰/문의 자동 답변
- 외부 계정 설정 변경

향후 자동화를 도입하려면 별도 안전범위, 예산 상한, 감사로그, rollback, 사용자 설정이 필요하다.

---

# 7. Measurement

## 금지

- 단순 전후 매출 상승을 모두 LOOFIO 효과라고 주장
- 외부 행사/계절/날씨 가능성을 무시하고 인과관계 단정
- baseline 없이 Incremental Revenue를 실제값처럼 표시
- measurement method/version 미기록
- action/result 연결 없이 효과 주장

---

# 8. Deployment / Operations

## 금지

- main branch에서 검증 없이 직접 production 반영
- production secret을 repository에 commit
- migration rollback/forward 전략 없이 위험 migration 배포
- 실패한 deployment를 성공으로 표시
- 운영 hotfix를 코드 저장소에 되돌려 반영하지 않음
- production DB 수동 변경 후 migration 미작성

---

# 9. Ownership / Review

리뷰 없이 금지:

- tenant/auth
- DB destructive migration
- Detector 공식
- Opportunity Score/Confidence
- 외부 AI로 전송하는 개인정보 범위
- 광고/메시지 자동 실행
- API breaking change
- Measurement/Incrementality
- AGENTS/Prohibited Changes 수정

1인 개발 단계에서는 PR 또는 변경기록에 위험 관점 자기검토를 남긴다.

---

# 10. 금지 규칙 예외

예외가 필요한 경우 코드에서 조용히 우회하지 않는다.

필수:

1. 이유
2. 영향
3. 대안 검토
4. 보안/데이터 영향
5. rollback
6. 만료일 또는 재검토일
7. 관련 문서 수정

을 ADR 또는 명시적 예외 문서로 남긴다.
