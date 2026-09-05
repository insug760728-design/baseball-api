# -*- coding: utf-8 -*-
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["자동 스케줄러"])

class SchedulerConfigUpdate(BaseModel):
    hour: int = Field(0, ge=0, le=23, description="실행 시각 (0~23시)")
    minute: int = Field(0, ge=0, le=59, description="실행 분 (0~59분)")
    enabled: bool = Field(True, description="스케줄러 활성화 여부")

@router.get("/status", summary="일일 자동 수집 스케줄러 상태 조회")
def get_status():
    """
    현재 스케줄러 가동 상태, 다음 실행 예정 시각, 마지막 실행 결과(시간, 소요시간, 상태) 반환
    """
    return SchedulerService.get_status()

@router.post("/run-now", summary="지금 즉시 전체 리그 자동 수집 1회 실행")
async def run_now():
    """
    대기 시간 없이 지금 즉시 KBO, NPB, MLB의 어제/오늘 경기 결과 및 세이버메트릭스 폴더 갱신 실행
    """
    res = await SchedulerService.trigger_now()
    return res

@router.post("/config", summary="스케줄러 실행 시각 및 활성화 설정 변경")
def update_config(payload: SchedulerConfigUpdate):
    """
    매일 실행될 시각(시, 분) 및 스케줄러 ON/OFF 변경
    """
    return SchedulerService.update_config(hour=payload.hour, minute=payload.minute, enabled=payload.enabled)
