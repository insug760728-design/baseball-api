# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query, Depends
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.services.betman_service import BetmanService
from app.core.database import get_db

class OddsHistoryCreateRequest(BaseModel):
    home_odds: float = Field(..., description="홈 배당률")
    draw_odds: Optional[float] = Field(None, description="무승부 배당률 (선택)")
    away_odds: float = Field(..., description="원정 배당률")
    captured_at: Optional[str] = Field(None, description="변동 시간 (KST 기준, 예: 2026-10-06 14:30)")
    win_vote_pct: Optional[str] = Field(None, description="승 투표율 (선택)")
    draw_vote_pct: Optional[str] = Field(None, description="무 투표율 (선택)")
    loss_vote_pct: Optional[str] = Field(None, description="패 투표율 (선택)")

router = APIRouter(prefix='/toto', tags=['토토 14경기 인터랙티브 & 베트맨 실시간 연동'])

@router.get('/betman', summary='베트맨(Betman) 14경기 공식 데이터 실시간 자동 수집 & 조회')
def get_betman_toto_round(
    gmId: str = Query('G011', description='게임 ID: G011(축구 승무패), G024(야구 승1패), G027(농구 승5패)'),
    gmTs: Optional[int] = Query(None, description='회차 번호 (미입력 시 최신 활성 회차 자동 조회)'),
    force: bool = Query(False, description='강제 최신 수집 여부')
):
    target_ts = gmTs if gmTs else BetmanService.get_active_round_ts(gmId)
    data = BetmanService.get_round_data(gm_id=gmId, gm_ts=target_ts, force_refresh=force)
    return data


@router.get('/live-summary', summary='베트맨 실시간 승무패/승1패 당첨금액 및 발매현황 요약')
def get_live_toto_summary(force: bool = Query(False, description='강제 최신 수집 여부')):
    return BetmanService.get_live_toto_summary(force_refresh=force)


@router.get('/rounds', summary='토토 회차 목록')
def get_available_rounds(gmId: str = Query('G011')):
    active_ts = BetmanService.get_active_round_ts(gmId)
    sport_name = '축구 승무패' if gmId == 'G011' else ('야구 승1패' if gmId == 'G024' else '농구 승5패')
    
    rounds = []
    # 최신 발매중 회차 + 최근 7개 회차 (총 8개 회차)
    for i in range(8):
        ts = active_ts - i
        if ts <= 0:
            continue
        r_num = ts % 1000
        is_live = (i == 0)
        rounds.append({
            'gmTs': ts,
            'roundNo': r_num,
            'label': f'{r_num}회',
            'fullLabel': f'{sport_name} {r_num}회차' + (' (실시간 발매중🔥)' if is_live else ' (종료결과)'),
            'status': 'SaleProgress' if is_live else 'Finished',
            'tag': '🔥발매중' if is_live else '종료',
            'is_live': is_live
        })
    rounds.reverse()
    return {
        'gmId': gmId,
        'sport': sport_name,
        'active_ts': active_ts,
        'rounds': rounds
    }


@router.get('/match-odds/{match_id}', summary='특정 경기 베트맨 전체 배당 조합 조회 (승패/핸디캡/U&O/SUM/전반 등)')
def get_match_full_odds(match_id: int):
    """
    경기 ID로 해당 경기의 베트맨 전체 배당 조합 반환.
    - 야구: 승패, 승1패, 핸디캡, 언더오버, SUM(홀짝), 전반 승무패, 전반 핸디캡, 전반 언더오버
    - 축구: 승무패, 핸디캡, 언더오버, SUM(홀짝)
    - 농구: 승패, 핸디캡, 언더오버, SUM(홀짝)
    """
    return BetmanService.get_match_full_odds(match_id=match_id)


@router.get('/odds-history/{match_id}', summary='특정 경기의 실제 베트맨 배당 변경 시계열 이력 조회')
def get_match_odds_history(match_id: int, db: Session = Depends(get_db)):
    """특정 경기의 실제 배당 변경 시계열 데이터 반환 (차트 실데이터 바인딩용)"""
    return BetmanService.get_match_odds_history(match_id=match_id, db=db)


@router.post('/odds-history/{match_id}', summary='특정 경기의 배당 변동 이력 수동 등록/입력')
def add_match_odds_history(match_id: int, req: OddsHistoryCreateRequest, db: Session = Depends(get_db)):
    """
    특정 경기에 실시간 배당 변동(날짜/시간, 승/무/패 배당률)을 수동으로 입력/등록합니다.
    """
    return BetmanService.add_odds_history_record(
        match_id=match_id,
        home_odds=req.home_odds,
        draw_odds=req.draw_odds,
        away_odds=req.away_odds,
        captured_at_str=req.captured_at,
        win_vote_pct=req.win_vote_pct,
        draw_vote_pct=req.draw_vote_pct,
        loss_vote_pct=req.loss_vote_pct,
        db=db
    )


@router.delete('/odds-history/record/{history_id}', summary='배당 변경 이력 항목 삭제')
def delete_odds_history_record(history_id: int, db: Session = Depends(get_db)):
    """
    등록된 배당 변경 이력 레코드를 삭제합니다.
    """
    return BetmanService.delete_odds_history_record(history_id=history_id, db=db)


@router.post('/sync-proto', summary='베트맨 프로토 배당 및 경기 전체 즉시 동기화')
def sync_proto_matches(db: Session = Depends(get_db)):
    """베트맨 공식 프로토 경기 및 배당률, 실시간 투표율을 DB에 즉시 동기화"""
    return BetmanService.sync_betman_proto_matches(db=db)

