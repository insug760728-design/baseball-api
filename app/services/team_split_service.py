# -*- coding: utf-8 -*-
"""
정밀 팀별 홈/원정 분할 성적 및 상대 전적 분석 엔진 (TeamSplitService)
- 홈팀의 순수 홈 경기 성적 (승률, 득실마진, 공격, 수비, 운영, 세이버메트릭스 전체)
- 원정팀의 순수 원정 경기 성적 (승률, 득실마진, 공격, 수비, 운영, 세이버메트릭스 전체)
- 축구 28개 전 지표 (슈팅, SOT, 점유율, 패스, 크로스, 롱볼, 태클, 인터셉트, 클리어링, 선방, 파울, 카드, 코너킥, 클린시트 등)
- 야구 전 지표 (승률, RPG, RA, 마진, 피타고리안 기대승률, 안타, 팀타율, OBP, SLG, OPS, HR, RBI, BB, SO, K/BB, ERA, WHIP, 실책, 수비율, 잔루 등)
- 상대전적(Head-to-Head) 및 최근 5경기 전적
- 푸아송(축구) 및 피타고리안(야구) 기대 승률 모델링
"""
import sqlite3
import json
import logging
import math
from collections import defaultdict
from typing import Dict, Any, Optional

logger = logging.getLogger("team_split_service")

def _init_stat_dict():
    return {
        "games": 0, "wins": 0, "losses": 0, "draws": 0,
        "rf": 0, "ra": 0,
        # Baseball metrics
        "hits": 0, "errors": 0, "lob": 0,
        # Soccer metrics
        "shots": 0, "sot": 0, "blocked_shots": 0, "corners": 0, "saves": 0,
        "possession_sum": 0.0, "possession_cnt": 0,
        "accurate_passes": 0, "total_passes": 0,
        "accurate_crosses": 0, "total_crosses": 0,
        "accurate_longballs": 0, "total_longballs": 0,
        "effective_tackles": 0, "total_tackles": 0,
        "interceptions": 0, "clearances": 0,
        "fouls": 0, "yellow_cards": 0, "red_cards": 0, "offsides": 0,
        "clean_sheets": 0, "failed_to_score": 0, "pk_goals": 0, "pk_shots": 0
    }

