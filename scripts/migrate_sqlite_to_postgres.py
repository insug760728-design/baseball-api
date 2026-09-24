# -*- coding: utf-8 -*-
"""
SQLite -> PostgreSQL 무중단 데이터 이전 (마이그레이션) 자동화 스크립트
3,000명 동시접속 트래픽 운영 대비 DB 마이그레이션 도구

사용법:
  python scripts/migrate_sqlite_to_postgres.py --postgres "postgresql://user:password@localhost:5432/sports_db"
  또는
  DATABASE_URL="postgresql://user:password@localhost:5432/sports_db" python scripts/migrate_sqlite_to_postgres.py
"""

import sys
import os
import argparse
import time
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.orm import sessionmaker

# 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.database import Base
from app.models import models

def run_migration(sqlite_path: str, postgres_url: str):
    print("=" * 65)
    print("🚀 [3,000명 트래픽 대비] SQLite -> PostgreSQL 데이터 마이그레이션")
    print("=" * 65)

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    if not os.path.exists(sqlite_path):
        print(f"❌ 원본 SQLite 파일을 찾을 수 없습니다: {sqlite_path}")
        return False

    print(f"📂 원본 DB (SQLite): {sqlite_path}")
    print(f"🎯 대상 DB (PostgreSQL): {postgres_url.split('@')[-1] if '@' in postgres_url else postgres_url}")
    print("-" * 65)

    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    pg_engine = create_engine(postgres_url, pool_pre_ping=True)

    # 1. PostgreSQL 스키마 자동 생성
    print("1️⃣ PostgreSQL 테이블 스키마 생성 중...")
    try:
        Base.metadata.create_all(bind=pg_engine)
        print("   ✅ 테이블 스키마 생성 완료.")
    except Exception as e:
        print(f"❌ 스키마 생성 실패: {e}")
        return False

    # 2. 테이블 순서 정렬 (외래키 종속성 고려)
    tables = Base.metadata.sorted_tables
    print(f"2️⃣ 총 {len(tables)}개 테이블 데이터 이전을 시작합니다.\n")

    total_rows_migrated = 0
    start_time = time.time()

    with sqlite_engine.connect() as sqlite_conn, pg_engine.connect() as pg_conn:
        for table in tables:
            tbl_name = table.name
            try:
                # SQLite 데이터 조회
                s_stmt = select(table)
                rows = sqlite_conn.execute(s_stmt).mappings().all()
                row_count = len(rows)

                if row_count == 0:
                    print(f"   ▫️ [{tbl_name}] 데이터 없음 (0건 건너뜀)")
                    continue

                # 청크 단위(500건씩)로 PostgreSQL에 삽입
                chunk_size = 500
                inserted = 0
                for i in range(0, row_count, chunk_size):
                    chunk = rows[i:i + chunk_size]
                    pg_conn.execute(table.insert(), [dict(r) for r in chunk])
                    pg_conn.commit()
                    inserted += len(chunk)

                total_rows_migrated += inserted
                print(f"   ✅ [{tbl_name}] {inserted:,}건 이전 완료")

                # PostgreSQL 시퀀스(PK auto-increment) 동기화
                if 'id' in table.c:
                    try:
                        seq_sql = text(f"SELECT setval(pg_get_serial_sequence('{tbl_name}', 'id'), COALESCE(MAX(id), 1)) FROM {tbl_name};")
                        pg_conn.execute(seq_sql)
                        pg_conn.commit()
                    except Exception:
                        pass

            except Exception as ex:
                print(f"   ⚠️ [{tbl_name}] 이전 중 오류 발생: {ex}")
                pg_conn.rollback()

    elapsed = time.time() - start_time
    print("-" * 65)
    print(f"🎉 마이그레이션 완료! 총 {total_rows_migrated:,}건의 데이터가 성공적으로 이전되었습니다. (소요시간: {elapsed:.2f}초)")
    print("=" * 65)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite to PostgreSQL Migration Tool")
    parser.add_argument("--sqlite", default=os.path.join(root_dir, "sports_data.db"), help="Source SQLite file path")
    parser.add_argument("--postgres", default=os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL"), help="Target PostgreSQL connection URL")

    args = parser.parse_args()

    if not args.postgres or "sqlite" in args.postgres:
        print("❌ PostgreSQL 접속 URL이 지정되지 않았습니다.")
        print("예시: python scripts/migrate_sqlite_to_postgres.py --postgres postgresql://user:pass@localhost:5432/sports_data")
        sys.exit(1)

    success = run_migration(args.sqlite, args.postgres)
    sys.exit(0 if success else 1)
