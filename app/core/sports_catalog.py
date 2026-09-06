# -*- coding: utf-8 -*-
"""
스포츠 및 리그 카탈로그
- 야구 (BASEBALL): MLB, KBO, NPB
- 축구 (SOCCER): EPL, LALIGA, BUNDESLIGA, SERIE_A, LIGUE_1
"""

SPORTS_CATALOG = {
    # [야구 3대 리그]
    "MLB": {
        "title": "미국 메이저리그 (MLB)",
        "sport_code": "BASEBALL",
        "leagues": [
            {"id": "MLB", "name": "미국 메이저리그 (MLB)"}
        ]
    },
    "KBO": {
        "title": "한국 프로야구 (KBO 리그)",
        "sport_code": "BASEBALL",
        "leagues": [
            {"id": "KBO", "name": "한국 프로야구 (KBO 리그)"}
        ]
    },
    "NPB": {
        "title": "일본 프로야구 (NPB)",
        "sport_code": "BASEBALL",
        "leagues": [
            {"id": "NPB", "name": "일본 프로야구 (NPB)"}
        ]
    },

    # [유럽 축구 5대 리그]
    "EPL": {
        "title": "잉글랜드 프리미어리그 (EPL)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "EPL", "name": "잉글랜드 프리미어리그 (EPL)", "api_code": "eng.1"}
        ]
    },
    "LALIGA": {
        "title": "스페인 라리가 (La Liga)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "LALIGA", "name": "스페인 라리가 (La Liga)", "api_code": "esp.1"}
        ]
    },
    "BUNDESLIGA": {
        "title": "독일 분데스리가 (Bundesliga)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "BUNDESLIGA", "name": "독일 분데스리가 (Bundesliga)", "api_code": "ger.1"}
        ]
    },
    "SERIE_A": {
        "title": "이탈리아 세리에 A (Serie A)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "SERIE_A", "name": "이탈리아 세리에 A (Serie A)", "api_code": "ita.1"}
        ]
    },
    "LIGUE_1": {
        "title": "프랑스 리그 1 (Ligue 1)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "LIGUE_1", "name": "프랑스 리그 1 (Ligue 1)", "api_code": "fra.1"}
        ]
    },
    "EREDIVISIE": {
        "title": "네덜란드 에레디비시 (Eredivisie)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "EREDIVISIE", "name": "네덜란드 에레디비시 (Eredivisie)", "api_code": "ned.1"}
        ]
    },

    # [농구 리그]
    "NBA": {
        "title": "미국 프로농구 (NBA)",
        "sport_code": "BASKETBALL",
        "leagues": [
            {"id": "NBA", "name": "미국 프로농구 (NBA)", "api_code": "nba"}
        ]
    },

    # [아시아 축구 리그]
    "KLEAGUE": {
        "title": "한국 K리그 (K-League 1 & 2)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "KLEAGUE", "name": "한국 K리그 (K-League)"},
            {"id": "KLEAGUE2", "name": "한국 K리그 2 (K League 2)"}
        ]
    },
    "JLEAGUE": {
        "title": "일본 J리그 (J.League)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "JLEAGUE", "name": "일본 J리그 (J.League)", "api_code": "jpn.1"}
        ]
    }
}