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
    "CHAMPIONSHIP": {
        "title": "잉글랜드 챔피언십 (Championship)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "CHAMPIONSHIP", "name": "잉글랜드 챔피언십 (Championship)", "api_code": "eng.2"}
        ]
    },
    "LIBERTADORES": {
        "title": "코파 리베르타도레스 (Copa Libertadores)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "LIBERTADORES", "name": "코파 리베르타도레스 (Copa Libertadores)", "api_code": "conmebol.libertadores"}
        ]
    },
    "UCL": {
        "title": "UEFA 챔피언스리그 (Champions League)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "UCL", "name": "UEFA 챔피언스리그 (UCL)", "api_code": "uefa.champions"},
            {"id": "UEL", "name": "UEFA 유로파리그 (UEL)", "api_code": "uefa.europa"}
        ]
    },
    "ENGLAND_CUP": {
        "title": "잉글랜드 컵 (FA컵 & 카라바오컵)",
        "sport_code": "SOCCER",
        "leagues": [
            {"id": "FA_CUP", "name": "잉글랜드 FA컵", "api_code": "eng.fa"},
            {"id": "CARABAO_CUP", "name": "잉글랜드 카라바오컵", "api_code": "eng.league_cup"}
        ]
    },
    "KBL": {
        "title": "한국 남자프로농구 (KBL)",
        "sport_code": "BASKETBALL",
        "leagues": [
            {"id": "KBL", "name": "한국 프로농구 (KBL)", "api_code": "kbl"}
        ]
    },
    "NBA": {
        "title": "미국 프로농구 (NBA)",
        "sport_code": "BASKETBALL",
        "leagues": [
            {"id": "NBA", "name": "미국 프로농구 (NBA)", "api_code": "nba"}
        ]
    },
    "FIBA_WOMEN": {
        "title": "FIBA 여자농구 월드컵 (Women's World Cup)",
        "sport_code": "BASKETBALL",
        "leagues": [
            {"id": "FIBA_WOMEN", "name": "FIBA 여자농구 월드컵 (Women's World Cup)", "api_code": "fiba.women"}
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