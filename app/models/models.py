from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, index=True)
    official_id = Column(String(100), unique=True, index=True, nullable=True) # 공식 사이트 경기 ID
    sport_code = Column(String(50), index=True, default='BASEBALL') # 야구 전문 (BASEBALL)
    league_name = Column(String(100), index=True) # 예: '미국 메이저리그 (MLB)', 'KBO'
    season = Column(String(20), default='2026')
    round_name = Column(String(50), nullable=True) # 예: '12라운드', '정규시즌'
    match_date = Column(String(50), index=True) # 예: '2026-09-05 19:30'
    stadium = Column(String(100), nullable=True)
    
    home_team_name = Column(String(100), index=True)
    away_team_name = Column(String(100), index=True)
    
    # 경기 결과 스코어
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    
    # 경기 상태: SCHEDULED(예정), LIVE(진행중), FINISHED(종료), POSTPONED(연기)
    status = Column(String(30), default='SCHEDULED', index=True)
    
    # 관리자 커스텀 수정 여부
    is_customized = Column(Boolean, default=False)
    custom_notes = Column(Text, nullable=True)

    @property
    def summary(self):
        return self.custom_notes

    @summary.setter
    def summary(self, value):
        self.custom_notes = value

    @property
    def home_starter_name(self):
        if hasattr(self, '_home_starter_name'):
            return self._home_starter_name
        if self.details and hasattr(self.details, 'team_stats'):
            try:
                stats = json.loads(self.details.team_stats) if isinstance(self.details.team_stats, str) else self.details.team_stats
                if isinstance(stats, dict):
                    if "starters" in stats and isinstance(stats["starters"], dict):
                        h_st = stats["starters"].get("home", {})
                        if isinstance(h_st, dict) and h_st.get("name"):
                            return h_st.get("name")
                        elif isinstance(h_st, str):
                            return h_st
                    return stats.get("home_starter") or stats.get("home_starter_name")
            except Exception:
                pass
        return None

    @home_starter_name.setter
    def home_starter_name(self, value):
        self._home_starter_name = value

    @property
    def away_starter_name(self):
        if hasattr(self, '_away_starter_name'):
            return self._away_starter_name
        if self.details and hasattr(self.details, 'team_stats'):
            try:
                stats = json.loads(self.details.team_stats) if isinstance(self.details.team_stats, str) else self.details.team_stats
                if isinstance(stats, dict):
                    if "starters" in stats and isinstance(stats["starters"], dict):
                        a_st = stats["starters"].get("away", {})
                        if isinstance(a_st, dict) and a_st.get("name"):
                            return a_st.get("name")
                        elif isinstance(a_st, str):
                            return a_st
                    return stats.get("away_starter") or stats.get("away_starter_name")
            except Exception:
                pass
        return None

    @away_starter_name.setter
    def away_starter_name(self, value):
        self._away_starter_name = value

    @property
    def audit_status(self):
        if self.details and hasattr(self.details, 'team_stats'):
            try:
                stats = json.loads(self.details.team_stats) if isinstance(self.details.team_stats, str) else self.details.team_stats
                if isinstance(stats, dict) and "audit" in stats:
                    return stats["audit"]
            except Exception:
                pass
        return {"verdict": "PASS", "score": 100}

    def _get_scoreboard_data(self):
        if self.details and hasattr(self.details, 'team_stats') and self.details.team_stats:
            try:
                ts = json.loads(self.details.team_stats) if isinstance(self.details.team_stats, str) else self.details.team_stats
                if isinstance(ts, dict):
                    sb = ts.get("scoreboard")
                    if isinstance(sb, dict):
                        return sb
                    return ts
            except Exception:
                pass
        return {}

    @property
    def current_inning(self):
        if hasattr(self, '_current_inning') and self._current_inning:
            return self._current_inning
        if self.details:
            if hasattr(self.details, 'period_scores') and self.details.period_scores:
                try:
                    ps = json.loads(self.details.period_scores) if isinstance(self.details.period_scores, str) else self.details.period_scores
                    if isinstance(ps, dict) and ps.get("current_inning"):
                        return ps["current_inning"]
                except Exception:
                    pass
            sb = self._get_scoreboard_data()
            if sb.get("current_inning"):
                return sb["current_inning"]
        return None

    @current_inning.setter
    def current_inning(self, val):
        self._current_inning = val

    @property
    def inning_text(self):
        return self.current_inning

    @inning_text.setter
    def inning_text(self, val):
        self._current_inning = val

    @property
    def outs(self):
        if hasattr(self, '_outs') and self._outs is not None:
            return self._outs
        return self._get_scoreboard_data().get("outs")

    @outs.setter
    def outs(self, val):
        self._outs = val

    @property
    def balls(self):
        if hasattr(self, '_balls') and self._balls is not None:
            return self._balls
        return self._get_scoreboard_data().get("balls")

    @balls.setter
    def balls(self, val):
        self._balls = val

    @property
    def strikes(self):
        if hasattr(self, '_strikes') and self._strikes is not None:
            return self._strikes
        return self._get_scoreboard_data().get("strikes")

    @strikes.setter
    def strikes(self, val):
        self._strikes = val

    @property
    def base1(self):
        if hasattr(self, '_base1') and self._base1 is not None:
            return self._base1
        sb = self._get_scoreboard_data()
        return bool(sb.get("base1") or sb.get("runner_1b") or sb.get("runner_on_1b") or sb.get("first_base") or sb.get("first") or sb.get("base_1"))

    @base1.setter
    def base1(self, val):
        self._base1 = val

    @property
    def base2(self):
        if hasattr(self, '_base2') and self._base2 is not None:
            return self._base2
        sb = self._get_scoreboard_data()
        return bool(sb.get("base2") or sb.get("runner_2b") or sb.get("runner_on_2b") or sb.get("second_base") or sb.get("second") or sb.get("base_2"))

    @base2.setter
    def base2(self, val):
        self._base2 = val

    @property
    def base3(self):
        if hasattr(self, '_base3') and self._base3 is not None:
            return self._base3
        sb = self._get_scoreboard_data()
        return bool(sb.get("base3") or sb.get("runner_3b") or sb.get("runner_on_3b") or sb.get("third_base") or sb.get("third") or sb.get("base_3"))

    @base3.setter
    def base3(self, val):
        self._base3 = val

    @property
    def base_1(self):
        return self.base1

    @base_1.setter
    def base_1(self, val):
        self.base1 = val

    @property
    def base_2(self):
        return self.base2

    @base_2.setter
    def base_2(self, val):
        self.base2 = val

    @property
    def base_3(self):
        return self.base3

    @base_3.setter
    def base_3(self, val):
        self.base3 = val

    @property
    def pitcher(self):
        if hasattr(self, '_pitcher') and self._pitcher:
            return self._pitcher
        sb = self._get_scoreboard_data()
        return sb.get("pitcher") or self.home_starter_name

    @pitcher.setter
    def pitcher(self, val):
        self._pitcher = val

    @property
    def batter(self):
        if hasattr(self, '_batter') and self._batter:
            return self._batter
        sb = self._get_scoreboard_data()
        return sb.get("batter")

    @batter.setter
    def batter(self, val):
        self._batter = val

    @property
    def team_stats(self):
        if hasattr(self, '_team_stats') and self._team_stats:
            return self._team_stats
        if self.details and hasattr(self.details, 'team_stats') and self.details.team_stats:
            try:
                return json.loads(self.details.team_stats) if isinstance(self.details.team_stats, str) else self.details.team_stats
            except Exception:
                pass
        return {}

    @team_stats.setter
    def team_stats(self, val):
        self._team_stats = val

    @property
    def period_scores(self):
        if hasattr(self, '_period_scores') and self._period_scores:
            return self._period_scores
        if self.details and hasattr(self.details, 'period_scores') and self.details.period_scores:
            try:
                return json.loads(self.details.period_scores) if isinstance(self.details.period_scores, str) else self.details.period_scores
            except Exception:
                pass
        return {}

    @period_scores.setter
    def period_scores(self, val):
        self._period_scores = val

    @property
    def linescore(self):
        if hasattr(self, '_linescore') and self._linescore:
            return self._linescore
        ts = self.team_stats or {}
        if isinstance(ts, dict) and ts.get("linescore"):
            return ts["linescore"]
        sb = self._get_scoreboard_data()
        if isinstance(sb, dict) and sb.get("linescore"):
            return sb["linescore"]
        ps = self.period_scores or {}
        if isinstance(ps, dict):
            inns = ps.get("innings", ps)
            if isinstance(inns, dict) and len(inns) > 0:
                return {
                    "home": [inns.get(str(i), {}).get("home", "-") if isinstance(inns.get(str(i)), dict) else "-" for i in range(1, 10)],
                    "away": [inns.get(str(i), {}).get("away", "-") if isinstance(inns.get(str(i)), dict) else "-" for i in range(1, 10)]
                }
        return None

    @linescore.setter
    def linescore(self, val):
        self._linescore = val
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    details = relationship('MatchDetail', back_populates='match', uselist=False, cascade='all, delete-orphan')
    events = relationship('MatchEvent', back_populates='match', cascade='all, delete-orphan')
    player_stats = relationship('PlayerMatchStat', back_populates='match', cascade='all, delete-orphan')
    odds_history = relationship('BetmanOddsHistory', back_populates='match', cascade='all, delete-orphan')

