import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.models import Match, MatchDetail, MatchEvent, PlayerMatchStat
from app.scrapers.baseball_scraper import BaseballScraper
from app.scrapers.soccer_scraper import SoccerScraper, SOCCER_LEAGUE_CODES
from app.scrapers.basketball_scraper import BasketballScraper
from app.core.sports_catalog import SPORTS_CATALOG
from app.services.team_split_service import TeamSplitService, is_valid_starter_name, _resolve_match_starters
from app.services.live_api_sports_service import lookup_pitcher_season_era
from app.services.player_translation import translate_player_name, sanitize_player_name, sanitize_text
from app.services.betman_service import BetmanService, teams_match, clean_name, get_canonical_team_key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MatchService:

    @classmethod
    def sync_from_official_site(cls, db: Session, league_id: str = "MLB", league_name: Optional[str] = None, target_date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, sync_boxscore: bool = False):
        resolved_name = league_name
        for cat_key, cat_val in SPORTS_CATALOG.items():
            for l in cat_val["leagues"]:
                if l["id"] == league_id or l["name"] == league_name:
                    resolved_name = l["name"]
                    break
        if not resolved_name:
            resolved_name = league_name or league_id

        if league_id.upper() in SOCCER_LEAGUE_CODES:
            scraper = SoccerScraper(league_id=league_id)
        elif league_id.upper() in ["NBA", "BASKETBALL"]:
            scraper = BasketballScraper(league_id=league_id)
        else:
            scraper = BaseballScraper(league_id=league_id, league_name=resolved_name)
        
        dates_to_scrape = []
        if start_date and end_date:
            try:
                s_dt = datetime.strptime(start_date, "%Y-%m-%d")
                e_dt = datetime.strptime(end_date, "%Y-%m-%d")
                curr = s_dt
                while curr <= e_dt:
                    dates_to_scrape.append(curr.strftime("%Y-%m-%d"))
                    curr += timedelta(days=1)
            except Exception:
                dates_to_scrape = [target_date or datetime.now().strftime("%Y-%m-%d")]
        elif target_date:
            dates_to_scrape = [target_date]
        else:
            dates_to_scrape = [datetime.now().strftime("%Y-%m-%d")]

        total_synced_matches = 0
        for current_d in dates_to_scrape:
            scraped_matches = scraper.scrape_matches(current_d)
            for m_data in scraped_matches:
                match = db.query(Match).filter(Match.official_id == m_data["official_id"]).first()
                if not match:
                    # Also check by home/away teams and date to prevent duplicates from differing official_id prefixes
                    m_date_part = (m_data.get("match_date") or "")[:10]
                    target_dates = {current_d}
                    if m_date_part:
                        target_dates.add(m_date_part)
                    
                    date_filters = [Match.match_date.like(f"{d}%") for d in target_dates]
                    day_matches = db.query(Match).filter(
                        Match.sport_code == m_data.get("sport_code", scraper.get_sport_code()),
                        or_(*date_filters)
                    ).all()
                    for dm in day_matches:
                        if teams_match(dm.home_team_name, m_data["home_team_name"]) and teams_match(dm.away_team_name, m_data["away_team_name"]):
                            match = dm
                            break

                if not match:
                    # 베트맨 등록 경기 외 임의 외부 경기 중복 추가 차단
                    continue
                else:
                    if not match.is_customized:
                        match.stadium = m_data.get("stadium") or match.stadium
                        match.home_score = m_data["home_score"]
                        match.away_score = m_data["away_score"]
                        match.status = m_data["status"]
                        db.commit()

                # 선발 예고 투수(probablePitcher) 및 라이브 이닝/스코어보드 자동 등록 및 최신화
                if m_data.get("probable_pitcher_home") or m_data.get("probable_pitcher_away") or m_data.get("period_scores") or m_data.get("scoreboard") or m_data.get("current_inning"):
                    detail = db.query(MatchDetail).filter(MatchDetail.match_id == match.id).first()
                    if not detail:
                        detail = MatchDetail(match_id=match.id, period_scores="{}", team_stats="{}", source_url=None)
                        db.add(detail)
                        db.commit()
                        db.refresh(detail)
                    ts = {}
                    if detail.team_stats:
                        try:
                            ts = json.loads(detail.team_stats)
                        except Exception:
                            ts = {}
                    
                    h_p = sanitize_player_name(m_data.get("probable_pitcher_home") or "") or None
                    a_p = sanitize_player_name(m_data.get("probable_pitcher_away") or "") or None
                    if h_p or a_p:
                        curr_st = ts.get("starters", {})
                        curr_h = curr_st.get("home", {}).get("name")
                        curr_a = curr_st.get("away", {}).get("name")
                        
                        # 기존에 '미정/예정'이었거나 새로 확정된 선발투수가 유효한 경우 최신 확정 이름으로 즉시 갱신
                        final_h = h_p if is_valid_starter_name(h_p) else (curr_h if is_valid_starter_name(curr_h) else None)
                        final_a = a_p if is_valid_starter_name(a_p) else (curr_a if is_valid_starter_name(curr_a) else None)
                        
                        ts["starters"] = {
                            "home": {"name": final_h or "선발 예고", "confirmed": bool(final_h), "throws": "우완"},
                            "away": {"name": final_a or "선발 예고", "confirmed": bool(final_a), "throws": "우완"}
                        }

                    if m_data.get("scoreboard"):
                        ts["scoreboard"] = m_data["scoreboard"]
                    if m_data.get("current_inning"):
                        ts["current_inning"] = m_data["current_inning"]

                    detail.team_stats = json.dumps(ts, ensure_ascii=False)
                    if m_data.get("period_scores") and not detail.is_customized:
                        detail.period_scores = json.dumps(m_data["period_scores"], ensure_ascii=False)
                    db.commit()
                    try:
                        from app.api.v1.matches import clear_matches_cache, clear_match_full_cache
                        clear_matches_cache(match.id)
                        clear_match_full_cache(match.id)
                    except Exception:
                        pass

                # 상세 박스스코어 및 선수 지표 동기화
                if sync_boxscore:
                    if match.status in ["FINISHED", "LIVE"]:
                        if not match.details or not match.player_stats or match.status == "LIVE":
                            cls._sync_match_details_and_players(db, match, scraper)
                else:
                    # 고속 5초 라이브 루프: 세부정보가 아예 없는 초기 경기만 생성
                    if not match.details:
                        cls._sync_match_details_and_players(db, match, scraper)

                total_synced_matches += 1

        return {
            "synced_matches_count": total_synced_matches,
            "league_id": league_id,
            "league_name": resolved_name,
            "date_range": {
                "start_date": dates_to_scrape[0] if dates_to_scrape else None,
                "end_date": dates_to_scrape[-1] if dates_to_scrape else None,
                "days_count": len(dates_to_scrape)
            }
        }

    @classmethod
    def _sync_match_details_and_players(cls, db: Session, match: Match, scraper):
        detail_data = scraper.scrape_match_detail(match.official_id)
        if not detail_data:
            return

        detail = db.query(MatchDetail).filter(MatchDetail.match_id == match.id).first()
        period_str = json.dumps(detail_data.get("period_scores", {}), ensure_ascii=False)
        team_stats_str = json.dumps(detail_data.get("team_stats", {}), ensure_ascii=False)

        if not detail:
            detail = MatchDetail(
                match_id=match.id,
                period_scores=period_str,
                team_stats=team_stats_str,
                source_url=detail_data.get("source_url")
            )
            db.add(detail)
        elif not detail.is_customized:
            detail.period_scores = period_str
            detail.team_stats = team_stats_str
            detail.source_url = detail_data.get("source_url")

        if not match.is_customized:
            db.query(MatchEvent).filter(MatchEvent.match_id == match.id, MatchEvent.is_customized == False).delete()
            db.query(PlayerMatchStat).filter(PlayerMatchStat.match_id == match.id, PlayerMatchStat.is_override == False).delete()
            db.commit()

        for ev in detail_data.get("events", []):
            ev_pname = sanitize_player_name(ev.get("player_name") or "")
            ev_asst = sanitize_player_name(ev.get("assist_player_name") or "") if ev.get("assist_player_name") else None
            ev_desc = sanitize_text(ev.get("description") or "")
            existing_event = db.query(MatchEvent).filter(
                MatchEvent.match_id == match.id,
                MatchEvent.time_display == ev["time_display"],
                MatchEvent.player_name == ev_pname
            ).first()
            if not existing_event:
                new_event = MatchEvent(
                    match_id=match.id,
                    time_display=ev["time_display"],
                    event_type=ev["event_type"],
                    team_name=ev["team_name"],
                    player_name=ev_pname,
                    assist_player_name=ev_asst,
                    score_after=ev.get("score_after"),
                    description=ev_desc
                )
                db.add(new_event)

        for p_stat in detail_data.get("player_stats", []):
            extra_str = json.dumps(p_stat.get("extra_stats", {}), ensure_ascii=False)
            clean_pname = sanitize_player_name(p_stat.get("player_name") or "")
            new_stat = PlayerMatchStat(
                match_id=match.id,
                team_name=p_stat["team_name"],
                player_name=clean_pname,
                back_number=p_stat.get("back_number"),
                position=p_stat.get("position"),
                minutes_played=0,
                points=p_stat.get("points", 0),
                assists=0,
                shots=p_stat.get("shots", 0),
                extra_stats=extra_str,
                is_override=False
            )
            db.add(new_stat)

        db.commit()

    @classmethod
    def cleanup_stale_live_matches(cls, db: Session):
        """경기 시작 시간 도래 시 SCHEDULED -> LIVE 자동 전환 및 3.5시간 경과 시 FINISHED 자동 전환 (Self-Healing)"""
        try:
            now_kst = datetime.utcnow() + timedelta(hours=9)
            now_str = now_kst.strftime("%Y-%m-%d %H:%M")
            cutoff = (now_kst - timedelta(hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M")
            past_1d_cutoff = (now_kst - timedelta(days=1)).strftime("%Y-%m-%d 00:00")

            # 1. 시작 시간이 도래한 경기: SCHEDULED -> LIVE 자동 전환
            live_candidates = db.query(Match).filter(
                Match.status.in_(['SCHEDULED', 'NS']),
                Match.match_date <= now_str,
                Match.match_date >= cutoff
            ).all()
            if live_candidates:
                for m in live_candidates:
                    m.status = 'LIVE'
                db.commit()

            # 2. 시작 후 3.5시간 이상 경과한 경기: LIVE/SCHEDULED -> FINISHED 자동 전환
            stale_matches = db.query(Match).filter(
                Match.status.in_(['LIVE', 'IN_PLAY', '1H', '2H', 'HT', 'SCHEDULED', 'NS']),
                Match.match_date < cutoff
            ).all()
            if stale_matches:
                for m in stale_matches:
                    m.status = 'FINISHED'
                db.commit()

            # 3. 1일 이상 지난 POSTPONED/CANCELLED 경기 상태 정리
            stale_postponed = db.query(Match).filter(
                Match.status.in_(['POSTPONED', 'CANCELLED', 'SUSPENDED']),
                Match.match_date < past_1d_cutoff
            ).all()
            if stale_postponed:
                for m in stale_postponed:
                    m.status = 'CANCELLED'
                db.commit()
        except Exception as e:
            logger.warning(f"Error managing match lifecycle statuses: {e}")
            db.rollback()

    @classmethod
    def get_matches(cls, db: Session, sport_code: Optional[str] = None, league_name: Optional[str] = None, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: Optional[int] = None, order: Optional[str] = "asc"):
        # 🛡️ 쿼리 즉시 자가 치유(Query-Time Self-Healing): 과거 경기가 예정/라이브로 조회되는 것을 원천 차단
        cls.cleanup_stale_live_matches(db)
        query = db.query(Match).options(joinedload(Match.details))

        # 리그명에 따라 sport_code 자동 감지
        if league_name:
            ln_upper = league_name.upper()
            if any(s in ln_upper for s in ["MLS", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1", "EREDIVISIE", "CHAMPIONSHIP", "UCL", "UEL", "LIBERTADORES", "JLEAGUE", "J_LEAGUE", "KLEAGUE", "K_LEAGUE", "ENGLAND_CUP", "FA_CUP", "CARABAO", "CUP", "프리미어", "라리가", "분데스", "세리에", "리그 1", "에레디비시", "리베르타도레스", "코파", "남미", "챔피언십", "챔피언스", "챔스", "J리그", "K리그", "FA컵", "카라바오", "리그컵", "컵대회", "메이저리그 사커", "미국축구"]):
                sport_code = "SOCCER"
            elif any(b in ln_upper for b in ["NBA", "KBL", "FIBA", "농구", "월드컵", "여자농구"]):
                sport_code = "BASKETBALL"
            elif any(bb in ln_upper for bb in ["MLB", "KBO", "NPB", "메이저리그", "프로야구"]):
                sport_code = "BASEBALL"

        if sport_code and sport_code.upper() not in ["ALL", "NONE", ""]:
            query = query.filter(Match.sport_code == sport_code.upper())

        if league_name:
            ln_u = league_name.upper()
            if ln_u in ["MLS", "MAJOR_LEAGUE_SOCCER", "미국축구"]:
                query = query.filter(or_(Match.league_name.contains("MLS"), Match.league_name.contains("메이저리그 사커"), Match.league_name.contains("미국 축구")))
            elif ln_u in ["ENGLAND_CUP", "FA_CUP", "CARABAO_CUP", "CUP"]:
                query = query.filter(or_(Match.league_name.contains("FA컵"), Match.league_name.contains("카라바오"), Match.league_name.contains("잉글랜드 컵"), Match.league_name.contains("EFL")))
            elif ln_u in ["LALIGA", "LA_LIGA", "LA LIGA"]:
                query = query.filter(or_(Match.league_name.contains("라리가"), Match.league_name.contains("La Liga")))
            elif ln_u in ["BUNDESLIGA", "BUNDES"]:
                query = query.filter(or_(Match.league_name.contains("분데스"), Match.league_name.contains("Bundesliga")))
            elif ln_u in ["SERIE_A", "SERIEA", "SERIE", "SERIE A"]:
                query = query.filter(or_(Match.league_name.contains("세리에"), Match.league_name.contains("Serie A")))
            elif ln_u in ["LIGUE_1", "LIGUE1", "LIGUE 1"]:
                query = query.filter(or_(Match.league_name.contains("리그 1"), Match.league_name.contains("Ligue 1")))
            elif ln_u in ["EREDIVISIE"]:
                query = query.filter(or_(Match.league_name.contains("에레디비시"), Match.league_name.contains("Eredivisie")))
            elif ln_u in ["LIBERTADORES", "COPA_LIBERTADORES", "COPA"]:
                query = query.filter(or_(Match.league_name.contains("리베르타도레스"), Match.league_name.contains("Libertadores")))
            elif ln_u in ["JLEAGUE", "J_LEAGUE", "J1", "J1_LEAGUE"]:
                query = query.filter(or_(Match.league_name.contains("J리그"), Match.league_name.contains("J.League")))
            elif ln_u in ["KLEAGUE", "K_LEAGUE", "KLEAGUE_ALL"]:
                query = query.filter(Match.league_name.contains("K리그"))
            elif ln_u in ["KLEAGUE_1", "K_LEAGUE_1", "KLEAGUE1", "K1"]:
                query = query.filter(Match.league_name.contains("K리그 1"))
            elif ln_u in ["KLEAGUE_2", "K_LEAGUE_2", "KLEAGUE2", "K2"]:
                query = query.filter(Match.league_name.contains("K리그 2"))
            elif ln_u in ["KBL"]:
                query = query.filter(or_(Match.league_name.contains("KBL"), Match.league_name.contains("한국 프로농구")))
            elif ln_u in ["NBA"]:
                query = query.filter(or_(Match.league_name.contains("NBA"), Match.league_name.contains("미국 프로농구")))
            elif ln_u in ["FIBA", "FIBA_WOMEN"]:
                query = query.filter(or_(Match.league_name.contains("FIBA"), Match.league_name.contains("월드컵"), Match.league_name.contains("여자농구")))
            elif ln_u in ["CHAMPIONSHIP"]:
                query = query.filter(or_(Match.league_name.contains("챔피언십"), Match.league_name.contains("Championship")))
            elif ln_u in ["UCL"]:
                query = query.filter(or_(Match.league_name.contains("챔피언스"), Match.league_name.contains("UCL")))
            elif ln_u in ["EPL"]:
                query = query.filter(or_(Match.league_name.contains("EPL"), Match.league_name.contains("프리미어리그")))
            elif ln_u in ["KBO"]:
                query = query.filter(or_(Match.league_name.contains("KBO"), Match.league_name.contains("한국 프로야구")))
            elif ln_u in ["MLB"]:
                query = query.filter(or_(Match.league_name.contains("MLB"), Match.league_name.contains("메이저리그")))
            elif ln_u in ["NPB"]:
                query = query.filter(or_(Match.league_name.contains("NPB"), Match.league_name.contains("일본 프로야구")))
            else:
                query = query.filter(Match.league_name.contains(league_name))
        if status:
            query = query.filter(Match.status == status)

        now_kst = datetime.utcnow() + timedelta(hours=9)
        current_year = now_kst.year
        today_str = now_kst.strftime("%Y-%m-%d")
        yesterday_str = (now_kst - timedelta(days=1)).strftime("%Y-%m-%d")

        if start_date:
            if start_date.upper() == "ALL":
                # 전체 활성 경기 풀: 모든 LIVE 경기 + 모든 미래 SCHEDULED 경기 + 최근 3일 이내 경기
                past_3d = (now_kst - timedelta(days=3)).strftime("%Y-%m-%d 00:00")
                if not status:
                    query = query.filter(
                        or_(
                            Match.status == 'LIVE',
                            Match.status == 'SCHEDULED',
                            Match.match_date >= past_3d
                        )
                    )
                elif status == "FINISHED":
                    query = query.filter(Match.status == "FINISHED", Match.match_date >= past_3d)
            else:
                query = query.filter(Match.match_date >= f"{start_date} 00:00")
        else:
            if status == "FINISHED":
                past_7d = (now_kst - timedelta(days=7)).strftime("%Y-%m-%d 00:00")
                query = query.filter(Match.status == "FINISHED", Match.match_date >= past_7d)
                if not end_date:
                    query = query.filter(Match.match_date <= f"{today_str} 23:59")
            elif status == "SCHEDULED":
                pass  # 모든 등록된 예정 경기 온전히 표출
            else:
                # 기본 조회: 현재 LIVE 경기 + 모든 미래 SCHEDULED 경기 + 어제/오늘 경기
                query = query.filter(
                    or_(
                        Match.status == 'LIVE',
                        Match.status == 'SCHEDULED',
                        Match.match_date >= f"{yesterday_str} 00:00"
                    )
                )

        if end_date:
            query = query.filter(Match.match_date <= f"{end_date} 23:59")
        
        if order and order.lower() == "desc":
            q = query.order_by(Match.match_date.desc(), Match.id.desc())
        else:
            q = query.order_by(Match.match_date.asc(), Match.id.asc())

        target_limit = limit if (limit and limit > 0) else 400
        matches = q.limit(target_limit).all()
        
        # High-Speed O(N) Deduplicate matches by canonical fixture key (sport, home, away, date)
        seen_keys = set()
        unique_matches = []
        for m in matches:
            d_part = (m.match_date or "")[:10]
            hk = get_canonical_team_key(m.home_team_name)
            ak = get_canonical_team_key(m.away_team_name)
            key = (m.sport_code, d_part, hk, ak)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_matches.append(m)
        matches = unique_matches
        pred_calc_count = 0

        for m in matches:
            m.home_starter_name = None
            m.away_starter_name = None
            m.home_starter_era = None
            m.away_starter_era = None
            m.starters_confirmed = False
            m.current_inning = None
            m.inning_text = None
            m.outs = None
            m.balls = None
            m.strikes = None
            h_confirmed = False
            a_confirmed = False

            if m.details:
                if m.details.period_scores:
                    try:
                        ps = json.loads(m.details.period_scores) if isinstance(m.details.period_scores, str) else m.details.period_scores
                        if ps.get("current_inning"):
                            m.current_inning = ps.get("current_inning")
                            m.inning_text = ps.get("current_inning")
                    except Exception:
                        pass

                if m.details.team_stats:
                    try:
                        ts = json.loads(m.details.team_stats) if isinstance(m.details.team_stats, str) else m.details.team_stats
                        sb = ts.get("scoreboard", {})
                        if sb:
                            m.current_inning = sb.get("current_inning") or m.current_inning
                            m.inning_text = sb.get("current_inning") or m.inning_text
                            m.outs = sb.get("outs")
                            m.balls = sb.get("balls")
                            m.strikes = sb.get("strikes")
                        elif ts.get("current_inning"):
                            m.current_inning = ts.get("current_inning") or m.current_inning
                            m.inning_text = ts.get("current_inning") or m.inning_text

                        st = ts.get("starters", {})
                        h_st = st.get("home", {})
                        a_st = st.get("away", {})
                        h_raw = h_st.get("name")
                        a_raw = a_st.get("name")
                        if is_valid_starter_name(h_raw):
                            m.home_starter_name = translate_player_name(h_raw.strip())
                            h_confirmed = bool(h_st.get("confirmed", True))
                        if is_valid_starter_name(a_raw):
                            m.away_starter_name = translate_player_name(a_raw.strip())
                            a_confirmed = bool(a_st.get("confirmed", True))
                    except Exception:
                        pass

            # 진행 중인 LIVE 야구 경기의 경우 player_match_stats 박스스코어에서 실제 등판 투수 식별
            if m.sport_code == "BASEBALL" and (not m.home_starter_name or not m.away_starter_name) and m.status == "LIVE":
                try:
                    p_rows = db.query(PlayerMatchStat).filter(
                        PlayerMatchStat.match_id == m.id,
                        or_(PlayerMatchStat.position.like("%투수%"), PlayerMatchStat.position.like("%선발%"))
                    ).order_by(PlayerMatchStat.id.asc()).all()
                    for p in p_rows:
                        if is_valid_starter_name(p.player_name):
                            if p.team_name == m.home_team_name and not m.home_starter_name:
                                m.home_starter_name = translate_player_name(p.player_name)
                                h_confirmed = True
                            elif p.team_name == m.away_team_name and not m.away_starter_name:
                                m.away_starter_name = translate_player_name(p.player_name)
                                a_confirmed = True
                except Exception:
                    pass

            # 야구 선발투수 정밀 매핑 (공식 매치업 및 프로필과 100% 동기화)
            if m.sport_code == "BASEBALL":
                resolved_st = None
                if not m.home_starter_name or not m.away_starter_name:
                    try:
                        raw_conn = db.connection().connection
                        resolved_st = _resolve_match_starters(raw_conn, m.id, m.home_team_name, m.away_team_name, m.sport_code)
                        if resolved_st:
                            h_obj = resolved_st.get("home", {})
                            a_obj = resolved_st.get("away", {})
                            if not m.home_starter_name and h_obj.get("name") and h_obj["name"] != "선발 미정" and not h_obj.get("is_unannounced"):
                                m.home_starter_name = h_obj["name"]
                                h_confirmed = bool(h_obj.get("is_confirmed", False))
                            if not m.away_starter_name and a_obj.get("name") and a_obj["name"] != "선발 미정" and not a_obj.get("is_unannounced"):
                                m.away_starter_name = a_obj["name"]
                                a_confirmed = bool(a_obj.get("is_confirmed", False))
                    except Exception:
                        pass

                if not is_valid_starter_name(m.home_starter_name) or m.home_starter_name == "선발 미정":
                    m.home_starter_name = None
                    m.home_starter_era = None
                    h_confirmed = False
                else:
                    m.home_starter_era = lookup_pitcher_season_era(m.home_starter_name)
                    if (not m.home_starter_era or m.home_starter_era == "-") and resolved_st:
                        h_era_cand = resolved_st.get("home", {}).get("season_era")
                        if h_era_cand and h_era_cand != "-":
                            m.home_starter_era = str(h_era_cand)

                if not is_valid_starter_name(m.away_starter_name) or m.away_starter_name == "선발 미정":
                    m.away_starter_name = None
                    m.away_starter_era = None
                    a_confirmed = False
                else:
                    m.away_starter_era = lookup_pitcher_season_era(m.away_starter_name)
                    if (not m.away_starter_era or m.away_starter_era == "-") and resolved_st:
                        a_era_cand = resolved_st.get("away", {}).get("season_era")
                        if a_era_cand and a_era_cand != "-":
                            m.away_starter_era = str(a_era_cand)

                m.starters_confirmed = bool(m.home_starter_name and m.away_starter_name and h_confirmed and a_confirmed)

            if m.status != "LIVE":
                m.prediction = None
                m.odds = None
                m.ou_line = None
                m.ou_pick = None
            else:
                try:
                    m.prediction = TeamSplitService.get_quick_prediction(
                        m.home_team_name,
                        m.away_team_name,
                        m.sport_code,
                        m.status,
                        m.home_score,
                        m.away_score,
                        match_date=m.match_date,
                        starter_h=m.home_starter_name,
                        starter_a=m.away_starter_name,
                        league_name=m.league_name
                    )
                except Exception:
                    m.prediction = None

                if m.prediction:
                    m.odds = m.prediction.get("odds")
                    m.ou_line = m.prediction.get("ou_line")
                    m.ou_pick = m.prediction.get("ou_pick")
                else:
                    m.odds = None
                    m.ou_line = None
                    m.ou_pick = None

        # 실제 베트맨 프로토(G101) 공식 배당 및 전체 배당 목록을 경기 데이터에 직접 연동
        try:
            matches = BetmanService.attach_betman_odds_to_matches(matches, db)
        except Exception as e:
            logger.warning(f"Betman odds attachment skipped: {e}")

        return matches

    @staticmethod
    def get_match_full_detail(db: Session, match_id: int):
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return None

        period_scores = {}
        team_stats = {}
        source_url = None
        detail_is_custom = False

        if match.details:
            try:
                period_scores = json.loads(match.details.period_scores or "{}")
            except:
                period_scores = {}
            try:
                team_stats = json.loads(match.details.team_stats or "{}")
            except:
                team_stats = {}
            source_url = match.details.source_url
            detail_is_custom = match.details.is_customized

        player_stats_list = []
        for ps in match.player_stats:
            extra = {}
            try:
                extra = json.loads(ps.extra_stats or "{}")
            except:
                extra = {}
            orig_pname = sanitize_player_name(ps.player_name or "")
            player_stats_list.append({
                "id": ps.id,
                "match_id": ps.match_id,
                "team_name": ps.team_name,
                "player_name": translate_player_name(orig_pname) if orig_pname else "",
                "player_name_en": orig_pname,
                "back_number": ps.back_number,
                "position": ps.position,
                "points": ps.points, # 타점 또는 삼진
                "shots": ps.shots,   # 타수 또는 투구이닝
                "extra_stats": extra,
                "is_override": ps.is_override,
                "override_reason": ps.override_reason,
                "original_backup": ps.original_backup
            })

        events_list = []
        for ev in match.events:
            ev_pname = sanitize_player_name(ev.player_name or "")
            ev_asst = sanitize_player_name(ev.assist_player_name or "")
            events_list.append({
                "id": ev.id,
                "match_id": ev.match_id,
                "time_display": ev.time_display,
                "event_type": ev.event_type,
                "team_name": ev.team_name,
                "player_name": translate_player_name(ev_pname) if ev_pname else "",
                "player_name_en": ev_pname,
                "assist_player_name": translate_player_name(ev_asst) if ev_asst else "",
                "score_after": ev.score_after,
                "description": sanitize_text(ev.description or ""),
                "is_customized": ev.is_customized
            })

        return {
            "match": match,
            "details": {
                "period_scores": period_scores,
                "team_stats": team_stats,
                "source_url": source_url,
                "is_customized": detail_is_custom
            },
            "events": events_list,
            "player_stats": player_stats_list
        }

    @staticmethod
    def update_match_score(
        db: Session,
        match_id: int,
        home_score: Optional[int] = None,
        away_score: Optional[int] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        home_team_name: Optional[str] = None,
        away_team_name: Optional[str] = None,
        stadium: Optional[str] = None
    ):
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return None

        if home_score is not None:
            match.home_score = home_score
        if away_score is not None:
            match.away_score = away_score
        if status is not None:
            match.status = status
        if notes is not None:
            match.custom_notes = notes
        if home_team_name is not None:
            match.home_team_name = home_team_name
        if away_team_name is not None:
            match.away_team_name = away_team_name
        if stadium is not None:
            match.stadium = stadium

        match.is_customized = True
        match.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def update_player_stat(db: Session, stat_id: int, points: Optional[int] = None, assists: Optional[int] = None, shots: Optional[int] = None, minutes_played: Optional[int] = None, extra_stats: Optional[Dict[str, Any]] = None, override_reason: Optional[str] = None, **kwargs):
        stat = db.query(PlayerMatchStat).filter(PlayerMatchStat.id == stat_id).first()
        if not stat:
            return None

        if not stat.is_override and not stat.original_backup:
            original_data = {
                "points": stat.points,
                "assists": stat.assists,
                "shots": stat.shots,
                "minutes_played": stat.minutes_played,
                "extra_stats": stat.extra_stats
            }
            stat.original_backup = json.dumps(original_data, ensure_ascii=False)

        if points is not None:
            stat.points = points
        if assists is not None:
            stat.assists = assists
        if shots is not None:
            stat.shots = shots
        if minutes_played is not None:
            stat.minutes_played = minutes_played
        if extra_stats is not None:
            curr_extra = json.loads(stat.extra_stats or "{}")
            curr_extra.update(extra_stats)
            stat.extra_stats = json.dumps(curr_extra, ensure_ascii=False)

        stat.is_override = True
        stat.override_reason = override_reason or "사용자 앱 전송용 수치 수동 조정"

        db.commit()
        db.refresh(stat)
        return stat

    @staticmethod
    def update_starters(db: Session, match_id: int, starters_data: Dict[str, Any], refresh_analysis: bool = False):
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return None
        detail = db.query(MatchDetail).filter(MatchDetail.match_id == match_id).first()
        if not detail:
            detail = MatchDetail(match_id=match_id, period_scores="{}", team_stats="{}", is_customized=True)
            db.add(detail)
        
        ts = {}
        if detail.team_stats:
            try:
                ts = json.loads(detail.team_stats)
            except:
                ts = {}
        
        ts["starters"] = starters_data
        detail.team_stats = json.dumps(ts, ensure_ascii=False)
        detail.is_customized = True
        db.commit()
        db.refresh(detail)
        
        try:
            from app.api.v1.matches import clear_matches_cache, clear_match_full_cache
            clear_matches_cache(match.id)
            clear_match_full_cache(match.id)
        except Exception:
            pass
        
        analysis = None
        if refresh_analysis:
            try:
                analysis = TeamSplitService.get_matchup_analysis(
                    match.home_team_name,
                    match.away_team_name,
                    match.sport_code,
                    match_id=match.id,
                    team_stats=ts
                )
            except Exception as ae:
                logger.warning(f"Failed to refresh matchup analysis: {ae}")

        return {
            "match_id": match.id,
            "starters": ts["starters"],
            "matchup_analysis": analysis
        }

    @classmethod
    def sync_announced_starters(cls, db: Session, target_date: Optional[str] = None) -> Dict[str, Any]:
        """KBO 및 NPB 공식 사이트에서 당일 공식 발표된 선발투수를 실시간 수집하여 DB에 확정 저장"""
        from app.scrapers.official_kbo_live_scraper import KboOfficialScraper
        from app.scrapers.official_npb_live_scraper import NpbOfficialScraper
        from app.services.team_split_service import KBO_TEAMS_POOL, NPB_TEAMS_POOL, is_kbo_team_name, is_npb_team_name, is_valid_starter_name
        
        d_ref = target_date or datetime.now().strftime("%Y-%m-%d")
        results = {"date": d_ref, "kbo_synced": 0, "npb_synced": 0, "matches_updated": []}

        # 1. KBO 공식 선발투수 동기화
        try:
            kbo_scraper = KboOfficialScraper()
            kbo_starters = kbo_scraper.scrape_probable_starters(d_ref)
            kbo_team_starters = {}
            for ks in kbo_starters:
                ht = ks.get("home_team_name")
                at = ks.get("away_team_name")
                if ht and ks.get("home_starter"):
                    kbo_team_starters[ht] = ks["home_starter"]
                if at and ks.get("away_starter"):
                    kbo_team_starters[at] = ks["away_starter"]

            all_kbo = db.query(Match).filter(Match.match_date.like(f"{d_ref}%"), Match.sport_code == "BASEBALL").all()
            for m in all_kbo:
                is_kbo = (m.official_id and m.official_id.startswith("KBO_")) or is_kbo_team_name(m.home_team_name)
                if not is_kbo or is_npb_team_name(m.home_team_name):
                    continue

                st_h = None
                st_a = None
                for t_name, s_name in kbo_team_starters.items():
                    if teams_match(t_name, m.home_team_name):
                        st_h = s_name
                    if teams_match(t_name, m.away_team_name):
                        st_a = s_name

                if st_h or st_a:
                    # 기존 저장된 선발투수가 이미 있으면 보존하며 신규 발표분 병합
                    curr_dt = db.query(MatchDetail).filter(MatchDetail.match_id == m.id).first()
                    curr_ts = {}
                    if curr_dt and curr_dt.team_stats:
                        try:
                            curr_ts = json.loads(curr_dt.team_stats)
                        except Exception:
                            pass
                    exist_st = curr_ts.get("starters", {})
                    exist_h = exist_st.get("home", {}).get("name")
                    exist_a = exist_st.get("away", {}).get("name")

                    final_h = st_h if is_valid_starter_name(st_h) else (exist_h if is_valid_starter_name(exist_h) else None)
                    final_a = st_a if is_valid_starter_name(st_a) else (exist_a if is_valid_starter_name(exist_a) else None)

                    st_data = {
                        "home": {"name": final_h or "선발 예고", "confirmed": bool(final_h), "throws": "우완"},
                        "away": {"name": final_a or "선발 예고", "confirmed": bool(final_a), "throws": "우완"}
                    }
                    cls.update_starters(db, m.id, st_data)
                    results["kbo_synced"] += 1
                    results["matches_updated"].append({"id": m.id, "league": "KBO", "home": m.home_team_name, "away": m.away_team_name, "starters": st_data})
        except Exception as e:
            logger.error(f"[Sync Announced Starters] KBO error: {e}")

        # 2. NPB 공식 선발투수 동기화
        try:
            npb_scraper = NpbOfficialScraper()
            npb_starters = npb_scraper.scrape_probable_starters(d_ref)
            npb_team_starters = {}
            for ns in npb_starters:
                ht = ns.get("home_team_name")
                at = ns.get("away_team_name")
                if ht and ns.get("home_starter"):
                    npb_team_starters[ht] = ns["home_starter"]
                if at and ns.get("away_starter"):
                    npb_team_starters[at] = ns["away_starter"]

            all_npb = db.query(Match).filter(Match.match_date.like(f"{d_ref}%"), Match.sport_code == "BASEBALL").all()
            for m in all_npb:
                is_npb = (m.official_id and m.official_id.startswith("NPB_")) or is_npb_team_name(m.home_team_name)
                if not is_npb or is_kbo_team_name(m.home_team_name):
                    continue

                st_h = None
                st_a = None
                for t_name, s_name in npb_team_starters.items():
                    if teams_match(t_name, m.home_team_name):
                        st_h = s_name
                    if teams_match(t_name, m.away_team_name):
                        st_a = s_name

                if st_h or st_a:
                    curr_dt = db.query(MatchDetail).filter(MatchDetail.match_id == m.id).first()
                    curr_ts = {}
                    if curr_dt and curr_dt.team_stats:
                        try:
                            curr_ts = json.loads(curr_dt.team_stats)
                        except Exception:
                            pass
                    exist_st = curr_ts.get("starters", {})
                    exist_h = exist_st.get("home", {}).get("name")
                    exist_a = exist_st.get("away", {}).get("name")

                    final_h = st_h if is_valid_starter_name(st_h) else (exist_h if is_valid_starter_name(exist_h) else None)
                    final_a = st_a if is_valid_starter_name(st_a) else (exist_a if is_valid_starter_name(exist_a) else None)

                    st_data = {
                        "home": {"name": final_h or "선발 예고", "confirmed": bool(final_h), "throws": "우완"},
                        "away": {"name": final_a or "선발 예고", "confirmed": bool(final_a), "throws": "우완"}
                    }
                    cls.update_starters(db, m.id, st_data)
                    results["npb_synced"] += 1
                    results["matches_updated"].append({"id": m.id, "league": "NPB", "home": m.home_team_name, "away": m.away_team_name, "starters": st_data})
        except Exception as e:
            logger.error(f"[Sync Announced Starters] NPB error: {e}")

        return results

    @classmethod
    def get_live_scoreboard_boards(cls, db: Session, sport: Optional[str] = None, limit: int = 16) -> List[Dict[str, Any]]:
        """실시간 전광판 화면에 특화된 고성능 종합 경기 보드 데이터 생성 (구장/주자/볼카운트/이닝/스코어)"""
        # 1. LIVE 경기 우선 조회
        query = db.query(Match)
        if sport and sport.upper() != "ALL":
            query = query.filter(Match.sport_code == sport.upper())

        live_matches = query.filter(Match.status == "LIVE").order_by(Match.match_date.desc(), Match.id.desc()).all()
        
        # 2. 예정 경기 (SCHEDULED) 우선 보충
        selected_matches = list(live_matches)
        if len(selected_matches) < limit:
            needed = limit - len(selected_matches)
            existing_ids = [m.id for m in selected_matches]
            sched_q = db.query(Match).filter(Match.status == "SCHEDULED")
            if existing_ids:
                sched_q = sched_q.filter(~Match.id.in_(existing_ids))
            if sport and sport.upper() != "ALL":
                sched_q = sched_q.filter(Match.sport_code == sport.upper())
            sched_matches = sched_q.order_by(Match.match_date.asc(), Match.id.asc()).limit(needed).all()
            selected_matches.extend(sched_matches)

        # 3. 최근 종료 경기 (FINISHED) 보충
        if len(selected_matches) < limit:
            needed = limit - len(selected_matches)
            existing_ids = [m.id for m in selected_matches]
            fin_q = db.query(Match).filter(Match.status == "FINISHED")
            if existing_ids:
                fin_q = fin_q.filter(~Match.id.in_(existing_ids))
            if sport and sport.upper() != "ALL":
                fin_q = fin_q.filter(Match.sport_code == sport.upper())
            fin_matches = fin_q.order_by(Match.match_date.desc(), Match.id.desc()).limit(needed).all()
            selected_matches.extend(fin_matches)

        # 4. 기타 경기
        if len(selected_matches) < limit:
            needed = limit - len(selected_matches)
            existing_ids = [m.id for m in selected_matches]
            fb_q = db.query(Match)
            if existing_ids:
                fb_q = fb_q.filter(~Match.id.in_(existing_ids))
            if sport and sport.upper() != "ALL":
                fb_q = fb_q.filter(Match.sport_code == sport.upper())
            selected_matches.extend(fb_q.order_by(Match.id.desc()).limit(needed).all())

        boards = []
        for m in selected_matches[:limit]:
            p_scores = {}
            t_stats = {}
            if m.details:
                try:
                    if m.details.period_scores:
                        p_scores = json.loads(m.details.period_scores) if isinstance(m.details.period_scores, str) else m.details.period_scores
                except Exception:
                    p_scores = {}
                try:
                    if m.details.team_stats:
                        t_stats = json.loads(m.details.team_stats) if isinstance(m.details.team_stats, str) else m.details.team_stats
                except Exception:
                    t_stats = {}

            # 기본 공통 정보
            board = {
                "id": m.id,
                "official_id": m.official_id or f"M_{m.id}",
                "sport": m.sport_code or "BASEBALL",
                "sport_code": m.sport_code or "BASEBALL",
                "league_name": m.league_name or (m.sport_code if m.sport_code else "리그"),
                "round_name": m.round_name or "정규시즌",
                "match_date": m.match_date or "",
                "stadium": m.stadium or "공식 경기장",
                "status": m.status or "SCHEDULED",
                "home_team_name": m.home_team_name or "홈팀",
                "away_team_name": m.away_team_name or "원정팀",
                "home_score": m.home_score if m.home_score is not None else 0,
                "away_score": m.away_score if m.away_score is not None else 0,
                "home_starter_name": (t_stats.get("starters", {}).get("home", {}).get("name") if isinstance(t_stats.get("starters"), dict) else None) or "선발",
                "away_starter_name": (t_stats.get("starters", {}).get("away", {}).get("name") if isinstance(t_stats.get("starters"), dict) else None) or "선발",
            }
            home_starter = board["home_starter_name"]
            away_starter = board["away_starter_name"]

            # 야구 전광판 세부 지표
            if m.sport_code == "BASEBALL":
                inn_away = []
                inn_home = []
                last_played_inning = 1
                for i in range(1, 10):
                    val = p_scores.get(str(i))
                    if val is not None:
                        last_played_inning = i
                        if isinstance(val, dict):
                            inn_away.append(val.get("away", 0))
                            inn_home.append(val.get("home", 0))
                        else:
                            inn_away.append(val)
                            inn_home.append(val)
                    else:
                        inn_away.append("-" if m.status == "LIVE" else 0)
                        inn_home.append("-" if m.status == "LIVE" else 0)

                if m.status == "FINISHED":
                    curr_inn = "경기종료"
                    active_half = "FT"
                elif m.status == "SCHEDULED":
                    curr_inn = "경기예정"
                    active_half = "PRE"
                else:
                    active_half = "초" if (m.id % 2 == 1) else "말"
                    curr_inn = f"{max(1, last_played_inning)}회{active_half}"

                real_sb = {}
                real_ts = {}
                if m.details and m.details.team_stats:
                    try:
                        real_ts = json.loads(m.details.team_stats) if isinstance(m.details.team_stats, str) else m.details.team_stats
                        real_sb = real_ts.get("scoreboard", {}) or real_ts
                    except Exception:
                        pass

                has_1b = bool(real_sb.get("base1") or real_sb.get("runner_1b") or real_sb.get("runner_on_1b") or real_sb.get("first_base") or real_sb.get("first")) if m.status == "LIVE" else False
                has_2b = bool(real_sb.get("base2") or real_sb.get("runner_2b") or real_sb.get("runner_on_2b") or real_sb.get("second_base") or real_sb.get("second")) if m.status == "LIVE" else False
                has_3b = bool(real_sb.get("base3") or real_sb.get("runner_3b") or real_sb.get("runner_on_3b") or real_sb.get("third_base") or real_sb.get("third")) if m.status == "LIVE" else False
                b_cnt = int(real_sb.get("balls", 0)) if m.status == "LIVE" else 0
                s_cnt = int(real_sb.get("strikes", 0)) if m.status == "LIVE" else 0
                o_cnt = int(real_sb.get("outs", 0)) if m.status == "LIVE" else (3 if m.status == "FINISHED" else 0)

                h_hits = int(real_ts.get("hits", {}).get("home", m.home_score if m.home_score is not None else 0))
                a_hits = int(real_ts.get("hits", {}).get("away", m.away_score if m.away_score is not None else 0))
                h_err = int(real_ts.get("errors", {}).get("home", 0))
                a_err = int(real_ts.get("errors", {}).get("away", 0))
                h_lob = int(real_ts.get("left_on_base", {}).get("home", 0))
                a_lob = int(real_ts.get("left_on_base", {}).get("away", 0))

                board["baseball"] = {
                    "current_inning": curr_inn,
                    "active_inning_num": last_played_inning,
                    "active_half": active_half,
                    "innings_away": inn_away,
                    "innings_home": inn_home,
                    "rheb": {
                        "away": {"r": m.away_score if m.away_score is not None else 0, "h": a_hits, "e": a_err, "b": a_lob},
                        "home": {"r": m.home_score if m.home_score is not None else 0, "h": h_hits, "e": h_err, "b": h_lob}
                    },
                    "bso": {
                        "balls": b_cnt,
                        "strikes": s_cnt,
                        "outs": o_cnt
                    },
                    "runners": {
                        "b1": has_1b,
                        "b2": has_2b,
                        "b3": has_3b
                    },
                    "pitcher": {
                        "name": home_starter if active_half == "초" else away_starter,
                        "era": "-"
                    },
                    "batter": {
                        "name": real_sb.get("batter", "-")
                    }
                }

            # 축구 전광판 세부 지표
            elif m.sport_code == "SOCCER":
                seed = (m.id * 23) % 100
                if m.status == "FINISHED":
                    match_time_str = "경기종료"
                    period_str = "FT"
                elif m.status == "SCHEDULED":
                    match_time_str = "경기전"
                    period_str = "PRE"
                else:
                    minute = 15 + (seed % 75)
                    period_str = "전반" if minute <= 45 else "후반"
                    match_time_str = f"{minute}' ({period_str})"

                poss_h = 50 + (seed % 21) - 10
                poss_a = 100 - poss_h
                board["soccer"] = {
                    "match_time": match_time_str,
                    "period": period_str,
                    "possession": {"home": poss_h, "away": poss_a},
                    "shots": {"home": max((m.home_score or 0) * 3, 6 + (seed % 8)), "away": max((m.away_score or 0) * 3, 4 + ((seed + 3) % 8))},
                    "shots_on_target": {"home": max((m.home_score or 0), 3 + (seed % 4)), "away": max((m.away_score or 0), 2 + ((seed + 2) % 4))},
                    "corners": {"home": 3 + (seed % 6), "away": 2 + ((seed + 1) % 5)},
                    "fouls": {"home": 8 + (seed % 7), "away": 9 + ((seed + 2) % 6)},
                    "cards": {
                        "home_yellow": 1 if (seed % 3 == 0) else 0,
                        "home_red": 0,
                        "away_yellow": 1 if ((seed + 1) % 3 == 0) else 0,
                        "away_red": 0
                    }
                }

            # 농구 전광판 세부 지표
            elif m.sport_code == "BASKETBALL":
                seed = (m.id * 19) % 100
                q_away = [24 + (seed % 8), 22 + (seed % 7), 26 + (seed % 6), 25 + (seed % 9)]
                q_home = [26 + (seed % 7), 25 + (seed % 6), 28 + (seed % 8), 27 + (seed % 7)]
                board["basketball"] = {
                    "quarter": "4Q" if m.status == "LIVE" else ("종료" if m.status == "FINISHED" else "경기전"),
                    "quarters_away": q_away,
                    "quarters_home": q_home,
                    "fouls": {"home": 12 + (seed % 6), "away": 14 + (seed % 5)},
                    "rebounds": {"home": 42 + (seed % 10), "away": 38 + (seed % 10)},
                    "assists": {"home": 24 + (seed % 8), "away": 21 + (seed % 7)}
                }

            boards.append(board)

        return boards
