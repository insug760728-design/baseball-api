import urllib.request
import json
import sys

leagues = ['eng.1', 'esp.1', 'ger.1', 'ita.1', 'fra.1', 'jpn.1', 'usa.1', 'kor.1']
for lg in leagues:
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard?dates=20240901-20240910"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            events = data.get('events', [])
            print(f"{lg}: {len(events)} events found")
            if events:
                ev = events[0]
                ev_id = ev['id']
                sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/summary?event={ev_id}"
                sum_req = urllib.request.Request(sum_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(sum_req, timeout=10) as sum_resp:
                    sum_data = json.loads(sum_resp.read().decode('utf-8'))
                    teams_stats = sum_data.get('boxscore', {}).get('teams', [])
                    print(f"   Event {ev_id}: {ev.get('name')}, boxscore teams count: {len(teams_stats)}")
                    if teams_stats:
                        stats = teams_stats[0].get('statistics', [])
                        print(f"   Stats sample: {[s.get('name') for s in stats[:6]]}")
    except Exception as e:
        print(f"{lg} error: {e}")
