import sqlite3
import json
import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

ALIAS_MAP = {
    # EPL
    "아스널": "Arsenal", "Arsenal": "Arsenal", "Arsenal FC": "Arsenal",
    "맨시티": "Manchester City", "맨체스터 시티": "Manchester City", "Manchester City": "Manchester City", "Man City": "Manchester City",
    "맨유": "Manchester United", "맨체스터 유나이티드": "Manchester United", "Manchester United": "Manchester United", "Man United": "Manchester United",
    "리버풀": "Liverpool", "Liverpool": "Liverpool", "Liverpool FC": "Liverpool",
    "첼시": "Chelsea", "Chelsea": "Chelsea", "Chelsea FC": "Chelsea",
    "토트넘": "Tottenham Hotspur", "Tottenham Hotspur": "Tottenham Hotspur", "Tottenham": "Tottenham Hotspur", "Spurs": "Tottenham Hotspur",
    "뉴캐슬": "Newcastle United", "Newcastle United": "Newcastle United", "Newcastle": "Newcastle United",
    "아스톤빌라": "Aston Villa", "아스톤 빌라": "Aston Villa", "Aston Villa": "Aston Villa",
    "브라이튼": "Brighton & Hove Albion", "Brighton & Hove Albion": "Brighton & Hove Albion", "Brighton": "Brighton & Hove Albion",
    "웨스트햄": "West Ham United", "West Ham United": "West Ham United", "West Ham": "West Ham United",
    "풀럼": "Fulham", "Fulham": "Fulham", "Fulham FC": "Fulham",
    "본머스": "AFC Bournemouth", "Bournemouth": "AFC Bournemouth", "AFC Bournemouth": "AFC Bournemouth",
    "브렌트포드": "Brentford", "Brentford": "Brentford", "Brentford FC": "Brentford",
    "C.팰리스": "Crystal Palace", "크리스탈 팰리스": "Crystal Palace", "Crystal Palace": "Crystal Palace",
    "울버햄튼": "Wolverhampton Wanderers", "울브스": "Wolverhampton Wanderers", "Wolverhampton Wanderers": "Wolverhampton Wanderers", "Wolves": "Wolverhampton Wanderers", "Wolverhampton": "Wolverhampton Wanderers",
    "에버턴": "Everton", "Everton": "Everton", "Everton FC": "Everton",
    "노팅엄": "Nottingham Forest", "노팅엄 포레스트": "Nottingham Forest", "Nottingham Forest": "Nottingham Forest",
    "루턴 타운": "Luton Town", "루턴": "Luton Town", "Luton Town": "Luton Town", "Luton": "Luton Town",
    "번리": "Burnley", "Burnley": "Burnley", "Burnley FC": "Burnley",
    "셰필드": "Sheffield United", "셰필드 유나이티드": "Sheffield United", "Sheffield United": "Sheffield United",
    "입스위치": "Ipswich Town", "Ipswich Town": "Ipswich Town", "Ipswich": "Ipswich Town",
    "레스터": "Leicester City", "레스터 시티": "Leicester City", "Leicester City": "Leicester City", "Leicester": "Leicester City",
    "사우샘프턴": "Southampton", "Southampton": "Southampton",
    "리즈": "Leeds United", "Leeds United": "Leeds United", "Leeds": "Leeds United",
    "왓포드": "Watford", "Watford": "Watford",
    "노리치": "Norwich City", "Norwich City": "Norwich City",
    "웨스트브롬": "West Bromwich Albion", "West Bromwich Albion": "West Bromwich Albion",
}

def norm(name):
    n = (name or '').strip()
    return ALIAS_MAP.get(n, n)

conn = sqlite3.connect('sports_data.db')
c = conn.cursor()

c.execute("""
    SELECT id, match_date, home_team_name, away_team_name, home_score, away_score
    FROM matches
    WHERE league_name = '잉글랜드 프리미어리그 (EPL)' AND match_date >= '2023-08-01' AND match_date <= '2024-05-31'
""")
db_matches = c.fetchall()

# Map by (date, home_norm, away_norm)
db_map = {}
for mid, mdate, h, a, hs, ascore in db_matches:
    d = str(mdate)[:10]
    db_map[(d, norm(h), norm(a))] = (mid, h, a, hs, ascore)

print(f"Total DB 2023-24 EPL matches loaded: {len(db_map)}")

# Fetch ESPN 2023-24 scoreboard
url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard?dates=20230801-20240531&limit=1000"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    events = data.get('events', [])

matched = 0
for ev in events:
    edate = ev.get('date', '')[:10]
    comp = ev.get('competitions', [{}])[0]
    comps = comp.get('competitors', [])
    if len(comps) >= 2:
        hc = next((c for c in comps if c.get('homeAway') == 'home'), comps[0])
        ac = next((c for c in comps if c.get('homeAway') == 'away'), comps[1])
        hn = norm(hc.get('team', {}).get('displayName'))
        an = norm(ac.get('team', {}).get('displayName'))
        if (edate, hn, an) in db_map:
            matched += 1

print(f"ESPN Events: {len(events)}, Matched with DB: {matched} ({matched/len(events)*100:.1f}%)")

conn.close()
