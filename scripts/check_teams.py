import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

c.execute("""
    SELECT DISTINCT home_team_name 
    FROM matches 
    WHERE league_name = '잉글랜드 프리미어리그 (EPL)' 
    ORDER BY home_team_name
""")
teams = [r[0] for r in c.fetchall()]
print(f"EPL DB Teams ({len(teams)}): {teams}")

c.execute("""
    SELECT DISTINCT home_team_name 
    FROM matches 
    WHERE league_name = '일본 J리그 (J.League)' OR league_name = '일본 J1리그'
    ORDER BY home_team_name
""")
jteams = [r[0] for r in c.fetchall()]
print(f"J-League DB Teams ({len(jteams)}): {jteams[:15]}")

conn.close()
