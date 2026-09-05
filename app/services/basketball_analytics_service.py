# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.models import Match, MatchDetail, PlayerMatchStat

logger = logging.getLogger("basketball_analytics")
logger.setLevel(logging.INFO)

class BasketballAnalyticsService:
    """
    농구 전문 세이버메트릭스 & 어드밴스드 지표 계산 서비스
    - 팀 어드밴스드: Pace, ORtg, DRtg, Net Rating, eFG%, TS%, AST/TO Ratio, REB%, TOV%
    - 선수 세이버메트릭스: TS%, eFG%, Hollinger Game Score, AST/TO, Per-36 Stats
    - 3·5·7·10 경기/일 롤링 지표 & 최근 게임 로그
    """

    @classmethod
    def compute_match_advanced_stats(cls, match: Match, detail: Optional[MatchDetail]) -> Dict[str, Any]:
        """
        경기별 양 팀의 현대 농구 어드밴스드 지표 산출
        """
        if not detail or not detail.team_stats:
            return {
                "home": cls._empty_team_advanced(),
                "away": cls._empty_team_advanced()
            }

        try:
            raw_stats = json.loads(detail.team_stats)
        except Exception:
            raw_stats = {}

        home_st = raw_stats.get("home", {})
        away_st = raw_stats.get("away", {})

        # 데이터가 비어 있는 경우
        if not home_st and not away_st:
            return {
                "home": cls._empty_team_advanced(),
                "away": cls._empty_team_advanced()
            }

        def get_stat(st, key, fallback=0):
            val = st.get(key, fallback)
            try:
                return float(val) if val is not None else float(fallback)
            except Exception:
                return float(fallback)

        h_pts = get_stat(home_st, "pts", match.home_score or 0)
        a_pts = get_stat(away_st, "pts", match.away_score or 0)

        h_fga = get_stat(home_st, "fga", 85)
        h_fgm = get_stat(home_st, "fgm", 38)
        h_fg3a = get_stat(home_st, "fg3a", 30)
        h_fg3m = get_stat(home_st, "fg3m", 10)
        h_fta = get_stat(home_st, "fta", 20)
        h_ftm = get_stat(home_st, "ftm", 15)
        h_oreb = get_stat(home_st, "oreb", 10)
        h_dreb = get_stat(home_st, "dreb", 32)
        h_reb = get_stat(home_st, "reb", h_oreb + h_dreb)
        h_ast = get_stat(home_st, "ast", 24)
        h_stl = get_stat(home_st, "stl", 7)
        h_blk = get_stat(home_st, "blk", 5)
        h_to = get_stat(home_st, "to", 12)
        h_pf = get_stat(home_st, "pf", 18)

        a_fga = get_stat(away_st, "fga", 85)
        a_fgm = get_stat(away_st, "fgm", 38)
        a_fg3a = get_stat(away_st, "fg3a", 30)
        a_fg3m = get_stat(away_st, "fg3m", 10)
        a_fta = get_stat(away_st, "fta", 20)
        a_ftm = get_stat(away_st, "ftm", 15)
        a_oreb = get_stat(away_st, "oreb", 10)
        a_dreb = get_stat(away_st, "dreb", 32)
        a_reb = get_stat(away_st, "reb", a_oreb + a_dreb)
        a_ast = get_stat(away_st, "ast", 24)
        a_stl = get_stat(away_st, "stl", 7)
        a_blk = get_stat(away_st, "blk", 5)
        a_to = get_stat(away_st, "to", 12)
        a_pf = get_stat(away_st, "pf", 18)

        # 1. Possessions (공격권 횟수 공식: 0.96 * (FGA + TO + 0.44 * FTA - OREB))
        h_poss = max(40.0, 0.96 * (h_fga + h_to + 0.44 * h_fta - h_oreb))
        a_poss = max(40.0, 0.96 * (a_fga + a_to + 0.44 * a_fta - a_oreb))
        avg_poss = (h_poss + a_poss) / 2.0

        # Pace (48분당 페이스)
        pace = round(avg_poss, 1)

        # 2. Offensive & Defensive Ratings
        h_ortg = round((h_pts / h_poss) * 100, 1) if h_poss > 0 else 0.0
        a_ortg = round((a_pts / a_poss) * 100, 1) if a_poss > 0 else 0.0
        h_drtg = a_ortg
        a_drtg = h_ortg

        # 3. Net Rating (공수 마진)
        h_net_rtg = round(h_ortg - h_drtg, 1)
        a_net_rtg = round(a_ortg - a_drtg, 1)

        # 4. eFG% & TS%
        h_efg = round(((h_fgm + 0.5 * h_fg3m) / h_fga * 100), 1) if h_fga > 0 else 0.0
        a_efg = round(((a_fgm + 0.5 * a_fg3m) / a_fga * 100), 1) if a_fga > 0 else 0.0

        h_ts_den = 2 * (h_fga + 0.44 * h_fta)
        h_ts = round((h_pts / h_ts_den * 100), 1) if h_ts_den > 0 else 0.0

        a_ts_den = 2 * (a_fga + 0.44 * a_fta)
        a_ts = round((a_pts / a_ts_den * 100), 1) if a_ts_den > 0 else 0.0

        # 5. AST/TO Ratio
        h_ast_to = round(h_ast / (h_to if h_to > 0 else 1), 2)
        a_ast_to = round(a_ast / (a_to if a_to > 0 else 1), 2)

        # 6. REB% (리바운드 점유율)
        tot_reb = h_reb + a_reb
        h_reb_pct = round((h_reb / tot_reb * 100), 1) if tot_reb > 0 else 50.0
        a_reb_pct = round((a_reb / tot_reb * 100), 1) if tot_reb > 0 else 50.0

        # 7. TOV% (턴오버율: TO / (FGA + 0.44 * FTA + TO) * 100)
        h_tov_den = h_fga + 0.44 * h_fta + h_to
        h_tov_pct = round((h_to / h_tov_den * 100), 1) if h_tov_den > 0 else 0.0

        a_tov_den = a_fga + 0.44 * a_fta + a_to
        a_tov_pct = round((a_to / a_tov_den * 100), 1) if a_tov_den > 0 else 0.0

        return {
            "home": {
                "pace": pace,
                "ortg": h_ortg,
                "drtg": h_drtg,
                "net_rating": h_net_rtg,
                "efg_pct": h_efg,
                "ts_pct": h_ts,
                "ast_to_ratio": h_ast_to,
                "reb_pct": h_reb_pct,
                "tov_pct": h_tov_pct,
                "pts": int(h_pts),
                "reb": int(h_reb),
                "ast": int(h_ast),
                "stl": int(h_stl),
                "blk": int(h_blk),
                "to": int(h_to),
                "fg_pct": home_st.get("fg_pct", round((h_fgm/h_fga*100), 1) if h_fga > 0 else 0.0),
                "fg3_pct": home_st.get("fg3_pct", round((h_fg3m/h_fg3a*100), 1) if h_fg3a > 0 else 0.0),
                "ft_pct": home_st.get("ft_pct", round((h_ftm/h_fta*100), 1) if h_fta > 0 else 0.0)
            },
            "away": {
                "pace": pace,
                "ortg": a_ortg,
                "drtg": a_drtg,
                "net_rating": a_net_rtg,
                "efg_pct": a_efg,
                "ts_pct": a_ts,
                "ast_to_ratio": a_ast_to,
                "reb_pct": a_reb_pct,
                "tov_pct": a_tov_pct,
                "pts": int(a_pts),
                "reb": int(a_reb),
                "ast": int(a_ast),
                "stl": int(a_stl),
                "blk": int(a_blk),
                "to": int(a_to),
                "fg_pct": away_st.get("fg_pct", round((a_fgm/a_fga*100), 1) if a_fga > 0 else 0.0),
                "fg3_pct": away_st.get("fg3_pct", round((a_fg3m/a_fg3a*100), 1) if a_fg3a > 0 else 0.0),
                "ft_pct": away_st.get("ft_pct", round((a_ftm/a_fta*100), 1) if a_fta > 0 else 0.0)
            }
        }

    @staticmethod
    def _empty_team_advanced() -> Dict[str, Any]:
        return {
            "pace": 0.0,
            "ortg": 0.0,
            "drtg": 0.0,
            "net_rating": 0.0,
            "efg_pct": 0.0,
            "ts_pct": 0.0,
            "ast_to_ratio": 0.0,
            "reb_pct": 0.0,
            "tov_pct": 0.0,
            "pts": 0,
            "reb": 0,
            "ast": 0,
            "stl": 0,
            "blk": 0,
            "to": 0,
            "fg_pct": 0.0,
            "fg3_pct": 0.0,
            "ft_pct": 0.0
        }

    @classmethod
    def compute_player_basketball_sabermetrics(cls, stat_records: List[PlayerMatchStat]) -> Dict[str, Any]:
        """
        선수의 복수 경기 기록을 합산하여 종합 세이버메트릭스 산출
        """
        if not stat_records:
            return {}

        total_pts = sum(s.points for s in stat_records)
        total_ast = sum(s.assists for s in stat_records)
        total_min = sum(s.minutes_played for s in stat_records)
        gp = len(stat_records)

        tot_fgm, tot_fga = 0, 0
        tot_fg3m, tot_fg3a = 0, 0
        tot_ftm, tot_fta = 0, 0
        tot_reb, tot_oreb, tot_dreb = 0, 0, 0
        tot_stl, tot_blk, tot_to, tot_pf = 0, 0, 0, 0
        tot_pm = 0
        tot_game_score = 0.0

        for s in stat_records:
            try:
                extra = json.loads(s.extra_stats) if s.extra_stats else {}
            except Exception:
                extra = {}

            tot_fgm += int(extra.get("fgm", 0) or 0)
            tot_fga += int(extra.get("fga", s.shots or 0) or 0)
            tot_fg3m += int(extra.get("fg3m", 0) or 0)
            tot_fg3a += int(extra.get("fg3a", 0) or 0)
            tot_ftm += int(extra.get("ftm", 0) or 0)
            tot_fta += int(extra.get("fta", 0) or 0)

            tot_reb += int(extra.get("reb", 0) or 0)
            tot_oreb += int(extra.get("oreb", 0) or 0)
            tot_dreb += int(extra.get("dreb", 0) or 0)
            tot_stl += int(extra.get("stl", 0) or 0)
            tot_blk += int(extra.get("blk", 0) or 0)
            tot_to += int(extra.get("to", 0) or 0)
            tot_pf += int(extra.get("pf", 0) or 0)
            tot_pm += int(extra.get("plus_minus", 0) or 0)

            gs = extra.get("game_score")
            if gs is not None:
                tot_game_score += float(gs)
            else:
                # 계산
                single_gs = (
                    s.points + 0.4 * int(extra.get("fgm", 0) or 0) - 0.7 * int(extra.get("fga", 0) or 0) -
                    0.4 * (int(extra.get("fta", 0) or 0) - int(extra.get("ftm", 0) or 0)) +
                    0.7 * int(extra.get("oreb", 0) or 0) + 0.3 * int(extra.get("dreb", 0) or 0) +
                    int(extra.get("stl", 0) or 0) + 0.7 * s.assists + 0.5 * int(extra.get("blk", 0) or 0) -
                    0.4 * int(extra.get("pf", 0) or 0) - int(extra.get("to", 0) or 0)
                )
                tot_game_score += single_gs

        fg_pct = round((tot_fgm / tot_fga * 100), 1) if tot_fga > 0 else 0.0
        fg3_pct = round((tot_fg3m / tot_fg3a * 100), 1) if tot_fg3a > 0 else 0.0
        ft_pct = round((tot_ftm / tot_fta * 100), 1) if tot_fta > 0 else 0.0

        efg_pct = round(((tot_fgm + 0.5 * tot_fg3m) / tot_fga * 100), 1) if tot_fga > 0 else 0.0
        ts_den = 2 * (tot_fga + 0.44 * tot_fta)
        ts_pct = round((total_pts / ts_den * 100), 1) if ts_den > 0 else 0.0

        ast_to = round(total_ast / (tot_to if tot_to > 0 else 1), 2)
        avg_game_score = round(tot_game_score / gp, 1) if gp > 0 else 0.0

        # Per 36 min
        pts_36 = round((total_pts / total_min * 36), 1) if total_min > 0 else 0.0
        reb_36 = round((tot_reb / total_min * 36), 1) if total_min > 0 else 0.0
        ast_36 = round((total_ast / total_min * 36), 1) if total_min > 0 else 0.0

        return {
            "gp": gp,
            "minutes": total_min,
            "avg_min": round(total_min / gp, 1) if gp > 0 else 0.0,
            "pts": total_pts,
            "avg_pts": round(total_pts / gp, 1) if gp > 0 else 0.0,
            "reb": tot_reb,
            "avg_reb": round(tot_reb / gp, 1) if gp > 0 else 0.0,
            "oreb": tot_oreb,
            "dreb": tot_dreb,
            "ast": total_ast,
            "avg_ast": round(total_ast / gp, 1) if gp > 0 else 0.0,
            "stl": tot_stl,
            "avg_stl": round(tot_stl / gp, 1) if gp > 0 else 0.0,
            "blk": tot_blk,
            "avg_blk": round(tot_blk / gp, 1) if gp > 0 else 0.0,
            "to": tot_to,
            "avg_to": round(tot_to / gp, 1) if gp > 0 else 0.0,
            "pf": tot_pf,
            "plus_minus": tot_pm,
            "avg_plus_minus": round(tot_pm / gp, 1) if gp > 0 else 0.0,
            "fgm": tot_fgm,
            "fga": tot_fga,
            "fg_pct": fg_pct,
            "fg3m": tot_fg3m,
            "fg3a": tot_fg3a,
            "fg3_pct": fg3_pct,
            "ftm": tot_ftm,
            "fta": tot_fta,
            "ft_pct": ft_pct,
            "efg_pct": efg_pct,
            "ts_pct": ts_pct,
            "game_score": avg_game_score,
            "ast_to_ratio": ast_to,
            "pts_per36": pts_36,
            "reb_per36": reb_36,
            "ast_per36": ast_36
        }

    @classmethod
    def calculate_player_rolling_stats(
        cls,
        db: Session,
        player_name: str,
        windows: List[int] = [3, 5, 7, 10],
        days: List[int] = [3, 5, 7, 10],
        player_type: str = "guard",
        team_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        농구 선수 3·5·7·10 경기/일 롤링 세이버 지표 및 최근 게임 로그 산출
        """
        query = db.query(PlayerMatchStat, Match).join(Match, PlayerMatchStat.match_id == Match.id)\
            .filter(PlayerMatchStat.player_name == player_name)\
            .filter(Match.sport_code == "BASKETBALL")

        if team_name:
            query = query.filter(PlayerMatchStat.team_name == team_name)

        rows = query.order_by(Match.match_date.desc()).all()

        if not rows:
            return {
                "player_name": player_name,
                "team_name": team_name,
                "player_type": player_type,
                "rolling_games": {},
                "rolling_days": {},
                "recent_game_logs": []
            }

        # 1. 경기수 기준 롤링
        rolling_games = {}
        for w in windows:
            subset = [p_stat for p_stat, m in rows[:w]]
            if subset:
                rolling_games[f"{w}G"] = cls.compute_player_basketball_sabermetrics(subset)

        # 2. 일자 기준 롤링
        rolling_days = {}
        latest_date_str = rows[0][1].match_date[:10]
        try:
            latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")
        except Exception:
            latest_dt = datetime.now()

        for d in days:
            threshold_dt = latest_dt - timedelta(days=d)
            subset = []
            for p_stat, m in rows:
                try:
                    m_dt = datetime.strptime(m.match_date[:10], "%Y-%m-%d")
                    if m_dt >= threshold_dt:
                        subset.append(p_stat)
                except Exception:
                    pass
            if subset:
                rolling_days[f"{d}D"] = cls.compute_player_basketball_sabermetrics(subset)

        # 3. 최근 게임 로그 (Game Logs)
        recent_logs = []
        for p_stat, m in rows[:15]:
            opp = m.away_team_name if p_stat.team_name == m.home_team_name else m.home_team_name
            try:
                extra = json.loads(p_stat.extra_stats) if p_stat.extra_stats else {}
            except Exception:
                extra = {}

            fgm = int(extra.get("fgm", 0) or 0)
            fga = int(extra.get("fga", p_stat.shots or 0) or 0)
            fg3m = int(extra.get("fg3m", 0) or 0)
            fg3a = int(extra.get("fg3a", 0) or 0)
            ftm = int(extra.get("ftm", 0) or 0)
            fta = int(extra.get("fta", 0) or 0)

            recent_logs.append({
                "match_date": m.match_date[:10],
                "opponent": opp,
                "minutes": p_stat.minutes_played,
                "pts": p_stat.points,
                "reb": int(extra.get("reb", 0) or 0),
                "oreb": int(extra.get("oreb", 0) or 0),
                "dreb": int(extra.get("dreb", 0) or 0),
                "ast": p_stat.assists,
                "stl": int(extra.get("stl", 0) or 0),
                "blk": int(extra.get("blk", 0) or 0),
                "to": int(extra.get("to", 0) or 0),
                "pf": int(extra.get("pf", 0) or 0),
                "plus_minus": int(extra.get("plus_minus", 0) or 0),
                "fg_str": f"{fgm}-{fga}",
                "fg_pct": extra.get("fg_pct", round((fgm/fga*100), 1) if fga > 0 else 0.0),
                "fg3_str": f"{fg3m}-{fg3a}",
                "fg3_pct": extra.get("fg3_pct", round((fg3m/fg3a*100), 1) if fg3a > 0 else 0.0),
                "ft_str": f"{ftm}-{fta}",
                "ft_pct": extra.get("ft_pct", round((ftm/fta*100), 1) if fta > 0 else 0.0),
                "efg_pct": extra.get("efg_pct", round(((fgm + 0.5 * fg3m)/fga*100), 1) if fga > 0 else 0.0),
                "ts_pct": extra.get("ts_pct", round((p_stat.points / (2 * (fga + 0.44 * fta)) * 100), 1) if (fga + 0.44 * fta) > 0 else 0.0),
                "game_score": extra.get("game_score", 0.0)
            })

        return {
            "player_name": player_name,
            "team_name": team_name,
            "player_type": player_type,
            "rolling_games": rolling_games,
            "rolling_days": rolling_days,
            "recent_game_logs": recent_logs
        }
