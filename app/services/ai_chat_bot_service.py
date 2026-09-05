# -*- coding: utf-8 -*-
import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("ai_chat_bot")

AI_PERSONAS = [
    {
        "author": "도산대로세이버",
        "channel": "BASEBALL",
        "sport_tag": "MLB",
        "templates": [
            "오늘 다저스 불펜 승계주자 실점률(LOB%) 84% 기록중이네요. 뒷문 단단해서 후반부 마핸 승부 유력합니다.",
            "선발 FIP 2.95에 탈삼진/볼넷 비율(K/BB) 4.2 찍히는 날은 확실히 타자들이 공략하기 힘드네요.",
            "오타니 1번 타순 출루율(OBP) .415 돌파했네요. 1회 첫 타석 출루하면 득점 확률 70% 이상입니다."
        ]
    },
    {
        "author": "런던붉은여우",
        "channel": "SOCCER",
        "sport_tag": "EPL",
        "templates": [
            "토트넘 손흥민 감아차기 궤적 보셨나요? xG값 0.04짜리 원더골이 터져버리네요 ㄷㄷ",
            "맨시티 전반 xG 2.1 찍히는데 압박 강도(PPDA 7.2)가 진짜 살벌하네요. 후반전 멀티골 페이스입니다.",
            "브렌트포드 홈에서 세트피스 득점 전환율이 리그 2위라 무승부 이상은 충분히 가져갈 흐름입니다."
        ]
    },
    {
        "author": "베트맨1등사냥꾼",
        "channel": "PREDICTION",
        "sport_tag": "토토분석",
        "templates": [
            "이번 14경기 토토 계산기 돌려보니까 1등 예상 3.5명 수준이네요. 역배 1~2개 섞은 조합이 대박입니다!",
            "1등 누적 상금 6억 넘게 쌓인 잭팟 회차라 복수마킹 3~4개 걸고 가볼 만합니다.",
            "AI 추천픽 신뢰도 80% 이상 경기들은 단통으로 묶고, 박빙 경기들만 2마킹 분산하는 게 정석이네요."
        ]
    },
    {
        "author": "잠실빅보이",
        "channel": "BASEBALL",
        "sport_tag": "KBO",
        "templates": [
            "오늘 잠실 맞바람이라 타구 속도 150km 이상 찍혀도 펜스 앞에서 잡히는 타구가 많네요. 언더 흐름!",
            "불펜 방어율 리그 1위 팀은 7회 이후 역전 허용률이 8% 미만입니다. 후반부 리드팀 승률 확실하네요.",
            "KBO 득점권 타율 3할 넘는 중심 타선 돌아오니까 잔루(LOB) 안 남기고 바로 득점 뽑아냅니다."
        ]
    },
    {
        "author": "산시로인테르",
        "channel": "SOCCER",
        "sport_tag": "세리에A",
        "templates": [
            "인테르 vs 나폴리 전반 1:1 명승부네요. 라우타로 오프더볼 침투랑 크바라츠헬리아 드리블 대결 볼만합니다!",
            "AS로마 홈에서 유효슈팅 허용률 3개 미만 유지중이라 아탈란타 공격진도 뚫기 쉽지 않네요.",
            "세리에A 빅매치는 후반 75분 이후 교체 자원 체력 싸움에서 승패 갈릴 확률 65% 이상입니다."
        ]
    },
    {
        "author": "골든스테이트3점",
        "channel": "BASKETBALL",
        "sport_tag": "NBA",
        "templates": [
            "eFG% 58% 이상 유지되면 쿼터당 기대득점 32점 페이스입니다. 224.5 오버 유력해 보입니다.",
            "페이스(Pace) 103 찍히는 날은 트랜지션 3점이 연속으로 터져서 10점차 리드도 3분이면 뒤집히네요.",
            "보스턴 셀틱스 오펜시브 레이팅(ORtg) 122 찍히는 날은 마핸 승률 82% 공식입니다."
        ]
    },
    {
        "author": "상암축구도사",
        "channel": "SOCCER",
        "sport_tag": "축구분석",
        "templates": [
            "후반 70분 넘어가면 양팀 수비 간격 벌어지니까 역습 한 방에 결승골 터질 확률 75%입니다.",
            "세이버 기대마진 홈팀 +0.7점 우세 지표 떴는데 실제 경기 내용도 홈팀이 라인 올리고 주도하네요.",
            "점유율 60% 이상에 박스 안 터치 횟수 20회 넘어가면 결국 골문 열리게 되어 있습니다."
        ]
    },
    {
        "author": "다저스타디움원정대",
        "channel": "BASEBALL",
        "sport_tag": "MLB",
        "templates": [
            "샌디에이고랑 다저스 라이벌전은 언제 봐도 긴장감 넘치네요. 볼카운트 싸움 치열합니다.",
            "오늘 야마모토 스플리터 낙폭이 38인치라 타자들 배트가 허공을 가르네요. 무실점 호투 예상!",
            "타구 속도 105마일 이상 하드히트 비율(HardHit%) 45% 넘는 타선은 언제든 빅이닝 가능합니다."
        ]
    },
    {
        "author": "알리안츠직관러",
        "channel": "SOCCER",
        "sport_tag": "분데스리가",
        "templates": [
            "바이에른 뮌헨 케인-무시알라 연계 플레이 예술이네요. 원정에서 전반에만 멀티골 작렬!",
            "분데스리가 특유의 게겐프레싱 템포 살아나니까 턴오버 유발 후 5초 안에 슈팅까지 연결되네요.",
            "슈투트가르트 홈 승률 78% 기록중이라 배당 대비 기대치 아주 좋습니다."
        ]
    },
    {
        "author": "데이터로승부",
        "channel": "PREDICTION",
        "sport_tag": "AI픽",
        "templates": [
            "AI 승률 시뮬레이션 10,000회 돌려본 결과 홈팀 승률 68.4% 도출됩니다. 세이버 메트릭스 믿고 갑니다.",
            "피타고리안 승률이랑 실제 승률 괴리율 분석해보면 오늘 원정팀이 저평가되어 있어서 꿀배당이네요.",
            "실시간 라이브 스코어보드 갱신 속도 진짜 빠르네요! 위성 피드라 그런지 경기장 현장이랑 거의 동시입니다."
        ]
    }
]

