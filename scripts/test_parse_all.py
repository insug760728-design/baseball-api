import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

def test_summary_parse(league_code, event_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/summary?event={event_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        boxscore = data.get('boxscore', {})
        teams = boxscore.get('teams', [])
        if len(teams) < 2:
            print("No boxscore teams")
            return
        
        home_entry = next((t for t in teams if t.get('homeAway') == 'home'), teams[0])
        away_entry = next((t for t in teams if t.get('homeAway') == 'away'), teams[1])
        
        def parse_stats(stats_list):
            res = {}
            for s in stats_list:
                name = s.get('name')
                val_str = s.get('displayValue')
                if name == 'possessionPct':
                    try:
                        res['possessionPct'] = float(val_str)
                        res['possession'] = f"{val_str}%"
                    except: pass
                elif name in ['totalShots', 'shotsOnTarget', 'wonCorners', 'yellowCards', 'redCards', 'foulsCommitted', 'saves', 'offsides']:
                    try:
                        res[name] = int(val_str)
                    except: pass
            return res
        
        home_stats = parse_stats(home_entry.get('statistics', []))
        away_stats = parse_stats(away_entry.get('statistics', []))
        
        print("Home:", home_entry.get('team', {}).get('displayName'), home_stats)
        print("Away:", away_entry.get('team', {}).get('displayName'), away_stats)

test_summary_parse('eng.1', '704279') # Man Utd vs Fulham
test_summary_parse('esp.1', '704797') # La Liga sample
test_summary_parse('ger.1', '711441') # Bundesliga sample
test_summary_parse('ita.1', '712134') # Serie A sample
test_summary_parse('fra.1', '706449') # Ligue 1 sample
test_summary_parse('jpn.1', '697426') # J-League sample
test_summary_parse('usa.1', '692995') # MLS sample
