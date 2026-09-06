import sqlite3
import json

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

c.execute("""
    SELECT DISTINCT league_name, home_team_name
    FROM matches 
    WHERE sport_code = 'SOCCER'
    ORDER BY league_name, home_team_name
""")

db_teams = {}
for lg, team in c.fetchall():
    db_teams.setdefault(lg, []).append(team)

with open('db_soccer_teams.json', 'w', encoding='utf-8') as f:
    json.dump(db_teams, f, ensure_ascii=False, indent=2)

print("Saved db_soccer_teams.json:")
for lg, teams in db_teams.items():
    print(f"  {lg}: {len(teams)} teams")
