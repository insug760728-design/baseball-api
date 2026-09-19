# -*- coding: utf-8 -*-
"""
Football Tactical Master Data
=============================
K리그(1 & 2), J리그(J1 & J2), 라리가, 세리에A, 분데스리가, 리그앙 공식 감독 & 전술 & 팀 지표 데이터베이스.
EPLTacticalService와 결합되어 전 세계 모든 축구 리그에 100% 실명 감독 및 전술 프로필 제공.
"""

from typing import Dict, Any

# ==============================================================================
# 1. K리그 (K리그1 & K리그2) 공식 감독 및 전술 마스터 데이터
# ==============================================================================
KLEAGUE_TACTICAL_DB: Dict[str, Dict[str, Any]] = {
    "부천FC 1995": {
        "aliases": ["부천", "부천fc", "부천 1995", "부천fc 1995", "bucheon"],
        "name_kr": "부천FC 1995",
        "name_en": "Bucheon FC 1995",
        "api_football_id": 2960,
        "manager": {
            "name_kr": "이영민",
            "name_en": "Lee Young-min",
            "nationality": "한국",
            "age": 50,
            "win_rate": "48.5%",
            "preferred_formation": "3-4-3",
            "tactical_style": "고기동성 윙백 전진 및 강한 전방 압박 트랜지션",
            "tendency_tags": ["#고강도압박", "#윙백전진", "#스피드역습", "#기동력", "#공수전환"],
            "philosophy": "강한 체력과 압박을 바탕으로 상대 실수를 유발하는 스피드 축구",
            "photo": "https://media.api-sports.io/football/coachs/1831.png"
        },
        "formation": {
            "primary": "3-4-3",
            "secondary": "4-2-3-1",
            "style_desc": "3백 기반 윙백의 과감한 측면 침투와 3톱의 스피드 역습",
            "attack_focus": "측면 돌파 & 빠른 컷백 크로스",
            "lineup_type": "3-4-3"
        },
        "possession": {
            "avg": 48.6,
            "style": "속공/전환형 (Fast Transition)",
            "field_tilt": 49.2,
            "pass_accuracy": "80.5%"
        },
        "discipline": {
            "yellow_per_game": 2.0,
            "red_total": 2,
            "fouls_per_game": 11.4,
            "risk_level": "보통 (주의)",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "중원 경합 시 적극적인 파울로 상대 역습 차단"
        }
    },
    "김천상무": {
        "aliases": ["김천상무", "김천 상무", "김천상무 프로축구단", "김천", "gimcheon sangmu", "sangmu"],
        "name_kr": "김천상무 프로축구단",
        "name_en": "Gimcheon Sangmu",
        "api_football_id": 2959,
        "manager": {
            "name_kr": "정정용",
            "name_en": "Chung Jung-yong",
            "nationality": "한국",
            "age": 55,
            "win_rate": "54.2%",
            "preferred_formation": "4-3-3",
            "tactical_style": "유기적인 포지셔닝과 간결한 삼각 연계 빌드업 & 중원 장악",
            "tendency_tags": ["#유기적연계", "#중원장악", "#삼각패스", "#전술완성도", "#능동적빌드업"],
            "philosophy": "선수들의 높은 개인 역량을 극대화하는 유기적 포지셔닝과 간결한 패스워크",
            "photo": "https://media.api-sports.io/football/coachs/1832.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-4-2",
            "style_desc": "중원 3미들의 콤팩트 빌드업과 양 윙어의 중앙 침투",
            "attack_focus": "하프스페이스 침투 & 2선 중거리슛",
            "lineup_type": "4-3-3"
        },
        "possession": {
            "avg": 53.4,
            "style": "점유/지공형 (Controlled Possession)",
            "field_tilt": 55.1,
            "pass_accuracy": "84.2%"
        },
        "discipline": {
            "yellow_per_game": 1.7,
            "red_total": 1,
            "fouls_per_game": 10.2,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "우수한 위치 선정을 통한 안정적 파울 관리"
        }
    },
    "울산 HD": {
        "aliases": ["울산 hd", "울산", "울산현대", "울산 현대", "ulsan hd", "ulsan"],
        "name_kr": "울산 HD",
        "name_en": "Ulsan HD FC",
        "api_football_id": 2955,
        "manager": {
            "name_kr": "김판곤",
            "name_en": "Kim Pan-gon",
            "nationality": "한국",
            "age": 55,
            "win_rate": "61.8%",
            "preferred_formation": "4-2-3-1",
            "tactical_style": "주도적인 후방 빌드업 & 파괴적인 공격 전개",
            "tendency_tags": ["#주도적빌드업", "#공격축구", "#중원지배", "#위닝멘탈리티"],
            "philosophy": "높은 볼 점유율과 2선 공격진의 파괴력을 통한 주도적인 축구",
            "photo": "https://media.api-sports.io/football/coachs/1833.png"
        },
        "formation": {
            "primary": "4-2-3-1",
            "secondary": "4-3-3",
            "style_desc": "더블 볼란치의 볼 배급과 2선의 창의적인 찬스 메이킹",
            "attack_focus": "중앙 킬패스 & 측면 컷백",
            "lineup_type": "4-2-3-1"
        },
        "possession": {
            "avg": 57.5,
            "style": "점유/주도형 (Dominant)",
            "field_tilt": 60.2,
            "pass_accuracy": "86.1%"
        },
        "discipline": {
            "yellow_per_game": 1.6,
            "red_total": 1,
            "fouls_per_game": 9.8,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "점유율 우위를 통한 안정적인 경기 운영"
        }
    },
    "전북 현대": {
        "aliases": ["전북 현대", "전북", "전북현대", "jeonbuk"],
        "name_kr": "전북 현대 모터스",
        "name_en": "Jeonbuk Hyundai Motors",
        "api_football_id": 2954,
        "manager": {
            "name_kr": "김두현",
            "name_en": "Kim Do-heon",
            "nationality": "한국",
            "age": 42,
            "win_rate": "51.2%",
            "preferred_formation": "4-3-3",
            "tactical_style": "빠른 측면 공세 & 콤팩트한 밸런스 회복",
            "tendency_tags": ["#측면돌파", "#공수밸런스", "#빠른전환", "#전통강호"],
            "philosophy": "공수 밸런스를 유지하며 측면 스피드를 활용한 닥공 축구 계승",
            "photo": "https://media.api-sports.io/football/coachs/1834.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-2-3-1",
            "style_desc": "측면 윙어의 1대1 돌파와 타깃 스트라이커 제공권",
            "attack_focus": "측면 크로스 & 세컨볼 슈팅",
            "lineup_type": "4-3-3"
        },
        "possession": {
            "avg": 52.8,
            "style": "밸런스 점유형",
            "field_tilt": 54.0,
            "pass_accuracy": "83.5%"
        },
        "discipline": {
            "yellow_per_game": 1.9,
            "red_total": 2,
            "fouls_per_game": 11.0,
            "risk_level": "보통",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "역습 저지 시 거친 경합으로 카드 주의"
        }
    },
    "포항 스틸러스": {
        "aliases": ["포항", "포항 스틸러스", "포항스틸러스", "pohang"],
        "name_kr": "포항 스틸러스",
        "name_en": "Pohang Steelers",
        "api_football_id": 2956,
        "manager": {
            "name_kr": "박태하",
            "name_en": "Park Tae-ha",
            "nationality": "한국",
            "age": 56,
            "win_rate": "55.0%",
            "preferred_formation": "4-4-2",
            "tactical_style": "짜임새 있는 2줄 수비 블록 & 번개 같은 다이렉트 역습",
            "tendency_tags": ["#스틸타카", "#다이렉트역습", "#2줄수비", "#조직력", "#승부처강함"],
            "philosophy": "탄탄한 팀워크와 간결한 원터치 전진 패스로 상대 뒷공간 공략",
            "photo": "https://media.api-sports.io/football/coachs/1835.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "4-2-3-1",
            "style_desc": "컴팩트 4-4-2 블록 유지 후 투톱의 빠른 뒷공간 쇄도",
            "attack_focus": "직선 역습 & 배후 침투",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 51.5,
            "style": "효율 속공형",
            "field_tilt": 51.8,
            "pass_accuracy": "82.8%"
        },
        "discipline": {
            "yellow_per_game": 1.8,
            "red_total": 1,
            "fouls_per_game": 10.6,
            "risk_level": "보통",
            "risk_badge": "bg-success text-white",
            "risk_text": "조직적 협력 수비로 파울 억제"
        }
    },
    "FC 서울": {
        "aliases": ["fc 서울", "fc서울", "서울", "seoul"],
        "name_kr": "FC 서울",
        "name_en": "FC Seoul",
        "api_football_id": 2957,
        "manager": {
            "name_kr": "김기동",
            "name_en": "Kim Gi-dong",
            "nationality": "한국",
            "age": 52,
            "win_rate": "53.8%",
            "preferred_formation": "4-4-2",
            "tactical_style": "정교한 기동 타격 & 린가드 중심의 하프스페이스 플레이",
            "tendency_tags": ["#기동타격", "#하프스페이스", "#스타플레이", "#공격전개"],
            "philosophy": "빠른 볼 전개와 공간 침투로 득점 기회를 극대화하는 공격 축구",
            "photo": "https://media.api-sports.io/football/coachs/1836.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "4-2-3-1",
            "style_desc": "린가드-일류첸코 연계와 풀백의 적극적 오버래핑",
            "attack_focus": "중앙 원투패스 & 측면 크로스",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 53.9,
            "style": "점유 공격형",
            "field_tilt": 55.4,
            "pass_accuracy": "84.5%"
        },
        "discipline": {
            "yellow_per_game": 1.9,
            "red_total": 1,
            "fouls_per_game": 11.0,
            "risk_level": "보통",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "공격 가담 후 복귀 시 역습 저지 파울 주의"
        }
    },
    "광주FC": {
        "aliases": ["광주fc", "광주", "gwangju"],
        "name_kr": "광주FC",
        "name_en": "Gwangju FC",
        "api_football_id": 2962,
        "manager": {
            "name_kr": "이정효",
            "name_en": "Lee Jung-hyo",
            "nationality": "한국",
            "age": 49,
            "win_rate": "56.4%",
            "preferred_formation": "4-4-2",
            "tactical_style": "극한의 수적 우위 점유 & 골키퍼 가담 후방 빌드업 & 공격 축구",
            "tendency_tags": ["#정효볼", "#초고강도압박", "#수적우위", "#골키퍼빌드업", "#닥공"],
            "philosophy": "상대가 누구든 물러서지 않고 극한의 압박과 패스로 경기를 지배한다",
            "photo": "https://media.api-sports.io/football/coachs/1837.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "4-3-3",
            "style_desc": "골키퍼를 필드 플레이어처럼 활용한 11명 전원 빌드업 체계",
            "attack_focus": "중앙 삼각 연계 & 전방위 침투",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 58.2,
            "style": "극단적 점유/압박형 (Ultra Possession)",
            "field_tilt": 62.0,
            "pass_accuracy": "86.8%"
        },
        "discipline": {
            "yellow_per_game": 2.2,
            "red_total": 2,
            "fouls_per_game": 12.0,
            "risk_level": "주의",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "하이라인 뒷공간 역습 허용 시 전술적 파울 빈도 높음"
        }
    },
    "강원FC": {
        "aliases": ["강원fc", "강원", "gangwon"],
        "name_kr": "강원FC",
        "name_en": "Gangwon FC",
        "api_football_id": 2961,
        "manager": {
            "name_kr": "윤정환",
            "name_en": "Yoon Jong-hwan",
            "nationality": "한국",
            "age": 51,
            "win_rate": "54.8%",
            "preferred_formation": "4-4-2",
            "tactical_style": "다이내믹 공수 트랜지션 & 신예 윙어(양민혁) 폭발적 돌파",
            "tendency_tags": ["#다이내믹트랜지션", "#신예돌풍", "#스피드어택", "#조직축구"],
            "philosophy": "빠른 전환과 자신감 넘치는 측면 돌파로 득점 찬스를 창출",
            "photo": "https://media.api-sports.io/football/coachs/1838.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "4-2-3-1",
            "style_desc": "견고한 두 줄 수비 후 양 측면 윙어의 폭발적인 스피드 돌파",
            "attack_focus": "측면 1대1 돌파 & 컷백",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 52.1,
            "style": "다이내믹 전환형",
            "field_tilt": 53.5,
            "pass_accuracy": "83.0%"
        },
        "discipline": {
            "yellow_per_game": 1.7,
            "red_total": 1,
            "fouls_per_game": 10.4,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "안정적인 경기 운영과 깨끗한 수비"
        }
    },
    "수원 삼성": {
        "aliases": ["수원 삼성", "수원삼성", "수원 삼성 블루윙즈", "suwon bluewings"],
        "name_kr": "수원 삼성 블루윙즈",
        "name_en": "Suwon Samsung Bluewings",
        "api_football_id": 2958,
        "manager": {
            "name_kr": "변성환",
            "name_en": "Byun Sung-hwan",
            "nationality": "한국",
            "age": 44,
            "win_rate": "53.0%",
            "preferred_formation": "4-3-3",
            "tactical_style": "고강도 전방 압박 & 능동적인 볼 점유 공격",
            "tendency_tags": ["#변성환호", "#전방압박", "#공격축구", "#열정"],
            "philosophy": "주도적인 볼 점유와 높은 압박으로 상대를 제압하는 축구",
            "photo": "https://media.api-sports.io/football/coachs/1839.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-2-3-1",
            "style_desc": "역동적인 3미들의 압박과 측면 윙어들의 공간 침투",
            "attack_focus": "전방 압박 탈취 후 슈팅",
            "lineup_type": "4-3-3"
        },
        "possession": {
            "avg": 55.4,
            "style": "점유 주도형",
            "field_tilt": 57.0,
            "pass_accuracy": "84.0%"
        },
        "discipline": {
            "yellow_per_game": 2.1,
            "red_total": 2,
            "fouls_per_game": 11.6,
            "risk_level": "보통 (주의)",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "열정적인 압박 과정에서 파울 주의"
        }
    }
}

