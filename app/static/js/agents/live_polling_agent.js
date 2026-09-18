/**
 * LivePollingAgent
 * ================
 * 백그라운드에서 주기적으로 최신 실시간 스코어 및 경기 상태를 안전하게 수집하고,
 * 화면 깜빡임이나 사용자 스크롤 방해 없이 변경된 점수/상태만 부드럽게 갱신(Targeted Micro-Update)하는 전담 에이전트.
 */
class LivePollingAgent {
  constructor() {
    this._intervalId = null;
    this._isPolling = false;
    this.intervalSeconds = 5;
    this._lastSyncTime = null;
    this._listeners = new Set();
  }

  subscribe(callback) {
    if (typeof callback === 'function') {
      this._listeners.add(callback);
    }
    return () => this._listeners.delete(callback);
  }

  _notify(changedIds) {
    this._listeners.forEach(cb => {
      try {
        cb(changedIds);
      } catch (e) {
        console.error('[LivePollingAgent] Listener error:', e);
      }
    });
  }

  start(intervalSeconds = 5) {
    this.intervalSeconds = intervalSeconds;
    if (this._intervalId) clearInterval(this._intervalId);

    this._isPolling = true;
    this._intervalId = setInterval(() => {
      this.poll();
    }, this.intervalSeconds * 1000);

    console.log(`[LivePollingAgent] Started polling with interval: ${this.intervalSeconds}s`);
  }

  stop() {
    if (this._intervalId) {
      clearInterval(this._intervalId);
      this._intervalId = null;
    }
    this._isPolling = false;
    console.log('[LivePollingAgent] Polling stopped.');
  }

  setWebSocketActive(active) {
    this._isWebSocketActive = active;
    if (active) {
      // 웹소켓 정상 연결 시, 불필요한 대역폭 낭비를 막고 60초 완화 폴링 백업으로 전환
      if (this.intervalSeconds !== 60) {
        this.start(60);
      }
      const statusEl = document.getElementById('hourlySyncStatus');
      if (statusEl) {
        statusEl.innerText = '⚡ WebSocket 실시간 초고속 동기화 활성 (지연 0ms)';
      }
    } else {
      // 웹소켓 단절 시 즉각 5초 긴급 HTTP 폴링으로 자가 복구
      if (this.intervalSeconds !== 5) {
        this.start(5);
      }
      const statusEl = document.getElementById('hourlySyncStatus');
      if (statusEl) {
        statusEl.innerText = '실시간 라이브 자동 갱신 (5초 주기 가동 중)';
      }
    }
  }

  /**
   * 1회성 실시간 폴링 실행
   */
  async poll() {
    try {
      const resp = await fetch(`/api/v1/matches?limit=80&order=asc&_t=${Date.now()}`, { cache: 'no-store' });
      if (!resp.ok) return;

      const rawList = await resp.json();
      if (!Array.isArray(rawList)) return;

      this._lastSyncTime = new Date();

      // MatchListAgent에 Diff 병합 위임
      if (window.matchListAgent) {
        const changedIds = window.matchListAgent.mergeMatches(rawList);
        if (changedIds && changedIds.length > 0) {
          console.log(`[LivePollingAgent] Updated ${changedIds.length} changed matches:`, changedIds);
          // 변경된 경기 DOM 부분 갱신 (화면 깜빡임 제로)
          this.applyMicroDomUpdates(changedIds);
          this._notify(changedIds);
        }
      }

      this._updateStatusUI();
    } catch (e) {
      console.warn('[LivePollingAgent] Polling failed:', e);
    }
  }

  /**
   * 화면 전체를 다시 그리지 않고, 점수와 이닝 뱃지만 찾아 부드럽게 글자만 교체
   */
  applyMicroDomUpdates(changedIds) {
    if (!Array.isArray(changedIds) || changedIds.length === 0) return;

    for (const id of changedIds) {
      const m = window.matchListAgent ? window.matchListAgent.getMatchById(id) : null;
      if (!m) continue;

      // 1. 메인 경기바 점수 엘리먼트 갱신
      const homeScoreEl = document.querySelector(`.live-score-home[data-match-id="${id}"]`);
      const awayScoreEl = document.querySelector(`.live-score-away[data-match-id="${id}"]`);
      if (homeScoreEl && homeScoreEl.innerText != m.home_score) {
        homeScoreEl.innerText = m.home_score;
        this._flashElement(homeScoreEl);
      }
      if (awayScoreEl && awayScoreEl.innerText != m.away_score) {
        awayScoreEl.innerText = m.away_score;
        this._flashElement(awayScoreEl);
      }

      // 2. 상태 뱃지 갱신 (LIVE, 종료 등)
      const statusBadgeEl = document.querySelector(`.live-status-badge[data-match-id="${id}"]`);
      if (statusBadgeEl) {
        const isLive = window.matchListAgent ? window.matchListAgent.isMatchTrulyLive(m) : m.status === 'LIVE';
        if (isLive) {
          statusBadgeEl.className = 'badge bg-danger live-status-badge';
          statusBadgeEl.innerText = m.current_period || 'LIVE';
        } else if (m.status === 'FINISHED') {
          statusBadgeEl.className = 'badge bg-secondary live-status-badge';
          statusBadgeEl.innerText = '종료';
        }
      }

      // 3. 상단 스트립 카드 점수 갱신
      const stripScoreEl = document.querySelector(`.strip-score[data-match-id="${id}"]`);
      if (stripScoreEl) {
        stripScoreEl.innerText = `${m.home_score} : ${m.away_score}`;
      }
    }
  }

  _flashElement(el) {
    if (!el) return;
    el.style.transition = 'color 0.3s ease, transform 0.3s ease';
    el.style.color = '#dc2626';
    el.style.transform = 'scale(1.15)';
    setTimeout(() => {
      el.style.color = '';
      el.style.transform = 'scale(1.0)';
    }, 800);
  }

  _updateStatusUI() {
    const statusEl = document.getElementById('hourlySyncStatus');
    if (statusEl) {
      statusEl.innerText = `실시간 라이브 자동 갱신 (${this.intervalSeconds}초 주기 가동 중)`;
    }
  }
}

// 전역 싱글톤 인스턴스 생성
window.livePollingAgent = new LivePollingAgent();
