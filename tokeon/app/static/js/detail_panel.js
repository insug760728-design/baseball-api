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

    const homeName = CommonUtils.formatTeamName(m.home_team_name);
    const awayName = CommonUtils.formatTeamName(m.away_team_name);

    const history = data.history || {};
    const h2hMatches = history.h2h_matches || [];
    const homeRecent = history.home_recent || [];
    const awayRecent = history.away_recent || [];

    // 1. Dual Official Odds Section (국내 프로토 배당 vs 해외 배당)
    const dualOddsHtml = buildDualOddsHtml(m, data.odds);

    // 1-1. 양 팀 직전 1경기 핵심 비교 대칭 테이블 (야구/축구 종목별 공식 수치 1:1 매칭)
    const lastMatchCompareHtml = buildLastMatchCompareTableHtml(homeRecent, awayRecent, homeName, awayName, sport);

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
        ${isBaseball ? `
          <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'pitchers' ? 'active' : ''}" data-tab="pitchers" onclick="DetailPanel.switchTab('pitchers')">
            <i class="bi bi-person-badge-fill text-dark me-1"></i>선발투수 등판일지
          </button>
        ` : ''}
        <button type="button" class="btn btn-sm detail-sub-tab ${activeTab === 'all' ? 'active' : ''}" data-tab="all" onclick="DetailPanel.switchTab('all')">
          <i class="bi bi-grid-fill me-1"></i>전체보기
        </button>
      </div>

      <!-- Tab 1: 전경기분석 (직전 1경기 핵심비교 + 상대전적 + 각 팀 최근 경기 상세 분석) -->
      <div id="tabContent-past_games" class="detail-tab-pane" style="display: ${activeTab === 'past_games' ? 'block' : 'none'};">
        ${lastMatchCompareHtml}
        ${h2hHtml}
        ${recentHtml}
      </div>

      <!-- Tab 2: 공식 배당 & 스코어보드 -->
      <div id="tabContent-overview" class="detail-tab-pane" style="display: ${activeTab === 'overview' ? 'block' : 'none'};">
        ${dualOddsHtml}
        ${scoreboardHtml}
      </div>

      <!-- Tab 3: 선발투수 등판일지 (야구) -->
      ${isBaseball ? `
        <div id="tabContent-pitchers" class="detail-tab-pane" style="display: ${activeTab === 'pitchers' ? 'block' : 'none'};">
          ${pitchersHtml}
        </div>
      ` : ''}

      <!-- Tab 4: 전체 한눈에 보기 -->
      <div id="tabContent-all" class="detail-tab-pane" style="display: ${activeTab === 'all' ? 'block' : 'none'};">
        ${lastMatchCompareHtml}
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

      let res = g.result;
      if (!res) {
        res = Number(tScore) > Number(oScore) ? 'W' : (Number(tScore) < Number(oScore) ? 'L' : 'D');
      }
      const resText = (res === 'W' || res === 'WIN') ? '승' : ((res === 'D' || res === 'DRAW') ? '무' : '패');
      const resBg = (res === 'W' || res === 'WIN') ? '#dc2626' : ((res === 'D' || res === 'DRAW') ? '#4b5563' : '#2563eb');

      const title = isHome ? `${myName} vs ${opp}` : `${opp} vs ${myName}`;
      const score = isHome ? `<b>${tScore}</b> : ${oScore}` : `${oScore} : <b>${tScore}</b>`;
      const badge = `<span class="badge py-0.5 px-1.5 text-white fw-bold" style="background:${resBg}; font-size:0.62rem;">${isHome ? '홈' : '원정'} ${resText}</span>`;

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
      const isSmall = label.includes('선발') || label.includes('사사구');

      rowsHtml += `
        <tr>
          <td class="fw-bold text-dark py-1 px-1" style="${isSmall ? 'font-size:0.68rem;' : ''}">${hM.val}</td>
          <td class="bg-light fw-bold text-muted py-1 px-1" style="font-size: 0.70rem;">${label}</td>
          <td class="fw-bold text-dark py-1 px-1" style="${isSmall ? 'font-size:0.68rem;' : ''}">${aM.val}</td>
        </tr>
      `;
    }

    const sportIcon = isBaseball ? '⚾' : (isSoccer ? '⚽' : '🏀');

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
                <th style="width: 38%; padding: 4px 2px;" class="text-primary text-truncate">
                  <div class="fw-bold text-truncate" style="font-size:0.82rem; color:#0f172a;">[${hData.title}]</div>
                  <div class="mt-0.5 d-flex align-items-center justify-content-center gap-1">
                    ${hData.badge}
                    <span class="badge" style="background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; font-size:0.62rem;">홈 : 원정</span>
                  </div>
                </th>
                <th style="width: 24%; padding: 4px 2px; background: #f1f5f9; color: #334155; font-size: 0.72rem; vertical-align: middle;">
                  <span class="badge" style="background:#0f172a; color:#ffffff; font-size:0.68rem; padding:3px 6px;">수치</span>
                </th>
                <th style="width: 38%; padding: 4px 2px;" class="text-danger text-truncate">
                  <div class="fw-bold text-truncate" style="font-size:0.82rem; color:#0f172a;">[${aData.title}]</div>
                  <div class="mt-0.5 d-flex align-items-center justify-content-center gap-1">
                    ${aData.badge}
                    <span class="badge" style="background:#fef2f2; color:#b91c1c; border:1px solid #fecaca; font-size:0.62rem;">홈 : 원정</span>
                  </div>
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
    const list = matches.slice(0, limit);
    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';

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
        }

        return `
          <div class="p-2 mb-2 rounded bg-white border">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center gap-1.5">
                <span class="badge bg-dark text-white font-monospace" style="font-size:0.65rem;">#${idx + 1}${idx === 0 ? ' (최신)' : ''}</span>
                <span class="text-muted font-monospace small">${date}</span>
              </div>
              <div class="d-flex align-items-center gap-2">
                <span class="fw-bold text-dark">${team1}</span>
                <span class="fw-bold font-monospace px-2 py-0.5 rounded bg-light border text-danger" style="font-size: 0.95rem;">${score1} : ${score2}</span>
                <span class="fw-bold text-dark">${team2}</span>
              </div>
              <span class="badge bg-light text-secondary border" style="font-size:0.65rem;">공식 맞대결</span>
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
            <i class="bi bi-arrow-left-right text-primary me-1"></i>상대전적 (맞대결 이력)
            <span class="badge bg-light text-dark border ms-1" style="font-size:0.68rem; font-weight:600;">● 실시간 날짜순 정렬 (총 ${totalCount}경기 보존)</span>
          </div>
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-xs ${_h2hLimit === 3 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit(3)">최근 3G</button>
            <button type="button" class="btn btn-xs ${_h2hLimit === 5 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit(5)">최근 5G</button>
            <button type="button" class="btn btn-xs ${_h2hLimit === 'all' ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setH2HLimit('all')">전체보기 (${totalCount})</button>
          </div>
        </div>
        ${cardsHtml}
      </div>
    `;
  }

  function buildRecentSectionHtml(homeRecent, awayRecent, homeName, awayName, sport) {
    const limit = _recentLimit === 'all' ? 999 : _recentLimit;
    const hList = homeRecent.slice(0, limit);
    const aList = awayRecent.slice(0, limit);
    const isBaseball = sport === 'BASEBALL';
    const isSoccer = sport === 'SOCCER';

    const renderRecentGameCards = (list, myTeam) => {
      if (!list || list.length === 0) {
        return `<div class="text-muted py-3 text-center small">최근 공식 경기 데이터 집계 대기 중입니다.</div>`;
      }
      return list.map((g, idx) => {
        const isHome = g.is_home ?? (g.home_away === '홈');
        const opp = CommonUtils.formatTeamName(g.opponent || (isHome ? g.away_team_name : g.home_team_name) || '상대팀');
        const myScore = g.team_score ?? (isHome ? g.home_score : g.away_score) ?? 0;
        const oppScore = g.opp_score ?? (isHome ? g.away_score : g.home_score) ?? 0;
        const res = g.result || (myScore > oppScore ? 'W' : (myScore < oppScore ? 'L' : 'D'));

        const isWin = res === 'WIN' || res === 'W';
        const isDraw = res === 'DRAW' || res === 'D';
        const resBadge = isWin
          ? '<span class="badge bg-danger text-white">승</span>'
          : (isDraw ? '<span class="badge bg-secondary text-white">무</span>' : '<span class="badge bg-primary text-white">패</span>');
        const resColor = isWin ? 'text-danger' : (isDraw ? 'text-secondary' : 'text-primary');

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
                    <span class="text-muted ms-auto font-monospace">${bp.ip}이닝 ${bp.er ?? 0}자책 ${bp.so ?? 0}K ${bp.bb ?? 0}사사구</span>
                  </div>
                ` : ''}
                ${hasBat ? `
                  <div class="d-flex align-items-center text-dark">
                    <span class="badge bg-primary text-white me-1 px-1 py-0.5" style="font-size: 0.62rem;">타격</span>
                    <span class="text-dark font-monospace fw-bold me-1">${bat.hits}안타 ${bat.home_runs ? `<span class="text-danger">(${bat.home_runs}홈런)</span>` : '(0홈런)'}</span>
                    <span class="text-muted ms-auto font-monospace">${bat.walks ?? 0}사사구 ${bat.strikeouts ?? 0}삼진 ${bat.runs ?? myScore}득점</span>
                  </div>
                ` : ''}
              </div>
            `;
          }
        } else if (isSoccer) {
          const hasScorers = scorers.length > 0;
          const hasStats = stats.possession != null || stats.shots != null;

          if (hasScorers || hasStats) {
            breakdownHtml = `
              <div class="mt-1.5 pt-1.5 border-top" style="font-size: 0.72rem;">
                <div class="d-flex align-items-center mb-1 text-dark">
                  <span class="badge bg-success text-white me-1 px-1 py-0.5" style="font-size: 0.62rem;">득점</span>
                  <span class="text-truncate fw-bold text-dark">${scorers.join(', ') || '무득점'}</span>
                </div>
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
        }

        return `
          <div class="p-2.5 mb-2 rounded bg-white border">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center gap-1.5">
                <span class="badge bg-dark text-white font-monospace" style="font-size:0.65rem;">#${idx + 1}${idx === 0 ? ' (최신)' : ''}</span>
                ${resBadge}
                <span class="text-muted font-monospace small">${g.date || ''}</span>
                <span class="text-dark fw-bold small ms-1">vs ${opp}</span>
              </div>
              <span class="fw-bold font-monospace fs-6 ${resColor}">${myScore} : ${oppScore}</span>
            </div>
            ${breakdownHtml}
          </div>
        `;
      }).join('');
    };

    return `
      <div class="mb-3">
        <div class="section-clean-title d-flex justify-content-between align-items-center">
          <div>
            <i class="bi bi-clock-history text-danger me-1"></i>전경기 상세 분석 (실시간 날짜순 자동 갱신)
            <span class="badge bg-light text-dark border ms-1" style="font-size:0.68rem; font-weight:600;">● 경기 종료 시 날짜순 자동 갱신</span>
          </div>
          <div class="btn-group btn-group-sm" role="group">
            <button type="button" class="btn btn-xs ${_recentLimit === 3 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit(3)">최근 3G</button>
            <button type="button" class="btn btn-xs ${_recentLimit === 5 ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit(5)">최근 5G</button>
            <button type="button" class="btn btn-xs ${_recentLimit === 'all' ? 'btn-primary' : 'btn-outline-secondary'}" onclick="DetailPanel.setRecentLimit('all')">전체보기</button>
          </div>
        </div>
        <div class="row g-2">
          <div class="col-12 col-md-6">
            <div class="p-2 rounded bg-light border">
              <div class="fw-bold text-dark mb-2 pb-1 border-bottom d-flex align-items-center justify-content-between">
                <span><span class="badge bg-danger text-white me-1">${homeName}</span>경기 이력 (${homeRecent.length}경기 기록됨)</span>
              </div>
              ${renderRecentGameCards(hList, homeName)}
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="p-2 rounded bg-light border">
              <div class="fw-bold text-dark mb-2 pb-1 border-bottom d-flex align-items-center justify-content-between">
                <span><span class="badge bg-primary text-white me-1">${awayName}</span>경기 이력 (${awayRecent.length}경기 기록됨)</span>
              </div>
              ${renderRecentGameCards(aList, awayName)}
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
