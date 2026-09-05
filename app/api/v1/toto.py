# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query
from typing import Optional
from app.services.betman_service import BetmanService

router = APIRouter(prefix='/toto', tags=['토토 14경기 인터랙티브 & 베트맨 실시간 연동'])

@router.get('/betman', summary='베트맨(Betman) 14경기 공식 데이터 실시간 자동 수집 & 조회')
def get_betman_toto_round(
    gmId: str = Query('G024', description='게임 ID: G024(야구 승1패), G011(축구 승무패), G027(농구 승5패)'),
    gmTs: Optional[int] = Query(None, description='회차 번호 (예: 260066, 260065)')
):
    target_ts = gmTs if gmTs else (260066 if gmId == 'G024' else None)
    data = BetmanService.get_round_data(gm_id=gmId, gm_ts=target_ts)
    return data

@router.get('/rounds', summary='토토 회차 목록')
def get_available_rounds(gmId: str = Query('G024')):
    if gmId == 'G024':
        return {
            'gmId': 'G024',
            'sport': '야구 승1패',
            'rounds': [
                {'gmTs': 260066, 'label': '66회차 (발매중 · 6억 이월🔥)', 'status': 'SaleProgress', 'is_live': True},
                {'gmTs': 260065, 'label': '65회차 (종료결과 · 3.9억)', 'status': 'Finished', 'is_live': False},
                {'gmTs': 260064, 'label': '64회차 (이전회차 · 2.7억)', 'status': 'Finished', 'is_live': False}
            ]
        }
    elif gmId == 'G011':
        return {
            'gmId': 'G011',
            'sport': '축구 승무패',
            'rounds': [
                {'gmTs': 260049, 'label': '49회차 (2,974만 원)', 'status': 'Upcoming', 'is_live': True}
            ]
        }
    else:
        return {
            'gmId': 'G027',
            'sport': '농구 승5패',
            'rounds': [
                {'gmTs': 260027, 'label': '27회차 (5,232만 원)', 'status': 'Finished', 'is_live': False}
            ]
        }
