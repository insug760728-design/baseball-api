import sqlite3
import json
import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

# Check sample matches in DB for EPL 2023-24 season
c.execute("""
    SELECT id, match_date, home_team_name, away_team_name, home_score, away_score
    FROM matches
    WHERE league_name = '잉글랜드 프리미어리그 (EPL)' AND match_date >= '2023-08-01' AND match_date <= '2024-05-31'
    ORDER BY match_date
    LIMIT 10
""")
db_rows = c.fetchall()
print("Sample DB EPL matches (2023-24):")
for r in db_rows:
    print(r)

conn.close()
