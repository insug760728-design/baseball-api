import os
import json
import zipfile
import shutil
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.models import Match, MatchDetail, MatchEvent, PlayerMatchStat
from app.core.teams_master import LEAGUE_TEAMS_DATA
from app.services.match_service import MatchService
from app.services.analytics_service import AnalyticsService

class FolderExportService:

    @classmethod
    def export_league_to_folder_structure(cls, db: Session, league_id: str = "MLB", start_date: str = "2026-09-01", end_date: str = "2026-09-07", base_dir: str = "exports"):
        """
        야구/축구 정밀 분석 폴더 구조 내보내기
        """
        if league_id.upper() in ["EPL", "LALIGA", "BUNDESLIGA", "SERIE_A", "LIGUE_1"]:
            return cls.export_soccer_league_to_folder_structure(db, league_id=league_id, start_date=start_date, end_date=end_date, base_dir=base_dir)
        elif league_id.upper() in ["NBA", "BASKETBALL"]:
            return cls.export_basketball_league_to_folder_structure(db, league_id=league_id, start_date=start_date, end_date=end_date, base_dir=base_dir)

        # 1. 해당 기간 경기 조회 (DB에 없을 경우에만 공식 사이트 동기화)
        all_matches = MatchService.get_matches(db, start_date=start_date, end_date=end_date)
        if not all_matches:
            MatchService.sync_from_official_site(db, league_id=league_id, start_date=start_date, end_date=end_date)
            all_matches = MatchService.get_matches(db, start_date=start_date, end_date=end_date)
        league_matches = [m for m in all_matches if league_id.upper() in (m.official_id or "") or league_id.upper() in m.league_name.upper()]
        if not league_matches:
            league_matches = all_matches

        # 3. 내보내기 디렉토리 초기화
        export_root = os.path.abspath(os.path.join(base_dir, league_id))
        if os.path.exists(export_root):
            shutil.rmtree(export_root)
        os.makedirs(export_root, exist_ok=True)

        # 4. 전체 팀 수집
        team_names = set()
        for m in league_matches:
            team_names.add(m.home_team_name)
            team_names.add(m.away_team_name)

        master_info = LEAGUE_TEAMS_DATA.get(league_id, {})
        for tm in master_info.get("teams", []):
            team_names.add(tm["team_name"])

        export_manifest = {
            "sport": "BASEBALL",
            "league_id": league_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "exported_at": os.getenv("CURRENT_TIME", "2026-09-05T13:30:00"),
            "total_teams": len(team_names),
            "teams": {}
        }

        # 5. 각 팀별 폴더 구성
        for team_name in sorted(list(team_names)):
            safe_team = team_name.replace(" ", "_").replace("/", "_")
            team_dir = os.path.join(export_root, safe_team)
            matches_dir = os.path.join(team_dir, "matches")
            hitters_dir = os.path.join(team_dir, "hitters")
            pitchers_dir = os.path.join(team_dir, "pitchers")

            os.makedirs(matches_dir, exist_ok=True)
            os.makedirs(hitters_dir, exist_ok=True)
            os.makedirs(pitchers_dir, exist_ok=True)

            team_match_objs = [m for m in league_matches if m.home_team_name == team_name or m.away_team_name == team_name]
            team_matches_summary = []
            player_logs = {}

            # (1) 경기별 상세 박스스코어 저장
            for m in team_match_objs:
                full_m = MatchService.get_match_full_detail(db, m.id)
                opponent = m.away_team_name if m.home_team_name == team_name else m.home_team_name
                is_home = (m.home_team_name == team_name)

                clean_date = m.match_date.replace(" ", "_").replace(":", "")
                safe_opp = opponent.replace(" ", "_").replace("/", "_")
                match_file = f"{clean_date}_vs_{safe_opp}.json"

                match_content = {
                    "sport": "BASEBALL",
                    "match_id": m.id,
                    "official_id": m.official_id,
                    "date": m.match_date,
                    "stadium": m.stadium,
                    "team": team_name,
                    "opponent": opponent,
                    "score": f"{m.home_score if is_home else m.away_score} : {m.away_score if is_home else m.home_score}",
                    "result": "승" if (m.home_score if is_home else m.away_score) > (m.away_score if is_home else m.home_score) else "패",
                    "innings_scoreboard": full_m["details"]["period_scores"],
                    "team_stats": full_m["details"]["team_stats"],
                    "events": [ev for ev in full_m["events"] if ev["team_name"] == team_name],
                    "team_players_boxscore": [p for p in full_m["player_stats"] if p["team_name"] == team_name]
                }

                with open(os.path.join(matches_dir, match_file), "w", encoding="utf-8") as mf:
                    json.dump(match_content, mf, ensure_ascii=False, indent=2)

                team_matches_summary.append({
                    "date": m.match_date,
                    "opponent": opponent,
                    "score": match_content["score"],
                    "result": match_content["result"],
                    "file": f"matches/{match_file}"
                })

                # 선수 경기 로그 집계
                for p in full_m["player_stats"]:
                    if p["team_name"] == team_name:
                        p_name = p["player_name"]
                        if p_name not in player_logs:
                            player_logs[p_name] = {
                                "player_name": p_name,
                                "back_number": p["back_number"],
                                "position": p["position"],
                                "extra_stats": p["extra_stats"],
                                "games": []
                            }
                        player_logs[p_name]["games"].append({
                            "match_date": m.match_date,
                            "opponent": opponent,
                            "points": p["points"],
                            "shots": p["shots"],
                            "extra_stats": p["extra_stats"],
                            "is_override": p["is_override"],
                            "override_reason": p["override_reason"]
                        })

            # (2) 타자 / 투수 분리 저장
            hitters_list = []
            pitchers_list = []

            for p_name, p_data in player_logs.items():
                safe_p = p_name.replace(" ", "_")
                p_type = p_data["extra_stats"].get("player_type", "HITTER")
                is_pitcher = (
                    p_type == "PITCHER" or
                    "P" in (p_data["position"] or "") or
                    "투수" in (p_data["position"] or "") or
                    any(g.get("extra_stats", {}).get("player_type") == "PITCHER" for g in p_data["games"])
                )

                if is_pitcher:
                    # 투수 정밀 분석 파일
                    target_dir = pitchers_dir
                    p_file = f"{safe_p}.json"
                    
                    pitching_games = [g for g in p_data["games"] if g.get("extra_stats", {}).get("player_type") == "PITCHER" or "투수" in (p_data["position"] or "")]
                    eval_games = pitching_games if pitching_games else p_data["games"]

                    total_so = sum(g["extra_stats"].get("strikeouts", g["extra_stats"].get("so", g.get("points", 0))) for g in eval_games)
                    total_er = sum(g["extra_stats"].get("er", 0) for g in eval_games)

                    rolling = AnalyticsService.calculate_pitcher_rolling_stats(
                        db, p_name, team_name=team_name,
                        windows=[3, 5, 7, 10],
                        days_windows=[3, 5, 7, 10]
                    )
                    first_p_stat = (pitching_games[0]["extra_stats"] if pitching_games else p_data["extra_stats"])
                    content = {
                        "player_name": p_name,
                        "team": team_name,
                        "role": "PITCHER (투수)",
                        "back_number": p_data["back_number"],
                        "position": p_data["position"],
                        "games_count": len(eval_games),
                        "recent_trends": rolling.get("rolling_stats", {}),
                        "sabermetrics_trends": rolling.get("sabermetrics", {}),
                        "aggregated_pitching_stats": {
                            "total_strikeouts": total_so,
                            "total_earned_runs": total_er,
                            "season_era": first_p_stat.get("era", "3.00"),
                            "season_whip": first_p_stat.get("whip", "1.10"),
                            "has_user_override": any(g["is_override"] for g in eval_games)
                        },
                        "game_logs": eval_games
                    }
                    pitchers_list.append({"name": p_name, "pos": p_data["position"], "file": f"pitchers/{p_file}"})
                else:
                    # 타자 정밀 분석 파일
                    target_dir = hitters_dir
                    p_file = f"{safe_p}.json"

                    total_ab = sum(g.get("shots", 0) for g in p_data["games"])
                    total_h = sum(g["extra_stats"].get("hits", 0) for g in p_data["games"])
                    total_rbi = sum(g.get("points", 0) for g in p_data["games"])
                    total_hr = sum(g["extra_stats"].get("homeruns", 0) for g in p_data["games"])
                    total_r = sum(g["extra_stats"].get("runs", 0) for g in p_data["games"])
                    total_sb = sum(g["extra_stats"].get("stolen_bases", 0) for g in p_data["games"])

                    rolling = AnalyticsService.calculate_hitter_rolling_stats(
                        db, p_name, team_name=team_name,
                        windows=[3, 5, 7, 10],
                        days_windows=[3, 5, 7, 10]
                    )
                    content = {
                        "player_name": p_name,
                        "team": team_name,
                        "role": "HITTER (타자)",
                        "back_number": p_data["back_number"],
                        "position": p_data["position"],
                        "games_count": len(p_data["games"]),
                        "recent_trends": rolling.get("rolling_stats", {}),
                        "sabermetrics_trends": rolling.get("sabermetrics", {}),
                        "aggregated_batting_stats": {
                            "total_at_bats": total_ab,
                            "total_hits": total_h,
                            "total_rbi": total_rbi,
                            "total_homeruns": total_hr,
                            "total_runs": total_r,
                            "total_stolen_bases": total_sb,
                            "season_avg": p_data["extra_stats"].get("avg", "0.300"),
                            "season_ops": p_data["extra_stats"].get("ops", "0.850"),
                            "has_user_override": any(g["is_override"] for g in p_data["games"])
                        },
                        "game_logs": p_data["games"]
                    }
                    hitters_list.append({"name": p_name, "pos": p_data["position"], "file": f"hitters/{p_file}"})

                with open(os.path.join(target_dir, p_file), "w", encoding="utf-8") as pf:
                    json.dump(content, pf, ensure_ascii=False, indent=2)

            # (3) team_summary.json
            with open(os.path.join(team_dir, "team_summary.json"), "w", encoding="utf-8") as tf:
                json.dump({
                    "team_name": team_name,
                    "league": league_id,
                    "period": {"start_date": start_date, "end_date": end_date},
                    "total_matches": len(team_matches_summary),
                    "hitters_count": len(hitters_list),
                    "pitchers_count": len(pitchers_list),
                    "matches": team_matches_summary,
                    "hitters": hitters_list,
                    "pitchers": pitchers_list
                }, tf, ensure_ascii=False, indent=2)

            export_manifest["teams"][team_name] = {
                "folder": safe_team,
                "matches_count": len(team_matches_summary),
                "hitters_count": len(hitters_list),
                "pitchers_count": len(pitchers_list)
            }

        # 6. manifest.json
        with open(os.path.join(export_root, "manifest.json"), "w", encoding="utf-8") as mf:
            json.dump(export_manifest, mf, ensure_ascii=False, indent=2)

        # 7. ZIP 압축
        zip_path = os.path.abspath(os.path.join(base_dir, f"{league_id}_baseball_export.zip"))
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_root):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, export_root)
                    zipf.write(full_p, arcname=os.path.join(league_id, rel_p))

        return {
            "status": "SUCCESS",
            "export_root_dir": export_root,
            "zip_file_path": zip_path,
            "manifest": export_manifest
        }

    @classmethod
    def export_soccer_league_to_folder_structure(cls, db: Session, league_id: str = "EPL", start_date: str = "2024-09-01", end_date: str = "2024-09-07", base_dir: str = "exports"):
        from app.services.soccer_analytics_service import SoccerAnalyticsService
        all_matches = MatchService.get_matches(db, sport_code="SOCCER", start_date=start_date, end_date=end_date)
        if not all_matches:
            MatchService.sync_from_official_site(db, league_id=league_id, start_date=start_date, end_date=end_date)
            all_matches = MatchService.get_matches(db, sport_code="SOCCER", start_date=start_date, end_date=end_date)
        league_matches = [m for m in all_matches if league_id.upper() in (m.official_id or "") or league_id.upper() in m.league_name.upper()]
        if not league_matches:
            league_matches = all_matches

        export_root = os.path.abspath(os.path.join(base_dir, "SOCCER", league_id))
        if os.path.exists(export_root):
            shutil.rmtree(export_root)
        os.makedirs(export_root, exist_ok=True)

        team_names = set()
        for m in league_matches:
            team_names.add(m.home_team_name)
            team_names.add(m.away_team_name)

        export_manifest = {
            "sport": "SOCCER",
            "league_id": league_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "exported_at": datetime.now().isoformat(),
            "total_teams": len(team_names),
            "teams": {}
        }

        for team_name in sorted(list(team_names)):
            safe_team = team_name.replace(" ", "_").replace("/", "_")
            team_dir = os.path.join(export_root, safe_team)
            matches_dir = os.path.join(team_dir, "matches")
            attackers_dir = os.path.join(team_dir, "attackers")
            midfielders_dir = os.path.join(team_dir, "midfielders")
            defenders_dir = os.path.join(team_dir, "defenders")
            gks_dir = os.path.join(team_dir, "goalkeepers")

            for d in [matches_dir, attackers_dir, midfielders_dir, defenders_dir, gks_dir]:
                os.makedirs(d, exist_ok=True)

            team_match_objs = [m for m in league_matches if m.home_team_name == team_name or m.away_team_name == team_name]
            player_logs = {}

            for m in team_match_objs:
                full_m = MatchService.get_match_full_detail(db, m.id)
                opponent = m.away_team_name if m.home_team_name == team_name else m.home_team_name
                is_home = (m.home_team_name == team_name)
                clean_date = m.match_date.replace(" ", "_").replace(":", "")
                safe_opp = opponent.replace(" ", "_").replace("/", "_")
                match_file = f"{clean_date}_vs_{safe_opp}.json"

                adv_stats = SoccerAnalyticsService.compute_match_advanced_stats(db, m.id)
                team_adv = adv_stats.get("home" if is_home else "away", {})

                match_content = {
                    "sport": "SOCCER",
                    "match_id": m.id,
                    "date": m.match_date,
                    "team": team_name,
                    "opponent": opponent,
                    "score": f"{m.home_score if is_home else m.away_score} : {m.away_score if is_home else m.home_score}",
                    "period_scores": full_m["details"]["period_scores"],
                    "team_stats": full_m["details"]["team_stats"],
                    "advanced_metrics": team_adv,
                    "events": [ev for ev in full_m["events"] if ev["team_name"] == team_name],
                    "team_players_boxscore": [p for p in full_m["player_stats"] if p["team_name"] == team_name]
                }

                with open(os.path.join(matches_dir, match_file), "w", encoding="utf-8") as mf:
                    json.dump(match_content, mf, ensure_ascii=False, indent=2)

                for p in full_m["player_stats"]:
                    if p["team_name"] == team_name:
                        p_name = p["player_name"]
                        if p_name not in player_logs:
                            player_logs[p_name] = {
                                "player_name": p_name,
                                "back_number": p["back_number"],
                                "position": p["position"],
                                "extra_stats": p["extra_stats"],
                                "games": []
                            }
                        player_logs[p_name]["games"].append(p)

            for p_name, p_data in player_logs.items():
                safe_p = p_name.replace(" ", "_").replace("/", "_")
                pos = p_data.get("position", "FW")
                if pos == "GK": target_dir = gks_dir
                elif pos == "DF": target_dir = defenders_dir
                elif pos == "MF": target_dir = midfielders_dir
                else: target_dir = attackers_dir

                rolling = SoccerAnalyticsService.calculate_player_rolling_stats(db, p_name, team_name=team_name)
                p_content = {
                    "player_name": p_name,
                    "team": team_name,
                    "position": pos,
                    "back_number": p_data.get("back_number"),
                    "games_count": len(p_data["games"]),
                    "sabermetrics_trends": rolling.get("sabermetrics", {})
                }
                with open(os.path.join(target_dir, f"{safe_p}.json"), "w", encoding="utf-8") as pf:
                    json.dump(p_content, pf, ensure_ascii=False, indent=2)

            export_manifest["teams"][team_name] = {
                "matches_count": len(team_match_objs),
                "players_count": len(player_logs)
            }

        with open(os.path.join(export_root, "manifest.json"), "w", encoding="utf-8") as mf:
            json.dump(export_manifest, mf, ensure_ascii=False, indent=2)

        zip_path = os.path.abspath(os.path.join(base_dir, f"{league_id}_soccer_export.zip"))
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_root):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, export_root)
                    zipf.write(full_p, arcname=os.path.join(league_id, rel_p))

        return {
            "status": "SUCCESS",
            "export_root_dir": export_root,
            "zip_file_path": zip_path,
            "manifest": export_manifest
        }

    @classmethod
    def export_basketball_league_to_folder_structure(cls, db: Session, league_id: str = "NBA", start_date: str = "2026-04-10", end_date: str = "2026-04-15", base_dir: str = "exports"):
        """
        농구(NBA) 전용 정밀 분석 폴더 구조화 및 ZIP 압축 내보내기
        - exports/BASKETBALL/NBA/{TEAM}/guards/
        - exports/BASKETBALL/NBA/{TEAM}/forwards/
        - exports/BASKETBALL/NBA/{TEAM}/centers/
        - exports/BASKETBALL/NBA/{TEAM}/matches/
        - exports/BASKETBALL/NBA/{TEAM}/team_summary.json
        - exports/NBA_basketball_export.zip
        """
        from app.services.basketball_analytics_service import BasketballAnalyticsService

        # 1. 경기 조회
        all_matches = MatchService.get_matches(db, sport_code="BASKETBALL", start_date=start_date, end_date=end_date)
        if not all_matches:
            MatchService.sync_from_official_site(db, league_id=league_id, start_date=start_date, end_date=end_date)
            all_matches = MatchService.get_matches(db, sport_code="BASKETBALL", start_date=start_date, end_date=end_date)

        league_matches = [m for m in all_matches if league_id.upper() in (m.official_id or "") or league_id.upper() in m.league_name.upper()]
        if not league_matches:
            league_matches = all_matches

        # 2. 내보내기 디렉토리 초기화
        export_root = os.path.abspath(os.path.join(base_dir, "BASKETBALL", league_id))
        if os.path.exists(export_root):
            shutil.rmtree(export_root)
        os.makedirs(export_root, exist_ok=True)

        team_names = set()
        for m in league_matches:
            team_names.add(m.home_team_name)
            team_names.add(m.away_team_name)

        export_manifest = {
            "sport": "BASKETBALL",
            "league_id": league_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "exported_at": datetime.now().isoformat(),
            "total_teams": len(team_names),
            "teams": {}
        }

        for team_name in sorted(list(team_names)):
            safe_team = team_name.replace(" ", "_").replace("/", "_")
            team_dir = os.path.join(export_root, safe_team)
            guards_dir = os.path.join(team_dir, "guards")
            forwards_dir = os.path.join(team_dir, "forwards")
            centers_dir = os.path.join(team_dir, "centers")
            matches_dir = os.path.join(team_dir, "matches")

            os.makedirs(guards_dir, exist_ok=True)
            os.makedirs(forwards_dir, exist_ok=True)
            os.makedirs(centers_dir, exist_ok=True)
            os.makedirs(matches_dir, exist_ok=True)

            team_match_objs = [m for m in league_matches if m.home_team_name == team_name or m.away_team_name == team_name]

            # 1) 경기별 파일 생성
            for m in team_match_objs:
                opp_name = m.away_team_name if m.home_team_name == team_name else m.home_team_name
                is_home = (m.home_team_name == team_name)
                m_date_str = m.match_date[:10]
                m_time_str = m.match_date[11:16].replace(":", "") if len(m.match_date) > 15 else "0000"
                match_file_name = f"{m_date_str}_{m_time_str}_vs_{opp_name.replace(' ', '_')}.json"

                detail_data = MatchService.get_match_full_detail(db, m.id)
                adv_stats = BasketballAnalyticsService.compute_match_advanced_stats(m, m.details)

                m_content = {
                    "match_id": m.id,
                    "official_id": m.official_id,
                    "match_date": m.match_date,
                    "stadium": m.stadium,
                    "team": team_name,
                    "opponent": opp_name,
                    "is_home": is_home,
                    "team_score": m.home_score if is_home else m.away_score,
                    "opponent_score": m.away_score if is_home else m.home_score,
                    "status": m.status,
                    "period_scores": detail_data["details"]["period_scores"],
                    "team_stats": detail_data["details"]["team_stats"],
                    "advanced_metrics": adv_stats
                }
                with open(os.path.join(matches_dir, match_file_name), "w", encoding="utf-8") as mf:
                    json.dump(m_content, mf, ensure_ascii=False, indent=2)

            # 2) 선수별 파일 및 롤링 계산
            player_logs = {}
            for m in team_match_objs:
                m_detail = MatchService.get_match_full_detail(db, m.id)
                for p in m_detail["player_stats"]:
                    if p["team_name"] == team_name:
                        p_name = p["player_name"]
                        if p_name not in player_logs:
                            player_logs[p_name] = {
                                "position": p.get("position", "G"),
                                "back_number": p.get("back_number"),
                                "games": []
                            }
                        player_logs[p_name]["games"].append(p)

            for p_name, p_data in player_logs.items():
                safe_p = p_name.replace(" ", "_").replace("/", "_")
                pos = p_data.get("position", "G")
                if "C" in pos: target_dir = centers_dir
                elif "F" in pos: target_dir = forwards_dir
                else: target_dir = guards_dir

                rolling = BasketballAnalyticsService.calculate_player_rolling_stats(db, p_name, team_name=team_name)
                p_content = {
                    "player_name": p_name,
                    "team": team_name,
                    "position": pos,
                    "back_number": p_data.get("back_number"),
                    "games_count": len(p_data["games"]),
                    "rolling_stats": rolling
                }
                with open(os.path.join(target_dir, f"{safe_p}.json"), "w", encoding="utf-8") as pf:
                    json.dump(p_content, pf, ensure_ascii=False, indent=2)

            # 3) 구단 종합 요약
            team_summary = {
                "team_name": team_name,
                "league": league_id,
                "matches_played": len(team_match_objs),
                "total_players": len(player_logs),
                "exported_at": datetime.now().isoformat()
            }
            with open(os.path.join(team_dir, "team_summary.json"), "w", encoding="utf-8") as ts_file:
                json.dump(team_summary, ts_file, ensure_ascii=False, indent=2)

            export_manifest["teams"][team_name] = {
                "matches_count": len(team_match_objs),
                "players_count": len(player_logs)
            }

        with open(os.path.join(export_root, "manifest.json"), "w", encoding="utf-8") as mf:
            json.dump(export_manifest, mf, ensure_ascii=False, indent=2)

        zip_path = os.path.abspath(os.path.join(base_dir, f"{league_id}_basketball_export.zip"))
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_root):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, export_root)
                    zipf.write(full_p, arcname=os.path.join(league_id, rel_p))

        return {
            "status": "SUCCESS",
            "export_root_dir": export_root,
            "zip_file_path": zip_path,
            "manifest": export_manifest
        }
