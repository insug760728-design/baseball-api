# -*- coding: utf-8 -*-
"""
KOVO V-리그 배구 분석 API
- /api/v1/volleyball/h2h        : 상대전적
- /api/v1/volleyball/recent     : 최근결과
- /api/v1/volleyball/analytics  : 팀 분석지표
- /api/v1/volleyball/standings  : 순위표
- /api/v1/volleyball/teams      : 팀 목록
"""

import sys
import os
import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

# volleyball_server 모듈 경로 추가
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_vb_dir = os.path.join(_root, "volleyball_server")
if _vb_dir not in sys.path:
    sys.path.insert(0, _vb_dir)

try:
    import kovo_service as kovo
    _KOVO_AVAILABLE = True
except ImportError:
    _KOVO_AVAILABLE = False
    logging.warning("[volleyball] kovo_service 모듈을 찾을 수 없습니다. volleyball_server/kovo_service.py 확인 필요")

router = APIRouter(prefix="/volleyball", tags=["배구 V-리그 KOVO"])

def _unavailable():
    return JSONResponse({"error": "KOVO 서비스 초기화 실패 — volleyball_server/kovo_service.py 확인 필요"}, status_code=503)


@router.get("/teams")
def get_teams():
    """남자/여자 팀 목록"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    return JSONResponse(kovo.get_all_teams())


@router.get("/h2h")
def get_h2h(
    team1: str = Query(..., description="팀1 코드 (예: 1001=대한항공)"),
    team2: str = Query(..., description="팀2 코드 (예: 1005=현대캐피탈)"),
    season: str = Query("021", description="시즌 코드 (021=2024-25, 022=2025-26)")
):
    """두 팀 상대전적 + 분석지표"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    data = kovo.get_h2h_with_analytics(team1, team2, season)
    return JSONResponse(data)


@router.get("/recent")
def get_recent(
    team: str = Query(..., description="팀 코드"),
    season: str = Query("021"),
    limit: int = Query(10, ge=1, le=30)
):
    """팀 최근 경기 결과"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    data = kovo.get_recent_results(team, season, limit)
    return JSONResponse(data)


@router.get("/analytics")
def get_analytics(season: str = Query("021")):
    """전 팀 분석지표 (공격효율/서브/블락/리시브/디그)"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    data = kovo.get_team_analytics(season)
    return JSONResponse(data)


@router.get("/standings")
def get_standings(season: str = Query("021")):
    """시즌 순위표"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    data = kovo.get_season_standings(season)
    return JSONResponse(data)


@router.post("/cache/clear")
def clear_cache():
    """캐시 초기화"""
    if not _KOVO_AVAILABLE:
        return _unavailable()
    kovo.clear_cache()
    return {"status": "ok", "message": "KOVO 캐시 초기화 완료"}
