# -*- coding: utf-8 -*-
import os
import json
import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/auth", tags=["Member Auth & Registry"])

logger = logging.getLogger("auth_members")

MEMBERS_DIR = os.path.join(os.getcwd(), "data", "members")
JSON_PATH = os.path.join(MEMBERS_DIR, "registered_users.json")
TXT_PATH = os.path.join(MEMBERS_DIR, "member_summary.txt")
LOGS_PATH = os.path.join(MEMBERS_DIR, "access_logs.json")
LOGS_TXT_PATH = os.path.join(MEMBERS_DIR, "access_history.txt")

import hashlib
import threading

SALT = "tokeon_secure_auth_salt_2026"
_AUTH_FILE_LOCK = threading.Lock()

ADMIN_NICKNAMES = {"whathehas", "운영자", "admin", "관리자", "master", "root", "tokeon"}

def _is_admin(nickname: str) -> bool:
    if not nickname:
        return False
    nick = nickname.strip().lower()
    return nick in {n.lower() for n in ADMIN_NICKNAMES} or "whathehas" in nick or "운영자" in nick or "admin" in nick

# 실시간 접속 세션 메모리 보관: nickname -> {nickname, ip, last_active, last_active_ts, device}
_ACTIVE_SESSIONS = {}

def _record_session_activity(nickname: str, ip: str = "127.0.0.1", device: str = "웹"):
    if not nickname:
        return
    now = datetime.now()
    _ACTIVE_SESSIONS[nickname] = {
        "nickname": nickname,
        "ip": ip,
        "last_active": now.strftime("%Y-%m-%d %H:%M:%S"),
        "last_active_ts": now.timestamp(),
        "device": device
    }

def _hash_password(pw: str) -> str:
    if not pw:
        return ""
    return hashlib.sha256(f"{SALT}_{pw}".encode("utf-8")).hexdigest()

class UserLoginPayload(BaseModel):
    nickname: str
    password: str
    age: Optional[int] = 30

class UserRegisterPayload(BaseModel):
    nickname: str
    password: str
    age: Optional[int] = 30

class SessionPingPayload(BaseModel):
    nickname: str

def _ensure_dir():
    os.makedirs(MEMBERS_DIR, exist_ok=True)

def _load_members() -> List[dict]:
    with _AUTH_FILE_LOCK:
        _ensure_dir()
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

def _load_access_logs() -> List[dict]:
    with _AUTH_FILE_LOCK:
        _ensure_dir()
        if os.path.exists(LOGS_PATH):
            try:
                with open(LOGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

def _record_access_log(user_dict: dict, ip: str = "127.0.0.1"):
    with _AUTH_FILE_LOCK:
        _ensure_dir()
        logs = []
        if os.path.exists(LOGS_PATH):
            try:
                with open(LOGS_PATH, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": now_str,
            "user_id": user_dict.get("id"),
            "nickname": user_dict.get("nickname"),
            "age": user_dict.get("age", 30),
            "login_count": user_dict.get("login_count", 1),
            "ip": ip
        }
        logs.insert(0, entry)
        if len(logs) > 500:
            logs = logs[:500]

        try:
            with open(LOGS_PATH, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)

            with open(LOGS_TXT_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}] '{user_dict.get('nickname')}' ({user_dict.get('age', 30)}세) 로그인 접속 (누적 {user_dict.get('login_count', 1)}회차) | IP: {ip}\n")
        except Exception as e:
            logger.warning(f"Failed to record access log: {e}")

def _clean_phone_digits(val: str) -> str:
    if not val:
        return ""
    return "".join(c for c in str(val) if c.isdigit())

