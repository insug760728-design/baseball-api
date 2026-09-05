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

class UserRegisterPayload(BaseModel):
    nickname: str
    age: int

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
            f.write(f"{m['id']:<6} {m['nickname']:<18} {str(m['age']) + '세':<12} {m['registered_at']:<22} {str(m.get('login_count', 1)) + '회':<8}\n")
        f.write("=" * 70 + "\n")

@router.post("/register-user", summary="초간편 별명+나이 회원 가입 & data/members 폴더 실시간 자동 저장")
def register_user(payload: UserRegisterPayload):
    nickname = payload.nickname.strip()
    age = payload.age

    if not nickname:
        raise HTTPException(status_code=400, detail="별명을 입력해주세요.")
    if not age or age < 1 or age > 120:
        raise HTTPException(status_code=400, detail="올바른 나이를 입력해주세요.")

    members = _load_members()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    existing = next((m for m in members if m["nickname"].lower() == nickname.lower()), None)
    if existing:
        existing["age"] = age
        existing["login_count"] = existing.get("login_count", 1) + 1
        existing["last_login_at"] = now_str
        target_user = existing
    else:
        new_id = (max([m["id"] for m in members], default=0)) + 1
        target_user = {
            "id": new_id,
            "nickname": nickname,
            "age": age,
            "registered_at": now_str,
            "login_count": 1,
            "last_login_at": now_str
        }
        members.insert(0, target_user) # new users at top

    _save_members(members)
    logger.info(f"[Member Registered] Nickname: {nickname}, Age: {age}, Total: {len(members)}")

    return {
        "status": "success",
        "message": f"'{nickname}'님({age}세) 가입 완료 (총 회원수: {len(members)}명)",
        "user": target_user,
        "total_members": len(members),
        "folder": "data/members"
    }

@router.get("/members", summary="가입한 회원 목록 및 총 인원수 조회 (data/members 폴더 연동)")
def get_members():
    members = _load_members()
    return {
        "status": "success",
        "total_members": len(members),
        "folder_path": MEMBERS_DIR,
        "summary_file": "data/members/member_summary.txt",
        "members": members
    }
