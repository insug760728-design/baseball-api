# -*- coding: utf-8 -*-
import urllib.request
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.scrapers.base import BaseScraper
from app.services.player_translation import sanitize_player_name, sanitize_text

logger = logging.getLogger("soccer_scraper")
logger.setLevel(logging.INFO)

SOCCER_LEAGUE_CODES = {
    "EPL": "eng.1",
    "LALIGA": "esp.1",
    "BUNDESLIGA": "ger.1",
    "SERIE_A": "ita.1",
    "LIGUE_1": "fra.1",
    "EREDIVISIE": "ned.1",
    "CHAMPIONSHIP": "eng.2",
    "UCL": "uefa.champions",
    "UEL": "uefa.europa",
    "LIBERTADORES": "conmebol.libertadores",
    "MLS": "usa.1"
}

SOCCER_LEAGUE_NAMES = {
    "EPL": "잉글랜드 프리미어리그 (EPL)",
    "LALIGA": "스페인 라리가 (La Liga)",
    "BUNDESLIGA": "독일 분데스리가 (Bundesliga)",
    "SERIE_A": "이탈리아 세리에 A (Serie A)",
    "LIGUE_1": "프랑스 리그 1 (Ligue 1)",
    "EREDIVISIE": "네덜란드 에레디비시 (Eredivisie)",
    "CHAMPIONSHIP": "잉글랜드 챔피언십 (Championship)",
    "UCL": "UEFA 챔피언스리그 (UCL)",
    "UEL": "UEFA 유로파리그 (UEL)",
    "LIBERTADORES": "코파 리베르타도레스 (Copa Libertadores)",
    "MLS": "미국 메이저리그 사커 (MLS)"
}

MLS_TEAM_TRANSLATION = {
    "Atlanta United FC": "애틀랜타 유나이티드", "Atlanta United": "애틀랜타 유나이티드",
    "Orlando City SC": "올랜도 시티", "Orlando City": "올랜도 시티",
    "CF Montréal": "CF 몬트리올", "CF Montreal": "CF 몬트리올", "Montreal Impact": "CF 몬트리올",
    "Charlotte FC": "샬럿 FC", "Charlotte": "샬럿 FC",
    "D.C. United": "DC 유나이티드", "DC United": "DC 유나이티드",
    "Columbus Crew": "콜럼버스 크루", "Columbus": "콜럼버스 크루",
    "Toronto FC": "토론토 FC", "Toronto": "토론토 FC",
    "Nashville SC": "내슈빌 SC", "Nashville": "내슈빌 SC",
    "Philadelphia Union": "필라델피아 유니온", "Philadelphia": "필라델피아 유니온",
    "FC Cincinnati": "FC 신시내티", "Cincinnati": "FC 신시내티",
    "New York City FC": "뉴욕 시티 FC", "NYCFC": "뉴욕 시티 FC",
    "New England Revolution": "뉴잉글랜드 레볼루션", "New England": "뉴잉글랜드 레볼루션",
    "Austin FC": "오스틴 FC", "Austin": "오스틴 FC",
    "Colorado Rapids": "콜로라도 래피즈", "Colorado": "콜로라도 래피즈",
    "Chicago Fire FC": "시카고 파이어", "Chicago Fire": "시카고 파이어",
    "Inter Miami CF": "인터 마이애미", "Inter Miami": "인터 마이애미",
    "Houston Dynamo FC": "휴스턴 다이나모", "Houston Dynamo": "휴스턴 다이나모",
    "Real Salt Lake": "레알 솔트레이크", "Salt Lake": "레알 솔트레이크",
    "Minnesota United FC": "미네소타 유나이티드", "Minnesota United": "미네소타 유나이티드",
    "FC Dallas": "FC 댈러스", "Dallas": "FC 댈러스",
    "LAFC": "로스앤젤레스 FC (LAFC)", "Los Angeles Football Club": "로스앤젤레스 FC (LAFC)", "Los Angeles FC": "로스앤젤레스 FC (LAFC)",
    "Red Bull New York": "뉴욕 레드불스", "New York Red Bulls": "뉴욕 레드불스", "NY Red Bulls": "뉴욕 레드불스",
    "Portland Timbers": "포틀랜드 팀버즈", "Portland": "포틀랜드 팀버즈",
    "St. Louis CITY SC": "세인트루이스 시티", "St Louis CITY SC": "세인트루이스 시티", "St. Louis City": "세인트루이스 시티",
    "San Diego FC": "샌디에이고 FC", "San Diego": "샌디에이고 FC",
    "San Jose Earthquakes": "산호세 어스퀘이크스", "San Jose": "산호세 어스퀘이크스",
    "Vancouver Whitecaps": "밴쿠버 화이트캡스", "Vancouver Whitecaps FC": "밴쿠버 화이트캡스",
    "LA Galaxy": "LA 갤럭시", "Galaxy": "LA 갤럭시",
    "Seattle Sounders FC": "시애틀 사운더스", "Seattle Sounders": "시애틀 사운더스",
    "Sporting Kansas City": "스포팅 캔자스시티", "Sporting KC": "스포팅 캔자스시티"
}

