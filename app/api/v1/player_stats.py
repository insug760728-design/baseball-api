import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.match_service import MatchService
from app.schemas.schemas import PlayerMatchStatUpdate, PlayerMatchStatResponse
from app.models.models import PlayerMatchStat

router = APIRouter(prefix="/players", tags=["선수 상세 수치 관리"])

@router.patch("/stats/{stat_id}", response_model=PlayerMatchStatResponse, summary="선수 세부 수치(골, 어시스트, 슈팅 등) 수정")
def update_stat(stat_id: int, payload: PlayerMatchStatUpdate, db: Session = Depends(get_db)):
    """
    공식 사이트에서 수집된 선수의 특정 경기 스탯(골/득점, 어시스트, 슈팅수, 추가 지표 등)을
    원하는 값으로 수정/오버라이드합니다. 앱으로 전송될 때 이 수정된 값이 우선 반영됩니다.
    """
    updated = MatchService.update_player_stat(
        db=db,
        stat_id=stat_id,
        points=payload.points,
        assists=payload.assists,
        shots=payload.shots,
        minutes_played=payload.minutes_played,
        extra_stats=payload.extra_stats,
        override_reason=payload.override_reason
    )
    if not updated:
        raise HTTPException(status_code=404, detail="해당 선수 기록을 찾을 수 없습니다.")

    extra = {}
    try:
        extra = json.loads(updated.extra_stats or "{}")
    except:
        extra = {}

    return PlayerMatchStatResponse(
        id=updated.id,
        match_id=updated.match_id,
        team_name=updated.team_name,
        player_name=updated.player_name,
        back_number=updated.back_number,
        position=updated.position,
        minutes_played=updated.minutes_played,
        points=updated.points,
        assists=updated.assists,
        shots=updated.shots,
        extra_stats=extra,
        is_override=updated.is_override,
        override_reason=updated.override_reason,
        original_backup=updated.original_backup
    )