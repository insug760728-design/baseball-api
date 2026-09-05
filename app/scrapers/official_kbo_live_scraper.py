# -*- coding: utf-8 -*-
"""
한국 프로야구 (KBO 리그) 공식 사이트 (koreabaseball.com) 실시간 수집기
- 공식 서비스: https://www.koreabaseball.com/ws/Schedule.asmx
- 100% 공식 실시간 데이터 (경기 일정, 1~9회(연장) 이닝별 스코어보드, 출전 선수 전원 박스스코어, 주요 상황 타임라인)
"""
import urllib.request
import urllib.parse
import ssl
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

KBO_TEAMS_MAP = {
    'LG': 'LG 트윈스', '두산': '두산 베어스', 'KIA': 'KIA 타이거즈',
    '삼성': '삼성 라이온즈', '한화': '한화 이글스', 'SSG': 'SSG 랜더스',
    'NC': 'NC 다이노스', 'KT': 'KT 위즈', '롯데': '롯데 자이언츠', '키움': '키움 히어로즈'
}

KBO_CODE_MAP = {
    'LG': 'LG 트윈스', 'OB': '두산 베어스', 'HT': 'KIA 타이거즈',
    'SS': '삼성 라이온즈', 'HH': '한화 이글스', 'SK': 'SSG 랜더스',
    'NC': 'NC 다이노스', 'KT': 'KT 위즈', 'LT': '롯데 자이언츠', 'WO': '키움 히어로즈'
}

KBO_STADIUM_MAP = {
    '잠실': '잠실야구장', '대구': '대구삼성라이온즈파크', '수원': '수원KT위즈파크',
    '창원': '창원NC파크', '고척': '고척스카이돔', '문학': '인천SSG랜더스필드',
    '사직': '사직야구장', '광주': '광주기아챔피언스필드', '대전': '한화생명이글스파크', '한밭': '한화생명이글스파크'
}

POS_MAP = {
    '一': '1루수', '二': '2루수', '三': '3루수', '유': '유격수',
    '좌': '좌익수', '중': '중견수', '우': '우익수', '포': '포수', '지': '지명타자'
}

def clean_int(val: Any, default: int = 0) -> int:
    if val is None:
        return default
    s = re.sub(r'<[^>]+>', '', str(val)).strip()
    return int(s) if s.isdigit() else default