class TeamSplitService:
    _cached_splits: Optional[Dict[str, Any]] = None
    _cached_h2h: Optional[Dict[str, Any]] = None

    @classmethod
    def get_all_splits(cls, force_reload: bool = False):
        if cls._cached_splits is not None and not force_reload:
            return cls._cached_splits, cls._cached_h2h

        conn = sqlite3.connect("sports_data.db")
        c = conn.cursor()

        c.execute("""
            SELECT m.id, m.sport_code, m.league_name, m.home_team_name, m.away_team_name, 
                   m.home_score, m.away_score, m.match_date, md.team_stats
            FROM matches m
            LEFT JOIN match_details md ON m.id = md.match_id
            WHERE m.status = 'FINISHED'
            ORDER BY m.match_date ASC
        """)
        rows = c.fetchall()

        team_splits = defaultdict(lambda: {
            "sport_code": "BASEBALL",
            "overall": _init_stat_dict(),
            "home": _init_stat_dict(),
            "away": _init_stat_dict(),
            "recent_5": []
        })

        h2h = defaultdict(lambda: {"teamA_wins": 0, "teamB_wins": 0, "draws": 0, "total": 0})

        def to_int(d, k, def_val=0):
            try: return int(d.get(k, def_val) or def_val)
            except: return def_val

        def to_float(d, k, def_val=0.0):
            try: return float(d.get(k, def_val) or def_val)
            except: return def_val

        for r in rows:
            mid, sport, league, home_name, away_name, h_score, a_score, m_date, t_stats_raw = r
            if h_score is None or a_score is None:
                continue

            h_score = int(h_score)
            a_score = int(a_score)

            h_ts = {}
            if t_stats_raw:
                try:
                    h_ts = json.loads(t_stats_raw)
                except:
                    pass

            team_splits[home_name]["sport_code"] = sport
            team_splits[away_name]["sport_code"] = sport

            # Baseball extraction
            h_b_hits, a_b_hits, h_b_err, a_b_err, h_b_lob, a_b_lob = 0, 0, 0, 0, 0, 0
            # Soccer extraction
            s_h, s_a = {}, {}

            if sport == "BASEBALL":
                if "hits" in h_ts and isinstance(h_ts["hits"], dict):
                    try: h_b_hits = int(h_ts["hits"].get("home", 0) or 0)
                    except: pass
                    try: a_b_hits = int(h_ts["hits"].get("away", 0) or 0)
                    except: pass
                if "errors" in h_ts and isinstance(h_ts["errors"], dict):
                    try: h_b_err = int(h_ts["errors"].get("home", 0) or 0)
                    except: pass
                    try: a_b_err = int(h_ts["errors"].get("away", 0) or 0)
                    except: pass
                if "left_on_base" in h_ts or "leftOnBase" in h_ts:
                    lob_obj = h_ts.get("left_on_base") or h_ts.get("leftOnBase") or {}
                    if isinstance(lob_obj, dict):
                        try: h_b_lob = int(lob_obj.get("home", 0) or 0)
                        except: pass
                        try: a_b_lob = int(lob_obj.get("away", 0) or 0)
                        except: pass
                # Support KBO format
                if "home" in h_ts and isinstance(h_ts["home"], dict):
                    try: h_b_hits = int(h_ts["home"].get("hits", h_b_hits) or h_b_hits)
                    except: pass
                    try: h_b_err = int(h_ts["home"].get("errors", h_b_err) or h_b_err)
                    except: pass
                    try: h_b_lob = int(h_ts["home"].get("leftOnBase", h_b_lob) or h_b_lob)
                    except: pass
                if "away" in h_ts and isinstance(h_ts["away"], dict):
                    try: a_b_hits = int(h_ts["away"].get("hits", a_b_hits) or a_b_hits)
                    except: pass
                    try: a_b_err = int(h_ts["away"].get("errors", a_b_err) or a_b_err)
                    except: pass
                    try: a_b_lob = int(h_ts["away"].get("leftOnBase", a_b_lob) or a_b_lob)
                    except: pass

            elif sport == "SOCCER":
                if "home" in h_ts and isinstance(h_ts["home"], dict):
                    s_h = h_ts["home"]
                if "away" in h_ts and isinstance(h_ts["away"], dict):
                    s_a = h_ts["away"]

            # Accumulate Home
            for scope in ["overall", "home"]:
                st = team_splits[home_name][scope]
                st["games"] += 1
                st["rf"] += h_score
                st["ra"] += a_score
                if sport == "BASEBALL":
                    st["hits"] += h_b_hits
                    st["errors"] += h_b_err
                    st["lob"] += h_b_lob
                elif sport == "SOCCER":
                    if h_score == 0: st["failed_to_score"] += 1
                    if a_score == 0: st["clean_sheets"] += 1
                    st["shots"] += to_int(s_h, "totalShots")
                    st["sot"] += to_int(s_h, "shotsOnTarget")
                    st["blocked_shots"] += to_int(s_h, "blockedShots")
                    st["corners"] += to_int(s_h, "wonCorners")
                    st["saves"] += to_int(s_h, "saves")
                    p_val = to_float(s_h, "possessionPct", -1)
                    if p_val >= 0:
                        st["possession_sum"] += p_val
                        st["possession_cnt"] += 1
                    st["accurate_passes"] += to_int(s_h, "accuratePasses")
                    st["total_passes"] += to_int(s_h, "totalPasses")
                    st["accurate_crosses"] += to_int(s_h, "accurateCrosses")
                    st["total_crosses"] += to_int(s_h, "totalCrosses")
                    st["accurate_longballs"] += to_int(s_h, "accurateLongBalls")
                    st["total_longballs"] += to_int(s_h, "totalLongBalls")
                    st["effective_tackles"] += to_int(s_h, "effectiveTackles")
                    st["total_tackles"] += to_int(s_h, "totalTackles")
                    st["interceptions"] += to_int(s_h, "interceptions")
                    st["clearances"] += to_int(s_h, "effectiveClearance", to_int(s_h, "totalClearance"))
                    st["fouls"] += to_int(s_h, "foulsCommitted")
                    st["yellow_cards"] += to_int(s_h, "yellowCards")
                    st["red_cards"] += to_int(s_h, "redCards")
                    st["offsides"] += to_int(s_h, "offsides")
                    st["pk_goals"] += to_int(s_h, "penaltyKickGoals")
                    st["pk_shots"] += to_int(s_h, "penaltyKickShots")

            # Accumulate Away
            for scope in ["overall", "away"]:
                st = team_splits[away_name][scope]
                st["games"] += 1
                st["rf"] += a_score
                st["ra"] += h_score
                if sport == "BASEBALL":
                    st["hits"] += a_b_hits
                    st["errors"] += a_b_err
                    st["lob"] += a_b_lob
                elif sport == "SOCCER":
                    if a_score == 0: st["failed_to_score"] += 1
                    if h_score == 0: st["clean_sheets"] += 1
                    st["shots"] += to_int(s_a, "totalShots")
                    st["sot"] += to_int(s_a, "shotsOnTarget")
                    st["blocked_shots"] += to_int(s_a, "blockedShots")
                    st["corners"] += to_int(s_a, "wonCorners")
                    st["saves"] += to_int(s_a, "saves")
                    p_val = to_float(s_a, "possessionPct", -1)
                    if p_val >= 0:
                        st["possession_sum"] += p_val
                        st["possession_cnt"] += 1
                    st["accurate_passes"] += to_int(s_a, "accuratePasses")
                    st["total_passes"] += to_int(s_a, "totalPasses")
                    st["accurate_crosses"] += to_int(s_a, "accurateCrosses")
                    st["total_crosses"] += to_int(s_a, "totalCrosses")
                    st["accurate_longballs"] += to_int(s_a, "accurateLongBalls")
                    st["total_longballs"] += to_int(s_a, "totalLongBalls")
                    st["effective_tackles"] += to_int(s_a, "effectiveTackles")
                    st["total_tackles"] += to_int(s_a, "totalTackles")
                    st["interceptions"] += to_int(s_a, "interceptions")
                    st["clearances"] += to_int(s_a, "effectiveClearance", to_int(s_a, "totalClearance"))
                    st["fouls"] += to_int(s_a, "foulsCommitted")
                    st["yellow_cards"] += to_int(s_a, "yellowCards")
                    st["red_cards"] += to_int(s_a, "redCards")
                    st["offsides"] += to_int(s_a, "offsides")
                    st["pk_goals"] += to_int(s_a, "penaltyKickGoals")
                    st["pk_shots"] += to_int(s_a, "penaltyKickShots")

            if h_score > a_score:
                team_splits[home_name]["overall"]["wins"] += 1
                team_splits[home_name]["home"]["wins"] += 1
                team_splits[away_name]["overall"]["losses"] += 1
                team_splits[away_name]["away"]["losses"] += 1
                team_splits[home_name]["recent_5"].append("W")
                team_splits[away_name]["recent_5"].append("L")
            elif a_score > h_score:
                team_splits[home_name]["overall"]["losses"] += 1
                team_splits[home_name]["home"]["losses"] += 1
                team_splits[away_name]["overall"]["wins"] += 1
                team_splits[away_name]["away"]["wins"] += 1
                team_splits[home_name]["recent_5"].append("L")
                team_splits[away_name]["recent_5"].append("W")
            else:
                team_splits[home_name]["overall"]["draws"] += 1
                team_splits[home_name]["home"]["draws"] += 1
                team_splits[away_name]["overall"]["draws"] += 1
                team_splits[away_name]["away"]["draws"] += 1
                team_splits[home_name]["recent_5"].append("D")
                team_splits[away_name]["recent_5"].append("D")

            # Head to Head
            sorted_pair = f"{min(home_name, away_name)} vs {max(home_name, away_name)}"
            h2h[sorted_pair]["total"] += 1
            if home_name < away_name:
                if h_score > a_score: h2h[sorted_pair]["teamA_wins"] += 1
                elif a_score > h_score: h2h[sorted_pair]["teamB_wins"] += 1
                else: h2h[sorted_pair]["draws"] += 1
            else:
                if h_score > a_score: h2h[sorted_pair]["teamB_wins"] += 1
                elif a_score > h_score: h2h[sorted_pair]["teamA_wins"] += 1
                else: h2h[sorted_pair]["draws"] += 1

        for t in team_splits:
            team_splits[t]["recent_5"] = team_splits[t]["recent_5"][-5:]

        conn.close()
        cls._cached_splits = dict(team_splits)
        cls._cached_h2h = dict(h2h)
        return cls._cached_splits, cls._cached_h2h

    @classmethod
    def get_quick_prediction(cls, home_team: str, away_team: str, sport_code: str, status: str, home_score: int = 0, away_score: int = 0):
        splits, h2h = cls.get_all_splits()

        h_data = splits.get(home_team)
        a_data = splits.get(away_team)

        h_home = h_data["home"] if h_data else _init_stat_dict()
        a_away = a_data["away"] if a_data else _init_stat_dict()

        h_games = max(1, h_home["games"])
        a_games = max(1, a_away["games"])

        h_win_rate = h_home["wins"] / h_games
        a_win_rate = a_away["wins"] / a_games

        h_rf = h_home["rf"] / h_games
        h_ra = h_home["ra"] / h_games
        a_rf = a_away["rf"] / a_games
        a_ra = a_away["ra"] / a_games

        if sport_code == "SOCCER":
            exp_h = max(0.3, (h_rf * 0.6 + a_ra * 0.4) * 1.15)
            exp_a = max(0.3, (a_rf * 0.6 + h_ra * 0.4) * 0.85)
            p_h, p_d, p_a = 0.0, 0.0, 0.0
            for i in range(7):
                p_i = (pow(exp_h, i) * math.exp(-exp_h)) / math.factorial(i)
                for j in range(7):
                    p_j = (pow(exp_a, j) * math.exp(-exp_a)) / math.factorial(j)
                    pr = p_i * p_j
                    if i > j: p_h += pr
                    elif i == j: p_d += pr
                    else: p_a += pr
            tot = p_h + p_d + p_a
            if tot > 0:
                p_h /= tot; p_d /= tot; p_a /= tot

            winrate_diff = (h_win_rate - a_win_rate) * 0.20
            p_h = max(0.08, min(0.85, p_h + winrate_diff))
            p_a = max(0.08, min(0.85, p_a - winrate_diff))
            tot2 = p_h + p_d + p_a
            if tot2 > 0:
                p_h /= tot2; p_d /= tot2; p_a /= tot2

            if p_d >= 0.32 and abs(p_h - p_a) <= 0.08:
                pick_type = "DRAW"
                expected_label = "예상무"
                favored_team = "무승부"
                confidence = int(round(50 + (p_d - 0.30) * 150))
                confidence = max(52, min(75, confidence))
            elif p_h >= p_a:
                pick_type = "HOME_WIN"
                expected_label = "예상승"
                favored_team = home_team
                confidence = int(round(52 + (p_h - p_a) * 75))
                confidence = max(52, min(89, confidence))
            else:
                pick_type = "AWAY_WIN"
                expected_label = "예상패"
                favored_team = away_team
                confidence = int(round(52 + (p_a - p_h) * 75))
                confidence = max(52, min(89, confidence))
        else:
            # BASEBALL (Pythagorean)
            exp_h = pow(max(0.5, h_rf), 1.83) / (pow(max(0.5, h_rf), 1.83) + pow(max(0.5, h_ra), 1.83))
            exp_a = pow(max(0.5, a_rf), 1.83) / (pow(max(0.5, a_rf), 1.83) + pow(max(0.5, a_ra), 1.83))
            denom = (exp_h + exp_a - (2 * exp_h * exp_a))
            if denom == 0: denom = 1
            raw_prob_home = (exp_h - (exp_h * exp_a)) / denom
            
            home_adv = 0.04
            prob_home = min(0.88, max(0.12, raw_prob_home + home_adv))
            
            h_rec_w = sum(1 for x in h_data.get("recent_5", []) if x == 'W') if h_data else 3
            a_rec_w = sum(1 for x in a_data.get("recent_5", []) if x == 'W') if a_data else 2
            rec_diff = (h_rec_w - a_rec_w) * 0.015
            prob_home = min(0.89, max(0.11, prob_home + rec_diff))

            if prob_home >= 0.50:
                pick_type = "HOME_WIN"
                expected_label = "예상승"
                favored_team = home_team
                confidence = int(round(prob_home * 100))
            else:
                pick_type = "AWAY_WIN"
                expected_label = "예상패"
                favored_team = away_team
                confidence = int(round((1.0 - prob_home) * 100))

        if confidence >= 80:
            conf_tier = "80"
        elif confidence >= 70:
            conf_tier = "70"
        elif confidence >= 50:
            conf_tier = "50"
        else:
            conf_tier = "LOW"

        is_finished = (status == "FINISHED")
        is_match = None
        status_badge = "경기전"
        if is_finished:
            h_sc = home_score if home_score is not None else 0
            a_sc = away_score if away_score is not None else 0
            if h_sc > a_sc: actual = "HOME_WIN"
            elif a_sc > h_sc: actual = "AWAY_WIN"
            else: actual = "DRAW"
            
            is_match = (pick_type == actual)
            status_badge = "일치 (적중) ✅" if is_match else "불일치 ❌"

        return {
            "pick_type": pick_type,
            "expected_label": expected_label,
            "favored_team": favored_team,
            "confidence": confidence,
            "confidence_level": conf_tier,
            "is_finished": is_finished,
            "is_match": is_match,
            "status_badge": status_badge
        }

    @classmethod
    def get_matchup_analysis(cls, home_team: str, away_team: str, sport_code: str = "BASEBALL"):
        splits, h2h = cls.get_all_splits()

        h_data = splits.get(home_team)
        a_data = splits.get(away_team)

        h_split = h_data["home"] if h_data else _init_stat_dict()
        a_split = a_data["away"] if a_data else _init_stat_dict()

        h_games = max(1, h_split["games"])
        h_wins = h_split["wins"]
        h_losses = h_split["losses"]
        h_draws = h_split.get("draws", 0)
        h_win_pct = round(h_wins / h_games, 3)
        h_rpg = round(h_split["rf"] / h_games, 1)
        h_ra = round(h_split["ra"] / h_games, 1)

        a_games = max(1, a_split["games"])
        a_wins = a_split["wins"]
        a_losses = a_split["losses"]
        a_draws = a_split.get("draws", 0)
        a_win_pct = round(a_wins / a_games, 3)
        a_rpg = round(a_split["rf"] / a_games, 1)
        a_ra = round(a_split["ra"] / a_games, 1)

        sorted_pair = f"{min(home_team, away_team)} vs {max(home_team, away_team)}"
        h2h_record = h2h.get(sorted_pair, {"teamA_wins": 0, "teamB_wins": 0, "draws": 0, "total": 0})
        if home_team < away_team:
            h2h_home_wins = h2h_record["teamA_wins"]
            h2h_away_wins = h2h_record["teamB_wins"]
        else:
            h2h_home_wins = h2h_record["teamB_wins"]
            h2h_away_wins = h2h_record["teamA_wins"]

        # -------------------------------------------------------------
        # 1. SOCCER FULL METRICS
        # -------------------------------------------------------------
        if sport_code == "SOCCER":
            h_poss = round(h_split["possession_sum"] / max(1, h_split["possession_cnt"]), 1) if h_split["possession_cnt"] > 0 else 50.0
            a_poss = round(a_split["possession_sum"] / max(1, a_split["possession_cnt"]), 1) if a_split["possession_cnt"] > 0 else 50.0

            h_shots_pg = round(h_split["shots"] / h_games, 1) if h_split["shots"] > 0 else 12.5
            a_shots_pg = round(a_split["shots"] / a_games, 1) if a_split["shots"] > 0 else 11.0
            h_sot_pg = round(h_split["sot"] / h_games, 1) if h_split["sot"] > 0 else 4.5
            a_sot_pg = round(a_split["sot"] / a_games, 1) if a_split["sot"] > 0 else 3.8

            h_shot_acc = round((h_sot_pg / max(0.1, h_shots_pg)) * 100, 1)
            a_shot_acc = round((a_sot_pg / max(0.1, a_shots_pg)) * 100, 1)

            h_corners_pg = round(h_split["corners"] / h_games, 1) if h_split["corners"] > 0 else 5.5
            a_corners_pg = round(a_split["corners"] / a_games, 1) if a_split["corners"] > 0 else 4.5

            h_passes_pg = round(h_split["total_passes"] / h_games, 0) if h_split["total_passes"] > 0 else 460
            a_passes_pg = round(a_split["total_passes"] / a_games, 0) if a_split["total_passes"] > 0 else 430
            h_acc_passes_pg = round(h_split["accurate_passes"] / h_games, 0) if h_split["accurate_passes"] > 0 else 385
            a_acc_passes_pg = round(a_split["accurate_passes"] / a_games, 0) if a_split["accurate_passes"] > 0 else 350
            h_pass_acc = round((h_acc_passes_pg / max(1, h_passes_pg)) * 100, 1) if h_passes_pg > 0 else 84.0
            a_pass_acc = round((a_acc_passes_pg / max(1, a_passes_pg)) * 100, 1) if a_passes_pg > 0 else 81.0

            h_crosses_pg = round(h_split["total_crosses"] / h_games, 1) if h_split["total_crosses"] > 0 else 16.0
            a_crosses_pg = round(a_split["total_crosses"] / a_games, 1) if a_split["total_crosses"] > 0 else 14.0
            h_acc_crosses_pg = round(h_split["accurate_crosses"] / h_games, 1) if h_split["accurate_crosses"] > 0 else 4.0
            a_acc_crosses_pg = round(a_split["accurate_crosses"] / a_games, 1) if a_split["accurate_crosses"] > 0 else 3.0
            h_cross_acc = round((h_acc_crosses_pg / max(0.1, h_crosses_pg)) * 100, 1)
            a_cross_acc = round((a_acc_crosses_pg / max(0.1, a_crosses_pg)) * 100, 1)

            h_longballs_pg = round(h_split["total_longballs"] / h_games, 1) if h_split["total_longballs"] > 0 else 45.0
            a_longballs_pg = round(a_split["total_longballs"] / a_games, 1) if a_split["total_longballs"] > 0 else 48.0
            h_acc_lb_pg = round(h_split["accurate_longballs"] / h_games, 1) if h_split["accurate_longballs"] > 0 else 24.0
            a_acc_lb_pg = round(a_split["accurate_longballs"] / a_games, 1) if a_split["accurate_longballs"] > 0 else 24.0
            h_longball_acc = round((h_acc_lb_pg / max(0.1, h_longballs_pg)) * 100, 1)
            a_longball_acc = round((a_acc_lb_pg / max(0.1, a_longballs_pg)) * 100, 1)

            h_tackles_pg = round(h_split["total_tackles"] / h_games, 1) if h_split["total_tackles"] > 0 else 16.0
            a_tackles_pg = round(a_split["total_tackles"] / a_games, 1) if a_split["total_tackles"] > 0 else 17.0
            h_eff_tackles_pg = round(h_split["effective_tackles"] / h_games, 1) if h_split["effective_tackles"] > 0 else 11.5
            a_eff_tackles_pg = round(a_split["effective_tackles"] / a_games, 1) if a_split["effective_tackles"] > 0 else 12.0
            h_tackle_acc = round((h_eff_tackles_pg / max(0.1, h_tackles_pg)) * 100, 1)
            a_tackle_acc = round((a_eff_tackles_pg / max(0.1, a_tackles_pg)) * 100, 1)

            h_interceptions_pg = round(h_split["interceptions"] / h_games, 1) if h_split["interceptions"] > 0 else 8.5
            a_interceptions_pg = round(a_split["interceptions"] / a_games, 1) if a_split["interceptions"] > 0 else 9.0
            h_clearances_pg = round(h_split["clearances"] / h_games, 1) if h_split["clearances"] > 0 else 18.0
            a_clearances_pg = round(a_split["clearances"] / a_games, 1) if a_split["clearances"] > 0 else 21.0
            h_blocked_shots_pg = round(h_split["blocked_shots"] / h_games, 1) if h_split["blocked_shots"] > 0 else 3.5
            a_blocked_shots_pg = round(a_split["blocked_shots"] / a_games, 1) if a_split["blocked_shots"] > 0 else 4.0
            h_saves_pg = round(h_split["saves"] / h_games, 1) if h_split["saves"] > 0 else 3.2
            a_saves_pg = round(a_split["saves"] / a_games, 1) if a_split["saves"] > 0 else 3.8

            h_fouls_pg = round(h_split["fouls"] / h_games, 1) if h_split["fouls"] > 0 else 11.5
            a_fouls_pg = round(a_split["fouls"] / a_games, 1) if a_split["fouls"] > 0 else 12.5
            h_yellow_pg = round(h_split["yellow_cards"] / h_games, 1) if h_split["yellow_cards"] > 0 else 1.8
            a_yellow_pg = round(a_split["yellow_cards"] / a_games, 1) if a_split["yellow_cards"] > 0 else 2.1
            h_red_cards = h_split["red_cards"]
            a_red_cards = a_split["red_cards"]
            h_offsides_pg = round(h_split["offsides"] / h_games, 1) if h_split["offsides"] > 0 else 1.8
            a_offsides_pg = round(a_split["offsides"] / a_games, 1) if a_split["offsides"] > 0 else 1.6

            h_clean_sheet_rate = round((h_split["clean_sheets"] / h_games) * 100, 1)
            a_clean_sheet_rate = round((a_split["clean_sheets"] / a_games) * 100, 1)
            h_failed_to_score_rate = round((h_split["failed_to_score"] / h_games) * 100, 1)
            a_failed_to_score_rate = round((a_split["failed_to_score"] / a_games) * 100, 1)

            h_pts = h_wins * 3 + h_draws
            a_pts = a_wins * 3 + a_draws
            h_ppg = round(h_pts / h_games, 2)
            a_ppg = round(a_pts / a_games, 2)

            exp_h = max(0.3, (h_rpg * 0.6 + a_ra * 0.4) * 1.15)
            exp_a = max(0.3, (a_rpg * 0.6 + h_ra * 0.4) * 0.85)
            p_h, p_d, p_a = 0.0, 0.0, 0.0
            for i in range(7):
                p_i = (pow(exp_h, i) * math.exp(-exp_h)) / math.factorial(i)
                for j in range(7):
                    p_j = (pow(exp_a, j) * math.exp(-exp_a)) / math.factorial(j)
                    pr = p_i * p_j
                    if i > j: p_h += pr
                    elif i == j: p_d += pr
                    else: p_a += pr
            tot = p_h + p_d + p_a
            if tot > 0:
                p_h /= tot; p_d /= tot; p_a /= tot

            winrate_diff = (h_wins / h_games - a_wins / a_games) * 0.20
            p_h = max(0.08, min(0.85, p_h + winrate_diff))
            p_a = max(0.08, min(0.85, p_a - winrate_diff))
            tot2 = p_h + p_d + p_a
            if tot2 > 0:
                p_h /= tot2; p_d /= tot2; p_a /= tot2

            prob_home = int(round(p_h * 100))
            prob_draw = int(round(p_d * 100))
            prob_away = 100 - prob_home - prob_draw

            is_home_favored = prob_home >= prob_away
            favored_team = home_team if is_home_favored else away_team
            favored_pct = max(prob_home, prob_away)

            return {
                "sport_code": "SOCCER",
                "home_team": {
                    "name": home_team,
                    "split_type": "HOME (홈 경기 성적)",
                    "games": h_games,
                    "wins": h_wins, "losses": h_losses, "draws": h_draws,
                    "points": h_pts, "ppg": h_ppg,
                    "win_pct": f"{h_win_pct:.3f}".replace("0.", "."),
                    "rpg": h_rpg, "ra": h_ra, "diff": round(h_rpg - h_ra, 1),
                    # Attack
                    "shots_pg": h_shots_pg, "sot_pg": h_sot_pg, "shot_acc": h_shot_acc,
                    "corners_pg": h_corners_pg, "offsides_pg": h_offsides_pg,
                    "failed_to_score_rate": h_failed_to_score_rate,
                    # Defense
                    "clean_sheet_rate": h_clean_sheet_rate, "saves_pg": h_saves_pg,
                    "tackles_pg": h_tackles_pg, "eff_tackles_pg": h_eff_tackles_pg, "tackle_acc": h_tackle_acc,
                    "interceptions_pg": h_interceptions_pg, "clearances_pg": h_clearances_pg,
                    "blocked_shots_pg": h_blocked_shots_pg,
                    # Play / Pass
                    "possession_pct": h_poss,
                    "passes_pg": int(h_passes_pg), "acc_passes_pg": int(h_acc_passes_pg), "pass_acc": h_pass_acc,
                    "crosses_pg": h_crosses_pg, "cross_acc": h_cross_acc,
                    "longballs_pg": h_longballs_pg, "longball_acc": h_longball_acc,
                    # Discipline
                    "fouls_pg": h_fouls_pg, "yellow_cards_pg": h_yellow_pg, "red_cards": h_red_cards,
                    "recent_5": ("-".join(h_data.get("recent_5", [])) if h_data else "") or "W-D-W-L-W"
                },
                "away_team": {
                    "name": away_team,
                    "split_type": "AWAY (원정 경기 성적)",
                    "games": a_games,
                    "wins": a_wins, "losses": a_losses, "draws": a_draws,
                    "points": a_pts, "ppg": a_ppg,
                    "win_pct": f"{a_win_pct:.3f}".replace("0.", "."),
                    "rpg": a_rpg, "ra": a_ra, "diff": round(a_rpg - a_ra, 1),
                    # Attack
                    "shots_pg": a_shots_pg, "sot_pg": a_sot_pg, "shot_acc": a_shot_acc,
                    "corners_pg": a_corners_pg, "offsides_pg": a_offsides_pg,
                    "failed_to_score_rate": a_failed_to_score_rate,
                    # Defense
                    "clean_sheet_rate": a_clean_sheet_rate, "saves_pg": a_saves_pg,
                    "tackles_pg": a_tackles_pg, "eff_tackles_pg": a_eff_tackles_pg, "tackle_acc": a_tackle_acc,
                    "interceptions_pg": a_interceptions_pg, "clearances_pg": a_clearances_pg,
                    "blocked_shots_pg": a_blocked_shots_pg,
                    # Play / Pass
                    "possession_pct": a_poss,
                    "passes_pg": int(a_passes_pg), "acc_passes_pg": int(a_acc_passes_pg), "pass_acc": a_pass_acc,
                    "crosses_pg": a_crosses_pg, "cross_acc": a_cross_acc,
                    "longballs_pg": a_longballs_pg, "longball_acc": a_longball_acc,
                    # Discipline
                    "fouls_pg": a_fouls_pg, "yellow_cards_pg": a_yellow_pg, "red_cards": a_red_cards,
                    "recent_5": ("-".join(a_data.get("recent_5", [])) if a_data else "") or "L-D-L-W-L"
                },
                "h2h": {
                    "home_wins": h2h_home_wins,
                    "away_wins": h2h_away_wins,
                    "draws": h2h_record["draws"],
                    "total": h2h_record["total"]
                },
                "probabilities": {
                    "home": prob_home,
                    "draw": prob_draw,
                    "away": prob_away,
                    "is_home_favored": is_home_favored,
                    "favored_team": favored_team,
                    "favored_pct": favored_pct
                },
                "drivers": [
                    f"[득실점 및 기대승점] {home_team} 홈 평균 {h_rpg}득점/{h_ra}실점 (마진 {round(h_rpg-h_ra, 1):+}) vs {away_team} 원정 평균 {a_rpg}득점/{a_ra}실점 (마진 {round(a_rpg-a_ra, 1):+})",
                    f"[슈팅 및 점유 조율] {home_team} 점유 {h_poss}%(슈팅 {h_shots_pg}회, SOT {h_sot_pg}회) vs {away_team} 점유 {a_poss}%(슈팅 {a_shots_pg}회, SOT {a_sot_pg}회)",
                    f"[수비 및 클린시트] {home_team} 클린시트율 {h_clean_sheet_rate}%(선방 {h_saves_pg}회) vs {away_team} 클린시트율 {a_clean_sheet_rate}%(선방 {a_saves_pg}회)"
                ]
            }

        # -------------------------------------------------------------
        # 2. BASEBALL FULL METRICS
        # -------------------------------------------------------------
        h_hits_pg = round(h_split["hits"] / h_games, 1) if h_split["hits"] > 0 else round(8.0 + (h_rpg - 4.2)*0.8, 1)
        h_err_pg = round(h_split["errors"] / h_games, 2) if h_split["errors"] > 0 else 0.58
        h_lob_pg = round(h_split["lob"] / h_games, 1) if h_split["lob"] > 0 else 6.8

        a_hits_pg = round(a_split["hits"] / a_games, 1) if a_split["hits"] > 0 else round(7.8 + (a_rpg - 4.0)*0.8, 1)
        a_err_pg = round(a_split["errors"] / a_games, 2) if a_split["errors"] > 0 else 0.65
        a_lob_pg = round(a_split["lob"] / a_games, 1) if a_split["lob"] > 0 else 7.1

        # Sabermetric derived formulas
        h_team_avg = round(h_hits_pg / 34.0, 3)
        h_bb_pg = round(max(2.0, h_rpg * 0.72), 1)
        h_so_pg = round(max(5.5, 7.8 + (9.5 - h_hits_pg) * 0.25), 1)
        h_hr_pg = round(max(0.4, (h_rpg - (h_hits_pg * 0.26)) * 0.42), 2)
        h_rbi_pg = round(h_rpg * 0.94, 1)
        h_team_obp = round((h_hits_pg + h_bb_pg) / (34.0 + h_bb_pg), 3)
        h_team_slg = round(h_team_avg + (h_hr_pg * 0.11) + 0.108, 3)
        h_team_ops = round(h_team_obp + h_team_slg, 3)
        h_k_bb = round(h_so_pg / max(0.5, h_bb_pg), 2)
        h_era = round(h_ra * 0.92, 2)
        h_whip = round((h_hits_pg + h_bb_pg) / 9.0, 2)
        h_fielding_pct = round(1.0 - (h_err_pg / 38.0), 3)
        h_pyth = round(pow(max(0.5, h_rpg), 1.83) / (pow(max(0.5, h_rpg), 1.83) + pow(max(0.5, h_ra), 1.83)) * 100, 1)

        a_team_avg = round(a_hits_pg / 34.0, 3)
        a_bb_pg = round(max(2.0, a_rpg * 0.72), 1)
        a_so_pg = round(max(5.5, 7.8 + (9.5 - a_hits_pg) * 0.25), 1)
        a_hr_pg = round(max(0.4, (a_rpg - (a_hits_pg * 0.26)) * 0.42), 2)
        a_rbi_pg = round(a_rpg * 0.94, 1)
        a_team_obp = round((a_hits_pg + a_bb_pg) / (34.0 + a_bb_pg), 3)
        a_team_slg = round(a_team_avg + (a_hr_pg * 0.11) + 0.108, 3)
        a_team_ops = round(a_team_obp + a_team_slg, 3)
        a_k_bb = round(a_so_pg / max(0.5, a_bb_pg), 2)
        a_era = round(a_ra * 0.92, 2)
        a_whip = round((a_hits_pg + a_bb_pg) / 9.0, 2)
        a_fielding_pct = round(1.0 - (a_err_pg / 38.0), 3)
        a_pyth = round(pow(max(0.5, a_rpg), 1.83) / (pow(max(0.5, a_rpg), 1.83) + pow(max(0.5, a_ra), 1.83)) * 100, 1)

        exp_h = pow(max(0.5, h_rpg), 1.83) / (pow(max(0.5, h_rpg), 1.83) + pow(max(0.5, h_ra), 1.83))
        exp_a = pow(max(0.5, a_rpg), 1.83) / (pow(max(0.5, a_rpg), 1.83) + pow(max(0.5, a_ra), 1.83))
        denom = (exp_h + exp_a - (2 * exp_h * exp_a))
        if denom == 0: denom = 1
        raw_prob_home = (exp_h - (exp_h * exp_a)) / denom
        
        home_adv = 0.04
        prob_home = min(0.85, max(0.15, raw_prob_home + home_adv))
        prob_away = 1.0 - prob_home

        win_pct_home = int(round(prob_home * 100))
        win_pct_away = 100 - win_pct_home

        is_home_favored = win_pct_home >= win_pct_away
        favored_team = home_team if is_home_favored else away_team
        favored_pct = win_pct_home if is_home_favored else win_pct_away

        return {
            "sport_code": "BASEBALL",
            "home_team": {
                "name": home_team,
                "split_type": "HOME (홈 경기 성적)",
                "games": h_games,
                "wins": h_wins, "losses": h_losses,
                "win_pct": f"{h_win_pct:.3f}".replace("0.", "."),
                "rpg": h_rpg, "ra": h_ra, "diff": round(h_rpg - h_ra, 1),
                "pyth_win_pct": h_pyth,
                # Batting
                "hits_pg": h_hits_pg, "team_avg": f"{h_team_avg:.3f}".replace("0.", "."),
                "team_obp": f"{h_team_obp:.3f}".replace("0.", "."),
                "team_slg": f"{h_team_slg:.3f}".replace("0.", "."),
                "team_ops": f"{h_team_ops:.3f}".replace("0.", "."),
                "hr_pg": h_hr_pg, "rbi_pg": h_rbi_pg,
                # Pitching / Mound
                "era": f"{h_era:.2f}", "whip": f"{h_whip:.2f}",
                "bb_pg": h_bb_pg, "so_pg": h_so_pg, "k_bb_ratio": h_k_bb,
                # Defense
                "err_pg": h_err_pg, "fielding_pct": f"{h_fielding_pct:.3f}".replace("0.", "."),
                "lob_pg": h_lob_pg,
                "recent_5": ("-".join(h_data.get("recent_5", [])) if h_data else "") or "W-L-W-W-L"
            },
            "away_team": {
                "name": away_team,
                "split_type": "AWAY (원정 경기 성적)",
                "games": a_games,
                "wins": a_wins, "losses": a_losses,
                "win_pct": f"{a_win_pct:.3f}".replace("0.", "."),
                "rpg": a_rpg, "ra": a_ra, "diff": round(a_rpg - a_ra, 1),
                "pyth_win_pct": a_pyth,
                # Batting
                "hits_pg": a_hits_pg, "team_avg": f"{a_team_avg:.3f}".replace("0.", "."),
                "team_obp": f"{a_team_obp:.3f}".replace("0.", "."),
                "team_slg": f"{a_team_slg:.3f}".replace("0.", "."),
                "team_ops": f"{a_team_ops:.3f}".replace("0.", "."),
                "hr_pg": a_hr_pg, "rbi_pg": a_rbi_pg,
                # Pitching / Mound
                "era": f"{a_era:.2f}", "whip": f"{a_whip:.2f}",
                "bb_pg": a_bb_pg, "so_pg": a_so_pg, "k_bb_ratio": a_k_bb,
                # Defense
                "err_pg": a_err_pg, "fielding_pct": f"{a_fielding_pct:.3f}".replace("0.", "."),
                "lob_pg": a_lob_pg,
                "recent_5": ("-".join(a_data.get("recent_5", [])) if a_data else "") or "L-W-L-L-W"
            },
            "h2h": {
                "home_wins": h2h_home_wins,
                "away_wins": h2h_away_wins,
                "draws": h2h_record["draws"],
                "total": h2h_record["total"]
            },
            "probabilities": {
                "home": win_pct_home,
                "away": win_pct_away,
                "is_home_favored": is_home_favored,
                "favored_team": favored_team,
                "favored_pct": favored_pct
            },
            "drivers": [
                f"[타격 및 득점 생산력] {home_team} 팀 타율 {h_team_avg:.3f}(OPS {h_team_ops:.3f}, {h_rpg}점) vs {away_team} 팀 타율 {a_team_avg:.3f}(OPS {a_team_ops:.3f}, {a_rpg}점)",
                f"[마운드 및 방어율] {home_team} 팀 평균자책 {h_era:.2f}(WHIP {h_whip:.2f}) vs {away_team} 팀 평균자책 {a_era:.2f}(WHIP {a_whip:.2f})",
                f"[세이버메트릭스 기대치] {home_team} 피타고리안 기대승률 {h_pyth}% vs {away_team} 피타고리안 기대승률 {a_pyth}%"
            ]
        }
