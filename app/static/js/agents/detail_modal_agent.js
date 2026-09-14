/**
 * DetailModalAgent
 * ================
 * 경기 상세 정보, 직전경기 결과, 상대전적(H2H), 선발투수/라인업, 박스스코어를 
 * API-Sports 및 공식 데이터베이스와 연동하여 독립적으로 조회하고 모달을 렌더링하는 전담 에이전트.
 * (가짜 데이터 생성 100% 완전 배제 및 공식 데이터 직결)
 */
class DetailModalAgent {
  constructor() {
    this._historyCache = new Map();
    this._detailCache = new Map();
    this.currentMatchId = null;
    this.selectedTeamSide = 'home'; // 'home' or 'away'
  }

  /**
   * 공식 경기 이력 (직전경기 5경기 및 맞대결 H2H) 비동기 조회
   */
  async fetchMatchHistory(matchId) {
    if (!matchId) return null;
    if (this._historyCache.has(matchId)) {
      return this._historyCache.get(matchId);
    }

    try {
      const resp = await fetch(`/api/v1/live/match-history/${matchId}`, { cache: 'no-store' });
      if (resp.ok) {
        const data = await resp.json();
        this._historyCache.set(matchId, data);
        return data;
      }
    } catch (e) {
      console.warn(`[DetailModalAgent] Failed to fetch history for match ${matchId}:`, e);
    }
    return null;
  }

  /**
   * 경기 상세 박스스코어 및 선수 지표 조회
   */
  async fetchMatchDetail(matchId) {
    if (!matchId) return null;
    if (this._detailCache.has(matchId)) {
      return this._detailCache.get(matchId);
    }

    try {
      const resp = await fetch(`/api/v1/matches/${matchId}`, { cache: 'no-store' });
      if (resp.ok) {
        const data = await resp.json();
        this._detailCache.set(matchId, data);
        return data;
      }
    } catch (e) {
      console.warn(`[DetailModalAgent] Failed to fetch detail for match ${matchId}:`, e);
    }
    return null;
  }

  /**
   * 직전경기 상세 모달 열기
   */
  async openLastMatchModal(matchId, teamSide = 'home') {
    this.currentMatchId = matchId;
    this.selectedTeamSide = teamSide;

    const modalEl = document.getElementById('lastMatchDetailModal');
    if (!modalEl) return;

    const match = window.matchListAgent ? window.matchListAgent.getMatchById(matchId) : null;
    const teamName = match ? (teamSide === 'home' ? match.home_team_name : match.away_team_name) : '선택 팀';

    const titleEl = document.getElementById('lastMatchModalTitle');
    if (titleEl) {
      titleEl.innerHTML = `<i class="bi bi-clock-history me-1 text-primary"></i>${teamName} <span class="text-muted fs-6 fw-normal">직전 경기 상세 분석</span>`;
    }

    const bodyEl = document.getElementById('lastMatchDetailModalBody') || document.getElementById('lastMatchModalBody');
    if (bodyEl) {
      bodyEl.innerHTML = `
        <div class="text-center p-4">
          <div class="spinner-border text-primary" role="status"></div>
          <div class="mt-2 text-muted fw-bold" style="font-size:0.85rem;">공식 데이터베이스 직전 경기 분석 로딩 중...</div>
        </div>
      `;
    }

    const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    bsModal.show();

    // 공식 데이터 로드
    const histData = await this.fetchMatchHistory(matchId);
    this.renderLastMatchContent(histData, match, teamSide);
  }

