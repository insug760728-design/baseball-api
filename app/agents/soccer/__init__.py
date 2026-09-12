from app.agents.soccer.base_agent import BaseSoccerLeagueAgent
from app.agents.soccer.manager import SoccerAgentManager
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

__all__ = [
    'BaseSoccerLeagueAgent', 'SoccerAgentManager',
    'EPLAgent', 'LaLigaAgent', 'SerieAAgent', 'BundesligaAgent',
    'Ligue1Agent', 'EredivisieAgent', 'KLeagueAgent', 'JLeagueAgent',
    'MLSAgent', 'UCLAgent', 'UELAgent', 'CopaAgent'
]
