# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from app.core.websocket_manager import manager

logger = logging.getLogger("community_api")

KST = timezone(timedelta(hours=9))

def get_kst_time_str() -> str:
    return datetime.now(KST).strftime("%H:%M")

router = APIRouter(tags=["Community & WebSocket"])

class ChatMessagePayload(BaseModel):
    author: str = "스포츠팬"
    channel: str = "ALL"  # ALL, BASEBALL, SOCCER, BASKETBALL, PREDICTION
    content: str
    sport_tag: Optional[str] = "일반"

def load_recent_finished_messages() -> List[dict]:
    """사용자 요청에 따라 커뮤니티 채팅창 초기 메시지 완전 비움"""
    return []

COMMUNITY_MESSAGES = []
_msg_id_counter = 1

@router.get("/community/messages", summary="실시간 커뮤니티 대화 및 토론 피드 목록")
def get_community_messages(channel: Optional[str] = Query(None)):
    if channel and channel != "ALL":
        filtered = [m for m in COMMUNITY_MESSAGES if m["channel"] == channel]
        return filtered[-50:]
    return COMMUNITY_MESSAGES[-50:]

@router.post("/community/clear", summary="커뮤니티 채팅창 전체 비우기")
async def clear_community_messages():
    global COMMUNITY_MESSAGES, _msg_id_counter
    COMMUNITY_MESSAGES.clear()
    _msg_id_counter = 1
    await manager.broadcast({
        "type": "CLEAR_COMMUNITY_MESSAGES"
    })
    return {"status": "ok", "message": "채팅창이 완전히 비워졌습니다."}

@router.post("/community/messages", summary="새 커뮤니티 글/댓글 등록 및 웹소켓 브로드캐스트")
async def post_community_message(payload: ChatMessagePayload):
    global _msg_id_counter
    new_msg = {
        "id": _msg_id_counter,
        "author": payload.author.strip() or "스포츠팬",
        "channel": payload.channel,
        "sport_tag": payload.sport_tag or "일반",
        "content": payload.content.strip(),
        "created_at": get_kst_time_str(),
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
    # Send connection welcome and synchronized client count
    from app.services.traffic_service import TrafficService
    live_count = TrafficService.get_realtime_active_count() + len(manager.active_connections)
    await websocket.send_text(json.dumps({
        "type": "CONNECTION_ESTABLISHED",
        "message": "tokeon.kr 실시간 스포츠 & 커뮤니티 웹소켓에 정상 연결되었습니다.",
        "active_clients": live_count
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
                            "created_at": get_kst_time_str(),
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
