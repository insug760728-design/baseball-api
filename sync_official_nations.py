import requests, json, os, sqlite3
from datetime import datetime
from app.core.config import settings

api_key = os.getenv('API_SPORTS_KEY') or settings.API_SPORTS_KEY
headers = {'x-apisports-key': api_key}

# Team name Korean mapping dictionary
NAME_MAP = {
    'Jamaica': '자메이카',
    'Guatemala': '과테말라',
    'South Africa': '남아프리카공화국',
    'Nigeria': '나이지리아',
    'India': '인도',
    'Congo DR': '콩고민주공화국',
    'DR Congo': '콩고민주공화국',
    'New Caledonia': '뉴칼레도니아',
    'Martinique': '마르티니크',
    'Grenada': '그레나다',
    'Curacao': '퀴라소',
    'Curaçao': '퀴라소',
    'Honduras': '온두라스',
    'Nicaragua': '니카라과',
    'Ecuador': '에콰도르',
    'Czechia': '체코',
    'Czech Republic': '체코',
    'Algeria': '알제리',
    'Canada': '캐나다',
    'Suriname': '수리남',
    'Panama': '파나마',
    'El Salvador': '엘살바도르',
    'USA': '미국',
    'United States': '미국',
    'Guadeloupe': '과들루프',
    'Dominican Republic': '도미니카공화국',
    'Costa Rica': '코스타리카',
    'Mexico': '멕시코',
    'Trinidad and Tobago': '트리니다드토바고',
    'Haiti': '아이티',
    'Cuba': '쿠바',
    'Bermuda': '버뮤다',
    'Guyana': '가이아나',
    'Venezuela': '베네수엘라',
    'Uruguay': '우루과이',
    'Brazil': '브라질',
    'Argentina': '아르헨티나',
    'Colombia': '콜롬비아',
    'Chile': '칠레',
    'Peru': '페루',
    'Bolivia': '볼리비아',
    'Paraguay': '파라과이'
}

LEAGUE_MAP = {
    'CONCACAF Nations League': 'CONCACAF 네이션스리그',
    'CONCACAF Gold Cup': 'CONCACAF 골드컵',
    'World Cup - Qualification CONCACAF': '북중미 월드컵 예선',
    'World Cup - Qualification Intercontinental Play-offs': '월드컵 대륙간 플레이오프',
    'Friendlies': 'A매치 친선경기',
    'Copa America': '코파 아메리카'
}

def translate_team(name):
    return NAME_MAP.get(name, name)

def translate_league(name):
    for k, v in LEAGUE_MAP.items():
        if k.lower() in name.lower():
            return v
    return name

# Fetch fixtures for Jamaica (2385)
jm_res = requests.get('https://v3.football.api-sports.io/fixtures?team=2385&last=20', headers=headers, timeout=10)
jm_fixtures = jm_res.json().get('response', []) if jm_res.ok else []

# Fetch fixtures for Guatemala (5161)
gt_res = requests.get('https://v3.football.api-sports.io/fixtures?team=5161&last=20', headers=headers, timeout=10)
gt_fixtures = gt_res.json().get('response', []) if gt_res.ok else []

# Fetch H2H
h2h_res = requests.get('https://v3.football.api-sports.io/fixtures/headtohead?h2h=2385-5161', headers=headers, timeout=10)
h2h_fixtures = h2h_res.json().get('response', []) if h2h_res.ok else []

all_fixtures = {}
for f in jm_fixtures + gt_fixtures + h2h_fixtures:
    fid = f['fixture']['id']
    status = f['fixture']['status']['short']
    # Only keep completed matches
    if status in ['FT', 'AET', 'PEN']:
        all_fixtures[fid] = f

print(f"Collected {len(all_fixtures)} unique completed official matches from API-Sports")

conn = sqlite3.connect('sports_data.db')
cursor = conn.cursor()

inserted = 0
updated = 0

for fid, f in all_fixtures.items():
    fixture = f['fixture']
    league = f['league']
    teams = f['teams']
    goals = f['goals']
    
    m_date_str = fixture['date'][:16].replace('T', ' ')
    h_team = translate_team(teams['home']['name'])
    a_team = translate_team(teams['away']['name'])
    h_score = goals['home'] if goals['home'] is not None else 0
    a_score = goals['away'] if goals['away'] is not None else 0
    l_name = translate_league(league['name'])
    official_id = str(fid)
    season = str(league.get('season') or '2024')
    round_name = str(league.get('round') or '')

    # Check if match already exists by official_id or (date + teams)
    cursor.execute("SELECT id FROM matches WHERE official_id = ? OR (match_date LIKE ? AND home_team_name = ? AND away_team_name = ?)", 
                   (official_id, f"{m_date_str[:10]}%", h_team, a_team))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE matches 
            SET home_score = ?, away_score = ?, status = 'FINISHED', league_name = ?
            WHERE id = ?
        """, (h_score, a_score, l_name, row[0]))
        updated += 1
    else:
        cursor.execute("""
            INSERT INTO matches (
                official_id, sport_code, league_name, season, round_name,
                match_date, stadium, home_team_name, away_team_name,
                home_score, away_score, status, is_customized, created_at, updated_at
            ) VALUES (?, 'SOCCER', ?, ?, ?, ?, '공식경기장', ?, ?, ?, ?, 'FINISHED', 0, datetime('now'), datetime('now'))
        """, (official_id, l_name, season, round_name, m_date_str, h_team, a_team, h_score, a_score))
        inserted += 1

conn.commit()
conn.close()

print(f"Sync complete! Inserted: {inserted}, Updated: {updated}")
