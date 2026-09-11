# -*- coding: utf-8 -*-
import requests
import json
import time
import os
import sqlite3
import re
from datetime import datetime, timezone, timedelta
from functools import lru_cache

BETMAN_TOTO_URL = 'https://www.betman.co.kr/buyPsblGame/totoGameData.do'
BETMAN_BUYABLE_URL = 'https://www.betman.co.kr/buyPsblGame/inqCacheBuyAbleGameInfoList.do'
BETMAN_INQ_URL = 'https://www.betman.co.kr/buyPsblGame/gameInfoInq.do'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.betman.co.kr/main/mainPage/gamebuy/gameSlip.do?gmId=G101'
}

_SESSION = requests.Session()
_SESSION.headers.update(HEADERS)

_CACHE = {}
CACHE_TTL = 300 # 5 minutes cache for real-time responsiveness

def format_kr_money(amount: int) -> str:
    """Format Korean won amount into readable eok/man string (e.g., 2억 8,249만 원)"""
    if not amount or amount <= 0:
        return "0원"
    eok = amount // 100_000_000
    man = (amount % 100_000_000) // 10_000
    if eok > 0 and man > 0:
        return f"{eok}억 {man:,}만 원"
    elif eok > 0:
        return f"{eok}억 원"
    else:
        return f"{man:,}만 원"


