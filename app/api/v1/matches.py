import time
import json
from typing import List, Optional, Dict, Tuple, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.match_service import MatchService
from app.services.team_split_service import TeamSplitService
from app.services.player_translation import translate_player_name
from app.schemas.schemas import MatchResponse, MatchUpdate, DateRangeSyncRequest, PlayerMatchStatUpdate

router = APIRouter(prefix="/matches", tags=["야구 경기 일정 및 결과"])

_MATCHES_CACHE: Dict[str, Tuple[float, Any]] = {}

def clear_matches_cache():
    _MATCHES_CACHE.clear()

@router.get("", response_model=List[MatchResponse], summary="경기 일정 및 결과 목록 조회 (종목/기간 필터 포함)")
def list_matches(
    response: Response,
    sport_code: Optional[str] = Query(None, description="스포츠 종목 코드 (BASEBALL, SOCCER, BASKETBALL 또는 ALL)"),
    league_name: Optional[str] = Query(None, description="리그명 (MLB, KBO, NPB, EPL, LALIGA, NBA, KLEAGUE, JLEAGUE 등)"),
    status: Optional[str] = Query(None, description="상태 필터 (SCHEDULED, LIVE, FINISHED)"),
    date: Optional[str] = Query(None, description="특정 일자 조회 (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, description="조회 개수 제한"),
    order: Optional[str] = Query("asc", description="정렬 방식 (asc=시간순 오름차순, desc=내림차순)"),
    db: Session = Depends(get_db)
):
    """지정된 종목 및 조건에 맞는 경기 일정/결과 목록을 조회합니다."""
    if date:
        if not start_date:
            start_date = date
        if not end_date:
            end_date = date

    response.headers["Cache-Control"] = "public, max-age=15, s-maxage=30"
    cache_key = f"{sport_code}:{league_name}:{status}:{start_date}:{end_date}:{limit}:{order}"
    now = time.time()
    if cache_key in _MATCHES_CACHE:
        cache_time, cached_res = _MATCHES_CACHE[cache_key]
        if now - cache_time < 30: # 30초 초고속 인메모리 반환 (<0.001s)
            return cached_res

    res = MatchService.get_matches(
        db,
        sport_code=sport_code,
        league_name=league_name,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        order=order
    )
    _MATCHES_CACHE[cache_key] = (now, res)
    return res

@router.post("/sync", summary="기간별 야구 경기 데이터 동기화 수집")
def sync_matches(payload: DateRangeSyncRequest, db: Session = Depends(get_db)):
    """지정된 야구 리그와 기간(start_date ~ end_date)의 경기 및 선수 세부 지표를 공식 사이트에서 수집합니다."""
    s_date = payload.start_date or payload.date
    e_date = payload.end_date or payload.date
    target_league = payload.league_id or "MLB"

    result = MatchService.sync_from_official_site(
        db=db,
        league_id=target_league,
        start_date=s_date,
        end_date=e_date
    )
    clear_matches_cache()
    return result

_MATCH_FULL_CACHE: Dict[int, Tuple[float, Any]] = {}

def clear_matches_cache():
    _MATCHES_CACHE.clear()
    _MATCH_FULL_CACHE.clear()

def clear_match_full_cache(match_id: Optional[int] = None):
    if match_id:
        _MATCH_FULL_CACHE.pop(match_id, None)
    else:
        _MATCH_FULL_CACHE.clear()

@router.get("/{match_id}", summary="경기 상세 정보, 1~9회 스코어보드, 타자/투수 세부 기록 종합 조회")
def get_match_full(match_id: int, response: Response, db: Session = Depends(get_db)):
    now = time.time()
    if match_id in _MATCH_FULL_CACHE:
        cache_time, cached_res = _MATCH_FULL_CACHE[match_id]
        ttl = 10 if (cached_res.get("status") == "LIVE") else (180 if cached_res.get("status") == "SCHEDULED" else 1800)
        if now - cache_time < ttl:
            response.headers["Cache-Control"] = "public, max-age=10, s-maxage=30"
            return cached_res

    data = MatchService.get_match_full_detail(db, match_id)
    if not data:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    
    m = data["match"]
    details_ts = data["details"].get("team_stats") if (data.get("details") and isinstance(data["details"], dict)) else {}
    matchup_analysis = TeamSplitService.get_matchup_analysis(m.home_team_name, m.away_team_name, m.sport_code, match_id=m.id, team_stats=details_ts)
    
    h_starter = None
    a_starter = None
    if isinstance(details_ts, str):
        try:
            details_ts = json.loads(details_ts)
        except Exception:
            details_ts = {}

    if isinstance(details_ts, dict):
        st = details_ts.get("starters", {})
        h_st = st.get("home", {})
        a_st = st.get("away", {})
        if h_st.get("name") and h_st.get("name") not in ["선발 예고", "선발 투수"]:
            h_starter = h_st.get("name")
        if a_st.get("name") and a_st.get("name") not in ["선발 예고", "선발 투수"]:
            a_starter = a_st.get("name")

    res = {
        "id": m.id,
        "official_id": m.official_id,
        "sport_code": m.sport_code,
        "league_name": m.league_name,
        "round_name": m.round_name,
        "match_date": m.match_date,
        "stadium": m.stadium,
        "home_team_name": m.home_team_name,
        "away_team_name": m.away_team_name,
        "home_score": m.home_score,
        "away_score": m.away_score,
        "home_starter_name": translate_player_name(h_starter) if h_starter else None,
        "away_starter_name": translate_player_name(a_starter) if a_starter else None,
        "status": m.status,
        "is_customized": m.is_customized,
        "custom_notes": m.custom_notes,
        "summary": m.custom_notes,
        "details": data["details"],
        "events": data["events"],
        "player_stats": data["player_stats"],
        "matchup_analysis": matchup_analysis
    }
    _MATCH_FULL_CACHE[match_id] = (now, res)
    response.headers["Cache-Control"] = "public, max-age=10, s-maxage=30"
    return res

@router.put("/{match_id}/score", response_model=MatchResponse, summary="경기 스코어 및 상태 직접 수정 (PUT)")
@router.patch("/{match_id}", response_model=MatchResponse, summary="경기 스코어 및 상태 직접 수정 (PATCH)")
def update_match(match_id: int, payload: MatchUpdate, db: Session = Depends(get_db)):
    clear_match_full_cache(match_id)
    updated = MatchService.update_match_score(
        db,
        match_id=match_id,
        home_score=payload.home_score,
        away_score=payload.away_score,
        status=payload.status,
        notes=payload.custom_notes
    )
    if not updated:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    return updated

@router.put("/{match_id}/starters", summary="야구 경기 선발 투수 확정 및 변경 (PUT)")
@router.post("/{match_id}/starters", summary="야구 경기 선발 투수 확정 및 변경 (POST)")
def update_match_starters(match_id: int, payload: dict, db: Session = Depends(get_db)):
    """야구 경기의 홈/원정 선발 투수를 확정(Confirmed)하거나 변경하고 최근 3경기 분석을 갱신합니다."""
    updated = MatchService.update_starters(db, match_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    clear_matches_cache()
    return updated


@router.put("/players/{stat_id}", summary="야구 선수 세부 지표 수정")
def update_player_stat(stat_id: int, payload: PlayerMatchStatUpdate, db: Session = Depends(get_db)):
    updated = MatchService.update_player_stat(
        db=db,
        stat_id=stat_id,
        points=payload.points,
        shots=payload.shots,
        extra_stats=payload.extra_stats,
        override_reason=payload.override_reason
    )
    if not updated:
        raise HTTPException(status_code=404, detail="해당 선수 기록을 찾을 수 없습니다.")
    return {"status": "SUCCESS", "id": updated.id, "is_override": updated.is_override}

@router.get("/latest/timeline", summary="방금 끝난(최신) 경기의 주요 상황 및 타점/홈런 타임라인 JSON")
def get_latest_match_timeline(db: Session = Depends(get_db)):
    matches = MatchService.get_matches(db)
    finished = [m for m in matches if m.status == "FINISHED"]
    target = finished[0] if finished else (matches[0] if matches else None)
    if not target:
        raise HTTPException(status_code=404, detail="경기 데이터가 없습니다.")
    detail = MatchService.get_match_full_detail(db, target.id)
    return {
        "match": {
            "id": target.id,
            "official_id": target.official_id,
            "match_date": target.match_date,
            "home_team": target.home_team_name,
            "away_team": target.away_team_name,
            "score": f"{target.away_score} : {target.home_score}",
            "status": target.status,
            "stadium": target.stadium
        },
        "timeline": detail.get("events", [])
    }

@router.get("/{match_id}/timeline", summary="특정 경기의 주요 상황 및 타점/홈런 타임라인 JSON")
def get_match_timeline(match_id: int, db: Session = Depends(get_db)):
    detail = MatchService.get_match_full_detail(db, match_id)
    if not detail:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    m = detail["match"]
    return {
        "match": {
            "id": m.id,
            "official_id": m.official_id,
            "match_date": m.match_date,
            "home_team": m.home_team_name,
            "away_team": m.away_team_name,
            "score": f"{m.away_score} : {m.home_score}",
            "status": m.status,
            "stadium": m.stadium
        },
        "timeline": detail.get("events", [])
    }

@router.post("/sync-starters", summary="KBO 및 NPB 공식 선발투수 실시간 동기화")
def sync_announced_starters_endpoint(date: Optional[str] = Query(None, description="기준일 (YYYY-MM-DD)"), db: Session = Depends(get_db)):
    """KBO 및 NPB 공식 사이트에서 당일 공식 발표된 선발투수를 실시간 수집하여 DB에 확정 저장하고 캐시를 갱신합니다."""
    res = MatchService.sync_announced_starters(db, target_date=date)
    clear_matches_cache()
    return res