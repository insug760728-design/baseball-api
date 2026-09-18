import os
import sys
import json
import time
import threading

if sys.platform == "win32":
    import asyncio
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models import models
from app.api.v1 import api_v1_router
from app.services.match_service import MatchService
from app.services.scheduler_service import SchedulerService
from app.core.sports_catalog import SPORTS_CATALOG
from app.core.error_monitor import init_error_monitoring, capture_exception
from app.core.websocket_manager import manager as ws_manager
from app.core.cache import init_cache

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_error_monitoring()
    init_cache()
    try:
        import asyncio
        ws_manager.set_event_loop(asyncio.get_running_loop())
    except Exception:
        pass
    db = SessionLocal()
    try:
        match_count = db.query(models.Match).count()
        if match_count == 0:
            print("[INFO] 야구 공식 데이터베이스 초기화: MLB 공식 데이터를 수집합니다...")
            MatchService.sync_from_official_site(
                db=db,
                league_id="MLB",
                league_name="미국 메이저리그 (MLB)"
            )
            print("[INFO] 공식 MLB 데이터 초기 수집 완료.")
    finally:
        db.close()

    # 일일 자동 수집 백그라운드 스케줄러 시작
    try:
        SchedulerService.start_scheduler()
    except Exception as e:
        print(f"[WARN] 스케줄러 시작 중 오류: {e}")

    # 서버 시작 즉시 전종목(UCL/UEL 포함) 동기화 — Render 슬립 재시작 후에도 최신 데이터 보장
    try:
        import asyncio
        asyncio.create_task(SchedulerService.execute_startup_sync())
        print("[INFO] 서버 시작 즉시 전종목 동기화 태스크 시작 (UCL/UEL 포함).")
    except Exception as e:
        print(f"[WARN] 시작 동기화 태스크 오류: {e}")

    # 4분 주기 AI 자동 채팅 봇 백그라운드 시작 (각자 다른 닉네임으로 실시간 소통)
    try:
        import asyncio
        from app.services.ai_chat_bot_service import start_ai_chat_bot_task
        asyncio.create_task(start_ai_chat_bot_task())
    except Exception as e:
        print(f"[WARN] AI 채팅 봇 시작 중 오류: {e}")

    # 🚀 백그라운드 사전 워밍업 (TeamSplitService 41,000건 적재 및 주요 경기 1:1 분석)
    try:
        def _warmup_background():
            # 1. TeamSplitService 사전 워밍업 (메모리 선적재로 통계 조회 0초화)
            try:
                import time
                from app.services.team_split_service import TeamSplitService
                t0 = time.time()
                TeamSplitService.get_all_splits()
                print(f"[INFO] TeamSplitService 분할 통계 사전 워밍업 완료 ({time.time() - t0:.2f}s).")
                refresh_server_matches_cache()
                print("[INFO] Server Matches Cache 초기 선적재 완료.")
            except Exception as e:
                print(f"[WARN] TeamSplitService 워밍업 중 오류: {e}")

            # 2. 오늘 주요 경기 1:1 세이버 정밀 분석 사전 워밍업
            try:
                from app.core.database import SessionLocal
                from app.services.match_service import MatchService
                from app.services.team_split_service import TeamSplitService
                from app.api.v1.matches import _MATCH_FULL_CACHE
                import time
                db = SessionLocal()
                try:
                    matches = MatchService.get_matches(db, limit=5, order="asc")
                    now = time.time()
                    for m in matches:
                        if m.id not in _MATCH_FULL_CACHE:
                            data = MatchService.get_match_full_detail(db, m.id)
                            if data:
                                details_ts = data["details"].get("team_stats") if (data.get("details") and isinstance(data["details"], dict)) else {}
                                matchup_analysis = TeamSplitService.get_matchup_analysis(m.home_team_name, m.away_team_name, m.sport_code, match_id=m.id, team_stats=details_ts)
                                res = {
                                    "id": m.id,
                                    "official_id": m.official_id,
                                    "sport_code": m.sport_code,
                                    "league_name": m.league_name,
                                    "round_name": m.round_name,
                                    "match_date": m.match_date,
                                    "stadium": m.stadium,
                                    "home_team_name": m.home_team_name,
                                    "away_team_name": m.away_team_name,
                                    "home_score": m.home_score,
                                    "away_score": m.away_score,
                                    "home_starter_name": m.home_starter_name,
                                    "away_starter_name": m.away_starter_name,
                                    "status": m.status,
                                    "is_customized": m.is_customized,
                                    "custom_notes": m.custom_notes,
                                    "summary": m.custom_notes,
                                    "details": data["details"],
                                    "events": data["events"],
                                    "player_stats": data["player_stats"],
                                    "matchup_analysis": matchup_analysis
                                }
                                _MATCH_FULL_CACHE[m.id] = (now, res)
                    print(f"[INFO] 오늘 주요 경기 {len(_MATCH_FULL_CACHE)}건 1:1 세이버 분석 사전 워밍업 완료.")
                finally:
                    db.close()
            except Exception as ex:
                print(f"[WARN] 경기 분석 사전 워밍업 중 오류: {ex}")

        import threading
        threading.Thread(target=_warmup_background, daemon=True).start()
        print("[INFO] 백그라운드 사전 워밍업 스레드 시작 완료 (서버 즉시 서빙 가능).")
    except Exception as e:
        print(f"[WARN] 백그라운드 사전 워밍업 스레드 시작 오류: {e}")

    # 🔄 1분 주기 경기 상태 자가 치유(Self-Healing) 데몬
    async def _match_lifecycle_daemon():
        while True:
            try:
                await asyncio.sleep(60)
                from app.core.database import SessionLocal
                from app.services.match_service import MatchService
                db = SessionLocal()
                try:
                    MatchService.cleanup_stale_live_matches(db)
                finally:
                    db.close()
            except Exception as e:
                pass

    try:
        import asyncio
        asyncio.create_task(_match_lifecycle_daemon())
        print("[INFO] 매치 상태 자가 치유 데몬 (1분 주기) 가동 시작.")
    except Exception as e:
        print(f"[WARN] 자가 치유 데몬 시작 오류: {e}")

    yield

    # 서버 종료 시 스케줄러 정리
    try:
        SchedulerService.shutdown_scheduler()
    except Exception as e:
        print(f"[WARN] 스케줄러 종료 중 오류: {e}")

