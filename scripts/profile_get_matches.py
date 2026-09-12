import time
import sys
import os

sys.path.insert(0, ".")
from app.core.database import SessionLocal
from app.services.match_service import MatchService
from app.models.models import Match
from app.services.betman_service import BetmanService

db = SessionLocal()
t0 = time.time()

# 1. DB query
t_start = time.time()
q_matches = MatchService.get_matches(db, limit=300, order="asc")
t_end = time.time()
print(f"get_matches total time: {t_end - t_start:.3f}s, count: {len(q_matches)}")

db.close()
