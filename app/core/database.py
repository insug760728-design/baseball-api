import os
import time
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite 자가 복구 (손상된 DB 파일 감지 시 자동 초기화)
if 'sqlite' in settings.DATABASE_URL:
    db_file_path = settings.DATABASE_URL.replace('sqlite:///', '').split('?')[0]
    if os.path.isabs(db_file_path) or os.path.exists(db_file_path):
        try:
            con = sqlite3.connect(db_file_path)
            res = con.execute("PRAGMA quick_check;").fetchall()
            con.close()
            if not res or res[0][0] != 'ok':
                print(f"[WARN] 손상된 SQLite 파일 감지: {res}. 새 DB로 자동 재생성합니다.")
                os.rename(db_file_path, f"{db_file_path}.bad_{int(time.time())}")
        except Exception as err:
            print(f"[WARN] SQLite 파일 읽기 실패 ({err}). 복구 진행.")
            try:
                os.rename(db_file_path, f"{db_file_path}.bad_{int(time.time())}")
            except Exception:
                pass

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={'check_same_thread': False, 'timeout': 15.0} if 'sqlite' in settings.DATABASE_URL else {}
)

if 'sqlite' in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=10000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        except Exception as e:
            print(f"[WARN] SQLite PRAGMA 설정 오류 무시: {e}")



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
