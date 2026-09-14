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
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const kst = new Date(utc + (9 * 3600000));
    
    // 다음 KST 자정까지 남은 밀리초 계산
    const nextMidnight = new Date(kst);
    nextMidnight.setHours(24, 0, 1, 0);
    const msUntilMidnight = nextMidnight.getTime() - kst.getTime();

    setTimeout(() => {
      console.log('[FilterAgent] Midnight KST reached. Auto refreshing date tabs...');
      this._notify();
      this._setupMidnightTimer(); // 다음 날 자정 타이머 재설정
    }, Math.max(1000, msUntilMidnight));
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
