import urllib.request
import json
import time
from concurrent.futures import ThreadPoolExecutor

url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20240815-20240901&limit=100"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    events = data.get('events', [])

def fetch_summary(ev):
    ev_id = ev['id']
    sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/summary?event={ev_id}"
    try:
        sum_req = urllib.request.Request(sum_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(sum_req, timeout=10) as sresp:
            sdata = json.loads(sresp.read().decode('utf-8'))
            teams = sdata.get('boxscore', {}).get('teams', [])
            return ev_id, len(teams)
    except Exception as e:
        return ev_id, str(e)

start = time.time()
with ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(fetch_summary, events))

print(f"Fetched {len(results)} match summaries in {time.time() - start:.2f}s")
print(f"Sample results: {results[:5]}")
