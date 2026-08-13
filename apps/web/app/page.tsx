"use client";

import { useEffect, useMemo, useState } from "react";

import "./dashboard.css";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const navigation = [["▦", "Dashboard"], ["⊞", "Data"]];

type Business = { business_id: string; name: string; location_name: string; };
type Money = { amount: string; currency: string; };
type Slot = { weekday: string; slot_start_hour: number; appointment_count: number; completed_count: number; cancelled_count: number; cancellation_rate: number; actual_revenue: Money; };
type Metrics = { period_start: string | null; period_end: string | null; observed_weeks: number; appointment_count: number; completed_count: number; cancelled_count: number; no_show_count: number; cancellation_rate: number; actual_revenue: Money; average_completed_revenue: Money | null; time_slots: Slot[]; limitations: string[]; };
type LowDemandCandidate = { weekday: string; slot_start_hour: number; observed_weeks: number; average_appointments_per_week: number; comparison_median_per_week: number; demand_index: number; };
type LowDemandDetection = { candidates: LowDemandCandidate[]; limitations: string[]; };
type Opportunity = { id: string; segment: { weekday: string; start_hour: number; end_hour: number; }; estimate: { value_low: Money; value_high: Money; assumptions: string[]; } | null; confidence: number; };
type Recommendation = { id: string; status: "draft" | "approved" | "rejected" | "modified" | "later"; hypothesis: string; explanation: string; limitations: string[]; latest_decision: { decision: string; reason_text: string | null } | null; };

const weekdayLabel: Record<string, string> = { MONDAY: "월", TUESDAY: "화", WEDNESDAY: "수", THURSDAY: "목", FRIDAY: "금", SATURDAY: "토", SUNDAY: "일" };
const money = (value: Money | null) => value ? new Intl.NumberFormat("ko-KR", { style: "currency", currency: value.currency, maximumFractionDigits: 0 }).format(Number(value.amount)) : "—";

