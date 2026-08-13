"use client";

import { FormEvent, useEffect, useState } from "react";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const specialties = [
  ["DERMATOLOGY", "피부과"],
  ["PLASTIC_SURGERY", "성형외과"],
  ["ORTHOPEDICS", "정형외과"],
  ["OPHTHALMOLOGY", "안과"],
  ["OTOLARYNGOLOGY", "이비인후과"],
] as const;

type Specialty = (typeof specialties)[number][0];

export default function BusinessOnboardingPage() {
  const [businessName, setBusinessName] = useState("");
  const [medicalDomain, setMedicalDomain] = useState<Specialty>("DERMATOLOGY");
  const [locationName, setLocationName] = useState("");
  const [isReady, setIsReady] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("Tenant 정보를 확인하고 있습니다…");

  useEffect(() => {
    fetch(`${apiBaseUrl}/auth/me`, { credentials: "include" }).then(async (response) => {
      if (response.status === 401) { window.location.assign("/login"); return; }
      if (!response.ok) { setMessage("로그인 정보를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요."); return; }
      const user = await response.json() as { active_tenant_id?: string | null };
      if (!user.active_tenant_id) { window.location.assign("/onboarding"); return; }
      setIsReady(true);
      setMessage("");
    }).catch(() => setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."));
  }, []);

  async function createBusiness(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!businessName.trim() || !locationName.trim()) { setMessage("병원명과 첫 지점 이름을 입력해 주세요."); return; }
    setIsSaving(true); setMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/businesses`, {
        method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: businessName, medical_domain: medicalDomain, location_name: locationName, timezone: "Asia/Seoul" }),
      });
      if (!response.ok) { const payload = await response.json(); setMessage(payload.error?.message ?? "병원 정보를 저장하지 못했습니다."); return; }
      window.location.assign("/");
    } catch { setMessage("API에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."); }
    finally { setIsSaving(false); }
  }

  return <main className="onboarding-shell"><section className="onboarding-card"><a className="login-brand" href="/"><span>◒</span> LOOFIO</a><p className="eyebrow">Step 2 of 2</p><h1>첫 병원과 지점을 등록하세요.</h1><p>이 정보는 데이터 업로드와 분석 범위를 정하는 기준입니다. 지점은 이후에도 추가할 수 있습니다.</p><form onSubmit={createBusiness}><label htmlFor="business-name">병원명</label><input id="business-name" value={businessName} onChange={(event) => setBusinessName(event.target.value)} placeholder="예: LOOFIO 피부과" maxLength={120} autoFocus /><label htmlFor="medical-domain">진료 분야</label><select id="medical-domain" value={medicalDomain} onChange={(event) => setMedicalDomain(event.target.value as Specialty)}>{specialties.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><label htmlFor="location-name">첫 지점 이름</label><input id="location-name" value={locationName} onChange={(event) => setLocationName(event.target.value)} placeholder="예: 강남점" maxLength={120} /><small>이후 다른 지점과 의료기관도 현재 Tenant 아래에서 관리합니다.</small><button disabled={isSaving || !isReady}>{isSaving ? "저장 중…" : "병원 등록 완료"}</button></form>{message && <p className="onboarding-message">{message}</p>}</section></main>;
}
