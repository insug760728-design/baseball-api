"""
3-Year Historical Data Batch Importer (2023 ~ 2025)
Orchestrates MLB, KBO, NPB, and European Top 5 + Championship + K-League + J-League Soccer Agents.
"""
import sqlite3
import json
import os
import sys
import logging
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.agents.mlb_historical_agent import MLBOfficialAgent
from app.agents.kbo_historical_agent import KBOHistoricalAgent
from app.agents.npb_historical_agent import NPBHistoricalAgent
from app.agents.soccer_historical_agent import SoccerHistoricalAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BatchImporter")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../sports_data.db'))

def create_db_indexes(conn):
    cur = conn.cursor()
    logger.info("Optimizing DB indexes for sub-millisecond querying...")
    cur.execute("""
        DELETE FROM matches WHERE id NOT IN (
            SELECT MIN(id) FROM matches GROUP BY official_id
        ) AND official_id IS NOT NULL;
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uidx_matches_official_id ON matches(official_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team_name, away_team_name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_sport_status ON matches(sport_code, status, match_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_match_details_match_id ON match_details(match_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_player_match_stats_match_id ON player_match_stats(match_id);")
    conn.commit()

def run_import():
    start_time = time.time()
    logger.info(f"Starting 3-Year Batch Ingestion into {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    create_db_indexes(conn)
    cur = conn.cursor()

    seasons = [2023, 2024, 2025]
    total_ingested = 0

    # 1. MLB Official Agent
    mlb_agent = MLBOfficialAgent()
    for s in seasons:
        logger.info(f"==> Launching MLB Agent for season {s}...")
        games = mlb_agent.fetch_season_games(s)
        total_ingested += save_games_to_db(conn, games)

    # 2. KBO Historical Agent
    kbo_agent = KBOHistoricalAgent()
    for s in seasons:
        logger.info(f"==> Launching KBO Agent for season {s}...")
        games = kbo_agent.fetch_season_games(s)
        total_ingested += save_games_to_db(conn, games)

    # 3. NPB Historical Agent
    npb_agent = NPBHistoricalAgent()
    for s in seasons:
        logger.info(f"==> Launching NPB Agent for season {s}...")
        games = npb_agent.fetch_season_games(s)
        total_ingested += save_games_to_db(conn, games)

    # 4. Comprehensive Soccer Agent (Big 5 + Championship + K-League + J-League)
    soccer_agent = SoccerHistoricalAgent()
    for s in seasons:
        logger.info(f"==> Launching Soccer Agent for season {s}...")
        games = soccer_agent.fetch_season_games(s)
        total_ingested += save_games_to_db(conn, games)

    # Check total DB count
    cur.execute("SELECT count(*) FROM matches;")
    match_cnt = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM match_details;")
    detail_cnt = cur.fetchone()[0]

    conn.close()
    elapsed = time.time() - start_time
    logger.info(f"🎉 Batch Ingestion Completed in {elapsed:.2f}s!")
    logger.info(f"Total Matches in DB: {match_cnt:,} | Total Match Details: {detail_cnt:,}")

def save_games_to_db(conn, games):
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

    # Fast batch UPSERT into matches
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
            match_date=excluded.match_date
    """, match_records)
    conn.commit()

    # Ingest match_details and player_stats in batch
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

            # Add player stats if present
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

if __name__ == '__main__':
    run_import()
