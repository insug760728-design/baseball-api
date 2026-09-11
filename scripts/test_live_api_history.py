import sys
sys.path.append('.')
from app.services.live_api_sports_service import LiveApiSportsService
import sqlite3
import json

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()
c.execute('''
    SELECT id, home_team_name, away_team_name, league_name 
    FROM matches 
    WHERE sport_code = 'SOCCER' AND status = 'SCHEDULED' 
    LIMIT 5
''')
matches = c.fetchall()
conn.close()

for m in matches:
    mid, h, a, lg = m
    print('=== Testing Match', mid, ':', h, 'vs', a, f'({lg}) ===')
    res = LiveApiSportsService.get_match_history(mid, 5)
    h_rec = res.get('home_recent', [])
    a_rec = res.get('away_recent', [])
    print('Home Recent:', len(h_rec), 'Away Recent:', len(a_rec))
    if h_rec:
        print('  Home Last Game:', h_rec[0].get('home_team_name'), 'vs', h_rec[0].get('away_team_name'), str(h_rec[0].get('home_score')) + ':' + str(h_rec[0].get('away_score')))
        print('  Home Last Stats:', json.dumps(h_rec[0].get('team_stats'), ensure_ascii=False))
    if a_rec:
        print('  Away Last Game:', a_rec[0].get('home_team_name'), 'vs', a_rec[0].get('away_team_name'), str(a_rec[0].get('home_score')) + ':' + str(a_rec[0].get('away_score')))
        print('  Away Last Stats:', json.dumps(a_rec[0].get('team_stats'), ensure_ascii=False))