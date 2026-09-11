import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

c.execute('''
    SELECT 
        m.league_name, 
        count(m.id) as total_matches,
        sum(case when d.team_stats is not null and d.team_stats != '{}' and d.team_stats like '%possessionPct%' then 1 else 0 end) as real_boxscores,
        sum(case when d.team_stats = '{}' or d.team_stats is null then 1 else 0 end) as empty_or_null,
        sum(case when d.team_stats like '%54.8%' or d.team_stats like '%53.2%' or d.team_stats like '%"possessionPct": 52%' then 1 else 0 end) as mock_dummy
    FROM matches m
    LEFT JOIN match_details d ON m.id = d.match_id
    WHERE m.sport_code = 'SOCCER'
    GROUP BY m.league_name
    ORDER BY total_matches DESC
''')

rows = c.fetchall()
header = f"{'League Name':40s} | {'Total':>7s} | {'Real Boxscore':>13s} | {'Clean/Empty':>11s} | {'Mock/Dummy':>10s}"
print(header)
print('-' * len(header))
for r in rows:
    if r[1] > 50:
        print(f"{r[0]:40s} | {r[1]:7d} | {r[2]:13d} | {r[3]:11d} | {r[4]:10d}")

conn.close()