class MatchDetail(Base):
    __tablename__ = 'match_details'

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), unique=True, nullable=False)
    
    # 기간별 스코어 (축구 전반/후반, 야구 1~9회, 농구 1~4쿼터 등) JSON 형태
    period_scores = Column(Text, default='{}')
    
    # 팀 통계 (점유율, 슈팅수, 유효슈팅, 코너킥, 파울, 안타, 홈런 등) JSON 형태
    team_stats = Column(Text, default='{}')
    
    source_url = Column(String(500), nullable=True)
    is_customized = Column(Boolean, default=False)

    match = relationship('Match', back_populates='details')

class MatchEvent(Base):
    __tablename__ = 'match_events'

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    
    time_display = Column(String(50)) # '23\'', '3회초', 'Q2 04:12'
    event_type = Column(String(50))   # GOAL, ASSIST, YELLOW_CARD, RED_CARD, HOMERUN, HIT 등
    team_name = Column(String(100))
    player_name = Column(String(100))
    assist_player_name = Column(String(100), nullable=True)
    score_after = Column(String(50), nullable=True) # 이벤트 후 스코어 '1-0', '2-1'
    description = Column(Text, nullable=True)
    
    is_customized = Column(Boolean, default=False)

    match = relationship('Match', back_populates='events')

