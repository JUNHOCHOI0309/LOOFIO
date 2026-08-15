"use client";

import { useEffect, useMemo, useState } from "react";

import "./dashboard.css";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const navigation = [["▦", "Dashboard"], ["⊞", "Data"]];

type Business = { business_id: string; name: string; location_name: string; };
type Money = { amount: string; currency: string; };
type Slot = { weekday: string; slot_start_hour: number; appointment_count: number; completed_count: number; cancelled_count: number; cancellation_rate: number; actual_revenue: Money; };
type Metrics = { observed_weeks: number; appointment_count: number; completed_count: number; cancelled_count: number; no_show_count: number; cancellation_rate: number; actual_revenue: Money; time_slots: Slot[]; limitations: string[]; };
type LowDemandCandidate = { weekday: string; slot_start_hour: number; average_appointments_per_week: number; comparison_median_per_week: number; demand_index: number; };
type LowDemandDetection = { candidates: LowDemandCandidate[]; limitations: string[]; };
type RevenueGapCandidate = { weekday: string; slot_start_hour: number; weekly_booking_gap: number; completed_payment_sample_count: number; average_reference_paid_amount: Money; monthly_value_low: Money; monthly_value_high: Money; };
type RevenueGapDetection = { candidates: RevenueGapCandidate[]; limitations: string[]; };
type CancellationHotspotCandidate = { weekday: string; slot_start_hour: number; offering_name: string; appointment_count: number; cancelled_count: number; no_show_count: number; disruption_rate: number; baseline_disruption_rate: number; rate_multiple: number; };
type CancellationHotspotDetection = { candidates: CancellationHotspotCandidate[]; limitations: string[]; };
type DormantCustomerCandidate = { customer_token: string; latest_offering_name: string | null; completed_visit_count: number; last_completed_visit_date: string; days_since_last_completed_visit: number; expected_revisit_days: number; overdue_ratio: number; baseline_source: string; reference_interval_count: number; };
type DormantCustomerDetection = { as_of_date: string; candidates: DormantCustomerCandidate[]; limitations: string[]; };
type ServiceDemandGapCandidate = { offering_name: string; weekday: string; slot_start_hour: number; offering_appointment_count: number; slot_appointment_count: number; slot_offering_appointment_count: number; business_offering_share: number; slot_offering_share: number; expected_slot_offering_appointment_count: number; share_index: number; };
type ServiceDemandGapDetection = { candidates: ServiceDemandGapCandidate[]; limitations: string[]; };
type OpportunityObservation = {
  kind: string;
  observed_weeks?: number | null;
  average_appointments_per_week?: number | null;
  comparison_median_per_week?: number | null;
  demand_index?: number | null;
  appointment_count?: number | null;
  disruption_rate?: number | null;
  rate_multiple?: number | null;
  customer_reference?: string | null;
  days_since_last_completed_visit?: number | null;
  expected_revisit_days?: number | null;
  overdue_ratio?: number | null;
  offering_appointment_count?: number | null;
  slot_appointment_count?: number | null;
  slot_offering_appointment_count?: number | null;
  business_offering_share?: number | null;
  slot_offering_share?: number | null;
  share_index?: number | null;
};
type Opportunity = {
  id: string;
  type: "LOW_DEMAND_SLOT" | "CANCELLATION_HOTSPOT" | "DORMANT_CUSTOMER" | "SERVICE_DEMAND_GAP";
  status: string;
  segment: Record<string, string | number>;
  observation: OpportunityObservation;
  estimate: { value_low: Money; value_high: Money; assumptions: string[]; } | null;
  score: number;
  confidence: number;
  limitations: string[];
  detector: { code: string; version: string; };
};
type Recommendation = { id: string; status: "draft" | "approved" | "rejected" | "modified" | "later"; hypothesis: string; explanation: string; limitations: string[]; };
type Action = { id: string; status: "planned" | "in_progress" | "completed" | "cancelled"; title: string; planned_start_at: string; planned_budget: Money | null; };
type ActionResultData = { id: string; execution_summary: string; measurement_start_at: string; measurement_end_at: string; actual_spend: Money | null; outcome_notes: string | null; };
type Measurement = { observed: { appointment_count: number; completed_count: number; actual_revenue: Money; }; baseline_average: { appointment_count: number; completed_count: number; actual_revenue: Money; } | null; change_from_baseline: { appointment_count: number; completed_count: number; actual_revenue: Money; } | null; limitations: string[]; };