TEAM_SYNONYMS = {
    # Baseball (MLB) - 30 Teams with full names, abbreviations & English
    "다저스": ["dodgers", "los angeles dodgers", "la dodgers", "la다저스", "l다저스", "다저스"],
    "에인절스": ["angels", "los angeles angels", "la angels", "la에인절스", "la에인절", "l에인절", "에인절스"],
    "파드리스": ["padres", "san diego padres", "샌디에이고", "샌디에이고 파드리스", "샌디파드", "샌디에고", "파드리스"],
    "자이언츠": ["giants", "san francisco giants", "sf giants", "샌프란시스코", "샌프란시스코 자이언츠", "샌프자이", "자이언츠"],
    "양키스": ["yankees", "new york yankees", "ny yankees", "뉴욕양키스", "뉴욕 양키스", "뉴욕양키", "양키스"],
    "메츠": ["mets", "new york mets", "ny mets", "뉴욕메츠", "뉴욕 메츠", "메츠"],
    "레드삭스": ["red sox", "boston red sox", "보스턴", "보스턴 레드삭스", "보스레드", "레드삭스"],
    "오리올스": ["orioles", "baltimore orioles", "볼티모어", "볼티모어 오리올스", "볼티오리", "볼티모어 오리올즈", "오리올스", "오리올즈"],
    "블루제이스": ["blue jays", "toronto blue jays", "토론토", "토론토 블루제이스", "토론블루", "블루제이스"],
    "레이스": ["rays", "tampa bay rays", "탬파베이", "탬파베이 레이스", "탬파레이", "템파베이", "템파레이", "레이스"],
    "화이트삭스": ["white sox", "chicago white sox", "시카고화이트삭스", "시카고 화이트삭스", "시카화이", "시카고화이", "화이트삭스"],
    "가디언스": ["guardians", "cleveland guardians", "클리블랜드", "클리블랜드 가디언스", "클리블랜드 가디언즈", "클리가디", "클리블랜", "가디언스", "가디언즈"],
    "타이거스": ["tigers", "detroit tigers", "디트로이트", "디트로이트 타이거스", "디트로이트 타이거즈", "디트로타", "타이거스", "타이거즈"],
    "로열스": ["royals", "kansas city royals", "캔자스시티", "캔자스시티 로얄스", "캔자스시티 로열스", "캔자로열", "캔자로얄", "로열스", "로얄스"],
    "트윈스": ["twins", "minnesota twins", "미네소타", "미네소타 트윈스", "미네트윈", "트윈스"],
    "애스트로스": ["astros", "houston astros", "휴스턴", "휴스턴 애스트로스", "휴스애스", "애스트로스"],
    "애슬레틱스": ["athletics", "oakland athletics", "오클랜드", "오클랜드 애슬레틱스", "오클애슬", "오클랜드 애슬레틱", "애슬레틱스", "애슬레틱"],
    "매리너스": ["mariners", "seattle mariners", "시애틀", "시애틀 매리너스", "시애매리", "매리너스"],
    "레인저스": ["rangers", "texas rangers", "텍사스", "텍사스 레인저스", "텍사레인", "텍사스 레인져스", "레인저스", "레인져스"],
    "브레이브스": ["braves", "atlanta braves", "애틀랜타", "애틀랜타 브레이브스", "애틀브레", "애틀란타", "애틀란타 브레이브스", "브레이브스", "브레이브즈"],
    "말린스": ["marlins", "miami marlins", "마이애미", "마이애미 말린스", "마이말린", "말린스"],
    "필리스": ["phillies", "philadelphia phillies", "필라델피아", "필라델피아 필리스", "필라필리", "필리스"],
    "내셔널스": ["nationals", "washington nationals", "워싱턴", "워싱턴 내셔널스", "워싱내셔", "내셔널스"],
    "컵스": ["cubs", "chicago cubs", "시카고컵스", "시카고 컵스", "시카컵스", "컵스"],
    "레즈": ["reds", "cincinnati reds", "신시내티", "신시내티 레즈", "신시레즈", "신시네티", "레즈"],
    "브루어스": ["brewers", "milwaukee brewers", "밀워키", "밀워키 브루어스", "밀워브루", "밀워키 브루어즈", "브루어스", "브루어즈"],
    "파이리츠": ["pirates", "pittsburgh pirates", "피츠버그", "피츠버그 파이리츠", "피츠버그 파이어리츠", "피츠파이", "파이리츠", "파이어리츠"],
    "카디널스": ["cardinals", "st louis cardinals", "세인트루이스", "세인트루이스 카디널스", "세인카디", "세인트루이스 카디널즈", "카디널스", "카디널즈"],
    "다이아몬드백스": ["diamondbacks", "arizona diamondbacks", "d-backs", "애리조나", "애리조나 다이아몬드백스", "애리디백", "디백스", "다이아몬드백스"],
    "로키스": ["rockies", "colorado rockies", "콜로라도", "콜로라도 로키스", "콜로로키", "로키스"],

    # Baseball (KBO) - 10 Teams
    "LG": ["lg", "lg트윈스", "lg 트윈스", "엘지"],
    "KIA": ["kia", "기아", "kia타이거즈", "kia 타이거즈", "기아 타이거즈"],
    "삼성": ["삼성", "삼성라이온즈", "삼성 라이온즈"],
    "두산": ["두산", "두산베어스", "두산 베어스"],
    "KT": ["kt", "kt위즈", "kt 위즈", "케이티"],
    "SSG": ["ssg", "ssg랜더스", "ssg 랜더스", "에스에스지", "랜더스"],
    "NC": ["nc", "nc다이노스", "nc 다이노스", "엔씨"],
    "한화": ["한화", "한화이글스", "한화 이글스"],
    "롯데": ["롯데", "롯데자이언츠", "롯데 자이언츠"],
    "키움": ["키움", "키움히어로즈", "키움 히어로즈"],

    # Baseball (NPB) - 12 Teams
    "요미우리": ["요미우리", "요미우리 자이언츠", "요미우리자이언츠", "자이언츠", "요미"],
    "야쿠르트": ["야쿠르트", "야쿠르트 스왈로스", "야쿠르트스왈로스", "도쿄야쿠르트"],
    "요코하마": ["요코하마", "요코하마 dena베이스타스", "요코하마 dena", "dena", "베이스타스", "요코하마 dena베이스타즈"],
    "히로시마": ["히로시마", "히로시마 도요카프", "히로시마도요카프", "도요카프", "카프"],
    "한신": ["한신", "한신 타이거스", "한신타이거스", "한신타이거즈", "한신 타이거즈"],
    "주니치": ["주니치", "주니치 드래건스", "주니치드래건스", "주니치드래곤즈", "주니치 드래곤즈"],
    "닛폰햄": ["닛폰햄", "닛폰햄 파이터스", "닛폰햄파이터스", "파이터스", "홋카이도닛폰햄"],
    "라쿠텐": ["라쿠텐", "라쿠텐 골든이글스", "라쿠텐골든이글스", "도호쿠라쿠텐"],
    "세이부": ["세이부", "세이부 라이온즈", "세이부라이온즈", "사이타마세이부"],
    "소프트뱅크": ["소프트뱅크", "소프트뱅크 호크스", "소프트뱅크호크스", "후쿠오카소프트뱅크", "소뱅"],
    "지바롯데": ["지바롯데", "지바롯데 마린스", "지바롯데마린스", "마린스"],
    "오릭스": ["오릭스", "오릭스 버팔로스", "오릭스버팔로스", "버팔로스", "오릭스 버팔로즈"],

    # Soccer (EPL)
    "토트넘": ["tottenham", "tottenham hotspur", "spurs", "토트넘 홋스퍼", "토트넘"],
    "맨체스c": ["manchester city", "man city", "man city fc", "맨체스터 시티", "맨시티"],
    "맨체스u": ["manchester united", "manchester utd", "man utd", "맨유", "맨체스터 유나이티드"],
    "아스널": ["arsenal", "아스날"],
    "첼시": ["chelsea"],
    "리버풀": ["liverpool"],
    "a빌라": ["aston villa", "villa", "아스톤빌라", "아스톤v", "애스턴빌라", "애스턴 빌라", "아스톤 빌라"],
    "뉴캐슬": ["newcastle", "newcastle united", "뉴캐슬 유나이티드"],
    "브라이턴": ["brighton", "brighton & hove albion", "brighton and hove albion", "브라이튼", "브라이턴&호브 앨비언"],
    "브렌트퍼": ["brentford", "브렌트포드", "브렌트퍼드"],
    "크리스탈": ["crystal palace", "palace", "크리스털", "크리스탈팰리스", "크리스털 팰리스", "크리스탈 팰리스"],
    "풀럼": ["fulham"],
    "웨스트햄": ["west ham", "west ham united", "웨스트햄 유나이티드"],
    "에버턴": ["everton", "에버튼"],
    "울버햄튼": ["wolverhampton", "wolves", "울버햄프턴", "울버햄튼 원더러스"],
    "본머스": ["bournemouth", "afc bournemouth", "afc본머스"],
    "노팅엄f": ["nottingham", "nottingham forest", "노팅엄", "노팅엄 포레스트", "노팅엄 포리스트", "노팅엄F"],
    "레스터": ["leicester", "leicester city", "레스터 시티"],
    "사우샘프": ["southampton", "사우샘프턴", "사우스햄튼"],
    "입스위치": ["ipswich", "ipswich town", "입스위치 타운"],
    "선덜랜드": ["sunderland"],
    "리즈u": ["leeds", "leeds united", "리즈", "리즈 유나이티드"],
    "코번트리": ["coventry", "coventry city", "코번트리 시티"],
    "헐시티": ["hull", "hull city", "헐 시티"],

    # Soccer (La Liga)
    "레알마드": ["real madrid", "레알 마드리드", "레알마드리드"],
    "바르셀로": ["barcelona", "바르셀로나", "바르샤"],
    "at마드": ["atletico madrid", "atletico", "아틀레티코", "아틀레티코 마드리드", "at마드리드"],
    "소시에다": ["real sociedad", "sociedad", "레알 소시에다드", "소시에다드"],
    "a빌바오": ["athletic bilbao", "athletic club", "아틀레틱 빌바오", "빌바오"],
    "오사수나": ["osasuna", "ca osasuna"],
    "에스파뇰": ["espanyol", "rcd espanyol", "에스파뇰"],
    "셀타비고": ["celta vigo", "celta", "셀타 비고", "셀타"],
    "말라가": ["malaga", "malaga cf"],
    "레반테": ["levante", "levante ud"],
    "헤타페": ["getafe", "getafe cf"],
    "데포아코": ["deportivo la coruna", "deportivo", "데포르티보"],
    "엘체": ["elche", "elche cf"],
    "비야레알": ["villarreal", "비야레알 cf"],
    "발렌시아": ["valencia", "valencia cf"],
    "베티스": ["real betis", "betis", "레알 베티스"],
    "세비야": ["sevilla", "sevilla fc"],

    # Soccer (UCL / Europe / World)
    "바이에른": ["bayern munich", "bayern", "바이에른 뮌헨", "바이에른"],
    "도르트문트": ["borussia dortmund", "dortmund", "보루시아 도르트문트"],
    "라이프치히": ["rb leipzig", "leipzig", "rb라이프치히"],
    "레버쿠젠": ["bayer leverkusen", "leverkusen", "바이어 레버쿠젠", "바이어04 레버쿠젠"],
    "psv": ["psv eindhoven", "psv", "psv에인트호번"],
    "페예노르트": ["feyenoord", "페예노르트 로테르담"],
    "아약스": ["ajax", "afc ajax", "afc아약스"],
    "페네르바체": ["fenerbahce", "페네르바체 sk"],
    "갈라타사라이": ["galatasaray", "갈라타사라이 sk"],
    "로마": ["as roma", "roma", "as 로마"],
    "라치오": ["lazio", "ss lazio", "ss 라치오"],
    "유벤투스": ["juventus", "유베"],
    "인테르": ["inter milan", "inter", "인터 밀란", "인테르나치오날레"],
    "ac밀란": ["ac milan", "milan", "ac 밀란"],
    "나폴리": ["napoli", "ssc napoli", "ssc 나폴리"],
    "파리생제": ["psg", "paris saint-germain", "파리 생제르맹", "파리생제르맹"],
    "플라멩구": ["flamengo", "cr flamengo", "cr플라멩구", "cr 플라멩구", "플라멩고", "플라멩구 rj"],
    "인디델바": ["independiente del valle", "인디펜디엔테 델바예", "인디펜디엔테 델 바예", "인디펜디엔테델바예", "델 바예", "델바예", "인디델바"],

    # Soccer (K League)
    "충남아산": ["충남아산", "충남아산 프로축구단", "충남아산fc"],
    "안산": ["안산", "안산 그리너스", "안산그리너스", "안산fc"],
    "김포": ["김포", "김포fc", "김포 fc"],
    "충북청주": ["충북청주", "충북청주 프로축구단", "충북청주fc"],
    "경남": ["경남", "경남fc", "경남 fc"],
    "대구": ["대구", "대구fc", "대구 fc"],
    "화성": ["화성", "화성fc", "화성 fc"],
    "서울이랜드": ["서울이랜드", "서울 이랜드", "서울이랜드fc"],
    "수원삼성": ["수원 삼성", "수원 삼성블루윙즈", "수원삼성"],
    "수원fc": ["수원fc", "수원 fc"],
    "김해": ["김해", "김해fc", "김해시청"],
    "용인": ["용인", "용인fc", "용인시축구센터"],
    "부산": ["부산", "부산 아이파크", "부산아이파크"],
    "전남": ["전남", "전남 드래곤즈", "전남드래곤즈"],
    "성남": ["성남", "성남fc", "성남 fc"],
    "천안": ["천안", "천안 시티", "천안시티fc", "천안시티"],
    "울산": ["울산", "울산 hd", "울산 현대"],
    "전북": ["전북", "전북 현대", "전북 현대모터스"],
    "포항": ["포항", "포항 스틸러스"],
    "인천": ["인천", "인천 유나이티드"],
    "서울": ["fc서울", "fc 서울", "서울"],
    "강원": ["강원", "강원fc", "강원 fc"],
    "광주": ["광주", "광주fc", "광주 fc"],
    "제주": ["제주", "제주 유나이티드", "제주 skfc", "제주skfc"],
    "대전": ["대전", "대전 하나시티즌", "대전하나시티즌"]
}

