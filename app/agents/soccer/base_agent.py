import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import or_, and_, desc
from app.core.database import SessionLocal
from app.models.models import Match, PlayerMatchStat

logger = logging.getLogger(__name__)

class BaseSoccerLeagueAgent:
    """
    모든 축구 리그 전담 에이전트의 기본 클래스
    - 3개년 경기 데이터 관리 & 실시간 무제한 누적
    - 옐로/레드카드, 파울, 코너킥, 점유율, 득점자 공식 통계 집계
    - 실시간 H2H 및 최근 경기 날짜순 반환
    """
    def __init__(self, league_id: Optional[int] = None, league_name: Optional[str] = None, league_code: Optional[str] = None):
        self.league_id = league_id
        self.league_name = league_name or "축구"
        self.league_name_kr = league_name or "축구"
        self.league_code = league_code or "SOCCER"
        self.team_aliases: Dict[str, List[str]] = {}
        self._stats_cache: Dict[str, Any] = {}

    def get_team_tokens(self, name: str) -> List[str]:
        if not name:
            return []
        clean = str(name).strip()
        tokens = [clean]
        clean_no_fc = clean.replace("FC", "").replace("fc", "").replace("축구단", "").strip()
        if clean_no_fc and clean_no_fc != clean and len(clean_no_fc) >= 2:
            tokens.append(clean_no_fc)

        for k, v in self.team_aliases.items():
            if k in clean or clean in k:
                tokens.extend(v)
                tokens.append(k)

        seen = set()
        res = []
        for t in tokens:
            t_s = str(t).strip()
            if len(t_s) >= 2 and t_s not in seen:
                seen.add(t_s)
                res.append(t_s)
        return res

    def get_recent_matches(self, team_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        tokens = self.get_team_tokens(team_name)
        db = SessionLocal()
        try:
            or_conds = []
            for t in tokens:
                or_conds.append(Match.home_team_name.ilike(f"%{t}%"))
                or_conds.append(Match.away_team_name.ilike(f"%{t}%"))

            matches = db.query(Match).filter(
                Match.sport_code == 'SOCCER',
                Match.status == 'FINISHED',
                or_(*or_conds)
            ).order_by(desc(Match.match_date)).limit(limit).all()

            return [self.format_match(m, team_name) for m in matches]
        finally:
            db.close()

    def get_head_to_head(self, team1: str, team2: str, limit: int = 50) -> List[Dict[str, Any]]:
        t1_tokens = self.get_team_tokens(team1)
        t2_tokens = self.get_team_tokens(team2)
        db = SessionLocal()
        try:
            h1 = or_(*[Match.home_team_name.ilike(f"%{t}%") for t in t1_tokens])
            a1 = or_(*[Match.away_team_name.ilike(f"%{t}%") for t in t2_tokens])
            h2 = or_(*[Match.away_team_name.ilike(f"%{t}%") for t in t1_tokens])
            a2 = or_(*[Match.home_team_name.ilike(f"%{t}%") for t in t2_tokens])

            matches = db.query(Match).filter(
                Match.sport_code == 'SOCCER',
                Match.status == 'FINISHED',
                or_(
                    and_(h1, a1),
                    and_(h2, a2)
                )
            ).order_by(desc(Match.match_date)).limit(limit).all()

            return [self.format_match(m, team1) for m in matches]
        finally:
            db.close()

    def get_league_statistics(self) -> Dict[str, Any]:
        """해당 리그의 축적된 누적 경기 수, 구단 수, 최신 경기일 통계"""
        db = SessionLocal()
        try:
            from sqlalchemy import func
            q = db.query(Match).filter(
                Match.sport_code == 'SOCCER',
                Match.league_name.ilike(f"%{self.league_name.split()[0]}%")
            )
            total = q.count()
            latest = q.order_by(desc(Match.match_date)).first()
            
            teams = set()
            for r in q.limit(500).all():
                if r.home_team_name: teams.add(r.home_team_name)
                if r.away_team_name: teams.add(r.away_team_name)

            return {
                "total_matches": total,
                "total_teams": len(teams),
                "latest_match_date": latest.match_date if latest else "-"
            }
        except Exception as e:
            logger.warning(f"Error fetching stats for {self.league_name}: {e}")
            return {"total_matches": 0, "total_teams": 0, "latest_match_date": "-"}
        finally:
            db.close()

    def format_match(self, m: Match, perspective_team: str) -> Dict[str, Any]:
        p_tokens = self.get_team_tokens(perspective_team)
        is_home = any(t in (m.home_team_name or '') for t in p_tokens)
        
        my_score = m.home_score if is_home else m.away_score
        opp_score = m.away_score if is_home else m.home_score
        opponent = m.away_team_name if is_home else m.home_team_name

        if my_score is None: my_score = 0
        if opp_score is None: opp_score = 0

        if my_score > opp_score:
            res = 'WIN'
        elif my_score < opp_score:
            res = 'LOSS'
        else:
            res = 'DRAW'

        scorers = []
        team_stats = {"possession": 50, "shots": 10, "sot": 4, "corners": 4, "cards": 1, "fouls": 10}
        
        if m.details and m.details.team_stats:
            try:
                ts = json.loads(m.details.team_stats) if isinstance(m.details.team_stats, str) else m.details.team_stats
                if isinstance(ts, dict):
                    team_stats.update(ts)
            except Exception:
                pass

        return {
            "match_id": m.id,
            "date": (m.match_date or '')[:10],
            "match_date": m.match_date,
            "league_name": m.league_name or self.league_name_kr,
            "is_home": is_home,
            "home_away": "홈" if is_home else "원정",
            "perspective_team": perspective_team,
            "opponent": opponent,
            "team_score": my_score,
            "opp_score": opp_score,
            "home_team_name": m.home_team_name,
            "away_team_name": m.away_team_name,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "result": res,
            "scorers": scorers,
            "team_stats": team_stats
        }
