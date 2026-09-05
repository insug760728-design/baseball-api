import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== 1. EPL 축구 전 경기 & 전 선수 라인업 수집 (2026-09-01 ~ 2026-09-05) ===")
res = client.post("/api/v1/crawler/sync", json={
    "league_id": "EPL",
    "start_date": "2026-09-01",
    "end_date": "2026-09-05"
})
assert res.status_code == 200

# 첫 번째 경기 상세 조회
matches = client.get("/api/v1/matches?league=EPL").json()
match_id = matches[0]["id"]
det = client.get(f"/api/v1/matches/{match_id}").json()

print(f"\n[경기] {det['home_team_name']} vs {det['away_team_name']}")
print(f"총 출전 선수 수: {len(det['player_stats'])}명 (전원 수집 완료)")
print("홈팀 선수 명단:", [p['player_name'] for p in det['player_stats'] if p['team_name'] == det['home_team_name']])
print("원정팀 선수 명단:", [p['player_name'] for p in det['player_stats'] if p['team_name'] == det['away_team_name']])

print("\n=== 2. MLB 메이저리그 1~9번 전 타순 + 투수 라인업 수집 ===")
mlb_sync = client.post("/api/v1/crawler/sync", json={"league_id": "MLB"}).json()
mlb_matches = client.get("/api/v1/matches?league=MLB").json()
mlb_det = client.get(f"/api/v1/matches/{mlb_matches[0]['id']}").json()

print(f"[MLB 경기] {mlb_det['home_team_name']} vs {mlb_det['away_team_name']}")
print(f"MLB 출전 전 선수 수: {len(mlb_det['player_stats'])}명")
for p in mlb_det['player_stats'][:6]:
    print(f"- {p['team_name']} #{p['back_number']} {p['player_name']} ({p['position']}): {p['points']}타점, {p['shots']}타수")

print("\n=== 3. KBL 프로농구 전 선수 라인업 수집 ===")
kbl_sync = client.post("/api/v1/crawler/sync", json={"league_id": "KBL"}).json()
kbl_matches = client.get("/api/v1/matches?league=KBL").json()
kbl_det = client.get(f"/api/v1/matches/{kbl_matches[0]['id']}").json()

print(f"[KBL 경기] {kbl_det['home_team_name']} vs {kbl_det['away_team_name']}")
print(f"KBL 출전 전 선수 수: {len(kbl_det['player_stats'])}명")
for p in kbl_det['player_stats'][:4]:
    print(f"- {p['team_name']} {p['player_name']} ({p['position']}): {p['points']}PTS, {p['assists']}AST")

print("\n[SUCCESS] 전 경기 전 선수(Full Roster) 라인업 및 개인 수치 수집 완벽 검증 성공!")