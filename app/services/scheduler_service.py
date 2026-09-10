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

def get_now_kst() -> datetime:
    """Return current Korean Standard Time (KST, UTC+9) regardless of server host timezone."""
    return datetime.utcnow() + timedelta(hours=9)

class SchedulerService:
    _scheduler: Optional[AsyncIOScheduler] = None
    _job_id = "daily_baseball_sync_job"
    _config = {
        "hour": 0,
        "minute": 0,
        "enabled": True,
        "leagues": ["KBO", "NPB", "MLB", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1", "MLS", "UCL", "UEL", "CHAMPIONSHIP", "ENGLAND_CUP", "EREDIVISIE", "LIBERTADORES", "JLEAGUE", "NBA", "KBL"]
    }
    _last_run_info: Dict[str, Any] = {
        "last_run_time": None,
        "status": "IDLE",
        "message": "스케줄러 대기 중",
        "details": {}
    }
    _is_running_task: bool = False
    _live_loop_task: Optional[asyncio.Task] = None

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
            # 1시간마다 향후 3일간 경기 및 스코어 자동 동기화 (매시 0분 실행)
            hourly_trigger = CronTrigger(minute=0)
            scheduler.add_job(
                cls.execute_hourly_sync_job,
                trigger=hourly_trigger,
                id="hourly_sports_sync_job",
                replace_existing=True
            )
            # 10분마다 베트맨(Betman) 공식 발매금액·투표율·이월금 자동 최신화 (매 10분마다 실행)
            # 10분마다 베트맨(Betman) 공식 발매금액·투표율·이월금 자동 최신화 (매 10분마다 실행)
            betman_trigger = CronTrigger(minute="*/10")
            scheduler.add_job(
                cls.execute_betman_10min_sync_job,
                trigger=betman_trigger,
                id="betman_10min_sync_job",
                replace_existing=True
            )
            # 10분마다 KBO 및 NPB 공식 선발투수 발표 실시간 동기화 (기존 15분 -> 10분)
            starters_trigger = CronTrigger(minute="*/10")
            scheduler.add_job(
                cls.execute_starters_sync_job,
                trigger=starters_trigger,
                id="starters_10min_sync_job",
                replace_existing=True
            )
            # 1분마다 바탕화면 실시간 접속자 및 시간대별 트래픽 파일 자동 갱신
            traffic_trigger = CronTrigger(minute="*")
            scheduler.add_job(
                cls.execute_traffic_export_job,
                trigger=traffic_trigger,
                id="traffic_desktop_export_job",
                replace_existing=True
            )
            # 2분마다 정기 유료 라이브 검증 백업
            live_api_trigger = CronTrigger(minute="*/2")
            scheduler.add_job(
                cls.execute_live_api_sports_job,
                trigger=live_api_trigger,
                id="live_api_sports_job",
                replace_existing=True
            )
            # 3분마다 KBO 및 NPB 공식 라이브 스코어보드 고속 동기화 (경기 시간대 13~23시)
            kbo_live_trigger = CronTrigger(minute="*/3")
            scheduler.add_job(
                cls.execute_kbo_npb_live_sync_job,
                trigger=kbo_live_trigger,
                id="kbo_npb_live_sync_job",
                replace_existing=True
            )
            scheduler.start()

            # ⚡ 5초 동적 초고속 실시간 수집 루프 백그라운드 태스크 기동
            if cls._live_loop_task is None or cls._live_loop_task.done():
                cls._live_loop_task = asyncio.create_task(cls._run_live_5sec_dynamic_loop())

            logger.info(f"[Scheduler] 매일 {cls._config['hour']:02d}:{cls._config['minute']:02d}, 1시간 전종목 동기화, 10분 주기 베트맨/선발투수, 1분 트래픽, 5초 동적 LIVE 초고속 수집 루프 시작 완료.")


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
    async def execute_startup_sync(cls):
        """서버 시작 직후 어제~오늘+1일 전 종목(UCL/UEL 포함) 즉시 동기화.
        Render 슬립 후 재시작 시에도 최신 경기 데이터가 바로 반영되도록 보장."""
        await asyncio.sleep(5)  # lifespan 초기화 완료 대기
        if cls._is_running_task:
            logger.info("[Startup Sync] 다른 작업 진행 중 - 시작 동기화 건너뜀")
            return

        cls._is_running_task = True
        start_time = get_now_kst()
        logger.info(f"[Startup Sync] 서버 시작 즉시 전종목 동기화 시작 (KST): {start_time.isoformat()}")

        yesterday_str = (start_time - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_str = (start_time + timedelta(days=1)).strftime("%Y-%m-%d")

        # UCL/UEL 경기는 한국 기준 새벽(01:45~04:00)이므로 어제 UTC = 오늘 KST 새벽
        sync_leagues = ["KBO", "NPB", "MLB", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A",
                        "LIGUE_1", "MLS", "UCL", "UEL", "CHAMPIONSHIP", "EREDIVISIE",
                        "LIBERTADORES", "JLEAGUE", "NBA", "KBL"]

        db = SessionLocal()
        summary = {}
        try:
            for lid in sync_leagues:
                try:
                    res = await asyncio.to_thread(
                        MatchService.sync_from_official_site,
                        db=db,
                        league_id=lid,
                        start_date=yesterday_str,
                        end_date=tomorrow_str
                    )
                    summary[lid] = res.get("synced_matches_count", 0)
                except Exception as ex:
                    summary[lid] = f"ERR: {str(ex)[:60]}"

            logger.info(f"[Startup Sync] 서버 시작 즉시 동기화 완료: {summary}")
            try:
                from app.core.websocket_manager import manager
                await manager.broadcast({
                    "type": "STARTUP_SYNC_COMPLETE",
                    "timestamp": get_now_kst().isoformat(),
                    "summary": summary,
                    "message": "서버 시작 시 전종목(챔스·유로파 포함) 자동 동기화 완료"
                })
            except Exception:
                pass
        except Exception as e:
            logger.error(f"[Startup Sync] 서버 시작 동기화 오류: {e}")
        finally:
            db.close()
            cls._is_running_task = False

    @classmethod
    async def execute_daily_sync_job(cls):
        if cls._is_running_task:
            logger.warning("[Scheduler] 이미 실행 중인 작업이 있어 건너뜁니다.")
            return

        cls._is_running_task = True
        start_time = get_now_kst()
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
            logger.info(f"[Scheduler] 일일 동기화 시작 (KST): 대상 날짜={yesterday_str} ~ {today_str}")

            for league_id in cls._config.get("leagues", ["KBO", "NPB", "MLB"]):
                try:
                    sync_res = await asyncio.to_thread(
                        MatchService.sync_from_official_site,
                        db=db,
                        league_id=league_id,
                        start_date=yesterday_str,
                        end_date=today_str
                    )
                    
                    try:
                        await asyncio.to_thread(
                            FolderExportService.export_league_to_folder_structure,
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

            end_time = get_now_kst()
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
                "last_run_time": get_now_kst().isoformat(),
                "status": "ERROR",
                "message": f"오류 발생: {str(e)}",
                "details": summary
            }
        finally:
            db.close()
            cls._is_running_task = False

    @classmethod
    async def execute_hourly_sync_job(cls):
        """1시간마다 야구/축구/농구 최근 및 향후 3일간 경기 일정 및 스코어 자동 동기화"""
        if cls._is_running_task:
            logger.info("[Scheduler Hourly] 일일 작업 진행 중으로 1시간 수집 대기")
            return

        cls._is_running_task = True
        start_time = get_now_kst()
        logger.info(f"[Scheduler Hourly] 1시간 주기 전 종목 자동 동기화 시작 (KST): {start_time.isoformat()}")

        db = SessionLocal()
        summary = {}

        # 어제 ~ 오늘+3일 (유럽/미주 새벽 종료 경기 결과 및 스코어 누락 방지)
        yesterday_str = (start_time - timedelta(days=1)).strftime("%Y-%m-%d")
        d3_str = (start_time + timedelta(days=3)).strftime("%Y-%m-%d")

        try:
            active_leagues = cls._config.get("leagues", ["KBO", "NPB", "MLB", "EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1", "MLS", "UCL", "UEL", "CHAMPIONSHIP", "ENGLAND_CUP", "EREDIVISIE", "LIBERTADORES", "JLEAGUE", "NBA", "KBL"])
            for lid in active_leagues:
                try:
                    res = await asyncio.to_thread(
                        MatchService.sync_from_official_site,
                        db=db,
                        league_id=lid,
                        start_date=yesterday_str,
                        end_date=d3_str
                    )
                    summary[lid] = res.get("synced_matches_count", 0)
                except Exception as ex:
                    summary[lid] = f"ERR: {str(ex)}"

            logger.info(f"[Scheduler Hourly] 1시간 주기 동기화 완료: {summary}")

            # Auto-resolve past scheduled matches older than 8 hours safely
            try:
                from app.models.models import Match
                cutoff_8h = (start_time - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
                past_sched = db.query(Match).filter(Match.status == "SCHEDULED", Match.match_date < cutoff_8h).all()
                for pm in past_sched:
                    if (pm.home_score or 0) > 0 or (pm.away_score or 0) > 0:
                        pm.status = "FINISHED"
                    else:
                        pm.status = "POSTPONED"
                if past_sched:
                    db.commit()
                    logger.info(f"[Scheduler Hourly] 과거 8시간 경과 경기 {len(past_sched)}건 안전 상태 정리 완료")
            except Exception as pe:
                logger.warning(f"[Scheduler Hourly] 과거 경기 정리 중 경고: {pe}")
            try:
                from app.services.live_api_sports_service import LiveApiSportsService
                if LiveApiSportsService.is_configured():
                    fb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_football)
                    bb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_baseball)
                    summary["API_SPORTS_LIVE"] = {"football": fb_res, "baseball": bb_res}
            except Exception as ase:
                logger.error(f"[Scheduler] API-Sports live sync error: {ase}")

            try:
                from app.core.websocket_manager import manager
                await manager.broadcast({
                    "type": "HOURLY_SYNC_COMPLETE",
                    "timestamp": datetime.now().isoformat(),
                    "summary": summary,
                    "message": "1시간 주기 전 종목(5대리그·MLB·KBO·K리그·NPB·J리그·NBA) 자동 동기화 완료"
                })
            except Exception as be:
                logger.warning(f"[Scheduler] WebSocket 브로드캐스트 오류: {be}")
        except Exception as e:
            logger.error(f"[Scheduler Hourly] 1시간 주기 동기화 중 오류: {e}")
        finally:
            db.close()
            cls._is_running_task = False

    @classmethod
    async def execute_betman_10min_sync_job(cls):
        """10분 주기 베트맨(BETMAN) 축구 승무패, 야구 승1패, 프로토 전체 배당/투표율 실시간 자동 최신화"""
        try:
            from app.services.betman_service import BetmanService
            from app.core.websocket_manager import manager
            from app.core.database import SessionLocal

            # 1. 활성 토토 회차(승무패/승1패/승5패) 실시간 매출 및 투표율 동적 최신화
            summary = await asyncio.to_thread(BetmanService.get_live_toto_summary, force_refresh=True)
            for gid, g_info in summary.get('games', {}).items():
                g_ts = g_info.get('gmTs')
                if g_ts:
                    try:
                        res = await asyncio.to_thread(BetmanService.get_round_data, gm_id=gid, gm_ts=g_ts, force_refresh=True)
                        logger.info(f"[Scheduler] 베트맨 10분 최신화: {g_info.get('title')} (총매출: {res.get('total_sell_amount', 0):,}원, 1등누적: {res.get('first_prize_pool', 0):,}원)")
                    except Exception as ex_target:
                        logger.warning(f"[Scheduler] 베트맨 개별 회차({gid}) 동기화 경고: {ex_target}")

            # 2. 프로토 승부식 최신 배당 및 투표율을 DB 경기에 자동 동기화
            db = SessionLocal()
            try:
                proto_res = await asyncio.to_thread(BetmanService.sync_betman_proto_matches, db=db)
                logger.info(f"[Scheduler] 베트맨 프로토 배당 자동 동기화: {proto_res}")
            finally:
                db.close()

            try:
                await manager.broadcast({
                    "type": "BETMAN_10MIN_UPDATED",
                    "timestamp": datetime.now().isoformat(),
                    "summary": summary
                })
            except Exception:
                pass
        except Exception as e:
            logger.error(f"[Scheduler] 베트맨 10분 동기화 오류: {e}")

    @classmethod
    def execute_traffic_export_job(cls):
        """1분 주기 바탕화면 실시간 접속자 및 시간대별 트래픽 파일 자동 갱신"""
        try:
            from app.services.traffic_service import TrafficService
            from app.core.websocket_manager import manager
            live_count = 664 + len(manager.active_connections)
            TrafficService.update_and_export(current_active=live_count)
        except Exception as e:
            logger.error(f"[Scheduler] 바탕화면 트래픽 갱신 오류: {e}")

    @classmethod
    async def execute_live_api_sports_job(cls):
        """2분 주기 API-Sports 유료 실시간 축구 & 야구 동기화"""
        try:
            from app.services.live_api_sports_service import LiveApiSportsService
            if LiveApiSportsService.is_configured():
                fb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_football)
                bb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_baseball)
                tot_updated = (fb_res.get('updated_db_matches', 0) or 0) + (bb_res.get('updated_db_matches', 0) or 0)
                logger.info(f"[Scheduler LiveApi] 실시간 유료 API 동기화 완료: 축구 {fb_res.get('updated_db_matches', 0)}경기, 야구 {bb_res.get('updated_db_matches', 0)}경기 갱신 (총 {tot_updated}건)")
                if tot_updated > 0:
                    try:
                        from app.core.websocket_manager import manager
                        await manager.broadcast({
                            "type": "LIVE_SCORE_UPDATE",
                            "timestamp": datetime.now().isoformat(),
                            "updated_total": tot_updated,
                            "football": fb_res.get('updated_db_matches', 0),
                            "baseball": bb_res.get('updated_db_matches', 0)
                        })
                    except Exception as be:
                        logger.warning(f"[Scheduler LiveApi] WebSocket broadcast error: {be}")
        except Exception as e:
            logger.error(f"[Scheduler LiveApi] 실시간 유료 API 동기화 오류: {e}")

    @classmethod
    async def execute_kbo_npb_live_sync_job(cls):
        """3분 주기 KBO 및 NPB 야구 실시간 스코어보드 고속 동기화 (경기 집중 시간대 13:00~23:30)"""
        now = get_now_kst()
        # 한국시간 기준 경기 시간대 (13시 ~ 23시)
        if not (13 <= now.hour <= 23):
            return

        def _sync_domestic():
            from app.services.match_service import MatchService
            from app.core.database import SessionLocal
            from app.api.v1.matches import clear_matches_cache
            today_str = now.strftime("%Y-%m-%d")
            db = SessionLocal()
            updated_any = False
            try:
                for league in ["KBO", "NPB"]:
                    try:
                        res = MatchService.sync_from_official_site(
                            db=db,
                            league_id=league,
                            target_date=today_str
                        )
                        if res.get("synced_matches_count", 0) > 0:
                            updated_any = True
                    except Exception as le:
                        logger.warning(f"[Scheduler Domestic] {league} 수집 경고: {le}")
                if updated_any:
                    clear_matches_cache()
            finally:
                db.close()
            return updated_any

        try:
            updated = await asyncio.to_thread(_sync_domestic)
            if updated:
                from app.core.websocket_manager import manager
                await manager.broadcast({
                    "type": "LIVE_SCORE_UPDATE",
                    "timestamp": datetime.now().isoformat(),
                    "sport": "BASEBALL_DOMESTIC",
                    "message": "KBO/NPB 공식 실시간 스코어보드 갱신 완료"
                })
        except Exception as e:
            logger.warning(f"[Scheduler Domestic Live] 오류: {e}")

    @classmethod
    async def execute_starters_sync_job(cls):
        """15분 주기 KBO 및 NPB 공식 선발투수 발표 실시간 동기화"""
        def _run_starters():
            from app.core.database import SessionLocal
            from app.services.match_service import MatchService
            db = SessionLocal()
            try:
                res = MatchService.sync_announced_starters(db)
                logger.info(f"[Scheduler Starters] 선발투수 실시간 동기화 완료: KBO {res.get('kbo_synced')}건, NPB {res.get('npb_synced')}건")
            except Exception as e:
                logger.error(f"[Scheduler Starters] 선발투수 동기화 오류: {e}")
            finally:
                db.close()
        await asyncio.to_thread(_run_starters)

    @classmethod
    async def _run_live_5sec_dynamic_loop(cls):
        """⚡ 5초 실시간 동적 초고속 수집 루프
        - LIVE 경기가 진행 중이거나 시작 직전인 경우: 5초 주기로 고속 수집
        - 진행 중인 경기가 없는 경우: 10초 대기 후 상태 재확인 (외부 유료 API 호출 0회 절약)
        """
        logger.info("[Scheduler Live5Sec] 5초 동적 실시간 수집 루프 가동 시작")
        while True:
            try:
                now_kst = get_now_kst()
                start_window = (now_kst - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")
                end_window = (now_kst + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M")

                has_live_or_active = False
                db = SessionLocal()
                try:
                    from app.models.models import Match
                    from sqlalchemy import or_, and_
                    # 1. LIVE 상태인 경기 확인
                    live_count = db.query(Match).filter(Match.status == "LIVE").count()
                    if live_count > 0:
                        has_live_or_active = True
                    else:
                        # 2. 현재 시간대 전후로 진행 중일 가능성이 있는 SCHEDULED 경기 확인
                        active_sched = db.query(Match).filter(
                            Match.status == "SCHEDULED",
                            Match.match_date >= start_window,
                            Match.match_date <= end_window
                        ).count()
                        if active_sched > 0:
                            has_live_or_active = True
                finally:
                    db.close()

                if has_live_or_active:
                    from app.services.live_api_sports_service import LiveApiSportsService
                    if LiveApiSportsService.is_configured():
                        fb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_football)
                        bb_res = await asyncio.to_thread(LiveApiSportsService.sync_live_baseball)
                        tot = (fb_res.get('updated_db_matches', 0) or 0) + (bb_res.get('updated_db_matches', 0) or 0)
                        if tot > 0:
                            logger.info(f"[Scheduler Live5Sec] ⚡ 5초 실시간 갱신: 축구 {fb_res.get('updated_db_matches', 0)}건, 야구 {bb_res.get('updated_db_matches', 0)}건")
                    await asyncio.sleep(5)
                else:
                    # 진행 중인 경기 없음: 외부 API 호출 없이 10초 대기
                    await asyncio.sleep(10)
            except asyncio.CancelledError:
                logger.info("[Scheduler Live5Sec] 5초 루프 종료됨")
                break
            except Exception as e:
                logger.warning(f"[Scheduler Live5Sec] 루프 경고: {e}")
                await asyncio.sleep(5)




