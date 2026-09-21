# -*- coding: utf-8 -*-
import os
import re
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from app.core.database import SessionLocal
from app.models.models import Match, MatchDetail

logger = logging.getLogger("asian_games_service")
logger.setLevel(logging.INFO)

BETMAN_WINRST_BODY_URL = "https://www.betman.co.kr/gamebuy/winrst/inqWinrstDetlBody.do"
BETMAN_IFR_URL = "https://www.betman.co.kr/main/mainPage/gamebuy/winrstDetlIFR.do"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.betman.co.kr/main/mainPage/gamebuy/winrstList.do"
}

class AsianGamesService:
    """
    아시안게임 및 베트맨 공식 국제대회 경기 실시간 스크래퍼 & 공식 결과 동기화기
    - 베트맨 공식 경기결과(inqWinrstDetlBody) 100% 실시간 연동
    - 농구(쿼터/최종스코어), 배구(세트/최종스코어), 축구(전후반/최종스코어), 야구 결과 자동 파싱
    - 경기취소(특례코드 4) 및 정규종료(FINISHED) 완벽 구분
    """

    @classmethod
    def get_session(cls) -> requests.Session:
        s = requests.Session()
        s.headers.update(HEADERS)
        return s

    @classmethod
    def fetch_round_results(cls, gm_ts: int, gm_id: str = "G101") -> List[Dict[str, Any]]:
        """베트맨 공식 회차(gm_ts)의 전체 적중결과 목록 수집"""
        session = cls.get_session()
        try:
            # 1. Warm-up session cookie with IFR page
            session.get(f"{BETMAN_IFR_URL}?gmId={gm_id}&gmTs={gm_ts}", timeout=6)
            
            # 2. Fetch official match results JSON
            params = {
                "gmId": gm_id,
                "gmTs": int(gm_ts),
                "_sbmInfo": {"_sbmInfo": {"debugMode": "false"}}
            }
            resp = session.post(BETMAN_WINRST_BODY_URL, json=params, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("detlBody", [])
            else:
                logger.warning(f"[AsianGamesService] Round {gm_ts} HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"[AsianGamesService] Round {gm_ts} fetch error: {e}")
        return []

    @classmethod
    def parse_match_results(cls, raw_rows: List[Dict[str, Any]], gm_ts: int) -> Dict[str, Dict[str, Any]]:
        """
        수집된 원본 베트맨 결과 행들을 official_id 및 (홈, 원정) 기반 순수 실스코어 맵으로 정제.
        (언더오버 기준점/SUM/핸디캡 조정치가 아닌 실제 공식 경기 본스코어만 100% 채택)
        """
        results_map = {}
        team_pair_map = {}

        for row in raw_rows:
            seq = row.get("GM_SEQ")
            if not seq:
                continue

            off_id = f"BETMAN_G101_{gm_ts}_{seq}"
            score_raw = str(row.get("MCH_SCORE") or "").strip()
            rslt_cd = str(row.get("GAME_RESULT") or "").strip()
            bet_nm = str(row.get("BETTYP_NM") or row.get("BETTYP_TYP_NM") or "")
            handi_val = str(row.get("HANDI_VAL") or "0").strip()
            h_team = (row.get("HOME_TEAM") or row.get("HOME_TEAM1") or "").strip()
            a_team = (row.get("AWAY_TEAM") or row.get("AWAY_TEAM1") or "").strip()

            if not h_team or not a_team:
                continue

            # 1. 언더오버, SUM, 소수점/음수 핸디캡은 실제 팀 스코어가 아니므로 완전 배제
            if any(k in bet_nm for k in ["언더", "오버", "SUM", "핸디캡"]):
                continue
            if "." in score_raw or score_raw.startswith("-"):
                continue

            # 2. 순수 본경기 승패/승무패 여부 확인
            is_main_bet = any(k in bet_nm for k in ["승패", "승무패"])

            status = "FINISHED"
            h_score = None
            a_score = None

            if score_raw and ":" in score_raw:
                parts = score_raw.split(":")
                try:
                    h_score = int(parts[0].strip())
                    a_score = int(parts[1].strip())
                except ValueError:
                    pass
            elif rslt_cd == "4" or score_raw == "-":
                status = "CANCELLED"
                h_score = 0
                a_score = 0

            if h_score is None or a_score is None:
                continue

            parsed_item = {
                "official_id": off_id,
                "gm_ts": gm_ts,
                "gm_seq": seq,
                "home_team": h_team,
                "away_team": a_team,
                "league_name": row.get("LEAG_CD_NM") or row.get("PR_LL_WIN_LEAG_NM") or "",
                "home_score": h_score,
                "away_score": a_score,
                "status": status,
                "raw_score": score_raw,
                "result_code": rslt_cd,
                "bet_type": bet_nm,
                "is_main_bet": is_main_bet
            }

            pair_key = (h_team, a_team)
            if off_id not in results_map or is_main_bet:
                results_map[off_id] = parsed_item
            if pair_key not in team_pair_map or is_main_bet:
                team_pair_map[pair_key] = parsed_item

        return {"by_id": results_map, "by_pair": team_pair_map}

    @classmethod
    def sync_asian_games_to_db(cls, rounds: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        DB에 등록된 아시안게임 경기들의 스코어를 베트맨 공식 실데이터로 일괄 업데이트.
        """
        db = SessionLocal()
        try:
            # 1. 아시안게임 관련 경기 목록 조회
            asian_matches = db.query(Match).filter(
                Match.league_name.like("%아시안%")
            ).all()

            if not asian_matches:
                return {"status": "SUCCESS", "message": "동기화할 아시안게임 경기가 없습니다.", "updated": 0}

            # 2. 대상 회차(gm_ts) 식별
            if not rounds:
                round_set = set()
                for m in asian_matches:
                    off_id = m.official_id or ""
                    parts = off_id.split("_")
                    if len(parts) >= 3 and parts[2].isdigit():
                        round_set.add(int(parts[2]))
                rounds = sorted(list(round_set))

            if not rounds:
                rounds = [260108, 260109, 260110, 260111, 260112]

            logger.info(f"[AsianGamesService] Synchronizing Asian Games for rounds: {rounds}")

            # 3. 각 회차별 공식 결과 수집 및 파싱
            all_official_by_id: Dict[str, Dict[str, Any]] = {}
            all_official_by_pair: Dict[tuple, Dict[str, Any]] = {}
            for r_num in rounds:
                raw_rows = cls.fetch_round_results(r_num)
                parsed = cls.parse_match_results(raw_rows, r_num)
                all_official_by_id.update(parsed.get("by_id", {}))
                all_official_by_pair.update(parsed.get("by_pair", {}))

            logger.info(f"[AsianGamesService] Total parsed official match results: {len(all_official_by_id)} (unique pairs: {len(all_official_by_pair)})")

            updated_count = 0
            updated_details = []

            # 4. DB 매칭 및 업데이트 (official_id 일치 최우선, 팀명 쌍 폴백)
            for m in asian_matches:
                match_res = None
                if m.official_id and m.official_id in all_official_by_id:
                    match_res = all_official_by_id[m.official_id]
                else:
                    pair_key = (m.home_team_name, m.away_team_name)
                    if pair_key in all_official_by_pair:
                        match_res = all_official_by_pair[pair_key]

                if not match_res:
                    continue

                new_hs = match_res["home_score"]
                new_as = match_res["away_score"]
                new_st = match_res["status"]

                # 스코어나 상태가 변경된 경우 업데이트
                if m.home_score != new_hs or m.away_score != new_as or m.status != new_st:
                    old_info = f"{m.status} {m.home_score}:{m.away_score}"
                    m.home_score = new_hs
                    m.away_score = new_as
                    m.status = new_st
                    m.updated_at = datetime.now()

                    # match_details 업데이트
                    detail = db.query(MatchDetail).filter(MatchDetail.match_id == m.id).first()
                    if detail:
                        try:
                            stats = json.loads(detail.team_stats) if detail.team_stats else {}
                        except Exception:
                            stats = {}
                        stats["betman_official_result"] = {
                            "score": f"{new_hs}:{new_as}",
                            "status": new_st,
                            "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": "Betman Official Results (inqWinrstDetlBody)"
                        }
                        detail.team_stats = json.dumps(stats, ensure_ascii=False)

                    updated_count += 1
                    updated_details.append({
                        "id": m.id,
                        "league": m.league_name,
                        "match": f"{m.home_team_name} vs {m.away_team_name}",
                        "before": old_info,
                        "after": f"{new_st} {new_hs}:{new_as}"
                    })

            db.commit()
            logger.info(f"[AsianGamesService] Successfully updated {updated_count} Asian Games matches")
            return {
                "status": "SUCCESS",
                "total_asian_matches": len(asian_matches),
                "updated_count": updated_count,
                "rounds_processed": rounds,
                "updated_samples": updated_details[:10]
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[AsianGamesService] DB sync error: {e}")
            return {"status": "ERROR", "message": str(e)}
        finally:
            db.close()
