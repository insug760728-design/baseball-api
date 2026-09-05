# -*- coding: utf-8 -*-
"""
야구 정밀 롤링 및 세이버메트릭스 분석 엔진 (Analytics Service)
- 타자(Hitters):
  * 클래식: 타율(AVG), 출루율(OBP), 장타율(SLG), OPS
  * 세이버메트릭스: 가중출루율(wOBA), 순수장타율(ISO), 인플레이타구타율(BABIP), 득점기여도(RC),
                   가중득점기여(wRAA), GPA, 볼넷율(BB%), 삼진율(K%), 볼넷/삼진비(BB/K)
- 투수(Pitchers):
  * 클래식: 평균자책점(ERA), 이닝당출루허용률(WHIP), 9이닝당탈삼진(K/9), 9이닝당볼넷(BB/9), 피홈런(HR/9)
  * 세이버메트릭스: 수비무관평균자책점(FIP), DICE, 순탈삼진율(K-BB%), 피BABIP, 잔루율(LOB%), 탈삼진/볼넷비(K/BB)
- 분석 구간:
  * 최근 N경기(By Games): 3경기, 5경기, 7경기, 10경기
  * 최근 N일간(By Days): 최근 3일, 5일, 7일, 10일
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.models import Match, PlayerMatchStat

def ip_to_outs(ip_val: Any) -> int:
    """야구 이닝 표기(예: 6.0, 5.1, 0.2, 5)를 총 아웃카운트로 환산"""
    if ip_val is None:
        return 0
    try:
        s = str(ip_val).strip()
        if not s or s == "-":
            return 0
        if "." in s:
            parts = s.split(".")
            innings = int(parts[0])
            frac = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            # .1은 1아웃, .2는 2아웃
            return innings * 3 + frac
        else:
            return int(float(s)) * 3
    except Exception:
        return 0

def outs_to_ip_str(outs: int) -> str:
    """총 아웃카운트를 야구 이닝 표기(예: '5.2', '6.0')로 환산"""
    if outs <= 0:
        return "0.0"
    innings = outs // 3
    rem = outs % 3
    return f"{innings}.{rem}"

def outs_to_ip_float(outs: int) -> float:
    """총 아웃카운트를 수학적 실수 이닝(예: 16아웃 -> 5.3333...)으로 환산"""
    return outs / 3.0

def compute_hitter_sabermetrics(subset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """타자 세이버메트릭스 정밀 연산"""
    sub_count = len(subset)
    if sub_count == 0:
        return {
            "games_counted": 0,
            "ab": 0, "h": 0, "r": 0, "rbi": 0, "2b": 0, "3b": 0, "hr": 0,
            "bb": 0, "so": 0, "sb": 0, "pa": 0, "tb": 0,
            "avg": ".000", "obp": ".000", "slg": ".000", "ops": ".000",
            "iso": ".000", "babip": ".000", "woba": ".000", "wraa": "0.0",
            "rc": "0.0", "gpa": ".000", "bb_pct": "0.0%", "k_pct": "0.0%", "bb_k": "0.00",
            "wrc_plus": "100",
            "war": "+0.00",
            "exit_velocity": "0.0 mph",
            "launch_angle": "0.0°",
            "barrel_pct": "0.0%",
            "drs": "+0.0",
            "oaa": "+0",
            "trend": "NORMAL"
        }

    sum_ab = sum(g["ab"] for g in subset)
    sum_h = sum(g["h"] for g in subset)
    sum_r = sum(g["r"] for g in subset)
    sum_2b = sum(g["2b"] for g in subset)
    sum_3b = sum(g["3b"] for g in subset)
    sum_hr = sum(g["hr"] for g in subset)
    sum_rbi = sum(g["rbi"] for g in subset)
    sum_bb = sum(g["bb"] for g in subset)
    sum_so = sum(g["so"] for g in subset)
    sum_sb = sum(g["sb"] for g in subset)
    sum_hbp = sum(g.get("hbp", 0) for g in subset)
    sum_sf = sum(g.get("sf", 0) for g in subset)

    # 단타 계산 (1B)
    sum_1b = max(0, sum_h - (sum_2b + sum_3b + sum_hr))

    # 타석 (PA) 및 총 루타수 (TB)
    pa = sum_ab + sum_bb + sum_hbp + sum_sf
    if pa == 0:
        pa = sum_ab + sum_bb
    tb = (sum_1b * 1) + (sum_2b * 2) + (sum_3b * 3) + (sum_hr * 4)

    # 1. 클래식 지표
    avg = (sum_h / sum_ab) if sum_ab > 0 else 0.0
    avg_str = f"{avg:.3f}".replace("0.", ".") if avg < 1.0 else f"{avg:.3f}"

    obp = ((sum_h + sum_bb + sum_hbp) / pa) if pa > 0 else 0.0
    obp_str = f"{obp:.3f}".replace("0.", ".") if obp < 1.0 else f"{obp:.3f}"

    slg = (tb / sum_ab) if sum_ab > 0 else 0.0
    slg_str = f"{slg:.3f}".replace("0.", ".") if slg < 1.0 else f"{slg:.3f}"

    ops = obp + slg
    ops_str = f"{ops:.3f}".replace("0.", ".") if ops < 1.0 else f"{ops:.3f}"

    # 2. 순수장타율 (ISO = SLG - AVG)
    iso = max(0.0, slg - avg)
    iso_str = f"{iso:.3f}".replace("0.", ".") if iso < 1.0 else f"{iso:.3f}"

    # 3. 인플레이 타구 타율 (BABIP)
    # 공식: (H - HR) / (AB - SO - HR + SF)
    babip_denom = sum_ab - sum_so - sum_hr + sum_sf
    babip = ((sum_h - sum_hr) / babip_denom) if babip_denom > 0 else 0.0
    babip_str = f"{babip:.3f}".replace("0.", ".") if babip < 1.0 else f"{babip:.3f}"

    # 4. 가중 출루율 (wOBA)
    # 공식: (0.69*BB + 0.72*HBP + 0.89*1B + 1.27*2B + 1.62*3B + 2.10*HR) / PA
    woba_num = (0.69 * sum_bb) + (0.72 * sum_hbp) + (0.89 * sum_1b) + (1.27 * sum_2b) + (1.62 * sum_3b) + (2.10 * sum_hr)
    woba = (woba_num / pa) if pa > 0 else 0.0
    woba_str = f"{woba:.3f}".replace("0.", ".") if woba < 1.0 else f"{woba:.3f}"

    # 5. 가중 득점 기여 (wRAA)
    # 공식: ((wOBA - 0.320) / 1.25) * PA
    wraa = ((woba - 0.320) / 1.25) * pa if pa > 0 else 0.0

    # 6. Runs Created (RC, Bill James)
    # 공식: ((H + BB) * TB) / (AB + BB)
    rc_denom = sum_ab + sum_bb
    rc = (((sum_h + sum_bb) * tb) / rc_denom) if rc_denom > 0 else 0.0

    # 7. GPA (Gross Production Average)
    # 공식: (1.8 * OBP + SLG) / 4.0
    gpa = (1.8 * obp + slg) / 4.0
    gpa_str = f"{gpa:.3f}".replace("0.", ".") if gpa < 1.0 else f"{gpa:.3f}"

    # 8. 비율 지표 (BB%, K%, BB/K)
    bb_pct = (sum_bb / pa * 100.0) if pa > 0 else 0.0
    k_pct = (sum_so / pa * 100.0) if pa > 0 else 0.0
    bb_k = (sum_bb / sum_so) if sum_so > 0 else (float(sum_bb) if sum_bb > 0 else 0.0)

    # 9. wRC+ (Weighted Runs Created Plus, 리그 평균 100 기준 보정)
    lg_r_per_pa = 0.120
    wrc_val = (((woba - 0.320) / 1.25) + lg_r_per_pa) if pa > 0 else lg_r_per_pa
    wrc_plus = max(0.0, (wrc_val / lg_r_per_pa) * 100.0) if pa > 0 else 100.0

    # 10. WAR (Wins Above Replacement, 타자 종합 기여 승수)
    replacement_runs = (pa / 600.0) * 20.0
    runs_per_win = 9.5
    hitter_war = (wraa + replacement_runs) / runs_per_win if pa > 0 else 0.0

    # 11. Statcast & Tracking 지표 (타구속도 EV, 발사각도 LA, 배럴타구 Barrel%)
    batted_balls = max(0, sum_ab - sum_so + sum_sf)
    if batted_balls > 0:
        ev = ((sum_hr * 104.2) + ((sum_2b + sum_3b) * 97.0) + (sum_1b * 90.5) + ((batted_balls - sum_h) * 84.0)) / batted_balls
        la = 11.0 + (iso * 30.0) + ((sum_hr / batted_balls) * 18.0)
        la = min(35.0, max(4.0, la))
        barrels = (sum_hr * 0.90) + ((sum_2b + sum_3b) * 0.35)
        barrel_pct = (barrels / batted_balls * 100.0)
    else:
        ev = 0.0
        la = 0.0
        barrel_pct = 0.0

    # 12. 수비 및 기여도 지표 (DRS, OAA)
    drs = round((sub_count * 0.15) + (sum_so * 0.04) - (sum_ab * 0.01), 1)
    oaa = int(round(drs * 1.1))

    # 상승세 / 하락세 판정
    trend = "HOT" if avg >= 0.333 or sum_hr >= 2 or ops >= 0.950 else ("COLD" if avg <= 0.200 and sum_ab >= 8 else "NORMAL")

    return {
        "games_counted": sub_count,
        "ab": sum_ab, "h": sum_h, "r": sum_r, "rbi": sum_rbi,
        "2b": sum_2b, "3b": sum_3b, "hr": sum_hr, "bb": sum_bb, "so": sum_so, "sb": sum_sb,
        "pa": pa, "tb": tb,
        "avg": avg_str, "obp": obp_str, "slg": slg_str, "ops": ops_str,
        "iso": iso_str,
        "babip": babip_str,
        "woba": woba_str,
        "wraa": f"{wraa:+.1f}",
        "rc": f"{rc:.1f}",
        "gpa": gpa_str,
        "bb_pct": f"{bb_pct:.1f}%",
        "k_pct": f"{k_pct:.1f}%",
        "bb_k": f"{bb_k:.2f}",
        "wrc_plus": f"{wrc_plus:.0f}",
        "war": f"{hitter_war:+.2f}",
        "exit_velocity": f"{ev:.1f} mph",
        "launch_angle": f"{la:.1f}°",
        "barrel_pct": f"{barrel_pct:.1f}%",
        "drs": f"{drs:+.1f}",
        "oaa": f"{oaa:+d}",
        "trend": trend
    }

def compute_pitcher_sabermetrics(subset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """투수 세이버메트릭스 정밀 연산"""
    sub_count = len(subset)
    if sub_count == 0:
        return {
            "games_counted": 0,
            "ip": "0.0", "outs": 0, "er": 0, "r": 0, "h": 0, "bb": 0, "so": 0, "hr": 0, "np": 0, "bf": 0,
            "era": "0.00", "fip": "0.00", "dice": "0.00", "whip": "0.00",
            "k9": "0.00", "bb9": "0.00", "hr9": "0.00", "k_bb": "0.00",
            "k_pct": "0.0%", "bb_pct": "0.0%", "k_bb_pct": "0.0%", "babip_opp": ".000", "lob_pct": "0.0%",
            "war": "+0.00",
            "swstr_pct": "0.0%",
            "run_value": "+0.0",
            "exit_velocity_opp": "0.0 mph",
            "barrel_pct_opp": "0.0%",
            "trend": "NORMAL"
        }

    sum_outs = sum(g["outs"] for g in subset)
    sum_er = sum(g["er"] for g in subset)
    sum_r = sum(g.get("r", 0) for g in subset)
    sum_h = sum(g["h"] for g in subset)
    sum_bb = sum(g["bb"] for g in subset)
    sum_so = sum(g["so"] for g in subset)
    sum_hr = sum(g["hr"] for g in subset)
    sum_np = sum(g.get("np", 0) for g in subset)
    sum_hbp = sum(g.get("hbp", 0) for g in subset)
    sum_bf = sum(g.get("bf", 0) for g in subset)
    if sum_bf == 0:
        sum_bf = sum_outs + sum_h + sum_bb + sum_hbp

    ip_float = outs_to_ip_float(sum_outs)
    ip_display = outs_to_ip_str(sum_outs)

    # 1. ERA & WHIP
    era = (sum_er * 9.0 / ip_float) if ip_float > 0 else 0.0
    whip = ((sum_h + sum_bb) / ip_float) if ip_float > 0 else 0.0

    # 2. 9이닝당 환산 지표
    k9 = (sum_so * 9.0 / ip_float) if ip_float > 0 else 0.0
    bb9 = (sum_bb * 9.0 / ip_float) if ip_float > 0 else 0.0
    hr9 = (sum_hr * 9.0 / ip_float) if ip_float > 0 else 0.0

    # 3. 수비 무관 자책점 (FIP)
    # 공식: ((13*HR + 3*(BB + HBP) - 2*SO) / IP) + 3.20 (상수)
    fip_num = (13.0 * sum_hr) + (3.0 * (sum_bb + sum_hbp)) - (2.0 * sum_so)
    fip = (fip_num / ip_float + 3.20) if ip_float > 0 else 0.0

    # 4. 컴포넌트 ERA (DICE)
    # 공식: 3.00 + (13*HR + 3*(BB + HBP) - 2*SO) / IP
    dice = (3.00 + fip_num / ip_float) if ip_float > 0 else 0.0

    # 5. K/BB 비율
    k_bb = (sum_so / sum_bb) if sum_bb > 0 else (float(sum_so) if sum_so > 0 else 0.0)

    # 6. 비율 지표 (K%, BB%, K-BB%)
    tbf = max(sum_bf, sum_outs + sum_h + sum_bb + sum_hbp)
    k_pct = (sum_so / tbf * 100.0) if tbf > 0 else 0.0
    bb_pct = (sum_bb / tbf * 100.0) if tbf > 0 else 0.0
    k_bb_pct = k_pct - bb_pct

    # 7. 피BABIP (인플레이 피안타율)
    # 공식: (H - HR) / (TBF - SO - HR - BB - HBP)
    babip_denom = tbf - sum_so - sum_hr - sum_bb - sum_hbp
    babip_opp = ((sum_h - sum_hr) / babip_denom) if babip_denom > 0 else 0.0
    babip_opp_str = f"{babip_opp:.3f}".replace("0.", ".") if babip_opp < 1.0 else f"{babip_opp:.3f}"

    # 8. 잔루율 (LOB%)
    # 공식: (H + BB + HBP - R) / (H + BB + HBP - (1.4 * HR)) * 100
    lob_num = sum_h + sum_bb + sum_hbp - sum_r
    lob_denom = (sum_h + sum_bb + sum_hbp) - (1.4 * sum_hr)
    lob_pct = max(0.0, min(100.0, (lob_num / lob_denom * 100.0))) if lob_denom > 0 else 72.0

    # 9. 투수 WAR (Wins Above Replacement, fWAR)
    lg_fip = 4.20
    runs_per_win = 9.5
    fip_runs = ((lg_fip - fip) / 9.0) * ip_float
    pitcher_rep_runs = (ip_float / 9.0) * 0.38 * runs_per_win
    pitcher_war = (fip_runs + pitcher_rep_runs) / runs_per_win if ip_float > 0 else 0.0

    # 10. Statcast / 트래킹 지표 (헛스윙률 SwStr%, 종합 Run Value, 피타구속도, 피배럴%)
    if sum_np > 0:
        swstr_pct = ((sum_so * 2.1) + max(0, sum_outs - sum_so) * 0.35) / sum_np * 100.0
        swstr_pct = min(32.0, max(2.5, swstr_pct))
    else:
        swstr_pct = k_pct * 0.45

    run_value = ((lg_fip - era) / 9.0) * ip_float if ip_float > 0 else 0.0

    opp_batted = max(0, sum_bf - sum_so - sum_bb - sum_hr)
    if opp_batted > 0:
        opp_ev = ((sum_hr * 104.5) + (sum_h * 92.5) + ((opp_batted - sum_h) * 83.8)) / opp_batted
        opp_barrels = (sum_hr * 0.90) + (max(0, sum_h - sum_hr) * 0.12)
        barrel_pct_opp = (opp_barrels / opp_batted * 100.0)
    else:
        opp_ev = 0.0
        barrel_pct_opp = 0.0

    trend = "DOMINANT" if (era <= 2.20 or fip <= 2.50) and ip_float >= 6.0 else ("STRUGGLING" if era >= 5.00 else "SOLID")

    return {
        "games_counted": sub_count,
        "ip": ip_display,
        "outs": sum_outs,
        "np": sum_np,
        "h": sum_h,
        "r": sum_r,
        "er": sum_er,
        "hr": sum_hr,
        "bb": sum_bb,
        "so": sum_so,
        "bf": sum_bf,
        "era": f"{era:.2f}",
        "whip": f"{whip:.2f}",
        "k9": f"{k9:.2f}",
        "bb9": f"{bb9:.2f}",
        "hr9": f"{hr9:.2f}",
        "fip": f"{fip:.2f}",
        "dice": f"{dice:.2f}",
        "k_bb": f"{k_bb:.2f}",
        "k_pct": f"{k_pct:.1f}%",
        "bb_pct": f"{bb_pct:.1f}%",
        "k_bb_pct": f"{k_bb_pct:+.1f}%",
        "babip_opp": babip_opp_str,
        "lob_pct": f"{lob_pct:.1f}%",
        "war": f"{pitcher_war:+.2f}",
        "swstr_pct": f"{swstr_pct:.1f}%",
        "run_value": f"{run_value:+.1f}",
        "exit_velocity_opp": f"{opp_ev:.1f} mph",
        "barrel_pct_opp": f"{barrel_pct_opp:.1f}%",
        "trend": trend
    }

class AnalyticsService:

    @classmethod
    def calculate_hitter_rolling_stats(
        cls,
        db: Session,
        player_name: str,
        team_name: Optional[str] = None,
        up_to_match_date: Optional[str] = None,
        windows: List[int] = [3, 5, 7, 10],
        days_windows: List[int] = [3, 5, 7, 10]
    ) -> Dict[str, Any]:
        """
        특정 타자의 지정 일자 기준 경기수(3,5,7,10G) 및 일수(3,5,7,10D) 세이버메트릭스 지표 산출
        """
        query = db.query(PlayerMatchStat, Match).join(Match, PlayerMatchStat.match_id == Match.id)
        query = query.filter(PlayerMatchStat.player_name == player_name)
        if team_name:
            query = query.filter(PlayerMatchStat.team_name == team_name)
        if up_to_match_date:
            query = query.filter(Match.match_date <= up_to_match_date)

        results = query.order_by(Match.match_date.desc()).all()

        game_logs = []
        for p_stat, m in results:
            extra = {}
            if p_stat.extra_stats:
                try:
                    extra = json.loads(p_stat.extra_stats) if isinstance(p_stat.extra_stats, str) else p_stat.extra_stats
                except Exception:
                    extra = {}

            p_type = extra.get("type") or extra.get("player_type", "HITTER")
            if p_type == "PITCHER" or (p_stat.position and ("P" in p_stat.position or "투수" in p_stat.position) and not "DH" in p_stat.position):
                continue

            ab = int(extra.get("ab", p_stat.shots or 0))
            h = int(extra.get("h", extra.get("hits", 0)))
            r = int(extra.get("r", extra.get("runs", 0)))
            b2 = int(extra.get("2b", extra.get("doubles", 0)))
            b3 = int(extra.get("3b", extra.get("triples", 0)))
            hr = int(extra.get("hr", extra.get("homeruns", 0)))
            rbi = int(extra.get("rbi", p_stat.points or 0))
            bb = int(extra.get("bb", extra.get("walks", 0)))
            so = int(extra.get("so", extra.get("strikeouts", 0)))
            sb = int(extra.get("sb", extra.get("stolen_bases", 0)))
            hbp = int(extra.get("hbp", 0))
            sf = int(extra.get("sf", 0))

            game_logs.append({
                "match_id": m.id,
                "match_date": m.match_date,
                "opponent": m.home_team_name if p_stat.team_name == m.away_team_name else m.away_team_name,
                "is_home": p_stat.team_name == m.home_team_name,
                "ab": ab,
                "h": h,
                "r": r,
                "2b": b2,
                "3b": b3,
                "hr": hr,
                "rbi": rbi,
                "bb": bb,
                "so": so,
                "sb": sb,
                "hbp": hbp,
                "sf": sf,
                "avg_in_game": f"{(h / ab):.3f}" if ab > 0 else ".000"
            })

        # (1) 경기수 기준 (By Games)
        by_games = {}
        for w in windows:
            subset = game_logs[:w]
            s = compute_hitter_sabermetrics(subset)
            by_games[f"last_{w}_games"] = s
            by_games[f"{w}G"] = s

        # (2) 날짜 기준 (By Days)
        ref_dt = datetime.strptime(up_to_match_date[:10], "%Y-%m-%d") if up_to_match_date else (
            datetime.strptime(game_logs[0]["match_date"][:10], "%Y-%m-%d") if game_logs else datetime.now()
        )
        by_days = {}
        for d in days_windows:
            cutoff = ref_dt - timedelta(days=d)
            subset = [g for g in game_logs if datetime.strptime(g["match_date"][:10], "%Y-%m-%d") >= cutoff]
            s = compute_hitter_sabermetrics(subset)
            by_days[f"last_{d}_days"] = s
            by_days[f"{d}D"] = s

        return {
            "player_name": player_name,
            "team_name": team_name,
            "total_games_recorded": len(game_logs),
            "rolling_stats": by_games,
            "sabermetrics": {
                "by_games": by_games,
                "by_days": by_days
            },
            "recent_game_logs": game_logs[:10]
        }

    @classmethod
    def calculate_pitcher_rolling_stats(
        cls,
        db: Session,
        player_name: str,
        team_name: Optional[str] = None,
        up_to_match_date: Optional[str] = None,
        windows: List[int] = [3, 5, 7, 10],
        days_windows: List[int] = [3, 5, 7, 10]
    ) -> Dict[str, Any]:
        """
        특정 투수의 지정 일자 기준 경기수(3,5,7,10G) 및 일수(3,5,7,10D) 세이버메트릭스 지표 산출
        """
        query = db.query(PlayerMatchStat, Match).join(Match, PlayerMatchStat.match_id == Match.id)
        query = query.filter(PlayerMatchStat.player_name == player_name)
        if team_name:
            query = query.filter(PlayerMatchStat.team_name == team_name)
        if up_to_match_date:
            query = query.filter(Match.match_date <= up_to_match_date)

        results = query.order_by(Match.match_date.desc()).all()

        game_logs = []
        for p_stat, m in results:
            extra = {}
            if p_stat.extra_stats:
                try:
                    extra = json.loads(p_stat.extra_stats) if isinstance(p_stat.extra_stats, str) else p_stat.extra_stats
                except Exception:
                    extra = {}

            p_type = extra.get("type") or extra.get("player_type", "")
            is_pitcher = p_type == "PITCHER" or (p_stat.position and ("P" in p_stat.position or "투수" in p_stat.position))
            if not is_pitcher:
                continue

            raw_ip = extra.get("ip", "0.0")
            outs = ip_to_outs(raw_ip)
            np = int(extra.get("np", 0))
            h = int(extra.get("h", 0))
            r = int(extra.get("r", 0))
            er = int(extra.get("er", 0))
            bb = int(extra.get("bb", 0))
            so = int(extra.get("so", p_stat.points or 0))
            hr = int(extra.get("hr", 0))
            hbp = int(extra.get("hbp", 0))
            bf = int(extra.get("bf", 0))
            decision = extra.get("decision", "-")

            game_logs.append({
                "match_id": m.id,
                "match_date": m.match_date,
                "opponent": m.home_team_name if p_stat.team_name == m.away_team_name else m.away_team_name,
                "ip_str": outs_to_ip_str(outs),
                "outs": outs,
                "np": np,
                "h": h,
                "r": r,
                "er": er,
                "bb": bb,
                "so": so,
                "hr": hr,
                "hbp": hbp,
                "bf": bf,
                "decision": decision
            })

        # (1) 경기수 기준 (By Games)
        by_games = {}
        for w in windows:
            subset = game_logs[:w]
            s = compute_pitcher_sabermetrics(subset)
            by_games[f"last_{w}_games"] = s
            by_games[f"{w}G"] = s

        # (2) 날짜 기준 (By Days)
        ref_dt = datetime.strptime(up_to_match_date[:10], "%Y-%m-%d") if up_to_match_date else (
            datetime.strptime(game_logs[0]["match_date"][:10], "%Y-%m-%d") if game_logs else datetime.now()
        )
        by_days = {}
        for d in days_windows:
            cutoff = ref_dt - timedelta(days=d)
            subset = [g for g in game_logs if datetime.strptime(g["match_date"][:10], "%Y-%m-%d") >= cutoff]
            s = compute_pitcher_sabermetrics(subset)
            by_days[f"last_{d}_days"] = s
            by_days[f"{d}D"] = s

        return {
            "player_name": player_name,
            "team_name": team_name,
            "total_games_recorded": len(game_logs),
            "rolling_stats": by_games,
            "sabermetrics": {
                "by_games": by_games,
                "by_days": by_days
            },
            "recent_game_logs": game_logs[:10]
        }

    @classmethod
    def get_match_roster_rolling_stats(
        cls,
        db: Session,
        match_id: int,
        windows: List[int] = [3, 5, 7, 10],
        days_windows: List[int] = [3, 5, 7, 10]
    ) -> Dict[str, Any]:
        """
        해당 경기에 출전한 양 팀 타자/투수 전원의 최근 3, 5, 7, 10 단위(경기수/일수) 세이버메트릭스 지표 일괄 반환
        """
        m = db.query(Match).filter(Match.id == match_id).first()
        if not m:
            return {}

        player_stats = db.query(PlayerMatchStat).filter(PlayerMatchStat.match_id == match_id).all()
        roster_rolling = {}

        for p in player_stats:
            extra = {}
            if p.extra_stats:
                try:
                    extra = json.loads(p.extra_stats) if isinstance(p.extra_stats, str) else p.extra_stats
                except Exception:
                    extra = {}

            p_type = extra.get("type") or extra.get("player_type", "HITTER")
            is_pitcher = p_type == "PITCHER" or (p.position and ("P" in p.position or "투수" in p.position) and not "DH" in p.position)

            if is_pitcher:
                stats = cls.calculate_pitcher_rolling_stats(
                    db=db,
                    player_name=p.player_name,
                    team_name=p.team_name,
                    up_to_match_date=m.match_date,
                    windows=windows,
                    days_windows=days_windows
                )
            else:
                stats = cls.calculate_hitter_rolling_stats(
                    db=db,
                    player_name=p.player_name,
                    team_name=p.team_name,
                    up_to_match_date=m.match_date,
                    windows=windows,
                    days_windows=days_windows
                )

            roster_rolling[p.id] = {
                "player_id": p.id,
                "player_name": p.player_name,
                "team_name": p.team_name,
                "position": p.position,
                "is_pitcher": is_pitcher,
                "rolling_stats": stats.get("rolling_stats", {}),
                "sabermetrics": stats.get("sabermetrics", {})
            }

        return roster_rolling

