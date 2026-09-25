# -*- coding: utf-8 -*-
import asyncio
import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

logger = logging.getLogger("ai_chat_bot")
KST = timezone(timedelta(hours=9))

_bot_running = False
_posted_match_ids = set()
_match_cursor = 0

def get_next_match_result_message() -> Dict[str, Any]:
    """로컬 DB에서 어제 및 오늘 종료된 실제 공식 경기 결과를 가볍고 정확하게 추출하여 브리핑 메시지 생성"""
    global _posted_match_ids, _match_cursor
    from app.core.database import SessionLocal
    from app.models.models import Match

    db = SessionLocal()
    try:
        now = datetime.now(KST)
        since_date = (now - timedelta(days=2)).strftime("%Y-%m-%d 00:00")
        matches = db.query(Match).filter(
            Match.status == "FINISHED",
            Match.match_date >= since_date
        ).order_by(Match.match_date.desc()).limit(30).all()

        if not matches:
            since_date_7d = (now - timedelta(days=7)).strftime("%Y-%m-%d 00:00")
            matches = db.query(Match).filter(
                Match.status == "FINISHED",
                Match.match_date >= since_date_7d
            ).order_by(Match.match_date.desc()).limit(30).all()

        sport_icons = {'BASEBALL': '⚾', 'SOCCER': '⚽', 'BASKETBALL': '🏀', 'VOLLEYBALL': '🏐'}
        author_pool = [
            '전일경기알리미', '스코어브리핑', '스포츠결과센터', '실시간결과알림',
            '경기요약봇', '야구결과센터', '축구결과센터'
        ]

        selected_match = None
        # 1. 아직 게시되지 않은 최신 경기 우선 선택
        for m in matches:
            if m.id not in _posted_match_ids:
                selected_match = m
                _posted_match_ids.add(m.id)
                break

        # 2. 모두 게시되었으면 커서 기반으로 순환 선택
        if not selected_match and matches:
            selected_match = matches[_match_cursor % len(matches)]
            _match_cursor += 1
            if len(_posted_match_ids) > 100:
                _posted_match_ids.clear()

        if selected_match:
            m = selected_match
            icon = sport_icons.get(m.sport_code, '🏆')
            league = (m.league_name or '').split('(')[0].strip() or m.sport_code
            h_score = m.home_score if m.home_score is not None else '-'
            a_score = m.away_score if m.away_score is not None else '-'

            m_date = (m.match_date or '')[:10]
            today_str = now.strftime('%Y-%m-%d')
            prefix = '[오늘 경기결과]' if m_date == today_str else '[전일 경기결과]'

            content = f"{prefix} {icon} {league} | {m.home_team_name} {h_score} : {a_score} {m.away_team_name} (종료)"

            sport_tag = "MLB" if "MLB" in (m.league_name or "") else ("KBO" if "KBO" in (m.league_name or "") else ("EPL" if "EPL" in (m.league_name or "") else m.sport_code[:6]))
            author = random.choice(author_pool)
            channel = m.sport_code if m.sport_code in ["BASEBALL", "SOCCER"] else "ALL"

            return {
                "author": author,
                "channel": channel,
                "sport_tag": sport_tag,
                "content": content,
                "created_at": now.strftime("%H:%M"),
                "likes": random.randint(5, 20)
            }
        else:
            return {
                "author": "스포츠결과센터",
                "channel": "ALL",
                "sport_tag": "일반",
                "content": "[경기 알림] 어제 및 오늘 경기 결과가 순차적으로 실시간 등록됩니다.",
                "created_at": now.strftime("%H:%M"),
                "likes": 8
            }
    except Exception as e:
        logger.warning(f"Error generating match result message: {e}")
        return {
            "author": "경기결과알리미",
            "channel": "ALL",
            "sport_tag": "일반",
            "content": "[경기 알림] 최신 경기 결과와 스코어보드를 확인해보세요.",
            "created_at": datetime.now(KST).strftime("%H:%M"),
            "likes": 5
        }
    finally:
        db.close()


async def start_ai_chat_bot_task():
    """사용자 요청에 따라 중앙 채팅창 자동 등록 기능 영구 비활성화"""
    logger.info("[AIChatBot] Automated match result broadcaster has been DISABLED by admin.")
    return
