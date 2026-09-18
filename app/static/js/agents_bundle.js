// --- match_list_agent.js ---
/**
 * MatchListAgent
 * ==============
 * 전 종목(야구, 축구, 농구, 배구 등)의 전체 경기 데이터를 단일 원천(Single Source of Truth)으로 수집,
 * 규격 정규화(Normalization), 중복 제거 및 캐싱하고 다른 에이전트들에게 데이터 변경을 전파하는 전담 에이전트.
 */
class MatchListAgent {
  constructor() {
    this._matches = [];
    this._listeners = new Set();
    this._isLoading = false;
    this._initialLoaded = false;
  }

  /**
   * 데이터 변경 리스너 등록 (Pub/Sub)
   */
  subscribe(callback) {
    if (typeof callback === 'function') {
      this._listeners.add(callback);
    }
    return () => this._listeners.delete(callback);
  }

  _notify(changedMatchIds = null) {
    const data = this.getAllMatches();
    this._listeners.forEach(cb => {
      try {
        cb(data, changedMatchIds);
      } catch (e) {
        console.error('[MatchListAgent] Listener error:', e);
      }
    });
  }

  /**
   * 전체 활성 경기 목록 반환 (불변 복사본)
   */
  getAllMatches() {
    return [...this._matches];
  }

  /**
   * ID로 특정 경기 조회
   */
  getMatchById(id) {
    if (!id) return null;
    return this._matches.find(m => m && (m.id == id || m.official_id == id)) || null;
  }

  /**
   * 경기가 실제로 진행 중(LIVE)인지 엄격 판정
   */
  isMatchTrulyLive(m) {
    if (!m) return false;
    if (m.status !== 'LIVE' && m.status !== 'IN_PLAY' && m.status !== '1H' && m.status !== '2H' && m.status !== 'HT') return false;
    if (m.match_date) {
      try {
        const mTime = new Date(m.match_date.replace(' ', 'T')).getTime();
        const nowTs = Date.now();
        // 5시간 이상 경과된 LIVE 상태는 종료된 것으로 안전 판정
        if ((nowTs - mTime) / (1000 * 60 * 60) > 5) return false;
      } catch (e) {}
    }
    return true;
  }

  /**
   * 백엔드 및 다양한 소스의 경기 객체를 단 하나의 표준 규격으로 일관되게 정규화
   */
  normalizeMatch(raw) {
    if (!raw) return null;
    
    // 공식 풀네임 및 약칭 정리
    const homeTeam = (raw.home_team_name || raw.homeTeam || raw.homeName || raw.home || '').trim();
    const awayTeam = (raw.away_team_name || raw.awayTeam || raw.awayName || raw.away || '').trim();
    const matchDate = raw.match_date || raw.gameDateStr || raw.gameDate || raw.date || '';
    const sportCode = (raw.sport_code || raw.sport || (raw.league_name && raw.league_name.includes('야구') ? 'BASEBALL' : 'SOCCER')).toUpperCase();
    const leagueName = raw.league_name || raw.leagueName || raw.league || sportCode;
    const status = (raw.status || raw.state || 'SCHEDULED').toUpperCase();

    return {
      id: raw.id || raw.match_id || raw.official_id,
      official_id: raw.official_id || `M_${raw.id}`,
      sport_code: sportCode,
      league_name: leagueName,
      match_date: matchDate,
      stadium: raw.stadium || '',
      home_team_name: homeTeam,
      away_team_name: awayTeam,
      home_score: typeof raw.home_score === 'number' ? raw.home_score : (parseInt(raw.homeScore || 0, 10) || 0),
      away_score: typeof raw.away_score === 'number' ? raw.away_score : (parseInt(raw.awayScore || 0, 10) || 0),
      status: status,
      current_period: raw.current_period || raw.current_inning || raw.period || '',
      prediction: raw.prediction || null,
      odds: raw.odds || raw.betman_main_odds || null,
      details: raw.details || null,
      round_name: raw.round_name || ''
    };
  }

  /**
   * 백엔드 API로부터 전체 공식 경기 목록 안전 로드
   */
  async loadMatches(force = false) {
    if (this._isLoading && !force) return this._matches;
    this._isLoading = true;

    try {
      const resp = await fetch('/api/v1/matches?limit=100&order=asc', { cache: 'no-store' });
      if (resp.ok) {
        const rawList = await resp.json();
        if (Array.isArray(rawList)) {
          this.setMatches(rawList);
          this._initialLoaded = true;
          return this._matches;
        }
      }
    } catch (e) {
      console.warn('[MatchListAgent] Failed to load matches:', e);
      this._loadLocalCache();
    } finally {
      this._isLoading = false;
    }
    return this._matches;
  }

