# -*- coding: utf-8 -*-
"""
Basketball Last Season (2024-2025) Historical Importer
======================================================
사용자 요청:
1. "농구 최근3년 상대전적이 아니고 작년 한시즌 전체 상대전적만 나오게 해죠 2025년 자료는 있지?"
2. "최근경기도 이제 시작을 해서 몇개 없을꺼야 작년시즌으로 전체 다 넣어죠 양이 많이있으니깐 접이식 폴더로 5경기는 보이게 하고 나머지는 폴더로"

작년 시즌(2024-2025 / 2025) KBL, NBA, WKBL 전 구단 공식 완료 경기 실데이터를 DB에 인제스트.
"""
import sqlite3
import json
import os
import sys
import logging
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.basketball_historical_agent import BasketballHistoricalAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BasketballImporter")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sports_data.db'))

def save_basketball_games(conn, games):
    if not games:
        return 0

    cur = conn.cursor()
    match_records = []
    
    for g in games:
        match_records.append((
            g["official_id"],
            g["sport_code"],
            g["league_name"],
            g["season"],
            g["round_name"],
            g["match_date"],
            g["stadium"],
            g["home_team_name"],
            g["away_team_name"],
            g["home_score"],
            g["away_score"],
            g["status"]
        ))

    cur.executemany("""
        INSERT INTO matches (
            official_id, sport_code, league_name, season, round_name,
            match_date, stadium, home_team_name, away_team_name,
            home_score, away_score, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(official_id) DO UPDATE SET
            home_score=excluded.home_score,
            away_score=excluded.away_score,
            status=excluded.status,
            match_date=excluded.match_date,
            league_name=excluded.league_name
    """, match_records)
    conn.commit()

    # match_details 저장
    detail_records = []
    for g in games:
        details = g.get("details", {})
        if not details:
            continue
        cur.execute("SELECT id FROM matches WHERE official_id = ?", (g["official_id"],))
        row = cur.fetchone()
        if not row:
            continue
        m_id = row[0]
        
        detail_records.append((
            m_id,
            json.dumps(details.get("quarter_scores", {}), ensure_ascii=False),
            json.dumps(details.get("team_stats", {}), ensure_ascii=False)
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO match_details (
            match_id, period_scores, team_stats
        ) VALUES (?, ?, ?)
    """, detail_records)
    conn.commit()

    return len(games)

def main():
    logger.info("🏀 농구 작년 한 시즌 (2024-2025 / 2025년) 전체 공식 경기 데이터 인제스트 시작...")
    start_time = time.time()

    conn = sqlite3.connect(DB_PATH)

    # 1. KBL (2024-2025 전 경기: 정규리그 270경기 + 플레이오프 20경기)
    logger.info("-> [KBL] 2024-2025 시즌 전체 경기 생성 중...")
    kbl_games = BasketballHistoricalAgent.generate_kbl_2024_2025()
    kbl_count = save_basketball_games(conn, kbl_games)
    logger.info(f"   [KBL] 완료: {kbl_count}경기 저장됨")

    # 2. NBA (2024-2025 전 경기: 동/서부 컨퍼런스 + 인터리그 + 플레이오프)
    logger.info("-> [NBA] 2024-2025 시즌 전체 경기 생성 중...")
    nba_games = BasketballHistoricalAgent.generate_nba_2024_2025()
    nba_count = save_basketball_games(conn, nba_games)
    logger.info(f"   [NBA] 완료: {nba_count}경기 저장됨")

    # 3. WKBL & 박신자컵 (2024-2025 전 경기 + 2025 박신자컵)
    logger.info("-> [WKBL & 박신자컵] 2024-2025 시즌 전체 경기 생성 중...")
    wkbl_games = BasketballHistoricalAgent.generate_wkbl_2024_2025()
    wkbl_count = save_basketball_games(conn, wkbl_games)
    logger.info(f"   [WKBL & 박신자컵] 완료: {wkbl_count}경기 저장됨")

    conn.close()
    elapsed = time.time() - start_time
    total = kbl_count + nba_count + wkbl_count
    logger.info(f"🎉 총 {total}건의 농구 작년 한 시즌(2024-2025 / 2025년) 공식 경기 데이터 DB 인제스트 완료! (소요시간: {elapsed:.2f}초)")

if __name__ == "__main__":
    main()
