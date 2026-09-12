/**
 * TOKEON V2 Live Board Module (live_board.js)
 * TotoCan-style real-time automated ingress live board
 */

const LiveBoard = (() => {
  let _liveData = [];
  let _activeMatchId = null;
  let _pollInterval = null;
  let _onSelectCallback = null;

  function init(onSelectMatch) {
    _onSelectCallback = onSelectMatch;
    fetchLiveBoards();
    startAutoPolling();
  }

  function startAutoPolling() {
    if (_pollInterval) clearInterval(_pollInterval);
    _pollInterval = setInterval(fetchLiveBoards, 3000);
  }

  async function fetchLiveBoards() {
    try {
      const resp = await fetch('/api/v1/live/boards');
      if (resp.ok) {
        const json = await resp.json();
        if (Array.isArray(json)) {
          _liveData = json;
          render();
        } else if (json && json.status === 'success' && Array.isArray(json.boards)) {
          _liveData = json.boards;
          render();
        }
      }
    } catch(e) {
      console.warn('Live boards fetch error:', e);
    }
  }

  function render() {
    const container = document.getElementById('v2LiveBoardList');
    const badgeCount = document.getElementById('v2LiveMatchCount');
    const headerBadge = document.getElementById('v2LiveMatchBadge');
    const modalCount = document.getElementById('v2ModalLiveCount');
    if (!container) return;

    const liveMatches = _liveData.filter(b => b.status === 'LIVE' || (b.status === 'SCHEDULED' && (b.home_score > 0 || b.away_score > 0)));
    
    if (badgeCount) badgeCount.innerText = `${liveMatches.length}경기 진행중`;
    if (headerBadge) headerBadge.innerText = `${liveMatches.length}`;
    if (modalCount) modalCount.innerText = `${liveMatches.length}경기 진행중`;


    if (liveMatches.length === 0) {
      container.innerHTML = `
        <tr>
          <td colspan="5" class="text-center py-3 text-muted" style="font-size: 0.78rem;">
            현재 진행 중인 실시간 경기가 없습니다. (경기가 시작되면 자동으로 인입됩니다)
          </td>
        </tr>
      `;
      return;
    }

    const rowsHtml = liveMatches.map((item, idx) => {
      const isBaseball = (item.sport_code || '').toUpperCase() === 'BASEBALL';
      const isBasketball = (item.sport_code || '').toUpperCase() === 'BASKETBALL';
      const isSoccer = (item.sport_code || '').toUpperCase() === 'SOCCER';

      const protoNum = item.proto_no || item.seq || (850 + idx * 4);
      const homeName = CommonUtils.formatTeamName(item.home_team_name);
      const awayName = CommonUtils.formatTeamName(item.away_team_name);
      const hScore = Number(item.home_score || 0);
      const aScore = Number(item.away_score || 0);

      const isHomeLeading = hScore > aScore;
      const isAwayLeading = aScore > hScore;

      // 2D Diamond or Sport Icon
      let iconHtml = '';
      if (isBaseball) {
        const runners = item.baseball_runners || { b1: item.runner_1b, b2: item.runner_2b, b3: item.runner_3b };
        const outs = item.baseball_outs ?? item.outs ?? (hScore % 3);
        iconHtml = CommonUtils.renderMiniDiamondSvg(runners, outs);
      } else if (isBasketball) {
        iconHtml = '<span style="font-size:1.1rem;">🏀</span>';
      } else if (isSoccer) {
        iconHtml = '<span style="font-size:1.1rem;">⚽</span>';
      } else {
        iconHtml = '<span style="font-size:1.1rem;">🏐</span>';
      }

      // Time / Inning Badge
      let timeBadgeText = item.live_period || item.inning_status || item.status_text || '진행중';
      if (isBaseball && !item.inning_status) {
        const inn = item.current_inning || 2;
        const isBottom = item.is_bottom ? '말' : '초';
        timeBadgeText = `${inn}회${isBottom}`;
      } else if (isBasketball && !item.live_period) {
        timeBadgeText = `4쿼 2'42`;
      }

      const isActive = (_activeMatchId === item.match_id || _activeMatchId === item.id);

      return `
        <tr class="live-board-row ${isActive ? 'active' : ''}" onclick="LiveBoard.selectMatch(${item.match_id || item.id})">
          <td class="text-center font-monospace fw-bold text-muted" style="width: 48px; font-size: 0.74rem;">
            ${protoNum}
          </td>
          <td class="text-center" style="width: 42px;">
            ${iconHtml}
          </td>
          <td>
            <div class="d-flex align-items-center justify-content-between px-1">
              <span class="fw-bold text-truncate ${isHomeLeading ? 'text-danger' : 'text-dark'}" style="max-width: 95px;" title="${homeName}">
                ${homeName}
              </span>
              <span class="fw-bold font-monospace px-2" style="font-size: 0.92rem; letter-spacing: 1px;">
                <b class="${isHomeLeading ? 'text-danger' : 'text-dark'}">${hScore}</b>
                <span class="text-muted" style="font-size:0.75rem;">:</span>
                <b class="${isAwayLeading ? 'text-danger' : 'text-dark'}">${aScore}</b>
              </span>
              <span class="fw-bold text-truncate ${isAwayLeading ? 'text-danger' : 'text-dark'}" style="max-width: 95px;" title="${awayName}">
                ${awayName}
              </span>
            </div>
          </td>
          <td class="text-center" style="width: 80px;">
            <span class="live-time-badge">${timeBadgeText}</span>
          </td>
          <td class="text-center" style="width: 36px;">
            <span style="cursor: pointer; font-size: 0.9rem; color: #0284c7;" title="실시간 알림 On">🔔</span>
          </td>
        </tr>
      `;
    }).join('');

    container.innerHTML = rowsHtml;
  }

  function selectMatch(matchId) {
    _activeMatchId = matchId;
    render();
    if (typeof _onSelectCallback === 'function') {
      _onSelectCallback(matchId);
    }
  }

  return {
    init,
    render,
    selectMatch,
    getLiveData: () => _liveData
  };
})();
