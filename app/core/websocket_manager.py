# -*- coding: utf-8 -*-
import json
import logging
import asyncio
from typing import List, Dict, Any, Set
from fastapi import WebSocket
from app.core.config import settings

logger = logging.getLogger("sports_websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._loop = None
        self._redis_client = None
        self._redis_sub_task = None
        self._redis_channel = "sports_hub_ws_broadcast"

    def set_event_loop(self, loop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[WebSocket] 새 클라이언트 접속 완료. 현재 접속자 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"[WebSocket] 클라이언트 접속 종료. 현재 접속자 수: {len(self.active_connections)}")

    async def _broadcast_local(self, message: Dict[str, Any]):
        """현재 인스턴스(워커)에 연결된 모든 클라이언트에게 비동기 병렬 전송 (3,000명 트래픽 최적화)"""
        if not self.active_connections:
            return
        
        text_data = json.dumps(message, ensure_ascii=False)
        targets = list(self.active_connections)
        
        async def _safe_send(ws: WebSocket):
            try:
                # 개별 클라이언트 전송 타임아웃 2초 적용 (느린 3G/모바일 클라이언트 병목 차단)
                await asyncio.wait_for(ws.send_text(text_data), timeout=2.0)
                return None
            except Exception:
                return ws

        # 🚀 3,000명 동시 전송 시 블로킹 없이 병렬 동시 처리
        results = await asyncio.gather(*[_safe_send(conn) for conn in targets], return_exceptions=True)
        dead = [r for r in results if isinstance(r, WebSocket)]
        for d in dead:
            self.disconnect(d)

    async def broadcast(self, message: Dict[str, Any]):
        """Redis가 설정되어 있으면 전체 워커 노드로 분산 전송, 없으면 로컬 인스턴스에 즉시 전송"""
        if self._redis_client:
            try:
                payload = json.dumps(message, ensure_ascii=False)
                await self._redis_client.publish(self._redis_channel, payload)
                return
            except Exception as e:
                logger.warning(f"[WebSocket] Redis 발행 실패, 로컬 브로드캐스트로 대체: {e}")
        
        await self._broadcast_local(message)

    def broadcast_threadsafe(self, message: Dict[str, Any]):
        """스레드나 동기 함수에서 웹소켓 브로드캐스트를 안전하게 비동기 전송"""
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

    async def init_redis(self):
        """Redis 분산 Pub/Sub 초기화 (멀티 워커 환경 3,000명 동기화)"""
        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            logger.info("[WebSocket] REDIS_URL 미설정 -> 단일 프로세스 인메모리 모드로 동작합니다.")
            return

        try:
            import redis.asyncio as aioredis
            self._redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            pubsub = self._redis_client.pubsub()
            await pubsub.subscribe(self._redis_channel)
            logger.info(f"[WebSocket] Redis Pub/Sub 채널({self._redis_channel}) 연결 성공.")

            async def _reader():
                try:
                    async for msg in pubsub.listen():
                        if msg and msg.get("type") == "message":
                            raw_data = msg.get("data")
                            if raw_data:
                                try:
                                    parsed = json.loads(raw_data)
                                    await self._broadcast_local(parsed)
                                except Exception:
                                    pass
                except asyncio.CancelledError:
                    pass
                except Exception as ex:
                    logger.warning(f"[WebSocket] Redis 리스너 에러: {ex}")

            self._redis_sub_task = asyncio.create_task(_reader())
        except Exception as e:
            logger.warning(f"[WebSocket] Redis 초기화 실패 (로컬 모드로 전환): {e}")
            self._redis_client = None

    async def close(self):
        """리소스 정리"""
        if self._redis_sub_task:
            self._redis_sub_task.cancel()
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception:
                pass

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
