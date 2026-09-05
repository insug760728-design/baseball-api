# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.database import SessionLocal
def clean_team_name(n):
    if not n: return ""
    return str(n).replace(" ", "").replace("·", "").replace(".", "").replace("-", "").lower()

logger = logging.getLogger("live_api_sports")
logger.setLevel(logging.INFO)

# Mapping API-Sports football status to our status
FOOTBALL_STATUS_MAP = {
    "1H": "LIVE", "HT": "LIVE", "2H": "LIVE", "ET": "LIVE", "BT": "LIVE", "P": "LIVE", "LIVE": "LIVE",
    "FT": "FINISHED", "AET": "FINISHED", "PEN": "FINISHED",
    "NS": "SCHEDULED", "TBD": "SCHEDULED",
    "PPD": "CANCELLED", "CANC": "CANCELLED", "ABD": "CANCELLED"
}

# Mapping API-Baseball status to our status
BASEBALL_STATUS_MAP = {
    "IN1": "LIVE", "IN2": "LIVE", "IN3": "LIVE", "IN4": "LIVE", "IN5": "LIVE",
    "IN6": "LIVE", "IN7": "LIVE", "IN8": "LIVE", "IN9": "LIVE", "IN": "LIVE",
    "FT": "FINISHED", "AOT": "FINISHED",
    "NS": "SCHEDULED", "POST": "CANCELLED", "CANC": "CANCELLED"
}

class LiveApiSportsService:
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        return settings.API_SPORTS_KEY or os.getenv("API_SPORTS_KEY") or settings.RAPIDAPI_KEY or os.getenv("RAPIDAPI_KEY")

    @classmethod
    def is_rapidapi(cls) -> bool:
        return bool(settings.RAPIDAPI_KEY or os.getenv("RAPIDAPI_KEY"))

    @classmethod
    def is_configured(cls) -> bool:
        key = cls.get_api_key()
        return bool(key and len(key.strip()) > 5)

    @classmethod
    def get_status_info(cls) -> Dict[str, Any]:
        key = cls.get_api_key()
        configured = bool(key and len(key.strip()) > 5)
        masked_key = (key[:4] + "****" + key[-4:]) if (key and len(key) >= 8) else ("SET" if configured else "NOT_CONFIGURED")
        return {
            "is_configured": configured,
            "provider": "RapidAPI" if cls.is_rapidapi() else "API-Sports (Direct)",
            "masked_key": masked_key,
            "supports": ["API-Football (축구 5대리그·K리그)", "API-Baseball (MLB·KBO·NPB)"]
        }

    @classmethod
    def _make_request(cls, endpoint: str, sport: str = "football") -> Optional[Dict[str, Any]]:
        key = cls.get_api_key()
        if not key:
            return None

        headers = {"User-Agent": "TOKEON-LiveSync/1.0"}
        if cls.is_rapidapi():
            headers["x-rapidapi-key"] = key
            if sport == "football":
                base_url = "https://api-football-v1.p.rapidapi.com/v3"
                headers["x-rapidapi-host"] = "api-football-v1.p.rapidapi.com"
            else:
                base_url = "https://api-baseball.p.rapidapi.com"
                headers["x-rapidapi-host"] = "api-baseball.p.rapidapi.com"
        else:
            headers["x-apisports-key"] = key
            if sport == "football":
                base_url = "https://v3.football.api-sports.io"
            else:
                base_url = "https://v1.baseball.api-sports.io"

        url = f"{base_url}{endpoint}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except Exception as e:
            logger.error(f"[LiveApiSports] Request failed for {url}: {e}")
            return None

    @classmethod
    def sync_live_football(cls) -> Dict[str, Any]:
        """Fetch all live soccer fixtures and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        data = cls._make_request("/fixtures?live=all", sport="football")
        if not data or not data.get("response"):
            return {"status": "SUCCESS", "updated_count": 0, "live_count": 0}

        fixtures = data.get("response", [])
        updated = 0
        db = SessionLocal()
        try:
            for f in fixtures:
                fixture_info = f.get("fixture", {})
                teams = f.get("teams", {})
                goals = f.get("goals", {})

                h_name = teams.get("home", {}).get("name", "")
                a_name = teams.get("away", {}).get("name", "")
                status_short = fixture_info.get("status", {}).get("short", "")

                mapped_status = FOOTBALL_STATUS_MAP.get(status_short, "LIVE")
                h_score = goals.get("home") or 0
                a_score = goals.get("away") or 0

                clean_h = clean_team_name(h_name)
                clean_a = clean_team_name(a_name)

                db_matches = db.query(Match).filter(Match.sport_code == "SOCCER").all()
                for m in db_matches:
                    if (clean_h in clean_team_name(m.home_team_name) or clean_team_name(m.home_team_name) in clean_h) and                        (clean_a in clean_team_name(m.away_team_name) or clean_team_name(m.away_team_name) in clean_a):
                        m.home_score = h_score
                        m.away_score = a_score
                        m.status = mapped_status
                        updated += 1
                        break
            db.commit()
        except Exception as e:
            logger.error(f"[LiveApiSports] Football sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "live_count": len(fixtures), "updated_count": updated}

    @classmethod
    def sync_live_baseball(cls) -> Dict[str, Any]:
        """Fetch all live baseball games and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        data = cls._make_request("/games?live=all", sport="baseball")
        if not data or not data.get("response"):
            return {"status": "SUCCESS", "updated_count": 0, "live_count": 0}

        games = data.get("response", [])
        updated = 0
        db = SessionLocal()
        try:
            for g in games:
                status_info = g.get("status", {})
                teams = g.get("teams", {})
                scores = g.get("scores", {})

                h_name = teams.get("home", {}).get("name", "")
                a_name = teams.get("away", {}).get("name", "")
                status_short = status_info.get("short", "")

                mapped_status = BASEBALL_STATUS_MAP.get(status_short, "LIVE")
                h_score = scores.get("home", {}).get("total") or 0
                a_score = scores.get("away", {}).get("total") or 0

                clean_h = clean_team_name(h_name)
                clean_a = clean_team_name(a_name)

                db_matches = db.query(Match).filter(Match.sport_code == "BASEBALL").all()
                for m in db_matches:
                    if (clean_h in clean_team_name(m.home_team_name) or clean_team_name(m.home_team_name) in clean_h) and                        (clean_a in clean_team_name(m.away_team_name) or clean_team_name(m.away_team_name) in clean_a):
                        m.home_score = h_score
                        m.away_score = a_score
                        m.status = mapped_status
                        updated += 1
                        break
            db.commit()
        except Exception as e:
            logger.error(f"[LiveApiSports] Baseball sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "live_count": len(games), "updated_count": updated}
