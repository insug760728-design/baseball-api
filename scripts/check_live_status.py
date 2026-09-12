import sqlite3
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("sports_data.db")
c = conn.cursor()
c.execute("""
    SELECT id, sport_code, league_name, match_date, home_team_name, away_team_name, home_score, away_score, status
    FROM matches
    WHERE match_date LIKE '2026-09-11%'
    ORDER BY match_date ASC
""")
rows = c.fetchall()
print(f"Total matches for today (2026-09-11): {len(rows)}")
for r in rows:
    print(r)
