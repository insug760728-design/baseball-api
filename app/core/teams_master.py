# -*- coding: utf-8 -*-
"""
야구 전문 전체 구단 및 주요 로스터 마스터
"""

LEAGUE_TEAMS_DATA = {
    "MLB": {
        "league_name": "미국 메이저리그 (MLB)",
        "sport_code": "BASEBALL",
        "teams": [
            {
                "team_name": "LA 다저스",
                "city": "Los Angeles", "stadium": "다저 스타디움",
                "players": [
                    {"name": "오타니 쇼헤이", "num": 17, "pos": "1번 DH"},
                    {"name": "무키 베츠", "num": 50, "pos": "2번 SS"},
                    {"name": "프레디 프리먼", "num": 5, "pos": "3번 1B"},
                    {"name": "테오스카 에르난데스", "num": 37, "pos": "4번 RF"},
                    {"name": "맥스 먼시", "num": 13, "pos": "5번 3B"},
                    {"name": "윌 스미스", "num": 16, "pos": "6번 C"},
                    {"name": "개빈 럭스", "num": 9, "pos": "7번 2B"},
                    {"name": "토미 에드먼", "num": 25, "pos": "8번 CF"},
                    {"name": "앤디 파헤스", "num": 84, "pos": "9번 LF"},
                    {"name": "야마모토 요시노부", "num": 18, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "샌디에이고 파드리스",
                "city": "San Diego", "stadium": "펫코 파크",
                "players": [
                    {"name": "루이스 아라에즈", "num": 4, "pos": "1번 DH"},
                    {"name": "페르난도 타티스 주니어", "num": 23, "pos": "2번 RF"},
                    {"name": "주릭슨 프로파", "num": 10, "pos": "3번 LF"},
                    {"name": "매니 마차도", "num": 13, "pos": "4번 3B"},
                    {"name": "잭슨 메릴", "num": 3, "pos": "5번 CF"},
                    {"name": "잰더 보가츠", "num": 2, "pos": "6번 2B"},
                    {"name": "제이크 크로넨워스", "num": 9, "pos": "7번 1B"},
                    {"name": "김하성", "num": 7, "pos": "8번 SS"},
                    {"name": "카일 히가시오카", "num": 20, "pos": "9번 C"},
                    {"name": "다르빗슈 유", "num": 11, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "샌프란시스코 자이언츠",
                "city": "San Francisco", "stadium": "오라클 파크",
                "players": [
                    {"name": "이정후", "num": 51, "pos": "1번 CF"},
                    {"name": "라몬테 웨이드 주니어", "num": 31, "pos": "2번 1B"},
                    {"name": "맷 채프먼", "num": 26, "pos": "3번 3B"},
                    {"name": "마이클 콘포토", "num": 8, "pos": "4번 LF"},
                    {"name": "호르헤 솔레어", "num": 2, "pos": "5번 DH"},
                    {"name": "타일러 피츠제럴드", "num": 49, "pos": "6번 SS"},
                    {"name": "패트릭 베일리", "num": 14, "pos": "7번 C"},
                    {"name": "마이크 야스트렘스키", "num": 5, "pos": "8번 RF"},
                    {"name": "브렛 와이즐리", "num": 70, "pos": "9번 2B"},
                    {"name": "로건 웹", "num": 62, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "뉴욕 양키스",
                "city": "New York", "stadium": "양키 스타디움",
                "players": [
                    {"name": "글레이버 토레스", "num": 25, "pos": "1번 2B"},
                    {"name": "후안 소토", "num": 22, "pos": "2번 RF"},
                    {"name": "애런 저지", "num": 99, "pos": "3번 CF"},
                    {"name": "지안카를로 스탠튼", "num": 27, "pos": "4번 DH"},
                    {"name": "재즈 치좀 주니어", "num": 13, "pos": "5번 3B"},
                    {"name": "앤서니 볼피", "num": 11, "pos": "6번 SS"},
                    {"name": "오스틴 웰스", "num": 28, "pos": "7번 C"},
                    {"name": "알렉스 버두고", "num": 24, "pos": "8번 LF"},
                    {"name": "앤서니 리조", "num": 48, "pos": "9번 1B"},
                    {"name": "게릿 콜", "num": 45, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "보스턴 레드삭스",
                "city": "Boston", "stadium": "펜웨이 파크",
                "players": [
                    {"name": "재런 듀란", "num": 16, "pos": "1번 CF"},
                    {"name": "라파엘 데버스", "num": 11, "pos": "2번 3B"},
                    {"name": "타일러 오닐", "num": 17, "pos": "3번 LF"},
                    {"name": "요시다 마사타카", "num": 7, "pos": "4번 DH"},
                    {"name": "윌리어 아브레유", "num": 52, "pos": "5번 RF"},
                    {"name": "코너 웡", "num": 12, "pos": "6번 C"},
                    {"name": "트레버 스토리", "num": 10, "pos": "7번 SS"},
                    {"name": "트리스톤 카사스", "num": 36, "pos": "8번 1B"},
                    {"name": "에마누엘 발데스", "num": 47, "pos": "9번 2B"},
                    {"name": "태너 하우크", "num": 89, "pos": "선발 P"}
                ]
            }
        ]
    },
    "KBO": {
        "league_name": "한국 프로야구 (KBO 리그)",
        "sport_code": "BASEBALL",
        "teams": [
            {
                "team_name": "LG 트윈스",
                "city": "서울", "stadium": "잠실야구장",
                "players": [
                    {"name": "홍창기", "num": 51, "pos": "1번 RF"},
                    {"name": "신민재", "num": 4, "pos": "2번 2B"},
                    {"name": "오스틴 딘", "num": 23, "pos": "3번 1B"},
                    {"name": "문보경", "num": 2, "pos": "4번 3B"},
                    {"name": "오지환", "num": 10, "pos": "5번 SS"},
                    {"name": "박동원", "num": 27, "pos": "6번 C"},
                    {"name": "김현수", "num": 22, "pos": "7번 DH"},
                    {"name": "박해민", "num": 17, "pos": "8번 CF"},
                    {"name": "문성주", "num": 8, "pos": "9번 LF"},
                    {"name": "임찬규", "num": 29, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "KIA 타이거즈",
                "city": "광주", "stadium": "광주기아챔피언스필드",
                "players": [
                    {"name": "박찬호", "num": 1, "pos": "1번 SS"},
                    {"name": "김도영", "num": 5, "pos": "2번 3B"},
                    {"name": "김선빈", "num": 3, "pos": "3번 2B"},
                    {"name": "최형우", "num": 34, "pos": "4번 DH"},
                    {"name": "소크라테스", "num": 30, "pos": "5번 CF"},
                    {"name": "이우성", "num": 25, "pos": "6번 1B"},
                    {"name": "나성범", "num": 47, "pos": "7번 RF"},
                    {"name": "김태군", "num": 42, "pos": "8번 C"},
                    {"name": "최원준", "num": 2, "pos": "9번 LF"},
                    {"name": "양현종", "num": 54, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "두산 베어스",
                "city": "서울", "stadium": "잠실야구장",
                "players": [
                    {"name": "정수빈", "num": 31, "pos": "1번 CF"},
                    {"name": "이유찬", "num": 7, "pos": "2번 2B"},
                    {"name": "양의지", "num": 25, "pos": "3번 C"},
                    {"name": "김재환", "num": 32, "pos": "4번 DH"},
                    {"name": "양석환", "num": 53, "pos": "5번 1B"},
                    {"name": "강승호", "num": 23, "pos": "6번 3B"},
                    {"name": "전민재", "num": 9, "pos": "7번 SS"},
                    {"name": "조수행", "num": 51, "pos": "8번 LF"},
                    {"name": "김대한", "num": 37, "pos": "9번 RF"},
                    {"name": "곽빈", "num": 47, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "삼성 라이온즈",
                "city": "대구", "stadium": "대구삼성라이온즈파크",
                "players": [
                    {"name": "김지찬", "num": 58, "pos": "1번 CF"},
                    {"name": "이재현", "num": 7, "pos": "2번 SS"},
                    {"name": "구자욱", "num": 5, "pos": "3번 LF"},
                    {"name": "디아즈", "num": 43, "pos": "4번 1B"},
                    {"name": "박병호", "num": 59, "pos": "5번 DH"},
                    {"name": "강민호", "num": 47, "pos": "6번 C"},
                    {"name": "김영웅", "num": 30, "pos": "7번 3B"},
                    {"name": "이성규", "num": 13, "pos": "8번 RF"},
                    {"name": "류지혁", "num": 16, "pos": "9번 2B"},
                    {"name": "원태인", "num": 18, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "한화 이글스",
                "city": "대전", "stadium": "한화생명이글스파크",
                "players": [
                    {"name": "이진영", "num": 50, "pos": "1번 RF"},
                    {"name": "문현빈", "num": 64, "pos": "2번 2B"},
                    {"name": "노시환", "num": 8, "pos": "3번 3B"},
                    {"name": "채은성", "num": 22, "pos": "4번 1B"},
                    {"name": "안치홍", "num": 3, "pos": "5번 DH"},
                    {"name": "김태연", "num": 25, "pos": "6번 LF"},
                    {"name": "최재훈", "num": 13, "pos": "7번 C"},
                    {"name": "이도윤", "num": 7, "pos": "8번 SS"},
                    {"name": "장진혁", "num": 39, "pos": "9번 CF"},
                    {"name": "류현진", "num": 99, "pos": "선발 P"}
                ]
            }
        ]
    },
    "NPB": {
        "league_name": "일본 프로야구 (NPB)",
        "sport_code": "BASEBALL",
        "teams": [
            {
                "team_name": "요미우리 자이언츠",
                "city": "도쿄", "stadium": "도쿄돔",
                "players": [
                    {"name": "마루 요시히로", "num": 8, "pos": "1번 RF"},
                    {"name": "요시카와 나오키", "num": 2, "pos": "2번 2B"},
                    {"name": "몬테스", "num": 39, "pos": "3번 LF"},
                    {"name": "오카모토 카즈마", "num": 25, "pos": "4번 1B"},
                    {"name": "사카모토 하야토", "num": 6, "pos": "5번 3B"},
                    {"name": "오시로 타쿠미", "num": 24, "pos": "6번 C"},
                    {"name": "코바야시 세이지", "num": 22, "pos": "7번 C"},
                    {"name": "카도와키 마코토", "num": 35, "pos": "8번 SS"},
                    {"name": "스가노 토모유키", "num": 19, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "한신 타이거스",
                "city": "오사카/효고", "stadium": "한신 고시엔 구장",
                "players": [
                    {"name": "치카모토 코지", "num": 5, "pos": "1번 CF"},
                    {"name": "나카노 타쿠무", "num": 51, "pos": "2번 2B"},
                    {"name": "모리시타 쇼타", "num": 1, "pos": "3번 RF"},
                    {"name": "오야마 유스케", "num": 3, "pos": "4번 1B"},
                    {"name": "사토 테루아키", "num": 8, "pos": "5번 3B"},
                    {"name": "마에가와 우쿄", "num": 58, "pos": "6번 LF"},
                    {"name": "우메노 류타로", "num": 2, "pos": "7번 C"},
                    {"name": "키나미 세이야", "num": 0, "pos": "8번 SS"},
                    {"name": "사이가키 히로토", "num": 35, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "주니치 드래곤즈",
                "city": "나고야", "stadium": "반테린 돔 나고야",
                "players": [
                    {"name": "오카바야시 유키", "num": 1, "pos": "1번 CF"},
                    {"name": "호소카와 세이야", "num": 55, "pos": "4번 LF"},
                    {"name": "타카하시 히로토", "num": 19, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "요코하마 DeNA 베이스타즈",
                "city": "요코하마", "stadium": "요코하마 스타디움",
                "players": [
                    {"name": "마키 슈고", "num": 2, "pos": "4번 2B"},
                    {"name": "사노 케이타", "num": 7, "pos": "3번 LF"},
                    {"name": "아즈마 카츠키", "num": 11, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "히로시마 도요 카프",
                "city": "히로시마", "stadium": "MAZDA Zoom-Zoom 스타디움",
                "players": [
                    {"name": "코조노 카이토", "num": 51, "pos": "3번 SS"},
                    {"name": "사카쿠라 쇼고", "num": 31, "pos": "4번 C"},
                    {"name": "토코다 히로키", "num": 28, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "도쿄 야쿠르트 스왈로스",
                "city": "도쿄", "stadium": "메이지 진구 야구장",
                "players": [
                    {"name": "무라카미 무네타카", "num": 55, "pos": "4번 3B"},
                    {"name": "야마다 테츠토", "num": 1, "pos": "3번 2B"},
                    {"name": "오가와 야스히로", "num": 29, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "후쿠오카 소프트뱅크 호크스",
                "city": "후쿠오카", "stadium": "미즈호 PayPay 돔 후쿠오카",
                "players": [
                    {"name": "야나기타 유키", "num": 9, "pos": "3번 RF"},
                    {"name": "콘도 켄스케", "num": 3, "pos": "4번 DH"},
                    {"name": "아리하라 코헤이", "num": 17, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "홋카이도 닛폰햄 파이터즈",
                "city": "홋카이도", "stadium": "에스콘 필드 HOKKAIDO",
                "players": [
                    {"name": "만나미 츄세이", "num": 66, "pos": "4번 RF"},
                    {"name": "키요미야 코타로", "num": 21, "pos": "3번 3B"},
                    {"name": "이토 히로미", "num": 17, "pos": "선발 P"}
                ]
            },
            {
                "team_name": "지바 롯데 마린스",
                "city": "지바", "stadium": "ZOZO 마린 스타디움",
                "players": [
                    {"name": "사사키 로키", "num": 17, "pos": "선발 P"},
                    {"name": "네프탈리 소토", "num": 99, "pos": "4번 1B"},
                    {"name": "후지와라 쿄타", "num": 1, "pos": "1번 CF"}
                ]
            },
            {
                "team_name": "도호쿠 라쿠텐 골든이글스",
                "city": "센다이", "stadium": "라쿠텐 모바일 파크 미야기",
                "players": [
                    {"name": "아사무라 히데토", "num": 3, "pos": "4번 DH"},
                    {"name": "타츠미 료스케", "num": 8, "pos": "3번 CF"},
                    {"name": "노리모토 타카히로", "num": 14, "pos": "마무리 P"}
                ]
            },
            {
                "team_name": "오릭스 버펄로스",
                "city": "오사카", "stadium": "교세라 돔 오사카",
                "players": [
                    {"name": "미야기 히로야", "num": 13, "pos": "선발 P"},
                    {"name": "모리 토모야", "num": 4, "pos": "4번 C"},
                    {"name": "쿠레바야시 코타로", "num": 24, "pos": "6번 SS"}
                ]
            },
            {
                "team_name": "사이타마 세이부 라이온즈",
                "city": "사이타마", "stadium": "베루나 돔",
                "players": [
                    {"name": "타카하시 코나", "num": 13, "pos": "선발 P"},
                    {"name": "겐다 소스케", "num": 6, "pos": "2번 SS"},
                    {"name": "토노사키 슈타", "num": 5, "pos": "3번 2B"}
                ]
            }
        ]
    }
}