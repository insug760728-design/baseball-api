import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.folder_export_service import FolderExportService
from app.services.match_service import MatchService

router = APIRouter(prefix="/content", tags=["팀 & 선수별 계층형 콘텐츠 및 파일 내보내기"])

class ExportFolderRequest(BaseModel):
    league_id: str = "MLB" # MLB, KBO, EPL, K_LEAGUE, KBL 등
    start_date: str = "2026-09-01"
    end_date: str = "2026-09-07"

@router.post("/export-folders", summary="팀별/선수별 폴더 및 JSON 파일 생성 (ZIP 패키징)")
def export_folders(payload: ExportFolderRequest, db: Session = Depends(get_db)):
    """
    지정된 리그와 기간 동안의 데이터를 [팀 폴더] -> [선수별 JSON / 경기별 JSON] 구조로
    디스크에 실제 파일들로 생성하고 다운로드 가능한 ZIP 파일로 패키징합니다.
    """
    result = FolderExportService.export_league_to_folder_structure(
        db=db,
        league_id=payload.league_id,
        start_date=payload.start_date,
        end_date=payload.end_date
    )
    return {
        "status": "SUCCESS",
        "message": f"'{payload.league_id}' 리그의 팀별/선수별 폴더 및 파일 생성이 완료되었습니다.",
        "download_url": f"/api/v1/content/download-zip/{payload.league_id}",
        "league_id": payload.league_id,
        "period": {"start_date": payload.start_date, "end_date": payload.end_date},
        "total_teams": result.get("manifest", {}).get("total_teams", 30),
        "export_path": result.get("export_root_dir", f"exports/{payload.league_id}"),
        "zip_path": result.get("zip_file_path", ""),
        "export_details": result
    }

@router.get("/download-zip/{league_id}", summary="생성된 팀/선수별 폴더 ZIP 파일 다운로드")
@router.get("/download-export-zip", summary="생성된 팀/선수별 폴더 ZIP 파일 다운로드 (Query Param)")
def download_zip(league_id: str = "MLB"):
    # 세 가지 파일명 패턴 지원 (야구, 축구, 공통)
    zip_path = os.path.abspath(os.path.join("exports", f"{league_id}_baseball_export.zip"))
    if not os.path.exists(zip_path):
        zip_path = os.path.abspath(os.path.join("exports", f"{league_id}_soccer_export.zip"))
    if not os.path.exists(zip_path):
        zip_path = os.path.abspath(os.path.join("exports", f"{league_id}_basketball_export.zip"))
    if not os.path.exists(zip_path):
        zip_path = os.path.abspath(os.path.join("exports", f"{league_id}_contents_export.zip"))
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="생성된 압축 파일을 찾을 수 없습니다. 먼저 /export-folders 생성을 실행하세요.")
    return FileResponse(zip_path, filename=f"{league_id}_content.zip", media_type="application/zip")

@router.get("/{league_id}/teams", summary="특정 리그의 전체 팀 목록 조회")
def get_league_teams(league_id: str, db: Session = Depends(get_db)):
    matches = MatchService.get_matches(db)
    filtered = [m for m in matches if league_id.upper() in (m.official_id or "") or league_id.upper() in m.league_name.upper()]
    teams = set()
    for m in filtered:
        teams.add(m.home_team_name)
        teams.add(m.away_team_name)
    return {
        "league_id": league_id,
        "total_teams": len(teams),
        "teams": sorted(list(teams))
    }