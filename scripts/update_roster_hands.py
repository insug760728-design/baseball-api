import json

LEFT_BATTERS = {
    # KBO
    '최형우', '소크라테스', '나성범', '최원준', '김지찬', '구자욱', '디아즈', '김영웅', '류지혁',
    '홍창기', '신민재', '문보경', '오지환', '박해민', '이영빈', '정수빈', '제러드', '김재환', '조수행',
    '강백호', '김민혁', '황영묵', '이도윤', '최지훈', '정준재', '한유섬', '박성한', '황성빈',
    '나승엽', '고승민', '박승욱', '박민우', '최정원', '이주형', '김혜성', '송성문', '최주환', '변상권', '이용규',
    # NPB
    '마루 요시히로', '요시카와 나오키', '오시로 타쿠미', '카도와키 마코토', '치카모토 코지', '나카노 타쿠무', '사토 테루아키',
    '마에가와 우쿄', '키나미 세이야', '니시카와 하루키', '무라카미 무네타카', '나가오카 히데키', '타케오카 류세이',
    '카지와라 코키', '사노 케이타', '모리 케이토', '오카바야시 유키', '타카하시 슈헤이', '무라마츠 카이토',
    '아키야마 쇼고', '노마 타카요시', '코조노 카이토', '사카쿠라 쇼고', '야노 마사야',
    '슈토 우쿄', '쿠리하라 료야', '콘도 켄스케', '나카무라 아키라', '마키하라 타이세이', '야나기타 유키',
    '카미가와바타 다이고', '키요미야 코타로', '미즈노 타츠키', '이소바타 료타',
    '후지와라 쿄타', '오가와 류세이', '폴랑코', '사토 토시야', '카쿠나카 카츠야', '후지오카 유다이',
    '코부카 히로토', '타츠미 료스케', '시마우치 히로아키', '스즈키 다이치', '오고 유야',
    '후쿠다 슈헤이', '무네 유마', '니시카와 료마', '모리 토모야', '차노 토쿠마사',
    '겐다 소스케', '니시카와 마나야', '야마무라 료헤이', '스즈키 쇼헤이',
    # MLB
    '오타니 쇼헤이', '프레디 프리먼', '맥스 먼시', '후안 소토', '코리 시거', '브라이스 하퍼',
    '카일 슈와버', '거너 헨더슨', '요르단 알바레즈', '카일 터커', '배지환', '이정후',
    '라파엘 데버스', '재런 듀란', '트리스턴 카사스', '루이스 아라에즈', '마이클 부시', '마이클 콘포토',
    '가빈 럭스', '잭 스윈스키', '조쉬 네일러', '놀란 존스', '찰리 블랙몬', '라스 눗바',
    '알렉 버를슨', '놀란 고먼', '브랜든 니모', '제프 맥닐', '코빈 캐롤', '조크 피더슨',
    '살 프렐릭', '크리스티안 옐리치', 'CJ 에이브람스', '브랜든 로우', '조쉬 로우', '나다니엘 로우',
    '세드릭 멀린스', '콜튼 카우저', '잭 겔로프', 'JJ 블리데이', 'JJ 블레데이', '루크 레일리',
    '제이크 맥카시', '도미닉 스미스', '앤서니 리조', '알렉스 버두고', '마커스 세미엔',
    '잭 넬슨', 'JP 크로포드', '도미닉 플레처', '마이클 매시', '라이언 오헌'
}

SWITCH_BATTERS = {
    '로하스', '페라자', '레이예스', '김주원', '카네코 유지', '프란시스코 린도어', '케텔 마르테',
    '애들리 러치맨', '오지 알비스', '호세 라미레즈', '이안 햅', '토미 에드먼', '앤서니 산탄데르',
    '딜런 칼슨', '엘리 데 라 크루즈', '조쉬 벨', '카를로스 산타나', '요안 몬카다', '브라이언 레이놀즈'
}

with open('app/services/baseball_rosters_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated_batters = 0
updated_pitchers = 0
for team_name, t_data in data.items():
    starter = t_data.get('starter', {})
    if starter.get('throws') in ('우투', '우완'):
        starter['throws'] = '우완'
        updated_pitchers += 1
    elif starter.get('throws') in ('좌투', '좌완'):
        starter['throws'] = '좌완'
        updated_pitchers += 1

    for b in t_data.get('batters', []):
        name = b.get('name', '')
        if name in SWITCH_BATTERS:
            b['hand'] = 'S'
            b['bats'] = '양타'
        elif name in LEFT_BATTERS:
            b['hand'] = 'L'
            b['bats'] = '좌타'
        else:
            b['hand'] = 'R'
            b['bats'] = '우타'
        updated_batters += 1

with open('app/services/baseball_rosters_master.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Updated {updated_batters} batters and {updated_pitchers} pitchers in baseball_rosters_master.json')

with open('app/static/data/rosters_master.js', 'w', encoding='utf-8') as f:
    f.write('// ⚾ 공식 구단 주전 로스터 및 투수 로테이션 마스터 (정적 캐시 모듈)\n\n')
    f.write('    const OFFICIAL_ROSTERS_MASTER = ')
    f.write(json.dumps(data, ensure_ascii=False, indent=2))
    f.write(';\n\n    if (typeof window !== "undefined") {\n      window.OFFICIAL_ROSTERS_MASTER = OFFICIAL_ROSTERS_MASTER;\n    }\n')

print('Successfully synchronized app/static/data/rosters_master.js')
