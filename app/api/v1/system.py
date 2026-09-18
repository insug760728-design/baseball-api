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

@router.get("/storage")
def get_system_storage():
    """
    서버 디스크 저장공간 및 컨테이너 리소스 상태 조회
    """
    import shutil
    import os
    from app.core.config import settings
    
    total, used, free = shutil.disk_usage("/")
    
    db_info = {}
    if "sqlite" in settings.DATABASE_URL:
        db_path = settings.DATABASE_URL.replace("sqlite:///", "").split("?")[0]
        if os.path.exists(db_path):
            db_info["path"] = db_path
            db_info["size_mb"] = round(os.path.getsize(db_path) / (1024 * 1024), 2)
        else:
            db_info["path"] = db_path
            db_info["exists"] = False
    else:
        db_info["type"] = "External Database"
        
    mem_info = {}
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        k = parts[0].strip()
                        if k in ["MemTotal", "MemFree", "MemAvailable"]:
                            mem_info[k] = round(int(parts[1].strip().split()[0]) / 1024, 1)
        except Exception:
            pass

    return {
        "status": "ok",
        "disk": {
            "total_gb": round(total / (1024 ** 3), 2),
            "used_gb": round(used / (1024 ** 3), 2),
            "free_gb": round(free / (1024 ** 3), 2),
            "free_percent": round((free / total) * 100, 1) if total else 0
        },
        "database": db_info,
        "memory_mb": mem_info
    }

