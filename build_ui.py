# -*- coding: utf-8 -*-
with open("app/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 기존 playerStatsTableBody 렌더링 부분을 홈팀 / 원정팀 전 선수 분할 렌더링으로 업그레이드
old_table_section = """          <!-- 선수별 세부 수치(득점/골/타점, 어시스트, 슈팅 등) 및 수정 테이블 -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 class="mb-0 fw-bold"><i class="bi bi-person-lines-fill me-2"></i>선수별 상세 수치 (실시간 편집 가능)</h5>
              <span class="badge bg-success">내 앱으로 전송될 수치</span>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>소속팀</th>
                      <th>선수명</th>
                      <th>포지션</th>
                      <th>득점(골/타점/PTS)</th>
                      <th>도움(AST)</th>
                      <th>슈팅/타수</th>
                      <th>관리</th>
                    </tr>
                  </thead>
                  <tbody id="playerStatsTableBody">
                  </tbody>
                </table>
              </div>
            </div>
          </div>"""

new_table_section = """          <!-- 양팀 전 선수 전체 라인업 & 세부 수치 관리 테이블 -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-0 fw-bold"><i class="bi bi-people-fill me-2"></i>출전 전 선수 전체 라인업 & 세부 수치</h5>
                <small class="text-muted">선발 및 교체 출전 선수 전원의 수치를 조회하고 직접 수정할 수 있습니다.</small>
              </div>
              <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-primary active" id="btnFilterAll" onclick="filterPlayerTeam('ALL')">전체 명단</button>
                <button type="button" class="btn btn-sm btn-outline-primary" id="btnFilterHome" onclick="filterPlayerTeam('HOME')">홈팀 선수</button>
                <button type="button" class="btn btn-sm btn-outline-primary" id="btnFilterAway" onclick="filterPlayerTeam('AWAY')">원정팀 선수</button>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 480px; overflow-y: auto;">
                <table class="table table-hover align-middle mb-0">
                  <thead class="table-light sticky-top">
                    <tr>
                      <th>팀</th>
                      <th>등번호</th>
                      <th>선수명</th>
                      <th>포지션</th>
                      <th>출전(분)</th>
                      <th>득점(골/타점)</th>
                      <th>도움</th>
                      <th>슈팅/타수</th>
                      <th>관리</th>
                    </tr>
                  </thead>
                  <tbody id="playerStatsTableBody">
                  </tbody>
                </table>
              </div>
            </div>
          </div>"""

if old_table_section in html:
    html = html.replace(old_table_section, new_table_section)

# renderPlayerStats 자바스크립트 함수 업그레이드
old_js = """    function renderPlayerStats(players) {
      const tbody = document.getElementById("playerStatsTableBody");
      if (!players || players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-3 text-muted">선수 기록이 없습니다.</td></tr>';
        return;
      }

      let html = '';
      players.forEach(p => {
        const overrideBadge = p.is_override ? '<span class="badge bg-warning text-dark ms-1" title="관리자가 직접 수정한 수치">수정됨</span>' : '';
        html += `
          <tr>
            <td><span class="badge bg-light text-dark border">${p.team_name}</span></td>
            <td class="fw-bold">${p.player_name} ${overrideBadge}</td>
            <td><span class="text-muted small">${p.position || '-'}</span></td>
            <td><span class="badge bg-primary fs-6">${p.points}</span></td>
            <td>${p.assists}</td>
            <td>${p.shots}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary" onclick="openPlayerEditModal(${p.id}, '${p.player_name}', ${p.points}, ${p.assists}, ${p.shots})">
                <i class="bi bi-pencil-square me-1"></i>수치 수정
              </button>
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }"""

new_js = """    let currentMatchPlayers = [];
    let currentTeamFilter = 'ALL';

    function filterPlayerTeam(teamType) {
      currentTeamFilter = teamType;
      document.getElementById('btnFilterAll').className = `btn btn-sm ${teamType === 'ALL' ? 'btn-primary' : 'btn-outline-primary'}`;
      document.getElementById('btnFilterHome').className = `btn btn-sm ${teamType === 'HOME' ? 'btn-primary' : 'btn-outline-primary'}`;
      document.getElementById('btnFilterAway').className = `btn btn-sm ${teamType === 'AWAY' ? 'btn-primary' : 'btn-outline-primary'}`;
      renderPlayerStats(currentMatchPlayers);
    }

    function renderPlayerStats(players) {
      currentMatchPlayers = players || [];
      const tbody = document.getElementById("playerStatsTableBody");
      if (!players || players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted">출전 선수 라인업 기록이 없습니다.</td></tr>';
        return;
      }

      const homeTeam = document.getElementById("detailHomeTeam").textContent;
      const awayTeam = document.getElementById("detailAwayTeam").textContent;

      let filtered = players;
      if (currentTeamFilter === 'HOME') {
        filtered = players.filter(p => p.team_name.includes(homeTeam) || homeTeam.includes(p.team_name));
      } else if (currentTeamFilter === 'AWAY') {
        filtered = players.filter(p => p.team_name.includes(awayTeam) || awayTeam.includes(p.team_name));
      }

      let html = '';
      filtered.forEach(p => {
        const overrideBadge = p.is_override ? '<span class="badge bg-warning text-dark ms-1" title="수정됨">수정됨</span>' : '';
        const isHome = p.team_name.includes(homeTeam) || homeTeam.includes(p.team_name);
        const teamBadgeColor = isHome ? 'bg-primary-subtle text-primary' : 'bg-danger-subtle text-danger';

        html += `
          <tr>
            <td><span class="badge ${teamBadgeColor} border">${p.team_name}</span></td>
            <td class="text-muted fw-bold">${p.back_number ? '#' + p.back_number : '-'}</td>
            <td class="fw-bold">${p.player_name} ${overrideBadge}</td>
            <td><span class="badge bg-light text-dark border">${p.position || '-'}</span></td>
            <td><small class="text-muted">${p.minutes_played > 0 ? p.minutes_played + "'" : '-'}</small></td>
            <td><span class="badge bg-primary fs-6">${p.points}</span></td>
            <td>${p.assists}</td>
            <td>${p.shots}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary" onclick="openPlayerEditModal(${p.id}, '${p.player_name}', ${p.points}, ${p.assists}, ${p.shots})">
                <i class="bi bi-pencil-square me-1"></i>수정
              </button>
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }"""

if old_js in html:
    html = html.replace(old_js, new_js)

with open("app/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("UI full roster update complete!")