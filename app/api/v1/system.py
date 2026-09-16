# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.core.error_monitor import record_error, get_recent_errors, is_sentry_active

router = APIRouter(prefix="/system", tags=["System"])

class ClientErrorPayload(BaseModel):
    type: str = "ClientError"
    message: str
    detail: Optional[str] = ""
    path: Optional[str] = ""

@router.get("/errors")
def get_system_errors():
    """
    시스템 최근 100건 에러 조회 및 Sentry 연동 상태 확인
    """
    return {
        "sentry_active": is_sentry_active(),
        "total_errors": len(get_recent_errors()),
        "errors": get_recent_errors()
    }

@router.post("/client-error")
def log_client_error(payload: ClientErrorPayload, request: Request):
    """
    프론트엔드 브라우저에서 발생한 JS 에러 수집
    """
    client_ip = request.client.host if request.client else "unknown"
    path_with_ip = f"{payload.path or ''} (IP: {client_ip})"
    record_error(
        source="FRONTEND",
        error_type=payload.type,
        message=payload.message,
        detail=payload.detail,
        path=path_with_ip
    )
    return {"status": "ok"}

@router.get("/cache-status")
def get_cache_status():
    """
    Redis 및 인메모리 TTL 캐시 상태와 적중률(Hit-Rate) 통계 조회
    """
    from app.core.cache import get_cache_stats
    return get_cache_stats()