def _find_member(members: List[dict], identifier: str) -> Optional[dict]:
    if not identifier:
        return None
    raw = identifier.strip()
    raw_lower = raw.lower()
    digits = _clean_phone_digits(raw)

    for m in members:
        if m.get("nickname", "").strip().lower() == raw_lower:
            return m
        if m.get("phone", "").strip().lower() == raw_lower:
            return m

    if len(digits) >= 8:
        for m in members:
            m_nick_digits = _clean_phone_digits(m.get("nickname", ""))
            m_phone_digits = _clean_phone_digits(m.get("phone", ""))
            if digits == m_nick_digits or digits == m_phone_digits:
                return m

    clean_id_str = raw.lstrip("#").strip()
    if clean_id_str.isdigit():
        try:
            num_id = int(clean_id_str)
            for m in members:
                if m.get("id") == num_id:
                    return m
        except Exception:
            pass

    return None

def _save_members(members: List[dict]):
    with _AUTH_FILE_LOCK:
        _ensure_dir()
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(members, f, ensure_ascii=False, indent=2)

            with open(TXT_PATH, "w", encoding="utf-8") as f:
                f.write("======================================================================\n")
                f.write("  TOKEON ANALYTICS 회원 접속 & 가입 현황 목록 (실시간 자동 기록 관리자 전용)\n")
                f.write(f"  총 등록 회원 수: {len(members)}명\n")
                f.write(f"  최종 갱신 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("======================================================================\n")
                f.write(f"{'번호':<6} {'별명(닉네임)':<22} {'나이':<10} {'총접속횟수':<12} {'가입일시':<22} {'최근접속일시':<22}\n")
                f.write("-" * 96 + "\n")
                for m in members:
                    display_name = m.get('nickname', '')
                    f.write(f"{m['id']:<6} {display_name:<22} {str(m.get('age', 30)) + '세':<10} {str(m.get('login_count', 1)) + '회':<12} {m.get('registered_at', '-'):<22} {m.get('last_login_at', '-'):<22}\n")
                f.write("=" * 96 + "\n")
        except Exception as e:
            logger.warning(f"Failed to save members: {e}")

@router.post("/login", summary="별명 + 나이 + 비밀번호 간편 로그인 & 접속 기록")
def login_user(payload: UserLoginPayload, request: Request):
    nickname = payload.nickname.strip()
    age = payload.age if (payload.age and payload.age > 0) else 30
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="별명(닉네임)을 입력해주세요.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")

    members = _load_members()
    existing = _find_member(members, nickname)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 계정이 없을 경우 즉시 간편 자동 가입 & 로그인 처리 (0초 접속)
    if not existing:
        new_id = (max([m["id"] for m in members], default=0)) + 1
        clean_phone = _clean_phone_digits(nickname)
        is_phone = len(clean_phone) >= 10

        target_user = {
            "id": new_id,
            "nickname": nickname,
            "phone": clean_phone if is_phone else "",
            "age": age,
            "password_hash": _hash_password(password),
            "registered_at": now_str,
            "login_count": 1,
            "last_login_at": now_str
        }
        is_admin = _is_admin(nickname)
        target_user["is_admin"] = is_admin
        target_user["role"] = "admin" if is_admin else "user"
        members.insert(0, target_user)
        _save_members(members)
        _record_access_log(target_user, client_ip)
        _record_session_activity(nickname, client_ip, request.headers.get("user-agent", "웹")[:40])
        logger.info(f"[Member Auto-Registered on Login] Nickname: {nickname}, Age: {age}, IsAdmin: {is_admin}")

        user_info = {
            "id": new_id,
            "nickname": nickname,
            "age": age,
            "registered_at": now_str,
            "login_count": 1,
            "last_login_at": now_str,
            "is_admin": is_admin,
            "role": "admin" if is_admin else "user"
        }
        return {
            "status": "success",
            "message": f"'{nickname}'님 계정이 안전하게 등록되어 즉시 접속되었습니다!",
            "user": user_info
        }

    hashed = _hash_password(password)
    # 기존에 비밀번호 없이 등록되었던 계정은 이번에 입력한 비밀번호로 최초 등록 및 연동
    if "password_hash" not in existing or not existing["password_hash"]:
        existing["password_hash"] = hashed
    elif existing["password_hash"] != hashed:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다. 다시 확인해주세요.")

    existing["login_count"] = existing.get("login_count", 1) + 1
    existing["last_login_at"] = now_str
    if age and age > 0:
        existing["age"] = age
    
    clean_digits = _clean_phone_digits(nickname)
    if len(clean_digits) >= 10 and not existing.get("phone"):
        existing["phone"] = clean_digits

    is_admin = _is_admin(existing["nickname"])
    existing["is_admin"] = is_admin
    existing["role"] = "admin" if is_admin else "user"

    _save_members(members)
    _record_access_log(existing, client_ip)
    _record_session_activity(existing["nickname"], client_ip, request.headers.get("user-agent", "웹")[:40])

    user_info = {
        "id": existing["id"],
        "nickname": existing["nickname"],
        "age": existing.get("age", age),
        "registered_at": existing.get("registered_at", now_str),
        "login_count": existing["login_count"],
        "last_login_at": existing["last_login_at"],
        "is_admin": is_admin,
        "role": "admin" if is_admin else "user"
    }
    logger.info(f"[Member Login Success] Nickname: {existing['nickname']}, Logins: {existing['login_count']}, IsAdmin: {is_admin}")
    return {
        "status": "success",
        "message": f"'{existing['nickname']}'님 환영합니다! (누적 {existing['login_count']}회 접속)",
        "user": user_info
    }