app = FastAPI(
    title="⚾ 야구 정밀 분석 & 데이터 관리 센터",
    description="MLB / KBO / NPB 야구 전문 경기결과, 전광판 스코어, 타자/투수 세부 분석 및 앱 전송 관리 API",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_cache_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=604800"
    return response

from fastapi.staticfiles import StaticFiles

landing_path = os.path.join(current_dir, "templates", "landing.html")
b2b_portal_path = os.path.join(current_dir, "templates", "b2b_api_portal.html")
dashboard_path = os.path.join(current_dir, "templates", "index.html")
live_center_path = os.path.join(current_dir, "templates", "live_center.html")
mobile_path = os.path.join(current_dir, "templates", "mobile.html")
mlb_dashboard_path = os.path.join(current_dir, "templates", "mlb_dashboard.html")

static_dir = os.path.join(current_dir, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

_PORTAL_HTML_CACHE = {}
_SERVER_MATCHES_CACHE = {"json_str": "[]", "updated_at": 0.0, "is_refreshing": False}

def refresh_server_matches_cache() -> str:
    global _SERVER_MATCHES_CACHE
    if _SERVER_MATCHES_CACHE.get("is_refreshing"):
        return _SERVER_MATCHES_CACHE.get("json_str", "[]")
    _SERVER_MATCHES_CACHE["is_refreshing"] = True
    db = None
    try:
        from app.schemas.schemas import MatchResponse
        db = SessionLocal()
        matches = MatchService.get_matches(db, limit=120, order='asc')
        serialized = [MatchResponse.model_validate(m).model_dump(mode="json") for m in matches]
        json_str = json.dumps(serialized, ensure_ascii=False)
        _SERVER_MATCHES_CACHE["json_str"] = json_str
        _SERVER_MATCHES_CACHE["updated_at"] = time.time()
        return json_str
    except Exception as e:
        print(f"[WARN] Failed to refresh server matches cache: {e}")
        return _SERVER_MATCHES_CACHE.get("json_str", "[]")
    finally:
        _SERVER_MATCHES_CACHE["is_refreshing"] = False
        if db is not None:
            try:
                db.close()
            except Exception:
                pass

def get_server_initial_matches_json() -> str:
    global _SERVER_MATCHES_CACHE
    now = time.time()
    if _SERVER_MATCHES_CACHE["json_str"] != "[]":
        # If cache is older than 20 seconds, trigger async background refresh without blocking current request
        if (now - _SERVER_MATCHES_CACHE["updated_at"] > 20.0) and not _SERVER_MATCHES_CACHE.get("is_refreshing"):
            import threading
            threading.Thread(target=refresh_server_matches_cache, daemon=True).start()
        return _SERVER_MATCHES_CACHE["json_str"]
    
    return refresh_server_matches_cache()

def get_portal_html(target_path: str):
    if not os.path.exists(target_path):
        return "", ""
    
    mtime = os.path.getmtime(target_path)
    if target_path not in _PORTAL_HTML_CACHE or _PORTAL_HTML_CACHE[target_path].get("mtime") != mtime:
        with open(target_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        _PORTAL_HTML_CACHE[target_path] = {"raw_content": raw_content, "mtime": mtime}
    else:
        raw_content = _PORTAL_HTML_CACHE[target_path]["raw_content"]

    # Pre-inject SERVER_INITIAL_MATCHES into <head> for zero-latency initial screen
    initial_matches_json = get_server_initial_matches_json()
    injection_script = f"<script id=\"serverInitialData\">window.SERVER_INITIAL_MATCHES = {initial_matches_json};</script>"
    if "</head>" in raw_content:
        content = raw_content.replace("</head>", f"{injection_script}\n</head>", 1)
    elif "<body" in raw_content:
        content = raw_content.replace("<body", f"{injection_script}\n<body", 1)
    else:
        content = f"{injection_script}\n{raw_content}"

    import hashlib
    etag = f'"{hashlib.md5(content.encode("utf-8")).hexdigest()}"'
    return content, etag

def is_b2b_domain(request: Request) -> bool:
    # 1. 쿼리 파라미터 확인 (?domain=tokeon.kr 또는 ?domain=b2b)
    domain_param = request.query_params.get("domain", "").lower()
    if "tokeon.kr" in domain_param and "co.kr" not in domain_param:
        return True
    if domain_param in ("b2b", "api"):
        return True
    
    # 2. Host 헤더 확인 (tokeon.kr vs tokeon.co.kr)
    host = request.headers.get("host", "").lower()
    if "tokeon.kr" in host and "co.kr" not in host:
        return True
    if host.startswith("api."):
        return True
        
import time
from fastapi import Response

@app.get("/health", summary="Health Check & Keep-Alive")
@app.get("/healthz", summary="Health Check & Keep-Alive")
@app.get("/api/v1/health", summary="Health Check & Keep-Alive")
def health_check():
    from datetime import datetime, timedelta
    now_kst = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "service": "Sports-API", "kst_time": now_kst, "timestamp": time.time()},
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/m", response_class=HTMLResponse, summary="TOKEON 스포츠 모바일 전용 앱 화면")
@app.get("/mobile", response_class=HTMLResponse, summary="TOKEON 스포츠 모바일 전용 앱 화면")
@app.get("/app", response_class=HTMLResponse, summary="TOKEON 스포츠 모바일 전용 앱 화면")
def mobile_portal(request: Request):
    try:
        target = mobile_path if os.path.exists(mobile_path) else landing_path
        content, etag = get_portal_html(target)
        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>모바일 화면 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/", response_class=HTMLResponse, summary="TOKEON 스포츠 분석 전문 포털 (tokeon.co.kr)")
def domain_portal(request: Request):
    try:
        # 모바일 강제 뷰 요청 (?view=mobile) 확인
        if request.query_params.get("view") == "mobile":
            target = mobile_path if os.path.exists(mobile_path) else landing_path
        else:
            # 경기목록 메인 포털 (landing.html) 기본 표출
            target = landing_path if os.path.exists(landing_path) else dashboard_path

        content, etag = get_portal_html(target)
        return HTMLResponse(
            content=content, 
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>포털 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/mlb", response_class=HTMLResponse, summary="2026 공식 MLB 전경기 전광판 및 선발 방어율 대시보드")
@app.get("/mlb-dashboard", response_class=HTMLResponse, summary="2026 공식 MLB 전경기 전광판 및 선발 방어율 대시보드")
@app.get("/history/mlb", response_class=HTMLResponse, summary="2026 공식 MLB 전경기 전광판")
def mlb_scoreboard_portal(request: Request):
    try:
        target = mlb_dashboard_path if os.path.exists(mlb_dashboard_path) else landing_path
        content, etag = get_portal_html(target)
        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>MLB 대시보드 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/b2b", response_class=HTMLResponse, summary="TOKEON DATA — B2B 스포츠 데이터 API 전문 포털 (tokeon.kr)")
@app.get("/api-company", response_class=HTMLResponse)
@app.get("/developer", response_class=HTMLResponse)
def b2b_portal():
    try:
        target = b2b_portal_path if os.path.exists(b2b_portal_path) else landing_path
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    except Exception as e:
        return HTMLResponse(content=f"<h1>B2B 포털 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/analytics", response_class=HTMLResponse, summary="TOKEON ANALYTICS — 스포츠 정밀 분석 웹 포털 (tokeon.co.kr)")
@app.get("/portal", response_class=HTMLResponse)
def analytics_portal(request: Request):
    try:
        content, etag = get_portal_html(landing_path)
        client_etag = request.headers.get("if-none-match")
        if client_etag and client_etag == etag:
            return Response(status_code=304, headers={"ETag": etag, "Cache-Control": "no-cache, no-store, must-revalidate"})
        return HTMLResponse(content=content, headers={"ETag": etag, "Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    except Exception as e:
        return HTMLResponse(content=f"<h1>분석 포털 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse, summary="스포츠 전문 관리 대시보드")
def admin_dashboard(request: Request):
    try:
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    except Exception as e:
        return HTMLResponse(content=f"<h1>대시보드 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/live", response_class=HTMLResponse, summary="PC/모바일 실시간 라이브 전광판 중계센터 (4/6/8/12 멀티뷰)")
@app.get("/live-center", response_class=HTMLResponse)
def live_center_portal(request: Request):
    try:
        target = live_center_path if os.path.exists(live_center_path) else landing_path
        content, etag = get_portal_html(target)
        client_etag = request.headers.get("if-none-match")
        if client_etag and client_etag == etag:
            return Response(status_code=304, headers={"ETag": etag, "Cache-Control": "no-cache, no-store, must-revalidate"})
        return HTMLResponse(content=content, headers={"ETag": etag, "Cache-Control": "no-cache, no-store, must-revalidate"})
    except Exception as e:
        return HTMLResponse(content=f"<h1>라이브 센터 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/mlb", response_class=HTMLResponse, summary="2026-09-17 공식 MLB 전경기 전광판 및 선발 방어율 조회 (가로 스크롤 0%)")
@app.get("/mlb-dashboard", response_class=HTMLResponse)
@app.get("/20260917", response_class=HTMLResponse)
def mlb_official_dashboard(request: Request):
    try:
        content, etag = get_portal_html(mlb_dashboard_path)
        return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    except Exception as e:
        return HTMLResponse(content=f"<h1>MLB 대시보드 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

def generate_timeline_widget_html(match_data: dict, events: list) -> str:
    ev_html = ""
    if not events:
        ev_html = '<div style="padding: 24px; text-align: center; color: #64748b;">기록된 주요 상황 및 타점/홈런 이벤트가 없습니다.</div>'
    else:
        for ev in events:
            is_hr = ev.get("event_type") == "HOMERUN"
            icon = "💥 홈런" if is_hr else "⚾ 적시타/타점"
            badge_bg = "#ef4444" if is_hr else "#2563eb"
            ev_html += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid #f1f5f9;">
                <div>
                    <span style="display: inline-block; background: #0f172a; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; margin-right: 8px;">{ev.get('time_display', '')}</span>
                    <span style="display: inline-block; background: {badge_bg}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; margin-right: 8px;">{icon}</span>
                    <strong style="color: #0f172a; margin-right: 6px;">[{ev.get('team_name', '')}] {ev.get('player_name', '')}</strong>
                    <span style="color: #475569; font-size: 13px;">{ev.get('description', '')}</span>
                </div>
                <div style="font-weight: 800; font-size: 14px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 6px; color: #0f172a; white-space: nowrap; margin-left: 12px;">
                    {ev.get('score_after', '')}
                </div>
            </div>
            """
    
    st_badge = "#10b981" if match_data.get("status") == "LIVE" else "#64748b"
    st_text = "LIVE 진행중" if match_data.get("status") == "LIVE" else ("종료 FINISHED" if match_data.get("status") == "FINISHED" else "예정")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MLB 실시간 타임라인 위젯</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: transparent; padding: 6px; }}
    .timeline-card {{ background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.06); overflow: hidden; }}
    .timeline-header {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; }}
    .timeline-body {{ max-height: 420px; overflow-y: auto; }}
  </style>
</head>
<body>
  <div class="timeline-card">
    <div class="timeline-header">
      <div>
        <span style="background: {st_badge}; color: white; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px;">{st_text}</span>
        <strong style="margin-left: 8px; font-size: 15px;">[홈] {match_data.get('home_team_name', '')} vs [원정] {match_data.get('away_team_name', '')}</strong>
        <span style="font-size: 12px; opacity: 0.8; margin-left: 6px;">({match_data.get('match_date', '')})</span>
      </div>
      <div style="font-size: 18px; font-weight: 800; color: #fbbf24;">
        {match_data.get('home_score', 0)} : {match_data.get('away_score', 0)}
      </div>
    </div>
    <div class="timeline-body">
      {ev_html}
    </div>
  </div>
</body>
</html>"""

@app.get("/embed/timeline/latest", response_class=HTMLResponse, summary="최신 경기 타임라인 임베드 위젯 (iFrame용)")
@app.get("/embed/timeline", response_class=HTMLResponse, summary="최신 경기 타임라인 임베드 위젯 (iFrame용)")
def embed_latest_timeline():
    db = SessionLocal()
    try:
        matches = MatchService.get_matches(db)
        finished = [m for m in matches if m.status == "FINISHED"]
        target = finished[0] if finished else (matches[0] if matches else None)
        if not target:
            return HTMLResponse("<h3>등록된 경기 데이터가 없습니다.</h3>", status_code=404)
        detail = MatchService.get_match_full_detail(db, target.id)
        m_dict = {
            "away_team_name": target.away_team_name,
            "home_team_name": target.home_team_name,
            "away_score": target.away_score,
            "home_score": target.home_score,
            "status": target.status,
            "match_date": target.match_date
        }
        html = generate_timeline_widget_html(m_dict, detail.get("events", []))
        return HTMLResponse(content=html)
    finally:
        db.close()

@app.get("/embed/timeline/{match_id}", response_class=HTMLResponse, summary="특정 경기 타임라인 임베드 위젯 (iFrame용)")
def embed_timeline_by_id(match_id: int):
    db = SessionLocal()
    try:
        detail = MatchService.get_match_full_detail(db, match_id)
        if not detail:
            return HTMLResponse("<h3>경기를 찾을 수 없습니다.</h3>", status_code=404)
        m = detail["match"]
        m_dict = {
            "away_team_name": m.away_team_name,
            "home_team_name": m.home_team_name,
            "away_score": m.away_score,
            "home_score": m.home_score,
            "status": m.status,
            "match_date": m.match_date
        }
        html = generate_timeline_widget_html(m_dict, detail.get("events", []))
        return HTMLResponse(content=html)
    finally:
        db.close()

import secrets

@app.post("/api/v1/auth/trial-key", summary="무료 Sandbox API Key 즉시 발급 (tokeon.kr B2B 개발자용)")
def generate_trial_api_key(request: Request):
    key = f"tk_live_free_{secrets.token_hex(6)}"
    return {
        "status": "success",
        "api_key": key,
        "tier": "Developer Free (Sandbox)",
        "rate_limit": "1,000 requests / day",
        "active": True,
        "message": "API 키가 성공적으로 발급되었습니다. X-API-Key 헤더에 포함하여 호출하세요."
    }

# ============================================================
# 📅 [일정 관리 전담 에이전트 (ScheduleManagerAgent) API]
# ============================================================
@app.get("/api/schedule/status", summary="일정 관리 에이전트 가동 상태 및 향후 일정 현황 조회")
@app.get("/api/v1/schedule/status")
def get_schedule_agent_status():
    from app.agents.schedule_manager_agent import ScheduleManagerAgent
    status = ScheduleManagerAgent.get_schedule_status()
    return JSONResponse(status_code=200, content=status)

@app.post("/api/schedule/sync", summary="전종목 공식 향후 일정 즉시 동기화 실행 (ScheduleManagerAgent)")
@app.post("/api/v1/schedule/sync")
def sync_schedule_agent(days: int = 14):
    from app.agents.schedule_manager_agent import ScheduleManagerAgent
    res = ScheduleManagerAgent.sync_all_upcoming_schedules(days_ahead=days)
    return JSONResponse(status_code=200, content=res)

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    if not request.url.path.startswith("/api/"):
        try:
            target = b2b_portal_path if is_b2b_domain(request) else landing_path
            content, _ = get_portal_html(target)
            return HTMLResponse(content=content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
        except Exception:
            pass
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    capture_exception(exc, path=request.url.path)
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": "서버 내부 처리 중 오류가 발생했습니다. 시스템에 자동 보고되었습니다.",
                "error_type": exc.__class__.__name__,
                "path": request.url.path
            }
        )
    return HTMLResponse(
        content="""
        <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; text-align: center; padding: 60px 20px;">
            <h2 style="color: #ef4444; font-size: 24px;">500 - 서비스 일시 오류</h2>
            <p style="color: #64748b; margin-top: 8px;">요청 처리 중 오류가 발생했습니다. 시스템 관리자에게 자동 보고되었습니다.</p>
            <a href="/" style="display: inline-block; margin-top: 16px; padding: 10px 20px; background: #2563eb; color: #fff; border-radius: 6px; text-decoration: none; font-weight: bold;">홈으로 돌아가기</a>
        </div>
        """,
        status_code=500
    )

from app.api.v1.community import router as community_router

app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(community_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
