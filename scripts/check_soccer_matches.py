import sqlite3
import sys
import os

sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import SessionLocal
from app.services.match_service import MatchService
from app.services.team_split_service import TeamSplitService

conn = sqlite3.connect("sports_data.db")
c = conn.cursor()
c.execute("""
    SELECT id, sport_code, league_name, match_date, home_team_name, away_team_name, status
    FROM matches
    WHERE sport_code = 'SOCCER' AND match_date LIKE '2026-09-11%'
    ORDER BY match_date ASC
""")
rows = c.fetchall()
print(f"Total soccer matches today (2026-09-11): {len(rows)}")
for r in rows:
    print(r)

if rows:
    first_match = rows[0]
    m_id = first_match[0]
    print(f"\n--- Checking detail for First Soccer Match (ID {m_id}: {first_match[4]} vs {first_match[5]}) ---")
    db = SessionLocal()
    detail = MatchService.get_match_full_detail(db, m_id)
    if detail:
        m = detail["match"]
        matchup = detail.get("matchup_analysis") or TeamSplitService.get_matchup_analysis(m.home_team_name, m.away_team_name, m.sport_code, match_id=m.id)
        h_rec = matchup.get("home_recent_matches", [])
        a_rec = matchup.get("away_recent_matches", [])
        print(f"Home ({m.home_team_name}) recent matches count: {len(h_rec)}")
        if h_rec:
            print("  First home recent match:", h_rec[0])
        print(f"Away ({m.away_team_name}) recent matches count: {len(a_rec)}")
        if a_rec:
            print("  First away recent match:", a_rec[0])
    db.close()