export default function Home() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [detection, setDetection] = useState<LowDemandDetection | null>(null);
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [recommendationMessage, setRecommendationMessage] = useState("");
  const [manualNotes, setManualNotes] = useState("");
  const [message, setMessage] = useState("데이터를 불러오고 있습니다…");

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
        const businesses = await businessesResponse.json() as Business[];
        const currentBusiness = businesses[0];
        if (!currentBusiness) { window.location.assign("/onboarding/business"); return; }
        setBusiness(currentBusiness);
        const metricsResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/metrics/appointments`, { credentials: "include" });
        if (!metricsResponse.ok) { setMessage("예약 지표를 불러오지 못했습니다."); return; }
        setMetrics(await metricsResponse.json() as Metrics);
        const detectorResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/detectors/low-demand-slots`, { credentials: "include" });
        if (detectorResponse.ok) { setDetection(await detectorResponse.json() as LowDemandDetection); }
        const opportunitiesResponse = await fetch(`${apiBaseUrl}/businesses/${currentBusiness.business_id}/opportunities`, { credentials: "include" });
        if (opportunitiesResponse.ok) {
          const currentOpportunity = (await opportunitiesResponse.json() as Opportunity[])[0] ?? null;
          setOpportunity(currentOpportunity);
          if (currentOpportunity) {
            const recommendationsResponse = await fetch(`${apiBaseUrl}/opportunities/${currentOpportunity.id}/recommendations`, { credentials: "include" });
            if (recommendationsResponse.ok) { setRecommendation((await recommendationsResponse.json() as Recommendation[])[0] ?? null); }
          }
        }
        setMessage("");
      } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    }
    loadDashboard();
  }, []);

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

  const topSlots = useMemo(() => [...(metrics?.time_slots ?? [])].sort((a, b) => b.appointment_count - a.appointment_count).slice(0, 5), [metrics]);
  const topCandidate = detection?.candidates[0] ?? null;
  const cards = metrics ? [
    { label: "실제 완료 매출", value: money(metrics.actual_revenue), change: "completed 예약의 paid_amount 합계", icon: "₩", tone: "violet" },
    { label: "전체 예약", value: metrics.appointment_count.toLocaleString("ko-KR"), change: `${metrics.observed_weeks}주 관측`, icon: "▦", tone: "mint" },
    { label: "완료 방문", value: metrics.completed_count.toLocaleString("ko-KR"), change: `노쇼 ${metrics.no_show_count.toLocaleString("ko-KR")}건`, icon: "✓", tone: "blue" },
    { label: "취소율", value: `${(metrics.cancellation_rate * 100).toFixed(1)}%`, change: `취소 ${metrics.cancelled_count.toLocaleString("ko-KR")}건`, icon: "×", tone: "pink" },
  ] : [];

  return <main className="app-shell"><aside className="sidebar"><div className="brand"><span>◒</span> LOOFIO</div><div className="workspace-name">{business?.name ?? "병원 선택"} <span>⌄</span></div><nav aria-label="Main navigation">{navigation.map(([icon, item], index) => <a className={index === 0 ? "active" : ""} href={item === "Data" ? "/data" : "/"} key={item}><span>{icon}</span>{item}</a>)}</nav><div className="sidebar-note"><span>✦</span><strong>예약 데이터에서<br />다음 기회를 찾으세요.</strong><a href="/data">데이터 업로드 →</a></div><a className="account" href="/login"><div>↗</div><p><strong>계정</strong><small>로그인 관리</small></p><span>›</span></a></aside><section className="workspace"><header><div><p className="breadcrumb">Dashboard <span>›</span> 예약 Observation</p><h1>병원 현황 <span>✦</span></h1><p className="subtitle">{business ? `${business.name} · ${business.location_name}의 저장된 예약 데이터입니다.` : "예약 데이터를 기준으로 사실을 계산합니다."}</p></div><a className="date-button" href="/data">▣ 데이터 업로드</a></header>{message && <p className="dashboard-message">{message}</p>}{metrics && metrics.appointment_count === 0 && <div className="dashboard-notice"><strong>아직 저장된 예약이 없습니다.</strong><p>Hospital v1 형식의 CSV를 업로드하면 실제 예약·매출 Observation을 표시합니다.</p><a href="/data">예약 CSV 업로드 →</a></div>}{metrics && metrics.appointment_count > 0 && <><div className="metric-grid">{cards.map((card) => <article className="metric-card" key={card.label}><div className={`metric-icon ${card.tone}`}>{card.icon}</div><p>{card.label}</p><strong>{card.value}</strong><small>{card.change}</small></article>)}</div><div className="content-grid"><article className="chart-card"><div className="card-title"><div><h2>요일 × 2시간 예약 수요</h2><p>저장된 예약을 기준으로 계산한 Observation입니다.</p></div></div><div className="slot-list">{topSlots.map((slot) => <div key={`${slot.weekday}-${slot.slot_start_hour}`}><strong>{weekdayLabel[slot.weekday]}요일 {slot.slot_start_hour.toString().padStart(2, "0")}:00–{(slot.slot_start_hour + 2).toString().padStart(2, "0")}:00</strong><span>예약 {slot.appointment_count} · 완료 {slot.completed_count} · 취소율 {(slot.cancellation_rate * 100).toFixed(1)}%</span></div>)}</div></article><article className="action-card"><div className="card-title"><div><h2>수요 저하 후보</h2><p>Detector가 계산한 Observation입니다.</p></div></div><div className="action-priority">{topCandidate ? <><span>Observation</span><strong>{weekdayLabel[topCandidate.weekday]}요일 {topCandidate.slot_start_hour.toString().padStart(2, "0")}:00–{(topCandidate.slot_start_hour + 2).toString().padStart(2, "0")} 수요 저하</strong><p>주 평균 예약 {topCandidate.average_appointments_per_week}건 · 같은 요일 비교 중앙값 {topCandidate.comparison_median_per_week}건 · Demand Index {topCandidate.demand_index}</p>{opportunity?.estimate && <p><b>Estimate</b> · 월 {money(opportunity.estimate.value_low)}–{money(opportunity.estimate.value_high)} 추가 매출 여지</p>}</> : <><span>관측 부족 또는 후보 없음</span><strong>수요 저하 후보를 확정하지 않았습니다.</strong><p>{detection?.limitations[0] ?? "Detector 결과를 불러오는 중입니다."}</p></>}</div><p className="safety">✓ Estimate는 가정 기반 범위이며, 실제 매출이나 Recommendation이 아닙니다.</p></article></div>{opportunity && <article className="opportunity-card recommendation-card"><div className="card-title"><div><h2>Recommendation · 사용자 결정</h2><p>Observation과 Estimate를 바꾸지 않는 검토용 실행 가설입니다.</p></div></div>{recommendation ? <div className="recommendation-body"><span>상태 · {recommendation.status}</span><strong>{recommendation.hypothesis}</strong><p>{recommendation.explanation}</p><ul className="limitations">{recommendation.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul><label>수정 메모 <input value={manualNotes} onChange={(event) => setManualNotes(event.target.value)} maxLength={500} placeholder="수동 검토 시 조정할 내용을 기록하세요" /></label><div className="recommendation-actions"><button className="primary" onClick={() => recordDecision("approved")}>승인 기록</button><button className="ghost" onClick={() => recordDecision("modified")}>수정 기록</button><button className="ghost" onClick={() => recordDecision("later")}>나중에</button><button className="ghost" onClick={() => recordDecision("rejected")}>거절</button></div></div> : <div className="recommendation-body"><p>이 Opportunity의 Observation·Estimate·한계를 바꾸지 않는 수동 실험 초안을 만들 수 있습니다.</p><button className="primary" onClick={createRecommendationDraft}>추천 초안 만들기</button></div>}{recommendationMessage && <p className="recommendation-message">{recommendationMessage}</p>}</article>}<article className="opportunity-card"><div className="card-title"><div><h2>계산 범위와 한계</h2><p>실제 데이터와 추정치를 혼합하지 않습니다.</p></div></div><ul className="limitations">{[...metrics.limitations, ...(detection?.limitations ?? [])].map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></article></>}<footer>ⓘ 실제 완료 매출은 완료된 예약의 결제금액만 합산합니다. 예상 효과는 아직 표시하지 않습니다.</footer></section></main>;
}
