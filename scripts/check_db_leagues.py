import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

target_leagues = [
    "잉글랜드 프리미어리그 (EPL)",
    "스페인 라리가 (La Liga)",
    "독일 분데스리가 (Bundesliga)",
    "이탈리아 세리에 A (Serie A)",
    "프랑스 리그 1 (Ligue 1)",
    "일본 J리그 (J.League)",
    "일본 J1리그",
    "미국 메이저리그 사커 (MLS)",
    "한국 K리그 1 (K League 1)",
    "한국 K리그 2 (K League 2)"
]

for lg in target_leagues:
    c.execute("SELECT count(*), min(match_date), max(match_date) FROM matches WHERE league_name = ?", (lg,))
    cnt, mind, maxd = c.fetchone()
    print(f"{lg:35s}: count={cnt}, range={mind} ~ {maxd}")

conn.close()