_last_used_index = -1
_bot_running = False

async def start_ai_chat_bot_task():
    """Background task: posts an authentic AI sports commentary every 4 minutes (240s)"""
    global _bot_running, _last_used_index
    if _bot_running:
        return
    _bot_running = True
    logger.info("[AIChatBot] 4-minute AI Chat commentary scheduler started.")

    while True:
        try:
            await asyncio.sleep(240) # Exactly 4 minutes

            from app.api.v1.community import COMMUNITY_MESSAGES, manager
            global _last_used_index

            # Pick a distinct persona different from last one
            idx = random.randint(0, len(AI_PERSONAS) - 1)
            if idx == _last_used_index:
                idx = (idx + 1) % len(AI_PERSONAS)
            _last_used_index = idx

            persona = AI_PERSONAS[idx]
            author = persona["author"]
            channel = persona["channel"]
            sport_tag = persona["sport_tag"]
            content = random.choice(persona["templates"])

            new_id = (max([m.get("id", 0) for m in COMMUNITY_MESSAGES], default=0)) + 1
            chat_obj = {
                "id": new_id,
                "author": author,
                "channel": channel,
                "sport_tag": sport_tag,
                "content": content,
                "created_at": datetime.now().strftime("%H:%M"),
                "likes": random.randint(3, 16)
            }
            COMMUNITY_MESSAGES.append(chat_obj)

            # Broadcast to all connected clients
            await manager.broadcast({
                "type": "NEW_COMMUNITY_MESSAGE",
                "message": chat_obj
            })
            logger.info(f"[AIChatBot] Posted 4-min chat from '{author}': {content[:30]}...")
        except Exception as e:
            logger.error(f"[AIChatBot] Error posting chat message: {e}")
            await asyncio.sleep(30)
