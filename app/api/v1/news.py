# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["실시간 스포츠 뉴스"])

@router.get("/", summary="실시간 스포츠 뉴스 목록 조회")
def get_sports_news(
    category: str = Query("ALL", description="종목 카테고리 (ALL, BASEBALL, SOCCER, BASKETBALL, ANALYTICS)"),
    refresh: bool = Query(False, description="강제 최신화 여부")
):
    news = NewsService.get_real_news(category=category, force_refresh=refresh)
    return {
        "status": "success",
        "total": len(news),
        "category": category,
        "data": news
    }

@router.post("/refresh", summary="실시간 스포츠 뉴스 즉시 최신화 수집")
def refresh_sports_news():
    news = NewsService.get_real_news(category="ALL", force_refresh=True)
    return {
        "status": "success",
        "message": "실시간 스포츠 뉴스 최신화 완료",
        "total": len(news)
    }
