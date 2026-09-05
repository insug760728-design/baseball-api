# -*- coding: utf-8 -*-
with open("app/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 헤더 아래에 "폴더 구조 내보내기" 퀵 배너 및 제어 버튼 삽입
folder_banner = """    <!-- 팀 및 선수별 폴더 구조 내보내기 모달 트리거 카드 -->
    <div class="card border-0 shadow-sm mb-4" style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white;">
      <div class="card-body p-4 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <h5 class="fw-bold mb-1"><i class="bi bi-folder-symlink-fill me-2 text-warning"></i>팀별 & 선수별 폴더 구조로 파일 생성 및 내보내기 (Export)</h5>
          <p class="mb-0 text-white-50 small">메이저리그/KBO/EPL 등 각 리그의 [전체 팀 폴더] 안에 [선수별 JSON 파일] 구조로 디스크에 저장하고 ZIP으로 쉽게 다운로드합니다.</p>
        </div>
        <div>
          <button class="btn btn-warning text-dark fw-bold px-4 py-2" onclick="openFolderExportModal()">
            <i class="bi bi-box-arrow-down me-1"></i> 팀/선수별 폴더 파일 생성 & 다운로드
          </button>
        </div>
      </div>
    </div>
"""

target_marker = """    <!-- 기간별 크롤링 및 필터링 제어 패널 -->"""
if target_marker in html and "folder-symlink-fill" not in html:
    html = html.replace(target_marker, folder_banner + "\n" + target_marker)

# 폴더 내보내기 결과 모달 추가
modal_html = """
  <!-- 팀/선수별 폴더 생성 및 다운로드 모달 -->
  <div class="modal fade" id="folderExportModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-dark text-white">
          <h5 class="modal-title fw-bold"><i class="bi bi-folder-check me-2 text-warning"></i>팀별 & 선수별 폴더 파일 생성 및 내보내기</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <div class="row g-3 mb-3">
            <div class="col-md-5">
              <label class="form-label fw-semibold">대상 리그 선택</label>
              <select id="modalExportLeague" class="form-select">
                <option value="MLB" selected>🇺🇸 미국 메이저리그 (MLB 전체 팀)</option>
                <option value="KBO">🇰🇷 한국 프로야구 (KBO 전체 구단)</option>
                <option value="EPL">🇪🇺 잉글랜드 프리미어리그 (EPL 전체 팀)</option>
                <option value="K_LEAGUE">🇰🇷 한국 프로축구 (K리그1)</option>
                <option value="KBL">🇰🇷 한국 프로농구 (KBL)</option>
              </select>
            </div>
            <div class="col-md-7">
              <label class="form-label fw-semibold">수집 및 정리 대상 기간</label>
              <div class="input-group">
                <input type="date" id="modalStartDate" class="form-control" value="2026-09-01">
                <span class="input-group-text">~</span>
                <input type="date" id="modalEndDate" class="form-control" value="2026-09-07">
              </div>
            </div>
          </div>

          <div class="d-grid mb-4">
            <button id="btnExecuteExport" class="btn btn-primary py-2 fw-bold" onclick="executeFolderExport()">
              <i class="bi bi-gear-wide-connected me-1"></i> [리그 ➡️ 팀 폴더 ➡️ 선수별 JSON 파일] 생성 시작
            </button>
          </div>

          <div id="exportResultArea" style="display: none;">
            <div class="alert alert-success d-flex justify-content-between align-items-center">
              <div>
                <i class="bi bi-check-circle-fill me-2 fs-5"></i>
                <span id="exportSuccessMsg">폴더 및 파일 생성이 완료되었습니다!</span>
              </div>
              <a id="btnDownloadZip" href="#" class="btn btn-success fw-bold">
                <i class="bi bi-file-earmark-zip-fill me-1"></i> ZIP 파일 다운로드
              </a>
            </div>

            <h6 class="fw-bold mb-2"><i class="bi bi-diagram-3-fill me-1"></i>생성된 팀별 / 선수별 파일 구조 (트리 뷰)</h6>
            <div class="border rounded p-3 bg-light" id="treeViewContainer" style="max-height: 250px; overflow-y: auto; font-family: monospace; font-size: 0.85rem;">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
"""

if "folderExportModal" not in html:
    html = html.replace("</body>", modal_html + "\n</body>")

# 자바스크립트 함수 추가
js_functions = """
    let folderModal = null;

    function openFolderExportModal() {
      if (!folderModal) {
        folderModal = new bootstrap.Modal(document.getElementById('folderExportModal'));
      }
      folderModal.show();
    }

    async function executeFolderExport() {
      const league = document.getElementById("modalExportLeague").value;
      const startDate = document.getElementById("modalStartDate").value;
      const endDate = document.getElementById("modalEndDate").value;
      const btn = document.getElementById("btnExecuteExport");

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> 팀/선수별 폴더 및 파일 생성 중...';

      try {
        const res = await fetch("/api/v1/content/export-folders", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ league_id: league, start_date: startDate, end_date: endDate })
        });
        const data = await res.json();

        document.getElementById("exportResultArea").style.display = "block";
        document.getElementById("exportSuccessMsg").textContent = data.message;
        document.getElementById("btnDownloadZip").href = data.download_url;

        // 트리 뷰 렌더링
        const manifest = data.export_details.manifest;
        let treeHtml = `<div class="fw-bold text-primary mb-2">📁 exports / ${manifest.league_id} / (${manifest.period.start_date} ~ ${manifest.period.end_date})</div>`;
        for (const [tName, tInfo] of Object.entries(manifest.teams)) {
          treeHtml += `
            <div class="ms-3 mb-2">
              <span class="fw-bold text-dark">📁 ${tName} /</span>
              <div class="ms-4 text-muted">
                <div>📄 team_info.json (${tInfo.matches_count}개 경기 요약)</div>
                <div>📁 matches/ (경기별 상세 내역 파일들)</div>
                <div>📁 players/ (${tInfo.players_count}명 선수별 상세 JSON 파일)</div>
              </div>
            </div>
          `;
        }
        document.getElementById("treeViewContainer").innerHTML = treeHtml;
      } catch (err) {
        alert("내보내기 중 오류 발생: " + err);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-gear-wide-connected me-1"></i> [리그 ➡️ 팀 폴더 ➡️ 선수별 JSON 파일] 생성 시작';
      }
    }
"""

if "openFolderExportModal" not in html:
    html = html.replace("</script>", js_functions + "\n</script>")

with open("app/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated index.html with folder export functionality!")