  /**
   * 새로운 경기 데이터 목록으로 교체 및 정규화
   */
  setMatches(newList) {
    if (!Array.isArray(newList)) return;

    const seenIds = new Set();
    const seenKeys = new Set();
    const cleanList = [];

    for (const raw of newList) {
      const m = this.normalizeMatch(raw);
      if (!m || !m.home_team_name || !m.away_team_name) continue;
      // 가짜 스케줄 프리픽스 배제
      if (m.official_id && m.official_id.startsWith('SCHED_')) continue;

      const dPart = (m.match_date || '').slice(0, 10);
      const key = `${m.sport_code}_${m.home_team_name}_${m.away_team_name}_${dPart}`;

      if (m.id && seenIds.has(m.id)) continue;
      if (seenKeys.has(key)) continue;

      if (m.id) seenIds.add(m.id);
      seenKeys.add(key);
      cleanList.push(m);
    }

    this._matches = cleanList;
    this._saveLocalCache();
    this._notify();
  }

  /**
   * 실시간 라이브 갱신 시 기존 목록과 안전하게 Diff 병합
   */
  mergeMatches(freshList) {
    if (!Array.isArray(freshList) || freshList.length === 0) return [];

    const map = new Map(this._matches.map(m => [m.id, m]));
    const changedMatchIds = [];

    for (const raw of freshList) {
      const fresh = this.normalizeMatch(raw);
      if (!fresh || !fresh.id) continue;

      const existing = map.get(fresh.id);
      if (!existing) {
        map.set(fresh.id, fresh);
        changedMatchIds.push(fresh.id);
      } else {
        if (existing.home_score !== fresh.home_score || 
            existing.away_score !== fresh.away_score || 
            existing.status !== fresh.status || 
            existing.current_period !== fresh.current_period) {
          map.set(fresh.id, { ...existing, ...fresh });
          changedMatchIds.push(fresh.id);
        }
      }
    }

    if (changedMatchIds.length > 0) {
      this._matches = Array.from(map.values());
      this._saveLocalCache();
      this._notify(changedMatchIds);
    }

    return changedMatchIds;
  }

  _saveLocalCache() {
    try {
      localStorage.setItem('tokeon_matches_cache_v99', JSON.stringify(this._matches));
    } catch (e) {}
  }

  _loadLocalCache() {
    try {
      const cached = localStorage.getItem('tokeon_matches_cache_v99');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) {
          this._matches = parsed.map(m => this.normalizeMatch(m)).filter(Boolean);
          this._notify();
        }
      }
    } catch (e) {}
  }
}

// 전역 싱글톤 인스턴스 생성
window.matchListAgent = new MatchListAgent();


// --- filter_agent.js ---
/**
 * FilterAgent
 * ===========
 * 스포츠 종목(축구/야구/농구/배구 등), 리그(KBO/MLB/EPL 등), 날짜 탭(진행/예정, 지난경기, 오늘, 내일),
 * 및 AI 승부예측 신뢰도 필터링과 탭별 뱃지 카운트 계산을 단독으로 책임지는 전담 에이전트.
 * (KST 한국 표준시 엄격 고정 및 자정 자동 갱신 탑재)
 */
class FilterAgent {
  constructor() {
    this.sport = 'ALL';
    this.league = 'ALL';
    this.dateTab = 'ACTIVE';
    this.confidence = 'ALL';
    this._listeners = new Set();

    // 자정(00:00 KST) 자동 갱신 타이머 가동
    this._setupMidnightTimer();
  }

  subscribe(callback) {
    if (typeof callback === 'function') {
      this._listeners.add(callback);
    }
    return () => this._listeners.delete(callback);
  }

  _notify() {
    const state = this.getState();
    this._listeners.forEach(cb => {
      try {
        cb(state);
      } catch (e) {
        console.error('[FilterAgent] Listener error:', e);
      }
    });
  }

  getState() {
    return {
      sport: this.sport,
      league: this.league,
      dateTab: this.dateTab,
      confidence: this.confidence
    };
  }

  setSport(sport) {
    this.sport = sport || 'ALL';
    this.league = 'ALL'; // 종목 변경 시 리그 초기화
    this._notify();
  }

