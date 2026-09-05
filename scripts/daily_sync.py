# -*- coding: utf-8 -*-
"""
야구 데이터 일일 자동 수집 & 세이버메트릭스 폴더 갱신 독립 스크립트
컴퓨터가 꺼져 있어도 GitHub Actions(무료)나 외부 크론에서 단독 실행할 수 있는 러너입니다.
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.core.database import SessionLocal, Base, engine
from app.models.models import Match
from app.services.match_service import MatchService
from app.services.folder_export_service import FolderExportService

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    now = datetime.now()
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")

    print(f"==================================================")
    print(f"⚾⚽ [야구 & 유럽축구 5대리그 일일 자동 수집기 가동]")
    print(f"📅 대상 날짜: {yesterday} ~ {today} (현재시각: {now.strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"==================================================")

    leagues = ["KBO", "NPB", "MLB", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1"]
    summary = {}

    for league in leagues:
        print(f"\n▶ [{league}] 공식 사이트 경기 결과 및 선수 박스스코어 동기화 중...")
        try:
            res = MatchService.sync_from_official_site(
                db=db,
                league_id=league,
                start_date=yesterday,
                end_date=today
            )
            synced_count = res.get("synced_matches_count", 0)
            print(f"  ✓ {league} 완료: 총 {synced_count}개 경기 동기화")

            # 구단 및 선수별 폴더 갱신
            print(f"  ▶ [{league}] 구단 및 선수별 세이버메트릭스 폴더/파일 갱신 중...")
            FolderExportService.export_league_to_folder_structure(
                db=db,
                league_id=league,
                start_date=yesterday,
                end_date=today
            )
            print(f"  ✓ {league} 세이버메트릭스 폴더 및 ZIP 압축 완료")

            summary[league] = {"status": "SUCCESS", "synced_matches": synced_count}
        except Exception as e:
            print(f"  ✗ {league} 처리 중 오류 발생: {e}")
            summary[league] = {"status": "ERROR", "error": str(e)}

    db.close()
    print(f"\n==================================================")
    print(f"✨ [전체 리그 일일 자동 수집 및 폴더 갱신 완료]")
    print(f"요약: {summary}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
