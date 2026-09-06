# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.services.traffic_service import TrafficService
from app.core.websocket_manager import manager

router = APIRouter(prefix="/traffic", tags=["Traffic & Analytics"])

@router.get("/status")
def get_traffic_status():
    live_count = 664 + len(manager.active_connections)
    return TrafficService.update_and_export(current_active=live_count)

@router.get("/data")
def get_traffic_raw_data():
    return TrafficService.load_traffic_data()
