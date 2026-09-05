import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoints():
    print("--- 1. 관리 대시보드 웹 UI (GET /) ---")
    res = client.get("/")
    assert res.status_code == 200
    assert "스포츠 데이터 수집 및 앱 관리 센터" in res.text
    print("UI 서빙 정상")

    print("\n--- 2. 경기 목록 조회 (GET /api/v1/matches) ---")
    res = client.get("/api/v1/matches")
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) > 0
    print(f"조회 성공: {len(matches)}개 경기 확인")

    match_id = matches[0]["id"]
    print(f"\n--- 3. 경기 상세 정보 조회 (GET /api/v1/matches/{match_id}) ---")
    res = client.get(f"/api/v1/matches/{match_id}")
    assert res.status_code == 200
    detail = res.json()
    print("홈팀 vs 원정팀:", detail["home_team_name"], "vs", detail["away_team_name"])
    print("이벤트 수:", len(detail["events"]), "선수 스탯 수:", len(detail["player_stats"]))

    if detail["player_stats"]:
        stat_id = detail["player_stats"][0]["id"]
        player_name = detail["player_stats"][0]["player_name"]
        print(f"\n--- 4. 선수 스탯 수정 (PATCH /api/v1/players/stats/{stat_id}) ---")
        patch_res = client.patch(
            f"/api/v1/players/stats/{stat_id}",
            json={"points": 5, "assists": 3, "override_reason": "앱 테스트용 수치 수정"}
        )
        assert patch_res.status_code == 200
        patched_data = patch_res.json()
        print(f"{player_name} 점수 변경 확인 -> 득점: {patched_data['points']}, 도움: {patched_data['assists']}, override: {patched_data['is_override']}")

    print(f"\n--- 5. 사용자 앱 연동용 최종 JSON 내보내기 (GET /api/v1/export/app-payload/{match_id}) ---")
    export_res = client.get(f"/api/v1/export/app-payload/{match_id}")
    assert export_res.status_code == 200
    app_payload = export_res.json()
    print("앱 전송용 페이로드 스키마 키:", list(app_payload.keys()))
    print("최종 스코어 요약:", app_payload["score_summary"])

    print("\n 모든 FastAPI 엔드포인트 동작 검증 완료!")

if __name__ == "__main__":
    test_api_endpoints()