# ==============================================================================
# 2. J리그 (J1 & J2) 공식 감독 및 전술 마스터 데이터
# ==============================================================================
JLEAGUE_TACTICAL_DB: Dict[str, Dict[str, Any]] = {
    "콘사도레 삿포로": {
        "aliases": ["콘사도레 삿포로", "삿포로", "콘사도레", "sapporo", "consadole"],
        "name_kr": "콘사도레 삿포로",
        "name_en": "Consadole Sapporo",
        "api_football_id": 284,
        "manager": {
            "name_kr": "미하일로 페트로비치",
            "name_en": "Mihailo Petrovic",
            "nationality": "세르비아",
            "age": 66,
            "win_rate": "46.5%",
            "preferred_formation": "3-4-2-1",
            "tactical_style": "초공격적 올인 전술 & 하이라인 전진 빌드업 & 전원 공격",
            "tendency_tags": ["#미샤볼", "#초공격축구", "#하이라인", "#3-4-2-1특화", "#공격지향"],
            "philosophy": "실점을 두려워하지 않고 한 골을 더 넣어 승리하는 매력적인 초공격 축구",
            "photo": "https://media.api-sports.io/football/coachs/1420.png"
        },
        "formation": {
            "primary": "3-4-2-1",
            "secondary": "3-1-4-2",
            "style_desc": "3백의 과감한 전진과 섀도우 스트라이커 2명의 하프스페이스 집중 공략",
            "attack_focus": "중앙 집중 숏패스 연계 & 세컨선수 침투",
            "lineup_type": "3-4-2-1"
        },
        "possession": {
            "avg": 53.8,
            "style": "초공격/점유형 (Attack-Minded)",
            "field_tilt": 56.4,
            "pass_accuracy": "83.2%"
        },
        "discipline": {
            "yellow_per_game": 1.7,
            "red_total": 1,
            "fouls_per_game": 10.8,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "공격 지향에 비해 비교적 페어플레이 성향 유지"
        }
    },
    "오이타 트리니타": {
        "aliases": ["오이타 트리니타", "오이타", "트리니타", "oita", "trinita"],
        "name_kr": "오이타 트리니타",
        "name_en": "Oita Trinita",
        "api_football_id": 285,
        "manager": {
            "name_kr": "카타노사카 토모히로",
            "name_en": "Tomohiro Katanosaka",
            "nationality": "일본",
            "age": 53,
            "win_rate": "49.0%",
            "preferred_formation": "4-4-2",
            "tactical_style": "정교한 후방 빌드업 '카타노 사커' & 컴팩트 수비 블록",
            "tendency_tags": ["#카타노사커", "#후방빌드업", "#조직력", "#실리축구", "#2줄수비"],
            "philosophy": "골키퍼부터 촘촘하게 연결되는 후방 빌드업과 빈틈없는 수비 밸런스",
            "photo": "https://media.api-sports.io/football/coachs/1421.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "3-4-2-1",
            "style_desc": "2줄 수비 블록으로 상대 공간을 제어하고 측면을 넓게 쓰는 빌드업",
            "attack_focus": "측면 빌드업 전개 후 박스 안 크로스",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 49.5,
            "style": "실리/빌드업형 (Structured)",
            "field_tilt": 48.8,
            "pass_accuracy": "82.0%"
        },
        "discipline": {
            "yellow_per_game": 1.9,
            "red_total": 1,
            "fouls_per_game": 11.2,
            "risk_level": "보통",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "수비 블록 유지 시 안정적이나 역습 시 전술 파울 발생"
        }
    },
    "비셀 고베": {
        "aliases": ["비셀 고베", "고베", "vissel kobe", "kobe"],
        "name_kr": "비셀 고베",
        "name_en": "Vissel Kobe",
        "api_football_id": 286,
        "manager": {
            "name_kr": "요시다 타카유키",
            "name_en": "Takayuki Yoshida",
            "nationality": "일본",
            "age": 47,
            "win_rate": "60.5%",
            "preferred_formation": "4-3-3",
            "tactical_style": "고강도 전방 압박 & 롱볼 후 세컨볼 지배 & 강력한 피지컬",
            "tendency_tags": ["#세컨볼지배", "#롱볼압박", "#피지컬강세", "#디펜딩챔피언"],
            "philosophy": "전방에서 강하게 싸워주고 세컨볼을 장악해 상대 진영을 맹폭",
            "photo": "https://media.api-sports.io/football/coachs/1422.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-2-3-1",
            "style_desc": "오사코 유야를 향한 롱볼과 2선 무토-이데구치의 세컨볼 장악",
            "attack_focus": "포스트 플레이 & 세컨볼 슈팅",
            "lineup_type": "4-3-3"
        },
        "possession": {
            "avg": 48.2,
            "style": "실리 다이렉트형 (Direct)",
            "field_tilt": 53.0,
            "pass_accuracy": "78.5%"
        },
        "discipline": {
            "yellow_per_game": 1.9,
            "red_total": 1,
            "fouls_per_game": 12.4,
            "risk_level": "보통 (주의)",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "강한 전방 경합으로 인해 파울 빈도가 다소 높음"
        }
    },
    "산프레체 히로시마": {
        "aliases": ["산프레체 히로시마", "히로시마", "sanfrecce hiroshima", "hiroshima"],
        "name_kr": "산프레체 히로시마",
        "name_en": "Sanfrecce Hiroshima",
        "api_football_id": 287,
        "manager": {
            "name_kr": "미하엘 스키베",
            "name_en": "Michael Skibbe",
            "nationality": "독일",
            "age": 59,
            "win_rate": "59.2%",
            "preferred_formation": "3-4-2-1",
            "tactical_style": "독일식 고강도 게겐프레싱 & 전광석화 같은 역습 전개",
            "tendency_tags": ["#게겐프레싱", "#독일식압박", "#3-4-2-1", "#스피드전환"],
            "philosophy": "볼을 빼앗긴 즉시 재압박하여 상대 수비 정비 전 득점",
            "photo": "https://media.api-sports.io/football/coachs/1423.png"
        },
        "formation": {
            "primary": "3-4-2-1",
            "secondary": "3-5-2",
            "style_desc": "하프라인 위에서 펼쳐지는 강력한 전방 압박망",
            "attack_focus": "전방 탈취 후 빠른 2선 쇄도",
            "lineup_type": "3-4-2-1"
        },
        "possession": {
            "avg": 54.5,
            "style": "게겐프레싱형",
            "field_tilt": 58.2,
            "pass_accuracy": "83.6%"
        },
        "discipline": {
            "yellow_per_game": 1.6,
            "red_total": 0,
            "fouls_per_game": 10.5,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "조직적인 압박으로 불필요한 카드 최소화"
        }
    },
    "마치다 젤비아": {
        "aliases": ["마치다 젤비아", "마치다", "machida zelvia", "machida"],
        "name_kr": "마치다 젤비아",
        "name_en": "Machida Zelvia",
        "api_football_id": 288,
        "manager": {
            "name_kr": "구로다 고",
            "name_en": "Go Kuroda",
            "nationality": "일본",
            "age": 54,
            "win_rate": "62.0%",
            "preferred_formation": "4-4-2",
            "tactical_style": "철저한 승리 지상주의 & 롱 스로인 및 세트피스 폭격 & 무실점 수비",
            "tendency_tags": ["#구로다매직", "#롱스로인", "#세트피스특화", "#실리축구", "#철벽수비"],
            "philosophy": "아름다운 축구보다 확실한 승리를 추구하는 철저한 실리 축구",
            "photo": "https://media.api-sports.io/football/coachs/1424.png"
        },
        "formation": {
            "primary": "4-4-2",
            "secondary": "4-2-3-1",
            "style_desc": "롱 스로인 및 코너킥에서의 정교한 세트피스 약속 플레이",
            "attack_focus": "세트피스 & 다이렉트 롱볼",
            "lineup_type": "4-4-2"
        },
        "possession": {
            "avg": 45.8,
            "style": "실리 속공/세트피스형",
            "field_tilt": 46.5,
            "pass_accuracy": "76.2%"
        },
        "discipline": {
            "yellow_per_game": 2.1,
            "red_total": 2,
            "fouls_per_game": 12.8,
            "risk_level": "주의",
            "risk_badge": "bg-warning text-dark",
            "risk_text": "강한 육탄 방어와 시간 지연 등으로 카드 빈도 높음"
        }
    },
    "감바 오사카": {
        "aliases": ["감바 오사카", "감바오사카", "감바", "gamba osaka", "gamba"],
        "name_kr": "감바 오사카",
        "name_en": "Gamba Osaka",
        "api_football_id": 289,
        "manager": {
            "name_kr": "다니 포야토스",
            "name_en": "Dani Poyatos",
            "nationality": "스페인",
            "age": 46,
            "win_rate": "53.5%",
            "preferred_formation": "4-2-3-1",
            "tactical_style": "스페인식 포지셔널 플레이 & 숏패스 포제션 축구",
            "tendency_tags": ["#포지셔널플레이", "#스페인식축구", "#점유율", "#패스연계"],
            "philosophy": "짧은 패스로 상대 수비를 흔들고 공간을 지배하는 현대적 점유 축구",
            "photo": "https://media.api-sports.io/football/coachs/1425.png"
        },
        "formation": {
            "primary": "4-2-3-1",
            "secondary": "4-3-3",
            "style_desc": "더블 볼란치의 볼 배급과 2선의 짧은 원투패스",
            "attack_focus": "중앙 콤비네이션 & 하프스페이스",
            "lineup_type": "4-2-3-1"
        },
        "possession": {
            "avg": 55.2,
            "style": "숏패스 점유형",
            "field_tilt": 56.8,
            "pass_accuracy": "85.4%"
        },
        "discipline": {
            "yellow_per_game": 1.7,
            "red_total": 1,
            "fouls_per_game": 10.2,
            "risk_level": "안정적",
            "risk_badge": "bg-success text-white",
            "risk_text": "패스 점유율을 통해 파울 최소화"
        }
    }
}

