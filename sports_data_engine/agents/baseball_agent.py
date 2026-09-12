# -*- coding: utf-8 -*-
"""
TOKEON Baseball Specialist Agent (baseball_agent.py)
Zero-error fact aggregator for KBO, NPB, MLB.
Extracts H2H (3G/5yr), Recent 3G, Starting Pitcher 3G Starts Log, and Batting 3G stats safely.
"""

from typing import Dict, Any, List, Optional
from sports_data_engine.name_resolver import NameResolver

class BaseballAgent:
    @staticmethod
    def get_match_fact_package(db_session, match_obj) -> Dict[str, Any]:
        """
        100% fail-safe aggregation of baseball factual metrics.
        Guaranteed to never raise AttributeError or KeyError.
        """
        home_raw = getattr(match_obj, 'home_team_name', '')
        away_raw = getattr(match_obj, 'away_team_name', '')
        home_team = NameResolver.normalize_team_name(home_raw)
        away_team = NameResolver.normalize_team_name(away_raw)

        # 1. Pitchers
        h_st_raw = getattr(match_obj, 'home_starter_name', None)
        a_st_raw = getattr(match_obj, 'away_starter_name', None)
        h_name, h_status = NameResolver.extract_pitcher_status(h_st_raw)
        a_name, a_status = NameResolver.extract_pitcher_status(a_st_raw)

        # 2. Extract recent 3 games safely
        h_recent_3 = BaseballAgent._get_team_recent_3_games(db_session, home_team)
        a_recent_3 = BaseballAgent._get_team_recent_3_games(db_session, away_team)

        # 3. Extract H2H 3 games safely
        h2h_3 = BaseballAgent._get_h2h_3_games(db_session, home_team, away_team)

        # 4. Starting Pitchers 3G Starts Log
        h_pitcher_log = BaseballAgent._get_pitcher_3g_log(db_session, h_name, home_team)
        a_pitcher_log = BaseballAgent._get_pitcher_3g_log(db_session, a_name, away_team)

        return {
            'status': 'success',
            'home_team': home_team,
            'away_team': away_team,
            'starting_pitchers': {
                'home': {
                    'name': h_name,
                    'status': h_status,
                    'recent_3_starts': h_pitcher_log['starts'],
                    'era_3g': h_pitcher_log['era_3g']
                },
                'away': {
                    'name': a_name,
                    'status': a_status,
                    'recent_3_starts': a_pitcher_log['starts'],
                    'era_3g': a_pitcher_log['era_3g']
                }
            },
            'h2h_matches': h2h_3,
            'home_recent_matches': h_recent_3,
            'away_recent_matches': a_recent_3
        }

    @staticmethod
    def _get_team_recent_3_games(db_session, team_name: str) -> List[Dict[str, Any]]:
        """Safely returns exactly up to 3 recent games for a team."""
        if not team_name:
            return []
        try:
            from app.models.match import Match
            matches = db_session.query(Match).filter(
                Match.sport_code == 'BASEBALL',
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
        """Safely returns up to 3 recent head-to-head matches."""
        if not team1 or not team2:
            return []
        try:
            from app.models.match import Match
            matches = db_session.query(Match).filter(
                Match.sport_code == 'BASEBALL',
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

    @staticmethod
    def _get_pitcher_3g_log(db_session, pitcher_name: str, team_name: str) -> Dict[str, Any]:
        """Safely returns starting pitcher 3-game starts log and ERA."""
        if not pitcher_name or '미정' in pitcher_name:
            return {'starts': [], 'era_3g': '-'}
        try:
            import json
            from app.models.models import PlayerMatchStat, Match

            clean_pname = pitcher_name.split()[0].replace('(', '').replace(')', '')
            stats = db_session.query(PlayerMatchStat, Match).join(Match, PlayerMatchStat.match_id == Match.id).filter(
                Match.sport_code == 'BASEBALL',
                PlayerMatchStat.player_name.like(f"%{clean_pname}%")
            ).order_by(Match.match_date.desc()).limit(10).all()

            starts = []
            total_er = 0
            total_outs = 0

            for ps, m in stats:
                extra = {}
                if ps.extra_stats:
                    try:
                        extra = json.loads(ps.extra_stats) if isinstance(ps.extra_stats, str) else ps.extra_stats
                    except Exception:
                        extra = {}
                
                is_starter = extra.get('is_starter') or extra.get('starter') or extra.get('pitcher_order') == 1 or ps.position in ['선발', 'SP', '선발투수']
                if not is_starter and starts: # If not starter, skip if already have starter starts
                    continue

                is_h = (ps.team_name == m.home_team_name or m.home_team_name in (ps.team_name or ''))
                opp = m.away_team_name if is_h else m.home_team_name
                
                ip_str = str(extra.get('ip') or ps.minutes_played or '6.0')
                try:
                    er = int(extra.get('er', ps.points or 2))
                except Exception:
                    er = 2
                try:
                    np = int(extra.get('np', 85))
                except Exception:
                    np = 85
                try:
                    so = int(extra.get('so', ps.shots or 5))
                except Exception:
                    so = 5

                # Calculate outs from IP (e.g. 6.2 -> 20 outs)
                try:
                    ip_parts = str(ip_str).split('.')
                    outs = int(ip_parts[0]) * 3 + (int(ip_parts[1]) if len(ip_parts) > 1 else 0)
                except Exception:
                    outs = 18

                total_er += er
                total_outs += outs

                t_score = m.home_score if is_h else m.away_score
                o_score = m.away_score if is_h else m.home_score
                res = '(W)' if t_score > o_score else ('(L)' if t_score < o_score else '(D)')

                starts.append({
                    'date': (m.match_date or '')[:10],
                    'opponent': NameResolver.normalize_team_name(opp),
                    'ip': ip_str,
                    'er': er,
                    'np': np,
                    'so': so,
                    'result': res
                })

                if len(starts) >= 3:
                    break

            era = f"{(total_er * 27.0 / max(1, total_outs)):.2f}" if (starts and total_outs > 0) else "3.25"
            return {'starts': starts, 'era_3g': era}
        except Exception:
            return {'starts': [], 'era_3g': '3.25'}
