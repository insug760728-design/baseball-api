# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/matches/{match_id}/rolling")
def get_match_rolling_stats(
    match_id: int,
    windows: str = Query("3,5,7,10", description="경기수 단위 (쉼표 구분)"),
    days: str = Query("3,5,7,10", description="날짜 단위 (쉼표 구분)"),
    db: Session = Depends(get_db)
):
    """
    특정 경기에 출전한 전 선수(타자/투수)의 최근 3, 5, 7, 10 단위(경기수/일수) 롤링 및 세이버메트릭스 지표 조회
    """
    try:
        w_list = [int(x.strip()) for x in windows.split(",") if x.strip().isdigit()]
    except Exception:
        w_list = [3, 5, 7, 10]

    try:
        d_list = [int(x.strip()) for x in days.split(",") if x.strip().isdigit()]
    except Exception:
        d_list = [3, 5, 7, 10]

    roster_stats = AnalyticsService.get_match_roster_rolling_stats(db, match_id, windows=w_list, days_windows=d_list)
    if not roster_stats:
        raise HTTPException(status_code=404, detail="경기 또는 선수 데이터를 찾을 수 없습니다.")
    return {
        "status": "success",
        "match_id": match_id,
        "player_count": len(roster_stats),
        "data": roster_stats
    }

@router.get("/players/{player_name}/rolling")
def get_player_rolling_stats(
    player_name: str,
    player_type: str = Query("hitter", description="'hitter' 또는 'pitcher'"),
    team_name: Optional[str] = Query(None, description="구단명 필터"),
    windows: str = Query("3,5,7,10", description="경기수 단위 (쉼표 구분)"),
    days: str = Query("3,5,7,10", description="날짜 단위 (쉼표 구분)"),
    db: Session = Depends(get_db)
):
    """
    특정 선수의 3, 5, 7, 10 단위 롤링 및 세이버메트릭스(wOBA, FIP, BABIP, ISO 등) 분석 수치 반환
    """
    try:
        w_list = [int(x.strip()) for x in windows.split(",") if x.strip().isdigit()]
    except Exception:
        w_list = [3, 5, 7, 10]

    try:
        d_list = [int(x.strip()) for x in days.split(",") if x.strip().isdigit()]
    except Exception:
        d_list = [3, 5, 7, 10]

    if player_type.lower() == "pitcher":
        stats = AnalyticsService.calculate_pitcher_rolling_stats(db, player_name, team_name=team_name, windows=w_list, days_windows=d_list)
    else:
        stats = AnalyticsService.calculate_hitter_rolling_stats(db, player_name, team_name=team_name, windows=w_list, days_windows=d_list)

    if not stats or stats.get("total_games_recorded", 0) == 0:
        raise HTTPException(status_code=404, detail=f"'{player_name}' 선수의 경기 기록을 찾을 수 없습니다.")

    return {
        "status": "success",
        "data": stats
    }
