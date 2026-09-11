# -*- coding: utf-8 -*-
"""
미국 메이저리그 사커 (MLS) 5개년(2021~2025) 공식 경기 데이터 및 정밀 박스스코어 수집/적재 파이프라인
출처: ESPN Soccer API (usa.1)
"""
import os, sys, json, sqlite3, urllib.request, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

root_dir = r"c:\Users\user\Desktop\api"
DB_PATH = os.path.join(root_dir, "sports_data.db")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

MLS_TEAM_MAP = {
    "Inter Miami CF": "인터 마이애미", "Inter Miami": "인터 마이애미",
    "LA Galaxy": "LA 갤럭시",
    "Los Angeles FC": "LAFC", "LAFC": "LAFC",
    "Atlanta United FC": "애틀랜타 유나이티드", "Atlanta United": "애틀랜타 유나이티드",
    "Seattle Sounders FC": "시애틀 사운더스", "Seattle Sounders": "시애틀 사운더스",
    "New York Red Bulls": "뉴욕 레드불스",
    "New York City FC": "NY시티FC", "NYCFC": "NY시티FC",
    "Philadelphia Union": "필라델피아 유니온",
    "Columbus Crew": "콜럼버스 크루", "Columbus Crew SC": "콜럼버스 크루",
    "FC Cincinnati": "FC 신시내티",
    "Orlando City SC": "올랜도 시티", "Orlando City": "올랜도 시티",
    "Charlotte FC": "샬럿FC",
    "Nashville SC": "내슈빌SC",
    "Toronto FC": "토론토FC",
    "CF Montréal": "몬트리올", "CF Montreal": "몬트리올", "Montreal Impact": "몬트리올",
    "D.C. United": "DC 유나이티드", "DC United": "DC 유나이티드",
    "New England Revolution": "뉴잉글랜드",
    "Chicago Fire FC": "시카고 파이어", "Chicago Fire": "시카고 파이어",
    "St. Louis CITY SC": "세인트루이스 시티", "St Louis City SC": "세인트루이스 시티",
    "Houston Dynamo FC": "휴스턴 다이나모", "Houston Dynamo": "휴스턴 다이나모",
    "FC Dallas": "FC 댈러스",
    "Austin FC": "오스틴FC",
    "Sporting Kansas City": "스포팅 캔자스시티",
    "Minnesota United FC": "미네소타 유나이티드", "Minnesota United": "미네소타 유나이티드",
    "Colorado Rapids": "콜로라도 래피즈",
    "Real Salt Lake": "레알 솔트레이크",
    "Portland Timbers": "포틀랜드 팀버즈",
    "Vancouver Whitecaps FC": "밴쿠버 화이트캡스", "Vancouver Whitecaps": "밴쿠버 화이트캡스",
    "San Jose Earthquakes": "산호세 어스퀘이크스",
    "San Diego FC": "샌디에이고 FC",
}

def clean_team_name(name):
    n = (name or '').strip()
    return MLS_TEAM_MAP.get(n, n)

def fetch_espn_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def parse_boxscore(teams_data):
    if not teams_data or len(teams_data) < 2:
        return None, None
    home_entry = next((t for t in teams_data if t.get('homeAway') == 'home'), teams_data[0])
    away_entry = next((t for t in teams_data if t.get('homeAway') == 'away'), teams_data[1])

    def parse_one(entry):
        res = {}
        for item in entry.get('statistics', []):
            name = item.get('name')
            val_str = item.get('displayValue')
            val_num = item.get('value')
            if name == 'possessionPct':
                try:
                    res['possessionPct'] = float(val_str)
                    res['possession'] = f"{val_str}%"
                except:
                    res['possessionPct'] = float(val_num) if val_num is not None else 50.0
                    res['possession'] = f"{res['possessionPct']}%"
            elif name in ['totalShots', 'shotsOnTarget', 'wonCorners', 'yellowCards', 'redCards', 'foulsCommitted', 'saves', 'offsides']:
                try: res[name] = int(val_str)
                except:
                    res[name] = int(val_num) if val_num is not None else 0
        return res

    return parse_one(home_entry), parse_one(away_entry)

