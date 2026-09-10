# -*- coding: utf-8 -*-
"""
NameUtils: 팀/선수 이름 약어 변환 유틸리티
- 팀 이름 약어 변환 (NC Dinos → NC)
- 선수 이름 약어 변환 (한국 선수는 전체 이름, 외국 선수는 성만)
"""

import re
from typing import Optional

class NameUtils:
    # 팀 이름 약어 매핑 테이블
    TEAM_ABBREVIATIONS = {
        # KBO
        "NC Dinos": "NC",
        "NC 다이노스": "NC",
        "KT Wiz": "KT",
        "KT 위즈": "KT",
        "LG Twins": "LG",
        "LG 트윈스": "LG",
        "SSG Landers": "SSG",
        "SSG 랜더스": "SSG",
        "Hanwha Eagles": "한화",
        "한화 이글스": "한화",
        "Lotte Giants": "롯데",
        "롯데 자이언츠": "롯데",
        "Samsung Lions": "삼성",
        "삼성 라이온즈": "삼성",
        "Doosan Bears": "두산",
        "두산 베어스": "두산",
        "Kiwoom Heroes": "키움",
        "키움 히어로즈": "키움",
        "KIA Tigers": "KIA",
        "KIA 타이거즈": "KIA",
        
        # NPB
        "Yakult Swallows": "야쿠르트",
        "야쿠르트 스왈로스": "야쿠르트",
        "Chunichi Dragons": "주니치",
        "주니치 드래건스": "주니치",
        "Hiroshima Toyo Carp": "히로시마",
        "히로시마 도요카프": "히로시마",
        "Yomiuri Giants": "요미우리",
        "요미우리 자이언츠": "요미우리",
        "Hanshin Tigers": "한신",
        "한신 타이거스": "한신",
        "Yokohama DeNA Baystars": "요코하마",
        "요코하마 DeNA": "요코하마",
        "Rakuten Golden Eagles": "라쿠텐",
        "라쿠텐 골든이글스": "라쿠텐",
        "Hokkaido Nippon-Ham Fighters": "닛폰햄",
        "닛폰햄 파이터스": "닛폰햄",
        "Orix Buffaloes": "오릭스",
        "오릭스 버팔로스": "오릭스",
        "Chiba Lotte Marines": "지바롯데",
        "지바롯데 마린스": "지바롯데",
        "Fukuoka SoftBank Hawks": "소프트뱅크",
        "소프트뱅크 호크스": "소프트뱅크",
        "Seibu Lions": "세이부",
        "세이부 라이온즈": "세이부",
        
        # MLB
        "Los Angeles Dodgers": "LAD",
        "New York Yankees": "NYY",
        "Boston Red Sox": "BOS",
        "Chicago Cubs": "CHC",
        "San Francisco Giants": "SF",
        "Atlanta Braves": "ATL",
        "Houston Astros": "HOU",
        "Philadelphia Phillies": "PHI",
        "St. Louis Cardinals": "STL",
        "Toronto Blue Jays": "TOR",
        "Seattle Mariners": "SEA",
        "New York Mets": "NYM",
        "Chicago White Sox": "CWS",
        "Los Angeles Angels": "LAA",
        "Oakland Athletics": "OAK",
        "Texas Rangers": "TEX",
        "Tampa Bay Rays": "TB",
        "Arizona Diamondbacks": "ARI",
        "Colorado Rockies": "COL",
        "San Diego Padres": "SD",
        "Miami Marlins": "MIA",
        "Milwaukee Brewers": "MIL",
        "Cincinnati Reds": "CIN",
        "Pittsburgh Pirates": "PIT",
        "Washington Nationals": "WSH",
        "Detroit Tigers": "DET",
        "Minnesota Twins": "MIN",
        "Cleveland Guardians": "CLE",
        "Kansas City Royals": "KC",
        "Baltimore Orioles": "BAL",
    }
    
    @staticmethod
    def abbreviate_team_name(name: str) -> str:
        """팀 이름을 약어로 변환"""
        if not name:
            return ""
        
        # 직접 매핑 확인
        for full_name, abbreviation in NameUtils.TEAM_ABBREVIATIONS.items():
            if full_name.lower() == name.lower():
                return abbreviation
        
        # 부분 일치 확인 (원본 이름이 축약어보다 긴 경우에만)
        for full_name, abbreviation in NameUtils.TEAM_ABBREVIATIONS.items():
            if len(name) > len(abbreviation) and (full_name.lower() in name.lower() or name.lower() in full_name.lower()):
                return abbreviation
        
        # 매핑이 없으면 원본 반환
        return name
    
    @staticmethod
    def abbreviate_player_name(name: str) -> str:
        """선수 이름을 약어로 변환 (한국 선수는 전체 이름, 외국 선수는 성만)"""
        if not name or not name.strip():
            return ""
        
        # 공백 제거
        name = name.strip()
        
        # 한국어 이름인 경우 - 전체 이름 유지
        if NameUtils._is_korean(name):
            return name
        
        # 영어 이름인 경우 - 성만 사용
        parts = name.split()
        if len(parts) >= 1:
            surname = parts[0]
            return surname
        
        return name
    
    @staticmethod
    def _is_korean(text: str) -> bool:
        """한국어 포함 여부 확인"""
        korean_pattern = re.compile(r'[가-힣]')
        return bool(korean_pattern.search(text))

# 싱글톤 인스턴스
name_utils = NameUtils()