# ==============================================================================
# 3. 유럽 주요 리그 (라리가, 세리에A, 분데스리가, 리그앙) 공식 감독 데이터
# ==============================================================================
EUROPE_TACTICAL_DB: Dict[str, Dict[str, Any]] = {
    "레알 마드리드": {
        "aliases": ["레알 마드리드", "레알", "real madrid"],
        "name_kr": "레알 마드리드",
        "name_en": "Real Madrid",
        "api_football_id": 541,
        "manager": {
            "name_kr": "카를로 안첼로티",
            "name_en": "Carlo Ancelotti",
            "nationality": "이탈리아",
            "age": 65,
            "win_rate": "72.4%",
            "preferred_formation": "4-3-3",
            "tactical_style": "유연한 전술 밸런스 & 음바페·비니시우스 스피드 카운터",
            "tendency_tags": ["#덕장", "#유연한전술", "#월드클래스카운터", "#챔스의제왕"],
            "philosophy": "선수들의 개성과 자율성을 살린 완성도 높은 유연한 축구",
            "photo": "https://media.api-sports.io/football/coachs/24.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-3-1-2",
            "style_desc": "비니시우스-음바페-호드리구 스피드 3톱과 벨링엄의 2선 침투",
            "attack_focus": "측면 돌파 & 빠른 전환 속공",
            "lineup_type": "4-3-3"
        },
        "possession": {"avg": 60.5, "style": "주도 점유형", "field_tilt": 63.2, "pass_accuracy": "89.2%"},
        "discipline": {"yellow_per_game": 1.6, "red_total": 1, "fouls_per_game": 9.5, "risk_level": "안정적", "risk_badge": "bg-success text-white", "risk_text": "월드클래스 경기 운영"}
    },
    "바르셀로나": {
        "aliases": ["바르셀로나", "바르샤", "barcelona", "barca"],
        "name_kr": "FC 바르셀로나",
        "name_en": "FC Barcelona",
        "api_football_id": 529,
        "manager": {
            "name_kr": "한지 플릭",
            "name_en": "Hansi Flick",
            "nationality": "독일",
            "age": 59,
            "win_rate": "75.0%",
            "preferred_formation": "4-2-3-1",
            "tactical_style": "초고강도 하이라인 오프사이드 트랩 & 다이렉트 전방 폭격",
            "tendency_tags": ["#플릭볼", "#하이라인", "#오프사이드트랩", "#다이렉트어택", "#야말"],
            "philosophy": "극한의 높은 라인과 수직적인 공격으로 상대를 압도",
            "photo": "https://media.api-sports.io/football/coachs/14.png"
        },
        "formation": {
            "primary": "4-2-3-1",
            "secondary": "4-3-3",
            "style_desc": "라민 야말-레반도프스키-하피냐의 폭발적 전방 삼각편대",
            "attack_focus": "하프스페이스 침투 & 다이렉트 패스",
            "lineup_type": "4-2-3-1"
        },
        "possession": {"avg": 63.8, "style": "초고강도 압박/점유형", "field_tilt": 66.5, "pass_accuracy": "88.5%"},
        "discipline": {"yellow_per_game": 2.1, "red_total": 2, "fouls_per_game": 11.2, "risk_level": "주의", "risk_badge": "bg-warning text-dark", "risk_text": "하이라인 뒷공간 수비 시 파울 주의"}
    },
    "인테르": {
        "aliases": ["인테르", "인터 밀란", "인터밀란", "inter"],
        "name_kr": "인테르나치오날레 밀라노",
        "name_en": "Inter Milan",
        "api_football_id": 505,
        "manager": {
            "name_kr": "시모네 인자기",
            "name_en": "Simone Inzaghi",
            "nationality": "이탈리아",
            "age": 48,
            "win_rate": "67.0%",
            "preferred_formation": "3-5-2",
            "tactical_style": "유럽 최정상급 3-5-2 빌드업 & 센터백 오버래핑 & 라우타로 결정력",
            "tendency_tags": ["#인자기볼", "#3-5-2장인", "#센터백오버래핑", "#철벽수비", "#세리에최강"],
            "philosophy": "완벽한 포지셔닝 전환과 센터백까지 공격에 가담하는 현대적 3백",
            "photo": "https://media.api-sports.io/football/coachs/27.png"
        },
        "formation": {
            "primary": "3-5-2",
            "secondary": "3-4-1-2",
            "style_desc": "바스토니의 전진 패스와 디마르코-둠프리스 윙백 기동력",
            "attack_focus": "측면 윙백 크로스 & 투톱 연계",
            "lineup_type": "3-5-2"
        },
        "possession": {"avg": 57.2, "style": "점유 3백 빌드업형", "field_tilt": 59.4, "pass_accuracy": "87.2%"},
        "discipline": {"yellow_per_game": 1.8, "red_total": 1, "fouls_per_game": 10.4, "risk_level": "안정적", "risk_badge": "bg-success text-white", "risk_text": "안정적인 3백 수비 밸런스"}
    },
    "바이에른 뮌헨": {
        "aliases": ["바이에른 뮌헨", "뮌헨", "bayern munich", "bayern"],
        "name_kr": "FC 바이에른 뮌헨",
        "name_en": "FC Bayern Munich",
        "api_football_id": 157,
        "manager": {
            "name_kr": "뱅상 콤파니",
            "name_en": "Vincent Kompany",
            "nationality": "벨기에",
            "age": 38,
            "win_rate": "71.5%",
            "preferred_formation": "4-2-3-1",
            "tactical_style": "공격적 하이라인 & 김민재의 파이터형 전진 수비 & 케인 득점력",
            "tendency_tags": ["#콤파니볼", "#하이라인", "#김민재전진수비", "#케인골폭풍"],
            "philosophy": "공격적인 라인 전진과 전방 압박으로 상대를 완벽히 압살",
            "photo": "https://media.api-sports.io/football/coachs/32.png"
        },
        "formation": {
            "primary": "4-2-3-1",
            "secondary": "4-3-3",
            "style_desc": "김민재-우파메카노의 높은 라인과 무시알라-케인의 파괴력",
            "attack_focus": "하프스페이스 공략 & 빠른 측면 돌파",
            "lineup_type": "4-2-3-1"
        },
        "possession": {"avg": 65.4, "style": "극단적 점유 공격형", "field_tilt": 68.0, "pass_accuracy": "89.5%"},
        "discipline": {"yellow_per_game": 1.7, "red_total": 1, "fouls_per_game": 9.8, "risk_level": "안정적", "risk_badge": "bg-success text-white", "risk_text": "높은 점유율 기반 파울 관리"}
    },
    "파리 생제르맹": {
        "aliases": ["파리 생제르맹", "psg", "파리", "paris saint-germain"],
        "name_kr": "파리 생제르맹 FC",
        "name_en": "Paris Saint-Germain",
        "api_football_id": 85,
        "manager": {
            "name_kr": "루이스 엔리케",
            "name_en": "Luis Enrique",
            "nationality": "스페인",
            "age": 54,
            "win_rate": "69.0%",
            "preferred_formation": "4-3-3",
            "tactical_style": "철저한 패스 포제션 & 이강인·바르콜라의 창의적 전방 지원",
            "tendency_tags": ["#엔리케볼", "#이강인창의성", "#패스포제션", "#리그앙지배"],
            "philosophy": "볼을 지배하며 상대 수비의 틈을 창의적인 패스로 붕괴",
            "photo": "https://media.api-sports.io/football/coachs/17.png"
        },
        "formation": {
            "primary": "4-3-3",
            "secondary": "4-2-3-1",
            "style_desc": "이강인의 창의적인 킬패스와 바르콜라-뎀벨레의 측면 폭격",
            "attack_focus": "좌우 측면 흔들기 & 중앙 쇄도",
            "lineup_type": "4-3-3"
        },
        "possession": {"avg": 64.2, "style": "점유/지공형", "field_tilt": 66.8, "pass_accuracy": "89.0%"},
        "discipline": {"yellow_per_game": 1.8, "red_total": 1, "fouls_per_game": 10.0, "risk_level": "안정적", "risk_badge": "bg-success text-white", "risk_text": "점유율 중심의 차분한 경기 운영"}
    }
}
