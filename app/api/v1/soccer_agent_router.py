import logging
from typing import Optional
from fastapi import APIRouter, Query
from app.agents.soccer.manager import SoccerAgentManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/soccer/agents", tags=["Soccer League Agents"])

@router.get("", summary="등록된 모든 리그별 전담 축구 에이전트 목록 조회")
def get_soccer_agents():
    return SoccerAgentManager.get_all_agents()

@router.get("/{league_code}/stats/{team_name}", summary="리그 전담 에이전트 기반 팀별 통계/카드/파울/코너킥/점유율 조회")
def get_team_stats(league_code: str, team_name: str, last_n_games: int = 15):
    return SoccerAgentManager.get_team_stats(league_code, team_name)

@router.get("/{league_code}/h2h/{home_team}/{away_team}", summary="리그 에이전트 기반 양 팀 3개년 상대전적 조회")
def get_h2h(league_code: str, home_team: str, away_team: str, limit: int = 15):
    return SoccerAgentManager.get_h2h(league_code, home_team, away_team, limit=limit)

@router.get("/{league_code}/recent/{team_name}", summary="리그 에이전트 기반 팀 최근 경기 이력 조회")
def get_recent_matches(league_code: str, team_name: str, limit: int = 15):
    agent = SoccerAgentManager.get_agent(league_code)
    return agent.get_recent_matches(team_name, limit=limit)
