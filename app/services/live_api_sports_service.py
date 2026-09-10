# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_

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

# Comprehensive Korean <-> English / International Team Synonyms
TEAM_SYNONYMS = {
    # Baseball (KBO)
    "키움": ["kiwoom", "kiwoom heroes", "키움 히어로즈", "히어로즈"],
    "NC": ["nc", "nc dinos", "nc 다이노스", "다이노스"],
    "KIA": ["kia", "kia tigers", "기아", "kia 타이거즈", "기아 타이거즈", "타이거즈"],
    "KT": ["kt", "kt wiz", "kt wiz suwon", "kt 위즈", "위즈"],
    "LG": ["lg", "lg twins", "lg 트윈스", "트윈스"],
    "삼성": ["samsung", "samsung lions", "삼성 라이온즈", "삼성라이온즈"],
    "롯데": ["lotte", "lotte giants", "롯데 자이언츠", "롯데자이언츠"],
    "한화": ["hanwha", "hanwha eagles", "한화 이글스", "이글스"],
    "SSG": ["ssg", "ssg landers", "ssg 랜더스", "랜더스", "sk"],
    "두산": ["doosan", "doosan bears", "두산 베어스", "베어스"],

    # Baseball (NPB)
    "요미우리": ["yomiuri", "yomiuri giants", "요미우리 자이언츠"],
    "한신": ["hanshin", "hanshin tigers", "한신 타이거스"],
    "주니치": ["chunichi", "chunichi dragons", "주니치 드래곤즈"],
    "야쿠르트": ["yakult", "yakult swallows", "도쿄 야쿠르트", "도쿄 야쿠르트 스왈로스"],
    "히로시마": ["hiroshima", "hiroshima carp", "히로시마 도요 카프"],
    "요코하마": ["yokohama", "yokohama baystars", "요코하마 dena 베이스타즈"],
    "소프트뱅크": ["softbank", "fukuoka softbank", "fukuoka s. hawks", "후쿠오카 소프트뱅크"],
    "오릭스": ["orix", "orix buffaloes", "오릭스 버펄로스"],
    "지바롯데": ["chiba lotte", "chiba lotte marines", "지바 롯데", "지바 롯데 마린스"],
    "라쿠텐": ["rakuten", "rakuten gold. eagles", "도호쿠 라쿠텐", "도호쿠 라쿠텐 골든이글스"],
    "세이부": ["seibu", "seibu lions", "사이타마 세이부 라이온즈"],
    "닛폰햄": ["nippon ham", "nippon ham fighters", "홋카이도 닛폰햄"],

    # Baseball (MLB)
    "다저스": ["dodgers", "los angeles dodgers", "la dodgers", "la다저스", "다저스"],
    "파드리스": ["padres", "san diego padres", "샌디에이고", "파드리스"],
    "자이언츠": ["giants", "san francisco giants", "샌프란시스코", "자이언츠"],
    "양키스": ["yankees", "new york yankees", "ny yankees", "뉴욕양키스", "뉴욕 양키스"],
    "메츠": ["mets", "new york mets", "ny mets", "뉴욕메츠", "뉴욕 메츠"],
    "레드삭스": ["red sox", "boston red sox", "보스턴", "레드삭스"],
    "오리올스": ["orioles", "baltimore orioles", "볼티모어", "오리올스"],
    "블루제이스": ["blue jays", "toronto blue jays", "토론토", "블루제이스"],
    "레이스": ["rays", "tampa bay rays", "탬파베이", "레이스"],
    "화이트삭스": ["white sox", "chicago white sox", "시카고화이트삭스", "시카고 화이트삭스"],
    "가디언스": ["guardians", "cleveland guardians", "클리블랜드", "가디언스"],
    "타이거스": ["tigers", "detroit tigers", "디트로이트", "타이거스"],
    "로열스": ["royals", "kansas city royals", "캔자스시티", "로열스"],
    "트윈스": ["twins", "minnesota twins", "미네소타", "트윈스"],
    "애스트로스": ["astros", "houston astros", "휴스턴", "애스트로스"],
    "에인절스": ["angels", "los angeles angels", "la에인절스", "la 에인절스"],
    "애슬레틱스": ["athletics", "oakland athletics", "오클랜드", "애슬레틱스"],
    "매리너스": ["mariners", "seattle mariners", "시애틀", "매리너스"],
    "레인저스": ["rangers", "texas rangers", "텍사스", "레인저스"],
    "브레이브스": ["braves", "atlanta braves", "애틀랜타", "브레이브스"],
    "말린스": ["marlins", "miami marlins", "마이애미", "말린스"],
    "필리스": ["phillies", "philadelphia phillies", "필라델피아", "필리스"],
    "내셔널스": ["nationals", "washington nationals", "워싱턴", "내셔널스"],
    "컵스": ["cubs", "chicago cubs", "시카고컵스", "시카고 컵스"],
    "레즈": ["reds", "cincinnati reds", "신시내티", "레즈"],
    "브루어스": ["brewers", "milwaukee brewers", "밀워키", "브루어스"],
    "파이리츠": ["pirates", "pittsburgh pirates", "피츠버그", "파이리츠"],
    "카디널스": ["cardinals", "st louis cardinals", "st. louis cardinals", "세인트루이스", "카디널스"],
    "다이아몬드백스": ["diamondbacks", "arizona diamondbacks", "d-backs", "애리조나", "다이아몬드백스"],
    "로키스": ["rockies", "colorado rockies", "콜로라도", "로키스"],

    # Soccer (EPL / La Liga / Serie A / Bundesliga / Ligue 1)
    "에버턴": ["everton", "에버튼"],
    "맨체스u": ["manchester united", "manchester utd", "man utd", "맨유", "맨체스터유나이티드", "맨체스터 유나이티드"],
    "맨체스c": ["manchester city", "man city", "man city fc", "맨시티", "맨체스터시티", "맨체스터 시티"],
    "아스널": ["arsenal", "아스날"],
    "첼시": ["chelsea"],
    "리버풀": ["liverpool"],
    "토트넘": ["tottenham", "tottenham hotspur", "spurs"],
    "a빌라": ["aston villa", "villa", "아스톤빌라", "아스톤v", "애스턴빌라", "아스톤 빌라"],
    "뉴캐슬": ["newcastle", "newcastle united"],
    "브라이턴": ["brighton", "brighton & hove albion", "brighton and hove albion", "브라이튼"],
    "브렌트퍼": ["brentford", "브렌트포드"],
    "크리스탈": ["crystal palace", "palace", "크리스털", "크리스탈팰리스", "크리스탈 팰리스"],
    "풀럼": ["fulham"],
    "웨스트햄": ["west ham", "west ham united"],
    "울버햄튼": ["wolverhampton", "wolves"],
    "본머스": ["bournemouth", "afc bournemouth"],
    "노팅엄f": ["nottingham", "nottingham forest", "노팅엄"],
    "레스터": ["leicester", "leicester city"],
    "사우샘프": ["southampton", "사우샘프턴"],
    "입스위치": ["ipswich", "ipswich town"],
    "헐시티": ["hull", "hull city"],
    "유벤투스": ["juventus", "유벤"],
    "ac밀란": ["ac milan", "milan", "밀란"],
    "인테르": ["internazionale", "inter", "inter milan", "인터밀란", "인터 밀란"],
    "나폴리": ["napoli", "ssc napoli"],
    "as로마": ["roma", "as roma", "로마"],
    "라치오": ["lazio", "ss lazio"],
    "아탈란타": ["atalanta", "atalanta bc"],
    "피오렌": ["fiorentina", "acf fiorentina", "피오렌티나"],
    "볼로냐": ["bologna"],
    "토리노": ["torino"],
    "몬차": ["monza", "ac monza", "ac몬차"],
    "제노아": ["genoa", "genoa cfc"],
    "베네치아": ["venezia", "venezia fc"],
    "파르마": ["parma", "parma calcio 1913"],
    "프로시노": ["frosinone", "frosinone calcio", "프로시노네", "프로시논"],
    "칼리아리": ["cagliari"],
    "우디네세": ["udinese"],
    "엠폴리": ["empoli"],
    "레체": ["lecce"],
    "베로나": ["hellas verona", "verona", "헬라스"],
    "코모": ["como"],
    "바르셀로": ["barcelona", "fc barcelona", "바르셀로나", "바르사"],
    "레알마드리드": ["real madrid", "레알", "레알 마드리드"],
    "아틀레티코": ["atletico madrid", "atletico de madrid", "atletico", "아틀레티코 마드리드"],
    "발렌시아": ["valencia", "valencia cf"],
    "비야레알": ["villarreal", "villarreal cf"],
    "세비야": ["sevilla", "sevilla fc"],
    "소시에다드": ["real sociedad", "레알 소시에다드"],
    "베티스": ["real betis", "레알 베티스"],
    "빌바오": ["athletic club", "athletic bilbao", "아틀레틱 빌바오"],
    "지로나": ["girona", "girona fc"],
    "에스파뇰": ["espanyol", "rcd espanyol"],
    "셀타비고": ["celta vigo", "celta de vigo", "셀타"],
    "헤타페": ["getafe", "getafe cf"],
    "오사수나": ["osasuna", "ca osasuna"],
    "알라베스": ["alaves", "deportivo alaves"],
    "라요": ["rayo", "rayo vallecano", "라요바예카노"],
    "라싱산탄": ["racing", "racing santander", "라싱", "라싱산탄데르"],
    "데포르": ["deportivo", "deportivo la coruna", "데포르티보"],
    "바이에른": ["bayern", "bayern munich", "bayern munchen", "바이에른뮌헨", "바이에른 뮌헨"],
    "도르트문트": ["dortmund", "borussia dortmund", "bvb"],
    "레버쿠젠": ["leverkusen", "bayer leverkusen"],
    "라이프치히": ["rb leipzig", "leipzig"],
    "프랑크푸르트": ["eintracht frankfurt", "frankfurt"],
    "슈투트가르트": ["vfb stuttgart", "stuttgart"],
    "볼프스부르크": ["vfl wolfsburg", "wolfsburg"],
    "묀헨글라트바흐": ["borussia monchengladbach", "monchengladbach"],
    "함부르크": ["hamburg", "hamburger sv", "hsv"],
    "마인츠": ["mainz", "mainz 05", "fsv mainz 05", "마인츠05"],
    "샬케04": ["schalke", "schalke 04", "샬케"],
    "파리생제르맹": ["psg", "paris saint germain", "paris saint-germain", "파리생제르망", "파리"],
    "마르세유": ["marseille", "olympique marseille"],
    "모나코": ["monaco", "as monaco"],
    "리옹": ["lyon", "olympique lyon"],
    "릴": ["lille", "lille osc"],
    "랑스": ["lens", "rc lens"],
    "로리앙": ["lorient", "fc lorient"],
    "르아브르": ["le havre", "le havre ac", "havre"],
    "브레스투": ["brest", "stade brestois 29", "브레스트"],
    "니스": ["nice", "ogc nice"],
    "르망": ["le mans", "le mans fc"],
    "트루아": ["troyes", "estac troyes"],
    "스트라스": ["strasbourg", "rc strasbourg", "스트라스부르"],
    "스타드렌": ["rennes", "stade rennais", "렌"],

    # Soccer (EFL Championship)
    "리즈": ["leeds", "leeds united", "leeds united fc"],
    "번리": ["burnley", "burnley fc"],
    "선덜랜드": ["sunderland", "sunderland afc"],
    "셰필드u": ["sheffield united", "sheffield utd", "셰필드", "셰필드유나이티드"],
    "셰필드w": ["sheffield wednesday", "sheffield wed", "셰필드웬즈데이"],
    "웨스트브롬": ["west brom", "west bromwich albion", "wba", "웨스트브로미치"],
    "미들즈브러": ["middlesbrough", "boro"],
    "노리치": ["norwich", "norwich city"],
    "코번트리": ["coventry", "coventry city"],
    "왓포드": ["watford"],
    "블랙번": ["blackburn", "blackburn rovers"],
    "스토크": ["stoke", "stoke city"],
    "브리스톨c": ["bristol city", "브리스톨"],
    "프레스턴": ["preston", "preston north end"],
    "스완지": ["swansea", "swansea city"],
    "QPR": ["qpr", "queens park rangers"],
    "밀월": ["millwall"],
    "더비": ["derby", "derby county"],
    "포츠머스": ["portsmouth"],
    "옥스퍼드": ["oxford united", "oxford"],
    "플리머스": ["plymouth argyle", "plymouth"],
    "카디프": ["cardiff", "cardiff city"],
    "루턴": ["luton", "luton town"],

    # Soccer (UEFA Champions League / European Competitions)
    "벤피카": ["benfica", "sl benfica"],
    "스포르팅": ["sporting cp", "sporting lisbon", "sporting"],
    "포르투": ["porto", "fc porto"],
    "페예노르트": ["feyenoord", "feyenoord rotterdam"],
    "PSV": ["psv", "psv eindhoven"],
    "셀틱": ["celtic", "celtic fc"],
    "레인저스FC": ["rangers", "glasgow rangers", "rangers fc"],
    "샤흐타르": ["shakhtar", "shakhtar donetsk"],
    "츠르베나": ["crvena zvezda", "red star belgrade", "츠르베나 즈베즈다"],
    "영보이스": ["young boys", "bsc young boys"],
    "디나모자그레브": ["dinamo zagreb", "gnk dinamo zagreb"],
    "잘츠부르크": ["salzburg", "red bull salzburg", "rb salzburg"],
    "스파르타프라하": ["sparta prague", "ac sparta praha"],
    "슬라비아프라하": ["slavia prague", "sk slavia praha"],
    "슈투름그라츠": ["sturm graz", "sk sturm graz"],
    "슬로반": ["slovan bratislava", "sk slovan bratislava"],
    "갈라타사라이": ["galatasaray", "galatasaray sk"],
    "페네르바체": ["fenerbahce", "fenerbahce sk"],
    "베식타시": ["besiktas", "besiktas jk"],
    "보되글림트": ["bodo/glimt", "fk bodo/glimt", "보되"],

    # Soccer (K League 1 & 2)
    "포항": ["pohang", "pohang steelers", "포항스틸러스", "포항 스틸러스"],
    "김천": ["gimcheon", "gimcheon sangmu", "gimcheon sangmu fc", "김천상무", "김천 상무"],
    "대전": ["daejeon", "daejeon citizen", "daejeon hana citizen", "대전하나시티즌", "대전 시티즌"],
    "안양": ["anyang", "fc anyang", "안양fc", "fc안양", "fc 안양"],
    "강원": ["gangwon", "gangwon fc", "강원fc", "강원 fc"],
    "전북": ["jeonbuk", "jeonbuk motors", "jeonbuk hyundai", "jeonbuk hyundai motors", "전북현대", "전북 현대"],
    "광주": ["gwangju", "gwangju fc", "광주fc", "광주 fc"],
    "제주": ["jeju", "jeju united", "jeju united fc", "제주유나이티드", "제주 유나이티드"],
    "울산": ["ulsan", "ulsan hyundai", "ulsan hd", "ulsan hd fc", "울산hd", "울산 현대"],
    "서울": ["seoul", "fc seoul", "fc서울", "fc 서울"],
    "인천": ["incheon", "incheon united", "인천유나이티드", "인천 유나이티드"],
    "대구": ["daegu", "daegu fc", "대구fc", "대구 fc"],
    "수원FC": ["suwon fc", "suwon", "수원fc"],
    "수원삼성": ["suwon samsung", "suwon samsung bluewings", "수원", "수원 삼성", "수원블루윙즈"],
    "부산": ["busan", "busan ipark", "부산아이파크", "부산 아이파크"],
    "성남": ["seongnam", "seongnam fc", "성남fc"],
    "부천": ["bucheon", "bucheon 1995", "부천fc"],
    "서울이랜드": ["seoul e-land", "seoul e land", "서울e", "서울 이랜드"],
    "충남아산": ["chungnam asan", "asan", "충남 아산"],
    "경남": ["gyeongnam", "gyeongnam fc", "경남fc"],
    "전남": ["jeonnam", "jeonnam dragons", "전남 드래곤즈"],
    "천안": ["cheonan", "cheonan city", "천안 시티"],
    "충북청주": ["cheongju", "chungbuk cheongju", "충북 청주"],
    "안산": ["ansan", "ansan greeners", "안산 그리너스"],
    "김포": ["gimpo", "gimpo fc", "김포fc"],

    # Soccer (J League)
    "고베": ["vissel kobe", "vissel", "비셀고베", "비셀 고베"],
    "산프레체": ["sanfrecce hiroshima", "sanfrecce", "산프레체 히로시마"],
    "마치다": ["machida zelvia", "machida", "마치다젤비아"],
    "요코하마M": ["yokohama f. marinos", "yokohama fm", "요코하마마리노스", "요코하마 f. 마리노스"],
    "가와사키": ["kawasaki frontale", "kawasaki", "가와사키 프론탈레"],
    "감바오사카": ["gamba osaka", "gamba", "감바 오사카"],
    "세레소오사카": ["cerezo osaka", "cerezo", "세레소 오사카"],
    "우라와": ["urawa red diamonds", "urawa", "우라와 레즈"],
    "나고야": ["nagoya grampus", "nagoya", "나고야 그램퍼스"],
    "가시마": ["kashima antlers", "kashima", "가시마 앤틀러스"],
    "도쿄": ["fc tokyo", "tokyo", "fc 도쿄", "fc도쿄"]
}

