import os
import sys

# Windows 콘솔 인코딩 에러(cp949) 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import webbrowser
import threading
import time
import uvicorn

# 프로젝트 루트 경로 확보
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def open_browser():
    time.sleep(1.5)
    print("\n[안내] 웹 브라우저에서 관리자 대시보드가 열립니다: http://localhost:8000/")
    webbrowser.open("http://localhost:8000/")

if __name__ == "__main__":
    print("=" * 65)
    print("[야구 정밀 데이터 수집 & 앱 관리 센터 시작 (MLB · KBO · NPB)]")
    print(">> 야구 관리 대시보드: http://localhost:8000/")
    print(">> Swagger API 문서 : http://localhost:8000/docs")
    print("=" * 65)
    
    # 1.5초 후 브라우저 자동 실행
    threading.Thread(target=open_browser, daemon=True).start()
    
    # FastAPI 서버 구동
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)