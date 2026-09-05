from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.match_service import MatchService
from app.schemas.schemas import MatchResponse, MatchUpdate, DateRangeSyncRequest, PlayerMatchStatUpdate

router = APIRouter(prefix="/matches", tags=["야구 경기 일정 및 결과"])

@router.get("", response_model=List[MatchResponse], summary="야구 경기 일정 및 결과 목록 조회 (기간 필터 포함)")
def list_matches(
    sport_code: Optional[str] = Query("BASEBALL", description="스포츠 종목 코드 (BASEBALL)"),
    league_name: Optional[str] = Query(None, description="야구 리그명 (MLB, KBO, NPB)"),
    status: Optional[str] = Query(None, description="상태 필터 (SCHEDULED, LIVE, FINISHED)"),
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """지정된 기간 및 조건에 맞는 야구 경기 일정/결과 목록을 조회합니다."""
    return MatchService.get_matches(
        db,
        sport_code=sport_code or "BASEBALL",
        league_name=league_name,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

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
    return result

@router.get("/{match_id}", summary="경기 상세 정보, 1~9회 스코어보드, 타자/투수 세부 기록 종합 조회")
def get_match_full(match_id: int, db: Session = Depends(get_db)):
    data = MatchService.get_match_full_detail(db, match_id)
    if not data:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")
    
    m = data["match"]
    return {
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
        "status": m.status,
        "is_customized": m.is_customized,
        "custom_notes": m.custom_notes,
        "details": data["details"],
        "events": data["events"],
        "player_stats": data["player_stats"]
    }

@router.put("/{match_id}/score", response_model=MatchResponse, summary="경기 스코어 및 상태 직접 수정 (PUT)")
@router.patch("/{match_id}", response_model=MatchResponse, summary="경기 스코어 및 상태 직접 수정 (PATCH)")
def update_match(match_id: int, payload: MatchUpdate, db: Session = Depends(get_db)):
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