/**
 * TOKEON V2 Authentication & Access Management Module (auth_manager.js)
 * 별명, 나이, 비밀번호 간편 로그인 및 관리자 전용 비밀 접속 통계 관리
 */

const AuthManager = (() => {
  const STORAGE_KEY = 'tokeon_auth_user';
  let _loginModalInstance = null;
  let _adminModalInstance = null;

  function init() {
    renderHeaderState();
  }

  function getCurrentUser() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  }

  function renderHeaderState() {
    const container = document.getElementById('v2AuthHeaderContainer');
    if (!container) return;

    const user = getCurrentUser();
    if (user && user.nickname) {
      container.innerHTML = `
        <div class="d-flex align-items-center bg-dark bg-opacity-50 border border-secondary rounded px-2.5 py-1 text-white gap-1.5" style="font-size: 0.78rem;">
          <i class="bi bi-person-check-fill text-success"></i>
          <span class="fw-bold text-truncate" style="max-width: 110px;">${escapeHtml(user.nickname)}</span>
          <span class="badge bg-secondary text-white" style="font-size:0.65rem;">${user.age || 30}세</span>
          <button type="button" class="btn btn-sm btn-outline-light py-0 px-1.5 ms-1" onclick="AuthManager.logout()" style="font-size: 0.68rem; border-radius: 4px;" title="로그아웃">
            로그아웃
          </button>
        </div>
      `;

      // Auto prefill chat input
      const chatNick = document.getElementById('chatNickInput');
      if (chatNick) chatNick.value = user.nickname;
      const liveChatAuthor = document.getElementById('liveChatAuthor');
      if (liveChatAuthor) liveChatAuthor.value = user.nickname;
    } else {
      container.innerHTML = `
        <button type="button" class="btn btn-sm btn-warning text-dark fw-bold d-flex align-items-center gap-1 shadow-sm px-2.5 py-1" onclick="AuthManager.openLoginModal()" style="font-size: 0.78rem; border-radius: 6px;">
          <i class="bi bi-box-arrow-in-right"></i>
          <span>로그인</span>
        </button>
      `;
    }
  }

  function openLoginModal() {
    const modalEl = document.getElementById('v2LoginModal');
    if (!modalEl) return;

    // Reset inputs & alerts
    const alertBox = document.getElementById('loginAlertBox');
    if (alertBox) {
      alertBox.classList.add('d-none');
      alertBox.innerText = '';
    }

    const nickInput = document.getElementById('loginNickname');
    const ageInput = document.getElementById('loginAge');
    const pwInput = document.getElementById('loginPassword');

    const currentUser = getCurrentUser();
    if (currentUser) {
      if (nickInput) nickInput.value = currentUser.nickname || '';
      if (ageInput) ageInput.value = currentUser.age || 30;
    } else {
      if (pwInput) pwInput.value = '';
    }

    if (!_loginModalInstance) {
      _loginModalInstance = new bootstrap.Modal(modalEl);
    }
    _loginModalInstance.show();

    setTimeout(() => {
      if (nickInput) nickInput.focus();
    }, 300);
  }

  async function submitLogin() {
    const nickInput = document.getElementById('loginNickname');
    const ageInput = document.getElementById('loginAge');
    const pwInput = document.getElementById('loginPassword');
    const alertBox = document.getElementById('loginAlertBox');
    const btnSubmit = document.getElementById('btnLoginSubmit');

    const nickname = (nickInput && nickInput.value.trim()) || '';
    const age = parseInt((ageInput && ageInput.value) || '30', 10);
    const password = (pwInput && pwInput.value.trim()) || '';

    if (!nickname) {
      showAlert('별명(닉네임)을 입력해주세요.');
      if (nickInput) nickInput.focus();
      return;
    }
    if (!age || age < 1 || age > 120) {
      showAlert('올바른 나이(연령)를 입력해주세요 (1~120세).');
      if (ageInput) ageInput.focus();
      return;
    }
    if (!password) {
      showAlert('비밀번호를 입력해주세요.');
      if (pwInput) pwInput.focus();
      return;
    }

    if (btnSubmit) {
      btnSubmit.disabled = true;
      btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>로그인 중...';
    }

    try {
      const resp = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nickname: nickname,
          age: age,
          password: password
        })
      });

      const res = await resp.json();

      if (!resp.ok) {
        throw new Error(res.detail || '로그인에 실패했습니다.');
      }

      if (res.status === 'success' && res.user) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(res.user));
        renderHeaderState();

        if (_loginModalInstance) {
          _loginModalInstance.hide();
        }

        alert(`✅ ${res.message || '로그인되었습니다!'}`);
      } else {
        throw new Error(res.message || '로그인 처리 오류');
      }
    } catch (err) {
      showAlert(err.message || '로그인 중 오류가 발생했습니다.');
    } finally {
      if (btnSubmit) {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="bi bi-box-arrow-in-right me-1.5"></i>로그인 및 즉시 접속';
      }
    }
  }

  function showAlert(msg) {
    const alertBox = document.getElementById('loginAlertBox');
    if (alertBox) {
      alertBox.innerText = msg;
      alertBox.classList.remove('d-none');
    } else {
      alert(msg);
    }
  }

  function logout() {
    if (confirm('로그아웃 하시겠습니까?')) {
      localStorage.removeItem(STORAGE_KEY);
      renderHeaderState();
      alert('로그아웃 되었습니다.');
    }
  }

  async function openAdminModal() {
    const modalEl = document.getElementById('v2AdminAccessModal');
    if (!modalEl) return;

    if (!_adminModalInstance) {
      _adminModalInstance = new bootstrap.Modal(modalEl);
    }
    _adminModalInstance.show();

    const container = document.getElementById('adminAccessDataContainer');
    if (container) {
      container.innerHTML = `
        <div class="text-center py-4 text-muted small">
          <div class="spinner-border spinner-border-sm text-primary mb-2"></div>
          <div>비밀 접속자 현황 통계 불러오는 중...</div>
        </div>
      `;
    }

    try {
      const resp = await fetch('/api/v1/auth/admin/access-stats');
      if (!resp.ok) throw new Error('조회 실패');
      const data = await resp.json();

      const members = data.members || [];
      const logs = data.recent_logs || [];

      let rowsHtml = members.map((m, idx) => `
        <tr>
          <td class="font-monospace fw-bold text-secondary text-center">${idx + 1}</td>
          <td class="fw-bold text-dark text-start ps-2">${escapeHtml(m.nickname)}</td>
          <td class="text-center">${m.age}세</td>
          <td class="text-center font-monospace"><span class="badge bg-primary text-white fs-6 px-2 py-0.5">${m.login_count}회</span></td>
          <td class="text-center text-muted small">${m.registered_at || '-'}</td>
          <td class="text-center text-danger fw-bold small">${m.last_login_at || '-'}</td>
        </tr>
      `).join('');

      let logsHtml = logs.slice(0, 30).map(l => `
        <div class="d-flex justify-content-between align-items-center py-1 border-bottom" style="font-size:0.75rem;">
          <div>
            <span class="fw-bold text-dark me-1">${escapeHtml(l.nickname)}</span>
            <span class="badge bg-light text-secondary border me-1">${l.age || 30}세</span>
            <span class="badge bg-secondary text-white font-monospace">${l.login_count}회차 접속</span>
          </div>
          <div class="text-muted font-monospace">
            <span>${l.timestamp}</span>
            <span class="badge bg-light text-dark ms-1">IP: ${l.ip || '127.0.0.1'}</span>
          </div>
        </div>
      `).join('');

      if (container) {
        container.innerHTML = `
          <!-- Summary Cards -->
          <div class="row g-2 mb-3 text-center">
            <div class="col-4">
              <div class="p-2.5 rounded bg-light border">
                <div class="text-muted small">총 등록 회원</div>
                <div class="fw-bold fs-4 text-primary">${data.total_users}명</div>
              </div>
            </div>
            <div class="col-4">
              <div class="p-2.5 rounded bg-light border">
                <div class="text-muted small">누적 총 접속수</div>
                <div class="fw-bold fs-4 text-danger">${data.total_logins}회</div>
              </div>
            </div>
            <div class="col-4">
              <div class="p-2.5 rounded bg-light border">
                <div class="text-muted small">보안 기록 파일</div>
                <div class="fw-bold small text-success">자동 백업 보존</div>
              </div>
            </div>
          </div>

          <!-- Members Table -->
          <div class="fw-bold text-dark mb-1.5" style="font-size:0.85rem;">
            <i class="bi bi-people-fill text-primary me-1"></i>회원별 접속 횟수 & 최근 활동 순위
          </div>
          <div class="table-responsive mb-3 border rounded bg-white" style="max-height: 280px; overflow-y: auto;">
            <table class="table table-bordered table-sm table-hover mb-0" style="font-size: 0.76rem;">
              <thead class="table-dark sticky-top">
                <tr>
                  <th style="width: 45px;" class="text-center">순번</th>
                  <th style="min-width: 110px;" class="text-center">별명 (닉네임)</th>
                  <th style="width: 65px;" class="text-center">나이</th>
                  <th style="width: 85px;" class="text-center">총접속횟수</th>
                  <th style="min-width: 120px;" class="text-center">가입일시</th>
                  <th style="min-width: 120px;" class="text-center">최근접속일시</th>
                </tr>
              </thead>
              <tbody>
                ${rowsHtml || '<tr><td colspan="6" class="text-center py-3 text-muted">등록된 회원이 없습니다.</td></tr>'}
              </tbody>
            </table>
          </div>

          <!-- Recent Access Logs -->
          <div class="fw-bold text-dark mb-1.5" style="font-size:0.85rem;">
            <i class="bi bi-clock-history text-danger me-1"></i>실시간 개별 로그인 타임라인 로그 (최근 30건)
          </div>
          <div class="p-2.5 rounded bg-white border" style="max-height: 220px; overflow-y: auto;">
            ${logsHtml || '<div class="text-muted small text-center py-2">접속 로그가 없습니다.</div>'}
          </div>
        `;
      }
    } catch (e) {
      if (container) {
        container.innerHTML = `<div class="alert alert-danger small py-2">접속 통계 로딩 오류: ${e.message}</div>`;
      }
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  return {
    init,
    getCurrentUser,
    openLoginModal,
    submitLogin,
    logout,
    openAdminModal
  };
})();
