# -*- coding: utf-8 -*-
code = '''import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models import models
from app.api.v1 import api_v1_router
from app.services.match_service import MatchService
from app.core.sports_catalog import SPORTS_CATALOG

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        match_count = db.query(models.Match).count()
        if match_count == 0:
            print("[INFO] 야구 전문 데이터베이스 초기화: MLB, KBO, NPB 야구 공식 데이터를 수집합니다...")
            for cat_key, cat_val in SPORTS_CATALOG.items():
                for l in cat_val["leagues"]:
                    MatchService.sync_from_official_site(
                        db=db,
                        league_id=l["id"],
                        league_name=l["name"]
                    )
            print("[INFO] 야구 공식 데이터 초기 수집 완료.")
    finally:
        db.close()
    yield

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

html_path = os.path.join(current_dir, "templates", "index.html")

@app.get("/", response_class=HTMLResponse, summary="야구 전문 관리 대시보드")
def admin_dashboard(request: Request):
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>대시보드 로딩 오류</h1><p>{str(e)}</p>", status_code=500)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
'''

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(code)
print("app/main.py updated for baseball only!")