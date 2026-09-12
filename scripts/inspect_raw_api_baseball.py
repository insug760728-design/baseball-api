import sys
import os
import json

sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.live_api_sports_service import LiveApiSportsService

data_today = LiveApiSportsService._make_request("/games?date=2026-09-11", sport="baseball")
games = (data_today or {}).get("response", [])
print(f"Total baseball games from API-Baseball for 2026-09-11: {len(games)}")
for g in games:
    league = g.get("league", {})
    teams = g.get("teams", {})
    scores = g.get("scores", {})
    status = g.get("status", {})
    print(f"ID: {g.get('id')} | League: {league.get('name')} | {teams.get('home', {}).get('name')} vs {teams.get('away', {}).get('name')} | Status: {status.get('short')}/{status.get('long')} | Score: {scores.get('home', {}).get('total')} : {scores.get('away', {}).get('total')}")
