import os
import time
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite 자가 복구 및 무결성 점검
if 'sqlite' in settings.DATABASE_URL:
    db_file_path = settings.DATABASE_URL.replace('sqlite:///', '').split('?')[0]
    if os.path.exists(db_file_path) and os.path.getsize(db_file_path) > 0:
        try:
            con = sqlite3.connect(db_file_path)
            res = con.execute("PRAGMA quick_check;").fetchall()
            if not res or res[0][0] != 'ok':
                print(f"[WARN] SQLite quick_check 경고: {res}. VACUUM 자동 최적화 시도...")
                try:
                    con.execute("VACUUM;")
                    con.commit()
                except Exception as vac_err:
                    print(f"[WARN] VACUUM 실패: {vac_err}")
            con.close()
        except sqlite3.DatabaseError as err:
            print(f"[ERROR] SQLite 치명적 손상 ({err}). 백업 후 재생성.")
            try:
                os.rename(db_file_path, f"{db_file_path}.bad_{int(time.time())}")
            except Exception:
                pass
        except Exception as err:
            print(f"[WARN] SQLite 점검 중 예외: {err}")

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

from sqlalchemy.pool import NullPool

if 'sqlite' in db_url:
    engine = create_engine(
        db_url,
        poolclass=NullPool,
        connect_args={'check_same_thread': False, 'timeout': 30.0}
    )
else:
    # 🚀 PostgreSQL / MySQL 고성능 커넥션 풀 (동시접속 3,000명 트래픽 대비)
    engine = create_engine(
        db_url,
        pool_size=30,
        max_overflow=50,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True
    )

if 'sqlite' in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=10000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-2000")
            cursor.execute("PRAGMA mmap_size=0")
            cursor.execute("PRAGMA temp_store=FILE")
            cursor.execute("PRAGMA wal_autocheckpoint=100")
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
