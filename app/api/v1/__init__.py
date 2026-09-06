from fastapi import APIRouter
from app.api.v1.matches import router as matches_router
from app.api.v1.player_stats import router as players_router
from app.api.v1.crawler import router as crawler_router
from app.api.v1.export import router as export_router
from app.api.v1.content import router as content_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.scheduler import router as scheduler_router
from app.api.v1.news import router as news_router
from app.api.v1.community import router as community_router
from app.api.v1.toto import router as toto_router
from app.api.v1.live import router as live_router
from app.api.v1.auth import router as auth_router
from app.api.v1.traffic import router as traffic_router

api_v1_router = APIRouter()
api_v1_router.include_router(matches_router)
api_v1_router.include_router(players_router)
api_v1_router.include_router(crawler_router)
api_v1_router.include_router(export_router)
api_v1_router.include_router(content_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(scheduler_router)
api_v1_router.include_router(news_router)
api_v1_router.include_router(community_router)
api_v1_router.include_router(toto_router)
api_v1_router.include_router(live_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(traffic_router)
