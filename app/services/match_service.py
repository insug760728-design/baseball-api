import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import Match, MatchDetail, MatchEvent, PlayerMatchStat
from app.scrapers.baseball_scraper import BaseballScraper
from app.scrapers.soccer_scraper import SoccerScraper, SOCCER_LEAGUE_CODES
from app.scrapers.basketball_scraper import BasketballScraper
from app.core.sports_catalog import SPORTS_CATALOG
from app.services.team_split_service import TeamSplitService

class MatchService:

    @classmethod
    def sync_from_official_site(cls, db: Session, league_id: str = "MLB", league_name: Optional[str] = None, target_date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
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
                    match = Match(
                        official_id=m_data["official_id"],
                        sport_code=m_data.get("sport_code", scraper.get_sport_code()),
                        league_name=m_data["league_name"],
                        season=m_data.get("season", "2026"),
                        round_name=m_data.get("round_name"),
                        match_date=m_data["match_date"],
                        stadium=m_data.get("stadium"),
                        home_team_name=m_data["home_team_name"],
                        away_team_name=m_data["away_team_name"],
                        home_score=m_data["home_score"],
                        away_score=m_data["away_score"],
                        status=m_data["status"]
                    )
                    db.add(match)
                    db.commit()
                    db.refresh(match)
                else:
                    if not match.is_customized:
                        match.home_team_name = m_data["home_team_name"]
                        match.away_team_name = m_data["away_team_name"]
                        match.stadium = m_data.get("stadium")
                        match.home_score = m_data["home_score"]
                        match.away_score = m_data["away_score"]
                        match.status = m_data["status"]
                        match.match_date = m_data["match_date"]
                        db.commit()

                if match.status in ["FINISHED", "LIVE"]:
                    if not match.details or not match.player_stats or match.status == "LIVE":
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
            existing_event = db.query(MatchEvent).filter(
                MatchEvent.match_id == match.id,
                MatchEvent.time_display == ev["time_display"],
                MatchEvent.player_name == ev["player_name"]
            ).first()
            if not existing_event:
                new_event = MatchEvent(
                    match_id=match.id,
                    time_display=ev["time_display"],
                    event_type=ev["event_type"],
                    team_name=ev["team_name"],
                    player_name=ev["player_name"],
                    assist_player_name=ev.get("assist_player_name"),
                    score_after=ev.get("score_after"),
                    description=ev.get("description")
                )
                db.add(new_event)

        for p_stat in detail_data.get("player_stats", []):
            extra_str = json.dumps(p_stat.get("extra_stats", {}), ensure_ascii=False)
            new_stat = PlayerMatchStat(
                match_id=match.id,
                team_name=p_stat["team_name"],
                player_name=p_stat["player_name"],
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

    @staticmethod
    def get_matches(db: Session, sport_code: Optional[str] = None, league_name: Optional[str] = None, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: Optional[int] = None, order: Optional[str] = "asc"):
        query = db.query(Match)

        # 리그명에 따라 sport_code 자동 감지
        if league_name:
            ln_upper = league_name.upper()
            if any(s in ln_upper for s in ["EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1", "프리미어", "라리가", "분데스", "세리에", "리그 1"]):
                sport_code = "SOCCER"
            elif any(b in ln_upper for b in ["NBA", "KBL", "농구"]):
                sport_code = "BASKETBALL"
            elif any(bb in ln_upper for bb in ["MLB", "KBO", "NPB", "메이저리그", "프로야구"]):
                sport_code = "BASEBALL"

        if sport_code and sport_code.upper() not in ["ALL", "NONE", ""]:
            query = query.filter(Match.sport_code == sport_code.upper())
        if league_name:
            query = query.filter(Match.league_name.contains(league_name))
        if status:
            query = query.filter(Match.status == status)
        if start_date:
            query = query.filter(Match.match_date >= f"{start_date} 00:00")
        if end_date:
            query = query.filter(Match.match_date <= f"{end_date} 23:59")
        
        if order and order.lower() == "desc":
            q = query.order_by(Match.match_date.desc(), Match.id.desc())
        else:
            q = query.order_by(Match.match_date.asc(), Match.id.asc())

        matches = q.limit(limit).all() if limit else q.all()
        for m in matches:
            try:
                m.prediction = TeamSplitService.get_quick_prediction(
                    m.home_team_name, m.away_team_name, m.sport_code, m.status, m.home_score, m.away_score
                )
            except Exception:
                m.prediction = None
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
            player_stats_list.append({
                "id": ps.id,
                "match_id": ps.match_id,
                "team_name": ps.team_name,
                "player_name": ps.player_name,
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
            events_list.append({
                "id": ev.id,
                "match_id": ev.match_id,
                "time_display": ev.time_display,
                "event_type": ev.event_type,
                "team_name": ev.team_name,
                "player_name": ev.player_name,
                "assist_player_name": ev.assist_player_name,
                "score_after": ev.score_after,
                "description": ev.description,
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
    def update_match_score(db: Session, match_id: int, home_score: Optional[int], away_score: Optional[int], status: Optional[str] = None, notes: Optional[str] = None):
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

        match.is_customized = True
        match.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def update_player_stat(db: Session, stat_id: int, points: Optional[int] = None, shots: Optional[int] = None, extra_stats: Optional[Dict[str, Any]] = None, override_reason: Optional[str] = None):
        stat = db.query(PlayerMatchStat).filter(PlayerMatchStat.id == stat_id).first()
        if not stat:
            return None

        if not stat.is_override and not stat.original_backup:
            original_data = {
                "points": stat.points,
                "shots": stat.shots,
                "extra_stats": stat.extra_stats
            }
            stat.original_backup = json.dumps(original_data, ensure_ascii=False)

        if points is not None:
            stat.points = points
        if shots is not None:
            stat.shots = shots
        if extra_stats is not None:
            curr_extra = json.loads(stat.extra_stats or "{}")
            curr_extra.update(extra_stats)
            stat.extra_stats = json.dumps(curr_extra, ensure_ascii=False)

        stat.is_override = True
        stat.override_reason = override_reason or "사용자 앱 전송용 야구 수치 수동 조정"

        db.commit()
        db.refresh(stat)
        return stat
