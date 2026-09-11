from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Player Match Stat Schemas ---
class PlayerMatchStatBase(BaseModel):
    team_name: str
    player_name: str
    back_number: Optional[int] = None
    position: Optional[str] = None
    minutes_played: int = 0
    points: int = 0 # 득점/골/타점/PTS
    assists: int = 0
    shots: int = 0
    extra_stats: Dict[str, Any] = Field(default_factory=dict)

class PlayerMatchStatUpdate(BaseModel):
    points: Optional[int] = None
    assists: Optional[int] = None
    shots: Optional[int] = None
    minutes_played: Optional[int] = None
    extra_stats: Optional[Dict[str, Any]] = None
    override_reason: Optional[str] = '관리자 앱 데이터 수동 조정'

class PlayerMatchStatResponse(PlayerMatchStatBase):
    id: int
    match_id: int
    is_override: bool = False
    override_reason: Optional[str] = None
    original_backup: Optional[str] = None

    class Config:
        from_attributes = True

# --- Match Event Schemas ---
class MatchEventBase(BaseModel):
    time_display: str
    event_type: str
    team_name: str
    player_name: str
    assist_player_name: Optional[str] = None
    score_after: Optional[str] = None
    description: Optional[str] = None

class MatchEventResponse(MatchEventBase):
    id: int
    match_id: int
    is_customized: bool = False

    class Config:
        from_attributes = True

# --- Match Detail Schemas ---
class MatchDetailBase(BaseModel):
    period_scores: Dict[str, Any] = Field(default_factory=dict)
    team_stats: Dict[str, Any] = Field(default_factory=dict)
    source_url: Optional[str] = None

class MatchDetailResponse(MatchDetailBase):
    id: int
    match_id: int
    is_customized: bool = False

    class Config:
        from_attributes = True

# --- Match Schemas ---
class MatchBase(BaseModel):
    official_id: Optional[str] = None
    sport_code: str = 'BASEBALL'
    league_name: str
    season: str = '2026'
    round_name: Optional[str] = None
    match_date: str
    stadium: Optional[str] = None
    home_team_name: str
    away_team_name: str
    home_score: int = 0
    away_score: int = 0
    status: str = 'SCHEDULED'

class MatchUpdate(BaseModel):
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None
    custom_notes: Optional[str] = None
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    stadium: Optional[str] = None

class MatchResponse(MatchBase):
    id: int
    is_customized: bool = False
    custom_notes: Optional[str] = None
    summary: Optional[str] = None
    prediction: Optional[Dict[str, Any]] = None
    odds: Optional[Dict[str, Any]] = None
    ou_line: Optional[str] = None
    ou_pick: Optional[str] = None
    home_starter_name: Optional[str] = None
    away_starter_name: Optional[str] = None
    starters_confirmed: Optional[bool] = False
    current_inning: Optional[str] = None
    inning_text: Optional[str] = None
    outs: Optional[int] = None
    balls: Optional[int] = None
    strikes: Optional[int] = None
    all_odds: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- 기간 범위 수집 요청 DTO ---
class DateRangeSyncRequest(BaseModel):
    league_id: str = "MLB" # MLB, KBO, NPB, ALL 등
    start_date: Optional[str] = None # 시작일 (YYYY-MM-DD)
    end_date: Optional[str] = None   # 종료일 (YYYY-MM-DD)
    date: Optional[str] = None       # 단일일자 (하위호환)