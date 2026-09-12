import sys
import os
import sqlite3
import json

sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import SessionLocal
from app.models.models import Match
from app.services.live_api_sports_service import LiveApiSportsService

print("=== 1. Checking Database Matches for 2026-09-11 Evening ===")
conn = sqlite3.connect("sports_data.db")
c = conn.cursor()
c.execute("""
    SELECT id, sport_code, league_name, match_date, home_team_name, away_team_name, home_score, away_score, status
    FROM matches
    WHERE match_date LIKE '2026-09-11 18%' OR match_date LIKE '2026-09-11 19%'
""")
for r in c.fetchall():
    print(r)

print("\n=== 2. Checking LiveApiSportsService Configuration ===")
print("Is Configured:", LiveApiSportsService.is_configured())
print("Provider:", "RapidAPI" if LiveApiSportsService.is_rapidapi() else "Direct API-Sports")
print("Key masked:", LiveApiSportsService.get_api_key()[:6] + "..." if LiveApiSportsService.get_api_key() else "None")

print("\n=== 3. Testing Baseball Live Sync ===")
bb_res = LiveApiSportsService.sync_live_baseball()
print("Baseball Sync Result:", bb_res)

print("\n=== 4. Testing Football Live Sync ===")
fb_res = LiveApiSportsService.sync_live_football()
print("Football Sync Result:", fb_res)

print("\n=== 5. Re-checking Database Matches ===")
c.execute("""
    SELECT id, sport_code, league_name, match_date, home_team_name, away_team_name, home_score, away_score, status
    FROM matches
    WHERE match_date LIKE '2026-09-11 18%' OR match_date LIKE '2026-09-11 19%'
""")
for r in c.fetchall():
    print(r)
