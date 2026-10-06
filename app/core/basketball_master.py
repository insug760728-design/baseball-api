# -*- coding: utf-8 -*-
"""
Basketball Master Team Normalization & 1:1 Matching Engine
=========================================================
KBL(남자농구 10구단), WKBL(여자농구 6구단), NBA(미국농구 30구단)
공식 단축명(Short Name) 정규화 및 1:1 상호 매칭 보장 모듈.
"""

from typing import Dict, List, Optional
from functools import lru_cache

# 1. KBL (한국 남자 프로농구 10개 구단)
KBL_CANONICAL_MAP = {
    "수원KT": [
        "수원KT 소닉붐", "수원 KT 소닉붐", "수원kt 소닉붐", "수원KT", "수원 KT", "수원kt",
        "KT 소닉붐", "kt 소닉붐", "KT소닉붐", "수원소닉붐", "부산KT", "부산 KT", "suwon kt sonicboom", "suwon kt"
    ],
    "창원LG": [
        "창원LG 세이커스", "창원 LG 세이커스", "창원lg 세이커스", "창원LG", "창원 LG", "창원lg",
        "LG 세이커스", "lg 세이커스", "LG세이커스", "창원세이커스", "changwon lg sakers", "changwon lg"
    ],
    "서울SK": [
        "서울SK 나이츠", "서울 SK 나이츠", "서울sk 나이츠", "서울SK", "서울 SK", "서울sk",
        "SK 나이츠", "sk 나이츠", "SK나이츠", "서울나이츠", "seoul sk knights", "seoul sk"
    ],
    "서울삼성": [
        "서울삼성 썬더스", "서울 삼성 썬더스", "서울삼성", "서울 삼성", "서울 삼성 썬더스",
        "삼성 썬더스", "삼성썬더스", "삼성 농구단", "seoul samsung thunders", "seoul samsung"
    ],
    "안양정관장": [
        "안양정관장 레드부스터스", "안양 정관장 레드부스터스", "안양 정관장", "안양정관장",
        "정관장 레드부스터스", "정관장레드부스터스", "정관장", "안양 KGC", "안양KGC", "KGC인삼공사", "anyang red boosters"
    ],
    "원주DB": [
        "원주DB 프로미", "원주 DB 프로미", "원주db 프로미", "원주DB", "원주 DB", "원주db",
        "DB 프로미", "db 프로미", "DB프로미", "원주 프로미", "원주동부", "wonju db promy", "wonju db"
    ],
    "고양소노": [
        "고양소노 스카이거너스", "고양 소노 스카이거너스", "고양소노", "고양 소노",
        "소노 스카이거너스", "소노스카이거너스", "소노", "고양 캐롯", "고양 오리온", "goyang sono skygunners", "goyang sono"
    ],
    "한국가스공사": [
        "대구한국가스공사 페가수스", "대구 한국가스공사 페가수스", "대구한국가스공사", "대구 한국가스공사",
        "한국가스공사 페가수스", "한국가스공사", "한국가스", "대구가스공사", "가스공사", "인천전자랜드", "daegu kogas"
    ],
    "부산KCC": [
        "부산KCC 이지스", "부산 KCC 이지스", "부산kcc 이지스", "부산KCC", "부산 KCC", "부산kcc",
        "KCC 이지스", "kcc 이지스", "KCC이지스", "전주KCC", "전주 KCC", "busan kcc egis", "busan kcc"
    ],
    "현대모비스": [
        "울산현대모비스 피버스", "울산 현대모비스 피버스", "울산현대모비스", "울산 현대모비스",
        "현대모비스 피버스", "현대모비스피버스", "현대모비스", "모비스", "울산모비스", "ulsan hyundai mobis", "ulsan mobis"
    ]
}

