# -*- coding: utf-8 -*-
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.services.match_service import MatchService
from app.services.folder_export_service import FolderExportService

logger = logging.getLogger("baseball_scheduler")
logger.setLevel(logging.INFO)

class SchedulerService:
    _scheduler: Optional[AsyncIOScheduler] = None
    _job_id = "daily_baseball_sync_job"
    _config = {
        "hour": 0,
        "minute": 0,
        "enabled": True,
        "leagues": ["KBO", "NPB", "MLB", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1", "NBA"]
    }
    _last_run_info: Dict[str, Any] = {
        "last_run_time": None,
        "status": "IDLE",
        "message": "스케줄러 대기 중",
        "details": {}
    }
    _is_running_task: bool = False

    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        if cls._scheduler is None:
            cls._scheduler = AsyncIOScheduler()
        return cls._scheduler

    @classmethod
    def start_scheduler(cls):
        scheduler = cls.get_scheduler()
        if not scheduler.running:
            trigger = CronTrigger(hour=cls._config["hour"], minute=cls._config["minute"])
            scheduler.add_job(
                cls.execute_daily_sync_job,
                trigger=trigger,
                id=cls._job_id,
                replace_existing=True
            )
            scheduler.start()
            logger.info(f"[Scheduler] 매일 {cls._config['hour']:02d}:{cls._config['minute']:02d} 자동 동기화 스케줄러 시작 완료.")

    @classmethod
    def shutdown_scheduler(cls):
        if cls._scheduler and cls._scheduler.running:
            cls._scheduler.shutdown(wait=False)
            logger.info("[Scheduler] 스케줄러 종료 완료.")

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        scheduler = cls.get_scheduler()
        job = scheduler.get_job(cls._job_id) if scheduler else None
        next_run = job.next_run_time.isoformat() if (job and job.next_run_time) else None

        return {
            "scheduler_running": scheduler.running if scheduler else False,
            "is_syncing_now": cls._is_running_task,
            "config": cls._config,
            "next_run_time": next_run,
            "last_run": cls._last_run_info
        }

    @classmethod
    def update_config(cls, hour: int, minute: int, enabled: bool = True):
        cls._config["hour"] = hour
        cls._config["minute"] = minute
        cls._config["enabled"] = enabled

        scheduler = cls.get_scheduler()
        if scheduler and scheduler.running:
            if enabled:
                trigger = CronTrigger(hour=hour, minute=minute)
                scheduler.reschedule_job(cls._job_id, trigger=trigger)
                logger.info(f"[Scheduler] 스케줄 시각 변경 -> 매일 {hour:02d}:{minute:02d}")
            else:
                job = scheduler.get_job(cls._job_id)
                if job:
                    scheduler.pause_job(cls._job_id)
                logger.info("[Scheduler] 일일 스케줄러 일시정지됨")
        return cls.get_status()

    @classmethod
    async def trigger_now(cls) -> Dict[str, Any]:
        if cls._is_running_task:
            return {"status": "ALREADY_RUNNING", "message": "현재 동기화 작업이 진행 중입니다."}
        
        asyncio.create_task(cls.execute_daily_sync_job())
        return {"status": "TRIGGERED", "message": "백그라운드 동기화 작업이 시작되었습니다."}

    @classmethod
    async def execute_daily_sync_job(cls):
        if cls._is_running_task:
            logger.warning("[Scheduler] 이미 실행 중인 작업이 있어 건너뜁니다.")
            return

        cls._is_running_task = True
        start_time = datetime.now()
        cls._last_run_info = {
            "last_run_time": start_time.isoformat(),
            "status": "RUNNING",
            "message": "경기 데이터 자동 수집 진행 중...",
            "details": {}
        }

        yesterday_str = (start_time - timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = start_time.strftime("%Y-%m-%d")

        db = SessionLocal()
        summary = {}

        try:
            logger.info(f"[Scheduler] 일일 동기화 시작: 대상 날짜={yesterday_str} ~ {today_str}")

            for league_id in cls._config.get("leagues", ["KBO", "NPB", "MLB"]):
                try:
                    sync_res = MatchService.sync_from_official_site(
                        db=db,
                        league_id=league_id,
                        start_date=yesterday_str,
                        end_date=today_str
                    )
                    
                    try:
                        FolderExportService.export_league_to_folder_structure(
                            db=db,
                            league_id=league_id,
                            start_date=yesterday_str,
                            end_date=today_str
                        )
                        folder_status = "SUCCESS"
                    except Exception as fe:
                        logger.error(f"[Scheduler] {league_id} 폴더 내보내기 오류: {fe}")
                        folder_status = f"ERROR: {str(fe)}"

                    summary[league_id] = {
                        "status": "SUCCESS",
                        "synced_matches": sync_res.get("synced_matches_count", 0),
                        "folder_export": folder_status
                    }
                except Exception as le:
                    logger.error(f"[Scheduler] {league_id} 수집 오류: {le}")
                    summary[league_id] = {
                        "status": "ERROR",
                        "error": str(le)
                    }

            end_time = datetime.now()
            duration_sec = round((end_time - start_time).total_seconds(), 1)
            cls._last_run_info = {
                "last_run_time": end_time.isoformat(),
                "duration_seconds": duration_sec,
                "status": "SUCCESS",
                "message": f"일일 자동 수집 완료 ({duration_sec}초 소요)",
                "details": summary
            }
            logger.info(f"[Scheduler] 일일 자동 수집 성공 완료 ({duration_sec}s): {summary}")

        except Exception as e:
            logger.error(f"[Scheduler] 치명적 오류 발생: {e}")
            cls._last_run_info = {
                "last_run_time": datetime.now().isoformat(),
                "status": "ERROR",
                "message": f"오류 발생: {str(e)}",
                "details": summary
            }
        finally:
            db.close()
            cls._is_running_task = False
