"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";

import "./import.css";

type PreviewRow = { source_record_id: string; visit_start_at: string; offering_name: string; status: string; customer_token_present: boolean; };
type Preview = { total_rows: number; valid_rows: number; invalid_rows: number; errors: string[]; preview: PreviewRow[]; };
type Business = { business_id: string; name: string; location_name: string; };
type ImportResult = { import_id: string; imported_rows: number; duplicate_rows: number; replayed: boolean; };
type Inspection = { source_columns: string[]; suggested_column_mapping: Record<string, string>; required_columns: string[]; };
type Mapping = { id: string; name: string; column_mapping: Record<string, string>; status_mapping: Record<string, string>; };

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function DataImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [businessId, setBusinessId] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [mappings, setMappings] = useState<Mapping[]>([]);
  const [mappingId, setMappingId] = useState("");
  const [mappingName, setMappingName] = useState("");
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({});
  const [statusMappingText, setStatusMappingText] = useState("");
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
        setBusinesses(uniqueBusinesses); setBusinessId(uniqueBusinesses[0].business_id); await loadMappings(uniqueBusinesses[0].business_id); setMessage(null);
      } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    }
    loadBusinesses();
  }, []);

  async function loadMappings(targetBusinessId: string) {
    const response = await fetch(`${apiBaseUrl}/businesses/${targetBusinessId}/imports/appointments/mappings`, { credentials: "include" });
    if (response.ok) { setMappings(await response.json() as Mapping[]); }
  }

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected); setPreview(null); setResult(null); setInspection(null); setColumnMapping({}); setStatusMappingText(""); setMessage(null);
    idempotencyKey.current = selected ? crypto.randomUUID() : "";
  }

  async function previewCsv() {
    if (!file || !businessId) { setMessage("병원과 appointments.csv 파일을 선택해 주세요."); return; }
    setIsLoading(true); setMessage(null); setResult(null);
    const body = new FormData(); body.append("file", file);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments/inspect`, { method: "POST", body, credentials: "include" });
      const payload = await response.json();
      if (!response.ok) { setInspection(null); setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "파일 헤더를 분석하지 못했습니다."); return; }
      setInspection(payload as Inspection); setColumnMapping((payload as Inspection).suggested_column_mapping); setMappingName(`${file.name.replace(/\.csv$/i, "")} 매핑`);
    } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    finally { setIsLoading(false); }
  }

  async function saveMappingAndPreview() {
    if (!file || !businessId) return;
    const missing = ["appointment_id", "visit_start_at", "offering_name", "status"].filter((field) => !columnMapping[field]);
    if (missing.length) { setMessage(`필수 필드 매핑이 필요합니다: ${missing.join(", ")}`); return; }
    const statusMapping = Object.fromEntries(statusMappingText.split("\n").map((line) => line.trim()).filter(Boolean).map((line) => line.split("=").map((value) => value.trim())).filter((pair) => pair.length === 2));
    setIsSaving(true); setMessage(null);
    try {
      const saveResponse = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments/mappings`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: mappingName || "CSV 매핑", column_mapping: columnMapping, status_mapping: statusMapping }) });
      const savedMapping = await saveResponse.json();
      if (!saveResponse.ok) { setMessage(savedMapping.error?.message ?? "CSV 매핑을 저장하지 못했습니다."); return; }
      setMappingId(savedMapping.id); await loadMappings(businessId);
      const body = new FormData(); body.append("file", file); body.append("mapping_id", savedMapping.id);
      const previewResponse = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments/preview`, { method: "POST", body, credentials: "include" });
      const previewPayload = await previewResponse.json();
      if (!previewResponse.ok) { setMessage(previewPayload.error?.details?.[0] ?? previewPayload.error?.message ?? "매핑된 데이터를 검증하지 못했습니다."); return; }
      setPreview(previewPayload as Preview);
    } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    finally { setIsSaving(false); }
  }

  async function previewSavedMapping() {
    if (!file || !businessId || !mappingId) return;
    setIsLoading(true); setMessage(null); setResult(null);
    const body = new FormData(); body.append("file", file); body.append("mapping_id", mappingId);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments/preview`, { method: "POST", body, credentials: "include" });
      const payload = await response.json();
      if (!response.ok) { setPreview(null); setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "저장된 매핑으로 검증하지 못했습니다."); return; }
      setPreview(payload as Preview);
    } catch { setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요."); }
    finally { setIsLoading(false); }
  }

  async function saveCsv() {
    if (!file || !businessId || !preview || preview.invalid_rows) { return; }
    setIsSaving(true); setMessage(null);
    const body = new FormData(); body.append("file", file); if (mappingId) body.append("mapping_id", mappingId);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/${businessId}/imports/appointments`, { method: "POST", body, credentials: "include", headers: { "Idempotency-Key": idempotencyKey.current || crypto.randomUUID() } });
      const payload = await response.json();
      if (!response.ok) { setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "예약 데이터를 저장하지 못했습니다."); return; }
      setResult(payload as ImportResult);
      const asOfDate = new Date().toISOString().slice(0, 10);
      const refreshResponse = await fetch(`${apiBaseUrl}/businesses/${businessId}/opportunities/refresh?as_of_date=${asOfDate}`, { method: "POST", credentials: "include" });
      if (!refreshResponse.ok) { setMessage("예약 데이터는 저장됐지만 Opportunity 재분석은 완료하지 못했습니다."); return; }
      setMessage(null);
    } catch { setMessage("API에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."); }
    finally { setIsSaving(false); }
  }

  return <main className="import-shell"><section className="import-page"><a className="back-link" href="/">← Dashboard</a><p className="eyebrow">Data · CSV Import</p><h1>예약 데이터를 가져오세요.</h1><p className="description">병원별 CSV 헤더를 먼저 분석하고, 확인한 매핑으로 표준 Appointment를 검증·저장합니다.</p>
    <article className="upload-card"><div className="file-icon">↑</div><h2>appointments.csv 업로드</h2><p>UTF-8 CSV · 헤더를 분석한 뒤 매핑을 확인합니다.</p><label className="select-label" htmlFor="business">저장할 병원</label><select id="business" className="business-select" value={businessId} onChange={(event) => { setBusinessId(event.target.value); setPreview(null); setResult(null); setInspection(null); setMappingId(""); void loadMappings(event.target.value); }} disabled={!businesses.length}>{businesses.map((business) => <option key={business.business_id} value={business.business_id}>{business.name} · {business.location_name}</option>)}</select>{mappings.length > 0 && <><label className="select-label" htmlFor="saved-mapping">저장된 CSV 매핑 (선택)</label><select id="saved-mapping" className="business-select" value={mappingId} onChange={(event) => { setMappingId(event.target.value); setInspection(null); setPreview(null); }}><option value="">새 파일 헤더 분석</option>{mappings.map((mapping) => <option value={mapping.id} key={mapping.id}>{mapping.name}</option>)}</select></>}<label className="file-control"><input type="file" accept=".csv,text/csv" onChange={selectFile} />파일 선택</label><p className="selected-file">{file ? file.name : "선택된 파일 없음"}</p><button className="preview-button" disabled={isLoading || !businessId || !file} onClick={mappingId ? previewSavedMapping : previewCsv}>{isLoading ? "검증 중…" : mappingId ? "저장된 매핑으로 검증" : "파일 헤더 분석"}</button>{message && <p className="import-message">{message}</p>}</article>
    {inspection && <article className="mapping-card"><p className="eyebrow">Column Mapping</p><h2>CSV 열을 확인해 주세요.</h2><p>자동 제안은 저장 전 반드시 확인합니다. 전화번호·이메일 등 평문 개인정보 열은 선택하지 마세요.</p><label>매핑 이름 <input value={mappingName} onChange={(event) => setMappingName(event.target.value)} maxLength={120} /></label>{inspection.required_columns.map((field) => <label key={field}>{field}<select value={columnMapping[field] ?? ""} onChange={(event) => setColumnMapping({ ...columnMapping, [field]: event.target.value })}><option value="">선택하세요</option>{inspection.source_columns.map((column) => <option value={column} key={column}>{column}</option>)}</select></label>)}<details><summary>선택 열 및 상태값 매핑</summary><p>인식된 선택 열은 자동 포함됩니다. 지원되지 않는 상태값만 `원본값=completed` 형식으로 한 줄씩 입력하세요.</p><textarea value={statusMappingText} onChange={(event) => setStatusMappingText(event.target.value)} placeholder={"내원완료=completed\n예약확정=booked"} /></details><button className="save-button" disabled={isSaving} onClick={saveMappingAndPreview}>{isSaving ? "매핑 저장·검증 중…" : "이 매핑 저장 후 데이터 검증"}</button></article>}
    {mappings.length > 0 && <article className="contract-card"><h2>저장된 매핑</h2><p>{mappings.map((mapping) => mapping.name).join(" · ")}</p></article>}
    <article className="contract-card"><h2>필수 컬럼</h2><code>appointment_id, visit_start_at, offering_name, status</code><p>시간은 UTC offset을 포함한 ISO-8601 형식이어야 하며, 고객 정보는 평문이 아닌 가명 토큰만 허용합니다.</p></article>
    {preview && <section className="preview-result"><div className="result-header"><div><p className="eyebrow">Validation Result</p><h2>파일 검증 결과</h2></div><span className={preview.invalid_rows ? "warning" : "success"}>{preview.invalid_rows ? "검토 필요" : "저장 가능"}</span></div><div className="result-summary"><div><span>전체 행</span><strong>{preview.total_rows}</strong></div><div><span>유효 행</span><strong className="green">{preview.valid_rows}</strong></div><div><span>오류 행</span><strong className="red">{preview.invalid_rows}</strong></div></div>{preview.errors.length > 0 && <div className="error-list"><strong>오류 상세</strong>{preview.errors.map((error) => <p key={error}>• {error}</p>)}</div>}{preview.preview.length > 0 && <div className="preview-table"><h3>정규화 미리보기</h3><table><thead><tr><th>원본 ID</th><th>방문 시작</th><th>Offering</th><th>상태</th><th>고객 토큰</th></tr></thead><tbody>{preview.preview.map((row) => <tr key={row.source_record_id}><td>{row.source_record_id}</td><td>{new Date(row.visit_start_at).toLocaleString("ko-KR")}</td><td>{row.offering_name}</td><td><span className="status-pill">{row.status}</span></td><td>{row.customer_token_present ? "있음" : "없음"}</td></tr>)}</tbody></table></div>}</section>}
    {result && <section className="preview-result import-complete"><p className="eyebrow">Import Complete</p><h2>예약 데이터를 저장했습니다.</h2><p>{result.imported_rows}건을 새로 저장했고, {result.duplicate_rows}건은 이미 등록된 원본 레코드라 건너뛰었습니다.</p><small>Import ID: {result.import_id}</small></section>}
  </section></main>;
}
