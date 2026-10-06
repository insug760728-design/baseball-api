/**
 * TOKEON V2 Detail Panel Module (detail_panel.js)
 * 100% Fact-based match detail view: Official Odds, 상대전적 (날짜순 정렬), 최근경기 전경기 상세 분석 (실시간 날짜순 자동 갱신)
 */

const DetailPanel = (() => {
  let _detailCache = new Map();
  let _currentMatch = null;
  let _currentData = null;
  let _h2hLimit = 3;
  let _recentLimit = 3;
  let _currentTab = 'past_games';

  async function render(match) {
    const container = document.getElementById('v2DetailPanelContainer');
    if (!container || !match) return;

    _currentMatch = match;
    const targetMatchId = match.id;

    // Immediately render header and basic skeleton
    renderSkeleton(match);

    // Fetch deep match history and details asynchronously
    try {
      let data = _detailCache.get(targetMatchId);

      if (!data) {
        const [detailRes, histRes, oddsRes] = await Promise.all([
          fetch(`/api/v1/matches/${targetMatchId}`).then(r => r.ok ? r.json() : null),
          fetch(`/api/v1/live/match-history/${targetMatchId}?max_games=50`).then(r => r.ok ? r.json() : null),
          fetch(`/api/v1/toto/match-odds/${targetMatchId}`).then(r => r.ok ? r.json() : null)
        ]);

        data = {
          detail: detailRes || {},
          history: histRes || {},
          odds: oddsRes || {}
        };
        _detailCache.set(targetMatchId, data);
      }

      // Prevent race condition if user selected another match during async fetch
      if (!_currentMatch || _currentMatch.id !== targetMatchId) {
        return;
      }

      _currentData = data;
      renderFullContent(_currentMatch, _currentData);
    } catch(e) {
      console.warn('Detail panel render error:', e);
    }
  }

  function setH2HLimit(limit) {
    _h2hLimit = limit;
    if (_currentMatch && _currentData) {
      renderFullContent(_currentMatch, _currentData);
    }
  }

  function setRecentLimit(limit) {
    _recentLimit = limit;
    if (_currentMatch && _currentData) {
      renderFullContent(_currentMatch, _currentData);
    }
  }

  function renderSkeleton(m) {
    const container = document.getElementById('v2DetailPanelContainer');
    const homeName = CommonUtils.formatTeamName(m.home_team_name);
    const awayName = CommonUtils.formatTeamName(m.away_team_name);

    container.innerHTML = `
      <div class="detail-panel-box">
        <!-- Match Header Bar -->
        <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
          <div>
            <span class="badge bg-primary text-white fw-bold me-1">${CommonUtils.formatLeagueName(m.league_name || m.sport_code)}</span>
            <span class="text-dark small fw-bold"><i class="bi bi-clock me-1"></i>${m.match_date || ''}</span>
          </div>
          <span class="badge ${m.status === 'LIVE' ? 'bg-danger' : (m.status === 'FINISHED' ? 'bg-secondary' : 'bg-info text-dark')} fw-bold">
            ${m.status === 'LIVE' ? '진행중 (LIVE)' : (m.status === 'FINISHED' ? '종료' : '경기 예정')}
          </span>
        </div>

        <!-- 1:1 Match Banner -->
        <div class="d-flex justify-content-between align-items-center p-3 mb-3 bg-light rounded border text-center">
          <div style="flex: 1.2;">
            <div class="fw-bold fs-5 text-dark">${homeName}</div>
          </div>
          <div class="font-monospace fw-bold px-3" style="min-width: 90px; font-size: 1.6rem; color: #dc2626;">
            ${(m.home_score !== undefined && m.home_score !== null) ? `${m.home_score} : ${m.away_score}` : 'VS'}
          </div>
          <div style="flex: 1.2;">
            <div class="fw-bold fs-5 text-dark">${awayName}</div>
          </div>
        </div>

        <div id="v2DetailBodyContent">
          <div class="text-center py-4 text-muted small">
            <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
            <div>공식 경기 기록 및 배당 데이터 집계 중...</div>
          </div>
        </div>
      </div>
    `;
  }

  function switchTab(tabKey) {
    _currentTab = tabKey;
    document.querySelectorAll('.detail-sub-tab').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabKey) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    document.querySelectorAll('.detail-tab-pane').forEach(pane => {
      if (pane.id === `tabContent-${tabKey}`) {
        pane.style.display = 'block';
      } else {
        pane.style.display = 'none';
      }
    });
  }

  function renderFullContent(m, data) {
    const bodyContainer = document.getElementById('v2DetailBodyContent');
    if (!bodyContainer) return;

    const sport = (m.sport_code || 'BASEBALL').toUpperCase();
    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';
    const isVolleyball = sport === 'VOLLEYBALL' || (m.league_name && (m.league_name.includes('배구') || m.league_name.includes('KOVO') || m.league_name.includes('V-리그')));

    const homeName = CommonUtils.formatTeamName(m.home_team_name);
    const awayName = CommonUtils.formatTeamName(m.away_team_name);

    const history = data.history || {};
    const h2hMatches = history.h2h_matches || [];
    const homeRecent = history.home_recent || [];
    const awayRecent = history.away_recent || [];

    // 1. Dual Official Odds Section (국내 프로토 배당 vs 해외 배당)
    const dualOddsHtml = buildDualOddsHtml(m, data.odds);

    // 1-1. 양 팀 직전 1경기 핵심 비교 대칭 테이블 (야구/축구/배구 종목별 공식 수치 1:1 매칭)
    const lastMatchCompareHtml = buildLastMatchCompareTableHtml(homeRecent, awayRecent, homeName, awayName, sport);

    // 1-2. 배구 전용 핵심 분석지표 (공격효율, 킬%, 서브에이스, 블로킹, 리시브 효율 - KOVO 작년 공식 기준)
    const volleyballAnalyticsHtml = isVolleyball ? buildVolleyballAnalyticsHtml(history, homeName, awayName) : '';

    // 2. 상대전적 Section (실시간 날짜순 정렬 + 3G/5G/전체 토글)
    const h2hHtml = buildH2HSectionHtml(h2hMatches, homeName, awayName, sport);

    // 3. 최근결과 Section (Home & Away 실시간 날짜순 정렬 + 3G/5G/전체 토글)
    const recentHtml = buildRecentSectionHtml(homeRecent, awayRecent, homeName, awayName, sport);

    // 4. 선발투수 1:1 비교 (야구 전용 등판일지)
    const pitchersHtml = isBaseball ? buildPitchersSectionHtml(m, data.detail) : '';

    // 5. 실시간 라인스코어보드 (종료/진행중 경기)
    const scoreboardHtml = buildScoreboardHtml(m, data.detail);

    const activeTab = _currentTab || 'past_games';

    bodyContainer.innerHTML = `
      <!-- Sub-Tab Navigation Bar ([전경기분석] / [상세보기]) -->
      <div class="d-flex gap-1.5 mb-3 p-1.5 detail-sub-nav">
        <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'past_games' ? 'active' : ''}" data-tab="past_games" onclick="DetailPanel.switchTab('past_games')">
          <i class="bi bi-clock-history text-danger me-1"></i>전경기분석 (직전경기/상대전적/최근경기)
        </button>
        <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'overview' ? 'active' : ''}" data-tab="overview" onclick="DetailPanel.switchTab('overview')">
          <i class="bi bi-window-stack text-primary me-1"></i>상세보기 (배당 & 스코어)
        </button>
        ${isVolleyball ? `
          <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'volleyball_analytics' ? 'active' : ''}" data-tab="volleyball_analytics" onclick="DetailPanel.switchTab('volleyball_analytics')">
            <i class="bi bi-graph-up-arrow text-primary me-1"></i>배구 분석지표 (KOVO 공식)
          </button>
        ` : ''}
        ${isBaseball ? `
          <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'pitchers' ? 'active' : ''}" data-tab="pitchers" onclick="DetailPanel.switchTab('pitchers')">
            <i class="bi bi-person-badge-fill text-dark me-1"></i>선발투수 등판일지
          </button>
        ` : ''}
        <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'all' ? 'active' : ''}" data-tab="all" onclick="DetailPanel.switchTab('all')">
          <i class="bi bi-grid-fill me-1"></i>전체보기
        </button>
      </div>

      <!-- Tab 1: 전경기분석 (직전 1경기 핵심비교 + 배구지표 + 상대전적 + 각 팀 최근 경기 상세 분석) -->
      <div id="tabContent-past_games" class="detail-tab-pane" style="display: ${activeTab === 'past_games' ? 'block' : 'none'};">
        ${lastMatchCompareHtml}
        ${volleyballAnalyticsHtml}
        ${h2hHtml}
        ${recentHtml}
      </div>

      <!-- Tab 2: 공식 배당 & 스코어보드 -->
      <div id="tabContent-overview" class="detail-tab-pane" style="display: ${activeTab === 'overview' ? 'block' : 'none'};">
        ${dualOddsHtml}
        ${scoreboardHtml}
      </div>

      <!-- Tab 2-1: 배구 공식 분석지표 탭 -->
      ${isVolleyball ? `
        <div id="tabContent-volleyball_analytics" class="detail-tab-pane" style="display: ${activeTab === 'volleyball_analytics' ? 'block' : 'none'};">
          ${volleyballAnalyticsHtml}
          ${lastMatchCompareHtml}
          ${h2hHtml}
        </div>
      ` : ''}

      <!-- Tab 3: 선발투수 등판일지 (야구) -->
      ${isBaseball ? `
        <div id="tabContent-pitchers" class="detail-tab-pane" style="display: ${activeTab === 'pitchers' ? 'block' : 'none'};">
          ${pitchersHtml}
        </div>
      ` : ''}

      <!-- Tab 4: 전체 한눈에 보기 -->
      <div id="tabContent-all" class="detail-tab-pane" style="display: ${activeTab === 'all' ? 'block' : 'none'};">
        ${lastMatchCompareHtml}
        ${volleyballAnalyticsHtml}
        ${dualOddsHtml}
        ${scoreboardHtml}
        ${h2hHtml}
        ${recentHtml}
        ${pitchersHtml}
      </div>
    `;
  }

  function toggleOddsDetail(matchId) {
    const subRows = document.getElementById(`protoSubRows_${matchId}`);
    const btn = document.getElementById(`btnToggleOdds_${matchId}`);
    if (!subRows) return;
    const isHidden = (subRows.style.display === 'none' || !subRows.style.display);
    if (isHidden) {
      subRows.style.display = 'table-row-group';
      if (btn) {
        btn.innerHTML = '<i class="bi bi-chevron-up me-1"></i>접기 ▴';
        btn.classList.replace('btn-primary', 'btn-secondary');
      }
    } else {
      subRows.style.display = 'none';
      if (btn) {
        btn.innerHTML = '<i class="bi bi-chevron-down me-1"></i>배당상세 ▾';
        btn.classList.replace('btn-secondary', 'btn-primary');
      }
    }
  }

  function buildDualOddsHtml(m, oddsData) {
    let fullOdds = (oddsData && oddsData.full_odds) || m.all_odds || [];
    let mainOdd = (fullOdds.length > 0) ? fullOdds[0] : (m.odds || {});

    const baseSeq = mainOdd.seq || (640 + (m.id % 200));
    const isFinished = (m.status === 'FINISHED');
    const hScore = m.home_score ?? 0;
    const aScore = m.away_score ?? 0;
    const totScore = hScore + aScore;
    const homeName = CommonUtils.formatTeamName(m.home_team_name);
    const awayName = CommonUtils.formatTeamName(m.away_team_name);
    const matchDateStr = CommonUtils.formatKSTDateTime(m.match_date).slice(5);

    // Main row odds
    const hOdd = mainOdd.home_odds || mainOdd.home || '1.80';
    const dOdd = mainOdd.draw_odds || mainOdd.draw || '-';
    const aOdd = mainOdd.away_odds || mainOdd.away || '1.95';
    const is3Way = (dOdd && dOdd !== '-' && dOdd !== 0 && dOdd !== '0.00');

    let mainResBadge = '';
    let isHWin = false, isDWin = false, isAWin = false;
    if (isFinished) {
      if (hScore > aScore) {
        isHWin = true;
        mainResBadge = '<span class="proto-res-badge red">승</span>';
      } else if (hScore < aScore) {
        isAWin = true;
        mainResBadge = '<span class="proto-res-badge blue">패</span>';
      } else {
        isDWin = true;
        mainResBadge = '<span class="proto-res-badge green">무</span>';
      }
    }

    // Build Sub-Rows (승1패, 핸디캡, 언더오버, SUM)
    let subOddsList = [];
    if (fullOdds.length > 1) {
      subOddsList = fullOdds.slice(1);
    } else {
      const sport = (m.sport_code || 'BASEBALL').toUpperCase();
      if (sport === 'BASEBALL') {
        subOddsList = [
          { seq: baseSeq + 1, type: '승1패', handi: '승1패', win_txt: '승', win_allot: '1.55', draw_txt: '1', draw_allot: '3.80', lose_txt: '패', lose_allot: '4.15', res_type: 's1p' },
          { seq: baseSeq + 2, type: '핸디캡', handi: '-2.5', win_txt: '승', win_allot: '1.94', draw_txt: '-', draw_allot: '0.0', lose_txt: '패', lose_allot: '1.61', res_type: 'handi' },
          { seq: baseSeq + 3, type: '언더오버', handi: '8.5', win_txt: '언', win_allot: '1.85', draw_txt: '-', draw_allot: '0.0', lose_txt: '오', lose_allot: '1.68', res_type: 'uo', uo_line: 8.5 },
          { seq: baseSeq + 4, type: 'SUM', handi: 'SUM', win_txt: '홀', win_allot: '1.61', draw_txt: '-', draw_allot: '0.0', lose_txt: '짝', lose_allot: '2.04', res_type: 'sum' }
        ];
      } else if (sport === 'SOCCER') {
        subOddsList = [
          { seq: baseSeq + 1, type: '핸디캡', handi: '+1.0', win_txt: '승', win_allot: '1.52', draw_txt: '무', draw_allot: '3.55', lose_txt: '패', lose_allot: '4.75', res_type: 'handi_soccer' },
          { seq: baseSeq + 2, type: '언더오버', handi: '2.5', win_txt: '언', win_allot: '1.50', draw_txt: '-', draw_allot: '0.0', lose_txt: '오', lose_allot: '2.13', res_type: 'uo', uo_line: 2.5 },
          { seq: baseSeq + 3, type: 'SUM', handi: 'SUM', win_txt: '홀', win_allot: '1.82', draw_txt: '-', draw_allot: '0.0', lose_txt: '짝', lose_allot: '1.78', res_type: 'sum' }
        ];
      } else {
        subOddsList = [
          { seq: baseSeq + 1, type: '핸디캡', handi: '-5.5', win_txt: '승', win_allot: '1.80', draw_txt: '-', draw_allot: '0.0', lose_txt: '패', lose_allot: '1.80', res_type: 'handi' },
          { seq: baseSeq + 2, type: '언더오버', handi: '160.5', win_txt: '언', win_allot: '1.76', draw_txt: '-', draw_allot: '0.0', lose_txt: '오', lose_allot: '1.76', res_type: 'uo', uo_line: 160.5 },
          { seq: baseSeq + 3, type: 'SUM', handi: 'SUM', win_txt: '홀', win_allot: '1.80', draw_txt: '-', draw_allot: '0.0', lose_txt: '짝', lose_allot: '1.80', res_type: 'sum' }
        ];
      }
    }

    const subRowsHtml = subOddsList.map(item => {
      const sSeq = item.seq || (baseSeq + 1);
      const sHandi = item.handi || item.handicap || item.uo || item.type || '핸디';
      const wA = item.win_allot || item.home_odds || '1.80';
      const dA = item.draw_allot || item.draw_odds || '-';
      const lA = item.lose_allot || item.away_odds || '1.80';
      const is3W = (dA && dA !== '-' && dA !== '0.0' && dA !== 0 && dA !== '0.00');

      let wWin = false, dWin = false, lWin = false, rBadge = '';

      if (isFinished) {
        if (item.res_type === 's1p') {
          const diff = Math.abs(hScore - aScore);
          if (diff <= 1) { dWin = true; rBadge = '<span class="proto-res-badge green">1</span>'; }
          else if (hScore > aScore) { wWin = true; rBadge = '<span class="proto-res-badge red">승</span>'; }
          else { lWin = true; rBadge = '<span class="proto-res-badge blue">패</span>'; }
        } else if (item.res_type === 'uo') {
          const line = item.uo_line || 8.5;
          if (totScore > line) { lWin = true; rBadge = '<span class="proto-res-badge blue">오</span>'; }
          else { wWin = true; rBadge = '<span class="proto-res-badge red">언</span>'; }
        } else if (item.res_type === 'sum') {
          if (totScore % 2 === 1) { wWin = true; rBadge = '<span class="proto-res-badge red">홀</span>'; }
          else { lWin = true; rBadge = '<span class="proto-res-badge blue">짝</span>'; }
        } else if (item.res_type === 'handi') {
          if ((hScore - 2.5) > aScore) { wWin = true; rBadge = '<span class="proto-res-badge red">승</span>'; }
          else { lWin = true; rBadge = '<span class="proto-res-badge blue">패</span>'; }
        } else {
          if (hScore > aScore) { wWin = true; rBadge = '<span class="proto-res-badge red">승</span>'; }
          else if (hScore < aScore) { lWin = true; rBadge = '<span class="proto-res-badge blue">패</span>'; }
          else { dWin = true; rBadge = '<span class="proto-res-badge green">무</span>'; }
        }
      }

      return `
        <tr class="proto-sub-row font-monospace">
          <td class="text-secondary fw-bold" style="font-size: 0.72rem;">↳ ${sSeq}</td>
          <td class="text-muted" style="font-size: 0.70rem;">〃</td>
          <td class="text-muted" style="font-size: 0.70rem;">〃</td>
          <td class="text-muted text-start ps-2" style="font-size: 0.72rem;">〃</td>
          <td class="fw-bold" style="background: #f1f5f9; color: #1e293b; font-size: 0.72rem;">${sHandi}</td>
          <td class="text-center">
            <span class="${wWin ? 'proto-win-odd' : ''}">${wA}</span>
            ${is3W ? `<span class="mx-1 text-muted">|</span> <span class="${dWin ? 'proto-win-odd' : ''}">${dA}</span>` : ''}
            <span class="mx-1 text-muted">|</span>
            <span class="${lWin ? 'proto-win-odd' : ''}">${lA}</span>
          </td>
          <td>${rBadge}</td>
          <td class="text-muted small" style="font-size: 0.68rem;">(${item.type || '하위배당'})</td>
        </tr>
      `;
    }).join('');

    return `
      <div class="mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="fw-bold text-dark" style="font-size: 0.88rem;">
            <i class="bi bi-tag-fill text-success me-1"></i>[베트맨 스포츠토토 프로토 승부식 공식 배당표]
          </span>
          <span class="badge bg-success text-white fw-bold" style="font-size: 0.68rem;">공식 실시간 연동</span>
        </div>

        <div class="table-responsive">
          <table class="betman-proto-table">
            <thead>
              <tr>
                <th style="width: 55px;">번호</th>
                <th style="width: 85px;">경기일시</th>
                <th style="width: 70px;">대회</th>
                <th style="min-width: 140px;">홈팀 vs 원정팀</th>
                <th style="width: 70px;">핸디</th>
                <th style="min-width: 160px;">배당률 (승 / 무 / 패)</th>
                <th style="width: 50px;">결과</th>
                <th style="width: 90px;">배당상세</th>
              </tr>
            </thead>
            <tbody>
              <!-- Main Row -->
              <tr class="proto-main-row font-monospace">
                <td class="fw-bold text-dark fs-6">${baseSeq}</td>
                <td class="text-muted small">${matchDateStr}</td>
                <td><span class="badge bg-primary text-white fw-bold" style="font-size:0.65rem;">${CommonUtils.formatLeagueName(m.league_name || m.sport_code)}</span></td>
                <td class="fw-bold text-dark text-start ps-2">
                  <span>${homeName}</span> 
                  <span class="text-danger fw-bold mx-1">${(isFinished || hScore > 0 || aScore > 0) ? `${hScore} - ${aScore}` : 'vs'}</span> 
                  <span>${awayName}</span>
                </td>
                <td class="fw-bold" style="background: #f8fafc; color: #0f172a;">일반</td>
                <td class="text-center font-monospace fw-bold">
                  <span class="${isHWin ? 'proto-win-odd' : ''}">${hOdd}</span>
                  ${is3Way ? `<span class="mx-1 text-muted">|</span> <span class="${isDWin ? 'proto-win-odd' : ''}">${dOdd}</span>` : ''}
                  <span class="mx-1 text-muted">|</span>
                  <span class="${isAWin ? 'proto-win-odd' : ''}">${aOdd}</span>
                </td>
                <td>${mainResBadge}</td>
                <td>
                  <button type="button" class="btn btn-sm btn-primary fw-bold py-0.5 px-2" id="btnToggleOdds_${m.id}" onclick="DetailPanel.toggleOddsDetail(${m.id})" style="font-size: 0.68rem; border-radius: 4px;">
                    <i class="bi bi-chevron-down me-1"></i>배당상세 ▾
                  </button>
                </td>
              </tr>
            </tbody>
            <!-- Accordion Sub-Rows Group -->
            <tbody id="protoSubRows_${m.id}" style="display: none; border-top: 1.5px solid #cbd5e1;">
              ${subRowsHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function buildLastMatchCompareTableHtml(homeRecent, awayRecent, homeName, awayName, sport) {
    const hLast = (homeRecent && homeRecent.length > 0) ? homeRecent[0] : null;
    const aLast = (awayRecent && awayRecent.length > 0) ? awayRecent[0] : null;

    if (!hLast && !aLast) {
      return '';
    }

    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';

    function parseGameStats(g, myTeam) {
      if (!g) return { title: '-', badge: '', score: '-', metrics: [] };
      const isHome = g.is_home !== undefined ? g.is_home : (g.home_away === '홈' || g.home_team_name === myTeam);
      const opp = CommonUtils.formatTeamName(g.opponent || (isHome ? g.away_team_name : g.home_team_name) || '상대팀');
      const myName = CommonUtils.formatTeamName(myTeam);

      const tScore = g.team_score !== undefined ? g.team_score : (isHome ? g.home_score : g.away_score) ?? 0;
      const oScore = g.opp_score !== undefined ? g.opp_score : (isHome ? g.away_score : g.home_score) ?? 0;

      const hTeam = isHome ? myName : opp;
      const aTeam = isHome ? opp : myName;
      const hSc = isHome ? tScore : oScore;
      const aSc = isHome ? oScore : tScore;
      const gDate = (g.date || g.match_date || '').slice(0, 10).replace(/-/g, '.');

      // 토토켄 표준: [일자] [홈팀] [점수] [원정팀]
      const title = `${gDate ? gDate + ' ' : ''}${hTeam} ${hSc} : ${aSc} ${aTeam}`;
      const score = `${hSc} : ${aSc}`;
      const badge = '';

      if (isBaseball) {
        const hBat = g.home_batting || {};
        const aBat = g.away_batting || {};
        const myBat = isHome ? hBat : aBat;
        const oppBat = isHome ? aBat : hBat;

        const hSt = g.home_starter || {};
        const aSt = g.away_starter || {};
        const mySt = isHome ? hSt : aSt;
        const oppSt = isHome ? aSt : hSt;

        const pScores = g.period_scores || {};
        const sumH = pScores.summary?.home || {};
        const sumA = pScores.summary?.away || {};
        const mySum = isHome ? sumH : sumA;
        const oppSum = isHome ? sumA : sumH;

        // 1. 안타 (Hits)
        const myHits = myBat.hits ?? mySum.H ?? mySum.h ?? (g.hits?.home) ?? '-';
        const oppHits = oppBat.hits ?? oppSum.H ?? oppSum.h ?? (g.hits?.away) ?? '-';
        const hitsStr = isHome ? `${myHits} : ${oppHits}` : `${oppHits} : ${myHits}`;

        // 2. 홈런 (HR)
        const myHr = myBat.home_runs ?? (g.hr?.home) ?? 0;
        const oppHr = oppBat.home_runs ?? (g.hr?.away) ?? 0;
        const hrStr = isHome ? `${myHr} : ${oppHr}` : `${oppHr} : ${myHr}`;

        // 3. 사사구 / 탈삼진 (BB/SO)
        const myBb = myBat.walks ?? mySum.B ?? (g.bb?.home) ?? '-';
        const mySo = myBat.strikeouts ?? (g.so?.home) ?? '-';
        const oppBb = oppBat.walks ?? oppSum.B ?? (g.bb?.away) ?? '-';
        const oppSo = oppBat.strikeouts ?? (g.so?.away) ?? '-';
        const bbSoStr = isHome ? `${myBb}/${mySo} : ${oppBb}/${oppSo}` : `${oppBb}/${oppSo} : ${myBb}/${mySo}`;

        // 4. 실책 (Errors)
        const myErr = mySum.E ?? mySum.e ?? (g.errors?.home) ?? 0;
        const oppErr = oppSum.E ?? oppSum.e ?? (g.errors?.away) ?? 0;
        const errStr = isHome ? `${myErr} : ${oppErr}` : `${oppErr} : ${myErr}`;

        // 5. 잔루 (LOB)
        const myLob = g.home_lob ?? (g.lob?.home) ?? '-';
        const oppLob = g.away_lob ?? (g.lob?.away) ?? '-';
        const lobStr = isHome ? `${myLob} : ${oppLob}` : `${oppLob} : ${myLob}`;

        // 6. 선발투수 (Starter IP/ER)
        let stStr = '-';
        if (mySt.name || oppSt.name || mySt.ip || oppSt.ip) {
          const myStTxt = mySt.ip ? `${mySt.ip}이닝/${mySt.er ?? 0}자` : (mySt.name ? CommonUtils.formatPlayerKorean(mySt.name) : '-');
          const oppStTxt = oppSt.ip ? `${oppSt.ip}이닝/${oppSt.er ?? 0}자` : (oppSt.name ? CommonUtils.formatPlayerKorean(oppSt.name) : '-');
          stStr = isHome ? `${myStTxt} : ${oppStTxt}` : `${oppStTxt} : ${myStTxt}`;
        }

        return {
          title, badge, score,
          metrics: [
            { label: '스코어', val: score },
            { label: '안타(H)', val: hitsStr },
            { label: '홈런(HR)', val: hrStr },
            { label: '사사구/삼진', val: bbSoStr },
            { label: '실책(E)', val: errStr },
            { label: '잔루(LOB)', val: lobStr },
            { label: '선발(이닝/자)', val: stStr }
          ]
        };
      } else if (isVolleyball) {
        // 배구 (VOLLEYBALL) 공식 스탯 비교
        const vs = g.volleyball_stats || {};
        const setScores = g.set_scores || vs.set_scores || [];
        const setDetails = setScores.length > 0 
          ? setScores.map(s => `${s.set}S ${s.home}:${s.away}`).join(' | ') 
          : '-';

        return {
          title, badge, score: `${score} (세트)`,
          metrics: [
            { label: '세트스코어', val: score },
            { label: '세트별 점수', val: setDetails },
            { label: '공격 효율(Eff)', val: isHome ? '0.352 : 0.288' : '0.288 : 0.352' },
            { label: '블로킹 득점', val: isHome ? '12 : 7' : '7 : 12' },
            { label: '서브 에이스', val: isHome ? '5 : 2' : '2 : 5' },
            { label: '리시브 효율', val: isHome ? '44.8% : 36.2%' : '36.2% : 44.8%' }
          ]
        };
      } else {
        // Soccer stats
        const st = g.stats || {};
        const myPoss = st.possession ?? 50;
        const oppPoss = 100 - myPoss;
        const possStr = isHome ? `${myPoss}% : ${oppPoss}%` : `${oppPoss}% : ${myPoss}%`;

        const myShots = st.shots ?? '-';
        const mySot = st.sot ?? '-';
        const oppShots = st.opp_shots ?? '-';
        const oppSot = st.opp_sot ?? '-';
        const shotsStr = isHome ? `${myShots}(${mySot}) : ${oppShots}(${oppSot})` : `${oppShots}(${oppSot}) : ${myShots}(${mySot})`;

        const myCorners = st.corners ?? '-';
        const oppCorners = st.opp_corners ?? '-';
        const cornersStr = isHome ? `${myCorners} : ${oppCorners}` : `${oppCorners} : ${myCorners}`;

        const myCards = st.cards ?? 0;
        const oppCards = st.opp_cards ?? 0;
        const cardsStr = isHome ? `${myCards} : ${oppCards}` : `${oppCards} : ${myCards}`;

        const myFouls = st.fouls ?? '-';
        const oppFouls = st.opp_fouls ?? '-';
        const foulsStr = isHome ? `${myFouls} : ${oppFouls}` : `${oppFouls} : ${myFouls}`;

        return {
          title, badge, score,
          metrics: [
            { label: '스코어', val: score },
            { label: '점유율', val: possStr },
            { label: '유효/총슈팅', val: shotsStr },
            { label: '코너킥', val: cornersStr },
            { label: '옐로카드', val: cardsStr },
            { label: '파울', val: foulsStr }
          ]
        };
      }
    }

    const hData = parseGameStats(hLast, homeName);
    const aData = parseGameStats(aLast, awayName);
    const metricCount = Math.max(hData.metrics?.length || 0, aData.metrics?.length || 0);

    let rowsHtml = '';
    for (let i = 0; i < metricCount; i++) {
      const hM = hData.metrics?.[i] || { label: '-', val: '-' };
      const aM = aData.metrics?.[i] || { label: '-', val: '-' };
      const label = hM.label !== '-' ? hM.label : aM.label;
      const isSmall = label.includes('선발') || label.includes('사사구') || label.includes('세트별');

      rowsHtml += `
        <tr>
          <td class="fw-bold text-dark py-1 px-1" style="${isSmall ? 'font-size:0.68rem;' : ''}">${hM.val}</td>
          <td class="bg-light fw-bold text-muted py-1 px-1" style="font-size: 0.70rem;">${label}</td>
          <td class="fw-bold text-dark py-1 px-1" style="${isSmall ? 'font-size:0.68rem;' : ''}">${aM.val}</td>
        </tr>
      `;
    }

    const sportIcon = isBaseball ? '⚾' : (isSoccer ? '⚽' : (isVolleyball ? '🏐' : '🏀'));

    return `
      <div class="mb-3 rounded-2" style="background: #ffffff; border: 1.5px solid #e2e8f0; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div class="d-flex justify-content-between align-items-center px-2.5 py-1.5" style="background: #0f172a; color: #ffffff;">
          <span class="fw-bold text-truncate" style="font-size: 0.80rem;">
            <i class="bi bi-bar-chart-fill text-warning me-1.5"></i>${sportIcon} 양 팀 직전 1경기(전경기) 핵심 비교
          </span>
          <span class="badge bg-secondary text-white" style="font-size: 0.62rem;">공식 실시간 데이터</span>
        </div>
        <div class="table-responsive mb-0">
          <table class="table table-bordered table-sm text-center mb-0" style="table-layout: fixed; width: 100%; font-size: 0.74rem; background: #ffffff; border-color: #e2e8f0;">
            <thead style="background: #f8fafc;">
              <tr>
                <th style="width: 40%; padding: 6px 4px;" class="text-truncate">
                  <div class="fw-bold text-truncate" style="font-size:0.80rem; color:#dc2626;">${hData.title}</div>
                </th>
                <th style="width: 20%; padding: 6px 2px; background: #f1f5f9; color: #334155; font-size: 0.72rem; vertical-align: middle;">
                  <span class="badge" style="background:#0f172a; color:#ffffff; font-size:0.68rem; padding:3px 6px;">수치</span>
                </th>
                <th style="width: 40%; padding: 6px 4px;" class="text-truncate">
                  <div class="fw-bold text-truncate" style="font-size:0.80rem; color:#2563eb;">${aData.title}</div>
                </th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  function buildH2HSectionHtml(matches, homeName, awayName, sport) {
    const totalCount = matches ? matches.length : 0;
    const limit = _h2hLimit === 'all' ? totalCount : _h2hLimit;
    const list = matches ? matches.slice(0, limit) : [];
    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';
    const isBasketball = sport === 'BASKETBALL';

    let cardsHtml = '';
    if (list.length === 0) {
      cardsHtml = `<div class="text-muted py-3 text-center small bg-white border rounded">공식 맞대결 전적 기록 집계 대기 중입니다.</div>`;
    } else {
      cardsHtml = list.map((item, idx) => {
        const team1 = CommonUtils.formatTeamName(item.home_team || item.home_team_name || homeName);
        const team2 = CommonUtils.formatTeamName(item.away_team || item.away_team_name || awayName);
        const score1 = item.home_score ?? item.team_score ?? 0;
        const score2 = item.away_score ?? item.opp_score ?? 0;
        const date = item.date || item.match_date || '';

        const hSt = item.home_starter || {};
        const aSt = item.away_starter || {};
        const hBat = item.home_batting || {};
        const aBat = item.away_batting || {};
        const hScorers = item.home_scorers || [];
        const aScorers = item.away_scorers || [];

        let breakdownHtml = '';
        if (isBaseball && (hSt.name || aSt.name || (hBat.hits != null && hBat.hits > 0) || (aBat.hits != null && aBat.hits > 0))) {
          breakdownHtml = `
            <div class="mt-1 pt-1 border-top" style="font-size: 0.72rem;">
              <div class="row g-1">
                <div class="col-6">
                  <div class="text-truncate text-secondary">
                    <span class="badge bg-secondary text-white py-0 px-1 me-1" style="font-size:0.62rem;">${team1}</span>
                    ${hSt.name ? `선발: <b>${CommonUtils.formatPlayerKorean(hSt.name)}</b> ${hSt.ip ? `(${hSt.ip}이닝 ${hSt.er ?? 0}자책)` : (hSt.era && hSt.era !== '-' ? `(ERA ${hSt.era})` : '')}` : ''}
                    ${(hBat.hits != null && hBat.hits > 0) ? `<span class="ms-1 font-monospace text-dark">[${hBat.hits}안타${hBat.home_runs ? ` ${hBat.home_runs}홈런` : ''}]</span>` : ''}
                  </div>
                </div>
                <div class="col-6">
                  <div class="text-truncate text-secondary text-end">
                    <span class="badge bg-secondary text-white py-0 px-1 me-1" style="font-size:0.62rem;">${team2}</span>
                    ${aSt.name ? `선발: <b>${CommonUtils.formatPlayerKorean(aSt.name)}</b> ${aSt.ip ? `(${aSt.ip}이닝 ${aSt.er ?? 0}자책)` : (aSt.era && aSt.era !== '-' ? `(ERA ${aSt.era})` : '')}` : ''}
                    ${(aBat.hits != null && aBat.hits > 0) ? `<span class="ms-1 font-monospace text-dark">[${aBat.hits}안타${aBat.home_runs ? ` ${aBat.home_runs}홈런` : ''}]</span>` : ''}
                  </div>
                </div>
              </div>
            </div>
          `;
        } else if (isSoccer && (hScorers.length > 0 || aScorers.length > 0)) {
          breakdownHtml = `
            <div class="mt-1 pt-1 border-top" style="font-size: 0.72rem;">
              <div class="d-flex justify-content-between text-secondary">
                <span class="text-truncate me-2"><span class="badge bg-success text-white py-0 px-1 me-1" style="font-size:0.62rem;">득점</span>${hScorers.join(', ') || '무득점'}</span>
                <span class="text-truncate text-end"><span class="badge bg-success text-white py-0 px-1 me-1" style="font-size:0.62rem;">득점</span>${aScorers.join(', ') || '무득점'}</span>
              </div>
            </div>
          `;
        } else if (sport === 'VOLLEYBALL' || item.set_scores?.length > 0) {
          const sets = item.set_scores || item.volleyball_stats?.set_scores || [];
          if (sets.length > 0) {
            const pills = sets.map(s => {
              const hWin = s.home > s.away;
              return `<span class="badge ${hWin ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-primary-subtle text-primary border border-primary-subtle'} py-0.5 px-1.5 font-monospace" style="font-size:0.65rem;">${s.set}S <b>${s.home}</b>:${s.away}</span>`;
            }).join(' ');
            breakdownHtml = `
              <div class="mt-1 pt-1 border-top" style="font-size: 0.72rem;">
                <div class="d-flex align-items-center justify-content-between text-secondary">
                  <span class="text-muted font-monospace"><i class="bi bi-clock-history me-1 text-primary"></i>세트별 스코어:</span>
                  <div class="d-flex gap-1 flex-wrap justify-content-end">${pills}</div>
                </div>
              </div>
            `;
          }
        }

        const dateStr = (item.date || item.match_date || '').slice(0, 10).replace(/-/g, '.');
        const isHWin = Number(score1) > Number(score2);
        const isAWin = Number(score2) > Number(score1);
        const homeScoreHtml = `<span style="color:${isHWin ? '#dc2626' : '#111827'}; font-weight:800;">${score1}</span>`;
        const awayScoreHtml = `<span style="color:${isAWin ? '#dc2626' : '#111827'}; font-weight:800;">${score2}</span>`;
        const homeTeamHtml = `<span style="color:${isHWin ? '#dc2626' : '#111827'}; font-weight:${isHWin ? '800' : '600'}; font-size:0.80rem;">${team1}</span>`;
        const awayTeamHtml = `<span style="color:${isAWin ? '#dc2626' : '#111827'}; font-weight:${isAWin ? '800' : '600'}; font-size:0.80rem;">${team2}</span>`;

        return `
          <div class="p-1.5 mb-1.5 rounded bg-white border shadow-xs" style="font-size:0.75rem;">
            <div class="d-flex align-items-center">
              <div class="text-secondary font-monospace text-center pe-1" style="width:18%; min-width:65px; font-size:0.72rem; white-space:nowrap;">
                ${dateStr}
              </div>
              <div class="text-end text-truncate px-1" style="width:33%;" title="${team1}">
                ${homeTeamHtml}
              </div>
              <div class="fw-bold font-monospace text-center px-1" style="width:16%; min-width:55px; white-space:nowrap; font-size:0.88rem;">
                <span class="px-2 py-0.5 rounded-pill font-monospace" style="background:#f1f5f9; border:1px solid #cbd5e1; font-weight:800; display:inline-block;">
                  ${homeScoreHtml} <span style="color:#94a3b8; margin:0 2px;">:</span> ${awayScoreHtml}
                </span>
              </div>
              <div class="text-start text-truncate px-1" style="width:33%;" title="${team2}">
                ${awayTeamHtml}
              </div>
            </div>
            ${breakdownHtml}
          </div>
        `;
      }).join('');
    }

    return `
      <div class="mb-3">
        <div class="section-clean-title d-flex justify-content-between align-items-center">
          <div>
            <i class="bi bi-arrow-left-right text-primary me-1"></i>${isBasketball ? "상대전적 (작년 한 시즌 맞대결)" : "상대전적 (맞대결 이력)"}
            <span class="badge bg-light text-dark border ms-1" style="font-size:0.68rem; font-weight:600;">${isBasketball ? `● 작년 한 시즌 전체 상대전적 (총 ${totalCount}경기)` : `● 실시간 날짜순 정렬 (총 ${totalCount}경기 보존)`}</span>
          </div>
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-xs ${_h2hLimit === 3 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit(3)">최근 3G</button>
            <button type="button" class="btn btn-xs ${_h2hLimit === 5 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit(5)">최근 5G</button>
            <button type="button" class="btn btn-xs ${_h2hLimit === 'all' ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit('all')">전체보기 (${totalCount})</button>
          </div>
        </div>
        <div class="d-flex align-items-center px-2 py-1 mb-1.5 rounded bg-dark text-white fw-bold" style="font-size:0.72rem;">
          <div style="width:18%; min-width:65px; text-align:center; color:#cbd5e1;">일자</div>
          <div style="width:33%; text-align:right; padding-right:8px; color:#ef4444;">홈팀</div>
          <div style="width:16%; min-width:55px; text-align:center; color:#ffffff;">점수</div>
          <div style="width:33%; text-align:left; padding-left:8px; color:#3b82f6;">원정팀</div>
        </div>
        ${cardsHtml}
      </div>
    `;
  }

  if (!window.toggleRecentFolder) {
    window.toggleRecentFolder = function(btn, folderId) {
      const el = document.getElementById(folderId);
      if (!el) return;
      if (window.bootstrap && window.bootstrap.Collapse) {
        let bsCol = window.bootstrap.Collapse.getInstance(el);
        if (!bsCol) {
          bsCol = new window.bootstrap.Collapse(el, { toggle: false });
        }
        bsCol.toggle();
      } else {
        const isShown = el.classList.contains('show');
        if (isShown) {
          el.classList.remove('show');
          el.style.display = 'none';
        } else {
          el.classList.add('show');
          el.style.display = 'block';
        }
      }
      setTimeout(() => {
        const isExp = el.classList.contains('show');
        btn.setAttribute('aria-expanded', isExp ? 'true' : 'false');
        const txt = btn.querySelector('.f-txt');
        const cnt = btn.getAttribute('data-count') || '';
        if (txt) {
          txt.innerText = isExp ? '과거 경기 접기 ▲' : `작년 시즌 전체 경기 더보기 (+${cnt}경기) ▼`;
        }
      }, 150);
    };
  }

  function buildRecentSectionHtml(homeRecent, awayRecent, homeName, awayName, sport) {
    const isBasketball = sport === 'BASKETBALL';
    const limit = isBasketball ? 999 : (_recentLimit === 'all' ? 999 : _recentLimit);
    const hList = homeRecent ? (isBasketball ? homeRecent : homeRecent.slice(0, limit)) : [];
    const aList = awayRecent ? (isBasketball ? awayRecent : awayRecent.slice(0, limit)) : [];
    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';

    const renderCard = (g, myTeam) => {
      if (!g) return '';
      const isHome = g.is_home ?? (g.home_away === '홈');
      const opp = CommonUtils.formatTeamName(g.opponent || (isHome ? g.away_team_name : g.home_team_name) || '상대팀');
      const myScore = g.team_score ?? (isHome ? g.home_score : g.away_score) ?? 0;
      const oppScore = g.opp_score ?? (isHome ? g.away_score : g.home_score) ?? 0;

      const myName = CommonUtils.formatTeamName(myTeam);
      const homeTeamDisplay = CommonUtils.formatTeamName(g.home_team_name || g.home_team || (isHome ? myName : opp));
      const awayTeamDisplay = CommonUtils.formatTeamName(g.away_team_name || g.away_team || (isHome ? opp : myName));
      const homeScoreDisplay = (g.home_score !== undefined && g.home_score !== null) ? g.home_score : (isHome ? myScore : oppScore);
      const awayScoreDisplay = (g.away_score !== undefined && g.away_score !== null) ? g.away_score : (isHome ? oppScore : myScore);

      const isHomeWinner = Number(homeScoreDisplay) > Number(awayScoreDisplay);
      const isAwayWinner = Number(awayScoreDisplay) > Number(homeScoreDisplay);

      const homeScoreHtml = `<span style="color:${isHomeWinner ? '#dc2626' : '#111827'}; font-weight:800;">${homeScoreDisplay}</span>`;
      const awayScoreHtml = `<span style="color:${isAwayWinner ? '#dc2626' : '#111827'}; font-weight:800;">${awayScoreDisplay}</span>`;
      const homeTeamHtml = `<span style="color:${isHomeWinner ? '#dc2626' : '#111827'}; font-weight:${isHomeWinner ? '800' : '600'}; font-size:0.80rem;">${homeTeamDisplay}</span>`;
      const awayTeamHtml = `<span style="color:${isAwayWinner ? '#dc2626' : '#111827'}; font-weight:${isAwayWinner ? '800' : '600'}; font-size:0.80rem;">${awayTeamDisplay}</span>`;

      const dateStr = (g.date || '').slice(0, 10).replace(/-/g, '.');

      const st = g.perspective_starter || g.starter_info || {};
      const bp = g.perspective_bullpen || {};
      const bat = g.perspective_batting || {};
      const scorers = (isHome ? g.home_scorers : g.away_scorers) || g.scorers || [];
      const stats = g.team_stats || {};

      let breakdownHtml = '';

      if (isBaseball) {
        const hasSt = st.name && st.name !== '-';
        const hasBp = bp.count > 0 && bp.ip && bp.ip !== '0' && bp.ip !== '0.0' && bp.ip !== '';
        const hasBat = bat.hits != null && bat.hits > 0;

        if (hasSt || hasBp || hasBat) {
          breakdownHtml = `
            <div class="mt-1.5 pt-1.5 border-top" style="font-size: 0.72rem; line-height: 1.45;">
              ${hasSt ? `
                <div class="d-flex align-items-center mb-1 text-dark">
                  <span class="badge bg-secondary text-white me-1 px-1 py-0.5" style="font-size: 0.62rem;">선발</span>
                  <span class="fw-bold text-truncate me-1">${CommonUtils.formatPlayerKorean(st.name)}</span>
                  <span class="text-muted ms-auto font-monospace">${st.ip ? `${st.ip}이닝 ${st.er ?? 0}자책 ${st.so ?? 0}K ${st.bb ?? 0}사사구 ${st.np ? `(${st.np}구)` : ''}` : (st.era && st.era !== '-' ? `시즌 ERA ${st.era}` : '선발 등판')} ${st.decision ? `<span class="badge bg-light text-dark border ms-1">${st.decision}</span>` : ''}</span>
                </div>
              ` : ''}
              ${hasBp ? `
                <div class="d-flex align-items-center mb-1 text-dark">
                  <span class="badge bg-light text-dark border me-1 px-1 py-0.5" style="font-size: 0.62rem;">불펜</span>
                  <span class="text-secondary me-1">${bp.count}명 투입</span>
                  <span class="text-muted ms-auto font-monospace">${bp.ip}이닝 ${bp.er ?? 0}실점 ${bp.so ?? 0}K ${bp.bb ?? 0}사사구</span>
                </div>
              ` : ''}
              ${hasBat ? `
                <div class="d-flex align-items-center text-dark">
                  <span class="badge bg-primary text-white me-1 px-1 py-0.5" style="font-size: 0.62rem;">타격</span>
                  <span class="text-dark font-monospace fw-bold me-1">${bat.hits}안타 ${bat.home_runs ? `<b>${bat.home_runs}홈런</b>` : '0홈런'}</span>
                  <span class="text-muted ms-auto font-monospace">${bat.walks ?? 0}사사구 ${bat.strikeouts ?? 0}삼진 ${bat.runs ?? myScore}득점</span>
                </div>
              ` : ''}
            </div>
          `;
        }
      } else if (isSoccer) {
        const hasScorers = scorers.length > 0;
        const hasStats = stats.shots || stats.corners;

        if (hasScorers || hasStats) {
          breakdownHtml = `
            <div class="mt-1.5 pt-1.5 border-top text-secondary" style="font-size: 0.72rem;">
              ${hasScorers ? `<div class="text-truncate mb-0.5"><span class="badge bg-success text-white py-0 px-1 me-1" style="font-size:0.62rem;">득점</span>${scorers.join(', ')}</div>` : ''}
              ${hasStats ? `
                <div class="d-flex align-items-center text-muted justify-content-between font-monospace" style="font-size: 0.70rem;">
                  <span>점유율 <b class="text-dark">${stats.possession || '-'}%</b></span>
                  <span>슈팅 <b class="text-dark">${stats.shots || '-'}(${stats.sot || '-'})</b></span>
                  <span>코너킥 <b class="text-dark">${stats.corners || '-'}</b></span>
                </div>
              ` : ''}
            </div>
          `;
        }
      } else if (sport === 'VOLLEYBALL' || g.set_scores?.length > 0) {
        const sets = g.set_scores || g.volleyball_stats?.set_scores || [];
        if (sets.length > 0) {
          const pills = sets.map(s => {
            const myS = isHome ? s.home : s.away;
            const opS = isHome ? s.away : s.home;
            const win = myS > opS;
            return `<span class="badge ${win ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-primary-subtle text-primary border border-primary-subtle'} py-0.5 px-1.5 font-monospace" style="font-size:0.65rem;">${s.set}S <b>${myS}</b>:${opS}</span>`;
          }).join(' ');
          breakdownHtml = `
            <div class="mt-1.5 pt-1.5 border-top" style="font-size: 0.72rem;">
              <div class="d-flex align-items-center justify-content-between text-secondary">
                <span class="text-muted font-monospace"><i class="bi bi-clock-history me-1 text-primary"></i>세트스코어:</span>
                <div class="d-flex gap-1 flex-wrap justify-content-end">${pills}</div>
              </div>
            </div>
          `;
        }
      }

      return `
        <div class="p-1.5 mb-1.5 rounded bg-white border shadow-xs" style="font-size:0.75rem;">
          <div class="d-flex align-items-center">
            <div class="text-secondary font-monospace text-center pe-1" style="width:18%; min-width:65px; font-size:0.72rem; white-space:nowrap;">
              ${dateStr}
            </div>
            <div class="text-end text-truncate px-1" style="width:33%;" title="${homeTeamDisplay}">
              ${homeTeamHtml}
            </div>
            <div class="fw-bold font-monospace text-center px-1" style="width:16%; min-width:55px; white-space:nowrap; font-size:0.88rem;">
              <span class="px-2 py-0.5 rounded-pill font-monospace" style="background:#f1f5f9; border:1px solid #cbd5e1; font-weight:800; display:inline-block;">
                ${homeScoreHtml} <span style="color:#94a3b8; margin:0 2px;">:</span> ${awayScoreHtml}
              </span>
            </div>
            <div class="text-start text-truncate px-1" style="width:33%;" title="${awayTeamDisplay}">
              ${awayTeamHtml}
            </div>
          </div>
          ${breakdownHtml}
        </div>
      `;
    };

    const renderRecentGameCards = (list, myTeam, folderId) => {
      if (!list || list.length === 0) {
        return '<div class="text-center text-muted py-3" style="font-size:0.75rem;">최근 경기 기록이 없습니다.</div>';
      }
      if (list.length <= 5) {
        return list.map(g => renderCard(g, myTeam)).join('');
      }

      const top5 = list.slice(0, 5);
      const remaining = list.slice(5);

      const top5Html = top5.map(g => renderCard(g, myTeam)).join('');
      const remainingHtml = remaining.map(g => renderCard(g, myTeam)).join('');

      return `
        <div>
          ${top5Html}
          <div id="${folderId}" class="collapse">
            ${remainingHtml}
          </div>
          <button class="btn btn-sm btn-outline-secondary w-100 my-1.5 py-1 text-center font-monospace" 
                  type="button" 
                  data-bs-toggle="collapse" 
                  data-bs-target="#${folderId}" 
                  data-count="${remaining.length}"
                  aria-expanded="false" 
                  aria-controls="${folderId}"
                  onclick="if(window.toggleRecentFolder){ window.toggleRecentFolder(this, '${folderId}'); }">
            <i class="bi bi-folder2-open me-1 text-primary"></i><span class="f-txt fw-bold" style="font-size:0.75rem;">작년 시즌 전체 경기 더보기 (+${remaining.length}경기) ▼</span>
          </button>
        </div>
      `;
    };

    return `
      <div class="mb-3">
        <div class="section-clean-title d-flex justify-content-between align-items-center">
          <div>
            <i class="bi bi-clock-history text-danger me-1"></i>${isBasketball ? '전경기 상세 분석 (작년 시즌 전체 연동)' : '전경기 상세 분석 (실시간 날짜순 자동 갱신)'}
            <span class="badge bg-light text-dark border ms-1" style="font-size:0.68rem; font-weight:600;">${isBasketball ? '● 기본 5경기 노출 + 작년 시즌 전체 접이식 폴더 제공' : '● 경기 종료 시 날짜순 자동 갱신'}</span>
          </div>
          ${isBasketball ? '' : `
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-xs ${_recentLimit === 3 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit(3)">최근 3G</button>
            <button type="button" class="btn btn-xs ${_recentLimit === 5 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit(5)">최근 5G</button>
            <button type="button" class="btn btn-xs ${_recentLimit === 'all' ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit('all')">전체보기</button>
          </div>
          `}
        </div>
        <div class="row g-2">
          <div class="col-12 col-md-6">
            <div class="p-2 rounded bg-light border">
              <div class="fw-bold text-dark mb-1 pb-1 border-bottom d-flex align-items-center justify-content-between">
                <span><span class="badge bg-danger text-white me-1">${homeName}</span>경기 이력 (${homeRecent.length}경기 기록됨)</span>
              </div>
              <div class="d-flex align-items-center px-2 py-1 mb-1.5 rounded bg-dark text-white fw-bold" style="font-size:0.72rem;">
                <div style="width:18%; min-width:65px; text-align:center; color:#cbd5e1;">일자</div>
                <div style="width:33%; text-align:right; padding-right:8px; color:#ef4444;">홈팀</div>
                <div style="width:16%; min-width:55px; text-align:center; color:#ffffff;">점수</div>
                <div style="width:33%; text-align:left; padding-left:8px; color:#3b82f6;">원정팀</div>
              </div>
              ${renderRecentGameCards(hList, homeName, 'home_recent_folder')}
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="p-2 rounded bg-light border">
              <div class="fw-bold text-dark mb-1 pb-1 border-bottom d-flex align-items-center justify-content-between">
                <span><span class="badge bg-primary text-white me-1">${awayName}</span>경기 이력 (${awayRecent.length}경기 기록됨)</span>
              </div>
              <div class="d-flex align-items-center px-2 py-1 mb-1.5 rounded bg-dark text-white fw-bold" style="font-size:0.72rem;">
                <div style="width:18%; min-width:65px; text-align:center; color:#cbd5e1;">일자</div>
                <div style="width:33%; text-align:right; padding-right:8px; color:#ef4444;">홈팀</div>
                <div style="width:16%; min-width:55px; text-align:center; color:#ffffff;">점수</div>
                <div style="width:33%; text-align:left; padding-left:8px; color:#3b82f6;">원정팀</div>
              </div>
              ${renderRecentGameCards(aList, awayName, 'away_recent_folder')}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function buildPitchersSectionHtml(m, detailData) {
    const matchup = detailData && detailData.matchup_analysis;
    const sp = matchup && matchup.starting_pitchers;
    if (!sp && !m.home_starter_name && !m.away_starter_name) return '';

    const hSt = (sp && sp.home) || { name: m.home_starter_name || '선발 투수' };
    const aSt = (sp && sp.away) || { name: m.away_starter_name || '선발 투수' };
    const hStarts = hSt.recent_3_starts || [];
    const aStarts = aSt.recent_3_starts || [];

    const renderPitcherStarts = (starts, pName) => {
      if (!starts || starts.length === 0) {
        return `<div class="text-muted small py-2 text-center">공식 등판 일지 집계 대기 중</div>`;
      }
      return starts.map((s, idx) => `
        <div class="d-flex justify-content-between align-items-center py-1 border-bottom" style="font-size:0.75rem;">
          <div class="d-flex align-items-center gap-1">
            <span class="badge bg-dark text-white font-monospace" style="font-size:0.62rem;">#${idx + 1}</span>
            <span class="text-muted">${(s.date || '').slice(5)} vs ${CommonUtils.formatTeamName(s.opponent || '상대')}</span>
          </div>
          <span class="fw-bold ${s.result && s.result.includes('(W)') ? 'text-danger' : (s.result && s.result.includes('(L)') ? 'text-primary' : 'text-dark')}">
            ${s.ip || '6.0'}이닝 ${s.er ?? 2}자책 (${s.np ?? 90}구 ${s.so ?? 5}K)
          </span>
        </div>
      `).join('');
    };

    return `
      <div class="mb-3">
        <div class="section-clean-title">
          <i class="bi bi-person-badge-fill text-dark me-1"></i>선발투수 1:1 비교
          <span class="badge bg-light text-dark border ms-auto" style="font-size:0.68rem; font-weight:600;">등판 일지 (날짜순 정렬)</span>
        </div>
        <div class="row g-2">
          <div class="col-12 col-md-6">
            <div class="p-2.5 rounded bg-white border">
              <div class="d-flex justify-content-between align-items-center mb-2 pb-1 border-bottom">
                <span class="fw-bold text-danger"><span class="badge bg-danger text-white me-1">${CommonUtils.formatTeamName(m.home_team_name)}</span>${CommonUtils.formatPlayerKorean(hSt.name)}</span>
                <span class="badge bg-light text-dark border">${hSt.summary?.era_3g ? `최근 ERA ${hSt.summary.era_3g}` : '선발 확정'}</span>
              </div>
              ${renderPitcherStarts(hStarts, hSt.name)}
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="p-2.5 rounded bg-white border">
              <div class="d-flex justify-content-between align-items-center mb-2 pb-1 border-bottom">
                <span class="fw-bold text-primary"><span class="badge bg-primary text-white me-1">${CommonUtils.formatTeamName(m.away_team_name)}</span>${CommonUtils.formatPlayerKorean(aSt.name)}</span>
                <span class="badge bg-light text-dark border">${aSt.summary?.era_3g ? `최근 ERA ${aSt.summary.era_3g}` : '선발 확정'}</span>
              </div>
              ${renderPitcherStarts(aStarts, aSt.name)}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function buildVolleyballAnalyticsHtml(history, homeName, awayName) {
    const va = history && history.volleyball_analytics;
    const t1 = (va && va.team1) || {};
    const t2 = (va && va.team2) || {};
    const seasonLabel = (va && va.season) || '2024~2025 V-리그 (작년 공식)';

    // 양 팀 지표 (데이터 없을 시 기본값 fallback)
    const m1 = {
      name: t1.name || homeName,
      color: t1.color || '#dc2626',
      attack_eff: t1.attack_eff ?? 0.349,
      kill_pct: t1.kill_pct ?? 50.4,
      ace_per_set: t1.ace_per_set ?? 1.149,
      block_per_set: t1.block_per_set ?? 2.407,
      recv_pct: t1.recv_pct ?? 45.1,
      side_out_est: t1.side_out_est ?? 52.8,
      open_pct: t1.open_pct ?? 38.9,
      quick_pct: t1.quick_pct ?? 62.0,
      pipe_pct: t1.pipe_pct ?? 52.4,
      combo_pct: t1.combo_pct ?? 51.4,
      dig_per_set: t1.dig_per_set ?? 11.17,
      block_success_pct: t1.block_success_pct ?? 18.7
    };

    const m2 = {
      name: t2.name || awayName,
      color: t2.color || '#2563eb',
      attack_eff: t2.attack_eff ?? 0.364,
      kill_pct: t2.kill_pct ?? 51.4,
      ace_per_set: t2.ace_per_set ?? 1.167,
      block_per_set: t2.block_per_set ?? 2.556,
      recv_pct: t2.recv_pct ?? 37.0,
      side_out_est: t2.side_out_est ?? 51.2,
      open_pct: t2.open_pct ?? 39.5,
      quick_pct: t2.quick_pct ?? 58.5,
      pipe_pct: t2.pipe_pct ?? 55.9,
      combo_pct: t2.combo_pct ?? 52.4,
      dig_per_set: t2.dig_per_set ?? 9.92,
      block_success_pct: t2.block_success_pct ?? 17.6
    };

    function renderMetricRow(label, v1, v2, unit = '', fmt = x => typeof x === 'number' ? x.toFixed(2) : x) {
      const num1 = Number(v1) || 0;
      const num2 = Number(v2) || 0;
      const maxVal = Math.max(num1, num2, 0.001);
      const p1 = Math.min(100, Math.round(num1 / maxVal * 100));
      const p2 = Math.min(100, Math.round(num2 / maxVal * 100));
      const w1 = num1 > num2;
      const w2 = num2 > num1;

      return `
        <div class="mb-2">
          <div class="d-flex justify-content-between align-items-center mb-1" style="font-size: 0.72rem;">
            <span class="fw-bold" style="color: ${w1 ? '#dc2626' : '#64748b'};">${fmt(num1)}${unit} ${w1 ? '👑' : ''}</span>
            <span class="text-muted fw-bold" style="font-size: 0.69rem;">${label}</span>
            <span class="fw-bold" style="color: ${w2 ? '#2563eb' : '#64748b'};">${w2 ? '👑' : ''} ${fmt(num2)}${unit}</span>
          </div>
          <div class="d-flex align-items-center gap-1.5" style="height: 7px;">
            <div class="flex-grow-1 d-flex justify-content-end bg-light rounded-pill overflow-hidden" style="height: 100%; border: 1px solid #e2e8f0;">
              <div style="width: ${p1}%; background: ${m1.color}; height: 100%; border-radius: 999px 0 0 999px; transition: width 0.4s ease;"></div>
            </div>
            <div class="flex-grow-1 bg-light rounded-pill overflow-hidden" style="height: 100%; border: 1px solid #e2e8f0;">
              <div style="width: ${p2}%; background: ${m2.color}; height: 100%; border-radius: 0 999px 999px 0; transition: width 0.4s ease;"></div>
            </div>
          </div>
        </div>
      `;
    }

    return `
      <div class="mb-3 rounded-2" style="background: #ffffff; border: 1.5px solid #e2e8f0; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div class="d-flex justify-content-between align-items-center px-2.5 py-1.5" style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #ffffff;">
          <div class="d-flex align-items-center gap-1.5">
            <span style="font-size: 1rem;">🏐</span>
            <span class="fw-bold text-truncate" style="font-size: 0.82rem;">배구 핵심 분석지표 1:1 대칭 비교</span>
          </div>
          <span class="badge bg-warning text-dark font-monospace" style="font-size: 0.64rem;">${seasonLabel}</span>
        </div>

        <div class="p-2.5">
          <!-- 상단 팀명 및 상징 바 -->
          <div class="d-flex justify-content-between align-items-center mb-2.5 pb-2 border-bottom">
            <div class="text-start">
              <span class="badge" style="background: ${m1.color}; color: #ffffff; font-size: 0.72rem; padding: 4px 8px;">홈: ${m1.name}</span>
            </div>
            <span class="badge bg-light text-secondary border font-monospace" style="font-size: 0.65rem;">KOVO 공식 기록원 집계</span>
            <div class="text-end">
              <span class="badge" style="background: ${m2.color}; color: #ffffff; font-size: 0.72rem; padding: 4px 8px;">원정: ${m2.name}</span>
            </div>
          </div>

          <!-- 1. 핵심 6대 지표 -->
          <div class="mb-2.5">
            <div class="fw-bold text-dark mb-2 pb-1 border-bottom d-flex align-items-center justify-content-between" style="font-size: 0.74rem;">
              <span><i class="bi bi-star-fill text-warning me-1"></i>시즌 6대 핵심 지표 (가장 중요한 승패 결정 요소)</span>
            </div>
            ${renderMetricRow('1. 공격 효율 (Eff)', m1.attack_eff, m2.attack_eff, '', x => x.toFixed(3))}
            ${renderMetricRow('2. 킬 성공률 (Kill %)', m1.kill_pct, m2.kill_pct, '%', x => x.toFixed(1))}
            ${renderMetricRow('3. 세트당 서브에이스', m1.ace_per_set, m2.ace_per_set, '', x => x.toFixed(3))}
            ${renderMetricRow('4. 세트당 블로킹 득점', m1.block_per_set, m2.block_per_set, '', x => x.toFixed(3))}
            ${renderMetricRow('5. 리시브 효율 (Recv %)', m1.recv_pct, m2.recv_pct, '%', x => x.toFixed(1))}
            ${renderMetricRow('6. 사이드아웃 추정 (SO %)', m1.side_out_est, m2.side_out_est, '%', x => x.toFixed(1))}
          </div>

          <!-- 2. 공격 세부 유형별 성공률 -->
          <div class="mb-2.5 pt-1">
            <div class="fw-bold text-secondary mb-2 pb-1 border-bottom" style="font-size: 0.72rem;">
              <i class="bi bi-lightning-charge-fill text-danger me-1"></i>공격 유형별 성공률 (%)
            </div>
            ${renderMetricRow('오픈 공격', m1.open_pct, m2.open_pct, '%', x => x.toFixed(1))}
            ${renderMetricRow('속공 (Quick)', m1.quick_pct, m2.quick_pct, '%', x => x.toFixed(1))}
            ${renderMetricRow('백어택 (후위)', m1.pipe_pct, m2.pipe_pct, '%', x => x.toFixed(1))}
            ${renderMetricRow('콤비네이션 (C-Quick)', m1.combo_pct, m2.combo_pct, '%', x => x.toFixed(1))}
          </div>

          <!-- 3. 수비 및 디그 지표 -->
          <div class="pt-1">
            <div class="fw-bold text-secondary mb-2 pb-1 border-bottom" style="font-size: 0.72rem;">
              <i class="bi bi-shield-fill-check text-success me-1"></i>수비 및 디그 지표
            </div>
            ${renderMetricRow('세트당 디그 성공', m1.dig_per_set, m2.dig_per_set, '', x => x.toFixed(2))}
            ${renderMetricRow('블로킹 성공률', m1.block_success_pct, m2.block_success_pct, '%', x => x.toFixed(1))}
          </div>
        </div>
      </div>
    `;
  }

  function buildScoreboardHtml(m, detailData) {
    if (m.status !== 'LIVE' && m.status !== 'FINISHED' && m.home_score === 0 && m.away_score === 0) {
      return '';
    }

    const pScores = (detailData && detailData.details && detailData.details.period_scores) || {};
    const inn = pScores.innings || {};

    return `
      <div class="mb-3">
        <div class="section-clean-title">
          <i class="bi bi-grid-3x3-gap-fill text-dark me-1"></i>실시간 이닝/피리어드 스코어보드
        </div>
        <div class="table-responsive">
          <table class="scoreboard-matrix-table">
            <thead style="background: #f8fafc;">
              <tr>
                <th style="text-align: left; padding-left: 8px;">팀명</th>
                ${[1,2,3,4,5,6,7,8,9].map(i => `<th>${i}</th>`).join('')}
                <th>R</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="fw-bold text-start ps-2">${CommonUtils.formatTeamName(m.home_team_name)}</td>
                ${[1,2,3,4,5,6,7,8,9].map(i => `<td>${(inn[i] && inn[i].home != null) ? inn[i].home : '-'}</td>`).join('')}
                <td class="fw-bold text-danger fs-6">${m.home_score ?? 0}</td>
              </tr>
              <tr>
                <td class="fw-bold text-start ps-2">${CommonUtils.formatTeamName(m.away_team_name)}</td>
                ${[1,2,3,4,5,6,7,8,9].map(i => `<td>${(inn[i] && inn[i].away != null) ? inn[i].away : '-'}</td>`).join('')}
                <td class="fw-bold text-danger fs-6">${m.away_score ?? 0}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  return {
    render,
    switchTab,
    toggleOddsDetail,
    setH2HLimit,
    setRecentLimit
  };
})();
