import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/summary?event=704279"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    boxscore = data.get('boxscore', {})
    teams = boxscore.get('teams', [])
    for t in teams:
        team_info = t.get('team', {})
        print(f"Team: {team_info.get('displayName')} (Home: {t.get('homeAway') == 'home'})")
        stats = t.get('statistics', [])
        for s in stats:
            print(f"   {s.get('name')}: {s.get('displayValue')} ({s.get('value')})")
