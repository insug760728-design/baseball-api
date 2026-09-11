import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

leagues = [
    ("잉글랜드 프리미어리그 (EPL)", "eng.1"),
    ("스페인 라리가 (La Liga)", "esp.1"),
    ("독일 분데스리가 (Bundesliga)", "ger.1"),
    ("이탈리아 세리에 A (Serie A)", "ita.1"),
    ("프랑스 리그 1 (Ligue 1)", "fra.1"),
    ("일본 J리그 (J.League)", "jpn.1"),
    ("미국 메이저리그 사커 (MLS)", "usa.1"),
]

for lg_name, espn_code in leagues:
    c.execute("SELECT DISTINCT home_team_name FROM matches WHERE league_name = ?", (lg_name,))
    teams = [r[0] for r in c.fetchall()]
    print(f"=== {lg_name} ({len(teams)} teams) ===")
    print(teams[:10])

conn.close()
