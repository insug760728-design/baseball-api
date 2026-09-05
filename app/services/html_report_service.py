# -*- coding: utf-8 -*-
import os
import json

def generate_standalone_scoreboard_html(match_dict: dict, detail_dict: dict, output_path: str):
    """
    공식 MLB 경기 결과 1~9회 전광판 및 타자/투수 세부 지표를
    브라우저에서 바로 열어볼 수 있는 독립형 고품질 HTML 파일로 생성합니다.
    """
    m = match_dict
    period = detail_dict.get("period_scores", {})
    innings = period.get("innings", {})
    summary = period.get("summary", {})
    home_sum = summary.get("home", {})
    away_sum = summary.get("away", {})
    events = detail_dict.get("events", [])
    player_stats = detail_dict.get("player_stats", [])

    in_keys = sorted(list(innings.keys()), key=lambda x: int(x))

    # 테이블 헤더 이닝 생성
    th_innings = "".join([f"<th class='text-center'>{k}</th>" for k in in_keys])
    
    # 원정팀(초공) 이닝 행
    away_innings_td = "".join([f"<td class='text-center'>{innings[k].get('away', '-')}</td>" for k in in_keys])
    
    # 홈팀(말공) 이닝 행
    home_innings_td = "".join([f"<td class='text-center'>{innings[k].get('home', '-')}</td>" for k in in_keys])

    # 타자 / 투수 분리
    hitters = [p for p in player_stats if p.get("extra_stats", {}).get("type") == "HITTER"]
    pitchers = [p for p in player_stats if p.get("extra_stats", {}).get("type") == "PITCHER"]

    hitters_rows = ""
    for p in hitters:
        ex = p.get("extra_stats", {})
        is_home = (p["team_name"] == m["home_team_name"])
        t_badge = "<span class='badge bg-primary-subtle text-primary border'>홈</span>" if is_home else "<span class='badge bg-danger-subtle text-danger border'>원정</span>"
        hitters_rows += f"""
        <tr>
          <td>{t_badge} {p['team_name']}</td>
          <td><span class='badge bg-light text-dark border'>{p['position']}</span></td>
          <td class='fw-bold'>{p['player_name']}</td>
          <td class='text-center'>{ex.get('ab', 0)}</td>
          <td class='text-center'>{ex.get('r', 0)}</td>
          <td class='text-center fw-bold text-primary'>{ex.get('h', 0)}</td>
          <td class='text-center'>{ex.get('2b', 0)}</td>
          <td class='text-center'>{ex.get('3b', 0)}</td>
          <td class='text-center fw-bold text-danger'>{ex.get('hr', 0)}</td>
          <td class='text-center fw-bold text-success'>{ex.get('rbi', 0)}</td>
          <td class='text-center'>{ex.get('bb', 0)}</td>
          <td class='text-center'>{ex.get('so', 0)}</td>
          <td class='text-center'>{ex.get('sb', 0)}</td>
          <td class='text-center'>{ex.get('avg', '-')}</td>
          <td class='text-center fw-semibold'>{ex.get('ops', '-')}</td>
        </tr>
        """

    pitchers_rows = ""
    for p in pitchers:
        ex = p.get("extra_stats", {})
        is_home = (p["team_name"] == m["home_team_name"])
        t_badge = "<span class='badge bg-primary-subtle text-primary border'>홈</span>" if is_home else "<span class='badge bg-danger-subtle text-danger border'>원정</span>"
        dec_badge = f"<span class='badge bg-warning text-dark'>{ex['decision']}</span>" if ex.get('decision') else "-"
        pitchers_rows += f"""
        <tr>
          <td>{t_badge} {p['team_name']}</td>
          <td><span class='badge bg-light text-dark border'>{p['position']}</span></td>
          <td class='fw-bold'>{p['player_name']}</td>
          <td class='text-center fw-bold text-primary'>{ex.get('ip', '-')}</td>
          <td class='text-center'>{ex.get('np', '-')}</td>
          <td class='text-center'>{ex.get('h', '-')}</td>
          <td class='text-center'>{ex.get('r', '-')}</td>
          <td class='text-center'>{ex.get('er', '-')}</td>
          <td class='text-center'>{ex.get('bb', '-')}</td>
          <td class='text-center fw-bold text-danger'>{ex.get('so', '-')}</td>
          <td class='text-center'>{ex.get('hr', '-')}</td>
          <td class='text-center'>{ex.get('era', '-')}</td>
          <td class='text-center'>{ex.get('whip', '-')}</td>
          <td class='text-center'>{dec_badge}</td>
        </tr>
        """

    events_html = ""
    for ev in events:
        is_hr = ev.get("event_type") == "HOMERUN"
        icon = "💥" if is_hr else "⚾"
        badge = "bg-danger" if is_hr else "bg-primary"
        events_html += f"""
        <div class="list-group-item py-2 d-flex justify-content-between align-items-center">
          <div>
            <span class="badge {badge} me-2">{ev['time_display']}</span>
            <span class="fw-bold me-2">{icon} [{ev['team_name']}] {ev['player_name']}</span>
            <span class="text-muted small">{ev.get('description', '')}</span>
          </div>
          <div>
            <span class="badge bg-light text-dark border fw-bold">{ev.get('score_after', '')}</span>
          </div>
        </div>
        """
    if not events_html:
        events_html = "<div class='text-muted p-3'>기록된 득점 이벤트가 없습니다.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>[공식 MLB 실시간 결과] {m['away_team_name']} vs {m['home_team_name']}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    body {{ background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    .header-box {{ background: linear-gradient(135deg, #0b1f3a 0%, #1e3a8a 100%); color: white; padding: 2.2rem 0; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.18); }}
    .score-badge {{ font-size: 2.2rem; font-weight: 800; min-width: 130px; text-align: center; }}
    .scoreboard-table th {{ background-color: #0f172a; color: white; text-align: center; font-size: 0.9rem; }}
    .scoreboard-table td {{ text-align: center; font-size: 0.95rem; font-weight: 500; vertical-align: middle; }}
    .scoreboard-total {{ font-weight: bold; background-color: #f8fafc; }}
  </style>
</head>
<body>

  <div class="header-box">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <span class="badge bg-success mb-2 px-3 py-1"><i class="bi bi-broadcast me-1"></i>메이저리그 공식 Stats API (statsapi.mlb.com) 실시간 연동</span>
          <h2 class="fw-bold mb-1"><i class="bi bi-trophy-fill text-warning me-2"></i>{m['away_team_name']} vs {m['home_team_name']}</h2>
          <p class="text-white-50 mb-0">일시: {m['match_date']} | 구장: {m['stadium']} | 공식 Game ID: {m['official_id']}</p>
        </div>
        <div>
          <a href="http://localhost:8000/" target="_blank" class="btn btn-warning text-dark fw-bold px-4 py-2">
            <i class="bi bi-sliders me-1"></i>웹 관리 센터 바로가기
          </a>
        </div>
      </div>
    </div>
  </div>

  <div class="container mb-5">
    <!-- 스코어 배너 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4 text-center">
        <div class="row align-items-center">
          <div class="col">
            <h3 class="fw-bold text-danger mb-1">{m['away_team_name']}</h3>
            <span class="badge bg-light text-muted border">초공 (AWAY)</span>
          </div>
          <div class="col-auto">
            <div class="badge bg-dark text-white score-badge px-4 py-2 shadow">{m['away_score']} : {m['home_score']}</div>
            <div class="mt-2"><span class="badge bg-secondary">{m['status']}</span></div>
          </div>
          <div class="col">
            <h3 class="fw-bold text-primary mb-1">{m['home_team_name']}</h3>
            <span class="badge bg-light text-muted border">말공 (HOME)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 1~9회 전광판 정밀 스코어보드 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0 fw-bold"><i class="bi bi-grid-3x3 me-2 text-primary"></i>1회부터 9회까지의 전광판 스코어보드 (Linescore)</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-bordered scoreboard-table mb-0">
            <thead>
              <tr>
                <th style="width: 180px;">팀 명</th>
                {th_innings}
                <th class="scoreboard-total text-danger">R</th>
                <th class="scoreboard-total">H</th>
                <th class="scoreboard-total">E</th>
                <th class="scoreboard-total">B</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="fw-bold text-start ps-3">{m['away_team_name']} (원정)</td>
                {away_innings_td}
                <td class="scoreboard-total text-danger fw-bold fs-6">{away_sum.get('R', m['away_score'])}</td>
                <td class="scoreboard-total">{away_sum.get('H', 0)}</td>
                <td class="scoreboard-total">{away_sum.get('E', 0)}</td>
                <td class="scoreboard-total">{away_sum.get('B', 0)}</td>
              </tr>
              <tr>
                <td class="fw-bold text-start ps-3">{m['home_team_name']} (홈)</td>
                {home_innings_td}
                <td class="scoreboard-total text-danger fw-bold fs-6">{home_sum.get('R', m['home_score'])}</td>
                <td class="scoreboard-total">{home_sum.get('H', 0)}</td>
                <td class="scoreboard-total">{home_sum.get('E', 0)}</td>
                <td class="scoreboard-total">{home_sum.get('B', 0)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 득점 및 승부처 타임라인 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0 fw-bold"><i class="bi bi-clock-history me-2 text-primary"></i>주요 경기 상황 및 홈런/타점 타임라인</h5>
      </div>
      <div class="card-body p-0">
        <div class="list-group list-group-flush">
          {events_html}
        </div>
      </div>
    </div>

    <!-- 타자 세부 기록 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0 fw-bold"><i class="bi bi-lightning-fill text-warning me-2"></i>출전 타자 정밀 기록 (1~9번 타순 및 교체)</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive" style="max-height: 480px; overflow-y: auto;">
          <table class="table table-hover align-middle mb-0 text-center" style="font-size: 0.88rem;">
            <thead class="table-light sticky-top">
              <tr>
                <th>구단</th>
                <th>타순/포지션</th>
                <th>선수명</th>
                <th>타수(AB)</th>
                <th>득점(R)</th>
                <th>안타(H)</th>
                <th>2루타</th>
                <th>3루타</th>
                <th>홈런(HR)</th>
                <th>타점(RBI)</th>
                <th>볼넷(BB)</th>
                <th>삼진(SO)</th>
                <th>도루(SB)</th>
                <th>시즌AVG</th>
                <th>시즌OPS</th>
              </tr>
            </thead>
            <tbody>
              {hitters_rows}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 투수 세부 기록 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0 fw-bold"><i class="bi bi-shield-shaded text-primary me-2"></i>출전 투수 정밀 기록 (선발 및 불펜)</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0 text-center" style="font-size: 0.88rem;">
            <thead class="table-light">
              <tr>
                <th>구단</th>
                <th>역할</th>
                <th>선수명</th>
                <th>이닝(IP)</th>
                <th>투구수(NP)</th>
                <th>피안타(H)</th>
                <th>실점(R)</th>
                <th>자책(ER)</th>
                <th>4사구(BB)</th>
                <th>탈삼진(SO)</th>
                <th>피홈런(HR)</th>
                <th>시즌ERA</th>
                <th>시즌WHIP</th>
                <th>결과</th>
              </tr>
            </thead>
            <tbody>
              {pitchers_rows}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 앱 연동 JSON 안내 -->
    <div class="card border-0 shadow-sm p-4 bg-light text-center">
      <h6 class="fw-bold mb-1">앱(모바일/웹) 연동용 데이터가 'exports/MLB/' 디렉토리에 자동 생성되었습니다.</h6>
      <p class="text-muted small mb-3">각 구단별 폴더 안에 타자별, 투수별, 경기별 JSON 파일이 생성되어 즉시 연동 가능합니다.</p>
      <div>
        <a href="http://localhost:8000/api/v1/content/download-zip/MLB" class="btn btn-primary fw-bold px-4 py-2">
          <i class="bi bi-file-earmark-zip-fill me-1"></i>전체 구단/선수 JSON 압축파일(ZIP) 다운로드
        </a>
      </div>
    </div>
  </div>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
