import sqlite3
conn = sqlite3.connect('sports_data.db')
c = conn.cursor()
c.execute('''
    UPDATE match_details
    SET team_stats = '{}'
    WHERE team_stats LIKE '%54.8%' 
       OR team_stats LIKE '%53.2%' 
       OR team_stats LIKE '%"possessionPct": 52%'
       OR team_stats LIKE '%"possessionPct": 53%'
       OR team_stats LIKE '%"possessionPct": 48%'
       OR team_stats LIKE '%"possessionPct": 47%'
''')
print('Purged count:', c.rowcount)
conn.commit()
conn.close()