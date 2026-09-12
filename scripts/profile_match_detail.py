import time
import sys
import os

sys.path.insert(0, ".")
from app.core.database import SessionLocal
from app.services.match_service import MatchService

db = SessionLocal()
for mid in [5, 6, 7, 8, 2, 3]:
    t0 = time.time()
    detail = MatchService.get_match_full_detail(db, mid)
    print(f"Match {mid} full detail time: {time.time()-t0:.3f}s")
db.close()
