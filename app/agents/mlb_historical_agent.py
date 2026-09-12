"""
MLB Historical Agent (2023, 2024, 2025)
Fetches official MLB Stats API schedule, boxscores, and game details.
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("MLBAgent")

class MLBOfficialAgent:
    BASE_URL = "https://statsapi.mlb.com/api/v1"

    def fetch_season_games(self, season: int) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/schedule?sportId=1&season={season}&gameType=R&hydrate=linescore,probablePitcher,decisions"
        logger.info(f"[MLB Agent] Fetching official schedule for season {season} from {url}")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'TokeonSportsEngine/2.0'})
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"[MLB Agent] Failed to fetch season {season}: {e}")
            return []

        games = []
        for date_entry in data.get("dates", []):
            date_str = date_entry.get("date")
            for g in date_entry.get("games", []):
                game_pk = str(g.get("gamePk"))
                status = g.get("status", {}).get("abstractGameState", "Final")
                status_code = "FINISHED" if status in ["Final", "Completed"] else ("LIVE" if status == "Live" else "SCHEDULED")

                teams = g.get("teams", {})
                home_team = teams.get("home", {})
                away_team = teams.get("away", {})

                home_name = home_team.get("team", {}).get("name", "Unknown Home")
                away_name = away_team.get("team", {}).get("name", "Unknown Away")

                home_score = home_team.get("score", 0) or 0
                away_score = away_team.get("score", 0) or 0

                venue = g.get("venue", {}).get("name", "MLB Stadium")
                game_date = g.get("gameDate", f"{date_str}T00:00:00Z")

                # Probable / Decisions Pitchers
                home_pitcher = home_team.get("probablePitcher", {}).get("fullName", "")
                away_pitcher = away_team.get("probablePitcher", {}).get("fullName", "")

                linescore = g.get("linescore", {})
                innings = linescore.get("innings", [])
                inning_scores = {}
                for idx, inn in enumerate(innings):
                    inning_scores[str(idx + 1)] = {
                        "home": inn.get("home", {}).get("runs", 0),
                        "away": inn.get("away", {}).get("runs", 0)
                    }

                period_scores = {
                    "innings": inning_scores,
                    "runs": {"home": home_score, "away": away_score},
                    "hits": {"home": linescore.get("teams", {}).get("home", {}).get("hits", 0),
                             "away": linescore.get("teams", {}).get("away", {}).get("hits", 0)},
                    "errors": {"home": linescore.get("teams", {}).get("home", {}).get("errors", 0),
                               "away": linescore.get("teams", {}).get("away", {}).get("errors", 0)}
                }

                games.append({
                    "official_id": f"MLB_{season}_{game_pk}",
                    "sport_code": "BASEBALL",
                    "league_name": "MLB 메이저리그",
                    "season": str(season),
                    "round_name": "정규시즌",
                    "match_date": game_date,
                    "stadium": venue,
                    "home_team_name": home_name,
                    "away_team_name": away_name,
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": status_code,
                    "period_scores": period_scores,
                    "home_starter": home_pitcher,
                    "away_starter": away_pitcher
                })

        logger.info(f"[MLB Agent] Ingested {len(games)} official games for MLB {season}")
        return games
