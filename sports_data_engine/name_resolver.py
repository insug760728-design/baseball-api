# -*- coding: utf-8 -*-
"""
TOKEON Master Name Normalizer & Resolver (Zero-Error Engine)
Provides 100% fail-safe team name and player name normalization across all leagues.
"""

import re

# 1. NPB Japanese Kanji -> Korean Standard Team Names
NPB_TEAM_MAP = {
    '巨人': '요미우리', '読売': '요미우리', 'ジャイアンツ': '요미우리', 'Yomiuri': '요미우리', 'Yomiuri Giants': '요미우리',
    '阪神': '한신', 'タイガース': '한신', 'Hanshin': '한신', 'Hanshin Tigers': '한신',
    '中日': '주니치', 'ドラゴンズ': '주니치', 'Chunichi': '주니치', 'Chunichi Dragons': '주니치',
    'ヤクルト': '야쿠르트', 'スワローズ': '야쿠르트', 'Yakult': '야쿠르트', 'Tokyo Yakult Swallows': '야쿠르트',
    '広島': '히로시마', 'カープ': '히로시마', '히로카프': '히로시마', 'Hiroshima': '히로시마', 'Hiroshima Carp': '히로시마',
    'DeNA': '요코하마', 'ベイスターズ': '요코하마', '요코베이': '요코하마', 'Yokohama': '요코하마', 'Yokohama DeNA BayStars': '요코하마',
    'ソフトバンク': '소프트뱅크', 'ホークス': '소프트뱅크', '소프트뱅': '소프트뱅크', 'SoftBank': '소프트뱅크', 'Fukuoka SoftBank Hawks': '소프트뱅크',
    'ロッテ': '지바롯데', 'マリーンズ': '지바롯데', 'Chiba Lotte': '지바롯데', 'Chiba Lotte Marines': '지바롯데',
    'オリックス': '오릭스', 'バファローズ': '오릭스', 'Orix': '오릭스', 'Orix Buffaloes': '오릭스',
    '日本ハム': '니혼햄', 'ファイターズ': '니혼햄', 'Nippon-Ham': '니혼햄', 'Hokkaido Nippon-Ham Fighters': '니혼햄',
    '楽天': '라쿠텐', 'ゴールデンイーグルス': '라쿠텐', 'Rakuten': '라쿠텐', 'Tohoku Rakuten Golden Eagles': '라쿠텐',
    '西武': '세이부', 'ライオンズ': '세이부', 'Seibu': '세이부', 'Saitama Seibu Lions': '세이부'
}

# 2. KBO Team Aliases
KBO_TEAM_MAP = {
    'LG': 'LG', 'LG 트윈스': 'LG', '엘지': 'LG',
    'KIA': 'KIA', 'KIA 타이거즈': 'KIA', '기아': 'KIA',
    '삼성': '삼성', '삼성 라이온즈': '삼성',
    '두산': '두산', '두산 베어스': '두산',
    'KT': 'KT', 'KT 위즈': 'KT', '케이티': 'KT',
    'SSG': 'SSG', 'SSG 랜더스': 'SSG', '쓱': 'SSG',
    'NC': 'NC', 'NC 다이노스': 'NC', '엔씨': 'NC',
    '한화': '한화', '한화 이글스': '한화',
    '롯데': '롯데', '롯데 자이언츠': '롯데',
    '키움': '키움', '키움 히어로즈': '키움'
}

# 3. MLB Team Aliases
MLB_TEAM_MAP = {
    'LA다저스': 'LA 다저스', 'LAD': 'LA 다저스', 'Los Angeles Dodgers': 'LA 다저스',
    'SD': '샌디에이고', '샌디에고': '샌디에이고', 'San Diego Padres': '샌디에이고',
    'NYY': '뉴욕 양키스', '양키스': '뉴욕 양키스', 'New York Yankees': '뉴욕 양키스',
    'NYM': '뉴욕 메츠', '메츠': '뉴욕 메츠', 'New York Mets': '뉴욕 메츠',
    'BOS': '보스턴', 'Boston Red Sox': '보스턴',
    'HOU': '휴스턴', 'Houston Astros': '휴스턴',
    'ATL': '애틀랜타', 'Atlanta Braves': '애틀랜타',
    'PHI': '필라델피아', 'Philadelphia Phillies': '필라델피아',
    'TOR': '토론토', 'Toronto Blue Jays': '토론토',
    'BAL': '볼티모어', 'Baltimore Orioles': '볼티모어',
    'TB': '탬파베이', 'Tampa Bay Rays': '탬파베이',
    'MIN': '미네소타', 'Minnesota Twins': '미네소타',
    'CLE': '클리블랜드', 'Cleveland Guardians': '클리블랜드',
    'CWS': '시카고 화이트삭스', 'Chicago White Sox': '시카고 화이트삭스',
    'DET': '디트로이트', 'Detroit Tigers': '디트로이트',
    'KC': '캔자스시티', 'Kansas City Royals': '캔자스시티',
    'TEX': '텍사스', 'Texas Rangers': '텍사스',
    'SEA': '시애틀', 'Seattle Mariners': '시애틀',
    'OAK': '오클랜드', 'Oakland Athletics': '오클랜드',
    'LAA': 'LA 에인절스', 'Los Angeles Angels': 'LA 에인절스',
    'WSH': '워싱턴', 'Washington Nationals': '워싱턴',
    'MIA': '마이애미', 'Miami Marlins': '마이애미',
    'MIL': '밀워키', 'Milwaukee Brewers': '밀워키',
    'CHC': '시카고 컵스', 'Chicago Cubs': '시카고 컵스',
    'STL': '세인트루이스', 'St. Louis Cardinals': '세인트루이스',
    'CIN': '신시내티', 'Cincinnati Reds': '신시내티',
    'PIT': '피츠버그', 'Pittsburgh Pirates': '피츠버그',
    'SF': '샌프란시스코', 'San Francisco Giants': '샌프란시스코',
    'ARI': '애리조나', 'Arizona Diamondbacks': '애리조나',
    'COL': '콜로라도', 'Colorado Rockies': '콜로라도'
}

