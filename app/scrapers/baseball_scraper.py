from typing import List, Dict, Any, Optional
from datetime import datetime
from app.scrapers.base import BaseScraper
from app.scrapers.official_mlb_live_scraper import MlbOfficialScraper
from app.scrapers.official_kbo_live_scraper import KboOfficialScraper
from app.scrapers.official_npb_live_scraper import NpbOfficialScraper

class BaseballScraper(BaseScraper):
    """
    야구(Baseball) 전문 정밀 데이터 수집기
    - 미국 메이저리그 (MLB) : 100% 메이저리그 공식 Stats API (statsapi.mlb.com) 실시간 연동
    - 한국 프로야구 (KBO 리그) : 100% KBO 공식 사이트 (koreabaseball.com) 실시간 연동
    - 일본 프로야구 (NPB) : 100% NPB 공식 사이트 (npb.jp) 실시간 연동
    """

    def __init__(self, league_id: str = "MLB", league_name: str = "미국 메이저리그 (MLB)"):
        self.league_id = league_id
        self.league_name = league_name
        self.mlb_live = MlbOfficialScraper()
        self.kbo_live = KboOfficialScraper()
        self.npb_live = NpbOfficialScraper()

    def get_sport_code(self) -> str:
        return "BASEBALL"

    def get_league_name(self) -> str:
        return self.league_name

    def scrape_matches(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        d = target_date or datetime.now().strftime("%Y-%m-%d")
        lid = self.league_id.upper()

        # 1. 미국 메이저리그 (MLB) -> 공식 MLB API 실시간 수집
        if lid == "MLB":
            return self.mlb_live.scrape_schedule(d)

        # 2. 한국 프로야구 (KBO) -> 공식 KBO 사이트 실시간 수집
        if lid == "KBO":
            return self.kbo_live.scrape_schedule(target_date=d)

        # 3. 일본 프로야구 (NPB) -> 공식 NPB 사이트 실시간 수집
        if lid == "NPB":
            return self.npb_live.scrape_schedule(target_date=d)

        # 4. 전체 야구 리그
        if lid == "ALL":
            mlb_games = self.mlb_live.scrape_schedule(d)
            kbo_games = self.kbo_live.scrape_schedule(target_date=d)
            npb_games = self.npb_live.scrape_schedule(target_date=d)
            return mlb_games + kbo_games + npb_games

        return []

    def scrape_match_detail(self, official_id: str) -> Dict[str, Any]:
        """MLB / KBO / NPB 공식 실시간 박스스코어, 라인스코어, 선수 지표 조회 (가짜 데이터 없음)"""
        if "MLB_" in official_id:
            try:
                game_pk_str = official_id.replace("MLB_", "")
                if game_pk_str.isdigit():
                    return self.mlb_live.scrape_game_detail(int(game_pk_str))
            except Exception as e:
                print(f"[MLB Live Detail Error] {e}")

        if "KBO_" in official_id:
            try:
                return self.kbo_live.scrape_game_detail(official_id)
            except Exception as e:
                print(f"[KBO Live Detail Error] {e}")

        if "NPB_" in official_id:
            try:
                return self.npb_live.scrape_game_detail(official_id)
            except Exception as e:
                print(f"[NPB Live Detail Error] {e}")

        return {
            "period_scores": {},
            "team_stats": {},
            "source_url": None,
            "events": [],
            "player_stats": []
        }
