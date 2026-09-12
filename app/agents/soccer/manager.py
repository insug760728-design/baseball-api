"""
TOKEON 전 리그 통합 에이전트 총괄 매니저 (SoccerAgentManager)
- 전 세계 12대 축구 리그 전담 에이전트 총괄 관리
- 실시간 경기 수집, 정밀 검증, 팩트 데이터 영구 누적 오케스트레이션
"""
import logging
from typing import Dict, Any, List
from app.agents.soccer.base_agent import BaseSoccerLeagueAgent
from app.agents.soccer.epl_agent import EPLAgent
from app.agents.soccer.laliga_agent import LaLigaAgent
from app.agents.soccer.seriea_agent import SerieAAgent
from app.agents.soccer.bundesliga_agent import BundesligaAgent
from app.agents.soccer.ligue1_agent import Ligue1Agent
from app.agents.soccer.eredivisie_agent import EredivisieAgent
from app.agents.soccer.kleague_agent import KLeagueAgent
from app.agents.soccer.jleague_agent import JLeagueAgent
from app.agents.soccer.mls_agent import MLSAgent
from app.agents.soccer.ucl_agent import UCLAgent
from app.agents.soccer.uel_agent import UELAgent
from app.agents.soccer.copa_agent import CopaAgent

logger = logging.getLogger(__name__)

class SoccerAgentManager:
    _agents: Dict[str, BaseSoccerLeagueAgent] = {}

    @classmethod
    def initialize(cls):
        """12대 리그 전담 에이전트 초기화"""
        cls._agents = {
            "EPL": EPLAgent(),
            "LALIGA": LaLigaAgent(),
            "SERIE_A": SerieAAgent(),
            "BUNDESLIGA": BundesligaAgent(),
            "LIGUE_1": Ligue1Agent(),
            "EREDIVISIE": EredivisieAgent(),
            "K_LEAGUE": KLeagueAgent(),
            "J_LEAGUE": JLeagueAgent(),
            "MLS": MLSAgent(),
            "UCL": UCLAgent(),
            "UEL": UELAgent(),
            "COPA": CopaAgent()
        }
        logger.info(f"[AgentManager] {len(cls._agents)}개 리그 전담 데이터 수집 에이전트 가동 완료.")

    @classmethod
    def get_agent(cls, league_code: str) -> BaseSoccerLeagueAgent:
        if not cls._agents:
            cls.initialize()
        return cls._agents.get(league_code.upper())

    @classmethod
    def get_all_agents(cls) -> Dict[str, BaseSoccerLeagueAgent]:
        if not cls._agents:
            cls.initialize()
        return cls._agents

    @classmethod
    def get_system_health_report(cls) -> List[Dict[str, Any]]:
        """전 리그 에이전트 수집 현황 통합 리포트"""
        if not cls._agents:
            cls.initialize()
        reports = []
        for code, agent in cls._agents.items():
            try:
                reports.append(agent.get_agent_status())
            except Exception as e:
                reports.append({
                    "agent_name": f"{code}_Agent",
                    "status": "ERROR",
                    "error": str(e)
                })
        return reports
