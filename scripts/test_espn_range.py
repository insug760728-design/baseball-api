import urllib.request
import json

# Test fetching a full season scoreboard or date chunks from ESPN
url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20240815-20240901&limit=100"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    events = data.get('events', [])
    print(f"Events found in range: {len(events)}")
    for ev in events[:3]:
        print(f"ID: {ev['id']}, Date: {ev['date']}, Name: {ev['name']}")
