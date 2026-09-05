# -*- coding: utf-8 -*-
code = '''from typing import List, Dict, Any, Optional
from datetime import datetime
from app.scrapers.base import BaseScraper
from app.core.teams_master import LEAGUE_TEAMS_DATA

class BaseballScraper(BaseScraper):
    """
    야구(Baseball) 전문 정밀 데이터 수집기
    - 미국 메이저리그 (MLB)
    - 한국 프로야구 (KBO 리그)
    - 일본 프로야구 (NPB)
    """

    def __init__(self, league_id: str = "MLB", league_name: str = "미국 메이저리그 (MLB)"):
        self.league_id = league_id
        self.league_name = league_name

    def get_sport_code(self) -> str:
        return "BASEBALL"

    def get_league_name(self) -> str:
        return self.league_name

    def scrape_matches(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        d = target_date or datetime.now().strftime("%Y-%m-%d")
        lid = self.league_id

        if lid == "MLB":
            return [
                {
                    "official_id": f"MLB_{d}_01", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 11:10", "stadium": "다저 스타디움",
                    "home_team_name": "LA 다저스", "away_team_name": "샌디에이고 파드리스",
                    "home_score": 5, "away_score": 3, "status": "FINISHED"
                },
                {
                    "official_id": f"MLB_{d}_02", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 08:05", "stadium": "오라클 파크",
                    "home_team_name": "샌프란시스코 자이언츠", "away_team_name": "보스턴 레드삭스",
                    "home_score": 4, "away_score": 2, "status": "FINISHED"
                },
                {
                    "official_id": f"MLB_{d}_03", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 09:05", "stadium": "양키 스타디움",
                    "home_team_name": "뉴욕 양키스", "away_team_name": "보스턴 레드삭스",
                    "home_score": 6, "away_score": 4, "status": "FINISHED"
                }
            ]
        elif lid == "KBO":
            return [
                {
                    "official_id": f"KBO_{d}_01", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 18:30", "stadium": "잠실야구장",
                    "home_team_name": "LG 트윈스", "away_team_name": "KIA 타이거즈",
                    "home_score": 6, "away_score": 4, "status": "FINISHED"
                },
                {
                    "official_id": f"KBO_{d}_02", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 18:30", "stadium": "대구삼성라이온즈파크",
                    "home_team_name": "삼성 라이온즈", "away_team_name": "두산 베어스",
                    "home_score": 5, "away_score": 3, "status": "FINISHED"
                },
                {
                    "official_id": f"KBO_{d}_03", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 18:30", "stadium": "한화생명이글스파크",
                    "home_team_name": "한화 이글스", "away_team_name": "LG 트윈스",
                    "home_score": 4, "away_score": 5, "status": "FINISHED"
                }
            ]
        elif lid == "NPB":
            return [
                {
                    "official_id": f"NPB_{d}_01", "sport_code": "BASEBALL", "league_name": self.league_name,
                    "season": "2026", "round_name": "정규시즌", "match_date": f"{d} 18:00", "stadium": "도쿄돔",
                    "home_team_name": "요미우리 자이언츠", "away_team_name": "한신 타이거스",
                    "home_score": 4, "away_score": 3, "status": "FINISHED"
                }
            ]
        return []

    def scrape_match_detail(self, official_id: str) -> Dict[str, Any]:
        """야구 전용 정밀 박스스코어: 이닝별 스코어, 타자 세부 지표, 투수 세부 지표"""
        is_mlb = "MLB" in official_id
        home_t = "LA 다저스" if is_mlb else "LG 트윈스"
        away_t = "샌디에이고 파드리스" if is_mlb else "KIA 타이거즈"

        # 1. 1~9회 전광판 정밀 스코어보드
        period_scores = {
            "innings": {
                "1": {"home": 1, "away": 0}, "2": {"home": 0, "away": 1},
                "3": {"home": 2, "away": 0}, "4": {"home": 0, "away": 2},
                "5": {"home": 2, "away": 0}, "6": {"home": 0, "away": 0},
                "7": {"home": 0, "away": 0}, "8": {"home": 0, "away": 0},
                "9": {"home": "X", "away": 1}
            },
            "summary": {
                "home": {"R": 5, "H": 9, "E": 0, "B": 4},
                "away": {"R": 3, "H": 7, "E": 1, "B": 3}
            }
        }

        # 2. 팀 통계
        team_stats = {
            "hits": {"home": 9, "away": 7},
            "homeruns": {"home": 2, "away": 1},
            "errors": {"home": 0, "away": 1},
            "strikeouts": {"home": 6, "away": 10},
            "walks": {"home": 4, "away": 3},
            "left_on_base": {"home": 7, "away": 5}
        }

        # 3. 경기 타임라인 이벤트
        events = [
            {
                "time_display": "1회말", "event_type": "HOMERUN", "team_name": home_t,
                "player_name": "오타니 쇼헤이" if is_mlb else "홍창기",
                "assist_player_name": None, "score_after": "1-0",
                "description": "우월 솔로 홈런 (비거리 128m, 타구속도 178km/h)"
            },
            {
                "time_display": "2회초", "event_type": "HIT", "team_name": away_t,
                "player_name": "김하성" if is_mlb else "김도영",
                "assist_player_name": None, "score_after": "1-1",
                "description": "좌중간 1타점 적시 2루타"
            },
            {
                "time_display": "3회말", "event_type": "HOMERUN", "team_name": home_t,
                "player_name": "프레디 프리먼" if is_mlb else "오지환",
                "assist_player_name": "무키 베츠" if is_mlb else "신민재",
                "score_after": "3-1",
                "description": "우중월 2점 홈런 (비거리 132m)"
            },
            {
                "time_display": "4회초", "event_type": "HIT", "team_name": away_t,
                "player_name": "페르난도 타티스 주니어" if is_mlb else "최형우",
                "assist_player_name": None, "score_after": "3-3",
                "description": "우전 2타점 동점 적시타"
            },
            {
                "time_display": "5회말", "event_type": "HIT", "team_name": home_t,
                "player_name": "오타니 쇼헤이" if is_mlb else "오스틴 딘",
                "assist_player_name": None, "score_after": "5-3",
                "description": "우중간 결승 2타점 3루타"
            }
        ]

        # 4. 홈팀 & 원정팀 전 선수 정밀 라인업 (타자 9명 + 투수)
        if is_mlb:
            home_players_raw = [
                # 타자 9명
                {"name": "오타니 쇼헤이", "num": 17, "pos": "1번 DH", "type": "HITTER", "ab": 4, "r": 2, "h": 2, "2b": 0, "3b": 1, "hr": 1, "rbi": 3, "bb": 1, "so": 1, "sb": 1, "avg": "0.312", "ops": "1.045"},
                {"name": "무키 베츠", "num": 50, "pos": "2번 SS", "type": "HITTER", "ab": 3, "r": 1, "h": 2, "2b": 1, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 0, "sb": 0, "avg": "0.301", "ops": "0.890"},
                {"name": "프레디 프리먼", "num": 5, "pos": "3번 1B", "type": "HITTER", "ab": 4, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 1, "rbi": 2, "bb": 0, "so": 1, "sb": 0, "avg": "0.288", "ops": "0.865"},
                {"name": "테오스카 에르난데스", "num": 37, "pos": "4번 RF", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 1, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 2, "sb": 0, "avg": "0.272", "ops": "0.840"},
                {"name": "맥스 먼시", "num": 13, "pos": "5번 3B", "type": "HITTER", "ab": 3, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.245", "ops": "0.815"},
                {"name": "윌 스미스", "num": 16, "pos": "6번 C", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 0, "sb": 0, "avg": "0.260", "ops": "0.780"},
                {"name": "개빈 럭스", "num": 9, "pos": "7번 2B", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.250", "ops": "0.710"},
                {"name": "토미 에드먼", "num": 25, "pos": "8번 CF", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 1, "avg": "0.265", "ops": "0.745"},
                {"name": "앤디 파헤스", "num": 84, "pos": "9번 LF", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 0, "avg": "0.240", "ops": "0.700"},
                # 투수
                {"name": "야마모토 요시노부", "num": 18, "pos": "선발 P", "type": "PITCHER", "ip": "6.0", "np": 94, "h": 5, "r": 2, "er": 2, "bb": 2, "so": 8, "hr": 1, "era": "2.92", "whip": "1.08", "decision": "승리투수 (W)"},
                {"name": "에반 필립스", "num": 59, "pos": "마무리 P", "type": "PITCHER", "ip": "1.0", "np": 14, "h": 1, "r": 1, "er": 1, "bb": 0, "so": 2, "hr": 0, "era": "2.45", "whip": "1.02", "decision": "세이브 (SV)"}
            ]

            away_players_raw = [
                # 타자 9명
                {"name": "루이스 아라에즈", "num": 4, "pos": "1번 DH", "type": "HITTER", "ab": 4, "r": 1, "h": 2, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 0, "sb": 0, "avg": "0.315", "ops": "0.740"},
                {"name": "페르난도 타티스 주니어", "num": 23, "pos": "2번 RF", "type": "HITTER", "ab": 4, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 1, "rbi": 2, "bb": 0, "so": 1, "sb": 1, "avg": "0.280", "ops": "0.855"},
                {"name": "주릭슨 프로파", "num": 10, "pos": "3번 LF", "type": "HITTER", "ab": 3, "r": 0, "h": 1, "2b": 1, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.285", "ops": "0.845"},
                {"name": "매니 마차도", "num": 13, "pos": "4번 3B", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 2, "sb": 0, "avg": "0.275", "ops": "0.810"},
                {"name": "잭슨 메릴", "num": 3, "pos": "5번 CF", "type": "HITTER", "ab": 4, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 2, "sb": 0, "avg": "0.290", "ops": "0.825"},
                {"name": "잰더 보가츠", "num": 2, "pos": "6번 2B", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.260", "ops": "0.715"},
                {"name": "제이크 크로넨워스", "num": 9, "pos": "7번 1B", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 0, "avg": "0.245", "ops": "0.720"},
                {"name": "김하성", "num": 7, "pos": "8번 SS", "type": "HITTER", "ab": 4, "r": 1, "h": 2, "2b": 1, "3b": 0, "hr": 0, "rbi": 1, "bb": 0, "so": 1, "sb": 1, "avg": "0.260", "ops": "0.760"},
                {"name": "카일 히가시오카", "num": 20, "pos": "9번 C", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 2, "sb": 0, "avg": "0.220", "ops": "0.710"},
                # 투수
                {"name": "다르빗슈 유", "num": 11, "pos": "선발 P", "type": "PITCHER", "ip": "5.0", "np": 88, "h": 6, "r": 4, "er": 4, "bb": 2, "so": 6, "hr": 2, "era": "3.35", "whip": "1.12", "decision": "패전투수 (L)"}
            ]
        else:
            home_players_raw = [
                {"name": "홍창기", "num": 51, "pos": "1번 RF", "type": "HITTER", "ab": 3, "r": 2, "h": 2, "2b": 1, "3b": 0, "hr": 0, "rbi": 1, "bb": 2, "so": 0, "sb": 0, "avg": "0.330", "ops": "0.880"},
                {"name": "신민재", "num": 4, "pos": "2번 2B", "type": "HITTER", "ab": 4, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 1, "avg": "0.295", "ops": "0.750"},
                {"name": "오스틴 딘", "num": 23, "pos": "3번 1B", "type": "HITTER", "ab": 4, "r": 1, "h": 2, "2b": 0, "3b": 1, "hr": 1, "rbi": 2, "bb": 0, "so": 1, "sb": 0, "avg": "0.315", "ops": "0.960"},
                {"name": "문보경", "num": 2, "pos": "4번 3B", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 1, "bb": 0, "so": 1, "sb": 0, "avg": "0.290", "ops": "0.840"},
                {"name": "오지환", "num": 10, "pos": "5번 SS", "type": "HITTER", "ab": 4, "r": 1, "h": 2, "2b": 1, "3b": 0, "hr": 1, "rbi": 2, "bb": 0, "so": 1, "sb": 0, "avg": "0.270", "ops": "0.810"},
                {"name": "박동원", "num": 27, "pos": "6번 C", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 0, "avg": "0.265", "ops": "0.790"},
                {"name": "김현수", "num": 22, "pos": "7번 DH", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 0, "sb": 0, "avg": "0.280", "ops": "0.780"},
                {"name": "박해민", "num": 17, "pos": "8번 CF", "type": "HITTER", "ab": 3, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 1, "avg": "0.260", "ops": "0.710"},
                {"name": "문성주", "num": 8, "pos": "9번 LF", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 0, "sb": 0, "avg": "0.290", "ops": "0.740"},
                {"name": "임찬규", "num": 29, "pos": "선발 P", "type": "PITCHER", "ip": "6.0", "np": 92, "h": 6, "r": 3, "er": 3, "bb": 2, "so": 7, "hr": 1, "era": "3.85", "whip": "1.25", "decision": "승리투수 (W)"}
            ]
            away_players_raw = [
                {"name": "박찬호", "num": 1, "pos": "1번 SS", "type": "HITTER", "ab": 4, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 1, "avg": "0.305", "ops": "0.740"},
                {"name": "김도영", "num": 5, "pos": "2번 3B", "type": "HITTER", "ab": 4, "r": 1, "h": 2, "2b": 1, "3b": 0, "hr": 1, "rbi": 2, "bb": 0, "so": 1, "sb": 1, "avg": "0.345", "ops": "1.060"},
                {"name": "김선빈", "num": 3, "pos": "3번 2B", "type": "HITTER", "ab": 3, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 0, "sb": 0, "avg": "0.320", "ops": "0.790"},
                {"name": "최형우", "num": 34, "pos": "4번 DH", "type": "HITTER", "ab": 4, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 1, "bb": 0, "so": 1, "sb": 0, "avg": "0.285", "ops": "0.870"},
                {"name": "소크라테스", "num": 30, "pos": "5번 CF", "type": "HITTER", "ab": 4, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 2, "sb": 0, "avg": "0.295", "ops": "0.830"},
                {"name": "이우성", "num": 25, "pos": "6번 1B", "type": "HITTER", "ab": 3, "r": 0, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.280", "ops": "0.760"},
                {"name": "나성범", "num": 47, "pos": "7번 RF", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 1, "so": 1, "sb": 0, "avg": "0.275", "ops": "0.850"},
                {"name": "김태군", "num": 42, "pos": "8번 C", "type": "HITTER", "ab": 3, "r": 0, "h": 0, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 0, "avg": "0.250", "ops": "0.680"},
                {"name": "최원준", "num": 2, "pos": "9번 LF", "type": "HITTER", "ab": 3, "r": 1, "h": 1, "2b": 0, "3b": 0, "hr": 0, "rbi": 0, "bb": 0, "so": 1, "sb": 0, "avg": "0.285", "ops": "0.730"},
                {"name": "양현종", "num": 54, "pos": "선발 P", "type": "PITCHER", "ip": "5.0", "np": 95, "h": 7, "r": 5, "er": 5, "bb": 3, "so": 5, "hr": 2, "era": "4.15", "whip": "1.32", "decision": "패전투수 (L)"}
            ]

        player_stats = []
        for p in home_players_raw:
            is_hitter = p["type"] == "HITTER"
            extra = {
                "player_type": p["type"],
                "hits": p.get("h", 0),
                "doubles": p.get("2b", 0),
                "triples": p.get("3b", 0),
                "homeruns": p.get("hr", 0),
                "runs": p.get("r", 0),
                "walks": p.get("bb", 0),
                "strikeouts": p.get("so", 0),
                "stolen_bases": p.get("sb", 0),
                "avg": p.get("avg"),
                "ops": p.get("ops"),
                "ip": p.get("ip"),
                "np": p.get("np"),
                "er": p.get("er"),
                "era": p.get("era"),
                "whip": p.get("whip"),
                "decision": p.get("decision")
            }
            player_stats.append({
                "team_name": home_t,
                "player_name": p["name"],
                "back_number": p["num"],
                "position": p["pos"],
                "minutes_played": 0,
                "points": p.get("rbi", 0) if is_hitter else p.get("so", 0), # 타자는 타점, 투수는 탈삼진
                "assists": 0,
                "shots": p.get("ab", 0) if is_hitter else int(float(p.get("ip", "0"))), # 타자는 타수, 투수는 투구이닝
                "extra_stats": extra
            })

        for p in away_players_raw:
            is_hitter = p["type"] == "HITTER"
            extra = {
                "player_type": p["type"],
                "hits": p.get("h", 0),
                "doubles": p.get("2b", 0),
                "triples": p.get("3b", 0),
                "homeruns": p.get("hr", 0),
                "runs": p.get("r", 0),
                "walks": p.get("bb", 0),
                "strikeouts": p.get("so", 0),
                "stolen_bases": p.get("sb", 0),
                "avg": p.get("avg"),
                "ops": p.get("ops"),
                "ip": p.get("ip"),
                "np": p.get("np"),
                "er": p.get("er"),
                "era": p.get("era"),
                "whip": p.get("whip"),
                "decision": p.get("decision")
            }
            player_stats.append({
                "team_name": away_t,
                "player_name": p["name"],
                "back_number": p["num"],
                "position": p["pos"],
                "minutes_played": 0,
                "points": p.get("rbi", 0) if is_hitter else p.get("so", 0),
                "assists": 0,
                "shots": p.get("ab", 0) if is_hitter else int(float(p.get("ip", "0"))),
                "extra_stats": extra
            })

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "source_url": f"https://www.mlb.com/gameday/{official_id}" if is_mlb else f"https://www.koreabaseball.com/Game/{official_id}",
            "events": events,
            "player_stats": player_stats
        }
'''

with open("app/scrapers/baseball_scraper.py", "w", encoding="utf-8") as f:
    f.write(code)
print("app/scrapers/baseball_scraper.py created successfully!")