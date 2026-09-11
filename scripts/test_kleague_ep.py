import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json; charset=utf-8",
    "user-agent": "Mozilla/5.0",
    "Referer": "https://www.kleague.com/"
}

# Try some common KLeague portal URLs
endpoints = [
    ("getGameDetail.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getMatchDetail.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getGameRecord.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getMatchRecord.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getMatchSummary.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getGameSummary.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
    ("getGameData.do", {"year": "2024", "leagueId": 1, "gameId": 1}),
]

for ep, body in endpoints:
    url = f"https://www.kleague.com/{ep}"
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"{ep}: SUCCESS! keys={list(data.keys())}")
    except Exception as e:
        print(f"{ep}: {e}")
