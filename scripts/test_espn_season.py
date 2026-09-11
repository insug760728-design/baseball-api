import urllib.request
import json

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20230801-20240531&limit=1000"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    events = data.get('events', [])
    print(f"EPL 2023-24 Season events count: {len(events)}")
