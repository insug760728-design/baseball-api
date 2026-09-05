from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.match_service import MatchService
from app.core.sports_catalog import SPORTS_CATALOG
from app.schemas.schemas import DateRangeSyncRequest

router = APIRouter(prefix="/crawler", tags=["데이터 수집 크롤러"])

@router.get("/catalog", summary="지원하는 스포츠 리그 목록 조회")
def get_catalog():
    """5대리그, 유럽파, 챔스, MLB, 한/일 축구/야구/농구 전체 카탈로그 반환"""
    return SPORTS_CATALOG

@router.post("/sync", summary="공식 사이트 데이터 수집 및 동기화 실행 (기간 범위 지원)")
def trigger_crawl(payload: DateRangeSyncRequest, db: Session = Depends(get_db)):
    """
    지정된 기간 [start_date ~ end_date] 또는 단일 date 동안의 공식 사이트 데이터를 즉시 수집합니다.
    """
    s_date = payload.start_date or payload.date
    e_date = payload.end_date or payload.date

    if payload.league_id == "ALL":
        results = []
        for cat_key, cat_val in SPORTS_CATALOG.items():
            for l in cat_val["leagues"]:
                res = MatchService.sync_from_official_site(
                    db=db,
                    league_id=l["id"],
                    league_name=l["name"],
                    start_date=s_date,
                    end_date=e_date
                )
                results.append(res)
        return {
            "status": "SUCCESS",
            "message": f"모든 스포츠 리그의 {s_date} ~ {e_date} 기간 데이터 일괄 수집이 완료되었습니다.",
            "total_leagues_synced": len(results),
            "period": {"start_date": s_date, "end_date": e_date},
            "details": results
        }
    else:
        result = MatchService.sync_from_official_site(
            db=db,
            league_id=payload.league_id,
            start_date=s_date,
            end_date=e_date
        )
        return {
            "status": "SUCCESS",
            "message": f"{result['league_name']} ({s_date} ~ {e_date}) 데이터 수집이 성공적으로 완료되었습니다.",
            "result": result
        }

@router.get("/live-api-status", summary="전용 유료 API(API-Football/API-Baseball) 연동 상태 조회")
def get_live_api_status():
    from app.services.live_api_sports_service import LiveApiSportsService
    return LiveApiSportsService.get_status_info()

@router.post("/sync-live-apisports", summary="전용 유료 API 실시간 라이브 스코어 동기화 실행")
def sync_live_apisports():
    from app.services.live_api_sports_service import LiveApiSportsService
    fb_res = LiveApiSportsService.sync_live_football()
    bb_res = LiveApiSportsService.sync_live_baseball()
    return {
        "status": "SUCCESS",
        "football": fb_res,
        "baseball": bb_res,
        "message": "전용 API-Sports 실시간 라이브 동기화 완료"
    }