@lru_cache(maxsize=4096)
def clean_name(n):
    if not n: return ''
    return str(n).replace(' ', '').replace('·', '').replace('.', '').replace('-', '').replace('/', '').replace('&', '').lower()

# Pre-compile cleaned synonym groups once at module load
_PRECOMPUTED_SYNONYM_GROUPS = [
    tuple([clean_name(k)] + [clean_name(a) for a in aliases])
    for k, aliases in TEAM_SYNONYMS.items()
]

def get_canonical_team_key(team_name: str) -> str:
    """팀명을 대표 정규 키로 변환"""
    if not team_name:
        return ""
    c = clean_name(team_name)
    if not c:
        return ""
    for grp in _PRECOMPUTED_SYNONYM_GROUPS:
        if any(g == c or (len(g) >= 3 and (g in c or c in g)) for g in grp):
            return grp[0]
    return c

def teams_match(api_name: str, db_name: str) -> bool:
    norm_api = clean_name(api_name)
    norm_db = clean_name(db_name)

    if not norm_api or not norm_db:
        return False
    if norm_api == norm_db or norm_api in norm_db or norm_db in norm_api:
        return True

    for grp in _PRECOMPUTED_SYNONYM_GROUPS:
        if not any(g in norm_api or norm_api in g for g in grp):
            continue
        if any(g in norm_db or norm_db in g for g in grp):
            return True

    return False

def compute_name_similarity(betman_team, db_team):
    if teams_match(betman_team, db_team):
        return 100
    b = clean_name(betman_team)
    d = clean_name(db_team)
    if not b or not d: return 0
    if b in d or d in b:
        return 100
    if len(b) >= 2 and b[:2] in d:
        return 80
    if len(b) >= 4 and b[2:4] in d:
        return 70
    return 0


