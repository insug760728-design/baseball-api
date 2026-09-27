import json
import sqlite3
from datetime import datetime

NAME_MAP = {
    'Albania': '알바니아',
    'Andorra': '안도라',
    'Anguilla': '앵귈라',
    'Antigua and Barbuda': '앤티가 바부다',
    'Armenia': '아르메니아',
    'Aruba': '아루바',
    'Austria': '오스트리아',
    'Azerbaijan': '아제르바이잔',
    'Bahamas': '바하마',
    'Barbados': '바베이도스',
    'Belarus': '벨라루스',
    'Belgium': '벨기에',
    'Belize': '벨리즈',
    'Bermuda': '버뮤다',
    'Bonaire': '보네르',
    'Bosnia & Herzegovina': '보스니아 헤르체고비나',
    'British Virgin Islands': '영국령 버진아일랜드',
    'Bulgaria': '불가리아',
    'Cayman Islands': '케이맨 제도',
    'Costa Rica': '코스타리카',
    'Croatia': '크로아티아',
    'Cuba': '쿠바',
    'Curaçao': '퀴라소',
    'Cyprus': '키프로스',
    'Czechia': '체코',
    'Czech Republic': '체코',
    'Denmark': '덴마크',
    'Dominica': '도미니카',
    'Dominican Republic': '도미니카공화국',
    'El Salvador': '엘살바도르',
    'England': '잉글랜드',
    'Estonia': '에스토니아',
    'FYR Macedonia': '북마케도니아',
    'North Macedonia': '북마케도니아',
    'Faroe Islands': '페로제도',
    'Finland': '핀란드',
    'France': '프랑스',
    'French Guyana': '프랑스령 기아나',
    'Georgia': '조지아',
    'Germany': '독일',
    'Gibraltar': '지브롤터',
    'Greece': '그리스',
    'Grenada': '그레나다',
    'Guadeloupe': '과들루프',
    'Guatemala': '과테말라',
    'Guyana': '가이아나',
    'Haiti': '아이티',
    'Honduras': '온두라스',
    'Hungary': '헝가리',
    'Iceland': '아이슬란드',
    'Israel': '이스라엘',
    'Italy': '이탈리아',
    'Jamaica': '자메이카',
    'Kazakhstan': '카자흐스탄',
    'Kosovo': '코소보',
    'Latvia': '라트비아',
    'Liechtenstein': '리히텐슈타인',
    'Lithuania': '리투아니아',
    'Luxembourg': '룩셈부르크',
    'Malta': '몰타',
    'Martinique': '마르티니크',
    'Moldova': '몰도바',
    'Montenegro': '몬테네그로',
    'Montserrat': '몬트세랫',
    'Netherlands': '네덜란드',
    'Nicaragua': '니카라과',
    'Northern Ireland': '북아일랜드',
    'Norway': '노르웨이',
    'Poland': '폴란드',
    'Portugal': '포르투갈',
    'Puerto Rico': '푸에르토리코',
    'Rep. Of Ireland': '아일랜드공화국',
    'Republic of Ireland': '아일랜드공화국',
    'Ireland': '아일랜드공화국',
    'Romania': '루마니아',
    'Saint Martin': '생마르탱',
    'San Marino': '산마리노',
    'Scotland': '스코틀랜드',
    'Serbia': '세르비아',
    'Sint Maarten': '신트마르턴',
    'Slovakia': '슬로바키아',
    'Slovenia': '슬로베니아',
    'Spain': '스페인',
    'St. Kitts and Nevis': '세인트키츠 네비스',
    'St. Lucia': '세인트루시아',
    'St. Vincent / Grenadines': '세인트빈센트 그레나딘',
    'Suriname': '수리남',
    'Sweden': '스웨덴',
    'Switzerland': '스위스',
    'Trinidad and Tobago': '트리니다드 토바고',
    'Turks and Caicos Islands': '터크스 케이커스 제도',
    'Türkiye': '튀르키예',
    'Turkey': '튀르키예',
    'US Virgin Islands': '미국령 버진아일랜드',
    'Ukraine': '우크라이나',
    'Wales': '웨일스'
}

def translate_team(name):
    return NAME_MAP.get(name, name)

conn = sqlite3.connect('sports_data.db')
cursor = conn.cursor()

# Get max id to generate safe non-conflicting IDs
cursor.execute("SELECT MAX(id) FROM matches")
max_id = cursor.fetchone()[0] or 30000
next_id = max(max_id + 1, 80000)

files_to_sync = [
    ('uefa_nations_2026.json', 'UEFA 네이션스리그'),
    ('uefa_nations_2024.json', 'UEFA 네이션스리그'),
    ('euro_2024.json', 'UEFA 유로 2024'),
    ('concacaf_nations_2025.json', 'CONCACAF 네이션스리그')
]

inserted_count = 0
updated_count = 0

for fn, default_league in files_to_sync:
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            fixtures = json.load(f)
    except Exception as e:
        print(f"Skipping {fn}: {e}")
        continue

    for fx in fixtures:
        status_short = fx['fixture']['status']['short']
        if status_short not in ['FT', 'AET', 'PEN']:
            continue
            
        gh = fx['goals']['home']
        ga = fx['goals']['away']
        if gh is None or ga is None:
            continue
            
        date_raw = fx['fixture']['date']
        # Convert UTC ISO date to KST date string YYYY-MM-DD HH:MM
        try:
            from datetime import timezone, timedelta
            dt_utc = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
            dt_kst = dt_utc.astimezone(timezone(timedelta(hours=9)))
            match_date = dt_kst.strftime('%Y-%m-%d %H:%M')
            d_part = dt_kst.strftime('%Y-%m-%d')
        except Exception:
            match_date = date_raw[:16].replace('T', ' ')
            d_part = date_raw[:10]

        h_en = fx['teams']['home']['name']
        a_en = fx['teams']['away']['name']
        h_kr = translate_team(h_en)
        a_kr = translate_team(a_en)
        
        league_name = default_league
        sport_code = 'SOCCER'
        
        # Check if this match already exists in matches table (by teams and date)
        cursor.execute("""
            SELECT id, home_score, away_score, status FROM matches 
            WHERE sport_code = 'SOCCER'
              AND (
                  (home_team_name = ? AND away_team_name = ?)
                  OR (home_team_name = ? AND away_team_name = ?)
              )
              AND match_date LIKE ?
        """, (h_kr, a_kr, a_kr, h_kr, f"{d_part}%"))
        
        row = cursor.fetchone()
        if row:
            mid, ex_hs, ex_as, ex_st = row
            # Update with true score
            cursor.execute("""
                UPDATE matches 
                SET home_score = ?, away_score = ?, status = 'FINISHED'
                WHERE id = ?
            """, (gh, ga, mid))
            updated_count += 1
        else:
            # Insert as official completed match
            cursor.execute("""
                INSERT INTO matches (
                    id, sport_code, league_name, match_date, 
                    home_team_name, away_team_name, home_score, away_score, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'FINISHED')
            """, (next_id, sport_code, league_name, match_date, h_kr, a_kr, gh, ga))
            next_id += 1
            inserted_count += 1

conn.commit()
print(f"Sync complete! Inserted: {inserted_count} official national matches, Updated: {updated_count} matches.")
