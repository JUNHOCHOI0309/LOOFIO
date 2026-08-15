# Appointment sample data

이 폴더에는 LOOFIO의 CSV import·Metric·Detector 검증에 사용하는 **익명화된 견본 데이터만** 둡니다.

- 표준 형식: Hospital v1 CSV
- 필수 열: `appointment_id`, `visit_start_at`, `offering_name`, `status`
- 시간: UTC offset을 포함한 ISO-8601 형식
- 상태: `booked`, `completed`, `cancelled`, `no_show`, `unknown`
- 금액: 쉼표 없는 숫자. 실제 완료 매출은 `completed` 행의 `paid_amount`만 집계됩니다.
- 고객 식별값이 필요하면 `customer_token`에 16자 이상의 가명 토큰만 사용합니다.

넣지 않는 데이터:

- 이름, 전화번호, 이메일, 주소, 주민등록번호
- 진단·증상·처방·검사·상담 등 의료정보
- 실제 운영 데이터 또는 secret

권장 견본 파일:

- `loofio_appointment_sample_hospital_v1.csv`: 기본 Hospital v1 견본
- `hospital_revenue_gap_positive_v1.csv`: RevenueGap이 검출되는 12주 이상 패턴
- `hospital_revenue_gap_sparse_payment_v1.csv`: 결제 표본 부족 처리 검증
- `hospital_operational_mix_v1.csv`: 취소·노쇼·서비스·시간대 혼합 패턴