class BetmanService:

    @staticmethod
    def get_active_rounds_map(force_refresh: bool = False) -> dict:
        """베트맨 공식 서버에서 현재 발매 중인 모든 토토/프로토 게임의 최신 회차(gmTs) 자동 조회"""
        now = time.time()
        cache_key = 'active_rounds_map'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        res_map = {'toto': {}, 'proto': {}}
        try:
            payload = {'_sbmInfo': {'_sbmInfo': {'debugMode': 'false'}}}
            r = _SESSION.post(BETMAN_BUYABLE_URL, json=payload, timeout=4.0)
            if r.status_code == 200:
                data = r.json()
                for tg in data.get('totoGames', []):
                    gid = tg.get('gmId')
                    ts = tg.get('gmTs')
                    if gid and ts:
                        if gid not in res_map['toto'] or ts > res_map['toto'][gid].get('gmTs', 0):
                            res_map['toto'][gid] = tg

                for pg in data.get('protoGames', []):
                    gid = pg.get('gmId')
                    ts = pg.get('gmTs')
                    if gid and ts:
                        if gid not in res_map['proto'] or ts > res_map['proto'][gid].get('gmTs', 0):
                            res_map['proto'][gid] = pg

                if res_map['toto'] or res_map['proto']:
                    _CACHE[cache_key] = (now, res_map)
                    return res_map
        except Exception as e:
            print(f"[WARN] BetmanService get_active_rounds_map error: {e}")

        # Default fallbacks if network fails
        res_map = {
            'toto': {
                'G011': {'gmId': 'G011', 'gmTs': 260052, 'gmOsidTsYear': 2026, 'gameName': '축구토토 승무패'},
                'G024': {'gmId': 'G024', 'gmTs': 260068, 'gmOsidTsYear': 2026, 'gameName': '야구토토 승1패'},
                'G027': {'gmId': 'G027', 'gmTs': 260028, 'gmOsidTsYear': 2026, 'gameName': '농구토토 승5패'}
            },
            'proto': {
                'G101': {'gmId': 'G101', 'gmTs': 260093, 'gmOsidTsYear': 2026, 'gameName': '프로토 승부식'}
            }
        }
        return res_map

    @staticmethod
    def get_active_round_ts(gm_id: str) -> int:
        """특정 게임(G011, G024, G101 등)의 최신 활성 회차 번호 반환"""
        rounds_map = BetmanService.get_active_rounds_map()
        if gm_id in rounds_map.get('toto', {}):
            return rounds_map['toto'][gm_id].get('gmTs')
        if gm_id in rounds_map.get('proto', {}):
            return rounds_map['proto'][gm_id].get('gmTs')
        if gm_id == 'G011': return 260052
        if gm_id == 'G024': return 260068
        if gm_id == 'G101': return 260093
        return 260001

    @staticmethod
    def get_live_toto_summary(force_refresh: bool = False) -> dict:
        """Fetch real-time sales, prize pools, and rollover status across active Betman Toto games"""
        now = time.time()
        cache_key = 'live_toto_summary'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        summary = {
            'status': 'success',
            'updated_at': datetime.now().strftime("%H:%M:%S"),
            'games': {}
        }
        try:
            payload = {'_sbmInfo': {'_sbmInfo': {'debugMode': 'false'}}}
            r = _SESSION.post(BETMAN_BUYABLE_URL, json=payload, timeout=4.0)
            if r.status_code == 200:
                res = r.json()
                for g in res.get('totoGames', []):
                    gid = g.get('gmId')
                    if gid in ['G011', 'G024', 'G027']:
                        sport_label = '야구 승1패' if gid == 'G024' else ('축구 승무패' if gid == 'G011' else '농구 승5패')
                        ts = g.get('gmTs')
                        s_amt = int(g.get('totalSellAmount') or 0)
                        f_amt = int(g.get('forwardAmount') or 0)
                        w_prize = int(g.get('winnerTotalPrize') or int(s_amt * 0.25))
                        f_pool = f_amt + w_prize

                        summary['games'][gid] = {
                            'gmId': gid,
                            'sport': sport_label,
                            'gmTs': ts,
                            'round_no': str(ts)[-2:],
                            'title': f"{sport_label} {str(ts)[-2:]}회차",
                            'total_sell_amount': s_amt,
                            'total_sale_cnt': int(g.get('totalSaleCnt') or (s_amt // 1000)),
                            'forward_amount': f_amt,
                            'forward_cnt': g.get('forwardCnt', 0),
                            'first_prize_pool': f_pool,
                            'first_prize_text': format_kr_money(f_pool),
                            'total_sell_text': format_kr_money(s_amt),
                            'forward_text': format_kr_money(f_amt) if f_amt > 0 else '이월 없음',
                            'status': 'SaleProgress' if s_amt > 0 else 'SaleComplete',
                            'is_live': True
                        }

                if summary['games']:
                    _CACHE[cache_key] = (now, summary)
                    return summary
        except Exception as e:
            print(f"[WARN] Failed to fetch live toto summary: {e}")

        # Fallback default live summary
        for gid in ['G011', 'G024', 'G027']:
            fts = BetmanService.get_active_round_ts(gid)
            summary['games'][gid] = {
                'gmId': gid,
                'sport': '야구 승1패' if gid == 'G024' else ('축구 승무패' if gid == 'G011' else '농구 승5패'),
                'gmTs': fts,
                'round_no': str(fts)[-2:],
                'title': f"{'야구 승1패' if gid == 'G024' else ('축구 승무패' if gid == 'G011' else '농구 승5패')} {str(fts)[-2:]}회차",
                'total_sell_amount': 0,
                'total_sale_cnt': 0,
                'forward_amount': 0,
                'forward_cnt': 0,
                'first_prize_pool': 0,
                'first_prize_text': '0원',
                'total_sell_text': '0원',
                'forward_text': '이월 없음',
                'status': 'SaleProgress',
                'is_live': True
            }

        _CACHE[cache_key] = (now, summary)
        return summary

    @staticmethod
    def get_round_data(gm_id: str = 'G011', gm_ts: int = None, force_refresh: bool = False) -> dict:
        """베트맨 특정 토토 게임(축구 승무패 G011, 야구 승1패 G024, 농구 승5패 G027) 14경기 공식 실시간 데이터 조회"""
        now = time.time()
        # Resolve active round dynamically if not provided
        if not gm_ts:
            gm_ts = BetmanService.get_active_round_ts(gm_id)

        cache_key = f'{gm_id}_{gm_ts}'

        # 1. In-memory cache check
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        # 2. Live API fetch with requests (Reliable & fast)
        try:
            params = {
                'gmId': gm_id,
                'gmTs': int(gm_ts),
                '_sbmInfo': {
                    '_sbmInfo': {
                        'debugMode': 'false'
                    }
                }
            }
            r = _SESSION.post(BETMAN_TOTO_URL, json=params, timeout=4.0)
            if r.status_code == 200:
                res = r.json()
                if isinstance(res, dict) and (res.get('schedulesList') or res.get('currentLottery')):
                    parsed = BetmanService._parse_betman_payload(res, gm_id, gm_ts)
                    if parsed and parsed.get('status') == 'success':
                        _CACHE[cache_key] = (now, parsed)
                        # Save local snapshot for fast offline recovery
                        try:
                            with open(f'betman_{gm_id}_{gm_ts}.json', 'w', encoding='utf-8') as sf:
                                json.dump(parsed, sf, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                        return parsed
        except Exception as e:
            print(f"[WARN] Betman totoGameData live fetch error ({gm_id} {gm_ts}): {e}")

        # 3. Fallback snapshot
        for snap_file in [f'betman_{gm_id}_{gm_ts}.json', f'betman_{gm_ts}.json']:
            if os.path.exists(snap_file):
                try:
                    with open(snap_file, 'r', encoding='utf-8') as f:
                        snap_data = json.load(f)
                        _CACHE[cache_key] = (now, snap_data)
                        return snap_data
                except Exception:
                    pass

        return {'status': 'error', 'message': f'베트맨 {gm_id} {gm_ts}회차 데이터를 불러올 수 없습니다.'}

    @staticmethod
    def get_proto_odds(force_refresh: bool = False) -> dict:
        """베트맨 프로토 승부식(G101) 최신 회차의 전체 700~1100개 배당 및 투표율 일괄 수집 (스냅샷 즉시 로드 + 실시간 백그라운드 갱신)"""
        now = time.time()
        active_ts = 260093
        try:
            active_ts = BetmanService.get_active_round_ts('G101')
        except Exception:
            active_ts = 260093

        cache_key = f'proto_G101_{active_ts}'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        # 1. 스냅샷 파일이 있으면 즉시 메모리 캐시에 적재 (0ms)
        snapshot_data = None
        for s_file in ['betman_proto_G101_latest.json', f'betman_proto_G101_{active_ts}.json', 'betman_G101.json']:
            if os.path.exists(s_file):
                try:
                    with open(s_file, 'r', encoding='utf-8') as f:
                        snapshot_data = json.load(f)
                        if snapshot_data and snapshot_data.get('datas'):
                            break
                except Exception:
                    pass

        # 2. 실시간 라이브 페칭 시도 (짧은 2.5초 타임아웃으로 블로킹 방지)
        try:
            payload = {
                "gmId": "G101",
                "gmTs": active_ts,
                "gameYear": "2026",
                "_sbmInfo": {"_sbmInfo": {"debugMode": "false"}}
            }
            r = _SESSION.post(BETMAN_INQ_URL, json=payload, timeout=2.5)
            if r.status_code == 200:
                data = r.json()
                keys = data.get('compSchedules', {}).get('keys', [])
                datas = data.get('compSchedules', {}).get('datas', [])
                vote_dict = {v.get('GM_SEQ'): v for v in data.get('voteStatus', [])}

                if datas:
                    parsed_result = {
                        'gmTs': active_ts,
                        'total_lines': len(datas),
                        'keys': keys,
                        'datas': datas,
                        'votes': vote_dict
                    }
                    _CACHE[cache_key] = (now, parsed_result)
                    try:
                        with open('betman_proto_G101_latest.json', 'w', encoding='utf-8') as sf:
                            json.dump(parsed_result, sf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    return parsed_result
        except Exception as e:
            pass

        # 3. 네트워크 실패 시 스냅샷 데이터 반환
        if snapshot_data and snapshot_data.get('datas'):
            _CACHE[cache_key] = (now, snapshot_data)
            return snapshot_data

        return {'gmTs': active_ts, 'total_lines': 0, 'keys': [], 'datas': [], 'votes': {}}

    @staticmethod
    def get_indexed_proto_matches(force_refresh: bool = False) -> dict:
        """
        베트맨 프로토 G101 전체 배당 데이터를 경기 단위(홈팀, 원정팀)로 완벽하게 인덱싱 및 메인 배당 계산
        """
        now = time.time()
        cache_key = 'indexed_proto_matches'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < 60: # 1분 캐시
                return data

        proto_data = BetmanService.get_proto_odds(force_refresh=force_refresh)
        keys = proto_data.get('keys', [])
        datas = proto_data.get('datas', [])
        vote_dict = proto_data.get('votes', {})

        indexed = {}
        for r in datas:
            d = dict(zip(keys, r))
            h_raw = d.get('homeName', '').strip()
            a_raw = d.get('awayName', '').strip()
            if not h_raw or not a_raw or h_raw == '미정' or a_raw == '미정':
                continue

            w_allot = float(d.get('winAllot') or 0.0)
            d_allot = float(d.get('drawAllot') or 0.0)
            l_allot = float(d.get('loseAllot') or 0.0)

            # 발매 전 0.0 더미 배당 제외
            if w_allot <= 0.0 and l_allot <= 0.0:
                continue

            h_norm = clean_name(h_raw)
            a_norm = clean_name(a_raw)
            sp = d.get('itemCode', 'BS')
            seq = d.get('matchSeq')
            handi_val = d.get('winHandi') if d.get('winHandi') is not None else d.get('handi')

            v = vote_dict.get(seq, {})
            tot = v.get('W_BET_CNT', 0) + v.get('D_BET_CNT', 0) + v.get('L_BET_CNT', 0)
            w_pct = round(v.get('W_BET_CNT', 0) / tot * 100, 1) if tot else 0.0
            l_pct = round(v.get('L_BET_CNT', 0) / tot * 100, 1) if tot else 0.0
            d_pct = round(v.get('D_BET_CNT', 0) / tot * 100, 1) if tot else 0.0

            odd_item = {
                'seq': seq,
                'type': d.get('betTypNm', '일반 승패'),
                'handicap': str(handi_val) if handi_val not in (None, '', 0, 0.0) else '',
                'uo': str(handi_val) if handi_val not in (None, '', 0, 0.0) else '',
                'home_odds': w_allot,
                'draw_odds': d_allot,
                'away_odds': l_allot,
                'win_vote_pct': f"{w_pct}%",
                'draw_vote_pct': f"{d_pct}%",
                'loss_vote_pct': f"{l_pct}%",
                'win_votes': v.get('W_BET_CNT', 0),
                'draw_votes': v.get('D_BET_CNT', 0),
                'loss_votes': v.get('L_BET_CNT', 0),
                'total_votes': tot
            }

            key = (h_norm, a_norm)
            if key not in indexed:
                sport_name = 'BASEBALL' if sp == 'BS' else ('SOCCER' if sp == 'SC' else ('BASKETBALL' if sp == 'BK' else 'VOLLEYBALL'))
                indexed[key] = {
                    'home_name': h_raw,
                    'away_name': a_raw,
                    'sport_code': sport_name,
                    'league_name': d.get('leagueName', ''),
                    'all_odds': [],
                    'main_odds': {},
                    'ou_line': None
                }

            indexed[key]['all_odds'].append(odd_item)

            btype = d.get('betTypNm', '')
            if '언더오버' in btype and handi_val:
                indexed[key]['ou_line'] = str(handi_val)

            if sp == 'BS': # 야구
                if '승1패' in btype or '승N패' in btype:
                    indexed[key]['s1p'] = {'home': w_allot, 'draw': d_allot, 'away': l_allot}
                elif '일반 승패' in btype or '승패' in btype:
                    indexed[key]['general'] = {'home': w_allot, 'draw': None, 'away': l_allot}
            elif sp == 'SC': # 축구
                if '승무패' in btype:
                    indexed[key]['main_odds'] = {
                        'home': w_allot,
                        'draw': d_allot,
                        'away': l_allot,
                        'domestic_home': w_allot,
                        'domestic_draw': d_allot,
                        'domestic_away': l_allot,
                        'is_betman_official': True
                    }
            elif sp == 'BK': # 농구
                if '일반 승패' in btype or '승패' in btype:
                    indexed[key]['general'] = {'home': w_allot, 'draw': None, 'away': l_allot}
                elif '승5패' in btype or '승N패' in btype:
                    indexed[key]['s5p'] = {'home': w_allot, 'draw': d_allot, 'away': l_allot}

        # 야구, 농구, 배구 메인 배당 최종 정립
        for k, v in indexed.items():
            if v['sport_code'] == 'BASEBALL':
                s1p = v.get('s1p')
                gen = v.get('general')
                if s1p:
                    v['main_odds'] = {
                        'home': s1p['home'],
                        'draw': s1p['draw'],
                        'away': s1p['away'],
                        's1p_home': s1p['home'],
                        's1p_draw': s1p['draw'],
                        's1p_away': s1p['away'],
                        'general_home': gen['home'] if gen else s1p['home'],
                        'general_away': gen['away'] if gen else s1p['away'],
                        'domestic_home': s1p['home'],
                        'domestic_draw': s1p['draw'],
                        'domestic_away': s1p['away'],
                        'is_betman_official': True
                    }
                elif gen:
                    v['main_odds'] = {
                        'home': gen['home'],
                        'draw': None,
                        'away': gen['away'],
                        'general_home': gen['home'],
                        'general_away': gen['away'],
                        'domestic_home': gen['home'],
                        'domestic_draw': None,
                        'domestic_away': gen['away'],
                        'is_betman_official': True
                    }
            elif v['sport_code'] == 'BASKETBALL':
                s5p = v.get('s5p')
                gen = v.get('general')
                if s5p:
                    v['main_odds'] = {
                        'home': s5p['home'],
                        'draw': s5p['draw'],
                        'away': s5p['away'],
                        'domestic_home': s5p['home'],
                        'domestic_draw': s5p['draw'],
                        'domestic_away': s5p['away'],
                        'is_betman_official': True
                    }
                elif gen:
                    v['main_odds'] = {
                        'home': gen['home'],
                        'draw': None,
                        'away': gen['away'],
                        'domestic_home': gen['home'],
                        'domestic_draw': None,
                        'domestic_away': gen['away'],
                        'is_betman_official': True
                    }
            elif v['sport_code'] == 'VOLLEYBALL':
                for o in v['all_odds']:
                    if '승패' in o['type']:
                        v['main_odds'] = {
                            'home': o['home_odds'],
                            'draw': None,
                            'away': o['away_odds'],
                            'domestic_home': o['home_odds'],
                            'domestic_away': o['away_odds'],
                            'is_betman_official': True
                        }
                        break

        # 초고속 O(1) 별칭 사전(alias_map) 빌드: 모든 동의어 조합을 사전 키로 매핑
        alias_map = {}
        for (h_norm, a_norm), match_info in indexed.items():
            h_aliases = [h_norm]
            for grp in _PRECOMPUTED_SYNONYM_GROUPS:
                if any(g == h_norm or g in h_norm or h_norm in g for g in grp):
                    h_aliases.extend(grp)
                    break
            a_aliases = [a_norm]
            for grp in _PRECOMPUTED_SYNONYM_GROUPS:
                if any(g == a_norm or g in a_norm or a_norm in g for g in grp):
                    a_aliases.extend(grp)
                    break
            for ha in set(h_aliases):
                for aa in set(a_aliases):
                    alias_map[(ha, aa)] = match_info

        _CACHE[cache_key] = (now, alias_map)
        return alias_map

    @staticmethod
    def attach_betman_odds_to_matches(matches: list, db=None) -> list:
        """
        MatchService.get_matches가 반환하는 경기 목록에 실제 베트맨 공식 배당(G101) 및 all_odds 주입 (O(1) 속도)
        """
        if not matches:
            return matches

        indexed_proto = BetmanService.get_indexed_proto_matches()
        if not indexed_proto:
            return matches

        for m in matches:
            h_norm = clean_name(m.home_team_name)
            a_norm = clean_name(m.away_team_name)

            proto_info = indexed_proto.get((h_norm, a_norm))
            if proto_info and proto_info.get('main_odds'):
                m.odds = proto_info['main_odds']
                m.all_odds = proto_info.get('all_odds', [])
                if proto_info.get('ou_line'):
                    m.ou_line = proto_info['ou_line']
                if getattr(m, 'prediction', None) and isinstance(m.prediction, dict):
                    m.prediction['odds'] = proto_info['main_odds']
                    if proto_info.get('ou_line'):
                        m.prediction['ou_line'] = proto_info['ou_line']

        return matches

    @staticmethod
    def get_match_full_odds(match_id: int) -> dict:
        """
        특정 경기(match_id)에 대한 베트맨 공식 배당 및 실시간 투표율 조회
        """
        try:
            db_path = 'sports_data.db'
            if not os.path.exists(db_path):
                return {'status': 'error', 'message': 'DB 없음'}
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, sport_code, league_name, home_team_name, away_team_name, match_date, status, home_score, away_score FROM matches WHERE id = ?",
                (match_id,)
            )
            row = cursor.fetchone()
            conn.close()
            if not row:
                return {'status': 'error', 'message': f'경기 {match_id} 없음'}
            match = dict(row)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

        sport_code = match.get('sport_code', 'BASEBALL')
        home_name = match.get('home_team_name', '')
        away_name = match.get('away_team_name', '')
        match_date = match.get('match_date', '')

        indexed = BetmanService.get_indexed_proto_matches()
        h_norm = clean_name(home_name)
        a_norm = clean_name(away_name)

        proto_info = indexed.get((h_norm, a_norm))
        if not proto_info:
            for (ih, ia), info in indexed.items():
                if teams_match(ih, h_norm) and teams_match(ia, a_norm):
                    proto_info = info
                    break

        matched_odds = proto_info.get('all_odds', []) if proto_info else []

        return {
            'status': 'success',
            'match_id': match_id,
            'home': home_name,
            'away': away_name,
            'sport_code': sport_code,
            'match_date': match_date,
            'toto_groups': [],
            'full_odds': matched_odds,
            'main_odds': proto_info.get('main_odds', {}) if proto_info else {}
        }

    @staticmethod
    def sync_betman_proto_matches(db) -> dict:
        """
        베트맨 최신 프로토(G101) 전 경기를 DB에 자동으로 동기화
        - 신규 경기 자동 등록
        - 공식 배당 및 실시간 투표율을 match_details에 저장
        """
        from app.models.models import Match, MatchDetail

        proto_data = BetmanService.get_proto_odds(force_refresh=True)
        keys = proto_data.get('keys', [])
        datas = proto_data.get('datas', [])
        vote_dict = proto_data.get('votes', {})
        active_ts = proto_data.get('gmTs', 260093)

        if not datas:
            return {'status': 'error', 'message': '프로토 데이터를 불러올 수 없습니다.'}

        # 1. Group rows by distinct match
        grouped = {}
        for row in datas:
            d = dict(zip(keys, row))
            h = d.get('homeName', '').strip()
            a = d.get('awayName', '').strip()
            l = d.get('leagueName', '').strip()
            sp = d.get('itemCode', 'BS')
            seq = d.get('matchSeq')
            m_key = f"{sp}_{l}_{h}_{a}"

            if m_key not in grouped:
                g_ts = d.get('gameDate')
                m_date_str = ""
                if g_ts:
                    try:
                        dt = datetime.fromtimestamp(g_ts / 1000, tz=timezone(timedelta(hours=9)))
                        m_date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        m_date_str = ""

                sport_code = "BASEBALL" if sp == "BS" else ("SOCCER" if sp == "SC" else ("BASKETBALL" if sp == "BK" else "VOLLEYBALL"))
                grouped[m_key] = {
                    'official_id': f"BETMAN_G101_{active_ts}_{seq}",
                    'sport_code': sport_code,
                    'league_name': l,
                    'home_team_name': h,
                    'away_team_name': a,
                    'match_date': m_date_str,
                    'stadium': d.get('meetStadiumFullName') or d.get('meetStadium') or '스타디움',
                    'odds_list': [],
                    'main_odds': {}
                }

            v = vote_dict.get(seq, {})
            tot = v.get('W_BET_CNT', 0) + v.get('D_BET_CNT', 0) + v.get('L_BET_CNT', 0)
            w_pct = round(v.get('W_BET_CNT', 0) / tot * 100, 1) if tot else 0.0
            l_pct = round(v.get('L_BET_CNT', 0) / tot * 100, 1) if tot else 0.0
            d_pct = round(v.get('D_BET_CNT', 0) / tot * 100, 1) if tot else 0.0

            odd_item = {
                'seq': seq,
                'type': d.get('betTypNm', '일반 승패'),
                'home_odds': float(d.get('winAllot') or 0.0),
                'draw_odds': float(d.get('drawAllot') or 0.0),
                'away_odds': float(d.get('loseAllot') or 0.0),
                'handicap': d.get('winHandi') or d.get('handi') or '',
                'win_votes': v.get('W_BET_CNT', 0),
                'draw_votes': v.get('D_BET_CNT', 0),
                'loss_votes': v.get('L_BET_CNT', 0),
                'win_pct': w_pct,
                'draw_pct': d_pct,
                'loss_pct': l_pct
            }
            grouped[m_key]['odds_list'].append(odd_item)
            if not grouped[m_key]['main_odds'] or '승무패' in d.get('betTypNm', '') or '일반 승패' in d.get('betTypNm', ''):
                grouped[m_key]['main_odds'] = odd_item

        synced_count = 0
        updated_count = 0

        for m_key, g_info in grouped.items():
            # Check existing match in DB by exact or canonical team match on that date
            d_prefix = g_info['match_date'][:10] if g_info['match_date'] else ""
            match = None
            if d_prefix:
                candidates = db.query(Match).filter(
                    Match.sport_code == g_info['sport_code'],
                    Match.match_date.like(f"{d_prefix}%")
                ).all()
                for cm in candidates:
                    if teams_match(cm.home_team_name, g_info['home_team_name']) and teams_match(cm.away_team_name, g_info['away_team_name']):
                        match = cm
                        break
            if not match:
                match = db.query(Match).filter(
                    Match.home_team_name == g_info['home_team_name'],
                    Match.away_team_name == g_info['away_team_name'],
                    Match.match_date == g_info['match_date']
                ).first()

            if not match:
                match = Match(
                    official_id=g_info['official_id'],
                    sport_code=g_info['sport_code'],
                    league_name=g_info['league_name'],
                    season="2026",
                    round_name=f"프로토 {str(active_ts)[-2:]}회차",
                    match_date=g_info['match_date'],
                    stadium=g_info['stadium'],
                    home_team_name=g_info['home_team_name'],
                    away_team_name=g_info['away_team_name'],
                    home_score=0,
                    away_score=0,
                    status="SCHEDULED"
                )
                db.add(match)
                db.commit()
                db.refresh(match)
                synced_count += 1
            else:
                updated_count += 1

            # Update match_details with betman odds
            detail = db.query(MatchDetail).filter(MatchDetail.match_id == match.id).first()
            if not detail:
                detail = MatchDetail(match_id=match.id, period_scores="{}", team_stats="{}", source_url="https://www.betman.co.kr")
                db.add(detail)
                db.commit()
                db.refresh(detail)

            try:
                ts = json.loads(detail.team_stats or "{}")
            except Exception:
                ts = {}

            ts['betman_odds'] = g_info['odds_list']
            ts['betman_main_odds'] = g_info['main_odds']
            ts['betman_gm_ts'] = active_ts
            detail.team_stats = json.dumps(ts, ensure_ascii=False)
            db.commit()

        return {
            'status': 'success',
            'active_gm_ts': active_ts,
            'total_matches': len(grouped),
            'synced_new': synced_count,
            'updated_existing': updated_count
        }

    @staticmethod
    def _parse_betman_payload(data: dict, gm_id: str, gm_ts: int) -> dict:
        cur = data.get('currentLottery', {})
        schedules = data.get('schedulesList', [])
        vote_data = data.get('voteStatus', {})
        vote_list = vote_data.get('homeVoteStatusList', []) if isinstance(vote_data, dict) else (vote_data if isinstance(vote_data, list) else [])

        actual_gm_ts = data.get('gmTs') or cur.get('gmTs') or gm_ts
        round_no = str(actual_gm_ts)[-2:]

        sport_label = '야구 승1패' if gm_id == 'G024' else ('축구 승무패' if gm_id == 'G011' else '농구 승5패')
        sport_code = 'BASEBALL' if gm_id == 'G024' else ('SOCCER' if gm_id == 'G011' else 'BASKETBALL')

        matches = []
        for idx, s in enumerate(schedules):
            votes = {'win': 0.0, 'draw': 0.0, 'loss': 0.0, 'win_count': 0, 'draw_count': 0, 'loss_count': 0}
            if idx < len(vote_list):
                v_item = vote_list[idx]
                v_items = v_item.get('awayVoteStatusList', []) if isinstance(v_item, dict) else []
                if len(v_items) >= 3:
                    w_cnt = v_items[0].get('voteCount', 0)
                    d_cnt = v_items[1].get('voteCount', 0)
                    l_cnt = v_items[2].get('voteCount', 0)
                    total = w_cnt + d_cnt + l_cnt
                    if total > 0:
                        votes = {
                            'win_count': w_cnt,
                            'draw_count': d_cnt,
                            'loss_count': l_cnt,
                            'win': round((w_cnt / total * 100), 1),
                            'draw': round((d_cnt / total * 100), 1),
                            'loss': round((l_cnt / total * 100), 1)
                        }

            res_code = s.get('gameResult')
            result_label = None
            if res_code == 'A': result_label = '승'
            elif res_code == 'D': result_label = '1' if gm_id == 'G024' else ('5' if gm_id == 'G027' else '무')
            elif res_code == 'B': result_label = '패'

            home_n = s.get('homeName', '')
            away_n = s.get('awayName', '')
            match_date_str = s.get('gameDateStr') or s.get('gameDate') or ''

            matches.append({
                'seq': s.get('matchSeq', idx + 1),
                'league': s.get('leagueName', 'EPL' if gm_id == 'G011' else ('KBO' if s.get('domastic') else 'MLB')),
                'date': s.get('gameDateStr', ''),
                'home': home_n,
                'away': away_n,
                'result': result_label,
                'result_code': res_code,
                'status': 'SCHEDULED',
                'home_score': 0,
                'away_score': 0,
                'votes': votes,
                'ai_pick': '승' if votes['win'] >= votes['loss'] else '패',
                'ai_conf': max(votes['win'], votes['loss'])
            })

        forward_amt = int(cur.get('forwardAmount') or 0)
        sell_amt = int(cur.get('totalSellAmount') or 0)
        sale_cnt = int(cur.get('totalSaleCnt') or (sell_amt // 1000) or 0)
        winner_prize = int(cur.get('winnerTotalPrize') or int(sell_amt * 0.25))

        first_prize_pool = forward_amt + winner_prize
        second_prize_pool = int(sell_amt * 0.10)
        third_prize_pool = int(sell_amt * 0.05)
        fourth_prize_pool = int(sell_amt * 0.10)

        now_str = datetime.now().strftime("%H:%M:%S")
        is_currently_selling = (sell_amt > 0 and cur.get('saleProgress') != False)

        return {
            'status': 'success',
            'gmId': gm_id,
            'gmTs': actual_gm_ts,
            'round_name': f'{sport_label} {round_no}회차',
            'title': cur.get('gameName', sport_label),
            'sale_status': cur.get('saleStatus') or ('SaleProgress' if is_currently_selling else 'SaleComplete'),
            'status_message': cur.get('statusMessage') or (f'실시간 집계 중 ({sale_cnt:,}표 발매)' if is_currently_selling else '경기 진행 중'),
            'forward_amount': forward_amt,
            'forward_cnt': cur.get('forwardCnt', 0),
            'total_sell_amount': sell_amt,
            'total_sale_cnt': sale_cnt,
            'first_prize_pool': first_prize_pool,
            'second_prize_pool': second_prize_pool,
            'third_prize_pool': third_prize_pool,
            'fourth_prize_pool': fourth_prize_pool,
            'first_prize_text': format_kr_money(first_prize_pool),
            'second_prize_text': format_kr_money(second_prize_pool),
            'third_prize_text': format_kr_money(third_prize_pool),
            'fourth_prize_text': format_kr_money(fourth_prize_pool),
            'total_sell_text': format_kr_money(sell_amt),
            'forward_text': (format_kr_money(forward_amt) + (f" ({cur.get('forwardCnt')}회 이월🔥)" if cur.get('forwardCnt') else "")) if forward_amt > 0 else '이월 없음',
            'is_live': is_currently_selling,
            'updated_at': now_str,
            'matches': matches
        }
