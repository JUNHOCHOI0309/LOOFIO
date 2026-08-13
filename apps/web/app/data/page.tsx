"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";

import "./import.css";

type PreviewRow = { source_record_id: string; visit_start_at: string; offering_name: string; status: string; customer_token_present: boolean; };
type Preview = { total_rows: number; valid_rows: number; invalid_rows: number; errors: string[]; preview: PreviewRow[]; };
type Business = { business_id: string; name: string; location_name: string; };
type ImportResult = { import_id: string; imported_rows: number; duplicate_rows: number; replayed: boolean; };

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function DataImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessId, setBusinessId] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [message, setMessage] = useState<string | null>("병원 정보를 확인하고 있습니다…");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const idempotencyKey = useRef("");

  useEffect(() => {
    async function loadBusinesses() {
      try {
        const me = await fetch(`${apiBaseUrl}/auth/me`, { credentials: "include" });
        if (me.status === 401) { window.location.assign("/login"); return; }
        if (!me.ok) { setMessage("로그인 정보를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요."); return; }
        const user = await me.json() as { active_tenant_id?: string | null };
        if (!user.active_tenant_id) { window.location.assign("/onboarding"); return; }
        const response = await fetch(`${apiBaseUrl}/businesses`, { credentials: "include" });
        if (!response.ok) { setMessage("병원 목록을 불러오지 못했습니다."); return; }
        const records = await response.json() as Business[];
        const uniqueBusinesses = records.filter((record, index) => records.findIndex((item) => item.business_id === record.business_id) === index);
        if (!uniqueBusinesses.length) { window.location.assign("/onboarding/business"); return; }
        setBusinesses(uniqueBusinesses); setBusinessId(uniqueBusinesses[0].business_id); setMessage(null);
      } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    }
    loadBusinesses();
  }, []);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected); setPreview(null); setResult(null); setMessage(null);
    idempotencyKey.current = selected ? crypto.randomUUID() : "";
  }

  async function previewCsv() {
    if (!file || !businessId) { setMessage("병원과 appointments.csv 파일을 선택해 주세요."); return; }
    setIsLoading(true); setMessage(null); setResult(null);
    const body = new FormData(); body.append("file", file);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments/preview`, { method: "POST", body, credentials: "include" });
      const payload = await response.json();
      if (!response.ok) { setPreview(null); setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "파일을 검증하지 못했습니다."); return; }
      setPreview(payload);
    } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    finally { setIsLoading(false); }
  }

  async function saveCsv() {
    if (!file || !businessId || !preview || preview.invalid_rows) { return; }
    setIsSaving(true); setMessage(null);
    const body = new FormData(); body.append("file", file);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments`, { method: "POST", body, credentials: "include", headers: { "Idempotency-Key": idempotencyKey.current || crypto.randomUUID() } });
      const payload = await response.json();
      if (!response.ok) { setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "예약 데이터를 저장하지 못했습니다."); return; }
      setResult(payload as ImportResult); setMessage(null);
    } catch { setMessage("API에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."); }
    finally { setIsSaving(false); }
  }

  return <main className="import-shell"><section className="import-page"><a className="back-link" href="/">← Dashboard</a><p className="eyebrow">Data · CSV Import</p><h1>예약 데이터를 가져오세요.</h1><p className="description">선택한 병원의 예약 데이터를 먼저 검증한 뒤 저장합니다. 유효하지 않은 행은 저장되지 않으며, 같은 요청을 다시 보내도 중복 저장되지 않습니다.</p>
    <article className="upload-card"><div className="file-icon">↑</div><h2>appointments.csv 업로드</h2><p>UTF-8 CSV · 최대 20개 행을 정규화해 미리 보여줍니다.</p><label className="select-label" htmlFor="business">저장할 병원</label><select id="business" className="business-select" value={businessId} onChange={(event) => { setBusinessId(event.target.value); setPreview(null); setResult(null); }} disabled={!businesses.length}>{businesses.map((business) => <option key={business.business_id} value={business.business_id}>{business.name} · {business.location_name}</option>)}</select><label className="file-control"><input type="file" accept=".csv,text/csv" onChange={selectFile} />파일 선택</label><p className="selected-file">{file ? file.name : "선택된 파일 없음"}</p><button className="preview-button" disabled={isLoading || !businessId} onClick={previewCsv}>{isLoading ? "검증 중…" : "데이터 미리보기"}</button>{preview && preview.invalid_rows === 0 && <button className="save-button" disabled={isSaving} onClick={saveCsv}>{isSaving ? "저장 중…" : "검증된 데이터 저장"}</button>}{message && <p className="import-message">{message}</p>}</article>
    <article className="contract-card"><h2>필수 컬럼</h2><code>appointment_id, visit_start_at, offering_name, status</code><p>시간은 UTC offset을 포함한 ISO-8601 형식이어야 하며, 고객 정보는 평문이 아닌 가명 토큰만 허용합니다.</p></article>
    {preview && <section className="preview-result"><div className="result-header"><div><p className="eyebrow">Validation Result</p><h2>파일 검증 결과</h2></div><span className={preview.invalid_rows ? "warning" : "success"}>{preview.invalid_rows ? "검토 필요" : "저장 가능"}</span></div><div className="result-summary"><div><span>전체 행</span><strong>{preview.total_rows}</strong></div><div><span>유효 행</span><strong className="green">{preview.valid_rows}</strong></div><div><span>오류 행</span><strong className="red">{preview.invalid_rows}</strong></div></div>{preview.errors.length > 0 && <div className="error-list"><strong>오류 상세</strong>{preview.errors.map((error) => <p key={error}>• {error}</p>)}</div>}{preview.preview.length > 0 && <div className="preview-table"><h3>정규화 미리보기</h3><table><thead><tr><th>원본 ID</th><th>방문 시작</th><th>Offering</th><th>상태</th><th>고객 토큰</th></tr></thead><tbody>{preview.preview.map((row) => <tr key={row.source_record_id}><td>{row.source_record_id}</td><td>{new Date(row.visit_start_at).toLocaleString("ko-KR")}</td><td>{row.offering_name}</td><td><span className="status-pill">{row.status}</span></td><td>{row.customer_token_present ? "있음" : "없음"}</td></tr>)}</tbody></table></div>}</section>}
    {result && <section className="preview-result import-complete"><p className="eyebrow">Import Complete</p><h2>예약 데이터를 저장했습니다.</h2><p>{result.imported_rows}건을 새로 저장했고, {result.duplicate_rows}건은 이미 등록된 원본 레코드라 건너뛰었습니다.</p><small>Import ID: {result.import_id}</small></section>}
  </section></main>;
}
