/**
 * TOKEON V2 Betman Toto 14-Match Interactive Modal Module (toto_modal.js)
 * Real-time Betman official sync for G011(승무패), G024(승1패), G027(승5패)
 * 2-Column Split: All 14 matches visible in 1 screen with zero vertical scrolling
 * Real-Time 1st~4th Tier Winning Probability (Poisson Binomial Distribution) & Prize Payout Calculator
 * Draggable popup support
 */

const TotoModal = (() => {
  let _currentGmId = 'G011';
  let _totoData = null;
  let _selections = {}; // { gmId: { matchSeq: { 'W': bool, 'D': bool, 'L': bool } } }
  let _modalInstance = null;

  function init() {
    makeModalDraggable('totoModal');
    makeModalDraggable('liveCenterModal');
  }

  async function open(gmId = 'G011', forceRefresh = false) {
    _currentGmId = gmId;
    
    const modalEl = document.getElementById('totoModal');
    if (modalEl) {
      if (!_modalInstance) {
        _modalInstance = new bootstrap.Modal(modalEl);
      }
      _modalInstance.show();
    }

    updateTabState();
    await loadData(forceRefresh);
  }

  function updateTabState() {
    document.querySelectorAll('.toto-tab-btn').forEach(btn => {
      if (btn.getAttribute('data-gmid') === _currentGmId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  async function loadData(forceRefresh = false) {
    const container = document.getElementById('totoMatchListContainer');
    if (container && !_totoData) {
      container.innerHTML = `
        <div class="text-center py-5 text-muted">
          <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
          <div>베트맨 공식 실시간 14경기 데이터를 불러오는 중입니다...</div>
        </div>
      `;
    }

    try {
      const resp = await fetch(`/api/v1/toto/betman?gmId=${_currentGmId}${forceRefresh ? '&force=true' : ''}`);
      if (resp.ok) {
        _totoData = await resp.json();
        if (!_selections[_currentGmId]) {
          _selections[_currentGmId] = {};
        }
        render();
      } else {
        showError('데이터를 가져오는 중 오류가 발생했습니다.');
      }
    } catch (e) {
      console.error('Toto fetch error:', e);
      showError('네트워크 통신 중 오류가 발생했습니다.');
    }
  }

  function showError(msg) {
    const container = document.getElementById('totoMatchListContainer');
    if (container) {
      container.innerHTML = `<div class="alert alert-danger m-3">${msg}</div>`;
    }
  }

  function switchGame(gmId) {
    _currentGmId = gmId;
    updateTabState();
    _totoData = null;
    loadData(false);
  }

  function toggleMark(seq, pick) {
    if (!_selections[_currentGmId]) {
      _selections[_currentGmId] = {};
    }
    if (!_selections[_currentGmId][seq]) {
      _selections[_currentGmId][seq] = { W: false, D: false, L: false };
    }

    _selections[_currentGmId][seq][pick] = !_selections[_currentGmId][seq][pick];
    
    // Update button visual
    const btn = document.getElementById(`toto_btn_${_currentGmId}_${seq}_${pick}`);
    if (btn) {
      if (_selections[_currentGmId][seq][pick]) {
        btn.classList.add('selected');
      } else {
        btn.classList.remove('selected');
      }
    }

    updateCalcSummary();
  }

  function applyAiPicks() {
    if (!_totoData || !_totoData.matches) return;
    
    if (!_selections[_currentGmId]) {
      _selections[_currentGmId] = {};
    }

    _totoData.matches.forEach(m => {
      const seq = m.seq;
      const v = m.votes || { win: 0, draw: 0, loss: 0 };
      
      let bestPick = 'W';
      if (v.loss > v.win && v.loss > v.draw) bestPick = 'L';
      else if (v.draw > v.win && v.draw > v.loss) bestPick = 'D';

      _selections[_currentGmId][seq] = {
        W: (bestPick === 'W'),
        D: (bestPick === 'D'),
        L: (bestPick === 'L')
      };
    });

    render();
  }

  function resetMarks() {
    if (_selections[_currentGmId]) {
      _selections[_currentGmId] = {};
    }
    render();
  }

  /**
   * Exact Poisson Binomial Distribution Calculation for 14 Toto Matches
   * Computes P(X=14) [1등], P(X=13) [2등], P(X=12) [3등], P(X=11) [4등]
   */
  function calculateTierProbabilities() {
    if (!_totoData || !_totoData.matches) {
      return { p1: 0, p2: 0, p3: 0, p4: 0, completedMatches: 0, totalCombos: 0, expectedHits: 0 };
    }

    const matches = _totoData.matches;
    const currentMarks = _selections[_currentGmId] || {};
    let totalCombos = 1;
    let completedMatches = 0;
    const pList = [];

    matches.forEach(m => {
      const seq = m.seq;
      const mPicks = currentMarks[seq] || { W: false, D: false, L: false };
      const markedCount = (mPicks.W ? 1 : 0) + (mPicks.D ? 1 : 0) + (mPicks.L ? 1 : 0);

      if (markedCount > 0) {
        totalCombos *= markedCount;
        completedMatches += 1;
      }

      const v = m.votes || { win: 0, draw: 0, loss: 0 };
      const totVotes = (v.win_count || 0) + (v.draw_count || 0) + (v.loss_count || 0);

      let matchProb = 0.0;
      if (totVotes > 0) {
        if (mPicks.W) matchProb += (v.win || 0) / 100.0;
        if (mPicks.D) matchProb += (v.draw || 0) / 100.0;
        if (mPicks.L) matchProb += (v.loss || 0) / 100.0;
      } else {
        // Uniform fallback if votes are unpopulated
        if (mPicks.W) matchProb += 0.3333;
        if (mPicks.D) matchProb += 0.3333;
        if (mPicks.L) matchProb += 0.3333;
      }

      matchProb = Math.min(1.0, Math.max(0.0, matchProb));
      pList.push(matchProb);
    });

    // Dynamic Programming for Poisson Binomial Distribution (N = matches.length <= 14)
    const n = pList.length;
    let dp = new Array(n + 1).fill(0.0);
    dp[0] = 1.0;

    for (let i = 0; i < n; i++) {
      const nextDp = new Array(n + 1).fill(0.0);
      const pi = pList[i];
      const qi = 1.0 - pi;
      for (let k = 0; k <= n; k++) {
        nextDp[k] += dp[k] * qi;
        if (k > 0) {
          nextDp[k] += dp[k - 1] * pi;
        }
      }
      dp = nextDp;
    }

    const expectedHits = pList.reduce((acc, p) => acc + p, 0);

    return {
      p1: n >= 14 ? dp[14] : 0,
      p2: n >= 13 ? dp[13] : 0,
      p3: n >= 12 ? dp[12] : 0,
      p4: n >= 11 ? dp[11] : 0,
      completedMatches,
      totalCombos: (completedMatches === matches.length) ? totalCombos : 0,
      expectedHits
    };
  }

  function formatProb(prob) {
    if (!prob || prob <= 0) return { pct: '0.000%', ratio: '마킹 필요' };
    const pctVal = prob * 100;
    let pctStr = '';
    if (pctVal >= 1) {
      pctStr = pctVal.toFixed(2) + '%';
    } else if (pctVal >= 0.01) {
      pctStr = pctVal.toFixed(3) + '%';
    } else if (pctVal >= 0.0001) {
      pctStr = pctVal.toFixed(4) + '%';
    } else {
      pctStr = pctVal.toFixed(6) + '%';
    }

    const ratioNum = Math.round(1 / prob);
    const ratioStr = ratioNum > 0 ? `1 / ${ratioNum.toLocaleString()}` : '-';
    return { pct: pctStr, ratio: ratioStr };
  }

  function updateCalcSummary() {
    if (!_totoData || !_totoData.matches) return;
    
    const { p1, p2, p3, p4, completedMatches, totalCombos, expectedHits } = calculateTierProbabilities();
    const finalAmount = totalCombos * 1000;

    const p1Fmt = formatProb(p1);
    const p2Fmt = formatProb(p2);
    const p3Fmt = formatProb(p3);
    const p4Fmt = formatProb(p4);

    const firstPrizeText = _totoData.first_prize_text || '0원';
    const secondPrizeText = _totoData.second_prize_text || '0원';
    const thirdPrizeText = _totoData.third_prize_text || '0원';
    const fourthPrizeText = _totoData.fourth_prize_text || '0원';

    const summaryEl = document.getElementById('totoCalcSummary');
    if (summaryEl) {
      summaryEl.innerHTML = `
        <!-- Top Summary Bar -->
        <div class="d-flex flex-wrap justify-content-between align-items-center bg-white p-2 rounded border mb-2 shadow-xs">
          <div class="d-flex align-items-center gap-3">
            <span class="fw-bold text-dark" style="font-size:0.85rem;">선택 경기: <b class="text-primary">${completedMatches}/14</b></span>
            <span class="text-muted">|</span>
            <span class="fw-bold text-dark" style="font-size:0.85rem;">조합수: <b class="text-danger">${totalCombos.toLocaleString()}</b> 조합</span>
            <span class="text-muted">|</span>
            <span class="fw-bold text-dark" style="font-size:0.85rem;">구매금액: <b class="text-success">${finalAmount.toLocaleString()}원</b></span>
          </div>
          <div class="d-flex align-items-center gap-2 text-muted" style="font-size:0.78rem;">
            <span>기대 적중 수: <b class="text-dark font-monospace">${expectedHits.toFixed(1)}개</b> / 14개</span>
            <span>|</span>
            <span>총 당첨확률(1~4등): <b class="text-primary font-monospace">${((p1 + p2 + p3 + p4) * 100).toFixed(2)}%</b></span>
          </div>
        </div>

        <!-- 1st to 4th Tier Winning Probability & Prize Cards Grid -->
        <div class="row g-2 w-100 m-0">
          <!-- 🥇 1등 (14개 전체 적중) -->
          <div class="col-12 col-sm-6 col-md-3 p-1">
            <div class="toto-tier-card tier-1 h-100">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-danger fw-bold" style="font-size:0.75rem;">🥇 1등 (14적중)</span>
                <span class="badge bg-danger-subtle text-danger border border-danger-subtle font-monospace" style="font-size:0.65rem;">총환급 50%+이월</span>
              </div>
              <div class="d-flex align-items-baseline justify-content-between mt-1.5">
                <span class="text-muted small">당첨확률</span>
                <span class="fw-black text-danger font-monospace" style="font-size:1.15rem; letter-spacing:-0.5px;">${p1Fmt.pct}</span>
              </div>
              <div class="d-flex justify-content-between text-muted" style="font-size:0.70rem;">
                <span>확률 비율</span>
                <span class="font-monospace text-dark fw-bold">${p1Fmt.ratio}</span>
              </div>
              <div class="border-top pt-1.5 mt-1.5 d-flex justify-content-between align-items-center">
                <span class="text-secondary small fw-bold">1등 총상금</span>
                <span class="fw-bold text-danger font-monospace" style="font-size:0.85rem;">${firstPrizeText}</span>
              </div>
            </div>
          </div>

          <!-- 🥈 2등 (13개 적중) -->
          <div class="col-12 col-sm-6 col-md-3 p-1">
            <div class="toto-tier-card tier-2 h-100">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-primary fw-bold" style="font-size:0.75rem;">🥈 2등 (13적중)</span>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace" style="font-size:0.65rem;">총발매 10%</span>
              </div>
              <div class="d-flex align-items-baseline justify-content-between mt-1.5">
                <span class="text-muted small">당첨확률</span>
                <span class="fw-black text-primary font-monospace" style="font-size:1.15rem; letter-spacing:-0.5px;">${p2Fmt.pct}</span>
              </div>
              <div class="d-flex justify-content-between text-muted" style="font-size:0.70rem;">
                <span>확률 비율</span>
                <span class="font-monospace text-dark fw-bold">${p2Fmt.ratio}</span>
              </div>
              <div class="border-top pt-1.5 mt-1.5 d-flex justify-content-between align-items-center">
                <span class="text-secondary small fw-bold">2등 총상금</span>
                <span class="fw-bold text-primary font-monospace" style="font-size:0.85rem;">${secondPrizeText}</span>
              </div>
            </div>
          </div>

          <!-- 🥉 3등 (12개 적중) -->
          <div class="col-12 col-sm-6 col-md-3 p-1">
            <div class="toto-tier-card tier-3 h-100">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-success fw-bold" style="font-size:0.75rem;">🥉 3등 (12적중)</span>
                <span class="badge bg-success-subtle text-success border border-success-subtle font-monospace" style="font-size:0.65rem;">총발매 5%</span>
              </div>
              <div class="d-flex align-items-baseline justify-content-between mt-1.5">
                <span class="text-muted small">당첨확률</span>
                <span class="fw-black text-success font-monospace" style="font-size:1.15rem; letter-spacing:-0.5px;">${p3Fmt.pct}</span>
              </div>
              <div class="d-flex justify-content-between text-muted" style="font-size:0.70rem;">
                <span>확률 비율</span>
                <span class="font-monospace text-dark fw-bold">${p3Fmt.ratio}</span>
              </div>
              <div class="border-top pt-1.5 mt-1.5 d-flex justify-content-between align-items-center">
                <span class="text-secondary small fw-bold">3등 총상금</span>
                <span class="fw-bold text-success font-monospace" style="font-size:0.85rem;">${thirdPrizeText}</span>
              </div>
            </div>
          </div>

          <!-- 🏅 4등 (11개 적중) -->
          <div class="col-12 col-sm-6 col-md-3 p-1">
            <div class="toto-tier-card tier-4 h-100">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-secondary fw-bold" style="font-size:0.75rem;">🏅 4등 (11적중)</span>
                <span class="badge bg-secondary-subtle text-secondary border border-secondary-subtle font-monospace" style="font-size:0.65rem;">총발매 10%</span>
              </div>
              <div class="d-flex align-items-baseline justify-content-between mt-1.5">
                <span class="text-muted small">당첨확률</span>
                <span class="fw-black text-secondary font-monospace" style="font-size:1.15rem; letter-spacing:-0.5px;">${p4Fmt.pct}</span>
              </div>
              <div class="d-flex justify-content-between text-muted" style="font-size:0.70rem;">
                <span>확률 비율</span>
                <span class="font-monospace text-dark fw-bold">${p4Fmt.ratio}</span>
              </div>
              <div class="border-top pt-1.5 mt-1.5 d-flex justify-content-between align-items-center">
                <span class="text-secondary small fw-bold">4등 총상금</span>
                <span class="fw-bold text-secondary font-monospace" style="font-size:0.85rem;">${fourthPrizeText}</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }
  }

  function render() {
    if (!_totoData) return;

    // 1. Render Summary Header Badges
    const titleEl = document.getElementById('totoModalTitle');
    const firstPrizeEl = document.getElementById('totoFirstPrizeBadge');
    const totalSellEl = document.getElementById('totoTotalSellBadge');
    const rolloverEl = document.getElementById('totoRolloverBadge');

    const sportIcon = _currentGmId === 'G011' ? '⚽' : (_currentGmId === 'G024' ? '⚾' : '🏀');
    const middleLabel = _currentGmId === 'G024' ? '1' : (_currentGmId === 'G027' ? '5' : '무');

    if (titleEl) {
      titleEl.innerHTML = `
        <span class="me-1">${sportIcon}</span>
        <b>${_totoData.round_name || _totoData.title}</b>
        <span class="badge bg-success ms-2 font-monospace" style="font-size:0.72rem;">실시간 집계중</span>
      `;
    }
    if (firstPrizeEl) firstPrizeEl.innerText = `1등 예상: ${_totoData.first_prize_text || '0원'}`;
    if (totalSellEl) totalSellEl.innerText = `총발매: ${_totoData.total_sell_text || '0원'}`;
    if (rolloverEl) {
      if (_totoData.forward_amount > 0) {
        rolloverEl.style.display = 'inline-block';
        rolloverEl.innerText = `이월: ${_totoData.forward_text}`;
      } else {
        rolloverEl.style.display = 'none';
      }
    }

    // 2. Render 2-Column Split Tables (1~7 on Left, 8~14 on Right) -> All 14 matches visible on 1 screen
    const container = document.getElementById('totoMatchListContainer');
    if (!container) return;

    const currentMarks = _selections[_currentGmId] || {};
    const matches = _totoData.matches || [];
    const col1Matches = matches.slice(0, 7);
    const col2Matches = matches.slice(7, 14);

    function renderColumnTable(colList) {
      const rows = colList.map(m => {
        const seq = m.seq;
        const v = m.votes || { win: 0, draw: 0, loss: 0 };
        const mPicks = currentMarks[seq] || { W: false, D: false, L: false };

        return `
          <tr class="toto-match-row" style="height: 44px;">
            <td class="text-center fw-bold text-secondary font-monospace px-1 py-1" style="width: 28px; font-size:0.78rem; vertical-align: middle;">
              ${seq}
            </td>
            <td class="px-1 py-1" style="width: 82px; vertical-align: middle;">
              <div class="fw-bold text-dark text-truncate-safe" style="font-size:0.72rem;">${m.league || '리그'}</div>
              <div class="text-muted" style="font-size:0.64rem;">${(m.date || '').replace(/^26\./, '')}</div>
            </td>
            <td class="px-1.5 py-1" style="vertical-align: middle;">
              <div class="d-flex justify-content-between align-items-center mb-0.5" style="font-size:0.78rem;">
                <span class="fw-bold text-dark text-truncate-safe" style="max-width: 85px;">${m.home}</span>
                <span class="text-muted fw-bold px-0.5" style="font-size:0.65rem;">VS</span>
                <span class="fw-bold text-dark text-truncate-safe text-end" style="max-width: 85px;">${m.away}</span>
              </div>
              <!-- 실시간 투표율 게이지 바 -->
              <div class="progress" style="height: 9px; border-radius: 3px; font-size: 0.58rem; font-weight: bold;">
                <div class="progress-bar bg-primary" role="progressbar" style="width: ${v.win}%;" title="승 ${v.win}%"></div>
                <div class="progress-bar bg-secondary" role="progressbar" style="width: ${v.draw}%;" title="${middleLabel} ${v.draw}%"></div>
                <div class="progress-bar bg-danger" role="progressbar" style="width: ${v.loss}%;" title="패 ${v.loss}%"></div>
              </div>
              <div class="d-flex justify-content-between text-muted mt-0.5" style="font-size:0.62rem; line-height: 1;">
                <span class="text-primary fw-bold">승 ${v.win}%</span>
                <span class="text-secondary fw-bold">${middleLabel} ${v.draw}%</span>
                <span class="text-danger fw-bold">패 ${v.loss}%</span>
              </div>
            </td>
            <td class="text-center px-1 py-1" style="width: 118px; vertical-align: middle;">
              <div class="btn-group btn-group-sm w-100" role="group">
                <button type="button" 
                  id="toto_btn_${_currentGmId}_${seq}_W"
                  class="btn btn-outline-primary fw-bold toto-pick-btn ${mPicks.W ? 'selected' : ''}" 
                  onclick="TotoModal.toggleMark(${seq}, 'W')" 
                  style="padding: 3px 0; font-size: 0.74rem;">
                  승
                </button>
                <button type="button" 
                  id="toto_btn_${_currentGmId}_${seq}_D"
                  class="btn btn-outline-secondary fw-bold toto-pick-btn ${mPicks.D ? 'selected' : ''}" 
                  onclick="TotoModal.toggleMark(${seq}, 'D')" 
                  style="padding: 3px 0; font-size: 0.74rem;">
                  ${middleLabel}
                </button>
                <button type="button" 
                  id="toto_btn_${_currentGmId}_${seq}_L"
                  class="btn btn-outline-danger fw-bold toto-pick-btn ${mPicks.L ? 'selected' : ''}" 
                  onclick="TotoModal.toggleMark(${seq}, 'L')" 
                  style="padding: 3px 0; font-size: 0.74rem;">
                  패
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      return `
        <table class="table table-hover table-bordered mb-0 align-middle">
          <thead class="table-light">
            <tr class="text-center" style="font-size: 0.72rem;">
              <th style="width: 28px;">No</th>
              <th style="width: 82px;">리그/일시</th>
              <th>대진 & 투표율</th>
              <th style="width: 118px;">마킹</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      `;
    }

    container.innerHTML = `
      <div class="row g-0">
        <div class="col-12 col-lg-6 border-end">
          ${renderColumnTable(col1Matches)}
        </div>
        <div class="col-12 col-lg-6">
          ${renderColumnTable(col2Matches)}
        </div>
      </div>
    `;

    updateCalcSummary();
  }

  // Initial fetch for top navigation badges
  async function syncNavBadges() {
    try {
      const resp = await fetch('/api/v1/toto/live-summary');
      if (resp.ok) {
        const data = await resp.json();
        const games = data.games || {};
        if (games['G011'] && games['G011'].round_no) {
          const b = document.getElementById('navBadgeG011');
          if (b) b.innerText = `${games['G011'].round_no}회`;
        }
        if (games['G024'] && games['G024'].round_no) {
          const b = document.getElementById('navBadgeG024');
          if (b) b.innerText = `${games['G024'].round_no}회`;
        }
        if (games['G027'] && games['G027'].round_no) {
          const b = document.getElementById('navBadgeG027');
          if (b) b.innerText = `${games['G027'].round_no}회`;
        }
      }
    } catch (e) {
      console.debug('Failed to sync nav badges:', e);
    }
  }

  return {
    init,
    open,
    switchGame,
    toggleMark,
    applyAiPicks,
    resetMarks,
    syncNavBadges,
    loadData
  };
})();

// Reusable Drag and Drop Helper for Bootstrap Modals
function makeModalDraggable(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  const dialog = modal.querySelector('.modal-dialog');
  const header = modal.querySelector('.modal-header');
  if (!dialog || !header) return;

  header.style.cursor = 'grab';
  header.style.userSelect = 'none';

  let isDragging = false;
  let startX = 0, startY = 0, initialLeft = 0, initialTop = 0;

  header.addEventListener('mousedown', (e) => {
    if (e.target.closest('button') || e.target.closest('a') || e.target.closest('input')) {
      return;
    }
    isDragging = true;
    header.style.cursor = 'grabbing';

    const rect = dialog.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    initialLeft = rect.left;
    initialTop = rect.top;

    dialog.style.margin = '0';
    dialog.style.position = 'fixed';
    dialog.style.left = `${initialLeft}px`;
    dialog.style.top = `${initialTop}px`;
    dialog.style.transform = 'none';
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    let newLeft = initialLeft + dx;
    let newTop = initialTop + dy;

    const maxLeft = window.innerWidth - 100;
    const maxTop = window.innerHeight - 80;
    newLeft = Math.max(10, Math.min(newLeft, maxLeft));
    newTop = Math.max(10, Math.min(newTop, maxTop));

    dialog.style.left = `${newLeft}px`;
    dialog.style.top = `${newTop}px`;
  });

  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      header.style.cursor = 'grab';
    }
  });

  modal.addEventListener('show.bs.modal', () => {
    dialog.style.position = '';
    dialog.style.left = '';
    dialog.style.top = '';
    dialog.style.margin = '';
    dialog.style.transform = '';
  });
}

window.openTotoModal = (gmId) => TotoModal.open(gmId);
window.makeModalDraggable = makeModalDraggable;
