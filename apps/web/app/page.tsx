const navigation = [
  ["▦", "Dashboard"],
  ["◇", "Opportunities"],
  ["⌁", "Analytics"],
  ["◉", "Customers"],
  ["✓", "Actions"],
  ["⊞", "Data"],
  ["▤", "Reports"],
  ["⚙", "Settings"],
];

const metrics = [
  { label: "발견된 예상 기회", value: "₩1,420,000", change: "이번 달", icon: "✦", tone: "violet" },
  { label: "Open Opportunities", value: "7", change: "지난주 대비 +2", icon: "↗", tone: "mint" },
  { label: "실행 중인 Action", value: "3", change: "승인 대기 2건", icon: "◎", tone: "blue" },
  { label: "측정 완료", value: "5", change: "결과 확인 가능", icon: "✓", tone: "pink" },
];

const opportunities = [
  ["화요일 오후 예약 수요 저하", "LOW_DEMAND_SLOT", "₩380K – ₩460K", "74%", "중간"],
  ["피코토닝 예약 취소 집중", "CANCELLATION_HOTSPOT", "₩210K – ₩290K", "82%", "높음"],
  ["재방문 예상 고객 미예약", "DORMANT_CUSTOMER", "₩120K – ₩180K", "68%", "중간"],
];

export default function Home() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span>◒</span> LOOFIO</div>
        <div className="workspace-name">OO 피부과 <span>⌄</span></div>
        <nav aria-label="Main navigation">
          {navigation.map(([icon, item], index) => (
            <a className={index === 0 ? "active" : ""} href="#" key={item}>
              <span>{icon}</span>{item}
            </a>
          ))}
        </nav>
        <div className="sidebar-note">
          <span>✦</span>
          <strong>데이터를 연결해<br />더 정확한 기회를 찾으세요.</strong>
          <a href="#">데이터 업로드 →</a>
        </div>
        <div className="account"><div>J</div><p><strong>김지연</strong><small>Owner</small></p><span>⌄</span></div>
      </aside>

      <section className="workspace">
        <header>
          <div><p className="breadcrumb">Dashboard <span>›</span> 오늘의 브리핑</p><h1>오늘의 기회 <span>✦</span></h1><p className="subtitle">OO 피부과의 데이터에서 발견한, 지금 검토할 만한 매출 기회입니다.</p></div>
          <button className="date-button">▣ 최근 30일 <span>⌄</span></button>
        </header>

        <div className="metric-grid">
          {metrics.map((metric) => <article className="metric-card" key={metric.label}>
            <div className={`metric-icon ${metric.tone}`}>{metric.icon}</div>
            <p>{metric.label}</p><strong>{metric.value}</strong><small>{metric.change}</small>
          </article>)}
        </div>

        <div className="content-grid">
          <article className="chart-card">
            <div className="card-title"><div><h2>예약 추이</h2><p><i className="purple" />예약 수 <i className="blue" />완료 방문</p></div><button>주별⌄</button></div>
            <div className="chart"><div className="grid-lines"><span>180</span><span>120</span><span>60</span><span>0</span></div><svg viewBox="0 0 620 220" role="img" aria-label="최근 8주 예약 추이"><path className="area" d="M18 165 L96 130 L174 146 L252 92 L330 118 L408 64 L486 82 L594 30 L594 210 L18 210Z" /><polyline className="line primary" points="18,165 96,130 174,146 252,92 330,118 408,64 486,82 594,30" /><polyline className="line secondary" points="18,185 96,164 174,171 252,133 330,152 408,112 486,125 594,81" /></svg><div className="axis"><span>06.23</span><span>06.30</span><span>07.07</span><span>07.14</span><span>07.21</span><span>07.28</span><span>08.04</span><span>08.11</span></div></div>
          </article>
          <article className="action-card">
            <div className="card-title"><div><h2>추천 Action</h2><p>승인 후에만 실행됩니다.</p></div><button className="more">•••</button></div>
            <div className="action-priority"><span>우선순위 높음</span><strong>화요일 14–16시<br />재방문 고객 혜택</strong><p>반복적으로 낮은 시간대의 예약을 테스트합니다.</p><div><button className="primary">검토하기</button><button className="ghost">나중에</button></div></div>
            <p className="safety">✓ 사용자 승인 전에는 외부 실행이 이루어지지 않습니다.</p>
          </article>
        </div>

        <article className="opportunity-card"><div className="card-title"><div><h2>최근 발견된 Opportunity</h2><p>Observation, Estimate, Recommendation을 구분해 확인하세요.</p></div><a href="#">모두 보기 →</a></div><div className="table-wrap"><table><thead><tr><th>기회</th><th>유형</th><th>예상 기회 가치</th><th>신뢰도</th><th /></tr></thead><tbody>{opportunities.map(([name, type, value, confidence, level]) => <tr key={name}><td><strong>{name}</strong></td><td><span className="type-tag">{type}</span></td><td>{value}</td><td><span className={`confidence ${level === "높음" ? "high" : "medium"}`}>{confidence} · {level}</span></td><td><button className="view">보기 →</button></td></tr>)}</tbody></table></div></article>
        <footer>ⓘ 모든 예상 효과는 추정치이며, 실제 결과는 Measurement에서 확인합니다.</footer>
      </section>
    </main>
  );
}
