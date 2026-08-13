"use client";

import { useEffect, useMemo, useState } from "react";

import "./dashboard.css";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const navigation = [["▦", "Dashboard"], ["⊞", "Data"]];

type Business = { business_id: string; name: string; location_name: string; };
type Money = { amount: string; currency: string; };
type Slot = { weekday: string; slot_start_hour: number; appointment_count: number; completed_count: number; cancelled_count: number; cancellation_rate: number; actual_revenue: Money; };
type Metrics = { period_start: string | null; period_end: string | null; observed_weeks: number; appointment_count: number; completed_count: number; cancelled_count: number; no_show_count: number; cancellation_rate: number; actual_revenue: Money; average_completed_revenue: Money | null; time_slots: Slot[]; limitations: string[]; };

const weekdayLabel: Record<string, string> = { MONDAY: "월", TUESDAY: "화", WEDNESDAY: "수", THURSDAY: "목", FRIDAY: "금", SATURDAY: "토", SUNDAY: "일" };
const money = (value: Money | null) => value ? new Intl.NumberFormat("ko-KR", { style: "currency", currency: value.currency, maximumFractionDigits: 0 }).format(Number(value.amount)) : "—";

export default function Home() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
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
        setMessage("");
      } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    }
    loadDashboard();
  }, []);

  const topSlots = useMemo(() => [...(metrics?.time_slots ?? [])].sort((a, b) => b.appointment_count - a.appointment_count).slice(0, 5), [metrics]);
  const cards = metrics ? [
    { label: "실제 완료 매출", value: money(metrics.actual_revenue), change: "completed 예약의 paid_amount 합계", icon: "₩", tone: "violet" },
    { label: "전체 예약", value: metrics.appointment_count.toLocaleString("ko-KR"), change: `${metrics.observed_weeks}주 관측`, icon: "▦", tone: "mint" },
    { label: "완료 방문", value: metrics.completed_count.toLocaleString("ko-KR"), change: `노쇼 ${metrics.no_show_count.toLocaleString("ko-KR")}건`, icon: "✓", tone: "blue" },
    { label: "취소율", value: `${(metrics.cancellation_rate * 100).toFixed(1)}%`, change: `취소 ${metrics.cancelled_count.toLocaleString("ko-KR")}건`, icon: "×", tone: "pink" },
  ] : [];

  return <main className="app-shell"><aside className="sidebar"><div className="brand"><span>◒</span> LOOFIO</div><div className="workspace-name">{business?.name ?? "병원 선택"} <span>⌄</span></div><nav aria-label="Main navigation">{navigation.map(([icon, item], index) => <a className={index === 0 ? "active" : ""} href={item === "Data" ? "/data" : "/"} key={item}><span>{icon}</span>{item}</a>)}</nav><div className="sidebar-note"><span>✦</span><strong>예약 데이터에서<br />다음 기회를 찾으세요.</strong><a href="/data">데이터 업로드 →</a></div><a className="account" href="/login"><div>↗</div><p><strong>계정</strong><small>로그인 관리</small></p><span>›</span></a></aside><section className="workspace"><header><div><p className="breadcrumb">Dashboard <span>›</span> 예약 Observation</p><h1>병원 현황 <span>✦</span></h1><p className="subtitle">{business ? `${business.name} · ${business.location_name}의 저장된 예약 데이터입니다.` : "예약 데이터를 기준으로 사실을 계산합니다."}</p></div><a className="date-button" href="/data">▣ 데이터 업로드</a></header>{message && <p className="dashboard-message">{message}</p>}{metrics && metrics.appointment_count === 0 && <div className="dashboard-notice"><strong>아직 저장된 예약이 없습니다.</strong><p>Hospital v1 형식의 CSV를 업로드하면 실제 예약·매출 Observation을 표시합니다.</p><a href="/data">예약 CSV 업로드 →</a></div>}{metrics && metrics.appointment_count > 0 && <><div className="metric-grid">{cards.map((card) => <article className="metric-card" key={card.label}><div className={`metric-icon ${card.tone}`}>{card.icon}</div><p>{card.label}</p><strong>{card.value}</strong><small>{card.change}</small></article>)}</div><div className="content-grid"><article className="chart-card"><div className="card-title"><div><h2>요일 × 2시간 예약 수요</h2><p>저장된 예약을 기준으로 계산한 Observation입니다.</p></div></div><div className="slot-list">{topSlots.map((slot) => <div key={`${slot.weekday}-${slot.slot_start_hour}`}><strong>{weekdayLabel[slot.weekday]}요일 {slot.slot_start_hour.toString().padStart(2, "0")}:00–{(slot.slot_start_hour + 2).toString().padStart(2, "0")}:00</strong><span>예약 {slot.appointment_count} · 완료 {slot.completed_count} · 취소율 {(slot.cancellation_rate * 100).toFixed(1)}%</span></div>)}</div></article><article className="action-card"><div className="card-title"><div><h2>다음 단계</h2><p>현재는 사실을 계산하는 단계입니다.</p></div></div><div className="action-priority"><span>준비 중</span><strong>수요 저하 Opportunity 탐지</strong><p>최소 8주 이상의 관측치를 바탕으로 상대 수요가 낮은 시간대를 탐지합니다.</p><a className="primary dashboard-link" href="/data">데이터 확인</a></div><p className="safety">✓ 추정 매출과 Recommendation은 Detector 구현 후 별도로 표시됩니다.</p></article></div><article className="opportunity-card"><div className="card-title"><div><h2>계산 범위와 한계</h2><p>실제 데이터와 추정치를 혼합하지 않습니다.</p></div></div><ul className="limitations">{metrics.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul></article></>}<footer>ⓘ 실제 완료 매출은 완료된 예약의 결제금액만 합산합니다. 예상 효과는 아직 표시하지 않습니다.</footer></section></main>;
}
