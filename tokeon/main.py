# -*- coding: utf-8 -*-
"""
TOKEON Master Web Server Entrypoint (tokeon/main.py)
Clean, lightweight, zero-error architecture.
"""

import os
import sys

# Ensure root workspace directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1 import api_v1_router
from app.core.database import engine, Base

# Initialize DB tables if needed
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TOKEON Sports Live Analytics Portal",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount Static Files
static_dir = os.path.join(current_dir, "app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount Existing API Routers
app.include_router(api_v1_router, prefix="/api/v1")

# Web Portal Root Route
template_path = os.path.join(current_dir, "app", "templates", "index.html")

@app.get("/", response_class=HTMLResponse, summary="TOKEON 메인 포털")
def read_root(request: Request):
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return HTMLResponse("<h1>TOKEON Service Loading...</h1>", status_code=200)

@app.get("/health", summary="헬스 체크")
def health_check():
    return {"status": "ok", "service": "tokeon_v2", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tokeon.main:app", host="0.0.0.0", port=8080, reload=True)
