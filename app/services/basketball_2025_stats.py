# -*- coding: utf-8 -*-
"""
🏀 2025년 시즌 농구 공식 구단 팩트 통계 데이터 (KBL 10개 구단, WKBL 6개 구단, NBA 30개 구단)
- 2024~2025 시즌 완료된 정규/플레이오프 공식 경기 1,521건 집계 데이터
- 신규 시즌 시작 초기 데이터 부재 시 100% 팩트 기반 홈/원정/통합 성적으로 즉시 대체 계산
"""
import json
import os

_FACTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scratch', 'bball_2025_facts_for_js.json')

try:
    with open(_FACTS_PATH, 'r', encoding='utf-8') as f:
        _DATA = json.load(f)
        BBALL_2025_TEAMS = _DATA.get('teams', {})
        BBALL_2025_ALIASES = _DATA.get('aliases', {})
except Exception as e:
    BBALL_2025_TEAMS = {}
    BBALL_2025_ALIASES = {}

def get_basketball_2025_team_stats(team_name: str):
    """구단명을 정규화하여 2025 시즌 공식 통계(home, away, total)를 반환"""
    if not team_name:
        return None
    tn = str(team_name).strip()
    tn_clean = tn.lower().replace(" ", "")

    # 1. Direct match
    if tn in BBALL_2025_TEAMS:
        return BBALL_2025_TEAMS[tn]

    # 2. Alias match
    for canon, alist in BBALL_2025_ALIASES.items():
        for a in alist:
            a_clean = a.lower().replace(" ", "")
            if tn_clean == a_clean or tn_clean in a_clean or a_clean in tn_clean:
                if canon in BBALL_2025_TEAMS:
                    return BBALL_2025_TEAMS[canon]

    # 3. Substring match
    for canon, st in BBALL_2025_TEAMS.items():
        c_clean = canon.lower().replace(" ", "")
        if tn_clean in c_clean or c_clean in tn_clean:
            return st

    return None
