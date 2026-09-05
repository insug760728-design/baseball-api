# -*- coding: utf-8 -*-
import urllib.request
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.scrapers.base import BaseScraper

logger = logging.getLogger("basketball_scraper")
logger.setLevel(logging.INFO)

class BasketballScraper(BaseScraper):
    """
    농구 전문 수집기 (ESPN NBA 공식 API 기반)
    - 1Q, 2Q, 3Q, 4Q, 연장(OT) 쿼터별 스코어보드
    - 팀별 득점, 리바운드, 어시스트, 스틸, 블록, 턴오버, FG%, 3P%, FT%
    - 선수별 14대 지표 상세 박스스코어 (MIN, PTS, FGM-FGA, 3PM-3PA, FTM-FTA, OREB, DREB, REB, AST, STL, BLK, TO, PF, +/-)
    """

    def __init__(self, league_id: str = "NBA"):
        self.league_id = league_id.upper()
        self.league_name = "미국 프로농구 (NBA)" if self.league_id == "NBA" else f"농구 ({self.league_id})"

    def get_sport_code(self) -> str:
        return "BASKETBALL"

    def get_league_name(self) -> str:
        return self.league_name

    def _fetch_json(self, url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def scrape_matches(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        특정 일자(YYYY-MM-DD)의 NBA 경기 목록 및 스코어보드 수집
        """
        d = target_date or datetime.now().strftime("%Y-%m-%d")
        d_clean = d.replace("-", "")
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d_clean}"

        try:
            data = self._fetch_json(url)
        except Exception as e:
            logger.error(f"[BasketballScraper] {self.league_id} {d} 경기 목록 조회 실패: {e}")
            return []

        events = data.get("events", [])
        result = []

        for ev in events:
            ev_id = ev.get("id")
            comps = ev.get("competitions", [{}])[0]
            competitors = comps.get("competitors", [])

            home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away_comp = next((c for c in competitors if c.get("homeAway") == "away"), {})

            home_team = home_comp.get("team", {}).get("displayName", "Home Team")
            away_team = away_comp.get("team", {}).get("displayName", "Away Team")

            home_score = int(home_comp.get("score", 0)) if home_comp.get("score") else 0
            away_score = int(away_comp.get("score", 0)) if away_comp.get("score") else 0

            status_type = comps.get("status", {}).get("type", {})
            status_desc = status_type.get("description", "").upper()
            status_state = status_type.get("state", "").lower()

            if "FINAL" in status_desc or status_state == "post":
                status = "FINISHED"
            elif "IN" in status_desc or status_state == "in":
                status = "LIVE"
            else:
                status = "SCHEDULED"

            # 쿼터별 스코어 (Linescores)
            def _extract_ls(comp):
                res = []
                for x in comp.get("linescores", []):
                    val = x.get("displayValue") if "displayValue" in x else x.get("value", 0)
                    try:
                        res.append(int(float(val)))
                    except Exception:
                        res.append(0)
                return res

            home_lines = _extract_ls(home_comp)
            away_lines = _extract_ls(away_comp)

            def make_period_dict(lines, total):
                q1 = int(lines[0]) if len(lines) > 0 else 0
                q2 = int(lines[1]) if len(lines) > 1 else 0
                q3 = int(lines[2]) if len(lines) > 2 else 0
                q4 = int(lines[3]) if len(lines) > 3 else 0
                ot = sum(int(x) for x in lines[4:]) if len(lines) > 4 else 0
                return {
                    "q1": q1,
                    "q2": q2,
                    "q3": q3,
                    "q4": q4,
                    "ot": ot,
                    "total": total
                }

            period_scores = {
                "home": make_period_dict(home_lines, home_score),
                "away": make_period_dict(away_lines, away_score)
            }

            match_date_str = ev.get("date", "")
            try:
                dt_obj = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%MZ")
                formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M")
            except Exception:
                formatted_date = d + " 19:00"

            venue_name = comps.get("venue", {}).get("fullName", "")

            match_item = {
                "official_id": f"{self.league_id}_{ev_id}",
                "official_match_code": f"{self.league_id}_{ev_id}",
                "sport_code": "BASKETBALL",
                "league_name": self.league_name,
                "season": "2026",
                "round_name": "정규시즌",
                "match_date": formatted_date,
                "stadium": venue_name,
                "home_team_name": home_team,
                "away_team_name": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
                "venue": venue_name,
                "source_url": f"https://www.espn.com/nba/game/_/gameId/{ev_id}",
                "period_scores": period_scores
            }
            result.append(match_item)

        return result

    def scrape_match_detail(self, official_match_code: str) -> Dict[str, Any]:
        """
        특정 경기의 상세 팀 기록 및 선수 박스스코어 수집
        """
        ev_id = official_match_code.rsplit("_", 1)[-1]
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={ev_id}"

        try:
            data = self._fetch_json(url)
        except Exception as e:
            logger.error(f"[BasketballScraper] {official_match_code} 상세 정보 조회 실패: {e}")
            return {"period_scores": {}, "team_stats": {}, "events": [], "player_stats": []}

        # 1. 스코어보드 (Linescores)
        header = data.get("header", {})
        comps = header.get("competitions", [{}])[0]
        competitors = comps.get("competitors", [])

        home_comp = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away_comp = next((c for c in competitors if c.get("homeAway") == "away"), {})

        def get_lines(comp):
            res = []
            for x in comp.get("linescores", []):
                val = x.get("displayValue") if "displayValue" in x else x.get("value", 0)
                try:
                    res.append(int(float(val)))
                except Exception:
                    res.append(0)
            return res

        home_lines = get_lines(home_comp)
        away_lines = get_lines(away_comp)
        home_tot = int(home_comp.get("score", 0)) if home_comp.get("score") else 0
        away_tot = int(away_comp.get("score", 0)) if away_comp.get("score") else 0

        def parse_q_dict(lines, total):
            return {
                "q1": int(lines[0]) if len(lines) > 0 else 0,
                "q2": int(lines[1]) if len(lines) > 1 else 0,
                "q3": int(lines[2]) if len(lines) > 2 else 0,
                "q4": int(lines[3]) if len(lines) > 3 else 0,
                "ot": sum(int(x) for x in lines[4:]) if len(lines) > 4 else 0,
                "total": total
            }

        period_scores = {
            "home": parse_q_dict(home_lines, home_tot),
            "away": parse_q_dict(away_lines, away_tot)
        }

        # 2. 팀 통계
        boxscore = data.get("boxscore", {})
        teams_box = boxscore.get("teams", [])

        team_stats = {"home": {}, "away": {}}
        for tb in teams_box:
            side = tb.get("team", {}).get("homeAway", "home")
            if not side or side not in ["home", "away"]:
                t_name = tb.get("team", {}).get("displayName", "")
                if t_name == home_comp.get("team", {}).get("displayName", ""):
                    side = "home"
                else:
                    side = "away"

            stats_dict = {}
            for st in tb.get("statistics", []):
                s_name = st.get("name")
                s_val = st.get("displayValue")
                stats_dict[s_name] = s_val

            fg_str = stats_dict.get("fieldGoalsMade-fieldGoalsAttempted", "0-0")
            fg3_str = stats_dict.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted", "0-0")
            ft_str = stats_dict.get("freeThrowsMade-freeThrowsAttempted", "0-0")

            def split_made_att(s):
                parts = s.split("-") if "-" in s else ["0", "0"]
                try:
                    return int(parts[0]), int(parts[1])
                except Exception:
                    return 0, 0

            fgm, fga = split_made_att(fg_str)
            fg3m, fg3a = split_made_att(fg3_str)
            ftm, fta = split_made_att(ft_str)

            try:
                fg_pct = float(stats_dict.get("fieldGoalPct", 0))
            except Exception:
                fg_pct = round((fgm / fga * 100), 1) if fga > 0 else 0.0

            try:
                fg3_pct = float(stats_dict.get("threePointFieldGoalPct", 0))
            except Exception:
                fg3_pct = round((fg3m / fg3a * 100), 1) if fg3a > 0 else 0.0

            try:
                ft_pct = float(stats_dict.get("freeThrowPct", 0))
            except Exception:
                ft_pct = round((ftm / fta * 100), 1) if fta > 0 else 0.0

            team_stats[side] = {
                "pts": home_tot if side == "home" else away_tot,
                "fgm": fgm,
                "fga": fga,
                "fg_pct": fg_pct,
                "fg3m": fg3m,
                "fg3a": fg3a,
                "fg3_pct": fg3_pct,
                "ftm": ftm,
                "fta": fta,
                "ft_pct": ft_pct,
                "reb": int(stats_dict.get("totalRebounds", 0) or 0),
                "oreb": int(stats_dict.get("offensiveRebounds", 0) or 0),
                "dreb": int(stats_dict.get("defensiveRebounds", 0) or 0),
                "ast": int(stats_dict.get("assists", 0) or 0),
                "stl": int(stats_dict.get("steals", 0) or 0),
                "blk": int(stats_dict.get("blocks", 0) or 0),
                "to": int(stats_dict.get("totalTurnovers", stats_dict.get("turnovers", 0)) or 0),
                "pf": int(stats_dict.get("fouls", 0) or 0),
                "points_in_paint": int(stats_dict.get("pointsInPaint", 0) or 0),
                "fast_break_points": int(stats_dict.get("fastBreakPoints", 0) or 0)
            }

        # 3. 선수별 상세 박스스코어
        players_group = boxscore.get("players", [])
        player_stats = []

        for pg in players_group:
            team_display = pg.get("team", {}).get("displayName", "")
            stats_block = pg.get("statistics", [{}])[0]
            col_names = stats_block.get("names", [])
            athletes = stats_block.get("athletes", [])

            for ath in athletes:
                athlete_info = ath.get("athlete", {})
                p_name = athlete_info.get("displayName", "Unknown Player")
                p_pos = athlete_info.get("position", {}).get("abbreviation", "G")
                is_starter = ath.get("starter", False)
                raw_stats = ath.get("stats", [])

                if not raw_stats:
                    continue

                stat_map = dict(zip(col_names, raw_stats))

                min_str = stat_map.get("MIN", "0")
                try:
                    minutes = int(min_str.split(":")[0]) if ":" in min_str else int(min_str)
                except Exception:
                    minutes = 0

                try:
                    pts = int(stat_map.get("PTS", 0))
                except Exception:
                    pts = 0

                fg_s = stat_map.get("FG", "0-0")
                fg3_s = stat_map.get("3PT", "0-0")
                ft_s = stat_map.get("FT", "0-0")

                def split_ath_stat(s):
                    parts = s.split("-") if "-" in s else ["0", "0"]
                    try:
                        return int(parts[0]), int(parts[1])
                    except Exception:
                        return 0, 0

                p_fgm, p_fga = split_ath_stat(fg_s)
                p_fg3m, p_fg3a = split_ath_stat(fg3_s)
                p_ftm, p_fta = split_ath_stat(ft_s)

                p_fg_pct = round((p_fgm / p_fga * 100), 1) if p_fga > 0 else 0.0
                p_fg3_pct = round((p_fg3m / p_fg3a * 100), 1) if p_fg3a > 0 else 0.0
                p_ft_pct = round((p_ftm / p_fta * 100), 1) if p_fta > 0 else 0.0

                def safe_int(k):
                    try:
                        return int(stat_map.get(k, 0) or 0)
                    except Exception:
                        return 0

                reb = safe_int("REB")
                oreb = safe_int("OREB")
                dreb = safe_int("DREB")
                ast = safe_int("AST")
                stl = safe_int("STL")
                blk = safe_int("BLK")
                to = safe_int("TO")
                pf = safe_int("PF")

                pm_str = stat_map.get("+/-", "0")
                try:
                    plus_minus = int(pm_str)
                except Exception:
                    plus_minus = 0

                efg_pct = round(((p_fgm + 0.5 * p_fg3m) / p_fga * 100), 1) if p_fga > 0 else 0.0
                ts_denom = 2 * (p_fga + 0.44 * p_fta)
                ts_pct = round((pts / ts_denom * 100), 1) if ts_denom > 0 else 0.0

                game_score = round(
                    pts + 0.4 * p_fgm - 0.7 * p_fga - 0.4 * (p_fta - p_ftm) +
                    0.7 * oreb + 0.3 * dreb + stl + 0.7 * ast + 0.5 * blk - 0.4 * pf - to,
                    1
                )

                extra = {
                    "starter": is_starter,
                    "fgm": p_fgm,
                    "fga": p_fga,
                    "fg_pct": p_fg_pct,
                    "fg3m": p_fg3m,
                    "fg3a": p_fg3a,
                    "fg3_pct": p_fg3_pct,
                    "ftm": p_ftm,
                    "fta": p_fta,
                    "ft_pct": p_ft_pct,
                    "reb": reb,
                    "oreb": oreb,
                    "dreb": dreb,
                    "ast": ast,
                    "stl": stl,
                    "blk": blk,
                    "to": to,
                    "pf": pf,
                    "plus_minus": plus_minus,
                    "efg_pct": efg_pct,
                    "ts_pct": ts_pct,
                    "game_score": game_score
                }

                player_stats.append({
                    "team_name": team_display,
                    "player_name": p_name,
                    "position": p_pos,
                    "minutes_played": minutes,
                    "points": pts,
                    "assists": ast,
                    "shots": p_fga,
                    "extra_stats": extra
                })

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "events": [],
            "player_stats": player_stats
        }