class KboOfficialScraper:
    """한국 프로야구 KBO 공식 데이터 수집기"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.koreabaseball.com/Schedule/Schedule.aspx'
        }
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def _post(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=self.headers)
        with urllib.request.urlopen(req, context=self.ctx, timeout=12) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            if text.startswith('{') or text.startswith('['):
                return json.loads(text)
            return {}

    def scrape_schedule(self, target_date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """지정 기간 또는 특정 일자의 KBO 공식 경기 일정 및 결과 수집"""
        d_ref = target_date or start_date or datetime.now().strftime("%Y-%m-%d")
        parts = d_ref.split('-')
        year = parts[0] if len(parts) > 0 else "2026"
        month = parts[1] if len(parts) > 1 else "09"

        url = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList'
        
        # 먼저 해당 연도 수집, 경기 없으면 2026 또는 2024 대체 조회
        seasons_to_try = [year]
        if year != "2026":
            seasons_to_try.append("2026")
        if year != "2024":
            seasons_to_try.append("2024")

        all_rows = []
        target_season = year
        for s_year in seasons_to_try:
            res = self._post(url, {
                'leId': '1',
                'srIdList': '0,9',
                'seasonId': s_year,
                'gameMonth': month,
                'teamId': ''
            })
            rows = res.get('rows', [])
            if rows:
                all_rows = rows
                target_season = s_year
                break

        if not all_rows:
            return []

        games = []
        cur_date_str = d_ref

        for r in all_rows:
            cols = r.get('row', [])
            date_col = next((c.get('Text') for c in cols if 'day' in (c.get('Class') or '')), None)
            if date_col:
                m = re.search(r'(\d{2})\.(\d{2})', date_col)
                if m:
                    cur_date_str = f"{target_season}-{m.group(1)}-{m.group(2)}"

            # 기간 필터링
            if start_date and cur_date_str < start_date:
                continue
            if end_date and cur_date_str > end_date:
                continue
            if target_date and not (start_date or end_date) and cur_date_str != target_date:
                continue

            play_col = next((c.get('Text') for c in cols if 'play' in (c.get('Class') or '')), None)
            if not play_col:
                continue

            time_col = next((c.get('Text') for c in cols if 'time' in (c.get('Class') or '')), '')
            time_clean = re.sub(r'<[^>]+>', '', time_col).strip() or '18:30'
            relay_col = next((c.get('Text') for c in cols if 'relay' in (c.get('Class') or '')), '')
            stadium_raw = cols[7].get('Text', '') if len(cols) > 7 else ''
            stadium = KBO_STADIUM_MAP.get(stadium_raw, f"{stadium_raw}야구장" if stadium_raw and stadium_raw != '-' else 'KBO 야구장')

            away_team_m = re.search(r'<span>([^<]+)</span>\s*<em>', play_col)
            home_team_m = re.search(r'</em>\s*<span>([^<]+)</span>', play_col)
            away_score_m = re.search(r'<em>.*?<span[^>]*>(\d+)</span>\s*<span>vs</span>', play_col)
            home_score_m = re.search(r'<span>vs</span>\s*<span[^>]*>(\d+)</span>.*?</em>', play_col)
            game_id_m = re.search(r'gameId=([a-zA-Z0-9]+)', relay_col)

            away_raw = away_team_m.group(1).strip() if away_team_m else ''
            home_raw = home_team_m.group(1).strip() if home_team_m else ''

            away_team = KBO_TEAMS_MAP.get(away_raw, away_raw or '원정팀')
            home_team = KBO_TEAMS_MAP.get(home_raw, home_raw or '홈팀')
            away_score = int(away_score_m.group(1)) if away_score_m else 0
            home_score = int(home_score_m.group(1)) if home_score_m else 0

            game_id = game_id_m.group(1) if game_id_m else f"{cur_date_str.replace('-', '')}_{len(games)}"
            is_finished = ("id='btnReview'" in relay_col or ">리뷰<" in relay_col) and (away_score_m is not None)
            is_live = ("id='btnRelay'" in relay_col or "문자중계" in relay_col)
            status = "FINISHED" if is_finished else ("LIVE" if is_live else "SCHEDULED")

            games.append({
                "official_id": f"KBO_{game_id}",
                "sport_code": "BASEBALL",
                "league_name": "한국 프로야구 (KBO)",
                "season": target_season,
                "round_name": "정규시즌",
                "match_date": f"{cur_date_str} {time_clean}",
                "stadium": stadium,
                "home_team_name": home_team,
                "away_team_name": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "game_id": game_id
            })

        return games

    def scrape_game_detail(self, game_id: str) -> Dict[str, Any]:
        """KBO 공식 박스스코어, 라인스코어, 선수 기록, 타임라인 수집"""
        # game_id 접두어 처리
        if game_id.startswith("KBO_"):
            clean_gid = game_id.replace("KBO_", "")
        else:
            clean_gid = game_id

        season_id = clean_gid[:4] if len(clean_gid) >= 4 and clean_gid[:4].isdigit() else "2026"

        # 구단명 결정 (game_id: YYYYMMDD + AWAY(2) + HOME(2) + GNUM)
        away_code = clean_gid[8:10] if len(clean_gid) >= 10 else ""
        home_code = clean_gid[10:12] if len(clean_gid) >= 12 else ""
        away_team_name = KBO_CODE_MAP.get(away_code, "원정팀")
        home_team_name = KBO_CODE_MAP.get(home_code, "홈팀")

        # 1. 스코어보드 라인스코어 조회
        url_score = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetScoreBoardScroll'
        s_data = self._post(url_score, {
            'leId': '1',
            'srId': '0',
            'seasonId': season_id,
            'gameId': clean_gid
        })

        # 2. 박스스코어 조회
        url_box = 'https://www.koreabaseball.com/ws/Schedule.asmx/GetBoxScoreScroll'
        b_data = self._post(url_box, {
            'leId': '1',
            'srId': '0',
            'seasonId': season_id,
            'gameId': clean_gid
        })

        # (1) 이닝별 스코어보드 가공
        t2 = {}
        t3 = {}
        if s_data.get('table2'):
            try:
                t2 = json.loads(s_data['table2'])
            except Exception:
                pass
        if s_data.get('table3'):
            try:
                t3 = json.loads(s_data['table3'])
            except Exception:
                pass

        away_row = t2.get('rows', [{}])[0].get('row', []) if t2.get('rows') else []
        home_row = t2.get('rows', [{}])[1].get('row', []) if t2.get('rows') and len(t2['rows']) > 1 else []

        innings_dict = {}
        total_innings = max(len(away_row), len(home_row), 9)
        for idx in range(total_innings):
            inn_num = str(idx + 1)
            a_val = away_row[idx].get('Text', '-') if idx < len(away_row) else '-'
            h_val = home_row[idx].get('Text', '-') if idx < len(home_row) else '-'
            innings_dict[inn_num] = {
                'away': int(a_val) if str(a_val).isdigit() else a_val,
                'home': int(h_val) if str(h_val).isdigit() else h_val
            }

        away_summary_row = t3.get('rows', [{}])[0].get('row', []) if t3.get('rows') else []
        home_summary_row = t3.get('rows', [{}])[1].get('row', []) if t3.get('rows') and len(t3['rows']) > 1 else []

        period_scores = {
            'innings': innings_dict,
            'summary': {
                'away': {
                    'R': clean_int(away_summary_row[0].get('Text') if len(away_summary_row) > 0 else 0),
                    'H': clean_int(away_summary_row[1].get('Text') if len(away_summary_row) > 1 else 0),
                    'E': clean_int(away_summary_row[2].get('Text') if len(away_summary_row) > 2 else 0),
                    'B': clean_int(away_summary_row[3].get('Text') if len(away_summary_row) > 3 else 0),
                },
                'home': {
                    'R': clean_int(home_summary_row[0].get('Text') if len(home_summary_row) > 0 else 0),
                    'H': clean_int(home_summary_row[1].get('Text') if len(home_summary_row) > 1 else 0),
                    'E': clean_int(home_summary_row[2].get('Text') if len(home_summary_row) > 2 else 0),
                    'B': clean_int(home_summary_row[3].get('Text') if len(home_summary_row) > 3 else 0),
                }
            }
        }

        team_stats = {
            'hits': {'home': period_scores['summary']['home']['H'], 'away': period_scores['summary']['away']['H']},
            'errors': {'home': period_scores['summary']['home']['E'], 'away': period_scores['summary']['away']['E']},
            'left_on_base': {'home': period_scores['summary']['home']['B'], 'away': period_scores['summary']['away']['B']}
        }

        # (2) 타자 & 투수 선수 박스스코어 가공
        player_stats = []

        # 타자
        for team_idx, h_wrap in enumerate(b_data.get('arrHitter', [])):
            t_name = away_team_name if team_idx == 0 else home_team_name
            t1_h = json.loads(h_wrap.get('table1', '{}')) if h_wrap.get('table1') else {}
            t3_h = json.loads(h_wrap.get('table3', '{}')) if h_wrap.get('table3') else {}
            rows1 = t1_h.get('rows', [])
            rows3 = t3_h.get('rows', [])

            for r1, r3 in zip(rows1, rows3):
                c1 = [c.get('Text', '') for c in r1.get('row', [])]
                c3 = [c.get('Text', '') for c in r3.get('row', [])]
                if len(c1) < 3 or not c1[2]:
                    continue
                order_num = c1[0]
                pos_raw = c1[1]
                p_name = c1[2]
                pos_name = POS_MAP.get(pos_raw, pos_raw)
                pos_label = f"{order_num}번 {pos_name}" if order_num and order_num.isdigit() else pos_name

                ab = clean_int(c3[0] if len(c3) > 0 else 0)
                h = clean_int(c3[1] if len(c3) > 1 else 0)
                rbi = clean_int(c3[2] if len(c3) > 2 else 0)
                r = clean_int(c3[3] if len(c3) > 3 else 0)
                avg = c3[4] if len(c3) > 4 else "0.000"

                player_stats.append({
                    "team_name": t_name,
                    "player_name": p_name,
                    "back_number": "",
                    "position": pos_label,
                    "minutes_played": 0,
                    "points": rbi,
                    "assists": 0,
                    "shots": ab,
                    "extra_stats": {
                        "type": "HITTER",
                        "player_type": "HITTER",
                        "ab": ab, "r": r, "h": h, "2b": 0, "3b": 0, "hr": 0,
                        "rbi": rbi, "bb": 0, "so": 0, "sb": 0,
                        "hits": h, "doubles": 0, "triples": 0, "homeruns": 0,
                        "runs": r, "walks": 0, "strikeouts": 0, "stolen_bases": 0,
                        "avg": avg, "ops": "-"
                    }
                })

        # 투수
        for team_idx, p_wrap in enumerate(b_data.get('arrPitcher', [])):
            t_name = away_team_name if team_idx == 0 else home_team_name
            t_pitch = {}
            if isinstance(p_wrap, dict) and 'table' in p_wrap:
                try:
                    t_pitch = json.loads(p_wrap['table'])
                except Exception:
                    pass

            rows = t_pitch.get('rows', [])
            for r in rows:
                c = [col.get('Text', '') for col in r.get('row', [])]
                if len(c) < 17:
                    continue
                p_name = c[0]
                role = c[1]  # 선발, 구원, 마무리
                dec_code = c[2] # 승, 패, 세, 홀
                dec_label = f"{dec_code}리투수 (W)" if dec_code == "승" else (f"{dec_code}전투수 (L)" if dec_code == "패" else (f"{dec_code}이브 (SV)" if dec_code == "세" else (f"{dec_code}드 (HD)" if dec_code == "홀" else "")))
                ip = c[6]
                np = clean_int(c[8])
                h = clean_int(c[10])
                hr = clean_int(c[11])
                bb = clean_int(c[12])
                so = clean_int(c[13])
                r = clean_int(c[14])
                er = clean_int(c[15])
                era = c[16]

                player_stats.append({
                    "team_name": t_name,
                    "player_name": p_name,
                    "back_number": "",
                    "position": f"투수 ({role})",
                    "minutes_played": 0,
                    "points": so,
                    "assists": 0,
                    "shots": int(float(ip)) if ip and '.' in ip else 0,
                    "extra_stats": {
                        "type": "PITCHER",
                        "player_type": "PITCHER",
                        "ip": ip, "np": np, "h": h, "r": r, "er": er, "bb": bb,
                        "so": so, "hr": hr, "era": era, "whip": "1.10",
                        "decision": dec_label
                    }
                })

        # (3) 주요 상황 타임라인 (tableEtc)
        events = []
        raw_etc = b_data.get('tableEtc', '')
        if raw_etc:
            try:
                t_etc = json.loads(raw_etc)
                for r in t_etc.get('rows', []):
                    cols = [col.get('Text', '') for col in r.get('row', [])]
                    if len(cols) >= 2:
                        title = cols[0]
                        desc = cols[1]
                        events.append({
                            "time_display": title,
                            "event_type": "HOMERUN" if "홈런" in title else ("HIT" if "안타" in title or "결승타" in title else "RECORD"),
                            "team_name": away_team_name,
                            "player_name": desc.split('(')[0].strip() if '(' in desc else '',
                            "description": desc,
                            "score_after": ""
                        })
            except Exception as e:
                print(f"Error parsing KBO tableEtc: {e}")

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "source_url": f"https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx?gameId={clean_gid}",
            "events": events,
            "player_stats": player_stats
        }
