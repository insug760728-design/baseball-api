# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.database import SessionLocal
from app.models.models import Match
from app.services.live_api_sports_service import LiveApiSportsService

router = APIRouter(prefix="/live", tags=["Real-time Live Sync (API-Sports & RapidAPI)"])

class ApiKeyPayload(BaseModel):
    key: str
    provider: Optional[str] = "api_sports"

@router.get("/status", summary="실시간 API-Sports / RapidAPI 연동 상태 조회")
def get_live_status():
    status_info = LiveApiSportsService.get_status_info()

    # Query active live matches in DB
    db = SessionLocal()
    try:
        live_matches = db.query(Match).filter(Match.status == "LIVE").all()
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_finished = db.query(Match).filter(
            Match.status == "FINISHED",
            Match.match_date.like(f"{today_str}%")
        ).all()

        status_info["active_live_count"] = len(live_matches)
        status_info["today_finished_count"] = len(today_finished)
        status_info["live_matches"] = [
            {
                "id": m.id,
                "sport_code": m.sport_code,
                "league_name": m.league_name,
                "home": m.home_team_name,
                "away": m.away_team_name,
                "score": f"{m.home_score} : {m.away_score}",
                "status": m.status,
                "time": m.match_date
            }
            for m in live_matches
        ]
    finally:
        db.close()

    return status_info

@router.post("/set-key", summary="사용자 API-Sports 또는 RapidAPI Key 등록 및 즉시 실시간 동기화")
def set_live_api_key(payload: ApiKeyPayload):
    if not payload.key or len(payload.key.strip()) < 5:
        raise HTTPException(status_code=400, detail="유효한 API 키를 입력해주세요.")

    result = LiveApiSportsService.set_api_key(key=payload.key, provider=payload.provider or "api_sports")
    return result

@router.post("/sync-now", summary="실시간 축구 및 야구 경기 결과 즉시 강제 동기화")
def force_sync_live():
    res = LiveApiSportsService.sync_all()
    return {
        "status": "SUCCESS",
        "message": "실시간 데이터 동기화 완료",
        "details": res,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
