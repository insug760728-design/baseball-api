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
