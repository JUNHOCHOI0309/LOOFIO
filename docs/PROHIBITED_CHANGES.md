# LOOFIO Prohibited Changes v2

- 기준일: 2026-08-18
- 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

이 문서는 코드가 동작하더라도 허용하지 않는 변경을 정의한다.

특히 Opportunity 이후의 **Decision Intelligence** (Cause Analysis → Strategy → Playbook → Experiment → Recommendation Package)가 일반 조언이나 검증되지 않은 AI 출력으로 퇴행하지 않도록 한다.

---

# 1. Analytics / Opportunity

금지:

- Raw Appointment/매출 데이터를 LLM에 넣고 문제를 찾게 하기
- LLM이 Metric·Detector·Score를 최종 계산하기
- Detector가 Cause·Strategy·Channel·Playbook을 선택하기
- Estimate를 Actual Revenue 또는 확정 손실로 표시하기
- score를 성공 확률로 표시하기
- limitations를 숨기기
- version 변경 없이 계산 의미 변경하기

---

# 2. Cause Analysis

금지:

- Cause를 사실로 확정하기
- Evidence reference 없는 cause candidate
- contradiction/missing data 생략
- `DATA_QUALITY_ARTIFACT` 가능성 미검토
- 환자 임상정보로 마케팅 원인을 추론
- 다른 tenant 데이터로 cause 생성
- External Context만으로 인과 단정

---

# 3. Strategy / Playbook

금지:

- 최소 대안 비교 없이 1순위 전략 선택
- 단일 후보 사유 미기록
- `NO_ACTION`, `DATA_COLLECTION`, `CAPACITY_OPERATION`을 배제
- AI 자유형 아이디어를 versioned Playbook처럼 취급
- Playbook definition에 tenant/customer/runtime budget 하드코딩
- precondition/contraindication 없는 Playbook
- 정책 검토 없이 Hospital Playbook 활성화
- 일반 조언을 최종 Recommendation으로 표시

일반 조언 예:

```text
SNS를 강화하세요.
전단지를 돌리세요.
프로모션을 해보세요.
고객에게 연락하세요.
```

---

# 4. Economics / Feasibility

금지:

- `unknown` cost를 0으로 계산
- 마진 없이 순기여이익 표시
- benefit/discount cost 누락
- staff time을 무조건 0으로 처리
- 예산 상한 없는 유료 Action
- 비용 근거 없는 ROI/CAC
- capacity 제약을 무시한 수요 확대 추천
- Action 실행 후에 경제성 가정을 조용히 변경

---

# 5. Experiment / Measurement

금지:

- success threshold 없는 실행
- stop condition 없는 실행
- primary metric 없는 실행
- result source 없는 실행
- 실행 후 primary metric·threshold 변경
- Grade C/D를 Incremental Revenue로 표현
- 단순 전후 상승을 전부 LOOFIO 효과로 주장
- target slot 증가와 다른 slot 감소를 신규 매출로 중복 계산
- 비용 미수집을 비용 0으로 해석
- 데이터 실패와 효과 없음 혼합

---

# 6. Recommendation Quality

금지:

- Quality Score 75 미만 결과를 final recommendation으로 표시
- Hard Fail이 있는 package를 `READY_FOR_REVIEW`로 표시
- LLM 자기평가를 Quality Score Source of Truth로 사용
- Evidence와 무관한 수치·문장
- target/channel/period/budget/owner/measurement가 없는 plan
- 대안 제외 이유 누락
- Quality Gate를 일반 사용자가 override
- validator version 미기록

---

# 7. AI

금지:

- business logic에 특정 provider/model 하드코딩
- AI가 수치·비용·기여이익·실험 결과 생성
- raw PII/clinical data 전송
- 다른 tenant context 혼합
- provider output을 validator 없이 저장·노출
- 무한 retry
- AI 실패로 Opportunity 삭제
- AI 설명이 deterministic evidence를 덮어쓰기

---

# 8. Data / Tenant

금지:

- tenant scope 없는 repository query
- tenant/business 없는 cache/file path
- 다른 business customer 자동 병합
- phone/email 평문을 공통 customer key로 사용
- patient name, resident ID, diagnosis, medical record 장기 분석 저장
- 공식 taxonomy를 LOOFIO mapping으로 덮어쓰기
- source lineage 제거
- Action target/export 무기한 보존

---

# 9. Architecture / Dependency

금지:

- UI→DB 직접 접근
- Domain→provider SDK 직접 접근
- Cause→Raw Import 직접 접근
- Strategy→AI provider 직접 접근
- Experiment metric을 AI text로 정의
- Orchestrator가 Detector/Metric 재계산
- Connector가 Opportunity/Strategy 판단
- Measurement가 Recommendation text를 사실로 사용
- 순환 의존을 DI로 숨기기
- `common/utils`에 Decision rule 이동

---

# 10. API / Database

금지:

- `/api/v1` 기존 필드·의미·enum 조용한 변경
- current `/recommendations/draft` 즉시 삭제
- legacy Action/Measurement 의미 즉시 변경
- migration 없는 운영 DDL
- destructive change 즉시 배포
- 핵심 field를 모두 JSONB로 이동
- current history를 새 version 의미로 재해석
- idempotency 없이 외부 side effect 실행

---

# 11. Product Safety / Channel Execution

MVP에서 승인 없이 금지:

- 메시지 발송
- 광고 집행/증액
- 게시
- 쿠폰/혜택 활성화
- 제휴 비용 확정
- 리뷰/문의 자동 답변
- 외부 계정 변경

금지:

- tracking 없는 온라인/오프라인 실행
- partner/printed material을 source code 없이 효과 측정
- hard budget cap 없는 paid action
- 실제 audience/spend/result reference 미수집

---

# 12. Deployment / Operations

금지:

- 검증 없이 main→production
- secret commit/log/frontend 노출
- migration 전략 없는 배포
- intelligence version 변경 미기록
- Quality regression 없이 Recommendation 배포
- 운영 hotfix를 repository에 미반영
- production DB 수동 변경 후 migration 미작성
- 실패 deployment를 성공 표시

---

# 13. Ownership / Review

필수 리뷰 없이 금지:

- Detector/Score
- Cause taxonomy/score
- Strategy mapping/score
- Playbook 신규/ACTIVE 승격
- Economics formula
- Experiment method/Evidence Grade
- Quality Bar
- AI context/provider/schema
- Hospital policy
- external execution
- Measurement/Incrementality
- tenant/auth/PII
- API breaking change
- destructive migration
- governance docs

---

# 14. 예외

예외는 코드에서 조용히 우회하지 않는다.

필수 기록:

1. 이유
2. 영향
3. 대안
4. tenant/PII/security 영향
5. economics/measurement 영향
6. rollback/disable
7. 만료·재검토일
8. owner
9. 관련 문서·ADR
