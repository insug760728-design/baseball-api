# -*- coding: utf-8 -*-
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.models import Match

client = TestClient(app)

def run_tests():
    print("=== [1. 야구 전문 대시보드 및 API 헬스체크] ===")
    res = client.get("/")
    assert res.status_code == 200, f"Dashboard failed: {res.status_code}"
    assert "BASEBALL" in res.text or "야구" in res.text
    print("✓ 대시보드 (index.html) 정상 렌더링 확인 (200 OK)")

    print("\n=== [2. 기간별 야구 경기 수집 API (sync)] ===")
    sync_res = client.post("/api/v1/matches/sync", json={
        "league_id": "MLB",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03"
    })
    assert sync_res.status_code == 200, f"Sync failed: {sync_res.text}"
    sync_data = sync_res.json()
    print(f"✓ MLB 수집 완료: 총 {sync_data.get('synced_matches_count')}개 경기 동기화")

    print("\n=== [3. 야구 경기 목록 조회 API] ===")
    matches_res = client.get("/api/v1/matches/?sport_code=BASEBALL")
    assert matches_res.status_code == 200
    matches = matches_res.json()
    assert len(matches) > 0, "No matches found"
    for m in matches:
        assert m["sport_code"] == "BASEBALL", f"Found non-baseball match: {m['sport_code']}"
    print(f"✓ 전체 {len(matches)}개 야구 경기 조회 성공 (모두 BASEBALL)")

    first_match_id = matches[0]["id"]

    print(f"\n=== [4. 야구 경기 상세 & 이닝 전광판 & 선수 지표 조회 (ID: {first_match_id})] ===")
    detail_res = client.get(f"/api/v1/matches/{first_match_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    
    # 이닝별 스코어 확인
    period = detail["details"]["period_scores"]
    assert "innings" in period, "No innings in period_scores"
    print(f"✓ 1~9회 이닝별 전광판 스코어 확인 완료: {list(period['innings'].keys())}")

    # 타자 / 투수 라인업 확인
    p_stats = detail["player_stats"]
    assert len(p_stats) > 0, "No player stats found"
    hitters = [p for p in p_stats if (p.get("extra_stats", {}).get("type") == "HITTER" or "DH" in (p.get("position") or ""))]
    pitchers = [p for p in p_stats if (p.get("extra_stats", {}).get("type") == "PITCHER" or "P" in (p.get("position") or ""))]
    print(f"✓ 출전 명단 확인: 타자 {len(hitters)}명, 투수 {len(pitchers)}명")

    # 타자 세부 지표 확인 (오타니 쇼헤이 등)
    if hitters:
        sample_hitter = hitters[0]
        extra = sample_hitter.get("extra_stats", {})
        print(f"  - 타자 표본 [{sample_hitter['player_name']}]: 타수={extra.get('ab')}, 안타={extra.get('h')}, 홈런={extra.get('hr')}, 타점={sample_hitter.get('points')}, AVG={extra.get('avg')}, OPS={extra.get('ops')}")

    # 투수 세부 지표 확인 (야마모토 등)
    if pitchers:
        sample_pitcher = pitchers[0]
        pextra = sample_pitcher.get("extra_stats", {})
        print(f"  - 투수 표본 [{sample_pitcher['player_name']}]: 이닝={pextra.get('ip')}, 투구수={pextra.get('np')}, 자책점={pextra.get('er')}, 삼진={sample_pitcher.get('points')}, ERA={pextra.get('era')}, WHIP={pextra.get('whip')}")

    print("\n=== [5. 경기 스코어 수정 API 테스트] ===")
    score_update_res = client.put(f"/api/v1/matches/{first_match_id}/score", json={
        "home_score": 7,
        "away_score": 4,
        "status": "FINISHED",
        "custom_notes": "관리자 점수 정정 테스트"
    })
    assert score_update_res.status_code == 200
    updated_match = score_update_res.json()
    assert updated_match["home_score"] == 7
    assert updated_match["away_score"] == 4
    assert updated_match["is_customized"] is True
    print("✓ 경기 스코어 7:4로 수정 및 is_customized=True 반영 확인")

    print("\n=== [6. 선수 세부 수치 수정 API 테스트] ===")
    first_player = p_stats[0]
    p_id = first_player["id"]
    p_update_res = client.put(f"/api/v1/matches/players/{p_id}", json={
        "points": 4, # 4타점
        "shots": 5,  # 5타수
        "extra_stats": {
            "hr": 2,
            "avg": "0.335",
            "ops": "1.120"
        },
        "override_reason": "앱 전송용 홈런/타점 수치 수동 수정"
    })
    assert p_update_res.status_code == 200
    print(f"✓ 선수 [{first_player['player_name']}] 수치(4타점, 2홈런, OPS 1.120) 수정 완료")

    print("\n=== [7. 야구 구단 및 선수별 폴더/파일 생성 & ZIP 내보내기 테스트] ===")
    export_res = client.post("/api/v1/content/export-folders", json={
        "league_id": "MLB",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03"
    })
    assert export_res.status_code == 200, f"Export failed: {export_res.text}"
    exp_data = export_res.json()
    print(f"✓ 폴더 생성 응답: {exp_data['message']}")
    
    # 실제 디스크 폴더 검증
    export_dir = os.path.abspath("exports/MLB")
    assert os.path.exists(export_dir), f"Directory {export_dir} does not exist"
    teams = [d for d in os.listdir(export_dir) if os.path.isdir(os.path.join(export_dir, d))]
    print(f"✓ 생성된 구단 폴더 수: {len(teams)}개 구단 (예: {teams[:3]})")

    sample_team = teams[0]
    team_path = os.path.join(export_dir, sample_team)
    hitters_dir = os.path.join(team_path, "hitters")
    pitchers_dir = os.path.join(team_path, "pitchers")
    matches_dir = os.path.join(team_path, "matches")
    summary_file = os.path.join(team_path, "team_summary.json")

    assert os.path.exists(hitters_dir), f"No hitters dir in {team_path}"
    assert os.path.exists(pitchers_dir), f"No pitchers dir in {team_path}"
    assert os.path.exists(matches_dir), f"No matches dir in {team_path}"
    assert os.path.exists(summary_file), f"No team_summary.json in {team_path}"

    hitters_files = os.listdir(hitters_dir)
    pitchers_files = os.listdir(pitchers_dir)
    matches_files = os.listdir(matches_dir)

    print(f"✓ 구단 [{sample_team}] 폴더 내부 구조:")
    print(f"  - hitters/ 타자 파일 ({len(hitters_files)}개): {hitters_files[:2]}")
    print(f"  - pitchers/ 투수 파일 ({len(pitchers_files)}개): {pitchers_files[:2]}")
    print(f"  - matches/ 경기 파일 ({len(matches_files)}개): {matches_files[:1]}")
    print(f"  - team_summary.json 존재 확인")

    # ZIP 다운로드 테스트
    zip_res = client.get("/api/v1/content/download-zip/MLB")
    assert zip_res.status_code == 200, f"ZIP download failed: {zip_res.status_code}"
    assert len(zip_res.content) > 1000, "ZIP content too small"
    print(f"✓ ZIP 압축 다운로드 성공: {len(zip_res.content)} bytes")

    print("\n🎉 모든 야구 전용 기능 (수집, 1~9회 스코어보드, 타자/투수 정밀 지표, 수정, 폴더/파일/ZIP 내보내기) 검증 통과!")

if __name__ == "__main__":
    run_tests()