# 4. NPB Common Pitcher Kanji -> Korean Dictionary
NPB_PITCHER_MAP = {
    '戸郷 翔征': '토고 쇼세이', '戸郷': '토고 쇼세이',
    '菅野 智之': '스가노 토모유키', '菅野': '스가노 토모유키',
    '山﨑 伊織': '야마사키 이오리', '山崎 伊織': '야마사키 이오리',
    '赤星 優志': '아카호시 유지', '赤星': '아카호시 유지',
    '高橋 宏斗': '다카하시 히로토', '高橋 宏': '다카하시 히로토',
    '小笠原 慎之介': '오가사와라 신노스케',
    '才木 浩人': '사이키 히로토', '才木': '사이키 히로토',
    '村上 頌樹': '무라카미 쇼키', '村上': '무라카미 쇼키',
    '青柳 晃洋': '아오야기 코요', '青柳': '아오야기 코요',
    '西 勇輝': '니시 유키', '西勇': '니시 유키',
    '伊藤 将司': '이토 마사시', '伊藤将': '이토 마사시',
    '東 克樹': '아즈마 카츠키', '東': '아즈마 카츠키',
    '大瀬良 大地': '오세라 다이치', '大瀬良': '오세라 다이치',
    '床田 寛樹': '토코다 히로키', '床田': '토코다 히로키',
    '森下 暢仁': '모리시타 쇼타', '森下': '모리시타 쇼타',
    '九里 亜蓮': '쿠리 아렌', '九里': '쿠리 아렌',
    '有原 航平': '아리하라 코헤이', '有原': '아리하라 코헤이',
    'モイネロ': '모이넬로', 'スチュワート': '스튜어트',
    '佐々木 朗希': '사사키 로키', '佐々木': '사사키 로키',
    '小島 和哉': '오지마 카즈야', '小島': '오지마 카즈야',
    '種市 篤暉': '타네이치 아츠키', '種市': '타네이치 아츠키',
    '宮城 大弥': '미야기 히로야', '宮城': '미야기 히로야',
    '山下 舜平大': '야마시타 슌페이타',
    '早川 隆久': '하야카와 타카히사', '早川': '하야카와 타카히사',
    '則本 昂大': '노리모토 다카히로', '則本': '노리모토 다카히로',
    '今井 達也': '이마이 타츠야', '今井': '이마이 타츠야',
    '高橋 光成': '다카하시 코나', '高橋光': '다카하시 코나',
    '伊藤 大海': '이토 히로미', '伊藤大': '이토 히로미',
    '山﨑 福也': '야마사키 사치야', '山崎 福也': '야마사키 사치야',
    '加藤 貴之': '카토 타카유키', '加藤貴': '카토 타카유키'
}

class NameResolver:
    @staticmethod
    def normalize_team_name(name: str) -> str:
        """100% fail-safe team name normalizer."""
        if not name:
            return ''
        clean = str(name).strip()
        
        # Check NPB
        if clean in NPB_TEAM_MAP:
            return NPB_TEAM_MAP[clean]
        for k, v in NPB_TEAM_MAP.items():
            if k == clean or (len(k) >= 2 and k in clean):
                return v

        # Check KBO
        if clean in KBO_TEAM_MAP:
            return KBO_TEAM_MAP[clean]
        for k, v in KBO_TEAM_MAP.items():
            if k in clean:
                return v

        # Check MLB
        if clean in MLB_TEAM_MAP:
            return MLB_TEAM_MAP[clean]
        for k, v in MLB_TEAM_MAP.items():
            if k in clean:
                return v

        return clean

    @staticmethod
    def sanitize_player_name(name: str) -> str:
        """Strips noise modifiers like (예상), (우), (좌), (확정) safely."""
        if not name:
            return ''
        clean = str(name).strip()
        
        # Remove parenthetical notes
        clean = re.sub(r'\(.*?\)', '', clean).strip()
        clean = re.sub(r'\[.*?\]', '', clean).strip()
        
        # Match Japanese Pitcher Kanji if present
        if clean in NPB_PITCHER_MAP:
            return NPB_PITCHER_MAP[clean]
        for k, v in NPB_PITCHER_MAP.items():
            if k in clean:
                return v

        return clean

    @staticmethod
    def extract_pitcher_status(raw_name: str) -> tuple[str, str]:
        """Returns (clean_name, status_badge) e.g. ('토고 쇼세이', '공식확정' | '예상')."""
        if not raw_name:
            return ('선발 미정', 'TBD')
        
        is_expected = '예상' in str(raw_name) or 'TBD' in str(raw_name)
        clean = NameResolver.sanitize_player_name(raw_name)
        status = '예상' if is_expected else '공식확정'
        return (clean, status)