class PlayerMatchStat(Base):
    __tablename__ = 'player_match_stats'

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    
    team_name = Column(String(100), index=True)
    player_name = Column(String(100), index=True)
    back_number = Column(Integer, nullable=True)
    position = Column(String(50), nullable=True) # FW, MF, DF, GK, 투수, 타자 등
    
    minutes_played = Column(Integer, default=0) # 출전 시간
    points = Column(Integer, default=0)         # 득점 / 골 / 득점기여
    assists = Column(Integer, default=0)        # 도움 / 어시스트
    shots = Column(Integer, default=0)          # 슈팅수 / 타수 / 안타수
    
    # 기타 상세 스탯 (유효슈팅, 패스성공률, 옐로카드, 리바운드, 삼진 등)
    extra_stats = Column(Text, default='{}')
    
    # 사용자가 앱에 전송하기 위해 수정한 지표인지 여부
    is_override = Column(Boolean, default=False)
    override_reason = Column(String(255), nullable=True)
    original_backup = Column(Text, nullable=True) # 공식 사이트 원본 값 백업(JSON)

    match = relationship('Match', back_populates='player_stats')
 
class BetmanOddsHistory(Base):
    __tablename__ = 'betman_odds_history'

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey('matches.id', ondelete='CASCADE'), nullable=True, index=True)
    seq = Column(Integer, nullable=True, index=True)
    home_odds = Column(String(20), nullable=True)
    draw_odds = Column(String(20), nullable=True)
    away_odds = Column(String(20), nullable=True)
    win_vote_pct = Column(String(20), nullable=True)
    draw_vote_pct = Column(String(20), nullable=True)
    loss_vote_pct = Column(String(20), nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_changed = Column(Boolean, default=False, index=True)

    match = relationship('Match', back_populates='odds_history')
