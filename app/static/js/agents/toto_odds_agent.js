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