const weekdayLabel: Record<string, string> = { MONDAY: "월", TUESDAY: "화", WEDNESDAY: "수", THURSDAY: "목", FRIDAY: "금", SATURDAY: "토", SUNDAY: "일" };
const money = (value: Money | null) => value ? new Intl.NumberFormat("ko-KR", { style: "currency", currency: value.currency, maximumFractionDigits: 0 }).format(Number(value.amount)) : "—";
const maskedCustomerToken = (value: string) => `${value.slice(0, 8)}…${value.slice(-4)}`;
const opportunityTypeLabel: Record<Opportunity["type"], string> = {
  LOW_DEMAND_SLOT: "수요 저하 · RevenueGap",
  CANCELLATION_HOTSPOT: "취소·노쇼 Hotspot",
  DORMANT_CUSTOMER: "재방문 지연",
  SERVICE_DEMAND_GAP: "Offering 수요 패턴",
};
const opportunitySlotLabel = (opportunity: Opportunity) => {
  const weekday = typeof opportunity.segment.weekday === "string" ? weekdayLabel[opportunity.segment.weekday] : null;
  const hour = typeof opportunity.segment.slot_start_hour === "number" ? opportunity.segment.slot_start_hour : null;
  return weekday && hour !== null ? `${weekday}요일 ${hour.toString().padStart(2, "0")}:00–${(hour + 2).toString().padStart(2, "0")}:00` : null;
};
const opportunitySummary = (opportunity: Opportunity) => {
  const observation = opportunity.observation;
  const slot = opportunitySlotLabel(opportunity);
  if (opportunity.type === "LOW_DEMAND_SLOT") return `${slot ?? "시간대"} · Demand Index ${observation.demand_index?.toFixed(2) ?? "—"}`;
  if (opportunity.type === "CANCELLATION_HOTSPOT") return `${slot ?? "시간대"} · 예약 이탈률 ${observation.disruption_rate !== undefined && observation.disruption_rate !== null ? `${(observation.disruption_rate * 100).toFixed(1)}%` : "—"}`;
  if (opportunity.type === "DORMANT_CUSTOMER") return `가명 고객 ${observation.customer_reference ?? "—"} · 마지막 완료 방문 후 ${observation.days_since_last_completed_visit ?? "—"}일`;
  return `${String(opportunity.segment.offering_name ?? "Offering")} · ${slot ?? "시간대"} · 비중 지수 ${observation.share_index?.toFixed(2) ?? "—"}`;
};
const supportsRecommendation = (opportunity: Opportunity | null) => opportunity?.type === "LOW_DEMAND_SLOT" && opportunity.detector.version === "low-demand-revenue-gap-v2";

