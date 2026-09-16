# -*- coding: utf-8 -*-
import json
import logging
import asyncio
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("sports_websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop = None

    def set_event_loop(self, loop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WebSocket] 새 클라이언트 접속 완료. 현재 접속자 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[WebSocket] 클라이언트 접속 종료. 현재 접속자 수: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        if not self.active_connections:
            return
        dead_connections = []
        text_data = json.dumps(message, ensure_ascii=False)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(text_data)
            except Exception:
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)

    def broadcast_threadsafe(self, message: Dict[str, Any]):
        """스레드나 동기 함수에서 웹소켓 브로드캐스트를 안전하게 비동기 전송"""
        if not self.active_connections:
            return
        try:
            loop = self._loop
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(self.broadcast(message), loop)
            else:
                try:
                    cur_loop = asyncio.get_running_loop()
                    cur_loop.create_task(self.broadcast(message))
                except RuntimeError:
                    pass
        except Exception as e:
            logger.warning(f"[WebSocket] broadcast_threadsafe warning: {e}")

    async def broadcast_live_scores(self, matches: List[Dict[str, Any]]):
        await self.broadcast({
            "type": "LIVE_SCORE_UPDATE",
            "matches": matches
        })

    def broadcast_live_scores_sync(self, matches: List[Dict[str, Any]]):
        self.broadcast_threadsafe({
            "type": "LIVE_SCORE_UPDATE",
            "matches": matches
        })

manager = ConnectionManager()