def normalize_name(n: str) -> str:
    if not n: return ""
    return str(n).replace(" ", "").replace("·", "").replace(".", "").replace("-", "").replace("/", "").lower()

_CANONICAL_LOOKUP: Dict[str, str] = {}
for _k, _aliases in TEAM_SYNONYMS.items():
    _k_norm = normalize_name(_k)
    _CANONICAL_LOOKUP[_k_norm] = _k
    for _a in _aliases:
        _CANONICAL_LOOKUP[normalize_name(_a)] = _k

def clean_team_tokens(n: str) -> str:
    s = normalize_name(n)
    for stop in ["footballclub", "football", "club", "city", "united", "town", "athletic", "rovers", "wanderers", "hotspur", "albion", "자이언츠", "베어스", "트윈스", "라이온즈", "타이거즈", "이글스", "랜더스", "히어로즈", "다이노스", "위즈", "fc", "cf", "sc", "ac"]:
        if s.endswith(stop) and len(s) > len(stop) + 2:
            s = s[:-len(stop)]
        elif s.startswith(stop) and len(s) > len(stop) + 2:
            s = s[len(stop):]
    return s

def get_canonical(n: str) -> str:
    norm = normalize_name(n)
    if not norm:
        return ""
    if norm in _CANONICAL_LOOKUP:
        return _CANONICAL_LOOKUP[norm]
    for k, canon in _CANONICAL_LOOKUP.items():
        if len(k) >= 3 and (k in norm or norm in k):
            return canon
    return norm

