import sys
sys.path.append('.')
from app.services.team_split_service import TeamSplitService
import json

svc = TeamSplitService()
res = svc.get_matchup_analysis('토트넘', '아스널', 'SOCCER', '잉글랜드 프리미어리그 (EPL)')
h_rec = res.get('home_recent_matches', [])
a_rec = res.get('away_recent_matches', [])
print(f'Home recent games: {len(h_rec)}, Away recent games: {len(a_rec)}')
if h_rec:
    print('Home Last Game:', h_rec[0].get('opponent'), h_rec[0].get('score'))
    print('Home Last Game Team Stats:', json.dumps(h_rec[0].get('team_stats'), ensure_ascii=False))
if a_rec:
    print('Away Last Game:', a_rec[0].get('opponent'), a_rec[0].get('score'))
    print('Away Last Game Team Stats:', json.dumps(a_rec[0].get('team_stats'), ensure_ascii=False))