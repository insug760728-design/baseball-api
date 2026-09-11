import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

leagues = [
    "잉글랜드 프리미어리그 (EPL)",
    "스페인 라리가 (La Liga)",
    "독일 분데스리가 (Bundesliga)",
    "이탈리아 세리에 A (Serie A)",
    "프랑스 리그 1 (Ligue 1)",
    "일본 J리그 (J.League)",
    "일본 J1리그",
    "미국 메이저리그 사커 (MLS)",
]

all_teams = {}
for lg in leagues:
    c.execute("SELECT DISTINCT home_team_name FROM matches WHERE league_name = ?", (lg,))
    teams = [r[0] for r in c.fetchall()]
    all_teams[lg] = sorted(teams)

with open('scripts/all_db_soccer_teams.json', 'w', encoding='utf-8') as f:
    json.dump(all_teams, f, ensure_ascii=False, indent=2)

print("Saved all teams to scripts/all_db_soccer_teams.json")
conn.close()
