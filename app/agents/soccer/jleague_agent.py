"""
TOKEON 일본 J1리그 (J-League) 전담 데이터 수집 & 검증 관리 에이전트 (JLeagueAgent)
- 전담 리그: 일본 J1리그 (J-League) (League ID: 98)
- 역할: 실시간 일정 수집, 종료 경기 팩트 검증, 세부 스탯(슈팅/점유율/코너/카드/파울) 영구 누적 관리
"""
from typing import Dict, Any, List
from app.agents.soccer.base_agent import BaseSoccerLeagueAgent

class JLeagueAgent(BaseSoccerLeagueAgent):
    def __init__(self):
        super().__init__(
            league_id=98,
            league_name="일본 J1리그 (J-League)",
            league_code="J_LEAGUE"
        )

    def get_agent_status(self) -> Dict[str, Any]:
        """에이전트 상태 및 관리 중인 경기 현황 리포트"""
        stats = self.get_league_statistics()
        return {
            "agent_name": "JLeagueAgent",
            "league_name": self.league_name,
            "league_id": self.league_id,
            "league_code": self.league_code,
            "total_accumulated_matches": stats.get("total_matches", 0),
            "total_teams": stats.get("total_teams", 0),
            "latest_match_date": stats.get("latest_match_date", "-"),
            "status": "ACTIVE_ACCUMULATING"
        }
