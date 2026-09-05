# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from app.core.websocket_manager import manager

logger = logging.getLogger("community_api")

router = APIRouter(tags=["Community & WebSocket"])

class ChatMessagePayload(BaseModel):
    author: str = "스포츠팬"
    channel: str = "ALL"  # ALL, BASEBALL, SOCCER, BASKETBALL, PREDICTION
    content: str
    sport_tag: Optional[str] = "일반"

# In-memory community storage seeded with authentic fan & analyst discussions
INITIAL_MESSAGES = [
    {
        "id": 1,
        "author": "세이버메트릭스매니아",
        "channel": "BASEBALL",
        "sport_tag": "MLB",
        "content": "오늘 다저스 선발 FIP 3.10에 불펜 2.85면 거의 무결점이네요. 상대 타선 잔루율 높은 거 보면 홈팀 승리 유력합니다.",
        "created_at": "19:10",
        "likes": 14
    },
    {
        "id": 2,
        "author": "토트넘팬클럽",
        "channel": "SOCCER",
        "sport_tag": "EPL",
        "content": "첼시 전반 xG 1.8 넘게 찍히는 거 보니까 압박 강도(PPDA 7.8)가 진짜 살벌하네요. 후반전 한 골 더 터질 듯!",
        "created_at": "19:15",
        "likes": 9
    },
    {
        "id": 3,
        "author": "KBO현장직관러",
        "channel": "BASEBALL",
        "sport_tag": "KBO",
        "content": "오늘 잠실 경기 바람 영향 좀 있는 거 같아요. 타구 속도랑 발사각 지표 확인하고 가야 할 듯요.",
        "created_at": "19:18",
        "likes": 7
    },
    {
        "id": 4,
        "author": "NBA빅데이터분석",
        "channel": "BASKETBALL",
        "sport_tag": "NBA",
        "content": "보스턴 셀틱스 eFG% 57% 찍는 날은 10점차 이상 대승 확률이 80% 넘어갑니다. Pace 101 유지하면 무난히 마핸 갈 듯!",
        "created_at": "19:22",
        "likes": 12
    },
    {
        "id": 5,
        "author": "축구도사",
        "channel": "SOCCER",
        "sport_tag": "KLEAGUE",
        "content": "K리그 서울 vs 수원 더비 분석 데이터 보셨나요? 파이널 서드 지배율(Field Tilt)이 62%라 박스 투입 빈도 높습니다.",
        "created_at": "19:25",
        "likes": 8
    }
]

COMMUNITY_MESSAGES = list(INITIAL_MESSAGES)
_msg_id_counter = len(COMMUNITY_MESSAGES) + 1

@router.get("/community/messages", summary="실시간 커뮤니티 대화 및 토론 피드 목록")
def get_community_messages(channel: Optional[str] = Query(None)):
    if channel and channel != "ALL":
        filtered = [m for m in COMMUNITY_MESSAGES if m["channel"] == channel]
        return filtered[-50:]
    return COMMUNITY_MESSAGES[-50:]

@router.post("/community/messages", summary="새 커뮤니티 글/댓글 등록 및 웹소켓 브로드캐스트")
async def post_community_message(payload: ChatMessagePayload):
    global _msg_id_counter
    new_msg = {
        "id": _msg_id_counter,
        "author": payload.author.strip() or "스포츠팬",
        "channel": payload.channel,
        "sport_tag": payload.sport_tag or "일반",
        "content": payload.content.strip(),
        "created_at": datetime.now().strftime("%H:%M"),
        "likes": 0
    }
    _msg_id_counter += 1
    COMMUNITY_MESSAGES.append(new_msg)

    # Broadcast to all connected WebSocket users in real time
    await manager.broadcast({
        "type": "NEW_COMMUNITY_MESSAGE",
        "message": new_msg
    })
    return {"status": "SUCCESS", "message": new_msg}

@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """
    실시간 경기 스코어 업데이트 및 실시간 팬 커뮤니티 채팅 웹소켓 엔드포인트
    """
    await manager.connect(websocket)
    # Send connection welcome and current client count
    await websocket.send_text(json.dumps({
        "type": "CONNECTION_ESTABLISHED",
        "message": "tokeon.kr 실시간 스포츠 & 커뮤니티 웹소켓에 정상 연결되었습니다.",
        "active_clients": len(manager.active_connections)
    }, ensure_ascii=False))

    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                msg_json = json.loads(data_text)
                m_type = msg_json.get("type")

                if m_type == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG", "time": datetime.now().isoformat()}))
                elif m_type == "CHAT":
                    global _msg_id_counter
                    author = str(msg_json.get("author", "스포츠팬")).strip()
                    content = str(msg_json.get("content", "")).strip()
                    channel = str(msg_json.get("channel", "ALL"))
                    sport_tag = str(msg_json.get("sport_tag", "일반"))

                    if content:
                        chat_obj = {
                            "id": _msg_id_counter,
                            "author": author or "스포츠팬",
                            "channel": channel,
                            "sport_tag": sport_tag,
                            "content": content,
                            "created_at": datetime.now().strftime("%H:%M"),
                            "likes": 0
                        }
                        _msg_id_counter += 1
                        COMMUNITY_MESSAGES.append(chat_obj)

                        # Broadcast to all users
                        await manager.broadcast({
                            "type": "NEW_COMMUNITY_MESSAGE",
                            "message": chat_obj
                        })
            except Exception as ex:
                logger.error(f"[WebSocket Parse Error] {ex}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[WebSocket Error] {e}")
        manager.disconnect(websocket)
