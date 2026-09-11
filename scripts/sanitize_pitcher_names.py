import sqlite3
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.player_translation import translate_player_name

conn = sqlite3.connect("sports_data.db")
c = conn.cursor()
c.execute("""
    SELECT id, home_team_name, away_team_name, home_pitcher, away_pitcher, league_name
    FROM matches
    WHERE sport_code = 'BASEBALL'
""")
rows = c.fetchall()
updated = 0
for r in rows:
    m_id, h_team, a_team, h_p, a_p, lg = r
    new_h_p = translate_player_name(h_p) if h_p else h_p
    new_a_p = translate_player_name(a_p) if a_p else a_p
    if new_h_p != h_p or new_a_p != a_p:
        c.execute("UPDATE matches SET home_pitcher = ?, away_pitcher = ? WHERE id = ?", (new_h_p, new_a_p, m_id))
        updated += 1
        print(f"Updated match {m_id}: {h_p}->{new_h_p} vs {a_p}->{new_a_p}")

conn.commit()
print(f"Total pitcher names updated: {updated}")