export default function Home() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [detection, setDetection] = useState<LowDemandDetection | null>(null);
  const [revenueGap, setRevenueGap] = useState<RevenueGapDetection | null>(null);
  const [cancellationHotspot, setCancellationHotspot] = useState<CancellationHotspotDetection | null>(null);
  const [dormantCustomers, setDormantCustomers] = useState<DormantCustomerDetection | null>(null);
  const [serviceDemandGaps, setServiceDemandGaps] = useState<ServiceDemandGapDetection | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [action, setAction] = useState<Action | null>(null);
  const [actionHistory, setActionHistory] = useState<Action[]>([]);
  const [actionResult, setActionResult] = useState<ActionResultData | null>(null);
  const [measurement, setMeasurement] = useState<Measurement | null>(null);
  const [message, setMessage] = useState("데이터를 불러오고 있습니다…");
  const [recommendationMessage, setRecommendationMessage] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [manualNotes, setManualNotes] = useState("");
  const [actionTitle, setActionTitle] = useState("");
  const [actionNotes, setActionNotes] = useState("");
  const [actionStartAt, setActionStartAt] = useState("");
  const [actionEndAt, setActionEndAt] = useState("");
  const [actionBudget, setActionBudget] = useState("");
  const [executionSummary, setExecutionSummary] = useState("");
  const [measurementStartAt, setMeasurementStartAt] = useState("");
  const [measurementEndAt, setMeasurementEndAt] = useState("");
  const [actualSpend, setActualSpend] = useState("");
  const [outcomeNotes, setOutcomeNotes] = useState("");
  const [resultMessage, setResultMessage] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const me = await fetch(`${apiBaseUrl}/auth/me`, { credentials: "include" });
        if (me.status === 401) { window.location.assign("/login"); return; }
        if (!me.ok) { setMessage("로그인 정보를 확인하지 못했습니다."); return; }
        const currentUser = await me.json() as { active_tenant_id?: string | null };
        if (!currentUser.active_tenant_id) { window.location.assign("/onboarding"); return; }
        const businessesResponse = await fetch(`${apiBaseUrl}/businesses`, { credentials: "include" });
        if (!businessesResponse.ok) { setMessage("병원 정보를 불러오지 못했습니다."); return; }
        const currentBusiness = (await businessesResponse.json() as Business[])[0];
        if (!currentBusiness) { window.location.assign("/onboarding/business"); return; }
        setBusiness(currentBusiness);
        const actionHistoryResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/actions`, { credentials: "include" });
        if (actionHistoryResponse.ok) setActionHistory(await actionHistoryResponse.json() as Action[]);
        const metricsResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/metrics/appointments`, { credentials: "include" });
        if (!metricsResponse.ok) { setMessage("예약 지표를 불러오지 못했습니다."); return; }
        setMetrics(await metricsResponse.json() as Metrics);
        const detectorResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/low-demand-slots`, { credentials: "include" });
        if (detectorResponse.ok) setDetection(await detectorResponse.json() as LowDemandDetection);
        const revenueGapResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/revenue-gaps`, { credentials: "include" });
        if (revenueGapResponse.ok) setRevenueGap(await revenueGapResponse.json() as RevenueGapDetection);
        const cancellationHotspotResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/cancellation-hotspots`, { credentials: "include" });
        if (cancellationHotspotResponse.ok) setCancellationHotspot(await cancellationHotspotResponse.json() as CancellationHotspotDetection);
        const asOfDate = new Date().toISOString().slice(0, 10);
        const dormantCustomerResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/dormant-customers?as_of_date=${asOfDate}`, { credentials: "include" });
        if (dormantCustomerResponse.ok) setDormantCustomers(await dormantCustomerResponse.json() as DormantCustomerDetection);
        const serviceDemandGapResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/service-demand-gaps`, { credentials: "include" });
        if (serviceDemandGapResponse.ok) setServiceDemandGaps(await serviceDemandGapResponse.json() as ServiceDemandGapDetection);
        const opportunitiesResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/opportunities`, { credentials: "include" });
        if (opportunitiesResponse.ok) {
          const storedOpportunities = await opportunitiesResponse.json() as Opportunity[];
          setOpportunities(storedOpportunities);
          const currentOpportunity = storedOpportunities.find((item) => item.detector.version === "low-demand-revenue-gap-v2") ?? storedOpportunities[0] ?? null;
          if (currentOpportunity) await selectOpportunity(currentOpportunity);
        }
        setMessage("");
      } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    }
    loadDashboard();
  }, []);

  async function loadActionResult(actionId: string) {
    const resultResponse = await fetch(`${apiBaseUrl}/actions/${actionId}/results`, { credentials: "include" });
    if (!resultResponse.ok) return;
    setActionResult(await resultResponse.json() as ActionResultData);
    const measurementResponse = await fetch(`${apiBaseUrl}/actions/${actionId}/measurements`, { credentials: "include" });
    if (measurementResponse.ok) setMeasurement(await measurementResponse.json() as Measurement);
  }

  async function selectOpportunity(selected: Opportunity) {
    setOpportunity(selected);
    setRecommendation(null);
    setAction(null);
    setActionResult(null);
    setMeasurement(null);
    setRecommendationMessage("");
    setActionMessage("");
    setResultMessage("");
    if (!supportsRecommendation(selected)) return;
    const recommendationsResponse = await fetch(`${apiBaseUrl}/opportunities/${selected.id}/recommendations`, { credentials: "include" });
    if (!recommendationsResponse.ok) return;
    const currentRecommendation = (await recommendationsResponse.json() as Recommendation[])[0] ?? null;
    setRecommendation(currentRecommendation);
    if (!currentRecommendation) return;
    const actionsResponse = await fetch(`${apiBaseUrl}/recommendations/${currentRecommendation.id}/actions`, { credentials: "include" });
    if (!actionsResponse.ok) return;
    const currentAction = (await actionsResponse.json() as Action[])[0] ?? null;
    setAction(currentAction);
    if (currentAction?.status === "completed") await loadActionResult(currentAction.id);
  }

  async function createRecommendationDraft() {
    if (!opportunity) return;
    setRecommendationMessage("추천 초안을 만들고 있습니다…");
    const response = await fetch(`${apiBaseUrl}/opportunities/${opportunity.id}/recommendations/draft`, { method: "POST", credentials: "include" });
    if (!response.ok) { setRecommendationMessage("추천 초안을 만들지 못했습니다. 권한과 API 상태를 확인해 주세요."); return; }
    setRecommendation(await response.json() as Recommendation);
    setRecommendationMessage("추천 초안은 검토용으로만 생성되었습니다. 아직 실행된 작업은 없습니다.");
  }

  async function recordDecision(decision: "approved" | "rejected" | "modified" | "later") {
    if (!recommendation) return;
    setRecommendationMessage("결정을 저장하고 있습니다…");
    const payload = decision === "modified" ? { decision, modified_payload: { manual_notes: manualNotes || "수동 검토 후 조정" } } : { decision };
    const response = await fetch(`${apiBaseUrl}/recommendations/${recommendation.id}/decisions`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!response.ok) { setRecommendationMessage("결정을 저장하지 못했습니다. 권한과 입력 내용을 확인해 주세요."); return; }
    setRecommendation(await response.json() as Recommendation);
    setRecommendationMessage("결정만 기록되었습니다. 고객 메시지·광고·쿠폰 등 외부 실행은 전혀 수행되지 않았습니다.");
  }

  async function createAction() {
    if (!recommendation || !actionTitle || !actionStartAt) { setActionMessage("Action 제목과 예정 시작 시각을 입력해 주세요."); return; }
    setActionMessage("수동 Action 계획을 저장하고 있습니다…");
    const payload = {
      title: actionTitle,
      execution_notes: actionNotes || null,
      planned_start_at: new Date(actionStartAt).toISOString(),
      planned_end_at: actionEndAt ? new Date(actionEndAt).toISOString() : null,
      planned_budget: actionBudget ? { amount: actionBudget, currency: "KRW" } : null,
    };
    const response = await fetch(`${apiBaseUrl}/recommendations/${recommendation.id}/actions`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const body = await response.json();
    if (!response.ok) { setActionMessage(body.error?.message ?? "Action 계획을 저장하지 못했습니다."); return; }
    setAction(body.action as Action);
    setActionHistory((current) => [body.action as Action, ...current.filter((item) => item.id !== body.action.id)]);
    setActionMessage("Action 계획만 저장되었습니다. 외부 실행은 수행되지 않았습니다.");
  }

  async function updateActionStatus(status: "in_progress" | "completed" | "cancelled") {
    if (!action) return;
    setActionMessage("Action 상태를 저장하고 있습니다…");
    const response = await fetch(`${apiBaseUrl}/actions/${action.id}`, { method: "PATCH", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
    const body = await response.json();
    if (!response.ok) { setActionMessage(body.error?.message ?? "Action 상태를 저장하지 못했습니다."); return; }
    setAction(body as Action);
    setActionHistory((current) => [body as Action, ...current.filter((item) => item.id !== body.id)]);
    setActionMessage(status === "completed" ? "완료를 기록했습니다. 아래에서 실행 결과와 측정 기간을 입력해 주세요." : "상태 이력을 저장했습니다.");
  }

  async function recordActionResult() {
    if (!action || !executionSummary || !measurementStartAt || !measurementEndAt) { setResultMessage("실행 요약과 측정 시작·종료 시각을 입력해 주세요."); return; }
    setResultMessage("실행 결과를 저장하고 예약 데이터를 측정하고 있습니다…");
    const response = await fetch(`${apiBaseUrl}/actions/${action.id}/results`, {
      method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ execution_summary: executionSummary, measurement_start_at: new Date(measurementStartAt).toISOString(), measurement_end_at: new Date(measurementEndAt).toISOString(), actual_spend: actualSpend ? { amount: actualSpend, currency: "KRW" } : null, outcome_notes: outcomeNotes || null }),
    });
    const body = await response.json();
    if (!response.ok) { setResultMessage(body.error?.message ?? "실행 결과를 저장하지 못했습니다."); return; }
    setActionResult(body.result as ActionResultData);
    const measurementResponse = await fetch(`${apiBaseUrl}/actions/${action.id}/measurements`, { credentials: "include" });
    if (measurementResponse.ok) setMeasurement(await measurementResponse.json() as Measurement);
    setResultMessage("결과와 관찰 기반 비교를 저장했습니다. 변화량은 인과효과나 추가매출을 뜻하지 않습니다.");
  }

  const topSlots = useMemo(() => [...(metrics?.time_slots ?? [])].sort((a, b) => b.appointment_count - a.appointment_count).slice(0, 5), [metrics]);
  const topCandidate = detection?.candidates[0] ?? null;
  const topRevenueGap = revenueGap?.candidates[0] ?? null;
  const topCancellationHotspot = cancellationHotspot?.candidates[0] ?? null;
  const topDormantCustomer = dormantCustomers?.candidates[0] ?? null;
  const topServiceDemandGap = serviceDemandGaps?.candidates[0] ?? null;
  const cards = metrics ? [
    { label: "실제 완료 매출", value: money(metrics.actual_revenue), change: "completed 예약의 paid_amount 합계", icon: "₩", tone: "violet" },
    { label: "전체 예약", value: metrics.appointment_count.toLocaleString("ko-KR"), change: `${metrics.observed_weeks}주 관측`, icon: "▦", tone: "mint" },
    { label: "완료 방문", value: metrics.completed_count.toLocaleString("ko-KR"), change: `노쇼 ${metrics.no_show_count.toLocaleString("ko-KR")}건`, icon: "✓", tone: "blue" },
    { label: "취소율", value: `${(metrics.cancellation_rate * 100).toFixed(1)}%`, change: `취소 ${metrics.cancelled_count.toLocaleString("ko-KR")}건`, icon: "×", tone: "pink" },
  ] : [];

  return <main className="app-shell">
    <aside className="sidebar"><div className="brand"><span>◒</span> LOOFIO</div><div className="workspace-name">{business?.name ?? "병원 선택"} <span>⌄</span></div><nav aria-label="Main navigation">{navigation.map(([icon, item], index) => <a className={index === 0 ? "active" : ""} href={item === "Data" ? "/data" : "/"} key={item}><span>{icon}</span>{item}</a>)}</nav><div className="sidebar-note"><span>✦</span><strong>예약 데이터에서<br />다음 기회를 찾으세요.</strong><a href="/data">데이터 업로드 →</a></div><a className="account" href="/login"><div>↗</div><p><strong>계정</strong><small>로그인 관리</small></p><span>›</span></a></aside>
    <section className="workspace">
      <header><div><p className="breadcrumb">Dashboard <span>›</span> 예약 Observation</p><h1>병원 현황 <span>✦</span></h1><p className="subtitle">{business ? `${business.name} · ${business.location_name}의 저장된 예약 데이터입니다.` : "예약 데이터를 기준으로 사실을 계산합니다."}</p></div><a className="date-button" href="/data">▣ 데이터 업로드</a></header>
      {message && <p className="dashboard-message">{message}</p>}
      {metrics && metrics.appointment_count === 0 && <div className="dashboard-notice"><strong>아직 저장된 예약이 없습니다.</strong><p>Hospital v1 형식의 CSV를 업로드하면 실제 예약·매출 Observation을 표시합니다.</p><a href="/data">예약 CSV 업로드 →</a></div>}
      {metrics && metrics.appointment_count > 0 && <>
        <div className="metric-grid">{cards.map((card) => <article className="metric-card" key={card.label}><div className={`metric-icon ${card.tone}`}>{card.icon}</div><p>{card.label}</p><strong>{card.value}</strong><small>{card.change}</small></article>)}</div>
        <div className="content-grid"><article className="chart-card"><div className="card-title"><div><h2>요일 × 2시간 예약 수요</h2><p>저장된 예약을 기준으로 계산한 Observation입니다.</p></div></div><div className="slot-list">{topSlots.map((slot) => <div key={`${slot.weekday}-${slot.slot_start_hour}`}><strong>{weekdayLabel[slot.weekday]}요일 {slot.slot_start_hour.toString().padStart(2, "0")}:00–{(slot.slot_start_hour + 2).toString().padStart(2, "0")}:00</strong><span>예약 {slot.appointment_count} · 완료 {slot.completed_count} · 취소율 {(slot.cancellation_rate * 100).toFixed(1)}%</span></div>)}</div></article><article className="action-card"><div className="card-title"><div><h2>수요 저하 · RevenueGap</h2><p>예약 격차와 같은 요일 결제 표본을 분리해 계산합니다.</p></div></div><div className="action-priority">{topCandidate ? <><span>Observation</span><strong>{weekdayLabel[topCandidate.weekday]}요일 {topCandidate.slot_start_hour.toString().padStart(2, "0")}:00–{(topCandidate.slot_start_hour + 2).toString().padStart(2, "0")} 수요 저하</strong><p>주 평균 예약 {topCandidate.average_appointments_per_week}건 · 같은 요일 비교 중앙값 {topCandidate.comparison_median_per_week}건 · Demand Index {topCandidate.demand_index}</p>{topRevenueGap ? <p><b>RevenueGap Estimate</b> · 월 {money(topRevenueGap.monthly_value_low)}–{money(topRevenueGap.monthly_value_high)} · 주간 예약 격차 {topRevenueGap.weekly_booking_gap}건 · 비교 결제 표본 {topRevenueGap.completed_payment_sample_count}건</p> : <p><b>RevenueGap</b> · {revenueGap?.limitations.at(-1) ?? "결제 표본을 확인하고 있습니다."}</p>}</> : <><span>관측 부족 또는 후보 없음</span><strong>수요 저하 후보를 확정하지 않았습니다.</strong><p>{detection?.limitations[0] ?? "Detector 결과를 불러오는 중입니다."}</p></>}</div><p className="safety">✓ RevenueGap은 회복 가정의 Estimate이며, 실제 손실·보장 매출·Recommendation이 아닙니다.</p></article></div>
        <article className="opportunity-card cancellation-hotspot-card"><div className="card-title"><div><h2>취소·노쇼 Hotspot</h2><p>요일·2시간 슬롯·Offering별 예약 이탈을 관찰합니다.</p></div></div>{topCancellationHotspot ? <div className="action-priority"><span>Observation</span><strong>{weekdayLabel[topCancellationHotspot.weekday]}요일 {topCancellationHotspot.slot_start_hour.toString().padStart(2, "0")}:00–{(topCancellationHotspot.slot_start_hour + 2).toString().padStart(2, "0")}:00 · {topCancellationHotspot.offering_name}</strong><p>예약 {topCancellationHotspot.appointment_count}건 · 취소 {topCancellationHotspot.cancelled_count}건 · 노쇼 {topCancellationHotspot.no_show_count}건</p><p><b>예약 이탈률 {(topCancellationHotspot.disruption_rate * 100).toFixed(1)}%</b> · 전체 {(topCancellationHotspot.baseline_disruption_rate * 100).toFixed(1)}%의 {topCancellationHotspot.rate_multiple.toFixed(1)}배</p></div> : <div className="action-priority"><span>관측 부족 또는 후보 없음</span><strong>비정상적으로 높은 예약 이탈 구간을 확정하지 않았습니다.</strong><p>{cancellationHotspot?.limitations[1] ?? "Detector 결과를 불러오는 중입니다."}</p></div>}<p className="safety">✓ 취소·노쇼 패턴은 Observation이며, 원인·매출 손실·Recommendation이 아닙니다.</p></article>
        <article className="opportunity-card dormant-customer-card"><div className="card-title"><div><h2>재방문 지연 후보</h2><p>가명 고객 토큰의 완료 방문 간격을 기준으로 관찰합니다.</p></div></div>{topDormantCustomer ? <div className="action-priority"><span>Observation · {dormantCustomers?.as_of_date} 기준</span><strong>{maskedCustomerToken(topDormantCustomer.customer_token)} · {topDormantCustomer.latest_offering_name ?? "Offering 미지정"}</strong><p>마지막 완료 방문 {topDormantCustomer.last_completed_visit_date} · 경과 {topDormantCustomer.days_since_last_completed_visit}일</p><p><b>기대 재방문 {topDormantCustomer.expected_revisit_days.toFixed(1)}일</b> · 지연 비율 {topDormantCustomer.overdue_ratio.toFixed(1)}배 · 기준 {topDormantCustomer.baseline_source}</p></div> : <div className="action-priority"><span>관측 부족 또는 후보 없음</span><strong>재방문 지연 후보를 확정하지 않았습니다.</strong><p>{dormantCustomers?.limitations[1] ?? "Detector 결과를 불러오는 중입니다."}</p></div>}<p className="safety">✓ 이는 이탈 판정이나 고객 메시지 제안이 아닌, 재방문 간격 기반 Observation입니다.</p></article>
        <article className="opportunity-card service-demand-gap-card"><div className="card-title"><div><h2>Offering 수요 패턴</h2><p>Offering의 전체 예약 비중과 요일·시간대 비중을 비교합니다.</p></div></div>{topServiceDemandGap ? <div className="action-priority"><span>Observation</span><strong>{topServiceDemandGap.offering_name} · {weekdayLabel[topServiceDemandGap.weekday]}요일 {topServiceDemandGap.slot_start_hour.toString().padStart(2, "0")}:00–{(topServiceDemandGap.slot_start_hour + 2).toString().padStart(2, "0")}:00</strong><p>해당 슬롯 예약 {topServiceDemandGap.slot_appointment_count}건 중 {topServiceDemandGap.offering_name} {topServiceDemandGap.slot_offering_appointment_count}건</p><p><b>슬롯 비중 {(topServiceDemandGap.slot_offering_share * 100).toFixed(1)}%</b> · 전체 비중 {(topServiceDemandGap.business_offering_share * 100).toFixed(1)}%의 {topServiceDemandGap.share_index.toFixed(2)}배</p></div> : <div className="action-priority"><span>관측 부족 또는 후보 없음</span><strong>상대 수요 저하 Offering 구간을 확정하지 않았습니다.</strong><p>{serviceDemandGaps?.limitations[1] ?? "Detector 결과를 불러오는 중입니다."}</p></div>}<p className="safety">✓ 상대 예약 비중의 Observation이며, 빈 슬롯·매출 기회·할인 효과를 뜻하지 않습니다.</p></article>
        {opportunities.length > 0 && <article className="opportunity-card opportunity-list-card"><div className="card-title"><div><h2>저장된 Opportunity</h2><p>Detector가 생성·갱신한 후보입니다. Observation과 Estimate, Recommendation을 구분해 표시합니다.</p></div><span className="opportunity-count">{opportunities.length}개</span></div><div className="opportunity-list">{opportunities.map((item) => <button className={item.id === opportunity?.id ? "selected" : ""} key={item.id} onClick={() => void selectOpportunity(item)}><div><span>{opportunityTypeLabel[item.type]}</span><strong>{opportunitySummary(item)}</strong><small>{item.detector.version} · 신뢰도 {(item.confidence * 100).toFixed(0)}%</small></div><div className="opportunity-list-estimate">{item.estimate ? <><b>Estimate</b><strong>{money(item.estimate.value_low)}–{money(item.estimate.value_high)}</strong></> : <><b>Observation</b><strong>추정 없음</strong></>}</div></button>)}</div><p className="safety">✓ Observation 전용 Opportunity는 원인·매출 손실·외부 실행을 뜻하지 않으며, 현재 Recommendation을 만들지 않습니다.</p></article>}
        {opportunity && <article className="opportunity-card recommendation-card"><div className="card-title"><div><h2>Recommendation · 사용자 결정</h2><p>Observation과 Estimate를 바꾸지 않는 검토용 실행 가설입니다.</p></div></div>{supportsRecommendation(opportunity) ? <>{recommendation ? <div className="recommendation-body"><span>상태 · {recommendation.status}</span><strong>{recommendation.hypothesis}</strong><p>{recommendation.explanation}</p><ul className="limitations">{recommendation.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul><label>수정 메모 <input value={manualNotes} onChange={(event) => setManualNotes(event.target.value)} maxLength={500} placeholder="수동 검토 시 조정할 내용을 기록하세요" /></label><div className="recommendation-actions"><button className="primary" onClick={() => recordDecision("approved")}>승인 기록</button><button className="ghost" onClick={() => recordDecision("modified")}>수정 기록</button><button className="ghost" onClick={() => recordDecision("later")}>나중에</button><button className="ghost" onClick={() => recordDecision("rejected")}>거절</button></div></div> : <div className="recommendation-body"><p>이 Opportunity의 Observation·Estimate·한계를 바꾸지 않는 수동 실험 초안을 만들 수 있습니다.</p><button className="primary" onClick={createRecommendationDraft}>추천 초안 만들기</button></div>}{recommendationMessage && <p className="recommendation-message">{recommendationMessage}</p>}</> : <div className="recommendation-body"><span>Observation 전용</span><strong>{opportunityTypeLabel[opportunity.type]} 후보를 선택했습니다.</strong><p>현재는 계산된 사실과 한계만 보관합니다. 원인·실제 손실·고객 의도·외부 실행을 가정한 Recommendation은 만들지 않습니다.</p><ul className="limitations">{opportunity.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></div>}</article>}
        {recommendation?.status === "approved" && <article className="opportunity-card action-plan-card"><div className="card-title"><div><h2>Action · 수동 실행 계획</h2><p>계획과 상태 이력만 기록합니다. 외부 실행은 하지 않습니다.</p></div></div>{action ? <div className="recommendation-body"><span>상태 · {action.status}</span><strong>{action.title}</strong><p>예정 시작 {new Date(action.planned_start_at).toLocaleString("ko-KR")}{action.planned_budget ? ` · 예정 예산 ${money(action.planned_budget)}` : ""}</p><div className="recommendation-actions">{action.status === "planned" && <><button className="primary" onClick={() => updateActionStatus("in_progress")}>실행 시작 기록</button><button className="ghost" onClick={() => updateActionStatus("cancelled")}>취소 기록</button></>}{action.status === "in_progress" && <><button className="primary" onClick={() => updateActionStatus("completed")}>완료 기록</button><button className="ghost" onClick={() => updateActionStatus("cancelled")}>취소 기록</button></>}</div></div> : <div className="action-form"><label>Action 제목 <input value={actionTitle} onChange={(event) => setActionTitle(event.target.value)} maxLength={160} placeholder="예: 화요일 오후 수동 혜택 실험" /></label><label>예정 시작 <input type="datetime-local" value={actionStartAt} onChange={(event) => setActionStartAt(event.target.value)} /></label><label>예정 종료 (선택) <input type="datetime-local" value={actionEndAt} onChange={(event) => setActionEndAt(event.target.value)} /></label><label>예정 예산 KRW (선택) <input inputMode="decimal" value={actionBudget} onChange={(event) => setActionBudget(event.target.value)} placeholder="0" /></label><label>내부 실행 메모 (선택) <input value={actionNotes} onChange={(event) => setActionNotes(event.target.value)} maxLength={1000} placeholder="외부 발송 내용이나 고객 정보는 입력하지 마세요" /></label><button className="primary" onClick={createAction}>수동 Action 계획 저장</button></div>}{actionMessage && <p className="recommendation-message">{actionMessage}</p>}</article>}
        {action?.status === "completed" && <article className="opportunity-card result-card"><div className="card-title"><div><h2>Result · 실행 결과와 측정</h2><p>실행 메모는 사람이 기록하고, 실제 완료 매출은 저장된 예약 데이터로만 계산합니다.</p></div></div>{actionResult ? <div className="recommendation-body"><span>결과 기록 완료</span><strong>{actionResult.execution_summary}</strong><p>측정 기간 {new Date(actionResult.measurement_start_at).toLocaleString("ko-KR")}–{new Date(actionResult.measurement_end_at).toLocaleString("ko-KR")}{actionResult.actual_spend ? ` · 실제 지출 ${money(actionResult.actual_spend)}` : ""}</p>{measurement && <div className="measurement-summary"><p><b>관찰 실제 완료 매출</b> {money(measurement.observed.actual_revenue)} · 예약 {measurement.observed.appointment_count}건 · 완료 {measurement.observed.completed_count}건</p>{measurement.baseline_average && <p><b>직전 4주 동일 창 평균</b> {money(measurement.baseline_average.actual_revenue)} · 차이 {money(measurement.change_from_baseline?.actual_revenue ?? null)}</p>}<small>{measurement.limitations[0]}</small></div>}</div> : <div className="action-form"><label>실행 요약 <input value={executionSummary} onChange={(event) => setExecutionSummary(event.target.value)} maxLength={1000} placeholder="실제로 수행한 내용을 간단히 기록하세요" /></label><label>측정 시작 <input type="datetime-local" value={measurementStartAt} onChange={(event) => setMeasurementStartAt(event.target.value)} /></label><label>측정 종료 <input type="datetime-local" value={measurementEndAt} onChange={(event) => setMeasurementEndAt(event.target.value)} /></label><label>실제 지출 KRW (선택) <input inputMode="decimal" value={actualSpend} onChange={(event) => setActualSpend(event.target.value)} placeholder="0" /></label><label>결과 메모 (선택) <input value={outcomeNotes} onChange={(event) => setOutcomeNotes(event.target.value)} maxLength={1000} placeholder="고객 개인정보나 외부 채널 원문은 입력하지 마세요" /></label><button className="primary" onClick={recordActionResult}>결과 기록 및 측정</button></div>}{resultMessage && <p className="recommendation-message">{resultMessage}</p>}<p className="safety">✓ 동일 시간대의 단순 비교이며, Action 효과·추가매출·ROI를 단정하지 않습니다.</p></article>}
        {actionHistory.length > 0 && <article className="opportunity-card action-history-card"><div className="card-title"><div><h2>최근 Action 이력</h2><p>이 사업장에 기록된 수동 실행의 상태입니다.</p></div></div><div className="action-history-list">{actionHistory.slice(0, 5).map((item) => <div key={item.id}><span>상태 · {item.status}</span><strong>{item.title}</strong><small>{new Date(item.planned_start_at).toLocaleString("ko-KR")}{item.planned_budget ? ` · 예정 예산 ${money(item.planned_budget)}` : ""}</small></div>)}</div><p className="safety">✓ 이력은 실행 상태를 보여주며, 성과 인과관계를 의미하지 않습니다.</p></article>}
        <article className="opportunity-card"><div className="card-title"><div><h2>계산 범위와 한계</h2><p>실제 데이터와 추정치를 혼합하지 않습니다.</p></div></div><ul className="limitations">{[...metrics.limitations, ...(detection?.limitations ?? []), ...(cancellationHotspot?.limitations ?? []), ...(dormantCustomers?.limitations ?? []), ...(serviceDemandGaps?.limitations ?? [])].map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></article>
      </>}
      <footer>ⓘ 실제 완료 매출은 완료된 예약의 결제금액만 합산합니다. 예상 효과는 아직 표시하지 않습니다.</footer>
    </section>
  </main>;
}
