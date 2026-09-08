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
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    details = relationship('MatchDetail', back_populates='match', uselist=False, cascade='all, delete-orphan')
    events = relationship('MatchEvent', back_populates='match', cascade='all, delete-orphan')
    player_stats = relationship('PlayerMatchStat', back_populates='match', cascade='all, delete-orphan')

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
