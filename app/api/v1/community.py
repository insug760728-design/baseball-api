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
    """로컬 DB에서 어제/오늘 종료된 실제 공식 경기 결과를 가볍고 산뜻하게 추출하여 커뮤니티 피드 초기화"""
    from app.core.database import SessionLocal
    from app.models.models import Match
    import random

    msgs = []
    db = SessionLocal()
    try:
        now = datetime.now(KST)
        since_date = (now - timedelta(days=2)).strftime("%Y-%m-%d 00:00")
        matches = db.query(Match).filter(
            Match.status == "FINISHED",
            Match.match_date >= since_date
        ).order_by(Match.match_date.desc()).limit(8).all()

        sport_icons = {'BASEBALL': '⚾', 'SOCCER': '⚽', 'BASKETBALL': '🏀', 'VOLLEYBALL': '🏐'}
        author_pool = ['전일경기알리미', '스코어브리핑', '스포츠결과센터', '실시간결과알림', '경기요약봇']

        for idx, m in enumerate(matches, 1):
            icon = sport_icons.get(m.sport_code, '🏆')
            league = (m.league_name or '').split('(')[0].strip() or m.sport_code
            h_score = m.home_score if m.home_score is not None else '-'
            a_score = m.away_score if m.away_score is not None else '-'
            m_date = (m.match_date or '')[:10]
            today_str = now.strftime('%Y-%m-%d')
            prefix = '[오늘 경기결과]' if m_date == today_str else '[전일 경기결과]'
            content = f"{prefix} {icon} {league} | {m.home_team_name} {h_score} : {a_score} {m.away_team_name} (종료)"

            post_time = (now - timedelta(minutes=5 + idx * 4)).strftime("%H:%M")
            sport_tag = "MLB" if "MLB" in (m.league_name or "") else ("KBO" if "KBO" in (m.league_name or "") else m.sport_code[:6])

            msgs.append({
                "id": idx,
                "author": author_pool[idx % len(author_pool)],
                "channel": m.sport_code if m.sport_code in ["BASEBALL", "SOCCER"] else "ALL",
                "sport_tag": sport_tag,
                "content": content,
                "created_at": post_time,
                "likes": random.randint(6, 18)
            })
    except Exception as e:
        logger.warning(f"Failed to load initial match results for community: {e}")
    finally:
        db.close()

    if not msgs:
        msgs = [
            {
                "id": 1,
                "author": "스포츠결과센터",
                "channel": "ALL",
                "sport_tag": "종합",
                "content": "[경기 알림] 어제 및 오늘 경기 결과가 순차적으로 실시간 등록됩니다.",
                "created_at": get_kst_time_str(),
                "likes": 10
            }
        ]
    msgs.reverse()
    return msgs

COMMUNITY_MESSAGES = load_recent_finished_messages()
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
    # Send connection welcome and synchronized client count (664 + active connections)
    await websocket.send_text(json.dumps({
        "type": "CONNECTION_ESTABLISHED",
        "message": "tokeon.kr 실시간 스포츠 & 커뮤니티 웹소켓에 정상 연결되었습니다.",
        "active_clients": 664 + len(manager.active_connections)
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
