# LOOFIO Dependency Rules v1

## 1. 목적

모듈 간 의존성을 한 방향으로 유지하여 LOOFIO가 특정 데이터 공급자, AI 모델, 외부 채널 또는 UI에 강결합되지 않도록 한다.

---

# 2. 기본 방향

```text
Apps/UI
  ↓
API
  ↓
Application
  ↓
Domain / Analytics
  ↓
Ports

Infrastructure/Connectors
  → Ports 구현
```

**안쪽 계층은 바깥쪽 구현을 알면 안 된다.**

## 2.1 현재 저장소 매핑

| 논리 계층 | 현재 경로 |
|---|---|
| Apps/UI | `apps/web/app` |
| API | `api/app/api/routes`, `api/app/schemas` |
| Application/Domain workflow | `api/app/imports`, `opportunities`, `recommendations`, `actions`, `results` |
| Metrics | `api/app/metrics` |
| Detectors | `api/app/analytics/detectors` |
| Scoring | `api/app/analytics/scoring` |
| Infrastructure store | 각 application module의 `store.py` |
| Database migration | `api/migrations` |

현재 작은 MVP에서는 application contract와 PostgreSQL adapter가 같은 feature package에 있지만, Detector와 Scoring은 DB·HTTP·AI 없이 테스트 가능한 pure module로 유지한다.

---

# 3. 허용 관계

| From | To | 허용 |
|---|---|---|
| Apps/UI | API Client Contract | ✅ |
| API | Application Use Case | ✅ |
| Application | Domain | ✅ |
| Application | Analytics Interface | ✅ |
| Application | Repository/AI/Connector Port | ✅ |
| Normalization | Domain Contract | ✅ |
| Domain Adapter | BusinessEvent Contract | ✅ |
| Metrics | Domain/BusinessEvent read model | ✅ |
| Detector | Metric output | ✅ |
| Scoring | Opportunity candidate | ✅ |
| Recommendation | Opportunity/Evidence | ✅ |
| Measurement | Action/Result/Metric | ✅ |
| Infrastructure | Port Interface | ✅ |
| Connector | External provider SDK/API | ✅ |
| AI Adapter | AI provider SDK/API | ✅ |

---

# 4. 금지 관계

| From | To | 이유 |
|---|---|---|
| Detector | AI Provider | Detector는 deterministic이어야 함 |
| Metric | LLM | 계산 재현성 훼손 |
| Domain | Connector SDK | 외부 공급자 강결합 |
| Domain | HTTP Controller | 계층 역전 |
| Domain | ORM-specific API 직접 의존 | 도메인 오염 방지 |
| Opportunity | Content Generator | 기회 탐지와 실행 콘텐츠 분리 |
| Connector | Detector 직접 호출 | 수집과 분석 lifecycle 분리 |
| AI Recommendation | Raw Import Row 직접 조회 | 정규화/근거 경계 우회 |
| UI | DB | API 계약 우회 |
| Measurement | AI의 설명 문장 | 실제 수치 대신 자연어에 의존 금지 |
| Tenant A module context | Tenant B data | 보안 불변조건 |

---

# 5. Data Dependency

정상 흐름:

```text
Raw Import
→ Normalized Domain
→ BusinessEvent
→ Metric
→ Detector
→ Opportunity
→ Recommendation
→ Action
→ Result
→ Measurement
```

다음 shortcut을 만들지 않는다.

```text
Raw Import ───────────────→ AI Recommendation   ❌
Raw Import ───────────────→ Detector            ❌
Recommendation ───────────→ Metric              ❌
AI text ──────────────────→ Revenue calculation ❌
```

---

# 6. Opportunity Engine Dependency

```text
metrics
  ↓
detectors
  ↓
scoring
  ↓
opportunity persistence
```

`detectors`는 다음에 의존할 수 있다.

- metric DTO
- detector config
- time/date utilities
- pure domain types

`detectors`가 의존하면 안 되는 것:

- OpenAI/Anthropic/기타 AI SDK
- HTTP request
- 외부 광고 API
- UI
- prompt template
- connector implementation

---

# 7. AI Dependency

```text
Application
→ AI Port
← AI Adapter
   → Provider SDK
```

비즈니스 로직은 다음과 같이 호출한다.

```text
generateRecommendation(input)
```

다음처럼 호출하지 않는다.

```text
openai.chat.completions(...)
```

를 Detector/Application 핵심 코드 곳곳에 직접 작성하는 방식.

모델명과 provider 선택은 AI Gateway/Adapter 내부 책임이다.

---

# 8. Connector Dependency

Connector 책임:

```text
External API
↕
Provider DTO
↕
Normalization / Port Contract
```

Connector가 다음을 결정하면 안 된다.

- Opportunity인지 여부
- Recommendation 내용
- Incremental Revenue
- 사용자 승인 정책

Connector는 데이터를 수집하거나 승인된 Action을 실행하는 어댑터다.

---

# 9. Domain Adapter Dependency

다업종 지원은 다음 패턴으로 추가한다.

```text
Provider Data
→ Domain Adapter
→ Domain Entity
→ BusinessEvent
→ Common Analytics
```

예:

```text
Appointment Adapter
Sale Adapter
WorkOrder Adapter
Booking Adapter
```

새 Domain Adapter가 기존 Detector를 복제해서 별도 구현하는 것을 기본값으로 삼지 않는다.

먼저 공통 Metric/Detector 재사용 가능성을 검토한다.

---

# 10. Shared/Common Module 제한

`common`, `utils`, `shared`는 아무 코드나 넣는 쓰레기통이 아니다.

허용:

- 순수 날짜/시간 유틸
- money/value object
- pagination type
- error base type
- ID type
- generic validation primitives

금지:

- Business-specific rule
- Opportunity rule
- AI prompt
- Connector rule
- DB repository implementation

공통 모듈이 도메인 모듈을 import하면 안 된다.

---

# 11. Circular Dependency 금지

순환 의존:

```text
business → marketing → business
```

발생 시 다음 중 하나로 해소한다.

1. 공통 Port/Contract 추출
2. Application orchestration으로 이동
3. 이벤트 기반 연결
4. 진짜 동일 도메인이라면 모듈 경계 재검토

순환 의존을 dependency injection trick으로 숨기지 않는다.

---

# 12. 테스트 경계

각 모듈은 바깥 구현 없이 테스트 가능해야 한다.

예:

```text
LowDemandSlotDetector
```

는 DB, HTTP, AI 없이 pure input으로 테스트 가능해야 한다.

외부 구현은 contract/integration test에서 검증한다.

---

# 13. 변경 규칙

새 dependency 추가 전 확인:

- 이 라이브러리가 어느 계층에 속하는가?
- Domain/Analytics를 외부 vendor에 묶는가?
- 순수 인터페이스 뒤로 숨길 수 있는가?
- Security/PII 영향이 있는가?
- 장기적으로 교체 가능한가?

새 외부 SaaS/SDK는 승인 없는 Core 의존성으로 추가하지 않는다.
