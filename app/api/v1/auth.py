# -*- coding: utf-8 -*-
import os
import json
import logging
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["Member Auth & Registry"])

logger = logging.getLogger("auth_members")

MEMBERS_DIR = os.path.join(os.getcwd(), "data", "members")
JSON_PATH = os.path.join(MEMBERS_DIR, "registered_users.json")
TXT_PATH = os.path.join(MEMBERS_DIR, "member_summary.txt")

import hashlib

SALT = "tokeon_secure_auth_salt_2026"

def _hash_password(pw: str) -> str:
    if not pw:
        return ""
    return hashlib.sha256(f"{SALT}_{pw}".encode("utf-8")).hexdigest()

class UserLoginPayload(BaseModel):
    nickname: str
    password: str

class UserRegisterPayload(BaseModel):
    nickname: str
    age: Optional[int] = 30
    password: str

def _ensure_dir():
    os.makedirs(MEMBERS_DIR, exist_ok=True)

def _load_members() -> List[dict]:
    _ensure_dir()
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

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

    # 1. Exact / case-insensitive nickname or phone match
    for m in members:
        if m.get("nickname", "").strip().lower() == raw_lower:
            return m
        if m.get("phone", "").strip().lower() == raw_lower:
            return m

    # 2. Phone digits match (e.g. 01012345678 == 010-1234-5678)
    if len(digits) >= 8:
        for m in members:
            m_nick_digits = _clean_phone_digits(m.get("nickname", ""))
            m_phone_digits = _clean_phone_digits(m.get("phone", ""))
            if digits == m_nick_digits or digits == m_phone_digits:
                return m

    # 3. Numeric ID match (e.g. 7 or #7)
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
    _ensure_dir()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write("======================================================================\n")
        f.write("  TOKEON ANALYTICS (tokeon.co.kr) 회원 가입 현황 목록 (실시간 자동 기록)\n")
        f.write(f"  총 가입 회원 수: {len(members)}명\n")
        f.write(f"  최종 갱신 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("======================================================================\n")
        f.write(f"{'번호':<6} {'별명/휴대폰번호':<22} {'연령(나이)':<12} {'가입일시':<22} {'접속횟수':<8}\n")
        f.write("-" * 74 + "\n")
        for m in members:
            display_name = m.get('phone') if (m.get('phone') and not m.get('nickname')) else m.get('nickname', '')
            f.write(f"{m['id']:<6} {display_name:<22} {str(m.get('age', 30)) + '세':<12} {m.get('registered_at', '-'):<22} {str(m.get('login_count', 1)) + '회':<8}\n")
        f.write("=" * 74 + "\n")

@router.post("/login", summary="휴대폰 번호/별명 + 비밀번호 간편 로그인")
def login_user(payload: UserLoginPayload):
    nickname = payload.nickname.strip()
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="휴대폰 번호 또는 별명(아이디)을 입력해주세요.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")

    members = _load_members()
    existing = _find_member(members, nickname)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 계정이 없을 경우 즉시 간편 자동 가입 & 로그인 처리 (0초 접속)
    if not existing:
        new_id = (max([m["id"] for m in members], default=0)) + 1
        clean_phone = _clean_phone_digits(nickname)
        is_phone = len(clean_phone) >= 10

        target_user = {
            "id": new_id,
            "nickname": nickname,
            "phone": clean_phone if is_phone else "",
            "age": 30,
            "password_hash": _hash_password(password),
            "registered_at": now_str,
            "login_count": 1,
            "last_login_at": now_str
        }
        members.insert(0, target_user)
        _save_members(members)
        logger.info(f"[Member Auto-Registered on Login] ID/Phone: {nickname}")

        user_info = {
            "id": new_id,
            "nickname": nickname,
            "age": 30,
            "registered_at": now_str,
            "login_count": 1,
            "last_login_at": now_str
        }
        return {
            "status": "success",
            "message": f"'{nickname}'님 계정이 등록되어 로그인되었습니다!",
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
    
    clean_digits = _clean_phone_digits(nickname)
    if len(clean_digits) >= 10 and not existing.get("phone"):
        existing["phone"] = clean_digits

    _save_members(members)

    user_info = {
        "id": existing["id"],
        "nickname": existing["nickname"],
        "age": existing.get("age", 30),
        "registered_at": existing.get("registered_at", now_str),
        "login_count": existing["login_count"],
        "last_login_at": existing["last_login_at"]
    }
    logger.info(f"[Member Login Success] Nickname: {existing['nickname']}")
    return {
        "status": "success",
        "message": f"'{existing['nickname']}'님 환영합니다!",
        "user": user_info
    }

@router.post("/register-user", summary="휴대폰 번호/별명 + 나이 + 비밀번호 신규 회원가입")
def register_user(payload: UserRegisterPayload):
    nickname = payload.nickname.strip()
    age = payload.age if (payload.age and payload.age > 0) else 30
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="휴대폰 번호 또는 별명(아이디)을 입력해주세요.")
    if len(nickname) > 30:
        raise HTTPException(status_code=400, detail="입력값은 최대 30자까지 가능합니다.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 4자리 이상이어야 합니다.")

    members = _load_members()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing = _find_member(members, nickname)
    if existing:
        existing["password_hash"] = _hash_password(password)
        existing["last_login_at"] = now_str
        existing["login_count"] = existing.get("login_count", 1) + 1
        _save_members(members)
        user_info = {
            "id": existing["id"],
            "nickname": existing["nickname"],
            "age": existing.get("age", age),
            "registered_at": existing.get("registered_at", now_str),
            "login_count": existing["login_count"],
            "last_login_at": existing["last_login_at"]
        }
        return {
            "status": "success",
            "message": f"'{existing['nickname']}'님 기존 등록 계정으로 즉시 로그인되었습니다.",
            "user": user_info,
            "total_members": len(members),
            "folder": "data/members"
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
        "last_login_at": now_str
    }
    members.insert(0, target_user)

    _save_members(members)
    logger.info(f"[Member Registered] Nickname/Phone: {nickname}, Total: {len(members)}")

    user_info = {
        "id": new_id,
        "nickname": nickname,
        "age": age,
        "registered_at": now_str,
        "login_count": 1,
        "last_login_at": now_str
    }

    return {
        "status": "success",
        "message": f"'{nickname}'님 회원가입이 완료되었습니다!",
        "user": user_info,
        "total_members": len(members),
        "folder": "data/members"
    }

@router.get("/members", summary="가입한 회원 목록 및 총 인원수 조회 (비밀번호 제외 보안 처리)")
def get_members():
    members = _load_members()
    safe_members = []
    for m in members:
        safe_m = {k: v for k, v in m.items() if k != "password_hash"}
        safe_members.append(safe_m)
    return {
        "status": "success",
        "total_members": len(safe_members),
        "folder_path": MEMBERS_DIR,
        "summary_file": "data/members/member_summary.txt",
        "members": safe_members
    }
