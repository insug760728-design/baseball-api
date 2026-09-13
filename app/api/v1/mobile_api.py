from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.services.match_service import MatchService
from app.models import models
import time

router = APIRouter(prefix="/app", tags=["📱 모바일 앱 전용 API"])

@router.get("/config", summary="모바일 앱 초기 설정 및 버전 정보")
def get_app_config():
    """
    모바일 앱 실행 시 필요한 최소 설정 및 공지, 최신 버전 정보 반환
    """
    return {
        "status": "success",
        "app_name": "TOKEON Sports Live",
        "min_version": "1.0.0",
        "latest_version": "1.0.0",
        "force_update": False,
        "features": {
            "live_scoreboard": True,
            "toto_calculator": True,
            "push_notification": True,
            "community": True
        },
        "supported_leagues": [
            {"code": "EPL", "name": "프리미어리그", "sport": "SOCCER", "icon": "⚽"},
            {"code": "LALIGA", "name": "라리가", "sport": "SOCCER", "icon": "🇪🇸"},
            {"code": "MLB", "name": "메이저리그", "sport": "BASEBALL", "icon": "⚾"},
            {"code": "KBO", "name": "KBO 리그", "sport": "BASEBALL", "icon": "🇰🇷"},
            {"code": "KBL", "name": "KBL 농구", "sport": "BASKETBALL", "icon": "🏀"}
        ],
        "server_time": time.time()
    }

@router.get("/matches/today", summary="모바일 첫 화면용 오늘의 경기 요약 목록")
def get_mobile_today_matches(
    sport: Optional[str] = Query(None, description="종목 코드 (SOCCER, BASEBALL, BASKETBALL 등)"),
    status: Optional[str] = Query(None, description="경기 상태 (LIVE, SCHEDULED, FINISHED)"),
    db: Session = Depends(get_db)
):
    """
    모바일 앱 메인 카드 뷰에 최적화된 경량 경기 목록
    """
    matches = MatchService.get_matches(db, sport_code=sport, status=status, limit=30, order="asc")
    if not matches:
        matches = MatchService.get_matches(db, sport_code=sport, limit=30, order="desc")
    
    result = []
    for m in matches:
        # 배당률 간소화
        odds = {}
        if m.details and isinstance(m.details, dict):
            raw_odds = m.details.get("odds", {})
            if isinstance(raw_odds, dict):
                odds = {
                    "home_win": raw_odds.get("home_win") or raw_odds.get("win", 0),
                    "draw": raw_odds.get("draw", 0),
                    "away_win": raw_odds.get("away_win") or raw_odds.get("lose", 0)
                }

        result.append({
            "id": m.id,
            "official_id": m.official_id,
            "sport_code": m.sport_code,
            "league_name": m.league_name,
            "round_name": m.round_name,
            "match_date": m.match_date,
            "stadium": m.stadium,
            "home_team_name": m.home_team_name,
            "away_team_name": m.away_team_name,
            "home_score": m.home_score if m.status in ("LIVE", "FINISHED") else None,
            "away_score": m.away_score if m.status in ("LIVE", "FINISHED") else None,
            "home_starter": m.home_starter_name,
            "away_starter": m.away_starter_name,
            "status": m.status,
            "odds": odds
        })
        
    return {
        "count": len(result),
        "matches": result
    }

@router.get("/matches/{match_id}/scoreboard", summary="모바일 전광판 & 상세 분석 데이터")
def get_mobile_match_scoreboard(match_id: int, db: Session = Depends(get_db)):
    """
    모바일 화면에 띄울 전광판, 이닝/세부 스코어보드, 주요 이벤트 타임라인
    """
    data = MatchService.get_match_full_detail(db, match_id)
    if not data:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    
    m = data["match"]
    details = data.get("details", {})
    events = data.get("events", [])
    player_stats = data.get("player_stats", [])

    return {
        "match_id": m.id,
        "sport_code": m.sport_code,
        "league_name": m.league_name,
        "match_date": m.match_date,
        "status": m.status,
        "teams": {
            "home": {
                "name": m.home_team_name,
                "score": m.home_score,
                "starter": m.home_starter_name
            },
            "away": {
                "name": m.away_team_name,
                "score": m.away_score,
                "starter": m.away_starter_name
            }
        },
        "period_scores": details.get("period_scores", {}),
        "team_stats": details.get("team_stats", {}),
        "events": events[:15],
        "top_players": player_stats[:10]
    }