# 2. WKBL (한국 여자 프로농구 6개 구단)
WKBL_CANONICAL_MAP = {
    "우리은행": [
        "아산 우리은행 우리WON", "아산 우리은행", "아산우리은행", "우리은행 우리WON", "우리은행우리WON", "우리은행", "우리won", "asan woori bank"
    ],
    "KB스타즈": [
        "청주 KB스타즈", "청주 KB국민은행 스타즈", "청주KB스타즈", "청주 KB", "KB스타즈", "KB 스타즈", "kb스타즈", "국민은행", "cheongju kb stars"
    ],
    "삼성생명": [
        "용인 삼성생명 블루밍스", "용인 삼성생명", "용인삼성생명", "삼성생명 블루밍스", "삼성생명블루밍스", "삼성생명", "yongin samsung life"
    ],
    "신한은행": [
        "인천 신한은행 에스버드", "인천 신한은행", "인천신한은행", "신한은행 에스버드", "신한은행에스버드", "신한은행", "incheon shinhan bank"
    ],
    "BNK썸": [
        "부산 BNK 썸", "부산 BNK썸", "부산BNK썸", "부산 BNK", "BNK 썸", "BNK썸", "bnk 썸", "bnk썸", "부산bnk", "busan bnk sum"
    ],
    "하나은행": [
        "부천 하나은행", "부천하나은행", "부천 하나원큐", "부천하나원큐", "하나원큐", "하나은행", "bucheon hana bank", "하나 원큐"
    ]
}

# 3. NBA (미국 프로농구 30개 구단)
NBA_CANONICAL_MAP = {
    # 동부
    "보스턴": ["Boston Celtics", "Boston", "보스턴 셀틱스", "보스턴"],
    "뉴욕닉스": ["New York Knicks", "NY Knicks", "New York", "뉴욕 닉스", "뉴욕닉스", "뉴욕"],
    "밀워키": ["Milwaukee Bucks", "Milwaukee", "밀워키 벅스", "밀워키"],
    "클리블랜드": ["Cleveland Cavaliers", "Cleveland", "클리블랜드 캐벌리어스", "클리블랜드", "클리블랜드 캐브스"],
    "인디애나": ["Indiana Pacers", "Indiana", "인디애나 페이서스", "인디애나"],
    "필라델피아": ["Philadelphia 76ers", "Philadelphia", "Phila 76ers", "필라델피아 세븐티식서스", "필라델피아", "필라"],
    "마이애미": ["Miami Heat", "Miami", "마이애미 히트", "마이애미"],
    "올랜도": ["Orlando Magic", "Orlando", "올랜도 매직", "올랜도"],
    "시카고불스": ["Chicago Bulls", "Chicago", "시카고 불스", "시카고불스", "시카고"],
    "애틀랜타": ["Atlanta Hawks", "Atlanta", "애틀랜타 호크스", "애틀랜타", "애틀란타"],
    "브루클린": ["Brooklyn Nets", "Brooklyn", "브루클린 네츠", "브루클린"],
    "토론토": ["Toronto Raptors", "Toronto", "토론토 랩터스", "토론토"],
    "샬럿": ["Charlotte Hornets", "Charlotte", "샬럿 호네츠", "샬럿"],
    "워싱턴": ["Washington Wizards", "Washington", "워싱턴 위저즈", "워싱턴", "워싱턴 위저드"],
    "디트로이트": ["Detroit Pistons", "Detroit", "디트로이트 피스톤스", "디트로이트 피스톤즈", "디트로이트"],
    # 서부
    "오클라호마": ["Oklahoma City Thunder", "OKC Thunder", "Oklahoma City", "오클라호마시티 썬더", "오클라호마 썬더", "오클라호마"],
    "덴버": ["Denver Nuggets", "Denver", "덴버 너게츠", "덴버"],
    "미네소타": ["Minnesota Timberwolves", "Minnesota", "미네소타 팀버울브스", "미네소타", "미네팀버"],
    "LA클리퍼스": ["LA Clippers", "Los Angeles Clippers", "Clippers", "LA 클리퍼스", "LA클리퍼스", "로스앤젤레스 클리퍼스", "클리퍼스"],
    "댈러스": ["Dallas Mavericks", "Dallas", "댈러스 매버릭스", "댈러스"],
    "피닉스": ["Phoenix Suns", "Phoenix", "피닉스 선즈", "피닉스 선스", "피닉스"],
    "LA레이커스": ["Los Angeles Lakers", "LA Lakers", "Lakers", "LA 레이커스", "LA레이커스", "로스앤젤레스 레이커스", "레이커스"],
    "뉴올리언스": ["New Orleans Pelicans", "New Orleans", "뉴올리언스 펠리컨스", "뉴올리언스", "뉴올펠리"],
    "새크라멘토": ["Sacramento Kings", "Sacramento", "새크라멘토 킹스", "새크라멘토", "새크킹스"],
    "골든스테이트": ["Golden State Warriors", "Golden State", "Warriors", "골든스테이트 워리어스", "골든스테이트", "GS 워리어스", "GS워리어스", "골스"],
    "휴스턴": ["Houston Rockets", "Houston", "휴스턴 로키츠", "휴스턴 로케츠", "휴스턴"],
    "유타": ["Utah Jazz", "Utah", "유타 재즈", "유타"],
    "멤피스": ["Memphis Grizzlies", "Memphis", "멤피스 그리즐리스", "멤피스"],
    "샌안토니오": ["San Antonio Spurs", "San Antonio", "샌안토니오 스퍼스", "샌안토니오", "샌안스퍼스"],
    "포틀랜드": ["Portland Trail Blazers", "Portland", "포틀랜드 트레일블레이저스", "포틀랜드", "포틀블레이"]
}

