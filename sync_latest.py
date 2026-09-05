# -*- coding: utf-8 -*-
"""
방금 끝난 야구 경기 원클릭 자동 수집 스크립트 (100% 공식 MLB Stats API 실시간 연동)
- 공식 메이저리그 사이트(statsapi.mlb.com)에서 실시간 경기 결과 즉시 크롤링
- 1회부터 9회까지의 전광판 스코어보드, 타자/투수 전원 박스스코어 자동 생성
- 디스크에 'exports/MLB/구단별/hitters/' 및 'pitchers/' JSON 파일 자동 분류 저장
- 브라우저에 1~9회 전광판 상세 결과 화면(방금끝난경기_전광판_상세결과.html) 즉시 자동 팝업
"""
import os
import sys
import json
import webbrowser
from datetime import datetime

# Windows 콘솔 인코딩 대응 (CP949 에러 방지)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.database import SessionLocal
from app.services.match_service import MatchService
from app.services.folder_export_service import FolderExportService
from app.services.html_report_service import generate_standalone_scoreboard_html

def main():
    print("=" * 70)
    print("⚡ [공식 MLB 실시간 자동 수집] 메이저리그 공식 사이트(statsapi.mlb.com) 연동 시작")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. MLB 최신 공식 경기 크롤링
        print(">> [1단계: MLB 공식 API 크롤링] 공식 메이저리그 경기 일정/결과 실시간 수집 중...")
        res = MatchService.sync_from_official_site(db, league_id="MLB")
        print(f"   ✓ 총 {res['synced_matches_count']}개 공식 MLB 경기 데이터 동기화 완료!")

        matches = MatchService.get_matches(db)
        if not matches:
            print("[오류] 수집된 경기 데이터가 없습니다.")
            return

        # 샌디에이고 vs 양키스 경기 우선 탐색 (종료된 FINISHED 경기 최우선)
        finished_matches = [m for m in matches if m.status == "FINISHED"]
        candidates = finished_matches if finished_matches else matches

        target = next((m for m in candidates if ("샌디에이고" in m.away_team_name or "샌디에이고" in m.home_team_name) and ("양키스" in m.home_team_name or "양키스" in m.away_team_name)), None)
        if not target:
            target = next((m for m in candidates if "샌디에이고" in m.away_team_name or "샌디에이고" in m.home_team_name), candidates[0])

        detail_data = MatchService.get_match_full_detail(db, target.id)
        period = detail_data["details"]["period_scores"]
        summary = period.get("summary", {})
        innings = period.get("innings", {})

        target_day = target.match_date[:10] if target and target.match_date else "2026-09-04"
        # 2. 구단 및 선수별 폴더/파일 자동 생성
        print("\n>> [2단계: 구단/선수별 폴더 파일 생성] 'exports/MLB/' 디렉토리에 자동 분류 저장 중...")
        exp_res = FolderExportService.export_league_to_folder_structure(db, league_id="MLB", start_date=target_day, end_date=target_day)
        print(f"   ✓ {target.away_team_name}, {target.home_team_name} 등 전체 구단 폴더 생성 완료!")
        print(f"   ✓ ZIP 압축 파일 패키징 완료: {exp_res.get('zip_file_path', 'exports/MLB_baseball_export.zip')}")

        # 3. 1~9회 전광판 콘솔 출력
        print("\n" + "=" * 70)
        print(f"⚾ [공식 경기 결과] {target.away_team_name} (원정) vs {target.home_team_name} (홈) - {target.status}")
        print(f"📍 구장: {target.stadium} | 경기일시: {target.match_date} | 공식 ID: {target.official_id}")
        print(f"🏆 최종 스코어: {target.away_team_name} {target.away_score} : {target.home_score} {target.home_team_name}")
        print("-" * 70)
        print("1회부터 9회(연장)까지의 전광판 스코어보드 (Linescore):")

        in_keys = sorted(list(innings.keys()), key=lambda x: int(x))
        in_header = "이닝:   " + "  ".join([f"{k}회" for k in in_keys]) + " |  R   H   E   B"
        print(in_header)

        away_row = f"{target.away_team_name[:4]}: " + "  ".join([f" {innings[k].get('away', '-')} " for k in in_keys])
        away_sum = summary.get("away", {})
        away_row += f" | {away_sum.get('R', target.away_score):2}  {away_sum.get('H', 0):2}  {away_sum.get('E', 0):2}  {away_sum.get('B', 0):2}"
        print(away_row)

        home_row = f"{target.home_team_name[:4]}: " + "  ".join([f" {innings[k].get('home', '-')} " for k in in_keys])
        home_sum = summary.get("home", {})
        home_row += f" | {home_sum.get('R', target.home_score):2}  {home_sum.get('H', 0):2}  {home_sum.get('E', 0):2}  {home_sum.get('B', 0):2}"
        print(home_row)
        print("-" * 70)

        # 주요 득점 이벤트 출력
        events = detail_data.get("events", [])
        if events:
            print("주요 득점 타임라인:")
            for ev in events[:5]:
                print(f"  • [{ev['time_display']}] {ev['team_name']} {ev['player_name']}: {ev.get('description', '')} (스코어: {ev.get('score_after', '')})")
        print("=" * 70)

        # 4. 독립형 전광판 HTML 화면 파일 생성
        report_html_path = os.path.abspath("방금끝난경기_전광판_상세결과.html")
        match_dict = {
            "away_team_name": target.away_team_name,
            "home_team_name": target.home_team_name,
            "away_score": target.away_score,
            "home_score": target.home_score,
            "status": target.status,
            "stadium": target.stadium,
            "match_date": target.match_date,
            "official_id": target.official_id
        }
        generate_standalone_scoreboard_html(match_dict, detail_data["details"], report_html_path)

        # 5. 브라우저에서 전광판 화면 즉시 띄우기
        print(f"\n>> [3단계] 1~9회 전광판 상세 화면을 브라우저에 바로 띄웁니다:")
        print(f"   -> 파일 경로: {report_html_path}")
        try:
            if sys.platform == "win32":
                os.startfile(report_html_path)
                os.system('start http://localhost:8000/')
            else:
                webbrowser.open(f"file://{report_html_path}")
                webbrowser.open("http://localhost:8000/")
        except Exception:
            webbrowser.open(report_html_path)
            webbrowser.open("http://localhost:8000/")

        print("\n🎉 메이저리그 공식 데이터 실시간 수집 및 1~9회 전광판 시각화 완료!")

    finally:
        db.close()

if __name__ == "__main__":
    main()