def run():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT match_date, home_team_name, away_team_name, id FROM matches WHERE league_name LIKE '%MLS%' OR league_name LIKE '%메이저리그 사커%'")
    existing = {}
    for r in c.fetchall():
        d_str = str(r[0])[:10]
        existing[(d_str, clean_team_name(r[1]), clean_team_name(r[2]))] = r[3]

    print(f"Existing MLS matches in DB: {len(existing)}")

    years = ["2021", "2022", "2023", "2024", "2025"]
    total_inserted = 0
    total_updated = 0

    for yr in years:
        print(f"\n--- Ingesting MLS Season {yr} ---")
        segments = [
            f"{yr}0201-{yr}0531",
            f"{yr}0601-{yr}0831",
            f"{yr}0901-{yr}1215"
        ]
        all_events = []
        for seg in segments:
            sb_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard?dates={seg}&limit=1000"
            sb_data = fetch_espn_json(sb_url)
            if sb_data and 'events' in sb_data:
                for ev in sb_data['events']:
                    st = ev.get('status', {}).get('type', {})
                    if st.get('completed', False) or st.get('state') == 'post':
                        all_events.append(ev)
            time.sleep(0.05)

        print(f"Found {len(all_events)} completed MLS events for {yr}")

        def process_ev(ev):
            ev_id = ev.get('id')
            raw_date = ev.get('date', '')
            g_date = raw_date[:10]
            g_time = raw_date[11:16] if 'T' in raw_date else '19:00'
            match_datetime = f"{g_date} {g_time}"

            comp = ev.get('competitions', [{}])[0]
            comps = comp.get('competitors', [])
            if len(comps) < 2: return None

            hc = next((x for x in comps if x.get('homeAway') == 'home'), comps[0])
            ac = next((x for x in comps if x.get('homeAway') == 'away'), comps[1])

            h_team = clean_team_name(hc.get('team', {}).get('displayName', ''))
            a_team = clean_team_name(ac.get('team', {}).get('displayName', ''))
            try: h_score = int(hc.get('score', 0))
            except: h_score = 0
            try: a_score = int(ac.get('score', 0))
            except: a_score = 0

            sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/summary?event={ev_id}"
            sum_data = fetch_espn_json(sum_url)
            h_stats, a_stats = parse_boxscore(sum_data.get('boxscore', {}).get('teams', [])) if sum_data else (None, None)

            lines_h = hc.get('linescores', [])
            lines_a = ac.get('linescores', [])
            ht_h = int(lines_h[0].get('value', 0)) if len(lines_h) > 0 else 0
            ht_a = int(lines_a[0].get('value', 0)) if len(lines_a) > 0 else 0

            stadium = comp.get('venue', {}).get('fullName', 'MLS 경기장')
            official_id = f"SOCCER_MLS_{yr}_{ev_id}_{g_date}_{h_team}_{a_team}".replace(' ', '_')

            return {
                "ev_id": ev_id, "g_date": g_date, "match_datetime": match_datetime,
                "h_team": h_team, "a_team": a_team, "h_score": h_score, "a_score": a_score,
                "stadium": stadium, "official_id": official_id,
                "h_stats": h_stats, "a_stats": a_stats,
                "period_scores": {"half_time": {"home": ht_h, "away": ht_a}, "full_time": {"home": h_score, "away": a_score}}
            }

        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [pool.submit(process_ev, ev) for ev in all_events]
            for f in as_completed(futures):
                item = f.result()
                if not item: continue

                key = (item["g_date"], item["h_team"], item["a_team"])
                now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                p_scores_json = json.dumps(item["period_scores"], ensure_ascii=False)
                t_stats_json = json.dumps({"home": item["h_stats"] or {}, "away": item["a_stats"] or {}}, ensure_ascii=False) if item["h_stats"] else "{}"
                src_url = f"https://www.espn.com/soccer/match/_/gameId/{item['ev_id']}"

                if key in existing:
                    m_id = existing[key]
                    c.execute("SELECT id FROM match_details WHERE match_id = ?", (m_id,))
                    d_row = c.fetchone()
                    if d_row:
                        c.execute("UPDATE match_details SET period_scores = ?, team_stats = ?, source_url = ? WHERE id = ?", (p_scores_json, t_stats_json, src_url, d_row[0]))
                    else:
                        c.execute("INSERT INTO match_details (match_id, period_scores, team_stats, source_url, is_customized) VALUES (?, ?, ?, ?, 0)", (m_id, p_scores_json, t_stats_json, src_url))
                    total_updated += 1
                else:
                    c.execute("""
                        INSERT INTO matches (
                            official_id, sport_code, league_name, season, round_name,
                            match_date, stadium, home_team_name, away_team_name,
                            home_score, away_score, status, is_customized, created_at, updated_at
                        ) VALUES (?, 'SOCCER', '미국 메이저리그 사커 (MLS)', ?, '정규리그', ?, ?, ?, ?, ?, ?, 'FINISHED', 0, ?, ?)
                    """, (item["official_id"], yr, item["match_datetime"], item["stadium"], item["h_team"], item["a_team"], item["h_score"], item["a_score"], now_ts, now_ts))
                    m_id = c.lastrowid
                    c.execute("INSERT INTO match_details (match_id, period_scores, team_stats, source_url, is_customized) VALUES (?, ?, ?, ?, 0)", (m_id, p_scores_json, t_stats_json, src_url))
                    existing[key] = m_id
                    total_inserted += 1

        conn.commit()
        print(f"✓ Year {yr} MLS complete. Inserted: {total_inserted}, Updated: {total_updated}")

    conn.close()
    print(f"\n>>> Total MLS Ingested: {total_inserted} new matches, {total_updated} updated with boxscores! <<<")

if __name__ == '__main__':
    run()