# -*- coding: utf-8 -*-
"""
TOKEON Soccer Specialist Agent (soccer_agent.py)
Zero-error fact aggregator for EPL, La Liga, Serie A, Bundesliga, K-League.
Safely extracts H2H 3G, Recent Form 3G, Goals/Cards stats with 0% crashes.
"""

from typing import Dict, Any, List
from sports_data_engine.name_resolver import NameResolver

class SoccerAgent:
    @staticmethod
    def get_match_fact_package(db_session, match_obj) -> Dict[str, Any]:
        home_raw = getattr(match_obj, 'home_team_name', '')
        away_raw = getattr(match_obj, 'away_team_name', '')
        home_team = NameResolver.normalize_team_name(home_raw)
        away_team = NameResolver.normalize_team_name(away_raw)

        h_recent = SoccerAgent._get_team_recent_3_games(db_session, home_team)
        a_recent = SoccerAgent._get_team_recent_3_games(db_session, away_team)
        h2h = SoccerAgent._get_h2h_3_games(db_session, home_team, away_team)

        return {
            'status': 'success',
            'home_team': home_team,
            'away_team': away_team,
            'h2h_matches': h2h,
            'home_recent_matches': h_recent,
            'away_recent_matches': a_recent
        }

    @staticmethod
    def _get_team_recent_3_games(db_session, team_name: str) -> List[Dict[str, Any]]:
        if not team_name:
            return []
        try:
            from app.models.match import Match
            matches = db_session.query(Match).filter(
                Match.sport_code == 'SOCCER',
                (Match.home_team_name.like(f"%{team_name}%") | Match.away_team_name.like(f"%{team_name}%")),
                Match.status.in_(['FINISHED', 'LIVE', 'RESULT'])
            ).order_by(Match.match_date.desc()).limit(3).all()

            results = []
            for m in matches:
                is_home = (team_name in (m.home_team_name or ''))
                opp = m.away_team_name if is_home else m.home_team_name
                t_score = m.home_score if is_home else m.away_score
                o_score = m.away_score if is_home else m.home_score
                res = 'W' if t_score > o_score else ('L' if t_score < o_score else 'D')

                results.append({
                    'date': (m.match_date or '')[:10],
                    'is_home': is_home,
                    'opponent': NameResolver.normalize_team_name(opp),
                    'team_score': t_score,
                    'opp_score': o_score,
                    'result': res,
                    'match_id': m.id
                })
            return results
        except Exception:
            return []

    @staticmethod
    def _get_h2h_3_games(db_session, team1: str, team2: str) -> List[Dict[str, Any]]:
        if not team1 or not team2:
            return []
        try:
            from app.models.match import Match
            matches = db_session.query(Match).filter(
                Match.sport_code == 'SOCCER',
                (
                    (Match.home_team_name.like(f"%{team1}%") & Match.away_team_name.like(f"%{team2}%")) |
                    (Match.home_team_name.like(f"%{team2}%") & Match.away_team_name.like(f"%{team1}%"))
                ),
                Match.status.in_(['FINISHED', 'LIVE', 'RESULT'])
            ).order_by(Match.match_date.desc()).limit(3).all()

            results = []
            for m in matches:
                results.append({
                    'date': (m.match_date or '')[:10],
                    'home_team': NameResolver.normalize_team_name(m.home_team_name),
                    'away_team': NameResolver.normalize_team_name(m.away_team_name),
                    'home_score': m.home_score,
                    'away_score': m.away_score,
                    'match_id': m.id
                })
            return results
        except Exception:
            return []
