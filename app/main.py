import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models import models
from app.api.v1 import api_v1_router
from app.services.match_service import MatchService
from app.services.scheduler_service import SchedulerService
from app.core.sports_catalog import SPORTS_CATALOG

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
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

landing_path = os.path.join(current_dir, "templates", "landing.html")
dashboard_path = os.path.join(current_dir, "templates", "index.html")

@app.get("/", response_class=HTMLResponse, summary="SPORTIX PRO — 스포츠 종합 포털 & 실시간 소식")
def domain_portal(request: Request):
    try:
        target = landing_path if os.path.exists(landing_path) else dashboard_path
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>포털 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse, summary="스포츠 전문 관리 대시보드")
def admin_dashboard(request: Request):
    try:
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>대시보드 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

@app.get("/portal", response_class=HTMLResponse, summary="스포츠 종합 포털 화면")
def portal_redirect(request: Request):
    return domain_portal(request)

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
        <strong style="margin-left: 8px; font-size: 15px;">{match_data.get('away_team_name', '')} vs {match_data.get('home_team_name', '')}</strong>
        <span style="font-size: 12px; opacity: 0.8; margin-left: 6px;">({match_data.get('match_date', '')})</span>
      </div>
      <div style="font-size: 18px; font-weight: 800; color: #fbbf24;">
        {match_data.get('away_score', 0)} : {match_data.get('home_score', 0)}
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

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    if not request.url.path.startswith("/api/"):
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except Exception:
            pass
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
