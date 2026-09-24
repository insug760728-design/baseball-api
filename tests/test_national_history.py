import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from app.agents.historical_agent_router import HistoricalAgentRouter

matches_to_test = [
    27366, 27367, 27368, 27369, 27370, 27371, 27372, 27373, 27374, 27375,
    27376, 27377, 27378, 27379, 27380, 27381, 27382, 27383, 27384, 27385,
    27386, 27387, 27388
]

for mid in matches_to_test:
    res = HistoricalAgentRouter.get_match_history_by_agent(mid, 10)
    home_tm = res.get('home_team')
    away_tm = res.get('away_team')
    h2h = res.get('h2h_matches', [])
    home_rec = res.get('home_recent', [])
    away_rec = res.get('away_recent', [])

    h2h_first = f"{h2h[0].get('date')} {h2h[0].get('home_team_name')} {h2h[0].get('home_score')}-{h2h[0].get('away_score')} {h2h[0].get('away_team_name')}" if h2h else "None"
    hr_first = f"{home_rec[0].get('date')} vs {home_rec[0].get('opponent')} [{home_rec[0].get('league_name')}]" if home_rec else "None"
    ar_first = f"{away_rec[0].get('date')} vs {away_rec[0].get('opponent')} [{away_rec[0].get('league_name')}]" if away_rec else "None"

    print(f"[{mid}] {home_tm} vs {away_tm} ({res.get('league_name')}): H2H={len(h2h)} ({h2h_first}) | HR={len(home_rec)} ({hr_first}) | AR={len(away_rec)} ({ar_first})")
