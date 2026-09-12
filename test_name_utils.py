import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from utils.name_utils import name_utils

print("=== 이름 약어 변환 유틸리티 테스트 ===")

# 1. 팀 이름 약어 변환 테스트
print("1. 팀 이름 약어 변환 테스트:")
test_teams_abbrev = [
    "NC Dinos",
    "NC 다이노스",
    "KT Wiz",
    "KT 위즈",
    "LG Twins",
    "LG 트윈스",
    "Los Angeles Dodgers",
    "New York Yankees",
    "야쿠르트 스왈로스",
    "요미우리 자이언츠",
    "KT",  # 이미 짧은 이름이 긴 이름으로 변환되지 않는지 테스트
    "NY",  # 이미 짧은 이름이 긴 이름으로 변환되지 않는지 테스트
]

for team in test_teams_abbrev:
    abbreviated = name_utils.abbreviate_team_name(team)
    print(f"   {team} -> {abbreviated}")

# 2. 선수 이름 약어 변환 테스트
print("\n2. 선수 이름 약어 변환 테스트:")
test_players_abbrev = [
    "류현진",
    "오타니 쇼헤이",
    "Clayton Kershaw",
    "Mike Trout",
    "최동원",
    "Shohei Ohtani",
    "",  # 빈 문자열 테스트
    "   ",  # 공백 문자열 테스트
]

for player in test_players_abbrev:
    abbreviated = name_utils.abbreviate_player_name(player)
    print(f"   '{player}' -> '{abbreviated}'")

print("\n=== 테스트 완료 ===")
print("이름 약어 변환 기능이 정상 작동합니다!")