@router.post("/register-user", summary="별명 + 비밀번호 신규 가입")
def register_user(payload: UserRegisterPayload, request: Request):
    nickname = payload.nickname.strip()
    age = payload.age if (payload.age and payload.age > 0) else 30
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="별명을 입력해주세요.")
    if len(nickname) > 30:
        raise HTTPException(status_code=400, detail="별명은 최대 30자까지 가능합니다.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 4자리 이상이어야 합니다.")

    members = _load_members()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.client.host if request.client else "127.0.0.1"

    is_admin = _is_admin(nickname)

    existing = _find_member(members, nickname)
    if existing:
        existing["password_hash"] = _hash_password(password)
        existing["last_login_at"] = now_str
        existing["login_count"] = existing.get("login_count", 1) + 1
        existing["age"] = age
        existing["is_admin"] = is_admin
        existing["role"] = "admin" if is_admin else "user"
        _save_members(members)
        _record_access_log(existing, client_ip)
        _record_session_activity(existing["nickname"], client_ip, request.headers.get("user-agent", "웹")[:40])
        user_info = {
            "id": existing["id"],
            "nickname": existing["nickname"],
            "age": existing.get("age", age),
            "registered_at": existing.get("registered_at", now_str),
            "login_count": existing["login_count"],
            "last_login_at": existing["last_login_at"],
            "is_admin": is_admin,
            "role": "admin" if is_admin else "user"
        }
        return {
            "status": "success",
            "message": f"'{existing['nickname']}'님 기존 등록 계정으로 즉시 로그인되었습니다.",
            "user": user_info
        }

    new_id = (max([m["id"] for m in members], default=0)) + 1
    clean_phone = _clean_phone_digits(nickname)
    is_phone = len(clean_phone) >= 10

    target_user = {
        "id": new_id,
        "nickname": nickname,
        "phone": clean_phone if is_phone else "",
        "age": age,
        "password_hash": _hash_password(password),
        "registered_at": now_str,
        "login_count": 1,
        "last_login_at": now_str,
        "is_admin": is_admin,
        "role": "admin" if is_admin else "user"
    }
    members.insert(0, target_user)

    _save_members(members)
    _record_access_log(target_user, client_ip)
    _record_session_activity(nickname, client_ip, request.headers.get("user-agent", "웹")[:40])
    logger.info(f"[Member Registered] Nickname: {nickname}, Total: {len(members)}, IsAdmin: {is_admin}")

    user_info = {
        "id": new_id,
        "nickname": nickname,
        "age": age,
        "registered_at": now_str,
        "login_count": 1,
        "last_login_at": now_str,
        "is_admin": is_admin,
        "role": "admin" if is_admin else "user"
    }

    return {
        "status": "success",
        "message": f"'{nickname}'님 회원가입이 완료되었습니다!",
        "user": user_info
    }

