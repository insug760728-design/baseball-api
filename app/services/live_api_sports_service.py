# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import Match, MatchDetail, MatchEvent

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

# Korean <-> English / International Team Synonyms
TEAM_SYNONYMS = {
    # Baseball (MLB)
    "다저스": ["dodgers", "los angeles dodgers", "la dodgers", "la다저스"],
    "파드리스": ["padres", "san diego padres", "샌디에이고"],
    "자이언츠": ["giants", "san francisco giants", "샌프란시스코"],
    "양키스": ["yankees", "new york yankees", "ny yankees", "뉴욕양키스"],
    "메츠": ["mets", "new york mets", "ny mets", "뉴욕메츠"],
    "레드삭스": ["red sox", "boston red sox", "보스턴"],
    "오리올스": ["orioles", "baltimore orioles", "볼티모어"],
    "블루제이스": ["blue jays", "toronto blue jays", "토론토"],
    "레이스": ["rays", "tampa bay rays", "탬파베이"],
    "화이트삭스": ["white sox", "chicago white sox", "시카고화이트삭스"],
    "가디언스": ["guardians", "cleveland guardians", "클리블랜드"],
    "타이거스": ["tigers", "detroit tigers", "디트로이트"],
    "로열스": ["royals", "kansas city royals", "캔자스시티"],
    "트윈스": ["twins", "minnesota twins", "미네소타"],
    "애스트로스": ["astros", "houston astros", "휴스턴"],
    "에인절스": ["angels", "los angeles angels", "la에인절스"],
    "애슬레틱스": ["athletics", "oakland athletics", "오클랜드"],
    "매리너스": ["mariners", "seattle mariners", "시애틀"],
    "레인저스": ["rangers", "texas rangers", "텍사스"],
    "브레이브스": ["braves", "atlanta braves", "애틀랜타"],
    "말린스": ["marlins", "miami marlins", "마이애미"],
    "필리스": ["phillies", "philadelphia phillies", "필라델피아"],
    "내셔널스": ["nationals", "washington nationals", "워싱턴"],
    "컵스": ["cubs", "chicago cubs", "시카고컵스"],
    "레즈": ["reds", "cincinnati reds", "신시내티"],
    "브루어스": ["brewers", "milwaukee brewers", "밀워키"],
    "파이리츠": ["pirates", "pittsburgh pirates", "피츠버그"],
    "카디널스": ["cardinals", "st louis cardinals", "세인트루이스"],
    "다이아몬드백스": ["diamondbacks", "arizona diamondbacks", "d-backs", "애리조나"],
    "로키스": ["rockies", "colorado rockies", "콜로라도"],

    # Soccer (EPL / La Liga / Serie A / Bundesliga / Ligue 1)
    "인테르": ["internazionale", "inter", "inter milan", "인터밀란"],
    "나폴리": ["napoli", "ssc napoli"],
    "헐시티": ["hull", "hull city"],
    "아스톤v": ["aston villa", "villa", "아스톤빌라"],
    "샬케04": ["schalke", "schalke 04", "샬케"],
    "바이에른": ["bayern", "bayern munich", "bayern munchen", "바이에른뮌헨"],
    "라요": ["rayo", "rayo vallecano", "라요바예카노"],
    "라싱산탄": ["racing", "racing santander", "라싱", "라싱산탄데르"],
    "랑스": ["lens", "rc lens"],
    "로리앙": ["lorient", "fc lorient"],
    "as로마": ["roma", "as roma", "로마"],
    "아탈란타": ["atalanta", "atalanta bc"],
    "르아브르": ["le havre", "le havre ac", "havre"],
    "브레스투": ["brest", "stade brestois 29", "브레스트"],
    "니스": ["nice", "ogc nice"],
    "르망": ["le mans", "le mans fc"],
    "비야레알": ["villarreal", "villarreal cf"],
    "데포르": ["deportivo", "deportivo la coruna", "데포르티보"],
    "에버턴": ["everton"],
    "맨체스u": ["manchester united", "manchester utd", "man utd", "맨유", "맨체스터유나이티드"],
    "함부르크": ["hamburg", "hamburger sv", "hsv"],
    "마인츠": ["mainz", "mainz 05", "fsv mainz 05", "마인츠05"],
    "발렌시아": ["valencia", "valencia cf"],
    "바르셀로": ["barcelona", "fc barcelona", "바르셀로나"],
    "프로시노": ["frosinone", "frosinone calcio", "프로시노네"],
    "베네치아": ["venezia", "venezia fc"],
    "파르마": ["parma", "parma calcio 1913"],
    "몬차": ["monza", "ac monza"],
    "트루아": ["troyes", "estac troyes"],
    "스트라스": ["strasbourg", "rc strasbourg", "스트라스부르"]
}

