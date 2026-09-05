from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.match_service import MatchService

router = APIRouter(prefix="/export", tags=["사용자 앱 연동 API"])

@router.get("/app-payload/{match_id}", summary="사용자 앱(모바일/웹) 전송용 최종 경기 및 선수 데이터")
def export_payload_for_app(match_id: int, db: Session = Depends(get_db)):
    """
    사용자가 직접 제작하는 앱에서 그대로 바인딩할 수 있는
    표준화된 최종 JSON 응답(가공/수정된 수치 포함)을 제공합니다.
    """
    data = MatchService.get_match_full_detail(db, match_id)
    if not data:
        raise HTTPException(status_code=404, detail="경기를 찾을 수 없습니다.")

    m = data["match"]
    
    # 홈팀/원정팀별 선수 분리 (유연한 팀명 매칭)
    def match_team(p_team, target_team):
        if not p_team or not target_team:
            return False
        p_clean = p_team.replace(" ", "").lower()
        t_clean = target_team.replace(" ", "").lower()
        first_token = target_team.split()[0].lower()
        return p_clean in t_clean or t_clean in p_clean or first_token in p_clean

    home_players = [p for p in data["player_stats"] if match_team(p["team_name"], m.home_team_name)]
    away_players = [p for p in data["player_stats"] if match_team(p["team_name"], m.away_team_name)]
    
    # 만약 매칭 분리가 모호한 경우 전체 선수 포함
    if not home_players and not away_players:
        home_players = data["player_stats"]

    return {
        "client_app_payload_version": "1.0",
        "sport": m.sport_code,
        "league": m.league_name,
        "match_id": m.id,
        "official_id": m.official_id,
        "schedule": {
            "date": m.match_date,
            "stadium": m.stadium,
            "round": m.round_name,
            "status": m.status
        },
        "score_summary": {
            "home_team": m.home_team_name,
            "away_team": m.away_team_name,
            "final_score": f"{m.home_score} : {m.away_score}",
            "home_score": m.home_score,
            "away_score": m.away_score,
            "is_user_modified": m.is_customized
        },
        "breakdown": {
            "periods": data["details"]["period_scores"],
            "team_stats": data["details"]["team_stats"]
        },
        "timeline_events": data["events"],
        "players_total": data["player_stats"],
        "roster_and_stats": {
            "home": {
                "team": m.home_team_name,
                "players": home_players
            },
            "away": {
                "team": m.away_team_name,
                "players": away_players
            }
        }
    }