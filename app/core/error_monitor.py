# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import datetime
from collections import deque
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("error_monitor")

_RECENT_ERRORS = deque(maxlen=100)
_IS_SENTRY_ACTIVE = False

def init_error_monitoring():
    global _IS_SENTRY_ACTIVE
    dsn = getattr(settings, 'SENTRY_DSN', None) or ""
    if dsn and dsn.strip():
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            sentry_sdk.init(
                dsn=dsn.strip(),
                traces_sample_rate=0.2,
                profiles_sample_rate=0.1,
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    StarletteIntegration(transaction_style="endpoint")
                ],
                send_default_pii=False,
                environment="production"
            )
            _IS_SENTRY_ACTIVE = True
            logger.info("Sentry SDK successfully initialized and active.")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry SDK: {e}")
    else:
        logger.info("Sentry DSN not configured. Using local in-memory Error Monitor.")

def record_error(source: str, error_type: str, message: str, detail: Optional[str] = None, path: Optional[str] = None):
    item = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "type": error_type,
        "message": message,
        "detail": detail or "",
        "path": path or ""
    }
    _RECENT_ERRORS.appendleft(item)
    logger.error(f"[{source}] {error_type}: {message} (path: {path})")

def capture_exception(e: Exception, path: str = ""):
    tb = traceback.format_exc()
    record_error(
        source="BACKEND",
        error_type=e.__class__.__name__,
        message=str(e),
        detail=tb,
        path=path
    )
    if _IS_SENTRY_ACTIVE:
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
        except Exception:
            pass

def get_recent_errors():
    return list(_RECENT_ERRORS)

def is_sentry_active():
    return _IS_SENTRY_ACTIVE
