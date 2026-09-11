import urllib.request
import json

candidates = [
    "eng.1", "esp.1", "ger.1", "ita.1", "fra.1", "jpn.1", "usa.1",
    "uefa.champions", "eng.2", "jpn.2", "ned.1", "por.1",
    "kor.1", "kor.k1", "kor.kleague", "korea.1", "south.korea.1", "kor.k_league"
]

for code in candidates:
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            league_name = data.get('leagues', [{}])[0].get('name', 'Unknown')
            print(f"{code:20s}: SUCCESS -> {league_name}")
    except Exception as e:
        print(f"{code:20s}: {e}")
