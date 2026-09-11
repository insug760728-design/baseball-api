# -*- coding: utf-8 -*-
import os
import sys
import json
import sqlite3
import urllib.request
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

root_dir = r"c:\Users\user\Desktop\api"
DB_PATH = os.path.join(root_dir, "sports_data.db")
ALIAS_PATH = os.path.join(root_dir, "scripts", "team_aliases.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

with open(ALIAS_PATH, 'r', encoding='utf-8') as f:
    NORM_MAP = json.load(f)

def norm_team(name):
    if not name:
        return ""
    n = str(name).strip()
    return NORM_MAP.get(n, n)

def fetch_espn_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None

def parse_boxscore_stats(teams_data):
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
            elif name in ['accuratePasses', 'totalPasses']:
                try: res[name] = int(val_str)
                except: pass
        return res

    home_stats = parse_one(home_entry)
    away_stats = parse_one(away_entry)
    return home_stats, away_stats

def run_precision_ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT m.id, m.official_id, m.league_name, m.match_date, m.home_team_name, m.away_team_name, d.id, d.team_stats
        FROM matches m
        LEFT JOIN match_details d ON m.id = d.match_id
        WHERE m.sport_code = 'SOCCER'
    """)
    db_rows = c.fetchall()
    print(f"Total soccer matches in DB: {len(db_rows)}")

    db_lookup = {}
    for mid, off_id, lg_name, mdate, h_name, a_name, detail_id, team_stats in db_rows:
        d_str = str(mdate)[:10].replace('.', '-')
        hn = norm_team(h_name)
        an = norm_team(a_name)
        key = (d_str, hn, an)
        db_lookup[key] = {
            "match_id": mid,
            "official_id": off_id,
            "league_name": lg_name,
            "match_date": mdate,
            "detail_id": detail_id,
        }

    target_leagues = [
        {"code": "eng.1", "name": "잉글랜드 프리미어리그 (EPL)"},
        {"code": "esp.1", "name": "스페인 라리가 (La Liga)"},
        {"code": "ger.1", "name": "독일 분데스리가 (Bundesliga)"},
        {"code": "ita.1", "name": "이탈리아 세리에 A (Serie A)"},
        {"code": "fra.1", "name": "프랑스 리그 1 (Ligue 1)"},
        {"code": "jpn.1", "name": "일본 J리그 (J.League)"},
        {"code": "usa.1", "name": "미국 메이저리그 사커 (MLS)"},
    ]

    date_segments = [
        "20210101-20210630", "20210701-20211231",
        "20220101-20220630", "20220701-20221231",
        "20230101-20230630", "20230701-20231231",
        "20240101-20240630", "20240701-20241231",
        "20250101-20250630", "20250701-20251231",
        "20260101-20260911"
    ]

    total_updated = 0

    for lg in target_leagues:
        lg_code = lg["code"]
        lg_name = lg["name"]
        print(f"\n=======================================================")
        print(f"Collecting Official Boxscores: {lg_name} ({lg_code})")
        print(f"=======================================================")

        all_events = []
        for seg in date_segments:
            sb_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg_code}/scoreboard?dates={seg}&limit=1000"
            sb_data = fetch_espn_json(sb_url)
            if sb_data and 'events' in sb_data:
                events = sb_data.get('events', [])
                for ev in events:
                    status_type = ev.get('status', {}).get('type', {})
                    if status_type.get('completed', False) or status_type.get('state') == 'post':
                        all_events.append(ev)
            time.sleep(0.04)

        print(f"Total completed events found for {lg_code}: {len(all_events)}")

        def fetch_event_boxscore(ev):
            ev_id = ev.get('id')
            raw_date = ev.get('date', '')[:10]
            comp = ev.get('competitions', [{}])[0]
            comps = comp.get('competitors', [])
            if len(comps) < 2:
                return None
            hc = next((c for c in comps if c.get('homeAway') == 'home'), comps[0])
            ac = next((c for c in comps if c.get('homeAway') == 'away'), comps[1])
            h_raw = hc.get('team', {}).get('displayName', '')
            a_raw = ac.get('team', {}).get('displayName', '')
            hn = norm_team(h_raw)
            an = norm_team(a_raw)

            sum_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg_code}/summary?event={ev_id}"
            sum_data = fetch_espn_json(sum_url)
            if not sum_data:
                return None

            boxscore_teams = sum_data.get('boxscore', {}).get('teams', [])
            h_stats, a_stats = parse_boxscore_stats(boxscore_teams)
            
            linescores_h = hc.get('linescores', [])
            linescores_a = ac.get('linescores', [])
            ht_h = int(linescores_h[0].get('value', 0)) if len(linescores_h) > 0 else 0
            ht_a = int(linescores_a[0].get('value', 0)) if len(linescores_a) > 0 else 0
            try: ft_h = int(hc.get('score', 0))
            except: ft_h = 0
            try: ft_a = int(ac.get('score', 0))
            except: ft_a = 0

            return {
                "event_id": ev_id,
                "date": raw_date,
                "home_norm": hn,
                "away_norm": an,
                "home_raw": h_raw,
                "away_raw": a_raw,
                "home_stats": h_stats,
                "away_stats": a_stats,
                "period_scores": {
                    "half_time": {"home": ht_h, "away": ht_a},
                    "full_time": {"home": ft_h, "away": ft_a}
                }
            }

        league_updated = 0
        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_ev = {executor.submit(fetch_event_boxscore, ev): ev for ev in all_events}
            for future in as_completed(future_to_ev):
                res = future.result()
                if not res or not res["home_stats"] or not res["away_stats"]:
                    continue

                d_str = res["date"]
                hn = res["home_norm"]
                an = res["away_norm"]
                key = (d_str, hn, an)

                db_item = db_lookup.get(key)
                if not db_item:
                    continue

                match_id = db_item["match_id"]
                detail_id = db_item["detail_id"]

                team_stats_json = json.dumps({
                    "home": res["home_stats"],
                    "away": res["away_stats"]
                }, ensure_ascii=False)

                period_scores_json = json.dumps(res["period_scores"], ensure_ascii=False)

                if detail_id:
                    c.execute("""
                        UPDATE match_details
                        SET team_stats = ?, period_scores = ?, source_url = ?, is_customized = 0
                        WHERE id = ?
                    """, (team_stats_json, period_scores_json, f"https://www.espn.com/soccer/match/_/gameId/{res['event_id']}", detail_id))
                else:
                    c.execute("""
                        INSERT INTO match_details (match_id, period_scores, team_stats, source_url, is_customized)
                        VALUES (?, ?, ?, ?, 0)
                    """, (match_id, period_scores_json, team_stats_json, f"https://www.espn.com/soccer/match/_/gameId/{res['event_id']}"))

                league_updated += 1
                total_updated += 1

                if league_updated % 100 == 0:
                    conn.commit()
                    print(f"  Updated {league_updated} matches...")

        conn.commit()
        print(f"✓ Completed {lg_name}: {league_updated} matches updated with genuine ESPN boxscores.")

    print("\n=======================================================")
    print("Purging remaining mock/formulaic dummy stats across entire DB...")
    print("=======================================================")

    c.execute("""
        UPDATE match_details
        SET team_stats = '{}'
        WHERE team_stats LIKE '%54.8%' 
           OR team_stats LIKE '%"possessionPct": 52%' 
           OR team_stats LIKE '%"possessionPct": 53%'
           OR team_stats LIKE '%"possessionPct": 48%'
           OR team_stats LIKE '%"possessionPct": 47%'
    """)
    cleaned_rows = c.rowcount
    conn.commit()
    print(f"✓ Cleaned {cleaned_rows} mock/formulaic detail records (set to empty {{}} so UI renders '-' cleanly).")

    conn.close()
    print(f"\n>>> Total Precision Soccer Boxscores Ingested: {total_updated:,} matches! <<<")

if __name__ == "__main__":
    run_precision_ingest()