  setLeague(league) {
    this.league = league || 'ALL';
    this._notify();
  }

  setDateTab(tab) {
    this.dateTab = tab || 'ACTIVE';
    this._notify();
  }

  setConfidence(conf) {
    this.confidence = conf || 'ALL';
    this._notify();
  }

  /**
   * KST 날짜 문자열 헬퍼 (YYYY-MM-DD)
   */
  getKSTDateString(d = new Date()) {
    const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
    const kst = new Date(utc + (9 * 3600000));
    const year = kst.getFullYear();
    const month = String(kst.getMonth() + 1).padStart(2, '0');
    const day = String(kst.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  getKSTDateTimeString(d = new Date()) {
    const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
    const kst = new Date(utc + (9 * 3600000));
    const year = kst.getFullYear();
    const month = String(kst.getMonth() + 1).padStart(2, '0');
    const day = String(kst.getDate()).padStart(2, '0');
    const hours = String(kst.getHours()).padStart(2, '0');
    const minutes = String(kst.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  }

  /**
   * 자정(00:00 KST) 자동 갱신 설정
   */
  _setupMidnightTimer() {
    const now = new Date();
    const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 5, 0);
    const msUntilMidnight = Math.max(60000, tomorrow.getTime() - now.getTime());

    setTimeout(() => {
      try {
        console.log('[FilterAgent] Midnight reached. Auto refreshing date tabs...');
        this._notify();
      } catch (e) {}
      this._setupMidnightTimer();
    }, msUntilMidnight);
  }

  /**
   * MatchListAgent의 데이터를 받아 현재 필터 조건에 맞게 정제 및 정렬된 경기 목록 반환
   */
  getFilteredMatches() {
    const rawMatches = window.matchListAgent ? window.matchListAgent.getAllMatches() : [];
    if (!rawMatches || rawMatches.length === 0) return [];

    const now = new Date();
    const d0Str = this.getKSTDateString(now);
    const d1Str = this.getKSTDateString(new Date(now.getTime() + 86400000));

    let list = [...rawMatches];

    // 1. 스포츠 종목 필터
    if (this.sport === 'SOCCER') {
      list = list.filter(m => m.sport_code === 'SOCCER');
    } else if (this.sport === 'BASEBALL') {
      list = list.filter(m => m.sport_code === 'BASEBALL');
    } else if (this.sport === 'BASKETBALL') {
      list = list.filter(m => m.sport_code === 'BASKETBALL' || (m.league_name && (m.league_name.includes('농구') || m.league_name.includes('NBA') || m.league_name.includes('KBL'))));
    } else if (this.sport === 'HOCKEY') {
      list = list.filter(m => m.sport_code === 'HOCKEY' || (m.league_name && (m.league_name.includes('하키') || m.league_name.includes('NHL'))));
    } else if (this.sport === 'VOLLEYBALL') {
      list = list.filter(m => m.sport_code === 'VOLLEYBALL' || (m.league_name && (m.league_name.includes('배구') || m.league_name.includes('V-리그'))));
    }

    // 2. 개별 리그 필터
    if (this.league !== 'ALL') {
      const l = this.league.toUpperCase();
      if (l === 'KBO') list = list.filter(m => m.league_name && m.league_name.includes('KBO'));
      else if (l === 'MLB') list = list.filter(m => m.league_name && m.league_name.includes('MLB'));
      else if (l === 'NPB') list = list.filter(m => m.league_name && (m.league_name.includes('NPB') || m.league_name.includes('일본 프로야구')));
      else if (l === 'EPL') list = list.filter(m => m.league_name && m.league_name.includes('EPL'));
      else if (l === 'LALIGA') list = list.filter(m => m.league_name && (m.league_name.includes('라리가') || m.league_name.includes('La Liga')));
      else if (l === 'BUNDESLIGA') list = list.filter(m => m.league_name && (m.league_name.includes('분데스') || m.league_name.includes('Bundesliga')));
      else if (l === 'SERIE_A') list = list.filter(m => m.league_name && (m.league_name.includes('세리에') || m.league_name.includes('Serie A')));
      else if (l === 'MLS') list = list.filter(m => m.league_name && (m.league_name.includes('MLS') || m.league_name.includes('메이저리그 사커') || m.league_name.includes('미국축구')));
      else if (l === 'EREDIVISIE') list = list.filter(m => m.league_name && (m.league_name.includes('네덜란드') || m.league_name.includes('에레디비시') || m.league_name.includes('Eredivisie')));
      else if (l === 'CHAMPIONSHIP') list = list.filter(m => m.league_name && (m.league_name.includes('챔피언십') || m.league_name.includes('Championship')));
      else if (l === 'UCL') list = list.filter(m => m.league_name && (m.league_name.includes('UCL') || m.league_name.includes('챔피언스')));
      else if (l === 'KBL') list = list.filter(m => m.league_name && (m.league_name.includes('KBL') || m.league_name.includes('한국 프로농구')));
      else if (l === 'NBA') list = list.filter(m => m.league_name && (m.league_name.includes('NBA') || m.league_name.includes('미국 프로농구')));
    }

    // 3. AI 승부예측 신뢰도 필터
    if (this.confidence === '80') {
      list = list.filter(m => m.prediction && m.prediction.confidence >= 80);
    } else if (this.confidence === '70') {
      list = list.filter(m => m.prediction && m.prediction.confidence >= 70);
    } else if (this.confidence === '50') {
      list = list.filter(m => m.prediction && m.prediction.confidence >= 50);
    }

    // 4. 날짜 탭 필터 (ACTIVE / FINISHED / D0 / D1 / ALL)
    const isLiveFn = m => window.matchListAgent ? window.matchListAgent.isMatchTrulyLive(m) : m.status === 'LIVE';

    if (this.dateTab === 'FINISHED' || this.dateTab === 'PAST') {
      list = list.filter(m => {
        if (m.status === 'FINISHED' || m.status === 'CANCELLED' || m.status === 'POSTPONED') return true;
        if (m.status === 'LIVE' && !isLiveFn(m)) return true;
        return false;
      });
      list.sort((a, b) => (b.match_date || '').localeCompare(a.match_date || ''));
    } else if (this.dateTab === 'D0') {
      list = list.filter(m => m.match_date && m.match_date.startsWith(d0Str));
      list.sort((a, b) => (a.match_date || '').localeCompare(b.match_date || ''));
    } else if (this.dateTab === 'D1') {
      list = list.filter(m => m.match_date && m.match_date.startsWith(d1Str));
      list.sort((a, b) => (a.match_date || '').localeCompare(b.match_date || ''));
    } else {
      // ACTIVE (진행/예정 기본 탭)
      const liveMatches = list.filter(isLiveFn);
      const upcomingMatches = list.filter(m => {
        if (m.status === 'CANCELLED' || m.status === 'POSTPONED' || m.status === 'FINISHED') return false;
        if (isLiveFn(m)) return false;
        return true;
      });

      liveMatches.sort((a, b) => (a.match_date || '').localeCompare(b.match_date || ''));
      upcomingMatches.sort((a, b) => (a.match_date || '').localeCompare(b.match_date || ''));
      list = [...liveMatches, ...upcomingMatches];
    }

    return list;
  }

  /**
   * 탭 뱃지 카운트 계산 (진행/예정 건수, 지난경기 건수)
   */
  getTabCounts() {
    const rawMatches = window.matchListAgent ? window.matchListAgent.getAllMatches() : [];
    if (!rawMatches || rawMatches.length === 0) {
      return { activeCount: 0, finishedCount: 0, liveCount: 0 };
    }

    let baseList = [...rawMatches];
    if (this.sport === 'SOCCER') {
      baseList = baseList.filter(m => m.sport_code === 'SOCCER');
    } else if (this.sport === 'BASEBALL') {
      baseList = baseList.filter(m => m.sport_code === 'BASEBALL');
    } else if (this.sport === 'BASKETBALL') {
      baseList = baseList.filter(m => m.sport_code === 'BASKETBALL' || (m.league_name && (m.league_name.includes('농구') || m.league_name.includes('NBA') || m.league_name.includes('KBL'))));
    } else if (this.sport === 'HOCKEY') {
      baseList = baseList.filter(m => m.sport_code === 'HOCKEY' || (m.league_name && (m.league_name.includes('하키') || m.league_name.includes('NHL'))));
    } else if (this.sport === 'VOLLEYBALL') {
      baseList = baseList.filter(m => m.sport_code === 'VOLLEYBALL' || (m.league_name && (m.league_name.includes('배구') || m.league_name.includes('V-리그'))));
    }

    const isLiveFn = m => window.matchListAgent ? window.matchListAgent.isMatchTrulyLive(m) : m.status === 'LIVE';

    let activeCount = 0;
    let finishedCount = 0;
    let liveCount = 0;

    for (const m of baseList) {
      if (isLiveFn(m)) {
        liveCount++;
        activeCount++;
      } else if (m.status === 'FINISHED' || m.status === 'CANCELLED' || m.status === 'POSTPONED') {
        finishedCount++;
      } else {
        // SCHEDULED
        activeCount++;
      }
    }

    return { activeCount, finishedCount, liveCount, total: baseList.length };
  }
}

// 전역 싱글톤 인스턴스 생성
window.filterAgent = new FilterAgent();


// --- detail_modal_agent.js ---
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


// --- live_polling_agent.js ---
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
    this.intervalSeconds = 3;
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

  start(intervalSeconds = 3) {
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
      // 웹소켓 단절 시 즉각 3초 긴급 HTTP 폴링으로 자가 복구
      if (this.intervalSeconds !== 3) {
        this.start(3);
      }
      const statusEl = document.getElementById('hourlySyncStatus');
      if (statusEl) {
        statusEl.innerText = '실시간 라이브 자동 갱신 (3초 주기 가동 중)';
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


// --- toto_odds_agent.js ---
/**
 * TotoOddsAgent
 * =============
 * 스포츠토토 및 베트맨 프로토(G101), 축구 승무패(G011), 야구 승1패(G024), 농구 승5패(G027)의
 * 회차 정보, 투표율, 배당률 계산 및 AI 승부예측 분석을 전담하는 독립 에이전트.
 */
class TotoOddsAgent {
  constructor() {
    this._summaryData = null;
    this._roundsCache = new Map();
    this.currentGmId = 'G101'; // Default: 프로토 승부식
    this.currentGmTs = null;
    this._isLoading = false;
  }

  /**
   * 토토/프로토 진행 회차 및 발매 요약 정보 로드
   */
  async loadSummary() {
    try {
      const resp = await fetch('/api/v1/toto/live-summary', { cache: 'no-store' });
      if (resp.ok) {
        this._summaryData = await resp.json();
        return this._summaryData;
      }
    } catch (e) {
      console.warn('[TotoOddsAgent] Failed to load toto summary:', e);
    }
    return null;
  }

  /**
   * 특정 회차 상세 데이터 로드
   */
  async loadRound(gmId = 'G101', gmTs = null) {
    const key = `${gmId}_${gmTs || 'latest'}`;
    if (this._roundsCache.has(key)) {
      return this._roundsCache.get(key);
    }

    try {
      const url = gmTs ? `/api/v1/toto/round?gm_id=${gmId}&gm_ts=${gmTs}` : `/api/v1/toto/round?gm_id=${gmId}`;
      const resp = await fetch(url, { cache: 'no-store' });
      if (resp.ok) {
        const data = await resp.json();
        this._roundsCache.set(key, data);
        this.currentGmId = gmId;
        this.currentGmTs = data.gmTs;
        return data;
      }
    } catch (e) {
      console.warn(`[TotoOddsAgent] Failed to load round ${key}:`, e);
    }
    return null;
  }

  /**
   * 투표율과 배당률을 바탕으로 한 AI 승부예측 추천
   */
  calculateAiRecommendation(item) {
    if (!item) return { pick: '승', conf: 50 };

    const votes = item.votes || {};
    const winV = parseFloat(votes.win || 0);
    const drawV = parseFloat(votes.draw || 0);
    const lossV = parseFloat(votes.loss || 0);

    let pick = '승';
    let conf = winV;

    if (drawV > winV && drawV > lossV) {
      pick = '무';
      conf = drawV;
    } else if (lossV > winV && lossV > drawV) {
      pick = '패';
      conf = lossV;
    }

    return {
      pick: pick,
      conf: Math.max(50, Math.round(conf))
    };
  }

  /**
   * 베트맨 금액 한글 포맷 변환 (예: 2억 8,400만 원)
   */
  formatMoney(amount) {
    const num = parseInt(amount, 10) || 0;
    if (num <= 0) return '0원';
    const eok = Math.floor(num / 100000000);
    const man = Math.floor((num % 100000000) / 10000);
    if (eok > 0 && man > 0) return `${eok}억 ${man.toLocaleString()}만 원`;
    if (eok > 0) return `${eok}억 원`;
    return `${man.toLocaleString()}만 원`;
  }
}

// 전역 싱글톤 인스턴스 생성
window.totoOddsAgent = new TotoOddsAgent();

