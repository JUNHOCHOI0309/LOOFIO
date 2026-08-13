const navigation = ["Dashboard", "Opportunities", "Analytics", "Customers", "Actions", "Data", "Reports", "Settings"];

export default function Home() {
  return (
    <main className="shell">
      <aside>
        <p className="brand">LOOFIO</p>
        <nav aria-label="Main navigation">
          {navigation.map((item, index) => (
            <a className={index === 0 ? "active" : ""} href="#" key={item}>{item}</a>
          ))}
        </nav>
      </aside>
      <section className="workspace">
        <p className="eyebrow">Hospital MVP</p>
        <h1>사업의 다음 기회를 찾습니다.</h1>
        <p className="intro">데이터 업로드, Opportunity 탐지, 승인된 Action과 Measurement를 연결하는 기반 환경이 준비되었습니다.</p>
        <div className="cards">
          <article><span>Frontend</span><strong>Next.js</strong><small>apps/web</small></article>
          <article><span>API</span><strong>FastAPI</strong><small>api</small></article>
          <article><span>Data</span><strong>PostgreSQL</strong><small>Docker Compose</small></article>
        </div>
      </section>
    </main>
  );
}
