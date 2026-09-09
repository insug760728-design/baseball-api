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
    age: int
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
        f.write(f"{'번호':<6} {'별명(닉네임)':<18} {'연령(나이)':<12} {'가입일시':<22} {'접속횟수':<8}\n")
        f.write("-" * 70 + "\n")
        for m in members:
            f.write(f"{m['id']:<6} {m['nickname']:<18} {str(m.get('age', 0)) + '세':<12} {m.get('registered_at', '-'):<22} {str(m.get('login_count', 1)) + '회':<8}\n")
        f.write("=" * 70 + "\n")

@router.post("/login", summary="별명+비밀번호 간편 로그인")
def login_user(payload: UserLoginPayload):
    nickname = payload.nickname.strip()
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="활동하실 별명(닉네임)을 입력해주세요.")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")

    members = _load_members()
    existing = next((m for m in members if m["nickname"].lower() == nickname.lower()), None)
    if not existing:
        raise HTTPException(status_code=404, detail=f"'{nickname}' 별명으로 등록된 계정이 없습니다. [신규 회원가입]을 먼저 진행해주세요.")

    hashed = _hash_password(password)
    # 기존에 비밀번호 없이 가입되었던 회원은 이번에 입력한 비밀번호로 최초 등록 및 연동
    if "password_hash" not in existing or not existing["password_hash"]:
        existing["password_hash"] = hashed
    elif existing["password_hash"] != hashed:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다. 다시 확인해주세요.")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing["login_count"] = existing.get("login_count", 1) + 1
    existing["last_login_at"] = now_str
    _save_members(members)

    user_info = {
        "id": existing["id"],
        "nickname": existing["nickname"],
        "age": existing.get("age", 25),
        "registered_at": existing.get("registered_at", now_str),
        "login_count": existing["login_count"],
        "last_login_at": existing["last_login_at"]
    }
    logger.info(f"[Member Login Success] Nickname: {nickname}")
    return {
        "status": "success",
        "message": f"'{existing['nickname']}'님 환영합니다!",
        "user": user_info
    }

@router.post("/register-user", summary="별명+나이+비밀번호 신규 회원가입 & data/members 폴더 실시간 자동 저장")
def register_user(payload: UserRegisterPayload):
    nickname = payload.nickname.strip()
    age = payload.age
    password = payload.password.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="활동하실 별명(닉네임)을 입력해주세요.")
    if len(nickname) > 12:
        raise HTTPException(status_code=400, detail="별명은 최대 12자까지 입력 가능합니다.")
    if not age or age < 1 or age > 120:
        raise HTTPException(status_code=400, detail="올바른 나이를 입력해주세요. (1~120)")
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력해주세요.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 4자리 이상이어야 합니다.")

    members = _load_members()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing = next((m for m in members if m["nickname"].lower() == nickname.lower()), None)
    if existing:
        raise HTTPException(status_code=400, detail=f"이미 등록된 별명('{nickname}')입니다. [간편 로그인] 탭에서 로그인해주세요.")

    new_id = (max([m["id"] for m in members], default=0)) + 1
    target_user = {
        "id": new_id,
        "nickname": nickname,
        "age": age,
        "password_hash": _hash_password(password),
        "registered_at": now_str,
        "login_count": 1,
        "last_login_at": now_str
    }
    members.insert(0, target_user)

    _save_members(members)
    logger.info(f"[Member Registered] Nickname: {nickname}, Age: {age}, Total: {len(members)}")

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
        "message": f"'{nickname}'님({age}세) 가입 완료 (총 회원수: {len(members)}명)",
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
