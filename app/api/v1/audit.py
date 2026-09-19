# -*- coding: utf-8 -*-
"""
Audit API Router
================
데이터 검증 전담 에이전트(DataAuditVerificationAgent)의 검증 요약 및 일괄 검수 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.models import Match
from app.agents.data_audit_verification_agent import DataAuditVerificationAgent

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/summary")
def get_audit_summary():
    """
    최신 데이터 검수 요약 통계 조회
    (PASS율, FAIL수, UNKNOWN수, 종목별 현황, 최근 자동 보정 내역)
    """
    summary = DataAuditVerificationAgent.get_latest_summary()
    if not summary.get("audited_at"):
        # 최초 요청 시 기본 감사 1회 실행하여 최신 통계 생성
        summary = DataAuditVerificationAgent.run_full_audit(auto_fix=False, limit=300)
    return {
        "status": "success",
        "data": summary
    }

@router.post("/run-all")
def run_full_data_audit(
    auto_fix: bool = Query(True, description="결함 발견 시 원천 API 대조 자동 보정 여부"),
    limit: int = Query(500, description="검수 대상 최대 경기 수")
):
    """
    전체 경기 1:1 정밀 검수 및 자동 보정 즉시 실행
    """
    summary = DataAuditVerificationAgent.run_full_audit(auto_fix=auto_fix, limit=limit)
    return {
        "status": "success",
        "message": f"전체 경기 1:1 대조 검수 완료 (패스율: {summary.get('pass_rate')}%, 보정: {summary.get('remediated_count')}건)",
        "data": summary
    }

@router.get("/match/{match_id}")
def audit_single_match(
    match_id: int,
    auto_fix: bool = Query(True, description="오류 시 자동 보정 여부"),
    db: Session = Depends(get_db)
):
    """
    특정 경기 1:1 정밀 검수 및 결과 반환
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    report = DataAuditVerificationAgent.audit_single_match(db, match, auto_fix=auto_fix)
    return {
        "status": "success",
        "data": report
    }
