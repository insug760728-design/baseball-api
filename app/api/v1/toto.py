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
    if gmId == 'G024':
        return {
            'gmId': 'G024',
            'sport': '야구 승1패',
            'rounds': [
                {'gmTs': active_ts, 'label': f'{str(active_ts)[-2:]}회차 (실시간 발매중🔥)', 'status': 'SaleProgress', 'is_live': True},
                {'gmTs': active_ts - 1, 'label': f'{str(active_ts - 1)[-2:]}회차 (종료결과)', 'status': 'Finished', 'is_live': False},
                {'gmTs': active_ts - 2, 'label': f'{str(active_ts - 2)[-2:]}회차 (종료결과)', 'status': 'Finished', 'is_live': False}
            ]
        }
    elif gmId == 'G011':
        return {
            'gmId': 'G011',
            'sport': '축구 승무패',
            'rounds': [
                {'gmTs': active_ts, 'label': f'{str(active_ts)[-2:]}회차 (실시간 발매중🔥)', 'status': 'SaleProgress', 'is_live': True},
                {'gmTs': active_ts - 1, 'label': f'{str(active_ts - 1)[-2:]}회차 (종료결과)', 'status': 'Finished', 'is_live': False},
                {'gmTs': active_ts - 2, 'label': f'{str(active_ts - 2)[-2:]}회차 (종료결과)', 'status': 'Finished', 'is_live': False}
            ]
        }
    else:
        return {
            'gmId': 'G027',
            'sport': '농구 승5패',
            'rounds': [
                {'gmTs': active_ts, 'label': f'{str(active_ts)[-2:]}회차 (실시간)', 'status': 'SaleProgress', 'is_live': True},
                {'gmTs': active_ts - 1, 'label': f'{str(active_ts - 1)[-2:]}회차 (종료결과)', 'status': 'Finished', 'is_live': False}
            ]
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


@router.post('/sync-proto', summary='베트맨 프로토 배당 및 경기 전체 즉시 동기화')
def sync_proto_matches(db: Session = Depends(get_db)):
    """베트맨 공식 프로토 경기 및 배당률, 실시간 투표율을 DB에 즉시 동기화"""
    return BetmanService.sync_betman_proto_matches(db=db)
