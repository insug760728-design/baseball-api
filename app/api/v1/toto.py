# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.services.betman_service import BetmanService
from app.core.database import get_db

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


@router.post('/sync-proto', summary='베트맨 프로토 배당 및 경기 전체 즉시 동기화')
def sync_proto_matches(db: Session = Depends(get_db)):
    """베트맨 공식 프로토 경기 및 배당률, 실시간 투표율을 DB에 즉시 동기화"""
    return BetmanService.sync_betman_proto_matches(db=db)