@router.post("/ping-session", summary="로그인 회원 실시간 접속 유지 핑 (Heartbeat)")
def ping_session(payload: SessionPingPayload, request: Request):
    nickname = payload.nickname.strip()
    if nickname:
        client_ip = request.client.host if request.client else "127.0.0.1"
        ua = request.headers.get("user-agent", "")
        device = "모바일" if any(k in ua.lower() for k in ["mobi", "android", "iphone"]) else "PC"
        _record_session_activity(nickname, client_ip, device)
    return {"status": "ok"}

@router.get("/admin/live-visitors", summary="[운영자 전용] 실시간 접속자 및 회원 현황")
def get_admin_live_visitors(request: Request, admin_nick: Optional[str] = None, nickname: Optional[str] = None):
    # Operator validation: check admin_nick, nickname parameter, or custom header
    caller_nick = admin_nick or nickname or request.headers.get("x-user-nickname", "")
    if not caller_nick or not _is_admin(caller_nick):
        raise HTTPException(status_code=403, detail="운영자(whathehas)만 접근할 수 있는 페이지입니다.")

    now_ts = datetime.now().timestamp()
    # Filter sessions active within last 10 minutes (600 seconds)
    online_members = []
    for nick, sess in list(_ACTIVE_SESSIONS.items()):
        diff_sec = now_ts - sess.get("last_active_ts", 0)
        if diff_sec <= 600:
            online_members.append({
                "nickname": nick,
                "ip": sess.get("ip", "-"),
                "last_active": sess.get("last_active"),
                "device": sess.get("device", "웹"),
                "is_online": True,
                "idle_sec": int(diff_sec)
            })

    online_members.sort(key=lambda x: x["idle_sec"])

    members = _load_members()
    logs = _load_access_logs()

    online_nick_set = {m["nickname"].lower() for m in online_members}
    all_members_with_status = []
    total_logins = 0
    for m in members:
        is_on = m["nickname"].lower() in online_nick_set
        safe_m = {
            "id": m["id"],
            "nickname": m["nickname"],
            "age": m.get("age", 30),
            "login_count": m.get("login_count", 1),
            "registered_at": m.get("registered_at", "-"),
            "last_login_at": m.get("last_login_at", "-"),
            "is_online": is_on,
            "is_admin": _is_admin(m.get("nickname", ""))
        }
        total_logins += safe_m["login_count"]
        all_members_with_status.append(safe_m)

    all_members_with_status.sort(key=lambda x: (not x["is_online"], -x.get("login_count", 0)))

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_visitors = set()
    for l in logs:
        if l.get("timestamp", "").startswith(today_str):
            today_visitors.add(l.get("nickname"))

    return {
        "status": "success",
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_registered_users": len(members),
        "today_unique_visitors": len(today_visitors),
        "current_online_count": len(online_members),
        "total_logins": total_logins,
        "online_users": online_members,
        "all_members": all_members_with_status,
        "recent_logs": logs[:100]
    }

@router.get("/admin/access-stats", summary="[관리자 전용] 회원별 접속 통계 및 실시간 로그인 이력 조회")
def get_admin_access_stats():
    members = _load_members()
    logs = _load_access_logs()

    safe_members = []
    total_logins = 0
    for m in members:
        safe_m = {
            "id": m["id"],
            "nickname": m["nickname"],
            "age": m.get("age", 30),
            "login_count": m.get("login_count", 1),
            "registered_at": m.get("registered_at", "-"),
            "last_login_at": m.get("last_login_at", "-"),
            "is_admin": _is_admin(m.get("nickname", ""))
        }
        total_logins += safe_m["login_count"]
        safe_members.append(safe_m)

    safe_members.sort(key=lambda x: x.get("login_count", 0), reverse=True)

    return {
        "status": "success",
        "total_users": len(safe_members),
        "total_logins": total_logins,
        "storage_paths": {
            "json_file": JSON_PATH,
            "txt_report": TXT_PATH,
            "access_log_file": LOGS_TXT_PATH
        },
        "members": safe_members,
        "recent_logs": logs[:100]
    }
