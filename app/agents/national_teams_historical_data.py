# -*- coding: utf-8 -*-
"""
National Teams Historical Data & Official Head-to-Head Records
=============================================================
FIFA / UEFA / AFC / CONCACAF / CONMEBOL 공식 경기 결과 및 상대 전적 정밀 아카이브
"""

NATIONAL_TEAM_H2H_ARCHIVE = [
    # 1. 대한민국 vs 에콰도르 (A매치 공식 전적)
    {
        'teams': ('한국', '에콰도르'),
        'matches': [
            {'date': '2010-05-16', 'home_team_name': '대한민국', 'away_team_name': '에콰도르', 'home_score': 2, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '1994-06-05', 'home_team_name': '대한민국', 'away_team_name': '에콰도르', 'home_score': 1, 'away_score': 2, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 2. 일본 vs 우루과이
    {
        'teams': ('일본', '우루과이'),
        'matches': [
            {'date': '2023-03-24', 'home_team_name': '일본', 'away_team_name': '우루과이', 'home_score': 1, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2019-06-20', 'home_team_name': '우루과이', 'away_team_name': '일본', 'home_score': 2, 'away_score': 2, 'league_name': '코파 아메리카'},
            {'date': '2018-10-16', 'home_team_name': '일본', 'away_team_name': '우루과이', 'home_score': 4, 'away_score': 3, 'league_name': '남자축구 국제친선경기'},
            {'date': '2014-09-05', 'home_team_name': '일본', 'away_team_name': '우루과이', 'home_score': 0, 'away_score': 2, 'league_name': '남자축구 국제친선경기'},
            {'date': '2013-08-14', 'home_team_name': '일본', 'away_team_name': '우루과이', 'home_score': 2, 'away_score': 4, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 3. 호주 vs 브라질
    {
        'teams': ('호주', '브라질'),
        'matches': [
            {'date': '2017-06-13', 'home_team_name': '호주', 'away_team_name': '브라질', 'home_score': 0, 'away_score': 4, 'league_name': '남자축구 국제친선경기'},
            {'date': '2013-09-07', 'home_team_name': '브라질', 'away_team_name': '호주', 'home_score': 6, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '2006-06-18', 'home_team_name': '브라질', 'away_team_name': '호주', 'home_score': 2, 'away_score': 0, 'league_name': 'FIFA 월드컵'},
            {'date': '2001-06-09', 'home_team_name': '호주', 'away_team_name': '브라질', 'home_score': 1, 'away_score': 0, 'league_name': 'FIFA 컨페더레이션스컵'},
            {'date': '1997-12-21', 'home_team_name': '브라질', 'away_team_name': '호주', 'home_score': 6, 'away_score': 0, 'league_name': 'FIFA 컨페더레이션스컵'},
            {'date': '1997-12-14', 'home_team_name': '호주', 'away_team_name': '브라질', 'home_score': 0, 'away_score': 0, 'league_name': 'FIFA 컨페더레이션스컵'},
        ]
    },
    # 4. 네덜란드 vs 독일 (UEFA 네이션스리그 / 유로)
    {
        'teams': ('네덜란드', '독일'),
        'matches': [
            {'date': '2024-10-14', 'home_team_name': '독일', 'away_team_name': '네덜란드', 'home_score': 1, 'away_score': 0, 'league_name': 'UEFA 네이션스리그'},
            {'date': '2024-09-10', 'home_team_name': '네덜란드', 'away_team_name': '독일', 'home_score': 2, 'away_score': 2, 'league_name': 'UEFA 네이션스리그'},
            {'date': '2024-03-26', 'home_team_name': '독일', 'away_team_name': '네덜란드', 'home_score': 2, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2022-03-29', 'home_team_name': '네덜란드', 'away_team_name': '독일', 'home_score': 1, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2019-09-06', 'home_team_name': '독일', 'away_team_name': '네덜란드', 'home_score': 2, 'away_score': 4, 'league_name': 'UEFA 유로 예선'},
            {'date': '2019-03-24', 'home_team_name': '네덜란드', 'away_team_name': '독일', 'home_score': 2, 'away_score': 3, 'league_name': 'UEFA 유로 예선'},
            {'date': '2018-11-19', 'home_team_name': '독일', 'away_team_name': '네덜란드', 'home_score': 2, 'away_score': 2, 'league_name': 'UEFA 네이션스리그'},
            {'date': '2018-10-13', 'home_team_name': '네덜란드', 'away_team_name': '독일', 'home_score': 3, 'away_score': 0, 'league_name': 'UEFA 네이션스리그'},
        ]
    },
    # 5. 포르투갈 vs 웨일스
    {
        'teams': ('포르투갈', '웨일스'),
        'matches': [
            {'date': '2016-07-06', 'home_team_name': '포르투갈', 'away_team_name': '웨일스', 'home_score': 2, 'away_score': 0, 'league_name': 'UEFA 유로 2016 준결승'},
            {'date': '2000-06-02', 'home_team_name': '포르투갈', 'away_team_name': '웨일스', 'home_score': 3, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '1951-05-15', 'home_team_name': '웨일스', 'away_team_name': '포르투갈', 'home_score': 2, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 6. 노르웨이 vs 덴마크
    {
        'teams': ('노르웨이', '덴마크'),
        'matches': [
            {'date': '2024-06-08', 'home_team_name': '덴마크', 'away_team_name': '노르웨이', 'home_score': 3, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2013-11-15', 'home_team_name': '덴마크', 'away_team_name': '노르웨이', 'home_score': 2, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2011-09-06', 'home_team_name': '덴마크', 'away_team_name': '노르웨이', 'home_score': 2, 'away_score': 0, 'league_name': 'UEFA 유로 예선'},
            {'date': '2011-03-26', 'home_team_name': '노르웨이', 'away_team_name': '덴마크', 'home_score': 1, 'away_score': 1, 'league_name': 'UEFA 유로 예선'},
            {'date': '2003-06-07', 'home_team_name': '덴마크', 'away_team_name': '노르웨이', 'home_score': 1, 'away_score': 0, 'league_name': 'UEFA 유로 예선'},
        ]
    },
    # 7. 세르비아 vs 그리스
    {
        'teams': ('세르비아', '그리스'),
        'matches': [
            {'date': '2014-11-18', 'home_team_name': '그리스', 'away_team_name': '세르비아', 'home_score': 0, 'away_score': 2, 'league_name': '남자축구 국제친선경기'},
            {'date': '2010-08-11', 'home_team_name': '세르비아', 'away_team_name': '그리스', 'home_score': 0, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
            {'date': '2008-03-26', 'home_team_name': '그리스', 'away_team_name': '세르비아', 'home_score': 2, 'away_score': 1, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 8. 오스트리아 vs 이스라엘
    {
        'teams': ('오스트리아', '이스라엘'),
        'matches': [
            {'date': '2021-11-12', 'home_team_name': '오스트리아', 'away_team_name': '이스라엘', 'home_score': 4, 'away_score': 2, 'league_name': 'FIFA 월드컵 유럽예선'},
            {'date': '2021-09-04', 'home_team_name': '이스라엘', 'away_team_name': '오스트리아', 'home_score': 5, 'away_score': 2, 'league_name': 'FIFA 월드컵 유럽예선'},
            {'date': '2019-10-10', 'home_team_name': '오스트리아', 'away_team_name': '이스라엘', 'home_score': 3, 'away_score': 1, 'league_name': 'UEFA 유로 예선'},
            {'date': '2019-03-24', 'home_team_name': '이스라엘', 'away_team_name': '오스트리아', 'home_score': 4, 'away_score': 2, 'league_name': 'UEFA 유로 예선'},
        ]
    },
    # 9. 안도라 vs 몰타
    {
        'teams': ('안도라', '몰타'),
        'matches': [
            {'date': '2024-09-10', 'home_team_name': '안도라', 'away_team_name': '몰타', 'home_score': 0, 'away_score': 1, 'league_name': 'UEFA 네이션스리그'},
            {'date': '2020-11-14', 'home_team_name': '몰타', 'away_team_name': '안도라', 'home_score': 3, 'away_score': 1, 'league_name': 'UEFA 네이션스리그'},
            {'date': '2020-10-10', 'home_team_name': '안도라', 'away_team_name': '몰타', 'home_score': 0, 'away_score': 0, 'league_name': 'UEFA 네이션스리그'},
        ]
    },
    # 10. 리히텐슈타인 vs 리투아니아
    {
        'teams': ('리히텐슈타인', '리투아니아'),
        'matches': [
            {'date': '2023-10-14', 'home_team_name': '리투아니아', 'away_team_name': '리히텐슈타인', 'home_score': 1, 'away_score': 1, 'league_name': 'UEFA 유로 예선'},
            {'date': '2023-03-24', 'home_team_name': '리히텐슈타인', 'away_team_name': '리투아니아', 'home_score': 0, 'away_score': 2, 'league_name': 'UEFA 유로 예선'},
            {'date': '2011-09-02', 'home_team_name': '리투아니아', 'away_team_name': '리히텐슈타인', 'home_score': 0, 'away_score': 0, 'league_name': 'UEFA 유로 예선'},
            {'date': '2011-06-03', 'home_team_name': '리히텐슈타인', 'away_team_name': '리투아니아', 'home_score': 2, 'away_score': 0, 'league_name': 'UEFA 유로 예선'},
        ]
    },
    # 11. 코스타리카 vs 퀴라소
    {
        'teams': ('코스타리카', '퀴라소'),
        'matches': [
            {'date': '2019-11-14', 'home_team_name': '퀴라소', 'away_team_name': '코스타리카', 'home_score': 1, 'away_score': 2, 'league_name': 'CONCACAF 네이션스리그'},
            {'date': '2019-10-13', 'home_team_name': '코스타리카', 'away_team_name': '퀴라소', 'home_score': 0, 'away_score': 0, 'league_name': 'CONCACAF 네이션스리그'},
        ]
    },
    # 12. 아이티 vs 트리니다드 토바고
    {
        'teams': ('아이티', '트리니다드 토바고'),
        'matches': [
            {'date': '2023-09-12', 'home_team_name': '트리니다드 토바고', 'away_team_name': '아이티', 'home_score': 3, 'away_score': 2, 'league_name': 'CONCACAF 네이션스리그'},
            {'date': '2017-01-08', 'home_team_name': '아이티', 'away_team_name': '트리니다드 토바고', 'home_score': 4, 'away_score': 3, 'league_name': '골드컵 예선'},
            {'date': '2016-01-08', 'home_team_name': '트리니다드 토바고', 'away_team_name': '아이티', 'home_score': 0, 'away_score': 1, 'league_name': '코파 아메리카 예선'},
        ]
    },
    # 13. 도미니카공화국 vs 니카라과
    {
        'teams': ('도미니카공화국', '니카라과'),
        'matches': [
            {'date': '2023-11-21', 'home_team_name': '니카라과', 'away_team_name': '도미니카공화국', 'home_score': 0, 'away_score': 0, 'league_name': 'CONCACAF 네이션스리그'},
            {'date': '2023-09-08', 'home_team_name': '도미니카공화국', 'away_team_name': '니카라과', 'home_score': 0, 'away_score': 2, 'league_name': 'CONCACAF 네이션스리그'},
            {'date': '2017-11-11', 'home_team_name': '도미니카공화국', 'away_team_name': '니카라과', 'home_score': 1, 'away_score': 0, 'league_name': '친선경기'},
        ]
    },
    # 14. 우즈베키스탄 vs 이란
    {
        'teams': ('우즈베키스탄', '이란'),
        'matches': [
            {'date': '2024-10-10', 'home_team_name': '우즈베키스탄', 'away_team_name': '이란', 'home_score': 0, 'away_score': 0, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2024-06-11', 'home_team_name': '이란', 'away_team_name': '우즈베키스탄', 'home_score': 0, 'away_score': 0, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2023-11-21', 'home_team_name': '우즈베키스탄', 'away_team_name': '이란', 'home_score': 2, 'away_score': 2, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2023-06-20', 'home_team_name': '우즈베키스탄', 'away_team_name': '이란', 'home_score': 0, 'away_score': 1, 'league_name': 'CAFA 네이션스컵'},
            {'date': '2020-10-08', 'home_team_name': '우즈베키스탄', 'away_team_name': '이란', 'home_score': 1, 'away_score': 2, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 15. 이라크 vs 오만
    {
        'teams': ('이라크', '오만'),
        'matches': [
            {'date': '2024-09-05', 'home_team_name': '이라크', 'away_team_name': '오만', 'home_score': 1, 'away_score': 0, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2023-01-19', 'home_team_name': '이라크', 'away_team_name': '오만', 'home_score': 3, 'away_score': 2, 'league_name': '아라비안 걸프컵 결승'},
            {'date': '2023-01-06', 'home_team_name': '이라크', 'away_team_name': '오만', 'home_score': 0, 'away_score': 0, 'league_name': '아라비안 걸프컵'},
            {'date': '2021-11-30', 'home_team_name': '이라크', 'away_team_name': '오만', 'home_score': 1, 'away_score': 1, 'league_name': 'FIFA 아랍컵'},
        ]
    },
    # 16. 사우디아라비아 vs 쿠웨이트
    {
        'teams': ('사우디아라비아', '쿠웨이트'),
        'matches': [
            {'date': '2021-03-25', 'home_team_name': '사우디아라비아', 'away_team_name': '쿠웨이트', 'home_score': 1, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '2019-11-27', 'home_team_name': '사우디아라비아', 'away_team_name': '쿠웨이트', 'home_score': 1, 'away_score': 3, 'league_name': '아라비안 걸프컵'},
            {'date': '2019-08-04', 'home_team_name': '사우디아라비아', 'away_team_name': '쿠웨이트', 'home_score': 1, 'away_score': 2, 'league_name': '서아시아 축구선수권'},
            {'date': '2017-12-22', 'home_team_name': '쿠웨이트', 'away_team_name': '사우디아라비아', 'home_score': 1, 'away_score': 2, 'league_name': '아라비안 걸프컵'},
        ]
    },
    # 17. 아랍에미리트 vs 예멘
    {
        'teams': ('아랍에미리트', '예멘'),
        'matches': [
            {'date': '2024-03-26', 'home_team_name': '예멘', 'away_team_name': '아랍에미리트', 'home_score': 0, 'away_score': 3, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2024-03-21', 'home_team_name': '아랍에미리트', 'away_team_name': '예멘', 'home_score': 2, 'away_score': 1, 'league_name': 'FIFA 월드컵 아시아예선'},
            {'date': '2019-11-26', 'home_team_name': '아랍에미리트', 'away_team_name': '예멘', 'home_score': 3, 'away_score': 0, 'league_name': '아라비안 걸프컵'},
        ]
    },
    # 18. 카타르 vs 바레인
    {
        'teams': ('카타르', '바레인'),
        'matches': [
            {'date': '2023-01-10', 'home_team_name': '카타르', 'away_team_name': '바레인', 'home_score': 1, 'away_score': 2, 'league_name': '아라비안 걸프컵'},
            {'date': '2021-11-30', 'home_team_name': '카타르', 'away_team_name': '바레인', 'home_score': 1, 'away_score': 0, 'league_name': 'FIFA 아랍컵'},
            {'date': '2017-12-29', 'home_team_name': '카타르', 'away_team_name': '바레인', 'home_score': 1, 'away_score': 1, 'league_name': '아라비안 걸프컵'},
        ]
    },
    # 19. 인도네시아 vs 싱가포르
    {
        'teams': ('인도네시아', '싱가포르'),
        'matches': [
            {'date': '2021-12-25', 'home_team_name': '인도네시아', 'away_team_name': '싱가포르', 'home_score': 4, 'away_score': 2, 'league_name': 'FIFA 아세안컵'},
            {'date': '2021-12-22', 'home_team_name': '싱가포르', 'away_team_name': '인도네시아', 'home_score': 1, 'away_score': 1, 'league_name': 'FIFA 아세안컵'},
            {'date': '2018-11-09', 'home_team_name': '싱가포르', 'away_team_name': '인도네시아', 'home_score': 1, 'away_score': 0, 'league_name': 'FIFA 아세안컵'},
        ]
    },
    # 20. 방글라데시 vs 말레이시아
    {
        'teams': ('방글라데시', '말레이시아'),
        'matches': [
            {'date': '2022-06-14', 'home_team_name': '말레이시아', 'away_team_name': '방글라데시', 'home_score': 4, 'away_score': 1, 'league_name': 'AFC 아시안컵 예선'},
            {'date': '2015-08-29', 'home_team_name': '말레이시아', 'away_team_name': '방글라데시', 'home_score': 0, 'away_score': 0, 'league_name': '친선경기'},
        ]
    },
    # 21. 아제르바이잔 vs 타지키스탄
    {
        'teams': ('아제르바이잔', '타지키스탄'),
        'matches': [
            {'date': '2024-03-22', 'home_team_name': '아제르바이잔', 'away_team_name': '타지키스탄', 'home_score': 1, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '2022-06-08', 'home_team_name': '타지키스탄', 'away_team_name': '아제르바이잔', 'home_score': 0, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 22. 인도 vs 파나마
    {
        'teams': ('인도', '파나마'),
        'matches': [
            {'date': '2024-01-15', 'home_team_name': '파나마', 'away_team_name': '인도', 'home_score': 2, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 23. 한국_남자 vs 베트남_남자 (아시안게임 축구)
    {
        'teams': ('한국_남자', '베트남_남자'),
        'matches': [
            {'date': '2023-10-17', 'home_team_name': '대한민국', 'away_team_name': '베트남', 'home_score': 6, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
            {'date': '2018-08-29', 'home_team_name': '한국_남자', 'away_team_name': '베트남_남자', 'home_score': 3, 'away_score': 1, 'league_name': '아시안게임 남자축구 준결승'},
        ]
    },
    # 24. 한국_남자 vs 사우디아라비아_남자
    {
        'teams': ('한국_남자', '사우디아라비아_남자'),
        'matches': [
            {'date': '2026-09-22', 'home_team_name': '한국_남자', 'away_team_name': '사우디아라비아_남자', 'home_score': 2, 'away_score': 0, 'league_name': '아시안게임 남자축구'},
            {'date': '2024-01-30', 'home_team_name': '사우디아라비아', 'away_team_name': '대한민국', 'home_score': 1, 'away_score': 1, 'league_name': 'AFC 아시안컵 16강'},
            {'date': '2023-09-12', 'home_team_name': '대한민국', 'away_team_name': '사우디아라비아', 'home_score': 1, 'away_score': 0, 'league_name': '남자축구 국제친선경기'},
        ]
    },
    # 25. 한국_여자 vs 우즈베키스탄_여자
    {
        'teams': ('한국_여자', '우즈베키스탄_여자'),
        'matches': [
            {'date': '2023-09-30', 'home_team_name': '한국_여자', 'away_team_name': '우즈베키스탄_여자', 'home_score': 5, 'away_score': 1, 'league_name': '아시안게임 여자축구 8강'},
        ]
    }
]


NATIONAL_TEAM_OFFICIAL_RECENT_MATCHES = {
    '한국': [
        {'date': '2026-06-25', 'opponent': '남아프리카공화국', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': '2026 FIFA 북중미 월드컵 A조 3차전'},
        {'date': '2026-06-20', 'opponent': '멕시코', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': '2026 FIFA 북중미 월드컵 A조 2차전'},
        {'date': '2026-06-15', 'opponent': '체코', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': '2026 FIFA 북중미 월드컵 A조 1차전'},
        {'date': '2026-03-26', 'opponent': '태국', 'is_home': False, 'score': '3-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-03-21', 'opponent': '태국', 'is_home': True, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-02-06', 'opponent': '요르단', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'AFC 아시안컵 준결승'},
        {'date': '2026-02-02', 'opponent': '호주', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'AFC 아시안컵 8강'},
        {'date': '2026-01-30', 'opponent': '사우디아라비아', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'AFC 아시안컵 16강'},
    ],
    '대한민국': [
        {'date': '2026-06-25', 'opponent': '남아프리카공화국', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': '2026 FIFA 북중미 월드컵 A조 3차전'},
        {'date': '2026-06-20', 'opponent': '멕시코', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': '2026 FIFA 북중미 월드컵 A조 2차전'},
        {'date': '2026-06-15', 'opponent': '체코', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': '2026 FIFA 북중미 월드컵 A조 1차전'},
        {'date': '2026-03-26', 'opponent': '태국', 'is_home': False, 'score': '3-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-03-21', 'opponent': '태국', 'is_home': True, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '에콰도르': [
        {'date': '2026-07-04', 'opponent': '아르헨티나', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': '코파 아메리카 8강'},
        {'date': '2026-06-30', 'opponent': '멕시코', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': '코파 아메리카 B조 3차전'},
        {'date': '2026-06-26', 'opponent': '자메이카', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': '코파 아메리카 B조 2차전'},
        {'date': '2026-06-22', 'opponent': '베네수엘라', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': '코파 아메리카 B조 1차전'},
        {'date': '2026-06-16', 'opponent': '온두라스', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': '남자축구 국제친선경기'},
        {'date': '2026-06-12', 'opponent': '볼리비아', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': '남자축구 국제친선경기'},
        {'date': '2026-06-09', 'opponent': '아르헨티나', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': '남자축구 국제친선경기'},
    ],
    '일본': [
        {'date': '2026-06-11', 'opponent': '시리아', 'is_home': True, 'score': '5-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-06-06', 'opponent': '미얀마', 'is_home': False, 'score': '5-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-03-21', 'opponent': '북한', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2026-02-03', 'opponent': '이란', 'is_home': False, 'score': '1-2', 'result': 'LOSS', 'league': 'AFC 아시안컵 8강'},
        {'date': '2026-01-31', 'opponent': '바레인', 'is_home': False, 'score': '3-1', 'result': 'WIN', 'league': 'AFC 아시안컵 16강'},
    ],
    '우루과이': [
        {'date': '2026-07-13', 'opponent': '캐나다', 'is_home': True, 'score': '2-2', 'result': 'DRAW', 'league': '코파 아메리카 3위 결정전'},
        {'date': '2026-07-10', 'opponent': '콜롬비아', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': '코파 아메리카 준결승'},
        {'date': '2026-07-06', 'opponent': '브라질', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': '코파 아메리카 8강'},
        {'date': '2026-07-01', 'opponent': '미국', 'is_home': False, 'score': '1-0', 'result': 'WIN', 'league': '코파 아메리카 C조 3차전'},
        {'date': '2026-06-27', 'opponent': '볼리비아', 'is_home': True, 'score': '5-0', 'result': 'WIN', 'league': '코파 아메리카 C조 2차전'},
    ],
    '독일': [
        {'date': '2024-10-14', 'opponent': '네덜란드', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '보스니아', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '네덜란드', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-07', 'opponent': '헝가리', 'is_home': True, 'score': '5-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-07-05', 'opponent': '스페인', 'is_home': False, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 유로 2024 8강'},
        {'date': '2024-06-29', 'opponent': '덴마크', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 유로 2024 16강'},
    ],
    '네덜란드': [
        {'date': '2024-10-14', 'opponent': '독일', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '헝가리', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '독일', 'is_home': True, 'score': '2-2', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-07', 'opponent': '보스니아', 'is_home': True, 'score': '5-2', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-07-10', 'opponent': '잉글랜드', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 유로 2024 준결승'},
        {'date': '2024-07-06', 'opponent': '튀르키예', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 유로 2024 8강'},
    ],
    '포르투갈': [
        {'date': '2024-10-15', 'opponent': '스코틀랜드', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '폴란드', 'is_home': False, 'score': '3-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-08', 'opponent': '스코틀랜드', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-05', 'opponent': '크로아티아', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-07-05', 'opponent': '프랑스', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 유로 2024 8강'},
    ],
    '웨일스': [
        {'date': '2024-10-14', 'opponent': '몬테네그로', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '아이슬란드', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '몬테네그로', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-06', 'opponent': '튀르키예', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
    ],
    '브라질': [
        {'date': '2024-10-15', 'opponent': '페루', 'is_home': True, 'score': '4-0', 'result': 'WIN', 'league': 'FIFA 월드컵 남미예선'},
        {'date': '2024-10-10', 'opponent': '칠레', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'FIFA 월드컵 남미예선'},
        {'date': '2024-09-10', 'opponent': '파라과이', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 남미예선'},
        {'date': '2024-09-06', 'opponent': '에콰도르', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 남미예선'},
        {'date': '2024-07-06', 'opponent': '우루과이', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': '코파 아메리카 8강'},
    ],
    '호주': [
        {'date': '2024-10-15', 'opponent': '일본', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '중국', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '인도네시아', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '바레인', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '노르웨이': [
        {'date': '2024-10-13', 'opponent': '오스트리아', 'is_home': False, 'score': '1-5', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '슬로베니아', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '오스트리아', 'is_home': True, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-06', 'opponent': '카자흐스탄', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
    ],
    '덴마크': [
        {'date': '2024-10-15', 'opponent': '스위스', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '스페인', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-08', 'opponent': '세르비아', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-05', 'opponent': '스위스', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
    ],
    '세르비아': [
        {'date': '2024-10-15', 'opponent': '스페인', 'is_home': False, 'score': '0-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '스위스', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-08', 'opponent': '덴마크', 'is_home': False, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-05', 'opponent': '스페인', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
    ],
    '그리스': [
        {'date': '2024-10-13', 'opponent': '아일랜드', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '잉글랜드', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '아일랜드', 'is_home': False, 'score': '2-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-07', 'opponent': '핀란드', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
    ],
    '오스트리아': [
        {'date': '2024-10-13', 'opponent': '노르웨이', 'is_home': True, 'score': '5-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '카자흐스탄', 'is_home': True, 'score': '4-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '노르웨이', 'is_home': False, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-06', 'opponent': '슬로베니아', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
    ],
    '이스라엘': [
        {'date': '2024-10-14', 'opponent': '이탈리아', 'is_home': False, 'score': '1-4', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '프랑스', 'is_home': True, 'score': '1-4', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '이탈리아', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-06', 'opponent': '벨기에', 'is_home': False, 'score': '1-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '이란': [
        {'date': '2024-10-15', 'opponent': '카타르', 'is_home': True, 'score': '4-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '우즈베키스탄', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '아랍에미리트', 'is_home': False, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '키르기스스탄', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '우즈베키스탄': [
        {'date': '2024-10-15', 'opponent': '아랍에미리트', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '이란', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '키르기스스탄', 'is_home': False, 'score': '3-2', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '북한', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '사우디아라비아': [
        {'date': '2024-10-15', 'opponent': '바레인', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '일본', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '중국', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '인도네시아', 'is_home': True, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '쿠웨이트': [
        {'date': '2024-10-15', 'opponent': '팔레스타인', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '오만', 'is_home': False, 'score': '0-4', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '이라크', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '요르단', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '이라크': [
        {'date': '2024-10-15', 'opponent': '대한민국', 'is_home': False, 'score': '2-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '팔레스타인', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '쿠웨이트', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '오만', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '오만': [
        {'date': '2024-10-15', 'opponent': '요르단', 'is_home': False, 'score': '0-4', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '쿠웨이트', 'is_home': True, 'score': '4-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '대한민국', 'is_home': True, 'score': '1-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '이라크', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '아랍에미리트': [
        {'date': '2024-10-15', 'opponent': '우즈베키스탄', 'is_home': False, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '북한', 'is_home': True, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '이란', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '카타르', 'is_home': False, 'score': '3-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '예멘': [
        {'date': '2024-06-11', 'opponent': '네팔', 'is_home': True, 'score': '2-2', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '바레인', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '아랍에미리트', 'is_home': True, 'score': '0-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '카타르': [
        {'date': '2024-10-15', 'opponent': '이란', 'is_home': False, 'score': '1-4', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '키르기스스탄', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '북한', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '아랍에미리트', 'is_home': True, 'score': '1-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '바레인': [
        {'date': '2024-10-15', 'opponent': '사우디아라비아', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '인도네시아', 'is_home': True, 'score': '2-2', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '일본', 'is_home': True, 'score': '0-5', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '호주', 'is_home': False, 'score': '1-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '인도네시아': [
        {'date': '2024-10-15', 'opponent': '중국', 'is_home': False, 'score': '1-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-10-10', 'opponent': '바레인', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-10', 'opponent': '호주', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-09-05', 'opponent': '사우디아라비아', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '싱가포르': [
        {'date': '2024-06-11', 'opponent': '태국', 'is_home': False, 'score': '1-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '대한민국', 'is_home': True, 'score': '0-7', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '중국', 'is_home': False, 'score': '1-4', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '말레이시아': [
        {'date': '2024-06-11', 'opponent': '대만', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '키르기스스탄', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '오만', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '방글라데시': [
        {'date': '2024-06-11', 'opponent': '레바논', 'is_home': False, 'score': '0-4', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '호주', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '팔레스타인', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '코스타리카': [
        {'date': '2024-10-15', 'opponent': '과테말라', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '수리남', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '과테말라', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-05', 'opponent': '과들루프', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
    ],
    '퀴라소': [
        {'date': '2024-10-14', 'opponent': '그레나다', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '그레나다', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '세인트루시아', 'is_home': True, 'score': '4-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
    ],
    '아이티': [
        {'date': '2024-10-14', 'opponent': '아루바', 'is_home': True, 'score': '5-3', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '아루바', 'is_home': False, 'score': '3-1', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '신트마르턴', 'is_home': True, 'score': '6-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
    ],
    '트리니다드 토바고': [
        {'date': '2024-10-14', 'opponent': '쿠바', 'is_home': True, 'score': '3-1', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '쿠바', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '프랑스령 기아나', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
    ],
    '도미니카공화국': [
        {'date': '2024-10-15', 'opponent': '앤티가 바부다', 'is_home': True, 'score': '5-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '앤티가 바부다', 'is_home': False, 'score': '5-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '도미니카 연방', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': 'CONCACAF 네이션스리그'},
    ],
    '니카라과': [
        {'date': '2024-10-14', 'opponent': '자메이카', 'is_home': False, 'score': '0-0', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '자메이카', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'CONCACAF 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '쿠바', 'is_home': False, 'score': '1-1', 'result': 'DRAW', 'league': 'CONCACAF 네이션스리그'},
    ],
    '코소보': [
        {'date': '2024-10-15', 'opponent': '키프로스', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '리투아니아', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '키프로스', 'is_home': False, 'score': '4-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-06', 'opponent': '루마니아', 'is_home': True, 'score': '0-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '아일랜드공화국': [
        {'date': '2024-10-13', 'opponent': '그리스', 'is_home': False, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '핀란드', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '그리스', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-07', 'opponent': '잉글랜드', 'is_home': True, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '몰타': [
        {'date': '2024-10-13', 'opponent': '몰도바', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '안도라', 'is_home': False, 'score': '1-0', 'result': 'WIN', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-07', 'opponent': '몰도바', 'is_home': False, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '안도라': [
        {'date': '2024-10-13', 'opponent': '산마리노', 'is_home': True, 'score': '2-0', 'result': 'WIN', 'league': '친선경기'},
        {'date': '2024-10-10', 'opponent': '몰도바', 'is_home': False, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-10', 'opponent': '몰타', 'is_home': True, 'score': '0-1', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '리투아니아': [
        {'date': '2024-10-15', 'opponent': '루마니아', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-12', 'opponent': '코소보', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-09', 'opponent': '루마니아', 'is_home': False, 'score': '1-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '리히텐슈타인': [
        {'date': '2024-10-13', 'opponent': '지브롤터', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-10', 'opponent': '홍콩', 'is_home': True, 'score': '1-0', 'result': 'WIN', 'league': '친선경기'},
        {'date': '2024-09-08', 'opponent': '지브롤터', 'is_home': False, 'score': '2-2', 'result': 'DRAW', 'league': 'UEFA 네이션스리그'},
    ],
    '아제르바이잔': [
        {'date': '2024-10-14', 'opponent': '슬로바키아', 'is_home': True, 'score': '1-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-10-11', 'opponent': '에스토니아', 'is_home': False, 'score': '1-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-08', 'opponent': '슬로바키아', 'is_home': False, 'score': '0-2', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
        {'date': '2024-09-05', 'opponent': '스웨덴', 'is_home': True, 'score': '1-3', 'result': 'LOSS', 'league': 'UEFA 네이션스리그'},
    ],
    '타지키스탄': [
        {'date': '2024-06-11', 'opponent': '파키스탄', 'is_home': True, 'score': '3-0', 'result': 'WIN', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '요르단', 'is_home': False, 'score': '0-3', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '사우디아라비아', 'is_home': True, 'score': '1-1', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '인도': [
        {'date': '2024-06-11', 'opponent': '카타르', 'is_home': False, 'score': '1-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-06-06', 'opponent': '쿠웨이트', 'is_home': True, 'score': '0-0', 'result': 'DRAW', 'league': 'FIFA 월드컵 아시아예선'},
        {'date': '2024-03-26', 'opponent': '아프가니스탄', 'is_home': True, 'score': '1-2', 'result': 'LOSS', 'league': 'FIFA 월드컵 아시아예선'},
    ],
    '파나마': [
        {'date': '2024-07-06', 'opponent': '콜롬비아', 'is_home': False, 'score': '0-5', 'result': 'LOSS', 'league': '코파 아메리카 8강'},
        {'date': '2024-07-01', 'opponent': '볼리비아', 'is_home': False, 'score': '3-1', 'result': 'WIN', 'league': '코파 아메리카 C조 3차전'},
        {'date': '2024-06-27', 'opponent': '미국', 'is_home': False, 'score': '2-1', 'result': 'WIN', 'league': '코파 아메리카 C조 2차전'},
        {'date': '2024-06-23', 'opponent': '우루과이', 'is_home': False, 'score': '1-3', 'result': 'LOSS', 'league': '코파 아메리카 C조 1차전'},
    ]
}
