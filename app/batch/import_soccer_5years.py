# -*- coding: utf-8 -*-
"""
Soccer 5-Year Historical Importer (2021 ~ 2026)
==============================================
사용자 요청: "최근결과란에 축구는 업데이트가 안되어있어 최근결과란 현시점부터 5년과거를 해당해"
현시점(2026년) 기준 과거 5년치(2021 ~ 2026) 전 리그 축구 공식 경기 및 맞대결 실데이터를 DB에 인제스트.
"""
import sqlite3
import json
import os
import sys
import logging
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.soccer_historical_agent import SoccerHistoricalAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SoccerImporter")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sports_data.db'))

def save_soccer_games(conn, games):
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

    detail_records = []
    player_stat_records = []
    
    for g in games:
        cur.execute("SELECT id FROM matches WHERE official_id = ?", (g["official_id"],))
        row = cur.fetchone()
        if row:
            m_id = row[0]
            period_json = json.dumps(g.get("period_scores", {}), ensure_ascii=False)
            team_stats_json = json.dumps(g.get("team_stats", {}), ensure_ascii=False)
            detail_records.append((m_id, period_json, team_stats_json))

            for ps in g.get("player_stats", []):
                player_stat_records.append((
                    m_id,
                    ps.get("team_name"),
                    ps.get("player_name"),
                    ps.get("position", "FW"),
                    ps.get("points", 0),
                    ps.get("assists", 0),
                    ps.get("shots", 0),
                    json.dumps(ps.get("extra_stats", {}), ensure_ascii=False)
                ))

    if detail_records:
        cur.executemany("""
            INSERT OR REPLACE INTO match_details (match_id, period_scores, team_stats)
            VALUES (?, ?, ?)
        """, detail_records)
        conn.commit()

    if player_stat_records:
        cur.executemany("""
            INSERT INTO player_match_stats (match_id, team_name, player_name, position, points, assists, shots, extra_stats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, player_stat_records)
        conn.commit()

    return len(games)

def run_soccer_import():
    start_time = time.time()
    logger.info(f"Starting 5-Year Soccer Batch Ingestion into {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uidx_matches_official_id ON matches(official_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team_name, away_team_name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_sport_status ON matches(sport_code, status, match_date);")
    conn.commit()

    seasons = [2021, 2022, 2023, 2024, 2025, 2026]
    total_ingested = 0

    soccer_agent = SoccerHistoricalAgent()
    for s in seasons:
        logger.info(f"==> Launching Soccer Agent for season {s}...")
        games = soccer_agent.fetch_season_games(s)
        cnt = save_soccer_games(conn, games)
        total_ingested += cnt
        logger.info(f"    Season {s}: Saved {cnt} matches.")

    cur.execute("SELECT count(*) FROM matches WHERE sport_code = 'SOCCER' AND status = 'FINISHED';")
    fin_cnt = cur.fetchone()[0]

    cur.execute("SELECT min(match_date), max(match_date) FROM matches WHERE sport_code = 'SOCCER' AND status = 'FINISHED';")
    min_d, max_d = cur.fetchone()

    conn.close()
    elapsed = time.time() - start_time
    logger.info(f"🎉 5-Year Soccer Ingestion Completed in {elapsed:.2f}s!")
    logger.info(f"Finished Soccer Matches in DB: {fin_cnt:,} (Range: {min_d} ~ {max_d})")

if __name__ == '__main__':
    run_soccer_import()
