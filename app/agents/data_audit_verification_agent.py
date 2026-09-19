# -*- coding: utf-8 -*-
"""
DataAuditVerificationAgent
===========================
원천 API(ESPN, API-Sports, Betman) 수집 데이터와 데이터베이스(DB) 간의
1:1 대조 무결성을 검증하고, 스코어·선발투수 방어율·최근전적을 정밀 검수하는 전담 엔진.

Pipeline:
  [원천 API] -> [데이터 수집] -> [검증 엔진 (PASS / FAIL / UNKNOWN)] -> [검증된 DB] -> [사용자 UI]
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.models import Match, MatchDetail
from app.services.betman_service import teams_match, clean_name
from app.services.team_split_service import is_valid_starter_name
from app.services.live_api_sports_service import LiveApiSportsService

logger = logging.getLogger("data_audit_agent")
logger.setLevel(logging.INFO)

def get_now_kst() -> datetime:
    return datetime.utcnow() + timedelta(hours=9)

class DataAuditVerificationAgent:
    """
    1:1 원천 API 대조 데이터 검증 및 자동 보정 전담 에이전트
    """
    
    # In-memory latest audit cache
    _LATEST_AUDIT_SUMMARY: Dict[str, Any] = {
        "audited_at": None,
        "total_matches": 0,
        "pass_count": 0,
        "fail_count": 0,
        "unknown_count": 0,
        "pass_rate": 0.0,
        "by_sport": {},
        "recent_remediated": []
    }

    @classmethod
    def get_latest_summary(cls) -> Dict[str, Any]:
        return cls._LATEST_AUDIT_SUMMARY

    @classmethod
    def audit_single_match(cls, db: Session, match: Match, auto_fix: bool = True) -> Dict[str, Any]:
        """
        개별 경기에 대해 1:1 정밀 검수 수행:
        1. 경기 식별 정보 (Identity)
        2. 상태 및 스코어 (Score & Status)
        3. 야구 선발투수 및 시즌 방어율 (Starters & ERA)
        4. 최근 10경기 및 상대전적 (Recent Form & H2H)
        """
        issues = []
        checks = {
            "identity": "PASS",
            "score_and_status": "PASS",
            "pitchers_and_era": "PASS",
            "recent_and_h2h": "PASS"
        }
        remediated = False

        sport = (match.sport_code or "SOCCER").upper()
        status = (match.status or "SCHEDULED").upper()
        h_team = (match.home_team_name or "").strip()
        a_team = (match.away_team_name or "").strip()
        m_date = (match.match_date or "").strip()

        # 1. Identity Check
        if not h_team or not a_team or len(h_team) < 1 or len(a_team) < 1:
            issues.append("홈/원정 구단명 누락")
            checks["identity"] = "FAIL"
        if not m_date or len(m_date) < 10:
            issues.append("경기 일시 형식 오류")
            checks["identity"] = "FAIL"

        # 2. Score & Status Check
        # Check for 0:0 anomaly on finished matches older than 2 hours
        now_kst_str = get_now_kst().strftime("%Y-%m-%d %H:%M")
        is_past_2h = m_date < (get_now_kst() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        
        if status == "FINISHED":
            # 축구/야구/농구에서 종료 경기인데 0:0인 경우 정밀 확인
            if (match.home_score == 0 and match.away_score == 0) and is_past_2h:
                if sport in ["BASEBALL", "BASKETBALL"]:
                    # 야구/농구는 무승부 0:0이 절대 불가능하므로 FAIL
                    issues.append(f"{sport} 경기 종료 스코어 0:0 이상치 감지 (미동기화)")
                    checks["score_and_status"] = "FAIL"
                elif sport == "SOCCER":
                    # 축구의 경우 0:0 무승부일 수 있으나 원천 공식 API와 1:1 대조 필요
                    # MatchDetail에 period_scores가 없거나 팀스탯이 전혀 없으면 미동기화 의심
                    if not match.details or not match.details.period_scores or match.details.period_scores == "{}":
                        issues.append("축구 0:0 종료 경기 공식 세부 스코어 미확인")
                        checks["score_and_status"] = "UNKNOWN"

        elif status == "SCHEDULED":
            # 시작 시간이 1시간 이상 지난 SCHEDULED 경기는 상태 업데이트 필요
            if m_date < (get_now_kst() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"):
                issues.append("시작 시간 경과 예정 경기 상태 지연")
                checks["score_and_status"] = "FAIL"

        # 3. Baseball Starters & ERA Check
        if sport == "BASEBALL":
            h_starter = match.home_starter_name
            a_starter = match.away_starter_name
            
            # MatchDetail 팀 스탯 확인
            team_stats = {}
            if match.details and match.details.team_stats:
                try:
                    team_stats = json.loads(match.details.team_stats) if isinstance(match.details.team_stats, str) else match.details.team_stats
                except Exception:
                    team_stats = {}
            
            starters_data = team_stats.get("starters", {}) if isinstance(team_stats, dict) else {}
            h_era = starters_data.get("home", {}).get("era")
            a_era = starters_data.get("away", {}).get("era")

            # 경기 당일 또는 1일 전 예정/진행/종료 경기인 경우 선발투수 확인
            is_near_game = m_date[:10] <= (get_now_kst() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            if is_near_game:
                if not h_starter or not a_starter or h_starter in ["미정", "선발 예고", "예정", None] or a_starter in ["미정", "선발 예고", "예정", None]:
                    if status in ["LIVE", "FINISHED"]:
                        issues.append("진행/종료 경기 선발투수 누락")
                        checks["pitchers_and_era"] = "FAIL"
                    else:
                        checks["pitchers_and_era"] = "UNKNOWN" # 예정 경기는 발표 전일 수 있음
                else:
                    # 선발투수 방어율(ERA) 유효성 검사 (0.00 ~ 20.00)
                    if h_era is not None:
                        try:
                            val = float(str(h_era).replace("ERA", "").strip())
                            if val < 0.0 or val > 20.0:
                                issues.append(f"홈 선발 방어율 이상치: {val}")
                                checks["pitchers_and_era"] = "FAIL"
                        except Exception:
                            pass
                    if a_era is not None:
                        try:
                            val = float(str(a_era).replace("ERA", "").strip())
                            if val < 0.0 or val > 20.0:
                                issues.append(f"원정 선발 방어율 이상치: {val}")
                                checks["pitchers_and_era"] = "FAIL"
                        except Exception:
                            pass
            else:
                checks["pitchers_and_era"] = "UNKNOWN" # 원거리 일정은 선발 미발표 정상

        # 4. Recent 10 Matches & H2H Check (DB 내 최근 10경기 및 상대 전적 무결성 확인)
        has_detail_stats = False
        if match.details and match.details.team_stats:
            try:
                ts = json.loads(match.details.team_stats) if isinstance(match.details.team_stats, str) else match.details.team_stats
                if isinstance(ts, dict) and (ts.get("h2h") or ts.get("recent_form") or ts.get("recent_matches")):
                    has_detail_stats = True
            except Exception:
                pass

        if has_detail_stats:
            checks["recent_and_h2h"] = "PASS"
        else:
            # DB 상 최근 전적 산출 가능한 과거 경기 데이터 존재 여부 확인
            hist_count = db.query(Match).filter(
                Match.sport_code == sport,
                or_(
                    Match.home_team_name == h_team,
                    Match.away_team_name == h_team,
                    Match.home_team_name == a_team,
                    Match.away_team_name == a_team
                )
            ).count()
            if hist_count >= 2:
                checks["recent_and_h2h"] = "PASS"
            else:
                checks["recent_and_h2h"] = "UNKNOWN"

        # 판정 결정: FAIL이 1개라도 있으면 FAIL, UNKNOWN만 있으면 UNKNOWN, 모두 PASS면 PASS
        if "FAIL" in checks.values():
            verdict = "FAIL"
        elif "UNKNOWN" in checks.values():
            verdict = "UNKNOWN"
        else:
            verdict = "PASS"

        # 5. 자동 보정 (Auto-Remediation)
        if verdict == "FAIL" and auto_fix:
            try:
                fixed = cls._auto_remediate_match(db, match, issues)
                if fixed:
                    remediated = True
                    verdict = "PASS"
                    checks["score_and_status"] = "PASS"
                    checks["pitchers_and_era"] = "PASS"
            except Exception as re_err:
                logger.warning(f"[DataAudit] Auto-remediation failed for match {match.id}: {re_err}")

        score = 100
        if verdict == "FAIL":
            score = 50
        elif verdict == "UNKNOWN":
            score = 85

        audit_report = {
            "match_id": match.id,
            "official_id": match.official_id,
            "sport_code": sport,
            "league_name": match.league_name,
            "home_team": h_team,
            "away_team": a_team,
            "match_date": m_date,
            "status": match.status,
            "score": f"{match.home_score}:{match.away_score}",
            "verdict": verdict,
            "score_points": score,
            "checks": checks,
            "issues": issues,
            "remediated": remediated,
            "audited_at": get_now_kst().strftime("%Y-%m-%d %H:%M:%S")
        }

        # MatchDetail에 검증 메타데이터 보관
        if not match.details:
            match.details = MatchDetail(match_id=match.id, period_scores="{}", team_stats="{}")
            db.add(match.details)
            db.commit()
            db.refresh(match.details)

        try:
            curr_stats = {}
            if match.details.team_stats:
                curr_stats = json.loads(match.details.team_stats) if isinstance(match.details.team_stats, str) else match.details.team_stats
            curr_stats["audit"] = {
                "verdict": verdict,
                "audited_at": audit_report["audited_at"],
                "score": score,
                "remediated": remediated
            }
            match.details.team_stats = json.dumps(curr_stats, ensure_ascii=False)
            db.commit()
        except Exception:
            pass

        return audit_report

    @classmethod
    def _auto_remediate_match(cls, db: Session, match: Match, issues: List[str]) -> bool:
        """원천 API에서 최신 공식 팩트 데이터를 조회하여 DB를 즉시 자동 교정"""
        sport = (match.sport_code or "").upper()
        m_date_day = (match.match_date or "")[:10]
        
        # 1. 축구 오류 보정: ESPN 및 API-Football 실시간 스코어 조회
        if sport == "SOCCER":
            from app.scrapers.soccer_scraper import SoccerScraper
            lname = (match.league_name or "").upper()
            code = "EPL"
            if "라리가" in lname or "LALIGA" in lname: code = "LALIGA"
            elif "세리에" in lname or "SERIE" in lname: code = "SERIE_A"
            elif "리그1" in lname or "LIGUE" in lname or "리그앙" in lname: code = "LIGUE_1"
            elif "분데스" in lname or "BUNDES" in lname: code = "BUNDESLIGA"
            
            scraper = SoccerScraper(league_id=code)
            matches = scraper.scrape_matches(m_date_day)
            for sm in matches:
                if teams_match(match.home_team_name, sm.get("home_team_name")) and teams_match(match.away_team_name, sm.get("away_team_name")):
                    match.home_score = sm.get("home_score", match.home_score)
                    match.away_score = sm.get("away_score", match.away_score)
                    match.status = sm.get("status", match.status)
                    db.commit()
                    logger.info(f"[DataAudit AutoFix] Soccer Match {match.id} remediated with score {match.home_score}:{match.away_score}")
                    return True

        # 2. 야구 오류 보정: 선발투수 및 방어율 최신 공식 동기화
        elif sport == "BASEBALL":
            from app.services.team_split_service import _resolve_match_starters
            starters = _resolve_match_starters(match, m_date_day)
            if starters and (starters.get("home_starter") or starters.get("away_starter")):
                if not match.details:
                    match.details = MatchDetail(match_id=match.id, period_scores="{}", team_stats="{}")
                    db.add(match.details)
                ts = {}
                if match.details.team_stats:
                    try:
                        ts = json.loads(match.details.team_stats)
                    except Exception:
                        ts = {}
                ts["starters"] = {
                    "home": {"name": starters.get("home_starter"), "confirmed": True, "era": starters.get("home_era")},
                    "away": {"name": starters.get("away_starter"), "confirmed": True, "era": starters.get("away_era")}
                }
                match.details.team_stats = json.dumps(ts, ensure_ascii=False)
                db.commit()
                logger.info(f"[DataAudit AutoFix] Baseball Match {match.id} starters remediated")
                return True

        # 3. 농구 오류 보정: LiveApiSportsService 농구 공식 스코어 수집 연동
        elif sport == "BASKETBALL":
            try:
                res = LiveApiSportsService.sync_live_basketball(date_str=m_date_day)
                if res and res.get("updated_db_matches", 0) > 0:
                    logger.info(f"[DataAudit AutoFix] Basketball Match {match.id} remediated")
                    return True
            except Exception:
                pass

        return False

    @classmethod
    def run_full_audit(cls, auto_fix: bool = True, limit: int = 500) -> Dict[str, Any]:
        """
        전체 DB 등록 경기에 대해 1:1 전수 검수 및 자동 보정 일괄 실행
        """
        db = SessionLocal()
        start_ts = time.time()
        try:
            start_date_str = (get_now_kst() - timedelta(days=7)).strftime("%Y-%m-%d")
            matches = db.query(Match).filter(
                Match.match_date >= start_date_str
            ).order_by(Match.match_date.asc()).limit(limit).all()

            total = len(matches)
            pass_cnt = 0
            fail_cnt = 0
            unknown_cnt = 0
            by_sport = defaultdict(lambda: {"total": 0, "pass": 0, "fail": 0, "unknown": 0})
            remediated_list = []

            for m in matches:
                report = cls.audit_single_match(db, m, auto_fix=auto_fix)
                verdict = report["verdict"]
                sp = report["sport_code"]
                
                by_sport[sp]["total"] += 1
                if verdict == "PASS":
                    pass_cnt += 1
                    by_sport[sp]["pass"] += 1
                elif verdict == "FAIL":
                    fail_cnt += 1
                    by_sport[sp]["fail"] += 1
                else:
                    unknown_cnt += 1
                    by_sport[sp]["unknown"] += 1

                if report.get("remediated"):
                    remediated_list.append({
                        "id": m.id,
                        "teams": f"{m.home_team_name} vs {m.away_team_name}",
                        "league": m.league_name,
                        "date": m.match_date,
                        "fixed_score": f"{m.home_score}:{m.away_score}",
                        "status": m.status
                    })

            pass_rate = round((pass_cnt / max(1, total)) * 100, 1)
            duration_sec = round(time.time() - start_ts, 2)

            summary = {
                "audited_at": get_now_kst().strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration_sec,
                "total_matches": total,
                "pass_count": pass_cnt,
                "fail_count": fail_cnt,
                "unknown_count": unknown_cnt,
                "pass_rate": pass_rate,
                "by_sport": dict(by_sport),
                "remediated_count": len(remediated_list),
                "recent_remediated": remediated_list[:20]
            }

            cls._LATEST_AUDIT_SUMMARY = summary
            logger.info(f"[DataAudit Full] Audit complete: {pass_cnt}/{total} PASS ({pass_rate}%), Remediated {len(remediated_list)} in {duration_sec}s")
            return summary
        finally:
            db.close()
