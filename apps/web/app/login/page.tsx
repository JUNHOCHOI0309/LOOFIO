const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export default function LoginPage() {
  return <main className="login-shell">
    <section className="login-panel">
      <a className="login-brand" href="/"><span>◒</span> LOOFIO</a>
      <p className="eyebrow">Hospital Opportunity Intelligence</p>
      <h1>데이터 기반의<br />다음 기회를 찾으세요.</h1>
      <p className="login-description">LOOFIO는 병원의 예약·매출 데이터를 분석해, 놓치고 있는 기회와 실행 가능한 다음 행동을 제안합니다.</p>
      <div className="login-points"><p><span>✓</span> 사용자 승인 전에는 외부 실행이 없습니다.</p><p><span>✓</span> 고객 정보는 필요한 최소 범위로 처리합니다.</p></div>
    </section>
    <section className="login-card-wrap">
      <div className="login-card">
        <p className="eyebrow">Sign in</p>
        <h2>LOOFIO에 로그인</h2>
        <p>계정으로 안전하게 로그인해 사업장 데이터와 Opportunity를 확인하세요.</p>
        <a className="oauth-button google" href={`${apiBaseUrl}/auth/google/login`}><span>G</span> Google로 계속하기</a>
        <a className="oauth-button naver" href={`${apiBaseUrl}/auth/naver/login`}><span>N</span> NAVER로 계속하기</a>
        <div className="login-divider"><span />또는<span /></div>
        <a className="back-dashboard" href="/">로그인 없이 화면 둘러보기 →</a>
        <small>로그인하면 <a href="#">이용약관</a> 및 <a href="#">개인정보 처리방침</a>에 동의하는 것으로 간주합니다.</small>
      </div>
    </section>
  </main>;
}