def teams_match(api_name: str, db_name: str) -> bool:
    norm_api = normalize_name(api_name)
    norm_db = normalize_name(db_name)

    if not norm_api or not norm_db:
        return False
    if norm_api == norm_db:
        return True

    # 1. Canonical synonym match
    canon_api = get_canonical(api_name)
    canon_db = get_canonical(db_name)
    if canon_api and canon_db and canon_api == canon_db:
        return True

    # 2. Clean tokens match (e.g. Wolverhampton Wanderers vs Wolverhampton, Brighton & Hove Albion vs Brighton)
    clean_api = clean_team_tokens(api_name)
    clean_db = clean_team_tokens(db_name)
    if clean_api and clean_db:
        if clean_api == clean_db:
            return True
        if len(clean_api) >= 4 and len(clean_db) >= 4:
            if clean_api in clean_db or clean_db in clean_api:
                return True

    # 3. Substring match
    if len(norm_api) >= 3 and len(norm_db) >= 3:
        if norm_api in norm_db or norm_db in norm_api:
            return True

    return False


def parse_utc_to_kst(utc_str: str) -> tuple[Optional[datetime], str]:
    """Convert API-Sports UTC ISO string (e.g. 2026-09-06T18:10:00+00:00) to KST datetime and string"""
    if not utc_str or 'T' not in str(utc_str):
        return None, ''
    try:
        clean_str = str(utc_str).replace('Z', '+00:00')
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is not None:
            kst_tz = timezone(timedelta(hours=9))
            kst_dt = dt.astimezone(kst_tz).replace(tzinfo=None)
        else:
            kst_dt = dt + timedelta(hours=9)
        return kst_dt, kst_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return None, ''


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
    def sync_live_football(cls, date_str: Optional[str] = None, include_adjacent: bool = False) -> Dict[str, Any]:
        """Fetch live & date soccer fixtures and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        now_dt = datetime.utcnow() + timedelta(hours=9)
        d_today = date_str or now_dt.strftime("%Y-%m-%d")
        d_yesterday = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        d_tomorrow = (now_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        # 1. Fetch all live soccer matches
        data_live = cls._make_request("/fixtures?live=all", sport="football")
        fixtures_live = (data_live or {}).get("response", [])

        # 2. Fetch today's soccer matches
        data_today = cls._make_request(f"/fixtures?date={d_today}", sport="football")
        fixtures_today = (data_today or {}).get("response", [])

        fixtures_yesterday = []
        fixtures_tomorrow = []
        if include_adjacent or now_dt.hour < 10:
            # 아침 시간대(10시 이전)에는 새벽에 끝난 어제 유럽 경기 결과 포함
            data_yesterday = cls._make_request(f"/fixtures?date={d_yesterday}", sport="football")
            fixtures_yesterday = (data_yesterday or {}).get("response", [])

        all_fixtures_dict = {}
        for f in (fixtures_today + fixtures_yesterday + fixtures_tomorrow + fixtures_live):
            fid = f.get("fixture", {}).get("id")
            if fid:
                all_fixtures_dict[fid] = f
        all_fixtures = list(all_fixtures_dict.values())

        updated = 0
        db = SessionLocal()
        try:
            # Match against yesterday, today, tomorrow, or ANY match currently marked LIVE
            db_matches = db.query(Match).filter(
                Match.sport_code == "SOCCER",
                or_(
                    Match.status == "LIVE",
                    Match.match_date.like(f"{d_yesterday}%"),
                    Match.match_date.like(f"{d_today}%"),
                    Match.match_date.like(f"{d_tomorrow}%")
                )
            ).all()

            # Auto-resolve stale LIVE matches older than 4.5 hours to FINISHED
            stale_cutoff = (now_dt - timedelta(hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M")
            stale_live = db.query(Match).filter(Match.sport_code == "SOCCER", Match.status == "LIVE", Match.match_date < stale_cutoff).all()
            for sm in stale_live:
                sm.status = "FINISHED"

            db_by_home = defaultdict(list)
            for m in db_matches:
                db_by_home[get_canonical(m.home_team_name)].append(m)

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

                kst_dt, _ = parse_utc_to_kst(fixture_info.get("date", ""))
                canon_h = get_canonical(h_name)
                candidate_matches = db_by_home.get(canon_h, [])
                if not candidate_matches:
                    # 유연한 2차 검색 (동의어 사전 미등록 팀도 teams_match로 전체 DB 매칭)
                    candidate_matches = [m for m in db_matches if teams_match(h_name, m.home_team_name)]

                # Pick the match candidate with the closest scheduled time
                best_match = None
                min_diff = float("inf")
                for m in candidate_matches:
                    if teams_match(a_name, m.away_team_name):
                        if kst_dt and m.match_date:
                            try:
                                db_dt = datetime.strptime(m.match_date[:16], "%Y-%m-%d %H:%M")
                                diff = abs((db_dt - kst_dt).total_seconds())
                                if diff < min_diff and diff <= 12 * 3600:
                                    min_diff = diff
                                    best_match = m
                            except Exception:
                                if not best_match:
                                    best_match = m
                        elif not best_match:
                            best_match = m

                if best_match:
                    best_match.home_score = h_score
                    best_match.away_score = a_score
                    best_match.status = mapped_status

                    # Update periods if detail exists
                    if not best_match.details:
                        best_match.details = MatchDetail(match_id=best_match.id)

                    halftime = score.get("halftime", {})
                    fulltime = score.get("fulltime", {})
                    period_dict = {
                        "1H": f"{halftime.get('home') or 0}-{halftime.get('away') or 0}",
                        "2H": f"{fulltime.get('home') or h_score}-{fulltime.get('away') or a_score}"
                    }
                    best_match.details.period_scores = json.dumps(period_dict)
                    updated += 1
            db.commit()

            # Broadcast real-time update via WebSocket & clear cache if any scores changed
            if updated > 0:
                try:
                    from app.api.v1.matches import clear_matches_cache
                    clear_matches_cache()
                except Exception:
                    pass
                cls._broadcast_live_update("SOCCER", updated)

        except Exception as e:
            logger.error(f"[LiveApiSports] Football sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "total_fixtures": len(all_fixtures), "updated_db_matches": updated}

    @classmethod
    def sync_live_baseball(cls, date_str: Optional[str] = None, include_adjacent: bool = False) -> Dict[str, Any]:
        """Fetch live & date baseball games and update matching matches in DB"""
        if not cls.is_configured():
            return {"status": "SKIPPED", "message": "API Key not configured"}

        now_dt = datetime.utcnow() + timedelta(hours=9)
        d_today = date_str or now_dt.strftime("%Y-%m-%d")
        d_yesterday = (now_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        d_tomorrow = (now_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        # 1. Fetch today's games (includes current live scores & status)
        data_date = cls._make_request(f"/games?date={d_today}", sport="baseball")
        games_date = (data_date or {}).get("response", [])

        games_yesterday = []
        games_tomorrow = []
        if include_adjacent or now_dt.hour < 10:
            # 아침 시간대(10시 이전)에는 새벽에 끝난 어제 미주 경기 결과 포함
            data_yesterday = cls._make_request(f"/games?date={d_yesterday}", sport="baseball")
            games_yesterday = (data_yesterday or {}).get("response", [])

        all_games_dict = {}
        for g in (games_date + games_yesterday + games_tomorrow):
            gid = g.get("id")
            if gid:
                all_games_dict[gid] = g
        all_games = list(all_games_dict.values())

        updated = 0
        db = SessionLocal()
        try:
            db_matches = db.query(Match).filter(
                Match.sport_code == "BASEBALL",
                or_(
                    Match.status == "LIVE",
                    Match.match_date.like(f"{d_yesterday}%"),
                    Match.match_date.like(f"{d_today}%"),
                    Match.match_date.like(f"{d_tomorrow}%")
                )
            ).all()

            # Auto-resolve stale LIVE matches older than 4.5 hours to FINISHED
            stale_cutoff = (now_dt - timedelta(hours=4, minutes=30)).strftime("%Y-%m-%d %H:%M")
            stale_live = db.query(Match).filter(Match.sport_code == "BASEBALL", Match.status == "LIVE", Match.match_date < stale_cutoff).all()
            for sm in stale_live:
                sm.status = "FINISHED"

            db_by_home = defaultdict(list)
            for m in db_matches:
                db_by_home[get_canonical(m.home_team_name)].append(m)

            for g in all_games:
                status_info = g.get("status", {})
                teams = g.get("teams", {})
                scores = g.get("scores", {})

                h_name = teams.get("home", {}).get("name", "")
                a_name = teams.get("away", {}).get("name", "")
                status_short = status_info.get("short", "")

                mapped_status = BASEBALL_STATUS_MAP.get(status_short, "SCHEDULED")
                h_score = scores.get("home", {}).get("total")
                a_score = scores.get("away", {}).get("total")
                if h_score is None:
                    h_score = 0
                if a_score is None:
                    a_score = 0

                kst_dt, _ = parse_utc_to_kst(g.get("date", ""))
                canon_h = get_canonical(h_name)
                candidate_matches = db_by_home.get(canon_h, [])
                if not candidate_matches:
                    # 유연한 2차 검색 (팀명 매칭 폴백)
                    candidate_matches = [m for m in db_matches if teams_match(h_name, m.home_team_name)]

                # Pick the match candidate with the closest scheduled time
                best_match = None
                min_diff = float("inf")
                for m in candidate_matches:
                    if teams_match(a_name, m.away_team_name):
                        if kst_dt and m.match_date:
                            try:
                                db_dt = datetime.strptime(m.match_date[:16], "%Y-%m-%d %H:%M")
                                diff = abs((db_dt - kst_dt).total_seconds())
                                if diff < min_diff and diff <= 12 * 3600:
                                    min_diff = diff
                                    best_match = m
                            except Exception:
                                if not best_match:
                                    best_match = m
                        elif not best_match:
                            best_match = m

                if best_match:
                    best_match.home_score = h_score
                    best_match.away_score = a_score
                    best_match.status = mapped_status

                    # Store baseball inning scores if available
                    innings = scores.get("home", {}).get("innings", {})
                    if innings and not best_match.details:
                        best_match.details = MatchDetail(match_id=best_match.id)
                    if innings and best_match.details:
                        best_match.details.period_scores = json.dumps(innings)

                    updated += 1
            db.commit()

            # Broadcast real-time update via WebSocket & clear cache if any scores changed
            if updated > 0:
                try:
                    from app.api.v1.matches import clear_matches_cache
                    clear_matches_cache()
                except Exception:
                    pass
                cls._broadcast_live_update("BASEBALL", updated)

        except Exception as e:
            logger.error(f"[LiveApiSports] Baseball sync error: {e}")
            db.rollback()
        finally:
            db.close()

        return {"status": "SUCCESS", "total_games": len(all_games), "updated_db_matches": updated}

    @classmethod
    def _broadcast_live_update(cls, sport: str, updated_count: int):
        try:
            from app.core.websocket_manager import manager
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast({
                    "type": "LIVE_SCORE_UPDATE",
                    "timestamp": datetime.now().isoformat(),
                    "sport": sport,
                    "updated_count": updated_count
                }))
            except RuntimeError:
                pass
        except Exception:
            pass

    @classmethod
    def sync_all(cls) -> Dict[str, Any]:
        return {
            "football": cls.sync_live_football(),
            "baseball": cls.sync_live_baseball()
        }

    @classmethod
    async def sync_live_football_async(cls, date_str: Optional[str] = None) -> Dict[str, Any]:
        import asyncio
        return await asyncio.to_thread(cls.sync_live_football, date_str)

    @classmethod
    async def sync_live_baseball_async(cls, date_str: Optional[str] = None) -> Dict[str, Any]:
        import asyncio
        return await asyncio.to_thread(cls.sync_live_baseball, date_str)

    @classmethod
    async def sync_all_async(cls) -> Dict[str, Any]:
        import asyncio
        fb, bb = await asyncio.gather(
            asyncio.to_thread(cls.sync_live_football),
            asyncio.to_thread(cls.sync_live_baseball),
            return_exceptions=True
        )
        return {
            "football": fb if not isinstance(fb, Exception) else {"status": "ERROR", "error": str(fb)},
            "baseball": bb if not isinstance(bb, Exception) else {"status": "ERROR", "error": str(bb)}
        }

    @classmethod
    def get_match_history(cls, match_id: int, max_games: int = 5) -> Dict[str, Any]:
        """
        특정 경기(match_id)에 대해 홈/원정 팀 최근 경기 + 상세 이벤트 반환.
        - 축구: /fixtures/events → 득점자, 경고/퇴장, 어시스트
        - 야구: /games/statistics → 선발, 이닝, 안타, 홈런, 볼넷, 삼진
        - 공통: DB에서 최근 N경기 조회 후 API-Sports external_id로 이벤트 패치
        """
        # 1. DB에서 경기 정보 조회
        from app.core.database import SessionLocal
        from app.models.models import Match
        db = SessionLocal()
        try:
            target = db.query(Match).filter(Match.id == match_id).first()
            if not target:
                return {"status": "error", "message": f"경기 {match_id} 없음"}

            sport_code = target.sport_code
            home_team = target.home_team_name
            away_team = target.away_team_name
            match_date = target.match_date or ''

            # 최근 경기 날짜 범위 (경기일 기준 30일 이내)
            import re
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', match_date)
            base_date = date_match.group(1) if date_match else match_date[:10]

            # 홈팀 최근 경기 (현재 경기 제외)
            home_recent = db.query(Match).filter(
                Match.sport_code == sport_code,
                Match.status == 'FINISHED',
                Match.id != match_id,
                (Match.home_team_name == home_team) | (Match.away_team_name == home_team)
            ).order_by(Match.match_date.desc()).limit(max_games).all()

            # 원정팀 최근 경기 (현재 경기 제외)
            away_recent = db.query(Match).filter(
                Match.sport_code == sport_code,
                Match.status == 'FINISHED',
                Match.id != match_id,
                (Match.home_team_name == away_team) | (Match.away_team_name == away_team)
            ).order_by(Match.match_date.desc()).limit(max_games).all()

        finally:
            db.close()

        def format_match_basic(m: Match, perspective_team: str) -> Dict[str, Any]:
            """경기 기본 정보 포맷"""
            is_home = (m.home_team_name == perspective_team)
            opponent = m.away_team_name if is_home else m.home_team_name
            team_score = m.home_score if is_home else m.away_score
            opp_score = m.away_score if is_home else m.home_score
            if team_score > opp_score:
                result = 'WIN'
                result_emoji = '✅'
            elif team_score < opp_score:
                result = 'LOSS'
                result_emoji = '❌'
            else:
                result = 'DRAW'
                result_emoji = '🟰'

            date_str = (m.match_date or '')[:10]
            home_away = '홈' if is_home else '원정'

            # 선발 정보 (야구)
            starter_info = ''
            if sport_code == 'BASEBALL':
                if is_home and m.details and hasattr(m, 'home_starter_name'):
                    starter_info = getattr(m, 'home_starter_name', '') or ''
                elif not is_home and hasattr(m, 'away_starter_name'):
                    starter_info = getattr(m, 'away_starter_name', '') or ''

            return {
                'match_id': m.id,
                'date': date_str,
                'home_away': home_away,
                'opponent': opponent,
                'score': f'{team_score} - {opp_score}',
                'result': result,
                'result_emoji': result_emoji,
                'starter': starter_info,
                'events': [],  # API-Sports 이벤트는 별도 패치
                'stats': {}
            }

        home_games = [format_match_basic(m, home_team) for m in home_recent]
        away_games = [format_match_basic(m, away_team) for m in away_recent]

        # 2. API-Sports로 이벤트/통계 패치 (키 설정되어 있는 경우만)
        if cls.is_configured():
            if sport_code == 'SOCCER':
                home_games = cls._enrich_football_events(home_games, home_team, home_recent)
                away_games = cls._enrich_football_events(away_games, away_team, away_recent)
            elif sport_code == 'BASEBALL':
                home_games = cls._enrich_baseball_stats(home_games, home_team, home_recent)
                away_games = cls._enrich_baseball_stats(away_games, away_team, away_recent)

        return {
            'status': 'success',
            'match_id': match_id,
            'sport_code': sport_code,
            'home_team': home_team,
            'away_team': away_team,
            'home_recent': home_games,
            'away_recent': away_games
        }

    @classmethod
    def _enrich_football_events(cls, games: list, team_name: str, db_matches: list) -> list:
        """
        축구 경기 이벤트 패치: /fixtures/events?fixture={id}
        득점자(시간/이름/어시스트), 경고/퇴장 파싱
        """
        for i, (game, db_match) in enumerate(zip(games, db_matches)):
            try:
                # official_id가 있으면 API-Sports fixture ID로 사용
                ext_id = getattr(db_match, 'official_id', None)
                if not ext_id:
                    continue

                # fixture ID가 숫자형인지 확인
                try:
                    int(ext_id)
                except (ValueError, TypeError):
                    continue

                data = cls._make_request(f"/fixtures/events?fixture={ext_id}", sport="football")
                if not data:
                    continue
                events_raw = data.get('response', [])

                goals = []
                cards = []
                for ev in events_raw:
                    ev_type = ev.get('type', '')
                    ev_detail = ev.get('detail', '')
                    ev_time = ev.get('time', {}).get('elapsed', '')
                    player_name = ev.get('player', {}).get('name', '')
                    assist_name = ev.get('assist', {}).get('name', '')
                    team_ev_name = ev.get('team', {}).get('name', '')
                    is_own_team = teams_match(team_ev_name, team_name)

                    if ev_type == 'Goal' and ev_detail != 'Missed Penalty':
                        side = '' if is_own_team else '(실점)'
                        assist_str = f' ({assist_name} 어시스트)' if assist_name else ''
                        goals.append(f"⚽ {ev_time}'{side} {player_name}{assist_str}")
                    elif ev_type == 'Card':
                        is_yellow = 'Yellow' in ev_detail
                        is_red = 'Red' in ev_detail
                        card_emoji = '🟡' if is_yellow else '🔴'
                        side = '' if is_own_team else '(상대)'
                        cards.append(f"{card_emoji} {ev_time}' {player_name}{side}")

                game['events'] = goals + cards
                games[i] = game
            except Exception:
                continue
        return games

    @classmethod
    def _enrich_baseball_stats(cls, games: list, team_name: str, db_matches: list) -> list:
        """
        야구 경기 통계 패치: /games/statistics?id={id}
        선발투수 이닝/볼넷/삼진, 팀 안타/홈런 파싱
        """
        for i, (game, db_match) in enumerate(zip(games, db_matches)):
            try:
                ext_id = getattr(db_match, 'official_id', None)
                if not ext_id:
                    # official_id 없으면 DB details에서 period_scores 사용
                    if db_match.details and db_match.details.team_stats:
                        try:
                            stats = json.loads(db_match.details.team_stats or '{}')
                            if stats:
                                game['stats'] = stats
                        except Exception:
                            pass
                    continue

                try:
                    int(ext_id)
                except (ValueError, TypeError):
                    continue

                data = cls._make_request(f"/games/statistics?id={ext_id}", sport="baseball")
                if not data:
                    continue
                stats_raw = data.get('response', [])

                for team_stat in stats_raw:
                    team_ev_name = team_stat.get('team', {}).get('name', '')
                    if not teams_match(team_ev_name, team_name):
                        continue
                    batting = team_stat.get('statistics', {}).get('batting', {})
                    pitching = team_stat.get('statistics', {}).get('pitching', {})
                    game['stats'] = {
                        'hits': batting.get('hits', 0),
                        'home_runs': batting.get('homeRuns', 0),
                        'walks': batting.get('baseOnBalls', 0),
                        'strikeouts_bat': batting.get('strikeOuts', 0),
                        'starter_ip': pitching.get('inningsPitched', ''),
                        'starter_er': pitching.get('earnedRuns', 0),
                        'starter_bb': pitching.get('baseOnBalls', 0),
                        'starter_k': pitching.get('strikeOuts', 0),
                    }
                    break
                games[i] = game
            except Exception:
                continue
        return games

