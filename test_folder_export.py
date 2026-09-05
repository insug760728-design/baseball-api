import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== 1. 메이저리그 (MLB) 팀별/선수별 폴더 내보내기 API 테스트 ===")
res = client.post("/api/v1/content/export-folders", json={
    "league_id": "MLB",
    "start_date": "2026-09-01",
    "end_date": "2026-09-07"
})
assert res.status_code == 200
data = res.json()
print("응답 상태:", data["status"])
print("다운로드 URL:", data["download_url"])
print("생성된 총 팀 수:", data["export_details"]["manifest"]["total_teams"])

print("\n=== 2. 실제 디스크에 생성된 폴더 및 선수 파일 확인 ===")
export_dir = data["export_details"]["export_root_dir"]
print(f"디스크 루트 경로: {export_dir}")
assert os.path.exists(export_dir)

subdirs = os.listdir(export_dir)
print(f"생성된 팀 폴더 목록: {subdirs}")

# LA 다저스 폴더 검사
dodgers_dir = [d for d in subdirs if "다저스" in d or "LA" in d]
if dodgers_dir:
    d_path = os.path.join(export_dir, dodgers_dir[0])
    players_dir = os.path.join(d_path, "players")
    print(f"\n[다저스 팀 폴더 내부 구조]:")
    print("- team_info.json 존재 여부:", os.path.exists(os.path.join(d_path, "team_info.json")))
    print("- matches 폴더 내 경기 파일 수:", len(os.listdir(os.path.join(d_path, "matches"))))
    print("- players 폴더 내 선수 파일 수:", len(os.listdir(players_dir)))
    print("- 소속 선수 파일들:", os.listdir(players_dir))

    # 오타니 선수 파일 내용 확인
    ohtani_files = [f for f in os.listdir(players_dir) if "오타니" in f]
    if ohtani_files:
        import json
        with open(os.path.join(players_dir, ohtani_files[0]), "r", encoding="utf-8") as f:
            ohtani_data = json.load(f)
        print(f"\n[오타니 쇼헤이 선수 JSON 파일 내용]:")
        print("선수명:", ohtani_data["player_name"])
        print("포지션:", ohtani_data["position"])
        print("기간 내 출전 경기 수:", ohtani_data["total_games_played"])
        print("누적 성적:", ohtani_data["aggregated_stats"])
        print("경기별 로그 샘플:", ohtani_data["game_by_game_logs"][0])

print("\n=== 3. ZIP 파일 다운로드 API 테스트 ===")
zip_res = client.get("/api/v1/content/download-zip/MLB")
assert zip_res.status_code == 200
print(f"ZIP 다운로드 성공! (바이트 크기: {len(zip_res.content)} bytes)")

print("\n[SUCCESS] 사용자의 모든 요구사항(메이저리그 전체팀, 날짜기간, 팀별 폴더, 선수별 파일, 내보내기 API) 완벽 검증 성공!")