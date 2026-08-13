"use client";

import { FormEvent, useEffect, useState } from "react";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type CurrentUser = { display_name?: string | null; active_tenant_id?: string | null };

export default function OnboardingPage() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [tenantName, setTenantName] = useState("");
  const [message, setMessage] = useState("계정 정보를 확인하고 있습니다…");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetch(`${apiBaseUrl}/auth/me`, { credentials: "include" }).then(async (response) => {
      if (response.status === 401) { window.location.assign("/login"); return; }
      if (!response.ok) { setMessage("로그인 정보를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요."); return; }
      const currentUser = await response.json() as CurrentUser;
      if (currentUser.active_tenant_id) { window.location.assign("/"); return; }
      setUser(currentUser);
      setMessage("");
    }).catch(() => setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."));
  }, []);

  async function createTenant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!tenantName.trim()) { setMessage("사업자 또는 의료그룹 이름을 입력해 주세요."); return; }
    setIsSaving(true); setMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/auth/tenants`, {
        method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: tenantName }),
      });
      if (!response.ok) { const payload = await response.json(); setMessage(payload.error?.message ?? "Tenant를 만들지 못했습니다."); return; }
      window.location.assign("/");
    } catch { setMessage("API에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."); }
    finally { setIsSaving(false); }
  }

  return <main className="onboarding-shell"><section className="onboarding-card"><a className="login-brand" href="/"><span>◒</span> LOOFIO</a><p className="eyebrow">Welcome</p><h1>{user?.display_name ? `${user.display_name}님, 반갑습니다.` : "시작할 준비가 됐어요."}</h1><p>먼저 업무와 데이터가 분리될 조직 단위를 만듭니다. 병원 그룹, 개인 사업자, 법인명 중 관리하기 편한 이름을 사용하세요.</p><form onSubmit={createTenant}><label htmlFor="tenant-name">Tenant 이름</label><input id="tenant-name" value={tenantName} onChange={(event) => setTenantName(event.target.value)} placeholder="예: LOOFIO 피부과" maxLength={120} autoFocus /><small>나중에 여러 병원·지점을 이 Tenant 아래에 추가할 수 있습니다.</small><button disabled={isSaving || !user}>{isSaving ? "만드는 중…" : "Tenant 만들기"}</button></form>{message && <p className="onboarding-message">{message}</p>}</section></main>;
}
