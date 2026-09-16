# -*- coding: utf-8 -*-
import os
import json
import time
import logging
from typing import Any, Optional, Dict
from app.core.config import settings

logger = logging.getLogger("cache_service")

_REDIS_CLIENT = None
_IS_REDIS_ACTIVE = False
_LOCAL_CACHE: Dict[str, tuple[float, Any]] = {}  # key -> (expire_at, value)
_CACHE_STATS = {
    "hits": 0,
    "misses": 0,
    "sets": 0
}

def init_cache():
    global _REDIS_CLIENT, _IS_REDIS_ACTIVE
    redis_url = getattr(settings, 'REDIS_URL', None) or os.getenv('REDIS_URL', '')
    if redis_url and redis_url.strip():
        try:
            import redis
            client = redis.from_url(
                redis_url.strip(),
                decode_responses=True,
                socket_timeout=1.5,
                socket_connect_timeout=1.5
            )
            client.ping()
            _REDIS_CLIENT = client
            _IS_REDIS_ACTIVE = True
            logger.info(f"[Cache] Redis 연결 성공 및 활성화 완료 ({redis_url[:16]}...)")
        except Exception as e:
            _IS_REDIS_ACTIVE = False
            _REDIS_CLIENT = None
            logger.warning(f"[Cache] Redis 연결 실패: {e}. 인메모리 고속 캐시로 자동 전환합니다.")
    else:
        logger.info("[Cache] REDIS_URL 미설정. 고속 인메모리(TTL) 캐시 레이어로 작동합니다.")

def is_redis_active() -> bool:
    return _IS_REDIS_ACTIVE

def cache_get(key: str) -> Optional[str]:
    global _CACHE_STATS
    if _IS_REDIS_ACTIVE and _REDIS_CLIENT:
        try:
            val = _REDIS_CLIENT.get(key)
            if val is not None:
                _CACHE_STATS["hits"] += 1
                return val
            _CACHE_STATS["misses"] += 1
            return None
        except Exception as e:
            logger.warning(f"[Cache] Redis get error on {key}: {e}")

    # Fallback to in-memory cache
    now = time.time()
    if key in _LOCAL_CACHE:
        expire_at, val = _LOCAL_CACHE[key]
        if expire_at > now:
            _CACHE_STATS["hits"] += 1
            return val
        else:
            del _LOCAL_CACHE[key]
    _CACHE_STATS["misses"] += 1
    return None

def cache_set(key: str, value: str, ttl_seconds: int = 300) -> bool:
    global _CACHE_STATS
    _CACHE_STATS["sets"] += 1
    if _IS_REDIS_ACTIVE and _REDIS_CLIENT:
        try:
            _REDIS_CLIENT.setex(key, ttl_seconds, value)
            return True
        except Exception as e:
            logger.warning(f"[Cache] Redis set error on {key}: {e}")

    # Fallback in-memory
    now = time.time()
    _LOCAL_CACHE[key] = (now + ttl_seconds, value)
    
    # Prune expired items if cache grows large
    if len(_LOCAL_CACHE) > 1000:
        expired_keys = [k for k, (exp, _) in _LOCAL_CACHE.items() if exp <= now]
        for k in expired_keys:
            _LOCAL_CACHE.pop(k, None)

    return True

def cache_get_json(key: str) -> Optional[Any]:
    val = cache_get(key)
    if val:
        try:
            return json.loads(val)
        except Exception:
            return None
    return None

def cache_set_json(key: str, data: Any, ttl_seconds: int = 300) -> bool:
    try:
        val = json.dumps(data, ensure_ascii=False)
        return cache_set(key, val, ttl_seconds=ttl_seconds)
    except Exception as e:
        logger.warning(f"[Cache] JSON serialization failed for {key}: {e}")
        return False

def cache_delete(key: str) -> bool:
    if _IS_REDIS_ACTIVE and _REDIS_CLIENT:
        try:
            _REDIS_CLIENT.delete(key)
        except Exception:
            pass
    _LOCAL_CACHE.pop(key, None)
    return True

def get_cache_stats() -> Dict[str, Any]:
    now = time.time()
    active_local_keys = sum(1 for _, (exp, _) in _LOCAL_CACHE.items() if exp > now)
    total_reqs = _CACHE_STATS["hits"] + _CACHE_STATS["misses"]
    hit_rate = round((_CACHE_STATS["hits"] / total_reqs * 100), 1) if total_reqs > 0 else 0.0

    return {
        "redis_active": _IS_REDIS_ACTIVE,
        "backend": "REDIS" if _IS_REDIS_ACTIVE else "IN_MEMORY_TTL",
        "active_keys": active_local_keys if not _IS_REDIS_ACTIVE else "managed_by_redis",
        "stats": _CACHE_STATS,
        "hit_rate_pct": hit_rate
    }