def translate_soccer_team_name(name: str) -> str:
    if not name: return ""
    clean_name = name.strip()
    if clean_name in MLS_TEAM_TRANSLATION:
        return MLS_TEAM_TRANSLATION[clean_name]
    for eng, kor in MLS_TEAM_TRANSLATION.items():
        if eng.lower() == clean_name.lower() or (len(eng) >= 5 and eng.lower() in clean_name.lower()):
            return kor
    try:
        from app.services.live_api_sports_service import translate_soccer_team
        return translate_soccer_team(clean_name)
    except Exception:
        return clean_name

class SoccerScraper(BaseScraper):
    """
    유럽 축구 5대 리그 전문 수집기
    - 잉글랜드 프리미어리그 (EPL)
    - 스페인 라리가 (La Liga)
    - 독일 분데스리가 (Bundesliga)
    - 이탈리아 세리에 A (Serie A)
    - 프랑스 리그 1 (Ligue 1)
    """

    def __init__(self, league_id: str = "EPL"):
        self.league_id = league_id.upper()
        self.api_code = SOCCER_LEAGUE_CODES.get(self.league_id, "eng.1")
        self.league_name = SOCCER_LEAGUE_NAMES.get(self.league_id, f"유럽 축구 ({self.league_id})")

    def get_sport_code(self) -> str:
        return "SOCCER"

    def get_league_name(self) -> str:
        return self.league_name

    def _fetch_json(self, url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def scrape_matches(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        특정 일자(YYYY-MM-DD)의 해당 리그 전 경기 일정 및 결과 수집
        """
        d = target_date or datetime.now().strftime("%Y-%m-%d")
        d_clean = d.replace("-", "")
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{self.api_code}/scoreboard?dates={d_clean}"

        try:
            data = self._fetch_json(url)
        except Exception as e:
            logger.error(f"[SoccerScraper] {self.league_id} {d} 경기 목록 조회 실패: {e}")
            return []

        events = data.get("events", [])
        result = []

        for ev in events:
            ev_id = ev.get("id")
            comps = ev.get("competitions", [{}])[0]
            competitors = comps.get("competitors", [])

            home_team, away_team = "홈팀", "원정팀"
            home_score, away_score = 0, 0

            for comp in competitors:
                t_name = comp.get("team", {}).get("displayName", "알수없음")
                sc = comp.get("score", 0)
                try:
                    sc_int = int(sc) if sc is not None else 0
                except Exception:
                    sc_int = 0

                if comp.get("homeAway") == "home":
                    home_team = translate_soccer_team_name(t_name)
                    home_score = sc_int
                else:
                    away_team = translate_soccer_team_name(t_name)
                    away_score = sc_int

            status_raw = comps.get("status", {}).get("type", {}).get("state", "pre")
            if status_raw == "post":
                status = "FINISHED"
            elif status_raw == "in":
                status = "LIVE"
            else:
                status = "SCHEDULED"

            raw_date = ev.get("date", "")
            if "T" in raw_date:
                try:
                    utc_clean = raw_date.replace("Z", "+00:00")
                    utc_dt = datetime.fromisoformat(utc_clean)
                    kst_dt = utc_dt + timedelta(hours=9)
                    match_date_str = kst_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    match_date_str = raw_date[:16].replace("T", " ")
            else:
                match_date_str = d

            stadium = comps.get("venue", {}).get("fullName") or "스타디움"
            round_name = ev.get("season", {}).get("slug", "정규시즌")

            result.append({
                "official_id": f"{self.league_id}_{ev_id}",
                "sport_code": "SOCCER",
                "league_name": self.league_name,
                "season": str(ev.get("season", {}).get("year", "2026")),
                "round_name": round_name,
                "match_date": match_date_str,
                "stadium": stadium,
                "home_team_name": home_team,
                "away_team_name": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "status": status
            })

        return result

    def scrape_match_detail(self, official_id: str) -> Dict[str, Any]:
        """
        경기 상세(전후반 스코어, 팀 통계, 골/카드 타임라인, 선수별 출전 스탯) 수집
        """
        if "_" in official_id:
            parts = official_id.rsplit("_", 1)
            l_code = SOCCER_LEAGUE_CODES.get(parts[0], self.api_code)
            ev_id = parts[1]
        else:
            l_code = self.api_code
            ev_id = official_id

        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{l_code}/summary?event={ev_id}"
        try:
            data = self._fetch_json(url)
        except Exception as e:
            logger.error(f"[SoccerScraper] {official_id} 상세 조회 실패: {e}")
            return {"period_scores": {}, "team_stats": {}, "source_url": url, "events": [], "player_stats": []}

        # 1. 전후반 스코어 및 팀 통계
        comps = data.get("header", {}).get("competitions", [{}])[0]
        competitors = comps.get("competitors", [])

        home_team_name, away_team_name = "홈팀", "원정팀"
        period_scores = {"home": {}, "away": {}}

        def _safe_int(v):
            try: return int(v)
            except Exception: return 0

        for comp in competitors:
            t_name = translate_soccer_team_name(comp.get("team", {}).get("displayName", ""))
            ha = comp.get("homeAway", "home")
            if ha == "home":
                home_team_name = t_name
            else:
                away_team_name = t_name

            lines = comp.get("linescores", [])
            if len(lines) >= 2:
                period_scores[ha]["1H"] = _safe_int(lines[0].get("value", 0))
                period_scores[ha]["2H"] = _safe_int(lines[1].get("value", 0))
            else:
                period_scores[ha]["FT"] = _safe_int(comp.get("score", 0))

        # 박스스코어 팀 통계
        box_teams = data.get("boxscore", {}).get("teams", [])
        team_stats = {"home": {}, "away": {}}
        for bt in box_teams:
            bt_name = bt.get("team", {}).get("displayName", "")
            ha = "home" if bt_name == home_team_name else "away"
            for st in bt.get("statistics", []):
                s_name = st.get("name")
                s_val = st.get("displayValue")
                team_stats[ha][s_name] = s_val

        # 2. 골 & 카드 이벤트 타임라인
        events_list = []
        raw_events = data.get("keyEvents", [])
        for re in raw_events:
            clock = re.get("clock", {}).get("displayValue", "")
            ev_type_text = re.get("type", {}).get("text", "")
            desc = re.get("text", "")
            
            ev_type = "EVENT"
            if "Goal" in ev_type_text or "goal" in desc.lower():
                ev_type = "GOAL"
            elif "Yellow Card" in ev_type_text:
                ev_type = "YELLOW_CARD"
            elif "Red Card" in ev_type_text:
                ev_type = "RED_CARD"
            elif "Substitution" in ev_type_text:
                ev_type = "SUBSTITUTION"

            # 득점자/어시스트 추출
            p_name = ""
            for athlete in re.get("participants", []):
                p_name = athlete.get("athlete", {}).get("displayName", "")
                break
            if not p_name and "(" in desc:
                p_name = desc.split("(")[0].strip()

            t_name = ""
            if "team" in re:
                t_name = re.get("team", {}).get("displayName", "")
            if not t_name:
                t_name = home_team_name if home_team_name in desc else away_team_name

            p_name = sanitize_player_name(p_name)
            desc = sanitize_text(desc)

            events_list.append({
                "time_display": clock,
                "event_type": ev_type,
                "team_name": t_name,
                "player_name": p_name or "선수",
                "assist_player_name": None,
                "score_after": None,
                "description": desc
            })

        # 골 이벤트를 바탕으로 전반/후반 스코어 정밀 보정
        def _sum_dict(d):
            return sum(_safe_int(v) for v in (d or {}).values())
        h_total = _sum_dict(period_scores.get("home", {}))
        a_total = _sum_dict(period_scores.get("away", {}))
        if h_total == 0 and a_total == 0:
            h_1h, h_2h, a_1h, a_2h = 0, 0, 0, 0
            for ev in events_list:
                if ev.get("event_type") == "GOAL":
                    t = ev.get("time_display", "")
                    min_val = 50
                    if "'" in t:
                        try:
                            min_val = int(t.split("'")[0].split("+")[0])
                        except Exception:
                            min_val = 50
                    is_h = (ev.get("team_name") == home_team_name)
                    if min_val <= 45:
                        if is_h: h_1h += 1
                        else: a_1h += 1
                    else:
                        if is_h: h_2h += 1
                        else: a_2h += 1
            period_scores["home"] = {"1H": h_1h, "2H": h_2h}
            period_scores["away"] = {"1H": a_1h, "2H": a_2h}

        # 3. 선수별 출전 스탯 및 라인업
        player_stats_list = []
        rosters = data.get("rosters", [])
        for team_roster in rosters:
            t_name = team_roster.get("team", {}).get("displayName", "")
            for p in team_roster.get("roster", []):
                athlete = p.get("athlete", {})
                p_name = sanitize_player_name(athlete.get("displayName", ""))
                jersey = athlete.get("jersey", p.get("jersey", "-"))
                pos_name = p.get("position", {}).get("displayName", "Player")

                stats_dict = {s.get("name"): s.get("displayValue") for s in p.get("stats", [])}

                # 골, 어시스트, 슈팅 등
                goals = int(stats_dict.get("totalGoals", 0) or 0)
                assists = int(stats_dict.get("goalAssists", 0) or 0)
                shots = int(stats_dict.get("totalShots", 0) or 0)
                sot = int(stats_dict.get("shotsOnTarget", 0) or 0)
                fouls_c = int(stats_dict.get("foulsCommitted", 0) or 0)
                fouls_s = int(stats_dict.get("foulsSuffered", 0) or 0)
                yellows = int(stats_dict.get("yellowCards", 0) or 0)
                reds = int(stats_dict.get("redCards", 0) or 0)
                saves = int(stats_dict.get("saves", 0) or 0)
                goals_conceded = int(stats_dict.get("goalsConceded", 0) or 0)

                # 포지션 대분류 (FW, MF, DF, GK)
                role = "FW"
                if "Goalkeeper" in pos_name or "골키퍼" in pos_name:
                    role = "GK"
                elif "Defender" in pos_name or "Back" in pos_name or "수비" in pos_name:
                    role = "DF"
                elif "Midfield" in pos_name or "미드" in pos_name:
                    role = "MF"
                elif "Forward" in pos_name or "Striker" in pos_name or "Winger" in pos_name or "공격" in pos_name:
                    role = "FW"

                extra_stats = {
                    "player_type": role,
                    "position_name": pos_name,
                    "starter": p.get("starter", False),
                    "goals": goals,
                    "assists": assists,
                    "shots": shots,
                    "shots_on_target": sot,
                    "fouls_committed": fouls_c,
                    "fouls_suffered": fouls_s,
                    "yellow_cards": yellows,
                    "red_cards": reds,
                    "saves": saves,
                    "goals_conceded": goals_conceded,
                    "raw_stats": stats_dict
                }

                player_stats_list.append({
                    "team_name": t_name,
                    "player_name": p_name,
                    "back_number": str(jersey),
                    "position": role,
                    "points": goals,
                    "shots": shots,
                    "extra_stats": extra_stats
                })

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "source_url": url,
            "events": events_list,
            "player_stats": player_stats_list
        }
