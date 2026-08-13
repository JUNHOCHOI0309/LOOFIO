"use client";

import { ChangeEvent, useState } from "react";

type PreviewRow = {
  source_record_id: string;
  visit_start_at: string;
  offering_name: string;
  status: string;
  customer_token_present: boolean;
};

type Preview = {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  errors: string[];
  preview: PreviewRow[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function DataImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    setPreview(null);
    setMessage(null);
  }

  async function previewCsv() {
    if (!file) {
      setMessage("먼저 appointments.csv 파일을 선택해 주세요.");
      return;
    }
    setIsLoading(true);
    setMessage(null);
    const body = new FormData();
    body.append("file", file);
    try {
      const response = await fetch(`${apiBaseUrl}/businesses/demo-hospital/imports/appointments/preview`, { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) {
        setPreview(null);
        setMessage(payload.error?.details?.[0] ?? payload.error?.message ?? "파일을 검증하지 못했습니다.");
        return;
      }
      setPreview(payload);
    } catch {
      setMessage("API에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해 주세요.");
    } finally {
      setIsLoading(false);
    }
  }

  return <main className="import-shell">
    <section className="import-page">
      <a className="back-link" href="/">← Dashboard</a>
      <p className="eyebrow">Data · CSV Import</p>
      <h1>예약 데이터를 확인하세요.</h1>
      <p className="description">저장하기 전에 Hospital v1 계약에 맞는지 검증합니다. 이 단계에서는 원본 데이터가 저장되거나 외부로 실행되지 않습니다.</p>

      <article className="upload-card">
        <div className="file-icon">↑</div>
        <h2>appointments.csv 업로드</h2>
        <p>UTF-8 CSV · 최대 20개 행을 정규화해 미리 보여줍니다.</p>
        <label className="file-control"><input type="file" accept=".csv,text/csv" onChange={selectFile} />파일 선택</label>
        <p className="selected-file">{file ? file.name : "선택된 파일 없음"}</p>
        <button className="preview-button" disabled={isLoading} onClick={previewCsv}>{isLoading ? "검증 중…" : "데이터 미리보기"}</button>
        {message && <p className="import-message">{message}</p>}
      </article>

      <article className="contract-card"><h2>필수 컬럼</h2><code>appointment_id, visit_start_at, offering_name, status</code><p>시간은 UTC offset을 포함한 ISO-8601 형식이어야 하며, 고객 정보는 평문이 아닌 가명 토큰만 허용합니다.</p></article>

      {preview && <section className="preview-result">
        <div className="result-header"><div><p className="eyebrow">Validation Result</p><h2>파일 검증 결과</h2></div><span className={preview.invalid_rows ? "warning" : "success"}>{preview.invalid_rows ? "검토 필요" : "검증 완료"}</span></div>
        <div className="result-summary"><div><span>전체 행</span><strong>{preview.total_rows}</strong></div><div><span>유효 행</span><strong className="green">{preview.valid_rows}</strong></div><div><span>오류 행</span><strong className="red">{preview.invalid_rows}</strong></div></div>
        {preview.errors.length > 0 && <div className="error-list"><strong>오류 상세</strong>{preview.errors.map((error) => <p key={error}>• {error}</p>)}</div>}
        {preview.preview.length > 0 && <div className="preview-table"><h3>정규화 미리보기</h3><table><thead><tr><th>원본 ID</th><th>방문 시작</th><th>Offering</th><th>상태</th><th>고객 토큰</th></tr></thead><tbody>{preview.preview.map((row) => <tr key={row.source_record_id}><td>{row.source_record_id}</td><td>{new Date(row.visit_start_at).toLocaleString("ko-KR")}</td><td>{row.offering_name}</td><td><span className="status-pill">{row.status}</span></td><td>{row.customer_token_present ? "있음" : "없음"}</td></tr>)}</tbody></table></div>}
      </section>}
    </section>
  </main>;
}