def normalize_name(n: str) -> str:
    if not n: return ""
    return str(n).replace(" ", "").replace("·", "").replace(".", "").replace("-", "").replace("/", "").lower()

def teams_match(api_name: str, db_name: str) -> bool:
    norm_api = normalize_name(api_name)
    norm_db = normalize_name(db_name)

    if not norm_api or not norm_db:
        return False
    if norm_api == norm_db:
        return True
    if norm_api in norm_db or norm_db in norm_api:
        return True

    # Check synonyms
    for k, aliases in TEAM_SYNONYMS.items():
        norm_k = normalize_name(k)
        norm_aliases = [normalize_name(a) for a in aliases]
        all_group = [norm_k] + norm_aliases

        api_in_group = any(g in norm_api or norm_api in g for g in all_group)
        db_in_group = any(g in norm_db or norm_db in g for g in all_group)

        if api_in_group and db_in_group:
            return True

    return False


class LiveApiSportsService:
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        return os.getenv("API_SPORTS_KEY") or settings.API_SPORTS_KEY or os.getenv("RAPIDAPI_KEY") or settings.RAPIDAPI_KEY

    @classmethod
    def is_rapidapi(cls) -> bool:
        return bool(os.getenv("RAPIDAPI_KEY") or settings.RAPIDAPI_KEY)

    @classmethod
    def is_configured(cls) -> bool:
        key = cls.get_api_key()
        return bool(key and len(key.strip()) > 5)

    @classmethod
    def set_api_key(cls, key: str, provider: str = "api_sports") -> Dict[str, Any]:
        """Save API Key to .env, set in os.environ and settings, and trigger verification"""
        key = key.strip()
        if not key or len(key) < 5:
            return {"status": "ERROR", "message": "유효한 API 키를 입력해주세요."}

        is_rapid = (provider.lower() == "rapidapi")

        # Update environment & settings
        if is_rapid:
            os.environ["RAPIDAPI_KEY"] = key
            settings.RAPIDAPI_KEY = key
            os.environ.pop("API_SPORTS_KEY", None)
            settings.API_SPORTS_KEY = ""
        else:
            os.environ["API_SPORTS_KEY"] = key
            settings.API_SPORTS_KEY = key
            os.environ.pop("RAPIDAPI_KEY", None)
            settings.RAPIDAPI_KEY = ""

        # Update or create .env file
        env_path = os.path.join(os.getcwd(), ".env")
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        new_lines = []
        key_written = False
        target_var = "RAPIDAPI_KEY" if is_rapid else "API_SPORTS_KEY"
        other_var = "API_SPORTS_KEY" if is_rapid else "RAPIDAPI_KEY"

        for line in lines:
            if line.startswith(f"{target_var}="):
                new_lines.append(f"{target_var}={key}\n")
                key_written = True
            elif line.startswith(f"{other_var}="):
                continue
            else:
                new_lines.append(line)

        if not key_written:
            new_lines.append(f"{target_var}={key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        logger.info(f"[LiveApiSports] API Key updated successfully for {provider}")

        # Run immediate live test & sync
        fb_res = cls.sync_live_football()
        bb_res = cls.sync_live_baseball()

        return {
            "status": "SUCCESS",
            "provider": "RapidAPI" if is_rapid else "API-Sports (Direct)",
            "message": "API 키가 성공적으로 등록되었으며 실시간 데이터 동기화가 활성화되었습니다.",
            "football_sync": fb_res,
            "baseball_sync": bb_res
        }

    @classmethod
    def get_status_info(cls) -> Dict[str, Any]:
        key = cls.get_api_key()
        configured = bool(key and len(key.strip()) > 5)
        masked_key = (key[:4] + "****" + key[-4:]) if (key and len(key) >= 8) else ("SET" if configured else "미등록")
        return {
            "is_configured": configured,
            "provider": "RapidAPI" if cls.is_rapidapi() else "API-Sports (Direct)",
            "masked_key": masked_key,
            "supports": ["API-Football (축구 5대리그·K리그)", "API-Baseball (MLB·KBO·NPB)"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    def sync_live_football(cls, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Fetch live & date soccer fixtures and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Fetch live matches
        data_live = cls._make_request("/fixtures?live=all", sport="football")
        fixtures_live = (data_live or {}).get("response", [])

        # 2. Fetch today's matches to get finished / updated scores
        data_date = cls._make_request(f"/fixtures?date={date_str}", sport="football")
        fixtures_date = (data_date or {}).get("response", [])

        all_fixtures = {f.get("fixture", {}).get("id"): f for f in (fixtures_date + fixtures_live) if f.get("fixture", {}).get("id")}.values()

        updated = 0
        db = SessionLocal()
        try:
            db_matches = db.query(Match).filter(
                Match.sport_code == "SOCCER",
                Match.match_date.like(f"{date_str}%")
            ).all()

            for f in all_fixtures:
                fixture_info = f.get("fixture", {})
                teams = f.get("teams", {})
                goals = f.get("goals", {})
                score = f.get("score", {})

                h_name = teams.get("home", {}).get("name", "")
                a_name = teams.get("away", {}).get("name", "")
                status_short = fixture_info.get("status", {}).get("short", "")

                mapped_status = FOOTBALL_STATUS_MAP.get(status_short, "SCHEDULED")
                h_score = goals.get("home") if goals.get("home") is not None else 0
                a_score = goals.get("away") if goals.get("away") is not None else 0

                for m in db_matches:
                    if teams_match(h_name, m.home_team_name) and teams_match(a_name, m.away_team_name):
                        m.home_score = h_score
                        m.away_score = a_score
                        m.status = mapped_status

                        # Update periods if detail exists
                        if not m.details:
                            m.details = MatchDetail(match_id=m.id)

                        halftime = score.get("halftime", {})
                        fulltime = score.get("fulltime", {})
                        period_dict = {
                            "1H": f"{halftime.get('home') or 0}-{halftime.get('away') or 0}",
                            "2H": f"{fulltime.get('home') or h_score}-{fulltime.get('away') or a_score}"
                        }
                        m.details.period_scores = json.dumps(period_dict)
                        updated += 1
                        break
            db.commit()
        except Exception as e:
            logger.error(f"[LiveApiSports] Football sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "total_fixtures": len(all_fixtures), "updated_db_matches": updated}

    @classmethod
    def sync_live_baseball(cls, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Fetch live & date baseball games and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Fetch live games
        data_live = cls._make_request("/games?live=all", sport="baseball")
        games_live = (data_live or {}).get("response", [])

        # 2. Fetch today's games
        data_date = cls._make_request(f"/games?date={date_str}", sport="baseball")
        games_date = (data_date or {}).get("response", [])

        all_games = {g.get("id"): g for g in (games_date + games_live) if g.get("id")}.values()

        updated = 0
        db = SessionLocal()
        try:
            db_matches = db.query(Match).filter(
                Match.sport_code == "BASEBALL",
                Match.match_date.like(f"{date_str}%")
            ).all()

            for g in all_games:
                status_info = g.get("status", {})
                teams = g.get("teams", {})
                scores = g.get("scores", {})

                h_name = teams.get("home", {}).get("name", "")
                a_name = teams.get("away", {}).get("name", "")
                status_short = status_info.get("short", "")

                mapped_status = BASEBALL_STATUS_MAP.get(status_short, "SCHEDULED")
                h_score = scores.get("home", {}).get("total") or 0
                a_score = scores.get("away", {}).get("total") or 0

                for m in db_matches:
                    if teams_match(h_name, m.home_team_name) and teams_match(a_name, m.away_team_name):
                        m.home_score = h_score
                        m.away_score = a_score
                        m.status = mapped_status

                        # Store baseball inning scores if available
                        innings = scores.get("home", {}).get("innings", {})
                        if innings and not m.details:
                            m.details = MatchDetail(match_id=m.id)
                        if innings and m.details:
                            m.details.period_scores = json.dumps(innings)

                        updated += 1
                        break
            db.commit()
        except Exception as e:
            logger.error(f"[LiveApiSports] Baseball sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "total_games": len(all_games), "updated_db_matches": updated}

    @classmethod
    def sync_all(cls) -> Dict[str, Any]:
        return {
            "football": cls.sync_live_football(),
            "baseball": cls.sync_live_baseball()
        }