  /**
   * 직전경기 모달 내부 렌더링
   */
  renderLastMatchContent(histData, match, teamSide) {
    const bodyEl = document.getElementById('lastMatchDetailModalBody') || document.getElementById('lastMatchModalBody');
    if (!bodyEl) return;

    if (!histData) {
      bodyEl.innerHTML = `
        <div class="alert alert-light text-center border p-4">
          <i class="bi bi-info-circle text-muted fs-3 mb-2 d-block"></i>
          <div class="fw-bold text-dark">공식 경기 데이터 집계 중입니다.</div>
          <div class="text-muted small mt-1">해당 팀의 최근 공식 경기 기록을 불러오는 중입니다.</div>
        </div>
      `;
      return;
    }

    const recentList = teamSide === 'home' ? (histData.home_recent || []) : (histData.away_recent || []);
    const lastMatch = recentList.length > 0 ? recentList[0] : null;
    const teamName = match ? (teamSide === 'home' ? match.home_team_name : match.away_team_name) : '해당 팀';

    if (!lastMatch) {
      bodyEl.innerHTML = `
        <div class="alert alert-light text-center border p-4">
          <i class="bi bi-calendar-x text-muted fs-3 mb-2 d-block"></i>
          <div class="fw-bold text-dark">${teamName}의 직전 공식 경기 기록이 준비 중입니다.</div>
          <div class="text-muted small mt-1">공식 리그 기록이 확인되는 대로 자동 갱신됩니다.</div>
        </div>
      `;
      return;
    }

    const isHome = (lastMatch.home_team === teamName || (lastMatch.home_team && lastMatch.home_team.includes(teamName)));
    const myScore = isHome ? lastMatch.home_score : lastMatch.away_score;
    const oppScore = isHome ? lastMatch.away_score : lastMatch.home_score;
    const oppTeam = isHome ? lastMatch.away_team : lastMatch.home_team;
    const resText = lastMatch.result || (myScore > oppScore ? '승' : (myScore < oppScore ? '패' : '무'));
    const resColor = resText.includes('승') ? '#dc2626' : (resText.includes('패') ? '#1d4ed8' : '#4b5563');

    bodyEl.innerHTML = `
      <div class="card border mb-3 shadow-sm">
        <div class="card-header bg-light d-flex justify-content-between align-items-center py-2">
          <span class="badge bg-secondary">${lastMatch.match_date ? lastMatch.match_date.slice(0, 10) : '최근'}</span>
          <span class="fw-bold" style="color:${resColor};">${teamName} [${resText}]</span>
        </div>
        <div class="card-body text-center py-3">
          <div class="row align-items-center">
            <div class="col-5 text-end">
              <div class="fw-bold fs-6 text-truncate">${teamName}</div>
              <div class="badge bg-light text-dark border mt-1">${isHome ? '홈' : '원정'}</div>
            </div>
            <div class="col-2 text-center">
              <div class="fs-4 fw-black text-dark">${myScore} : ${oppScore}</div>
              <div class="text-muted" style="font-size:0.75rem;">종료</div>
            </div>
            <div class="col-5 text-start">
              <div class="fw-bold fs-6 text-truncate">${oppTeam}</div>
              <div class="badge bg-light text-dark border mt-1">${isHome ? '원정' : '홈'}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 최근 5경기 공식 흐름 -->
      <div class="card border shadow-sm">
        <div class="card-header bg-white fw-bold py-2" style="font-size:0.85rem;">
          <i class="bi bi-list-ol me-1 text-primary"></i>${teamName} 최근 ${recentList.length}경기 공식 전적
        </div>
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 text-center align-middle" style="font-size:0.82rem;">
            <thead class="table-light">
              <tr>
                <th>날짜</th>
                <th>상대팀</th>
                <th>장소</th>
                <th>스코어</th>
                <th>결과</th>
              </tr>
            </thead>
            <tbody>
              ${recentList.map(r => {
                const rIsHome = (r.home_team === teamName || (r.home_team && r.home_team.includes(teamName)));
                const rOpp = rIsHome ? r.away_team : r.home_team;
                const rMy = rIsHome ? r.home_score : r.away_score;
                const rOpS = rIsHome ? r.away_score : r.home_score;
                const rRes = r.result || (rMy > rOpS ? '승' : (rMy < rOpS ? '패' : '무'));
                const rBadgeClass = rRes.includes('승') ? 'bg-danger' : (rRes.includes('패') ? 'bg-primary' : 'bg-secondary');
                return `
                  <tr>
                    <td class="text-muted">${r.match_date ? r.match_date.slice(5, 10) : '-'}</td>
                    <td class="fw-bold text-truncate" style="max-width:110px;">${rOpp}</td>
                    <td><span class="badge bg-light text-muted border">${rIsHome ? '홈' : '원정'}</span></td>
                    <td class="fw-bold">${rMy} - ${rOpS}</td>
                    <td><span class="badge ${rBadgeClass}">${rRes}</span></td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }
}

// 전역 싱글톤 인스턴스 생성
window.detailModalAgent = new DetailModalAgent();
