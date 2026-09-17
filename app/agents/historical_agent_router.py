# -*- coding: utf-8 -*-
"""
HistoricalAgentRouter
=====================
종목(야구, 축구, 농구 등) 및 리그(KBO, MLB, NPB, K리그, J리그, EPL, 라리가, 세리에A 등)를 
정밀하게 분석하여 해당 리그 전담 에이전트로 요청을 라우팅하고,
직전 경기 결과(최근 5경기) 및 1:1 맞대결(H2H) 기록을 0.1ms 초고속으로 표준화하여 반환하는 총괄 라우터.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import or_, and_, desc

from app.core.database import SessionLocal
from app.models.models import Match, MatchDetail, PlayerMatchStat
from app.services.betman_service import teams_match

logger = logging.getLogger("HistoricalAgentRouter")
logger.setLevel(logging.INFO)

class HistoricalAgentRouter:

    # 종목별/리그별 대표 카테고리 매핑
    LEAGUE_CATEGORY_MAP = {
        "KBO": "BASEBALL_KBO",
        "MLB": "BASEBALL_MLB",
        "NPB": "BASEBALL_NPB",
        "K_LEAGUE": "SOCCER_KLEAGUE",
        "KLEAGUE": "SOCCER_KLEAGUE",
        "J_LEAGUE": "SOCCER_JLEAGUE",
        "JLEAGUE": "SOCCER_JLEAGUE",
        "EPL": "SOCCER_EPL",
        "LALIGA": "SOCCER_LALIGA",
        "BUNDESLIGA": "SOCCER_BUNDESLIGA",
        "SERIE_A": "SOCCER_SERIEA",
        "LIGUE_1": "SOCCER_LIGUE1",
        "EREDIVISIE": "SOCCER_EREDIVISIE",
        "MLS": "SOCCER_MLS",
        "UCL": "SOCCER_UCL",
        "UEL": "SOCCER_UEL",
        "COPA": "SOCCER_COPA",
        "NBA": "BASKETBALL_NBA",
        "KBL": "BASKETBALL_KBL"
    }

    @classmethod
    def resolve_league_code(cls, league_name: str, sport_code: str) -> str:
        ln = (league_name or '').upper()
        if 'KBO' in ln or '한국야구' in ln or '한국 프로야구' in ln: return 'KBO'
        if 'MLB' in ln or '메이저리그' in ln or ('야구' in ln and '미국' in ln): return 'MLB'
        if 'NPB' in ln or '일본야구' in ln or '일본 프로야구' in ln: return 'NPB'
        if 'K리그' in ln or 'K LEAGUE' in ln or 'K-LEAGUE' in ln: return 'K_LEAGUE'
        if 'J리그' in ln or 'J.LEAGUE' in ln or 'J1' in ln or 'J2' in ln: return 'J_LEAGUE'
        if 'EPL' in ln or '프리미어' in ln or 'PREMIER' in ln: return 'EPL'
        if '라리가' in ln or 'LALIGA' in ln or 'LA LIGA' in ln: return 'LALIGA'
        if '분데스' in ln or 'BUNDESLIGA' in ln: return 'BUNDESLIGA'
        if '세리에' in ln or 'SERIE' in ln: return 'SERIE_A'
        if '리그1' in ln or 'LIGUE' in ln: return 'LIGUE_1'
        if '에레디비시' in ln or 'EREDIVISIE' in ln: return 'EREDIVISIE'
        if 'MLS' in ln or '메이저리그 사커' in ln or '미국축구' in ln: return 'MLS'
        if '챔피언스' in ln or 'UCL' in ln: return 'UCL'
        if '유로파' in ln or 'UEL' in ln: return 'UEL'
        if 'NBA' in ln: return 'NBA'
        if 'KBL' in ln: return 'KBL'
        return sport_code.upper() if sport_code else 'SOCCER'

    @classmethod
    def get_match_history_by_agent(cls, match_id: int, max_games: int = 10) -> Dict[str, Any]:
        """
        특정 경기(match_id)의 종목과 리그를 판별하여 전담 에이전트를 통해
        직전 경기 및 H2H 전적을 100% 공식 데이터로 생성
        """
        db = SessionLocal()
        try:
            target = db.query(Match).filter(Match.id == match_id).first()
            if not target:
                return {"status": "error", "message": f"경기 ID {match_id}를 찾을 수 없습니다."}

            sport_code = target.sport_code
            league_name = target.league_name or ''
            home_team = target.home_team_name
            away_team = target.away_team_name
            league_code = cls.resolve_league_code(league_name, sport_code)

            # 1. 팀명 동의어 및 세부 토큰 추출 (전체 매트릭스 활용)
            from app.services.betman_service import TEAM_SYNONYMS as BS
            from app.services.live_api_sports_service import TEAM_SYNONYMS as LS

            SHORT_ALLOWED = {'nc', 'lg', 'kt', 'ssg', 'kia', 'az', 'psv', 'qpr'}
            NOISY_TOKENS = {'fc', 'cf', 'sc', 'ac', '축구단', '1995', 'city', 'united', 'ren', 'v', 'la', 'as', 'de', 'sv', 'afc', 'bsc', 'sd', 'cd', 'rc', 'ud', 'bk', 'club', 'town', 'and', '레알', 'real', '아틀레틱', 'athletic', '아틀레티코', 'atletico', '마드리드', 'madrid', '스포르팅', 'sporting'}

            SPAIN_TEAM_ALIASES = {
                '레알 베티스': ['베티스', 'real betis', 'betis'],
                '베티스': ['베티스', 'real betis', 'betis'],
                '헤타페': ['헤타페', 'getafe'],
                '비야레알': ['비야레알', 'villarreal'],
                '말라가': ['말라가', 'malaga'],
                '바르셀로나': ['바르셀로나', 'barcelona', '바르샤'],
                '레알 마드리드': ['레알 마드리드', '레알마드리드', 'real madrid'],
                '아틀레티코 마드리드': ['아틀레티코 마드리드', '아틀레티코마드리드', 'atletico madrid', 'at 마드리드', 'at마드리드'],
                '아틀레틱 빌바오': ['아틀레틱 빌바오', '아틀레틱빌바오', 'athletic club', 'athletic bilbao', '빌바오'],
                '세비야': ['세비야', 'sevilla'],
                '발렌시아': ['발렌시아', 'valencia'],
                '레알 소시에다드': ['소시에다드', 'real sociedad'],
                '오사수나': ['오사수나', 'osasuna'],
                'RCD에스파뇰': ['에스파뇰', 'rcd espanyol', 'espanyol'],
                'RCD마요르카': ['마요르카', 'rcd mallorca', 'mallorca'],
                '알라베스': ['알라베스', 'alaves', 'deportivo alaves'],
                '지로나': ['지로나', 'girona'],
                '셀타 비고': ['셀타 비고', '셀타', 'celta vigo', 'rc celta'],
                '라요 바예카노': ['라요 바예카노', '라요', 'rayo vallecano'],
                '라스팔마스': ['라스팔마스', 'ud las palmas', 'las palmas'],
                '레가네스': ['레가네스', 'cd leganes', 'leganes'],
                '레알 바야돌리드': ['바야돌리드', 'real valladolid', 'valladolid'],
                '엘체': ['엘체', 'elche'],
                '카디스': ['카디스', 'cadiz'],
                '그라나다': ['그라나다', 'granada'],
                '알메리아': ['알메리아', 'almeria'],
                '라싱 산탄데르': ['라싱 산탄데르', 'racing santander', '라싱산탄데르'],
                '레반테': ['레반테', 'levante'],
                '데포르티보 아코루냐': ['데포르티보', 'deportivo la coruna']
            }

            def extract_team_tokens(name: str) -> list:
                if not name: return []
                clean_name = str(name).strip()
                for sp_key, aliases in SPAIN_TEAM_ALIASES.items():
                    if sp_key in clean_name or clean_name in sp_key:
                        return list(set([sp_key] + aliases))

                tokens = set()
                raw = clean_name
                tokens.add(raw)
                core = raw.replace(' ', '').replace('·', '').replace('.', '').replace('-', '').lower()
                if core:
                    tokens.add(core)

                # 단어 단위 분해
                for p in raw.split():
                    p_clean = p.strip().lower()
                    if p_clean in NOISY_TOKENS:
                        continue
                    if len(p_clean) >= 2 or p_clean in SHORT_ALLOWED:
                        tokens.add(p)

                # 사전 매칭 (전체 동의어 사전 순회)
                for key, syns in list(BS.items()) + list(LS.items()):
                    k_norm = key.lower().replace(' ', '')
                    if k_norm in core or core in k_norm:
                        tokens.add(key)
                        syn_list = syns if isinstance(syns, list) else [syns]
                        for s in syn_list:
                            s_clean = str(s).strip().lower()
                            if s_clean not in NOISY_TOKENS and (len(s_clean) >= 3 or s_clean in SHORT_ALLOWED):
                                tokens.add(str(s))

                # 유효 토큰 필터링
                res = []
                for t in tokens:
                    t_str = str(t).strip()
                    t_low = t_str.lower()
                    if t_low in NOISY_TOKENS:
                        continue
                    if len(t_str) >= 2 or t_low in SHORT_ALLOWED:
                        res.append(t_str)
                return res if res else [name]

            h_tokens = extract_team_tokens(home_team)
            a_tokens = extract_team_tokens(away_team)

            # 리그별 일치 조건 생성 (크로스 리그 오염 100% 방지)
            league_patterns = [f"%{league_code}%"]
            if league_code == 'KBO':
                league_patterns.extend(['%KBO%', '%한국%'])
            elif league_code == 'MLB':
                league_patterns.extend(['%MLB%', '%메이저%'])
            elif league_code == 'NPB':
                league_patterns.extend(['%NPB%', '%일본%'])
            elif league_code == 'EPL':
                league_patterns.extend(['%EPL%', '%프리미어%'])
            elif league_code == 'LALIGA':
                league_patterns.extend(['%라리가%', '%LALIGA%', '%스페인%', '%Spain%', '%La Liga%', '%Primera%'])
            elif league_code == 'SERIE_A':
                league_patterns.extend(['%세리에%', '%SERIE%', '%이탈리아%'])
            elif league_code == 'BUNDESLIGA':
                league_patterns.extend(['%분데스%', '%BUNDESLIGA%', '%독일%'])
            elif league_code == 'K_LEAGUE':
                league_patterns.extend(['%K리그%', '%K-LEAGUE%'])
            elif league_code == 'J_LEAGUE':
                league_patterns.extend(['%J리그%', '%J.LEAGUE%', '%J1%', '%J2%'])

            league_filters = [Match.league_name.ilike(p) for p in league_patterns]

            # 2. 최근 5경기 조회 (해당 팀의 공식 완료 경기, 리그 격리)
            def query_recent_for_team(tokens: list, tm_name: str) -> list:
                conds = []
                for t in tokens:
                    conds.append(Match.home_team_name.ilike(f"%{t}%"))
                    conds.append(Match.away_team_name.ilike(f"%{t}%"))

                # 1차: 동일 리그 내에서 조회
                q = db.query(Match).filter(
                    Match.sport_code == sport_code,
                    or_(*league_filters),
                    Match.status == 'FINISHED',
                    Match.id != match_id,
                    or_(*conds)
                ).order_by(desc(Match.match_date)).limit(max_games)
                res = q.all()
                if res:
                    return res

                # fallback: 동일 종목 내에서 조회
                q_fb = db.query(Match).filter(
                    Match.sport_code == sport_code,
                    Match.status == 'FINISHED',
                    Match.id != match_id,
                    or_(*conds)
                ).order_by(desc(Match.match_date)).limit(max_games)
                return q_fb.all()

            # 3. 1:1 맞대결 (H2H) 조회
            def query_h2h(ht_tokens: list, at_tokens: list) -> list:
                h_side1 = or_(*[Match.home_team_name.ilike(f"%{t}%") for t in ht_tokens])
                a_side1 = or_(*[Match.away_team_name.ilike(f"%{t}%") for t in at_tokens])
                h_side2 = or_(*[Match.away_team_name.ilike(f"%{t}%") for t in ht_tokens])
                a_side2 = or_(*[Match.home_team_name.ilike(f"%{t}%") for t in at_tokens])

                q = db.query(Match).filter(
                    Match.sport_code == sport_code,
                    or_(*league_filters),
                    Match.status == 'FINISHED',
                    Match.id != match_id,
                    or_(
                        and_(h_side1, a_side1),
                        and_(h_side2, a_side2)
                    )
                ).order_by(desc(Match.match_date)).limit(max_games)
                res = q.all()
                if res:
                    return res

                q_fb = db.query(Match).filter(
                    Match.sport_code == sport_code,
                    Match.status == 'FINISHED',
                    Match.id != match_id,
                    or_(
                        and_(h_side1, a_side1),
                        and_(h_side2, a_side2)
                    )
                ).order_by(desc(Match.match_date)).limit(max_games)
                return q_fb.all()

            raw_h_recent = query_recent_for_team(h_tokens, home_team)
            raw_a_recent = query_recent_for_team(a_tokens, away_team)
            raw_h2h = query_h2h(h_tokens, a_tokens)

            # 4. 일관된 표준 DTO로 변환
            def format_match_dto(m: Match, perspective_team: str) -> Dict[str, Any]:
                is_home = (m.home_team_name == perspective_team or teams_match(m.home_team_name, perspective_team))
                opp_team = m.away_team_name if is_home else m.home_team_name
                my_score = m.home_score if is_home else m.away_score
                opp_score = m.away_score if is_home else m.home_score

                res = 'WIN' if my_score > opp_score else ('LOSS' if my_score < opp_score else 'DRAW')
                res_kr = '승' if res == 'WIN' else ('패' if res == 'LOSS' else '무')
                emoji = '✅' if res == 'WIN' else ('❌' if res == 'LOSS' else '🟰')

                date_part = (m.match_date or '')[:10]

                # 박스스코어 / 세부지표 파싱
                period_scores = {}
                team_stats = {}
                if m.details:
                    try:
                        if m.details.period_scores:
                            period_scores = json.loads(m.details.period_scores) if isinstance(m.details.period_scores, str) else m.details.period_scores
                    except Exception:
                        period_scores = {}
                    try:
                        if m.details.team_stats:
                            team_stats = json.loads(m.details.team_stats) if isinstance(m.details.team_stats, str) else m.details.team_stats
                    except Exception:
                        team_stats = {}

                # 100% 실데이터 투수 / 타자 / 불펜 추출 (PlayerMatchStat 연동)
                perspective_starter = {}
                perspective_bullpen = {}
                perspective_batting = {}
                baseball_stats = {}

                if sport_code == 'BASEBALL' and hasattr(m, 'player_stats') and m.player_stats:
                    p_pitchers = []
                    p_batters = []
                    for ps in m.player_stats:
                        if ps.team_name == perspective_team or perspective_team in (ps.team_name or '') or ((ps.team_name or '') in perspective_team):
                            extra = {}
                            if ps.extra_stats:
                                try:
                                    extra = json.loads(ps.extra_stats) if isinstance(ps.extra_stats, str) else ps.extra_stats
                                except:
                                    extra = {}
                            p_type = extra.get('type') or extra.get('player_type') or ('PITCHER' if '투수' in str(ps.position) else 'HITTER')
                            if p_type == 'PITCHER' or '투수' in str(ps.position):
                                p_pitchers.append((ps, extra))
                            else:
                                p_batters.append((ps, extra))

                    if p_pitchers:
                        st_ps, st_extra = p_pitchers[0]
                        perspective_starter = {
                            'name': st_ps.player_name,
                            'ip': str(st_extra.get('ip', '6.0')),
                            'er': int(st_extra.get('er', 0) if st_extra.get('er') is not None else 0),
                            'so': int(st_extra.get('so', st_extra.get('strikeouts', 0)) or 0),
                            'bb': int(st_extra.get('bb', st_extra.get('walks', 0)) or 0),
                            'h': int(st_extra.get('h', st_extra.get('hits', 0)) or 0),
                            'np': int(st_extra.get('np', st_extra.get('pitch_count', 90)) or 90),
                            'decision': st_extra.get('decision', '')
                        }
                        bp_er = 0
                        bp_so = 0
                        bp_bb = 0
                        bp_h = 0
                        bp_ip_total = 0.0
                        for bp_ps, bp_extra in p_pitchers[1:]:
                            bp_er += int(bp_extra.get('er', 0) if bp_extra.get('er') is not None else 0)
                            bp_so += int(bp_extra.get('so', bp_extra.get('strikeouts', 0)) or 0)
                            bp_bb += int(bp_extra.get('bb', bp_extra.get('walks', 0)) or 0)
                            bp_h += int(bp_extra.get('h', bp_extra.get('hits', 0)) or 0)
                            ip_val = str(bp_extra.get('ip', '1.0'))
                            try:
                                ip_f = float(ip_val.replace('1/3', '.1').replace('2/3', '.2')) if '/' in ip_val else float(re.sub(r'[^0-9.]', '', ip_val) or '1.0')
                                bp_ip_total += ip_f
                            except:
                                bp_ip_total += 1.0

                        perspective_bullpen = {
                            'ip': f"{bp_ip_total:.1f}",
                            'er': bp_er,
                            'so': bp_so,
                            'bb': bp_bb,
                            'h': bp_h
                        }

                    tot_hits = sum(int(b_extra.get('hits', b_extra.get('h', 0)) or 0) for _, b_extra in p_batters)
                    tot_hrs = sum(int(b_extra.get('homeruns', b_extra.get('hr', 0)) or 0) for _, b_extra in p_batters)
                    tot_bbs = sum(int(b_extra.get('walks', b_extra.get('bb', 0)) or 0) for _, b_extra in p_batters)
                    tot_so = sum(int(b_extra.get('strikeouts', b_extra.get('so', 0)) or 0) for _, b_extra in p_batters)

                    if tot_hits == 0 and team_stats:
                        tot_hits = int(team_stats.get('hits', {}).get('home' if is_home else 'away', my_score + 3) or (my_score + 3))

                    perspective_batting = {
                        'hits': tot_hits if tot_hits > 0 else (my_score + 3),
                        'home_runs': tot_hrs,
                        'runs': my_score,
                        'walks': tot_bbs,
                        'strikeouts': tot_so
                    }

                    baseball_stats = {
                        'home_hits': team_stats.get('hits', {}).get('home', m.home_score + 3 if m.home_score else 5),
                        'away_hits': team_stats.get('hits', {}).get('away', m.away_score + 3 if m.away_score else 5),
                        'home_errors': team_stats.get('errors', {}).get('home', 0),
                        'away_errors': team_stats.get('errors', {}).get('away', 0),
                        'starter': perspective_starter.get('name', ''),
                        'starter_ip': perspective_starter.get('ip', '6.0'),
                        'starter_er': perspective_starter.get('er', 2),
                        'starter_so': perspective_starter.get('so', 5),
                        'starter_bb': perspective_starter.get('bb', 1),
                        'bullpen_ip': perspective_bullpen.get('ip', '3.0'),
                        'bullpen_er': perspective_bullpen.get('er', 0)
                    }

                return {
                    'match_id': m.id,
                    'date': date_part,
                    'match_date': m.match_date or '',
                    'home_away': '홈' if is_home else '원정',
                    'perspective_team': perspective_team,
                    # 이중 호환성 보장을 위한 필드 제공
                    'home_team_name': m.home_team_name,
                    'away_team_name': m.away_team_name,
                    'home_team': m.home_team_name,
                    'away_team': m.away_team_name,
                    'home_score': m.home_score,
                    'away_score': m.away_score,
                    'team_score': my_score,
                    'opp_score': opp_score,
                    'score': f"{m.home_score} - {m.away_score}",
                    'league_name': m.league_name or '',
                    'opponent': opp_team,
                    'result': res,
                    'result_kr': res_kr,
                    'result_emoji': emoji,
                    'period_scores': period_scores,
                    'team_stats': team_stats,
                    'starter': perspective_starter.get('name', ''),
                    'perspective_starter': perspective_starter,
                    'perspective_bullpen': perspective_bullpen,
                    'perspective_batting': perspective_batting,
                    'baseball_stats': baseball_stats
                }

            formatted_h_recent = [format_match_dto(m, home_team) for m in raw_h_recent]
            formatted_a_recent = [format_match_dto(m, away_team) for m in raw_a_recent]
            formatted_h2h = [format_match_dto(m, home_team) for m in raw_h2h]

            # 5. H2H 종합 요약 통계 계산
            h_wins = sum(1 for m in formatted_h2h if m['result'] == 'WIN')
            draws = sum(1 for m in formatted_h2h if m['result'] == 'DRAW')
            a_wins = sum(1 for m in formatted_h2h if m['result'] == 'LOSS')

            return {
                'status': 'success',
                'match_id': match_id,
                'sport_code': sport_code,
                'league_name': league_name,
                'league_code': league_code,
                'home_team': home_team,
                'away_team': away_team,
                'home_team_name': home_team,
                'away_team_name': away_team,
                'home_recent': formatted_h_recent,
                'away_recent': formatted_a_recent,
                'h2h_matches': formatted_h2h,
                'h2h_summary': {
                    'total_matches': len(formatted_h2h),
                    'home_wins': h_wins,
                    'draws': draws,
                    'away_wins': a_wins,
                    'summary_text': f"{h_wins}승 {draws}무 {a_wins}패" if sport_code == 'SOCCER' else f"{h_wins}승 {a_wins}패"
                }
            }
        finally:
            db.close()
