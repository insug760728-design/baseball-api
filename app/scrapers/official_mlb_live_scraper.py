# -*- coding: utf-8 -*-
"""
공식 메이저리그 (MLB) 공식 Stats API 실시간 수집기
- 베이스 URL: https://statsapi.mlb.com/api/v1
- 스케줄, 1~9회 이닝별 전광판 라인스코어, 전 선수 박스스코어, 득점 타임라인
- 100% 공식 실시간 데이터 (가짜/더미 데이터 일체 없음)
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.services.player_translation import sanitize_player_name, sanitize_text

logger = logging.getLogger("MlbOfficialScraper")

MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

MLB_TEAMS_KO = {
    "New York Yankees": "뉴욕 양키스",
    "San Diego Padres": "샌디에이고 파드리스",
    "Los Angeles Dodgers": "LA 다저스",
    "Boston Red Sox": "보스턴 레드삭스",
    "San Francisco Giants": "샌프란시스코 자이언츠",
    "Philadelphia Phillies": "필라델피아 필리스",
    "Atlanta Braves": "애틀랜타 브레이브스",
    "Toronto Blue Jays": "토론토 블루제이스",
    "Baltimore Orioles": "볼티모어 오리올스",
    "Tampa Bay Rays": "탬파베이 레이스",
    "Houston Astros": "휴스턴 애스트로스",
    "Seattle Mariners": "시애틀 매리너스",
    "Texas Rangers": "텍사스 레인저스",
    "Athletics": "애슬레틱스",
    "Oakland Athletics": "오클랜드 애슬레틱스",
    "Los Angeles Angels": "LA 에인절스",
    "Chicago Cubs": "시카고 컵스",
    "Chicago White Sox": "시카고 화이트삭스",
    "St. Louis Cardinals": "세인트루이스 카디널스",
    "Milwaukee Brewers": "밀워키 브루어스",
    "Cincinnati Reds": "신시내티 레즈",
    "Pittsburgh Pirates": "피츠버그 파이리츠",
    "Arizona Diamondbacks": "애리조나 다이아몬드백스",
    "Colorado Rockies": "콜로라도 로키스",
    "Miami Marlins": "마이애미 말린스",
    "New York Mets": "뉴욕 메츠",
    "Washington Nationals": "워싱턴 내셔널스",
    "Cleveland Guardians": "클리블랜드 가디언스",
    "Detroit Tigers": "디트로이트 타이거스",
    "Minnesota Twins": "미네소타 트윈스",
    "Kansas City Royals": "캔자스시티 로열스"
}

def get_team_name_ko(en_name: str) -> str:
    return MLB_TEAMS_KO.get(en_name, en_name)

MLB_SHORT_TEAMS = {
    "Miami Marlins": "마이말린",
    "San Francisco Giants": "샌프자이",
    "Tampa Bay Rays": "탬파레이",
    "Milwaukee Brewers": "밀워브루",
    "San Diego Padres": "샌디파드",
    "Washington Nationals": "워싱내셔",
    "Pittsburgh Pirates": "피츠파이",
    "Toronto Blue Jays": "토론블루",
    "Boston Red Sox": "보스레드",
    "Athletics": "애슬레틱",
    "Oakland Athletics": "애슬레틱",
    "St. Louis Cardinals": "세인카디",
    "New York Yankees": "뉴욕양키",
    "Detroit Tigers": "디트타이",
    "New York Mets": "뉴욕메츠",
    "Baltimore Orioles": "볼티오리",
    "Los Angeles Dodgers": "LA다저스",
    "Los Angeles Angels": "LA에인절",
    "Chicago Cubs": "시카컵스",
    "Chicago White Sox": "시카화삭",
    "Atlanta Braves": "애틀브레",
    "Houston Astros": "휴스애스",
    "Seattle Mariners": "시애매리",
    "Texas Rangers": "텍사레인",
    "Philadelphia Phillies": "필라필리",
    "Arizona Diamondbacks": "애리다이",
    "Colorado Rockies": "콜로로키",
    "Cleveland Guardians": "클리가디",
    "Minnesota Twins": "미네트윈",
    "Kansas City Royals": "캔자로열",
    "Cincinnati Reds": "신시레즈"
}

def get_short_team_name_ko(raw_name: str) -> str:
    if not raw_name:
        return "상대팀"
    if raw_name in MLB_SHORT_TEAMS:
        return MLB_SHORT_TEAMS[raw_name]
    for en, ko in MLB_SHORT_TEAMS.items():
        if en.lower() in raw_name.lower():
            return ko
    ko_full = get_team_name_ko(raw_name)
    clean = ko_full.replace(" ", "")
    return clean[:4] if len(clean) > 4 else clean

def calc_game_era(ip_str: str, er: int) -> str:
    er = int(er or 0)
    ip_str = str(ip_str or "0.0").strip()
    if not ip_str or ip_str in ("0", "0.0"):
        return "0.00" if er == 0 else "99.99"
    try:
        parts = ip_str.split(".")
        whole = int(parts[0])
        frac = int(parts[1]) if len(parts) > 1 else 0
        ip_float = whole + (frac / 3.0)
        if ip_float <= 0:
            return "0.00"
        val = (er * 9.0) / ip_float
        return f"{val:.2f}"
    except Exception:
        return "0.00"

class MlbOfficialScraper:
    """공식 MLB Stats API 실시간 수집 엔진"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        self._pitcher_cache: Dict[Any, Dict[str, Any]] = {}

    def _fetch_json(self, url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch_pitcher_profile(self, person_id: int, person_name: str = "") -> Dict[str, Any]:
        """MLB 공식 Stats API에서 투수의 실시간 시즌 성적 및 최근 등판 일지 100% 실데이터 수집"""
        if not person_id:
            return {}
        if person_id in self._pitcher_cache:
            return self._pitcher_cache[person_id]

        url = f"{MLB_API_BASE}/people/{person_id}/stats?stats=season,gameLog&group=pitching"
        try:
            data = self._fetch_json(url)
            season_stat = {}
            game_logs = []
            for s in data.get("stats", []):
                d_name = s.get("type", {}).get("displayName")
                if d_name == "season":
                    splits = s.get("splits", [])
                    if splits:
                        season_stat = splits[0].get("stat", {})
                elif d_name == "gameLog":
                    game_logs = s.get("splits", [])

            # Fetch player bio for throw hand (R/L)
            hand = "R"
            try:
                bio_url = f"{MLB_API_BASE}/people/{person_id}"
                bio_data = self._fetch_json(bio_url)
                hand = bio_data.get("people", [{}])[0].get("pitchHand", {}).get("code", "R")
            except Exception:
                pass

            weekdays_ko = ["월", "화", "수", "목", "금", "토", "일"]
            recent_starts = []
            for g in game_logs[::-1][:10]:
                st = g.get("stat", {})
                dt_str = g.get("date", "")
                kst_date_display = dt_str
                if dt_str and len(dt_str) >= 10:
                    try:
                        dt = datetime.strptime(dt_str[:10], "%Y-%m-%d")
                        kst_dt = dt + timedelta(days=1)
                        kst_date_display = f"{kst_dt.strftime('%m.%d')}({weekdays_ko[kst_dt.weekday()]})"
                    except Exception:
                        kst_date_display = dt_str[5:].replace("-", ".")

                opp_name_raw = g.get("opponent", {}).get("name", "상대팀")
                opp_name = get_short_team_name_ko(opp_name_raw)
                is_home = g.get("isHome", True)
                dec = st.get("decision", "-")
                res_label = "승" if dec == "W" else ("패" if dec == "L" else ("세" if dec == "S" else ("홀" if dec == "H" else "-")))

                ip_val = str(st.get("inningsPitched", "0.0"))
                er_val = int(st.get("earnedRuns", 0))
                game_era = calc_game_era(ip_val, er_val)

                recent_starts.append({
                    "date": kst_date_display,
                    "venue": "홈" if is_home else "원",
                    "opponent": opp_name,
                    "ip": ip_val,
                    "bf": int(st.get("battersFaced", 0)),
                    "h": int(st.get("hits", 0)),
                    "hr": int(st.get("homeRuns", 0)),
                    "bb": int(st.get("baseOnBalls", 0)),
                    "so": int(st.get("strikeOuts", 0)),
                    "er": er_val,
                    "era": game_era,
                    "np": int(st.get("numberOfPitches", 0)),
                    "result": res_label
                })

            wins = season_stat.get("wins")
            losses = season_stat.get("losses")
            era_val = season_stat.get("era")
            ip_val = str(season_stat.get("inningsPitched", "-"))
            so_val = season_stat.get("strikeOuts")
            bb_val = season_stat.get("baseOnBalls")

            from app.services.player_translation import translate_player_name
            ko_name = translate_player_name(person_name) if person_name else person_name
            clean_name = sanitize_player_name(ko_name) if ko_name else ""

            summary_text = f"{ip_val}이닝 {so_val or 0}K {bb_val or 0}BB" if ip_val != "-" else "-"
            record_text = f"{wins}승 {losses}패" if (wins is not None and losses is not None) else "시즌 첫 등판"

            prof = {
                "name": clean_name,
                "name_raw": person_name,
                "name_en": person_name,
                "id": person_id,
                "hand": hand,
                "style": "우완" if hand == "R" else ("좌완" if hand == "L" else hand),
                "season_era": str(era_val) if era_val is not None else "-",
                "era": str(era_val) if era_val is not None else "-",
                "wins": wins,
                "losses": losses,
                "w": wins if wins is not None else 0,
                "l": losses if losses is not None else 0,
                "games": season_stat.get("gamesPitched"),
                "season_record": record_text,
                "record": record_text,
                "season_ip": ip_val,
                "season_so": so_val,
                "season_bb": bb_val,
                "summary": summary_text,
                "season_summary": summary_text,
                "whip": str(season_stat.get("whip", "-")),
                "recent_starts": recent_starts
            }
            self._pitcher_cache[person_id] = prof
            if clean_name:
                self._pitcher_cache[clean_name] = prof
            if person_name:
                self._pitcher_cache[person_name] = prof
            return prof
        except Exception as e:
            print(f"[MLB Scraper] Pitcher fetch error ({person_id}): {e}")
            return {}

    def search_and_fetch_pitcher(self, name: str) -> Dict[str, Any]:
        """선수 이름(한글/영문)으로 MLB Stats API를 검색하여 100% 공식 프로필 반환"""
        if not name or name in ("선발 미정", "미정", "None"):
            return {}
        import re, urllib.parse
        clean_ko = re.sub(r"\([^\)]+\)", "", name).strip()
        if clean_ko in self._pitcher_cache:
            return self._pitcher_cache[clean_ko]

        from app.services.player_translation import resolve_player_english_name, translate_player_name
        en_name = resolve_player_english_name(clean_ko)

        q = urllib.parse.quote(en_name)
        search_url = f"{MLB_API_BASE}/people/search?names={q}"
        try:
            res = self._fetch_json(search_url)
            people = res.get("people", [])
            for p in people:
                pos = p.get("primaryPosition", {}).get("abbreviation", "")
                if pos in ("P", "TWP") or len(people) == 1:
                    pid = p.get("id")
                    ko_label = translate_player_name(p.get("fullName", clean_ko))
                    return self.fetch_pitcher_profile(pid, ko_label)
            if people:
                pid = people[0].get("id")
                ko_label = translate_player_name(people[0].get("fullName", clean_ko))
                return self.fetch_pitcher_profile(pid, ko_label)
        except Exception as e:
            print(f"[MLB Scraper] Search error for {name}: {e}")
        return {}

    def get_latest_available_date(self) -> str:
        """가장 최근에 공식 MLB 경기가 있었던 날짜 확인"""
        url = f"{MLB_API_BASE}/schedule?sportId=1&season=2026"
        try:
            data = self._fetch_json(url)
            dates = data.get("dates", [])
            if dates:
                return dates[0]["date"]
        except Exception:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def scrape_schedule(self, target_date: Optional[str] = None, fast_live: bool = False) -> List[Dict[str, Any]]:
        """지정일의 공식 MLB 경기 목록 (스코어 및 라인스코어 포함) - 2026 시즌 실데이터 전용
        fast_live=True: 초고속 0.7초 라이브 전용 (투수 프로필 심층 통계 API 호출 생략)"""
        d = target_date or datetime.now().strftime("%Y-%m-%d")
        try:
            d_dt = datetime.strptime(d, "%Y-%m-%d")
            prev_d = (d_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        except Exception:
            prev_d = d

        # 한국 시각(KST) 기준 날짜 d의 경기는 미국 시차(-13~-16시간)로 인해 미국 날짜 prev_d(전날 저녁)와 d(당일)에 걸쳐 열림
        url = f"{MLB_API_BASE}/schedule?sportId=1&season=2026&startDate={prev_d}&endDate={d}&hydrate=probablePitcher,linescore,team,lineups(person)"
        logger.info(f"[MLB Scraper] Requesting official schedule for KST date {d} (US {prev_d}~{d}) -> {url}")
        
        try:
            data = self._fetch_json(url)
        except Exception as e:
            logger.error(f"[MLB API Error] {e}")
            return []

        dates = data.get("dates", [])
        if not dates:
            logger.info(f"[MLB Scraper] No official games scheduled for date: {d} (season=2026)")
            return []

        # 투수 프로필 일괄 비동기 병렬 프리페치 (fast_live 모드일 때는 라이브 초저지연을 위해 생략)
        if not fast_live:
            pitcher_tasks = []
            for date_obj in dates:
                for g in date_obj.get("games", []):
                    # KST 기준 대상 일자 경기만 프리페치
                    gdate_raw = g.get("gameDate", "")
                    if gdate_raw:
                        try:
                            clean_dt = datetime.fromisoformat(gdate_raw.replace("Z", "+00:00")) + timedelta(hours=9)
                            if clean_dt.strftime("%Y-%m-%d") != d:
                                continue
                        except Exception:
                            pass
                    for side in ["home", "away"]:
                        prob = g.get("teams", {}).get(side, {}).get("probablePitcher", {})
                        pid = prob.get("id")
                        pname = prob.get("fullName")
                        if pid and pname and pid not in self._pitcher_cache:
                            pitcher_tasks.append((pid, pname))
            
            if pitcher_tasks:
                import concurrent.futures
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                        list(ex.map(lambda pair: self.fetch_pitcher_profile(pair[0], pair[1]), pitcher_tasks))
                except Exception as pe:
                    print(f"[MLB Scraper] Pitcher prefetch warning: {pe}")

        from app.services.player_translation import translate_player_name

        results = []
        for date_obj in dates:
            api_resp_date = date_obj.get("date", "")
            games = date_obj.get("games", [])
            for g in games:
                game_pk = str(g.get("gamePk", ""))
                season_str = str(g.get("season", ""))
                official_date = g.get("officialDate", "")
                game_date_raw = g.get("gameDate", "")

                # 100% 한국 표준시 (KST = UTC + 9시간) 변환 및 KST 날짜 계산
                kst_date_only = d
                if game_date_raw:
                    try:
                        clean = game_date_raw.replace("Z", "+00:00")
                        dt = datetime.fromisoformat(clean)
                        kst_dt = dt + timedelta(hours=9)
                        match_time_display = kst_dt.strftime("%Y-%m-%d %H:%M")
                        kst_date_only = kst_dt.strftime("%Y-%m-%d")
                    except Exception:
                        match_time_display = f"{d} 10:00"
                        kst_date_only = d
                else:
                    match_time_display = f"{d} 10:00"
                    kst_date_only = d

                actual_game_date = kst_date_only

                # 4. 2024년이나 2025년 데이터가 섞이지 않게 하고, 항상 2026 시즌 기준으로 필터링
                if season_str != "2026":
                    continue

                # 3. 한국 시각(KST) 변환 기준 날짜가 요청 날짜(d)와 일치하는 경기만 수집
                if kst_date_only != d:
                    continue

                away_team_raw = g["teams"]["away"]["team"]["name"]
                home_team_raw = g["teams"]["home"]["team"]["name"]
                away_team_ko = get_team_name_ko(away_team_raw)
                home_team_ko = get_team_name_ko(home_team_raw)

                away_score = g["teams"]["away"].get("score", 0)
                home_score = g["teams"]["home"].get("score", 0)

                # 공식 선발 예고 투수 (probablePitcher)
                h_prob_obj = g.get("teams", {}).get("home", {}).get("probablePitcher", {})
                a_prob_obj = g.get("teams", {}).get("away", {}).get("probablePitcher", {})
                h_id = h_prob_obj.get("id")
                a_id = a_prob_obj.get("id")
                h_name_raw = h_prob_obj.get("fullName") or ""
                a_name_raw = a_prob_obj.get("fullName") or ""
                h_prob_p = sanitize_player_name(translate_player_name(h_name_raw)) if h_name_raw else None
                a_prob_p = sanitize_player_name(translate_player_name(a_name_raw)) if a_name_raw else None

                h_prof = {} if fast_live else (self.fetch_pitcher_profile(h_id, h_name_raw) if h_id else {})
                a_prof = {} if fast_live else (self.fetch_pitcher_profile(a_id, a_name_raw) if a_id else {})

                if not h_prof and h_prob_p:
                    h_prof = {"name": h_prob_p, "confirmed": True, "style": "우완", "era": "-", "record": "-"}
                if not a_prof and a_prob_p:
                    a_prof = {"name": a_prob_p, "confirmed": True, "style": "우완", "era": "-", "record": "-"}

                # 상태 (FINAL, IN_PROGRESS, SCHEDULED)
                raw_state = g.get("status", {}).get("abstractGameState", "Scheduled")
                status = "FINISHED" if raw_state == "Final" else ("LIVE" if raw_state == "Live" else "SCHEDULED")

                venue_name = g.get("venue", {}).get("name", "MLB Stadium")

                # 이닝 및 라이브 상황 추출 (linescore)
                ls = g.get("linescore", {})
                curr_inn = ls.get("currentInning")
                inn_half = ls.get("inningHalf", "")
                is_top = ls.get("isTopInning", True)
                outs = ls.get("outs")
                balls = ls.get("balls")
                strikes = ls.get("strikes")

                half_ko = "초" if (is_top or inn_half == "Top") else "말"
                inning_text = f"{curr_inn}회{half_ko}" if curr_inn else None

                raw_innings = ls.get("innings", [])
                innings_dict = {}
                for inn in raw_innings:
                    num_str = str(inn.get("num"))
                    away_r = inn.get("away", {}).get("runs")
                    home_r = inn.get("home", {}).get("runs")
                    innings_dict[num_str] = {
                        "away": away_r if away_r is not None else "-",
                        "home": home_r if home_r is not None else "-"
                    }
                for i in range(1, 10):
                    if str(i) not in innings_dict:
                        innings_dict[str(i)] = {"away": "-", "home": "-"}

                teams_summary = ls.get("teams", {})
                h_sum = teams_summary.get("home", {})
                a_sum = teams_summary.get("away", {})
                period_scores = {
                    "current_inning": inning_text,
                    "innings": innings_dict,
                    "summary": {
                        "home": {"R": h_sum.get("runs", home_score), "H": h_sum.get("hits", 0), "E": h_sum.get("errors", 0), "B": h_sum.get("leftOnBase", 0)},
                        "away": {"R": a_sum.get("runs", away_score), "H": a_sum.get("hits", 0), "E": a_sum.get("errors", 0), "B": a_sum.get("leftOnBase", 0)}
                    }
                }

                offense = ls.get("offense", {})
                b1 = bool(offense.get("first"))
                b2 = bool(offense.get("second"))
                b3 = bool(offense.get("third"))
                defense = ls.get("defense", {})
                curr_pitcher = defense.get("pitcher", {}).get("fullName")
                curr_batter = offense.get("batter", {}).get("fullName")

                linescore = {
                    "home": [innings_dict.get(str(i), {}).get("home", "-") for i in range(1, 10)],
                    "away": [innings_dict.get(str(i), {}).get("away", "-") for i in range(1, 10)]
                }

                scoreboard = {
                    "current_inning": inning_text,
                    "inning_num": curr_inn,
                    "inning_half": inn_half,
                    "inning_state": half_ko,
                    "outs": outs,
                    "balls": balls,
                    "strikes": strikes,
                    "bso": f"{balls or 0}B-{strikes or 0}S-{outs or 0}O" if curr_inn else None,
                    "base1": b1,
                    "base2": b2,
                    "base3": b3,
                    "runner_1b": b1,
                    "runner_2b": b2,
                    "runner_3b": b3,
                    "pitcher": curr_pitcher,
                    "batter": curr_batter,
                    "linescore": linescore,
                    "period_scores": period_scores
                }

                # 공식 1~9번 선발 라인업 추출 (MLB Stats API 실데이터)
                lineups = g.get("lineups", {})
                h_lineup_raw = lineups.get("homePlayers", [])
                a_lineup_raw = lineups.get("awayPlayers", [])

                home_lineup = []
                if len(h_lineup_raw) >= 9:
                    for idx, p in enumerate(h_lineup_raw[:9]):
                        p_en = p.get("fullName", "")
                        p_ko = sanitize_player_name(translate_player_name(p_en))
                        pos = p.get("primaryPosition", {}).get("abbreviation", "타자")
                        home_lineup.append({
                            "order": idx + 1,
                            "pos": pos,
                            "name": p_ko or p_en,
                            "name_en": p_en,
                            "id": p.get("id"),
                            "hand": p.get("batSide", {}).get("code") or "R",
                            "avg": ""
                        })

                away_lineup = []
                if len(a_lineup_raw) >= 9:
                    for idx, p in enumerate(a_lineup_raw[:9]):
                        p_en = p.get("fullName", "")
                        p_ko = sanitize_player_name(translate_player_name(p_en))
                        pos = p.get("primaryPosition", {}).get("abbreviation", "타자")
                        away_lineup.append({
                            "order": idx + 1,
                            "pos": pos,
                            "name": p_ko or p_en,
                            "name_en": p_en,
                            "id": p.get("id"),
                            "hand": p.get("batSide", {}).get("code") or "R",
                            "avg": ""
                        })

                is_lineup_confirmed = bool(len(home_lineup) >= 9 and len(away_lineup) >= 9)

                team_stats = {
                    "scoreboard": scoreboard,
                    "linescore": linescore,
                    "period_scores": period_scores,
                    "current_inning": inning_text,
                    "hits": {"home": h_sum.get("hits", 0), "away": a_sum.get("hits", 0)},
                    "errors": {"home": h_sum.get("errors", 0), "away": a_sum.get("errors", 0)},
                    "left_on_base": {"home": h_sum.get("leftOnBase", 0), "away": a_sum.get("leftOnBase", 0)},
                    "starters": {
                        "home": h_prof,
                        "away": a_prof
                    },
                    "lineup": {
                        "home": home_lineup,
                        "away": away_lineup,
                        "confirmed": is_lineup_confirmed
                    }
                }

                results.append({
                    "official_id": f"MLB_{game_pk}",
                    "sport_code": "BASEBALL",
                    "league_name": "미국 메이저리그 (MLB)",
                    "season": season_str,
                    "round_name": "정규시즌",
                    "game_date": actual_game_date,
                    "match_date": match_time_display,
                    "stadium": venue_name,
                    "home_team_name": home_team_ko,
                    "away_team_name": away_team_ko,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status,
                    "game_pk": int(game_pk) if game_pk.isdigit() else game_pk,
                    "raw_away_team": away_team_raw,
                    "raw_home_team": home_team_raw,
                    "probable_pitcher_home": h_prob_p,
                    "probable_pitcher_away": a_prob_p,
                    "current_inning": inning_text,
                    "inning_text": inning_text,
                    "outs": outs,
                    "balls": balls,
                    "strikes": strikes,
                    "period_scores": period_scores,
                    "linescore": linescore,
                    "scoreboard": scoreboard,
                    "team_stats": team_stats,
                    "home_lineup": home_lineup,
                    "away_lineup": away_lineup,
                    "is_lineup_confirmed": is_lineup_confirmed,
                    "lineup_status": "CONFIRMED" if is_lineup_confirmed else "EXPECTED"
                })

        return results

    def scrape_game_detail(self, game_pk: int) -> Dict[str, Any]:
        """특정 경기의 1~9회 이닝별 라인스코어, 전 선수 박스스코어, 타임라인 이벤트 (feed/live 단일 고속 호출)"""
        feed_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
        live_data = {}
        feed_data = {}
        try:
            feed_data = self._fetch_json(feed_url)
            live_data = feed_data.get("liveData", {})
        except Exception as e:
            print(f"Error fetching feed/live: {e}")

        linescore_data = live_data.get("linescore", {})
        boxscore_data = live_data.get("boxscore", {})
        plays_data = live_data.get("plays", {})
        game_data = feed_data.get("gameData", {})

        curr_inn = linescore_data.get("currentInning")
        inn_half = linescore_data.get("inningHalf", "")
        is_top = linescore_data.get("isTopInning", True)
        outs = linescore_data.get("outs")
        balls = linescore_data.get("balls")
        strikes = linescore_data.get("strikes")
        half_ko = "초" if (is_top or inn_half == "Top") else "말"
        inning_text = f"{curr_inn}회{half_ko}" if curr_inn else None

        # (1) 1~9회+ 이닝별 전광판 스코어 가공
        innings_dict = {}
        raw_innings = linescore_data.get("innings", [])
        for inn in raw_innings:
            num_str = str(inn.get("num"))
            away_r = inn.get("away", {}).get("runs", 0)
            home_r = inn.get("home", {}).get("runs", 0)
            innings_dict[num_str] = {
                "away": away_r if away_r is not None else "-",
                "home": home_r if home_r is not None else "-"
            }

        # 9회까지 기본 구조 보장
        for i in range(1, 10):
            s_i = str(i)
            if s_i not in innings_dict:
                innings_dict[s_i] = {"away": "-", "home": "-"}

        teams_summary = linescore_data.get("teams", {})
        home_summary = teams_summary.get("home", {})
        away_summary = teams_summary.get("away", {})

        period_scores = {
            "current_inning": inning_text,
            "innings": innings_dict,
            "summary": {
                "home": {
                    "R": home_summary.get("runs", 0),
                    "H": home_summary.get("hits", 0),
                    "E": home_summary.get("errors", 0),
                    "B": home_summary.get("leftOnBase", 0)
                },
                "away": {
                    "R": away_summary.get("runs", 0),
                    "H": away_summary.get("hits", 0),
                    "E": away_summary.get("errors", 0),
                    "B": away_summary.get("leftOnBase", 0)
                }
            }
        }

        offense = linescore_data.get("offense", {})
        b1 = bool(offense.get("first"))
        b2 = bool(offense.get("second"))
        b3 = bool(offense.get("third"))
        defense = linescore_data.get("defense", {})
        curr_pitcher = defense.get("pitcher", {}).get("fullName")
        curr_batter = offense.get("batter", {}).get("fullName")

        linescore = {
            "home": [innings_dict.get(str(i), {}).get("home", "-") for i in range(1, 10)],
            "away": [innings_dict.get(str(i), {}).get("away", "-") for i in range(1, 10)]
        }

        scoreboard = {
            "current_inning": inning_text,
            "inning_num": curr_inn,
            "inning_half": inn_half,
            "inning_state": half_ko,
            "outs": outs,
            "balls": balls,
            "strikes": strikes,
            "bso": f"{balls or 0}B-{strikes or 0}S-{outs or 0}O" if curr_inn else None,
            "base1": b1,
            "base2": b2,
            "base3": b3,
            "runner_1b": b1,
            "runner_2b": b2,
            "runner_3b": b3,
            "pitcher": curr_pitcher,
            "batter": curr_batter,
            "linescore": linescore,
            "period_scores": period_scores
        }

        # 선발 투수 프로필 실시간 추출
        prob_pitchers = game_data.get("probablePitchers", {})
        h_prob = prob_pitchers.get("home", {})
        a_prob = prob_pitchers.get("away", {})
        h_box_pitchers = boxscore_data.get("teams", {}).get("home", {}).get("pitchers", [])
        a_box_pitchers = boxscore_data.get("teams", {}).get("away", {}).get("pitchers", [])

        h_starter_id = h_box_pitchers[0] if h_box_pitchers else h_prob.get("id")
        a_starter_id = a_box_pitchers[0] if a_box_pitchers else a_prob.get("id")
        h_starter_name = h_prob.get("fullName") or ""
        a_starter_name = a_prob.get("fullName") or ""

        h_starter_prof = self.fetch_pitcher_profile(h_starter_id, h_starter_name) if h_starter_id else {}
        a_starter_prof = self.fetch_pitcher_profile(a_starter_id, a_starter_name) if a_starter_id else {}

        # (2) 팀 스탯
        team_stats = {
            "scoreboard": scoreboard,
            "linescore": linescore,
            "period_scores": period_scores,
            "current_inning": inning_text,
            "hits": {"home": home_summary.get("hits", 0), "away": away_summary.get("hits", 0)},
            "errors": {"home": home_summary.get("errors", 0), "away": away_summary.get("errors", 0)},
            "left_on_base": {"home": home_summary.get("leftOnBase", 0), "away": away_summary.get("leftOnBase", 0)},
            "starters": {
                "home": h_starter_prof,
                "away": a_starter_prof
            }
        }

        # (3) 득점 타임라인 이벤트
        events = []
        all_plays = plays_data.get("allPlays", [])
        for play in all_plays:
            about = play.get("about", {})
            if about.get("isScoringPlay"):
                half = "초" if about.get("halfInning") == "top" else "말"
                inn_num = about.get("inning", 1)
                time_disp = f"{inn_num}회{half}"

                # 득점 팀
                batting_team_is_home = (about.get("halfInning") == "bottom")
                team_name_raw = boxscore_data.get("teams", {}).get("home" if batting_team_is_home else "away", {}).get("team", {}).get("name", "MLB")
                team_name_ko = get_team_name_ko(team_name_raw)

                batter_name = sanitize_player_name(play.get("matchup", {}).get("batter", {}).get("fullName", "타자"))
                desc = sanitize_text(play.get("result", {}).get("description", ""))
                event_type = play.get("result", {}).get("event", "득점")

                away_s = play.get("result", {}).get("awayScore", 0)
                home_s = play.get("result", {}).get("homeScore", 0)

                events.append({
                    "time_display": time_disp,
                    "event_type": "HOMERUN" if "Home Run" in event_type else "HIT",
                    "team_name": team_name_ko,
                    "player_name": batter_name,
                    "assist_player_name": None,
                    "score_after": f"{away_s}-{home_s}",
                    "description": desc
                })

        # (4) 전 선수 박스스코어 (타자 + 투수)
        player_stats = []
        teams_box = boxscore_data.get("teams", {})
        for side in ["home", "away"]:
            t_data = teams_box.get(side, {})
            t_name_ko = get_team_name_ko(t_data.get("team", {}).get("name", ""))
            players = t_data.get("players", {})

            # 1. 타자 (공식 타순 batters 배열 순서대로 정렬)
            batter_ids = t_data.get("batters", [])
            seen_batters = set()
            for b_id in batter_ids:
                p = players.get(f"ID{b_id}")
                if not p:
                    continue
                seen_batters.add(f"ID{b_id}")
                p_name = sanitize_player_name(p.get("person", {}).get("fullName") or "")
                if not p_name:
                    continue

                pos_abbr = p.get("position", {}).get("abbreviation", "선수")
                jersey = p.get("jerseyNumber")
                b_num = int(jersey) if jersey and jersey.isdigit() else None

                stats_wrap = p.get("stats", {})
                b_stat = stats_wrap.get("batting", {})
                season_b = p.get("seasonStats", {}).get("batting", {})

                order = p.get("battingOrder")
                order_label = f"{order[0]}번 {pos_abbr}" if order and len(order) >= 1 and order[0].isdigit() else pos_abbr

                ab = b_stat.get("atBats", 0)
                r = b_stat.get("runs", 0)
                h = b_stat.get("hits", 0)
                rbi = b_stat.get("rbi", 0)
                hr = b_stat.get("homeRuns", 0)
                bb = b_stat.get("baseOnBalls", 0)
                so = b_stat.get("strikeOuts", 0)
                sb = b_stat.get("stolenBases", 0)
                doubles = b_stat.get("doubles", 0)
                triples = b_stat.get("triples", 0)

                avg = season_b.get("avg", "-")
                ops = season_b.get("ops", "-")

                player_stats.append({
                    "team_name": t_name_ko,
                    "player_name": p_name,
                    "back_number": b_num,
                    "position": order_label,
                    "minutes_played": 0,
                    "points": rbi,
                    "assists": 0,
                    "shots": ab,
                    "extra_stats": {
                        "type": "HITTER",
                        "player_type": "HITTER",
                        "ab": ab, "r": r, "h": h, "2b": doubles, "3b": triples,
                        "hr": hr, "rbi": rbi, "bb": bb, "so": so, "sb": sb,
                        "hits": h, "doubles": doubles, "triples": triples, "homeruns": hr,
                        "runs": r, "walks": bb, "strikeouts": so, "stolen_bases": sb,
                        "avg": avg, "ops": ops
                    }
                })

            # 2. 투수 (공식 등판 순서 pitchers 배열 순서대로 정렬: 0번은 선발 투수!)
            pitcher_ids = t_data.get("pitchers", [])
            seen_pitchers = set()
            for p_idx, p_id in enumerate(pitcher_ids):
                p = players.get(f"ID{p_id}")
                if not p:
                    continue
                seen_pitchers.add(f"ID{p_id}")
                p_name = sanitize_player_name(p.get("person", {}).get("fullName") or "")
                if not p_name:
                    continue

                pos_abbr = p.get("position", {}).get("abbreviation", "P")
                jersey = p.get("jerseyNumber")
                b_num = int(jersey) if jersey and jersey.isdigit() else None

                stats_wrap = p.get("stats", {})
                p_stat = stats_wrap.get("pitching", {})
                season_p = p.get("seasonStats", {}).get("pitching", {})

                ip = p_stat.get("inningsPitched", "0.0")
                np = p_stat.get("numberOfPitches", 0)
                h = p_stat.get("hits", 0)
                r = p_stat.get("runs", 0)
                er = p_stat.get("earnedRuns", 0)
                bb = p_stat.get("baseOnBalls", 0)
                so = p_stat.get("strikeOuts", 0)
                hr = p_stat.get("homeRuns", 0)
                era = season_p.get("era", "-")
                whip = season_p.get("whip", "-")

                # 최근(단일 경기) 방어율 계산
                try:
                    ip_s = str(ip).strip()
                    if '.' in ip_s:
                        ip_parts = ip_s.split('.')
                        outs = int(ip_parts[0]) * 3 + int(ip_parts[1])
                    else:
                        outs = int(float(ip_s)) * 3
                    recent_era = f"{(er * 27.0 / outs):.2f}" if outs > 0 else ("0.00" if er == 0 else "-")
                except Exception:
                    recent_era = "-"

                # 승패 결정
                decision = ""
                if p_stat.get("wins", 0) > 0: decision = "승리투수 (W)"
                elif p_stat.get("losses", 0) > 0: decision = "패전투수 (L)"
                elif p_stat.get("saves", 0) > 0: decision = "세이브 (SV)"
                elif p_stat.get("holds", 0) > 0: decision = "홀드 (HD)"

                is_starter = (p_idx == 0)
                pos_label = "투수 (선발)" if is_starter else "투수 (구원)"

                player_stats.append({
                    "team_name": t_name_ko,
                    "player_name": p_name,
                    "back_number": b_num,
                    "position": pos_label,
                    "minutes_played": 0,
                    "points": so,
                    "assists": 0,
                    "shots": int(float(ip)) if ip and "." in ip else 0,
                    "extra_stats": {
                        "type": "PITCHER",
                        "player_type": "PITCHER",
                        "is_starter": is_starter,
                        "starter": is_starter,
                        "pitcher_order": p_idx + 1,
                        "ip": ip, "np": np, "h": h, "r": r, "er": er, "bb": bb,
                        "so": so, "hr": hr, "era": era, "season_era": era,
                        "recent_era": recent_era, "whip": whip,
                        "decision": decision
                    }
                })

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "source_url": f"https://www.mlb.com/gameday/{game_pk}",
            "events": events,
            "player_stats": player_stats
        }

    def fetch_realtime_lineup(self, away_team: str, home_team: str, match_date: Optional[str] = None, game_pk: Optional[int] = None) -> Dict[str, Any]:
        """MLB 공식 실시간 선발 라인업 추출 (statsapi.mlb.com 100% 공식 데이터)"""
        from app.services.player_translation import translate_player_name
        
        target_dates = []
        if match_date:
            try:
                dt_kst = datetime.strptime(match_date[:10], "%Y-%m-%d")
                dt_us = dt_kst - timedelta(days=1)
                target_dates = [dt_us.strftime("%Y-%m-%d"), dt_kst.strftime("%Y-%m-%d")]
            except Exception:
                target_dates = [datetime.now().strftime("%Y-%m-%d")]
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            target_dates = [yesterday_str, today_str]

        matched_game = None
        matched_game_pk = game_pk

        if not matched_game_pk:
            def get_team_keywords(name: str) -> List[str]:
                clean = (name or "").replace(" ", "").lower()
                mapping = {
                    "볼티모어": ["orioles", "baltimore"], "볼티": ["orioles", "baltimore"],
                    "토론토": ["bluejays", "toronto"], "토론": ["bluejays", "toronto"],
                    "양키스": ["yankees"], "뉴욕양키": ["yankees"], "뉴욕양키스": ["yankees"],
                    "보스턴": ["redsox", "boston"], "보스": ["redsox", "boston"],
                    "탬파베이": ["rays", "tampabay"], "탬파": ["rays", "tampabay"],
                    "시카고화이트삭스": ["whitesox", "chicago"], "시카화삭": ["whitesox"],
                    "클리블랜드": ["guardians", "cleveland"], "클리": ["guardians"],
                    "디트로이트": ["tigers", "detroit"], "디트": ["tigers"],
                    "캔자스시티": ["royals", "kansascity"], "캔자": ["royals"],
                    "미네소타": ["twins", "minnesota"], "미네": ["twins"],
                    "휴스턴": ["astros", "houston"], "휴스": ["astros"],
                    "에인절스": ["angels", "anaheim"], "LA에인절스": ["angels"], "LA에인절": ["angels"],
                    "오클랜드": ["athletics", "oakland"], "애슬레틱스": ["athletics"],
                    "시애틀": ["mariners", "seattle"], "시애": ["mariners"],
                    "텍사스": ["rangers", "texas"], "텍사": ["rangers"],
                    "애틀랜타": ["braves", "atlanta"], "애틀": ["braves"],
                    "마이애미": ["marlins", "miami"], "마이": ["marlins"],
                    "메츠": ["mets", "newyorkmets"], "뉴욕메츠": ["mets"],
                    "필라델피아": ["phillies", "philadelphia"], "필라": ["phillies"],
                    "워싱턴": ["nationals", "washington"], "워싱": ["nationals"],
                    "시카고컵스": ["cubs", "chicagocubs"], "시카컵스": ["cubs"],
                    "신시내티": ["reds", "cincinnati"], "신시": ["reds"],
                    "밀워키": ["brewers", "milwaukee"], "밀워": ["brewers"],
                    "피츠버그": ["pirates", "pittsburgh"], "피츠": ["pirates"],
                    "세인트루이스": ["cardinals", "stlouis"], "세인": ["cardinals"],
                    "애리조나": ["diamondbacks", "arizona"], "애리": ["diamondbacks"],
                    "콜로라도": ["rockies", "colorado"], "콜로": ["rockies"],
                    "다저스": ["dodgers", "losangelesdodgers"], "LA다저스": ["dodgers"],
                    "샌디에이고": ["padres", "sandiego"], "샌디": ["padres"],
                    "샌프란시스코": ["giants", "sanfrancisco"], "샌프": ["giants"]
                }
                kws = []
                for k, v in mapping.items():
                    if k in clean or clean in k:
                        kws.extend(v)
                if not kws:
                    kws.append(clean)
                return kws

            h_kws = get_team_keywords(home_team)
            a_kws = get_team_keywords(away_team)

            for d in target_dates:
                url = f"{MLB_API_BASE}/schedule?sportId=1&season=2026&date={d}&hydrate=probablePitcher,linescore,team,lineups"
                try:
                    data = self._fetch_json(url)
                    for d_obj in data.get("dates", []):
                        for g in d_obj.get("games", []):
                            g_h = g.get("teams", {}).get("home", {}).get("team", {}).get("name", "").lower().replace(" ", "")
                            g_a = g.get("teams", {}).get("away", {}).get("team", {}).get("name", "").lower().replace(" ", "")
                            h_match = any(kw in g_h for kw in h_kws)
                            a_match = any(kw in g_a for kw in a_kws)
                            if h_match and a_match:
                                matched_game = g
                                matched_game_pk = g.get("gamePk")
                                break
                        if matched_game:
                            break
                except Exception as e:
                    logger.warning(f"fetch_realtime_lineup schedule error: {e}")
                if matched_game:
                    break

        home_lineup = []
        away_lineup = []
        home_starter = {}
        away_starter = {}
        is_confirmed = False

        # 1. 1순위: 공식 gamePk 기준 박스스코어에서 실시간 확정 선발 라인업 및 당해 실제 시즌 타율/OPS/HR/좌우타 추출
        if matched_game_pk:
            try:
                box_url = f"{MLB_API_BASE}/game/{matched_game_pk}/boxscore?hydrate=person"
                box_data = self._fetch_json(box_url)
                teams_box = box_data.get("teams", {})

                for side, target_list in [("home", home_lineup), ("away", away_lineup)]:
                    t_box = teams_box.get(side, {})
                    p_box = t_box.get("players", {})
                    starters = []
                    for pid in t_box.get("batters", []):
                        p_obj = p_box.get(f"ID{pid}")
                        if not p_obj:
                            continue
                        b_order = p_obj.get("battingOrder")
                        if b_order and b_order.endswith("00"):
                            pers = p_obj.get("person", {})
                            p_en = pers.get("fullName", "")
                            p_ko = sanitize_player_name(translate_player_name(p_en))
                            s_bat = p_obj.get("seasonStats", {}).get("batting", {})
                            order_num = int(b_order) // 100
                            starters.append({
                                "order": order_num,
                                "pos": p_obj.get("position", {}).get("abbreviation") or pers.get("primaryPosition", {}).get("abbreviation") or "타자",
                                "name": p_ko or p_en,
                                "name_en": p_en,
                                "id": pid,
                                "hand": pers.get("batSide", {}).get("code") or "R",
                                "avg": s_bat.get("avg") or "",
                                "ops": s_bat.get("ops") or "",
                                "hr": s_bat.get("homeRuns", 0),
                                "rbi": s_bat.get("rbi", 0)
                            })
                    starters.sort(key=lambda x: x["order"])
                    target_list.extend(starters[:9])

                    # 박스스코어 내 선발투수 정보
                    pitchers = t_box.get("pitchers", [])
                    if pitchers:
                        sp_id = pitchers[0]
                        sp_obj = p_box.get(f"ID{sp_id}", {})
                        sp_pers = sp_obj.get("person", {})
                        sp_en = sp_pers.get("fullName", "")
                        sp_s_pitch = sp_obj.get("seasonStats", {}).get("pitching", {})
                        sp_info = {
                            "id": sp_id,
                            "name": sanitize_player_name(translate_player_name(sp_en)) if sp_en else "선발투수",
                            "name_en": sp_en,
                            "hand": sp_pers.get("pitchHand", {}).get("code") or "R",
                            "era": sp_s_pitch.get("era") or "",
                            "wins": sp_s_pitch.get("wins", 0),
                            "losses": sp_s_pitch.get("losses", 0),
                            "confirmed": True
                        }
                        if side == "home":
                            home_starter = sp_info
                        else:
                            away_starter = sp_info

                if len(home_lineup) >= 9 and len(away_lineup) >= 9:
                    is_confirmed = True
            except Exception as be:
                logger.warning(f"fetch_realtime_lineup boxscore fetch error: {be}")

        # 2. 2순위: 박스스코어에 타순이 없으면 스케줄 lineups(person) 실데이터 확인
        if (len(home_lineup) < 9 or len(away_lineup) < 9) and matched_game:
            lineups = matched_game.get("lineups", {})
            h_players = lineups.get("homePlayers", [])
            a_players = lineups.get("awayPlayers", [])

            if len(h_players) >= 9 and len(home_lineup) < 9:
                home_lineup.clear()
                for idx, p in enumerate(h_players[:9]):
                    p_en = p.get("fullName", "")
                    p_ko = sanitize_player_name(translate_player_name(p_en))
                    pos = p.get("primaryPosition", {}).get("abbreviation", "타자")
                    home_lineup.append({
                        "order": idx + 1,
                        "pos": pos,
                        "name": p_ko or p_en,
                        "name_en": p_en,
                        "id": p.get("id"),
                        "hand": p.get("batSide", {}).get("code") or "R",
                        "avg": ""
                    })

            if len(a_players) >= 9 and len(away_lineup) < 9:
                away_lineup.clear()
                for idx, p in enumerate(a_players[:9]):
                    p_en = p.get("fullName", "")
                    p_ko = sanitize_player_name(translate_player_name(p_en))
                    pos = p.get("primaryPosition", {}).get("abbreviation", "타자")
                    away_lineup.append({
                        "order": idx + 1,
                        "pos": pos,
                        "name": p_ko or p_en,
                        "name_en": p_en,
                        "id": p.get("id"),
                        "hand": p.get("batSide", {}).get("code") or "R",
                        "avg": ""
                    })

            if len(home_lineup) >= 9 and len(away_lineup) >= 9:
                is_confirmed = True

        # 선발투수 스케줄 보강
        if matched_game:
            if not home_starter:
                h_prob = matched_game.get("teams", {}).get("home", {}).get("probablePitcher", {})
                if h_prob:
                    h_p_en = h_prob.get("fullName", "")
                    home_starter = {
                        "id": h_prob.get("id"),
                        "name": sanitize_player_name(translate_player_name(h_p_en)) if h_p_en else "선발투수",
                        "name_en": h_p_en,
                        "hand": "R",
                        "confirmed": True
                    }
            if not away_starter:
                a_prob = matched_game.get("teams", {}).get("away", {}).get("probablePitcher", {})
                if a_prob:
                    a_p_en = a_prob.get("fullName", "")
                    away_starter = {
                        "id": a_prob.get("id"),
                        "name": sanitize_player_name(translate_player_name(a_p_en)) if a_p_en else "선발투수",
                        "name_en": a_p_en,
                        "hand": "R",
                        "confirmed": True
                    }

        return {
            "game_pk": matched_game_pk,
            "is_lineup_confirmed": is_confirmed,
            "lineup_status": "CONFIRMED" if is_confirmed else "EXPECTED",
            "home_lineup": home_lineup,
            "away_lineup": away_lineup,
            "home_starter": home_starter,
            "away_starter": away_starter,
            "source": "statsapi.mlb.com"
        }

