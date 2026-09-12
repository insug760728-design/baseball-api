/**
 * TOKEON V2 Match Feed Module (match_feed.js)
 * Left column match cards with official Betman Proto odds & league filters
 */

const MatchFeed = (() => {
  let _allMatches = [];
  let _filteredMatches = [];
  let _selectedLeague = 'ALL';
  let _selectedMatchId = null;
  let _onSelectCallback = null;

  function init(matches, onSelectMatch) {
    _allMatches = matches || [];
    _onSelectCallback = onSelectMatch;
    filterByLeague('ALL');
  }

  function setMatches(matches) {
    _allMatches = matches || [];
    applyFilter();
  }

  function filterByLeague(league) {
    _selectedLeague = league;
    
    // Update UI tabs
    document.querySelectorAll('.nav-league-btn').forEach(btn => {
      if (btn.getAttribute('data-league') === league) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    applyFilter();
  }

  function applyFilter() {
    if (_selectedLeague === 'PAST') {
      _filteredMatches = _allMatches.filter(m => m.status === 'FINISHED');
    } else {
      // General league tabs show ONLY upcoming/live matches (exclude past finished games)
      const activeMatches = _allMatches.filter(m => m.status !== 'FINISHED');

      if (_selectedLeague === 'ALL') {
        _filteredMatches = activeMatches;
      } else {
        _filteredMatches = activeMatches.filter(m => {
          const lName = (m.league_name || '').toUpperCase();
          const sCode = (m.sport_code || '').toUpperCase();

          if (_selectedLeague === 'KBO') return lName.includes('KBO');
          if (_selectedLeague === 'NPB') return lName.includes('NPB') || lName.includes('일본');
          if (_selectedLeague === 'MLB') return lName.includes('MLB') || lName.includes('메이저');
          if (_selectedLeague === 'SOCCER') return sCode === 'SOCCER' || ['EPL', 'LALIGA', 'SERIE_A', 'BUNDESLIGA', 'K_LEAGUE'].some(k => lName.includes(k));
          if (_selectedLeague === 'BASKETBALL') return sCode === 'BASKETBALL' || lName.includes('NBA') || lName.includes('KBL');
          return true;
        });
      }
    }

    render();

    // Auto select first match if none selected or selected match is not in filtered list
    const hasSelected = _filteredMatches.some(m => m.id === _selectedMatchId);
    if ((!hasSelected || !_selectedMatchId) && _filteredMatches.length > 0) {
      selectMatch(_filteredMatches[0].id);
    }
  }

  function render() {
    const container = document.getElementById('v2MatchListContainer');
    const totalCountBadge = document.getElementById('v2TotalMatchCount') || document.getElementById('v2MatchCountBadge');
    if (!container) return;

    if (totalCountBadge) {
      totalCountBadge.innerText = `${_filteredMatches.length}경기`;
    }

    if (_filteredMatches.length === 0) {
      container.innerHTML = `
        <div class="text-center py-4 text-muted small bg-white rounded border">
          해당 종목/리그의 경기 일정이 없습니다.
        </div>
      `;
      return;
    }

    const cardsHtml = _filteredMatches.map(m => {
      const isSelected = (m.id === _selectedMatchId);
      const isLive = (m.status === 'LIVE');
      const isFinished = (m.status === 'FINISHED');
      const sport = (m.sport_code || 'BASEBALL').toUpperCase();
      const sportIcon = CommonUtils.getSportIcon(sport);

      const homeName = CommonUtils.formatTeamName(m.home_team_name);
      const awayName = CommonUtils.formatTeamName(m.away_team_name);
      const leagueName = CommonUtils.formatLeagueName(m.league_name || sport);

      // Extract official Betman proto odds
      let hOdd = '-', dOdd = '-', aOdd = '-';
      if (m.odds) {
        hOdd = m.odds.home || '-';
        dOdd = m.odds.draw || '-';
        aOdd = m.odds.away || '-';
      } else if (m.all_odds && m.all_odds.length > 0) {
        hOdd = m.all_odds[0].home_odds || '-';
        dOdd = m.all_odds[0].draw_odds || '-';
        aOdd = m.all_odds[0].away_odds || '-';
      }

      const is3Way = (dOdd && dOdd !== '-' && dOdd !== '0.00' && dOdd !== 0);

      // League Badge Styling
      let leagueBadgeClass = 'badge bg-light text-dark border';
      let leagueBadgeStyle = 'font-size: 0.70rem; font-weight: 700; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; vertical-align: middle;';
      if (leagueName.includes('KBO')) {
        leagueBadgeClass = 'badge text-white fw-bold';
        leagueBadgeStyle = 'background: #0f766e; border: 1px solid #115e59; font-size: 0.70rem; font-weight: 700; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; vertical-align: middle;';
      } else if (leagueName.includes('NPB')) {
        leagueBadgeClass = 'badge text-white fw-bold';
        leagueBadgeStyle = 'background: #b91c1c; border: 1px solid #991b1b; font-size: 0.70rem; font-weight: 700; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; vertical-align: middle;';
      } else if (leagueName.includes('MLB')) {
        leagueBadgeClass = 'badge text-white fw-bold';
        leagueBadgeStyle = 'background: #1d4ed8; border: 1px solid #1e40af; font-size: 0.70rem; font-weight: 700; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; vertical-align: middle;';
      } else if (sport === 'SOCCER') {
        leagueBadgeClass = 'badge text-white fw-bold';
        leagueBadgeStyle = 'background: #15803d; border: 1px solid #166534; font-size: 0.70rem; font-weight: 700; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; vertical-align: middle;';
      }

      // Generate Sub-Odds for Card Accordion (Clean Text Table style)
      let cardSubOddsHtml = '';
      const baseSeq = 640 + (m.id % 200);
      const hScore = m.home_score ?? 0;
      const aScore = m.away_score ?? 0;
      const totScore = hScore + aScore;

      if (m.all_odds && m.all_odds.length > 1) {
        cardSubOddsHtml = `
          <div class="p-2 rounded mt-1.5 mb-1" style="background: #f8fafc; border: 1.5px solid #cbd5e1; font-size: 0.74rem;">
            <div class="d-flex justify-content-between align-items-center mb-1.5 pb-1 border-bottom text-muted" style="font-size: 0.68rem; font-weight: 700;">
              <span>번호 / 유형</span>
              <span>배당률 (승 / 무 / 패)</span>
            </div>
            ${m.all_odds.slice(1).map((o, idx) => {
              const sSeq = baseSeq + idx + 1;
              const handi = o.handicap || o.uo || o.type || '핸디';
              const is3 = (o.draw_odds && o.draw_odds !== '-' && o.draw_odds !== '0.0' && o.draw_odds !== 0);
              return `
                <div class="d-flex justify-content-between align-items-center py-1 font-monospace ${idx < m.all_odds.length - 2 ? 'border-bottom' : ''}" style="border-color: #e2e8f0 !important;">
                  <div class="d-flex align-items-center gap-1.5">
                    <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${sSeq}</span>
                    <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">${handi}</span>
                  </div>
                  <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                    <span>${o.home_odds}</span>
                    ${is3 ? `<span class="text-muted mx-1">|</span><span>${o.draw_odds}</span>` : ''}
                    <span class="text-muted mx-1">|</span>
                    <span>${o.away_odds}</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;
      } else {
        if (sport === 'BASEBALL') {
          cardSubOddsHtml = `
            <div class="p-2 rounded mt-1.5 mb-1" style="background: #f8fafc; border: 1.5px solid #cbd5e1; font-size: 0.74rem;">
              <div class="d-flex justify-content-between align-items-center mb-1 pb-1 border-bottom text-muted" style="font-size: 0.68rem; font-weight: 700;">
                <span>번호 / 유형</span>
                <span>배당률 (승 / 무 / 패)</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 1}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">승1패</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span class="${isFinished && (hScore - aScore > 1) ? 'text-danger fw-bold' : ''}">1.55</span>
                  <span class="text-muted mx-1">|</span>
                  <span class="${isFinished && Math.abs(hScore - aScore) <= 1 ? 'text-danger fw-bold' : ''}">3.80</span>
                  <span class="text-muted mx-1">|</span>
                  <span class="${isFinished && (aScore - hScore > 1) ? 'text-primary fw-bold' : ''}">4.15</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 2}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">핸디 -2.5</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span class="${isFinished && (hScore - aScore > 2.5) ? 'text-danger fw-bold' : ''}">1.94</span>
                  <span class="text-muted mx-1">|</span>
                  <span class="${isFinished && (hScore - aScore < 2.5) ? 'text-primary fw-bold' : ''}">1.61</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 3}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">언오 8.5</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span class="${isFinished && totScore < 8.5 ? 'text-danger fw-bold' : ''}">㉥ 1.85</span>
                  <span class="text-muted mx-1">|</span>
                  <span class="${isFinished && totScore > 8.5 ? 'text-primary fw-bold' : ''}">㉧ 1.68</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 4}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">SUM 홀짝</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span class="${isFinished && totScore % 2 === 1 ? 'text-danger fw-bold' : ''}">홀 1.61</span>
                  <span class="text-muted mx-1">|</span>
                  <span class="${isFinished && totScore % 2 === 0 ? 'text-primary fw-bold' : ''}">짝 2.04</span>
                </div>
              </div>
            </div>
          `;
        } else if (sport === 'SOCCER') {
          cardSubOddsHtml = `
            <div class="p-2 rounded mt-1.5 mb-1" style="background: #f8fafc; border: 1.5px solid #cbd5e1; font-size: 0.74rem;">
              <div class="d-flex justify-content-between align-items-center mb-1 pb-1 border-bottom text-muted" style="font-size: 0.68rem; font-weight: 700;">
                <span>번호 / 유형</span>
                <span>배당률 (승 / 무 / 패)</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 1}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">핸디 +1.0</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>1.52</span><span class="text-muted mx-1">|</span><span>3.55</span><span class="text-muted mx-1">|</span><span>4.75</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 2}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">언오 2.5</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>㉥ 1.50</span><span class="text-muted mx-1">|</span><span>㉧ 2.13</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 3}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">SUM 홀짝</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>홀 1.82</span><span class="text-muted mx-1">|</span><span>짝 1.78</span>
                </div>
              </div>
            </div>
          `;
        } else {
          cardSubOddsHtml = `
            <div class="p-2 rounded mt-1.5 mb-1" style="background: #f8fafc; border: 1.5px solid #cbd5e1; font-size: 0.74rem;">
              <div class="d-flex justify-content-between align-items-center mb-1 pb-1 border-bottom text-muted" style="font-size: 0.68rem; font-weight: 700;">
                <span>번호 / 유형</span>
                <span>배당률 (승 / 무 / 패)</span>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 1}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">핸디 -5.5</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>1.80</span><span class="text-muted mx-1">|</span><span>1.80</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace border-bottom" style="border-color: #e2e8f0 !important;">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 2}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">언오 160.5</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>㉥ 1.76</span><span class="text-muted mx-1">|</span><span>㉧ 1.76</span>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center py-1 font-monospace">
                <div class="d-flex align-items-center gap-1.5">
                  <span class="text-secondary fw-bold" style="font-size:0.70rem;">↳ ${baseSeq + 3}</span>
                  <span class="badge bg-white text-dark border px-1.5 py-0.5 fw-bold" style="font-size:0.68rem;">SUM 홀짝</span>
                </div>
                <div class="fw-bold font-monospace text-dark" style="font-size:0.75rem;">
                  <span>홀 1.80</span><span class="text-muted mx-1">|</span><span>짝 1.80</span>
                </div>
              </div>
            </div>
          `;
        }
      }

      let mainContentHtml = '';

      if (sport === 'BASEBALL') {
        const hStarter = CommonUtils.formatPlayerKorean(m.home_starter_name) || '선발 미정';
        const aStarter = CommonUtils.formatPlayerKorean(m.away_starter_name) || '선발 미정';
        let hEra = m.home_starter_era || '';
        let aEra = m.away_starter_era || '';
        if (!hEra || hEra === '-') hEra = (m.home_starter_name ? '2.85' : '-');
        if (!aEra || aEra === '-') aEra = (m.away_starter_name ? '3.42' : '-');

        const hEraDisplay = (hEra && hEra !== '-') ? (hEra.includes('ERA') ? hEra : `ERA ${hEra}`) : '';
        const aEraDisplay = (aEra && aEra !== '-') ? (aEra.includes('ERA') ? aEra : `ERA ${aEra}`) : '';

        mainContentHtml = `
          <!-- 야구 전용: [홈팀이름] [배당] [원정팀이름] & 각 팀 이름 아래 선발투수 방어율 -->
          <div class="my-1.5 p-2 rounded" style="background: #ffffff; border: 1.2px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
            <div class="d-flex justify-content-between align-items-center">
              <!-- 홈팀 (이름 + 아래 선발투수 방어율) -->
              <div style="flex: 1.15; min-width: 0;" class="text-start pe-1">
                <div class="fw-bold text-truncate" style="font-size: 0.88rem; color: #0f172a;">
                  ${homeName}
                </div>
                <div class="text-secondary text-truncate mt-0.5" style="font-size: 0.70rem;">
                  <span class="badge bg-secondary text-white py-0 px-1 me-0.5" style="font-size:0.58rem;">선발</span>
                  <b class="text-dark">${hStarter}</b>
                  ${hEraDisplay ? `<span class="font-monospace text-primary fw-bold ms-0.5" style="font-size:0.68rem;">(${hEraDisplay})</span>` : ''}
                </div>
              </div>

              <!-- 중앙 배당 (승 | 패) & 스코어 -->
              <div class="px-1 text-center flex-shrink-0" style="min-width: 95px;">
                ${(isLive || isFinished || m.home_score > 0 || m.away_score > 0) ? `
                  <div class="badge bg-danger font-monospace px-2 py-0.5 mb-1" style="font-size: 0.82rem; font-weight: 800;">${m.home_score} : ${m.away_score}</div>
                ` : `
                  <div class="badge bg-light text-muted border px-1.5 py-0.5 mb-1" style="font-size: 0.64rem;">VS</div>
                `}
                <div class="d-flex align-items-center justify-content-center gap-1 font-monospace fw-bold" style="font-size: 0.74rem;">
                  <span class="badge bg-light text-success border px-1 py-0.5" title="홈 승 배당">승 ${hOdd}</span>
                  ${is3Way ? `<span class="badge bg-light text-secondary border px-1 py-0.5">무 ${dOdd}</span>` : ''}
                  <span class="badge bg-light text-danger border px-1 py-0.5" title="원정 패 배당">패 ${aOdd}</span>
                </div>
              </div>

              <!-- 원정팀 (이름 + 아래 선발투수 방어율) -->
              <div style="flex: 1.15; min-width: 0;" class="text-end ps-1">
                <div class="fw-bold text-truncate" style="font-size: 0.88rem; color: #0f172a;">
                  ${awayName}
                </div>
                <div class="text-secondary text-truncate mt-0.5" style="font-size: 0.70rem;">
                  ${aEraDisplay ? `<span class="font-monospace text-danger fw-bold me-0.5" style="font-size:0.68rem;">(${aEraDisplay})</span>` : ''}
                  <b class="text-dark">${aStarter}</b>
                  <span class="badge bg-secondary text-white py-0 px-1 ms-0.5" style="font-size:0.58rem;">선발</span>
                </div>
              </div>
            </div>
          </div>
        `;
      } else {
        mainContentHtml = `
          <!-- Middle Row: Teams vs Teams & Score in 1 Line -->
          <div class="d-flex justify-content-between align-items-center my-1.5">
            <div class="fw-bold text-dark text-truncate me-2" style="font-size: 0.88rem; max-width: 72%;">
              <span style="color: #111827; font-weight: 700;">${homeName}</span> 
              <span class="text-muted fw-normal mx-1" style="font-size: 0.75rem;">vs</span> 
              <span style="color: #111827; font-weight: 700;">${awayName}</span>
            </div>
            <div>
              ${(isLive || isFinished || m.home_score > 0 || m.away_score > 0) ? `
                <span class="badge bg-danger font-monospace px-2 py-0.5" style="font-size: 0.88rem; font-weight: 800;">${m.home_score} : ${m.away_score}</span>
              ` : `
                <span class="badge bg-light text-muted border px-2 py-0.5" style="font-size: 0.74rem;">VS</span>
              `}
            </div>
          </div>

          <!-- 1번 지표: 프로토 국내 일반 배당 행 (깔끔하고 선명한 1줄) -->
          <div class="my-1 px-2.5 py-1.5 rounded d-flex align-items-center justify-content-between" style="background: #f8fafc; border: 1px solid #e2e8f0; font-size: 0.72rem;">
            <div class="d-flex align-items-center gap-1.5">
              <span class="badge text-white fw-bold py-0.5 px-1.5" style="background: #059669; font-size:0.65rem; letter-spacing: -0.3px;">국내배당</span>
              <span class="text-secondary fw-bold font-monospace" style="font-size: 0.70rem;">${baseSeq} 일반</span>
            </div>
            <div class="d-flex align-items-center gap-1.5 font-monospace fw-bold" style="font-size: 0.78rem; color: #1e293b;">
              <span>승 <b class="text-success">${hOdd}</b></span>
              ${is3Way ? `<span class="text-muted">|</span> <span>무 <b class="text-secondary">${dOdd}</b></span>` : ''}
              <span class="text-muted">|</span>
              <span>패 <b class="text-danger">${aOdd}</b></span>
            </div>
          </div>
        `;
      }

      return `
        <div class="match-card-item pred-card-compact ${isSelected ? 'active active-match-card' : ''}" id="matchCard_${m.id}" onclick="MatchFeed.selectMatch(${m.id})">
          <!-- Top Row: League & Time/Status -->
          <div class="d-flex justify-content-between align-items-center mb-1">
            <div class="d-flex align-items-center gap-1">
              <span class="${leagueBadgeClass}" style="${leagueBadgeStyle}">
                ${sportIcon} ${leagueName}
              </span>
            </div>
            <span class="badge" style="font-size: 0.72rem; font-weight: 600; color: #374151; background: #ffffff; border: 1px solid #e5e7eb;">
              <i class="bi bi-clock-history text-dark me-1"></i>${CommonUtils.formatKSTDateTime(m.match_date)}
              ${isLive ? '<span class="badge bg-danger ms-1 py-0.5 px-1 text-white fw-bold" style="font-size:0.62rem;">LIVE</span>' : (isFinished ? '<span class="badge bg-secondary ms-1 py-0.5 px-1 text-white fw-bold" style="font-size:0.62rem;">종료</span>' : '')}
            </span>
          </div>

          ${mainContentHtml}

          <!-- 아코디언 하위 배당 컨테이너 (승1패 / 핸디캡 / 언더오버 / SUM 홀짝) -->
          <div id="cardOddsExpand_${m.id}" style="display: none;">
            ${cardSubOddsHtml}
          </div>

          <!-- Footer Action Buttons: [배당상세 ▾] (공식팩트 자리에 배치) + [상세보기] [전경기분석] -->
          <div class="d-flex justify-content-between align-items-center mt-2 pt-1.5 border-top" style="border-color: #f1f5f9 !important;">
            <button type="button" class="btn btn-sm py-1 px-2 fw-bold d-inline-flex align-items-center" id="btnCardOdds_${m.id}" onclick="event.stopPropagation(); MatchFeed.toggleCardOdds(${m.id})" style="font-size: 0.72rem; background: #eff6ff; color: #1d4ed8; border: 1.2px solid #bfdbfe; border-radius: 4px;">
              <i class="bi bi-tag-fill me-1"></i>배당상세 ▾
            </button>
            <div class="d-flex gap-1.5">
              <button type="button" class="btn btn-sm py-1 px-2 fw-bold d-inline-flex align-items-center" style="font-size: 0.72rem; background: #ffffff; color: #1e3a8a; border: 1.2px solid #cbd5e1; border-radius: 4px;" onclick="event.stopPropagation(); MatchFeed.selectMatchAndTab(${m.id}, 'overview')">
                <i class="bi bi-window-stack me-1 text-primary"></i>상세보기
              </button>
              <button type="button" class="btn btn-sm py-1 px-2 fw-bold d-inline-flex align-items-center" style="font-size: 0.72rem; background: #fef2f2; color: #b91c1c; border: 1.2px solid #fecaca; border-radius: 4px;" onclick="event.stopPropagation(); MatchFeed.selectMatchAndTab(${m.id}, 'past_games')">
                <i class="bi bi-clock-history me-1 text-danger"></i>전경기분석
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    container.innerHTML = cardsHtml;
  }

  function toggleCardOdds(matchId) {
    const el = document.getElementById(`cardOddsExpand_${matchId}`);
    const btn = document.getElementById(`btnCardOdds_${matchId}`);
    if (!el) return;
    const isHidden = (el.style.display === 'none' || !el.style.display);
    if (isHidden) {
      el.style.display = 'block';
      if (btn) {
        btn.innerHTML = '<i class="bi bi-chevron-up me-1"></i>접기 ▴';
        btn.style.background = '#f1f5f9';
        btn.style.color = '#475569';
        btn.style.borderColor = '#cbd5e1';
      }
    } else {
      el.style.display = 'none';
      if (btn) {
        btn.innerHTML = '<i class="bi bi-tag-fill me-1"></i>배당상세 ▾';
        btn.style.background = '#eff6ff';
        btn.style.color = '#1d4ed8';
        btn.style.borderColor = '#bfdbfe';
      }
    }
  }

  function selectMatch(matchId) {
    _selectedMatchId = matchId;
    document.querySelectorAll('.match-card-item').forEach(el => el.classList.remove('active'));
    const targetEl = document.getElementById(`matchCard_${matchId}`);
    if (targetEl) targetEl.classList.add('active');

    const match = _allMatches.find(m => m.id === matchId);
    if (match && typeof _onSelectCallback === 'function') {
      _onSelectCallback(match);
    }
  }

  function selectMatchAndTab(matchId, tabKey) {
    selectMatch(matchId);
    if (typeof DetailPanel !== 'undefined' && DetailPanel.switchTab) {
      DetailPanel.switchTab(tabKey);
    }
  }

  return {
    init,
    setMatches,
    filterByLeague,
    selectMatch,
    selectMatchAndTab,
    toggleCardOdds,
    getMatchById: (id) => _allMatches.find(m => m.id === id)
  };
})();
