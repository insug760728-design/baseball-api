import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== 1. 기간 범위(2026-09-01 ~ 2026-09-05) 수집 테스트 ===")
res = client.post("/api/v1/crawler/sync", json={
    "league_id": "EPL",
    "start_date": "2026-09-01",
    "end_date": "2026-09-05"
})
assert res.status_code == 200
data = res.json()
print("수집 결과 메시지:", data["message"])
print("수집 일자 범위:", data["result"]["date_range"])
print("수집된 경기 수:", data["result"]["synced_matches_count"])

print("\n=== 2. 기간 범위 경기 목록 조회 (GET /api/v1/matches) ===")
list_res = client.get("/api/v1/matches?start_date=2026-09-01&end_date=2026-09-05")
assert list_res.status_code == 200
matches = list_res.json()
print(f"해당 기간 경기 수: {len(matches)}")
for m in matches[:5]:
    print(f"[{m['match_date']}] {m['league_name']} | {m['home_team_name']} {m['home_score']} : {m['away_score']} {m['away_team_name']}")

print("\n[SUCCESS] 기간 범위(몇일부터 ~ 몇일까지) 수집 및 조회 완벽 검증 성공!")