# 역방향 빠른 조회를 위한 통합 Lookup 테이블 (소문자 & 공백제거)
_ALL_BASKETBALL_LOOKUP: Dict[str, str] = {}
_ALL_ALIASES_BY_CANONICAL: Dict[str, List[str]] = {}

def _normalize_key(s: str) -> str:
    if not s: return ""
    return str(s).replace(" ", "").replace("_", "").replace("-", "").replace(".", "").replace("·", "").lower()

for mapping_dict in [KBL_CANONICAL_MAP, WKBL_CANONICAL_MAP, NBA_CANONICAL_MAP]:
    for canonical, aliases in mapping_dict.items():
        all_variants = [canonical] + aliases
        _ALL_ALIASES_BY_CANONICAL[canonical] = list(set(all_variants))
        for variant in all_variants:
            _ALL_BASKETBALL_LOOKUP[_normalize_key(variant)] = canonical

@lru_cache(maxsize=1024)
def to_short_basketball_name(team_name: str) -> str:
    """
    농구 팀명을 표준 단축명으로 1:1 변환.
    예: '수원KT 소닉붐' -> '수원KT'
        '창원LG 세이커스' -> '창원LG'
        '용인 삼성생명 블루밍스' -> '삼성생명'
        'Los Angeles Lakers' -> 'LA레이커스'
    농구 팀이 아니면 원본의 공백 정리본 반환.
    """
    if not team_name:
        return ""
    
    clean = str(team_name).strip()
    norm = _normalize_key(clean)
    
    # 1. 완전 일치 조회
    if norm in _ALL_BASKETBALL_LOOKUP:
        return _ALL_BASKETBALL_LOOKUP[norm]
    
    # 2. 부분 일치 (긴 키 우선)
    sorted_keys = sorted(_ALL_BASKETBALL_LOOKUP.keys(), key=lambda k: len(k), reverse=True)
    for k in sorted_keys:
        if len(k) >= 2 and (k in norm or norm in k):
            return _ALL_BASKETBALL_LOOKUP[k]
            
    return clean

def is_same_basketball_team(name1: str, name2: str) -> bool:
    """
    두 팀명이 동일 농구팀인지 1:1 정밀 검증.
    예: is_same_basketball_team('수원KT 소닉붐', '수원KT') == True
    """
    if not name1 or not name2:
        return False
    
    c1 = to_short_basketball_name(name1)
    c2 = to_short_basketball_name(name2)
    
    if c1 and c2 and c1 == c2:
        return True
        
    return _normalize_key(name1) == _normalize_key(name2)

def get_basketball_tokens_for_query(team_name: str) -> List[str]:
    """
    DB 검색 및 전적 조회 시 단축명, 풀네임, 핵심 토큰을 모두 포함하는 쿼리 리스트 반환
    """
    canon = to_short_basketball_name(team_name)
    if canon in _ALL_ALIASES_BY_CANONICAL:
        return _ALL_ALIASES_BY_CANONICAL[canon]
    return [team_name, canon]
