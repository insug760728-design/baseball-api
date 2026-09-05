# -*- coding: utf-8 -*-
import os

html_code = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SPORTIX PRO — 글로벌 3대 스포츠 실시간 소식 & 세이버메트릭스 포털</title>
  <!-- Bootstrap 5.3 & Icons -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <!-- Google Fonts: Pretendard / Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-main: #0a0e1a;
      --bg-card: #121829;
      --bg-card-hover: #18223a;
      --bg-panel: #0d1322;
      --border-color: #1e293b;
      --border-light: #2d3b55;
      --accent-blue: #38bdf8;
      --accent-green: #10b981;
      --accent-amber: #f59e0b;
      --accent-purple: #a855f7;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: 'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow-x: hidden;
      line-height: 1.6;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    ::-webkit-scrollbar-track {
      background: var(--bg-main);
    }
    ::-webkit-scrollbar-thumb {
      background: #27354f;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #38bdf8;
    }

    /* Navbar */
    .navbar-glass {
      background: rgba(10, 14, 26, 0.85);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 1000;
      transition: all 0.3s ease;
    }
    .nav-brand-title {
      font-weight: 800;
      font-size: 1.35rem;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, #ffffff 30%, #38bdf8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .nav-link-custom {
      color: var(--text-muted);
      font-size: 0.95rem;
      font-weight: 500;
      padding: 0.5rem 0.9rem;
      transition: color 0.2s ease;
      text-decoration: none;
    }
    .nav-link-custom:hover {
      color: var(--accent-blue);
    }

    /* Live Breaking News Marquee */
    .breaking-ticker {
      background: #0f172a;
      border-bottom: 1px solid var(--border-color);
      padding: 8px 0;
      overflow: hidden;
      font-size: 0.88rem;
    }
    .ticker-wrap {
      display: flex;
      align-items: center;
    }
    .ticker-badge {
      background: #ef4444;
      color: white;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 4px;
      white-space: nowrap;
      margin-right: 15px;
      letter-spacing: 0.5px;
      animation: pulseGlow 2s infinite;
    }
    @keyframes pulseGlow {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.75; }
    }
    .ticker-content {
      display: inline-block;
      white-space: nowrap;
      animation: marquee 35s linear infinite;
    }
    .ticker-content:hover {
      animation-play-state: paused;
    }
    @keyframes marquee {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }
    .ticker-item {
      display: inline-block;
      margin-right: 40px;
      color: #cbd5e1;
      cursor: pointer;
    }
    .ticker-item:hover {
      color: var(--accent-blue);
      text-decoration: underline;
    }

    /* Hero Section */
    .hero-section {
      padding: 4rem 0 3rem 0;
      position: relative;
      background: radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.08) 0%, transparent 50%),
                  radial-gradient(circle at 20% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
    }
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--accent-blue);
      font-size: 0.85rem;
      font-weight: 600;
      padding: 5px 14px;
      border-radius: 9999px;
      margin-bottom: 1.5rem;
    }
    .hero-title {
      font-size: 3rem;
      font-weight: 800;
      line-height: 1.25;
      letter-spacing: -1px;
      margin-bottom: 1.25rem;
    }
    .hero-desc {
      font-size: 1.15rem;
      color: var(--text-muted);
      line-height: 1.7;
      margin-bottom: 2rem;
      max-width: 620px;
    }
    .btn-gradient {
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
      color: white;
      font-weight: 600;
      padding: 0.75rem 1.6rem;
      border-radius: 10px;
      border: none;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
      transition: all 0.2s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .btn-gradient:hover {
      background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
      color: white;
    }
    .btn-outline-glass {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      font-weight: 600;
      padding: 0.75rem 1.6rem;
      border-radius: 10px;
      transition: all 0.2s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .btn-outline-glass:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: #475569;
      color: white;
    }

    /* Featured Story Card */
    .featured-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      overflow: hidden;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
      cursor: pointer;
    }
    .featured-card:hover {
      transform: translateY(-5px);
      border-color: rgba(56, 189, 248, 0.5);
      box-shadow: 0 20px 40px -15px rgba(56, 189, 248, 0.2);
    }
    .featured-img-wrap {
      height: 240px;
      background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    .featured-img-icon {
      font-size: 5rem;
      opacity: 0.15;
      position: absolute;
      right: 20px;
      bottom: -10px;
    }
    .featured-badge-top {
      position: absolute;
      top: 16px;
      left: 16px;
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(8px);
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Live Match Center Strip */
    .match-strip-section {
      padding: 2.5rem 0;
      background: var(--bg-panel);
      border-top: 1px solid var(--border-color);
      border-bottom: 1px solid var(--border-color);
    }
    .strip-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 14px 16px;
      min-width: 250px;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .strip-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent-blue);
      transform: translateY(-2px);
    }
    .strip-league {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .strip-score {
      font-size: 1.25rem;
      font-weight: 800;
      color: #fff;
    }
    .strip-team {
      font-weight: 600;
      font-size: 0.92rem;
      color: #e2e8f0;
    }

    /* News Cards */
    .news-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      overflow: hidden;
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
      height: 100%;
      cursor: pointer;
    }
    .news-card:hover {
      background: var(--bg-card-hover);
      border-color: #3b82f6;
      transform: translateY(-4px);
      box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.5);
    }
    .news-header-bg {
      height: 140px;
      position: relative;
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .bg-baseball { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-bottom: 2px solid #3b82f6; }
    .bg-soccer { background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%); border-bottom: 2px solid #10b981; }
    .bg-basketball { background: linear-gradient(135deg, #78350f 0%, #0f172a 100%); border-bottom: 2px solid #f59e0b; }
    .bg-analytics { background: linear-gradient(135deg, #581c87 0%, #0f172a 100%); border-bottom: 2px solid #a855f7; }

    .news-body {
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }
    .news-title {
      font-size: 1.1rem;
      font-weight: 700;
      line-height: 1.45;
      margin-bottom: 0.75rem;
      color: #f1f5f9;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .news-desc {
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      flex-grow: 1;
    }
    .data-chip {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--border-color);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--accent-blue);
    }

    /* Category Filter Tabs */
    .filter-btn {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 0.9rem;
      font-weight: 600;
      padding: 8px 18px;
      border-radius: 8px;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .filter-btn:hover, .filter-btn.active {
      background: #2563eb;
      color: white;
      border-color: #2563eb;
    }

    /* Analytics Showcase */
    .analytics-section {
      padding: 5rem 0;
      background: radial-gradient(circle at 50% 50%, rgba(30, 41, 59, 0.5) 0%, var(--bg-main) 100%);
    }
    .metric-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.8rem;
      height: 100%;
      transition: all 0.3s ease;
    }
    .metric-card:hover {
      border-color: var(--accent-blue);
      transform: translateY(-4px);
    }
    .metric-icon-wrap {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      margin-bottom: 1.25rem;
    }

    /* Pricing Plans */
    .pricing-section {
      padding: 5rem 0;
      border-top: 1px solid var(--border-color);
      background: linear-gradient(180deg, var(--bg-main) 0%, #0d1424 100%);
    }
    .pricing-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 2.5rem 2rem;
      height: 100%;
      position: relative;
      transition: all 0.3s ease;
      display: flex;
      flex-direction: column;
    }
    .pricing-card.popular {
      border: 2px solid #3b82f6;
      background: linear-gradient(180deg, #162038 0%, #121829 100%);
      box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.3);
    }
    .pricing-card:hover {
      transform: translateY(-5px);
    }
    .pricing-price {
      font-size: 2.5rem;
      font-weight: 800;
      color: #fff;
      margin: 1.25rem 0;
    }
    .pricing-features {
      list-style: none;
      padding: 0;
      margin: 1.5rem 0 2rem 0;
      flex-grow: 1;
    }
    .pricing-features li {
      padding: 8px 0;
      font-size: 0.92rem;
      color: #cbd5e1;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    /* Footer */
    .footer-section {
      background: #070a12;
      border-top: 1px solid var(--border-color);
      padding: 4rem 0 2rem 0;
      color: var(--text-dim);
      font-size: 0.88rem;
    }
    .footer-link {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.2s ease;
    }
    .footer-link:hover {
      color: var(--accent-blue);
    }

    /* Custom Modal */
    .modal-content-custom {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      color: var(--text-main);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    .modal-header-custom {
      border-bottom: 1px solid var(--border-color);
      padding: 1.25rem 1.75rem;
    }
    .modal-footer-custom {
      border-top: 1px solid var(--border-color);
      padding: 1rem 1.75rem;
    }
  </style>
</head>
<body>

  <!-- Top Navbar -->
  <nav class="navbar navbar-expand-lg navbar-glass">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" href="#">
        <div style="background: linear-gradient(135deg, #0284c7, #2563eb); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
          <i class="bi bi-lightning-charge-fill text-white fs-5"></i>
        </div>
        <span class="nav-brand-title">SPORTIX PRO</span>
      </a>

      <!-- Sync Status Badge -->
      <div class="d-none d-md-flex align-items-center gap-2 ms-3 px-3 py-1" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9999px;">
        <span style="width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; animation: pulseGlow 1.5s infinite;"></span>
        <span style="font-size: 0.78rem; font-weight: 700; color: #10b981;">3대 스포츠 259경기 실시간 동기화 LIVE</span>
      </div>

      <button class="navbar-toggler border-0 text-white" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
        <i class="bi bi-list fs-2"></i>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navMenu">
        <ul class="navbar-nav align-items-center gap-1 my-2 my-lg-0">
          <li class="nav-item"><a class="nav-link-custom" href="#news-section"><i class="bi bi-newspaper me-1"></i>스포츠 뉴스</a></li>
          <li class="nav-item"><a class="nav-link-custom" href="#match-strip"><i class="bi bi-broadcast me-1"></i>라이브 스코어</a></li>
          <li class="nav-item"><a class="nav-link-custom" href="#analytics-section"><i class="bi bi-cpu me-1"></i>세이버메트릭스 랩</a></li>
          <li class="nav-item"><a class="nav-link-custom" href="#pricing-section"><i class="bi bi-currency-dollar me-1"></i>API 요금제</a></li>
          <li class="nav-item ms-lg-2">
            <button class="btn btn-sm btn-outline-glass" onclick="openApiKeyModal()">
              <i class="bi bi-key-fill text-warning me-1"></i>API 키 발급
            </button>
          </li>
          <li class="nav-item ms-lg-2">
            <a href="/dashboard" class="btn btn-sm btn-gradient">
              <i class="bi bi-speedometer2 me-1"></i>데이터 관리 콘솔
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- 실시간 속보 전광판 Ticker -->
  <div class="breaking-ticker">
    <div class="container d-flex align-items-center">
      <span class="ticker-badge"><i class="bi bi-broadcast-pin me-1"></i>BREAKING NEWS</span>
      <div style="overflow: hidden; width: 100%;">
        <div class="ticker-content" id="tickerItems">
          <!-- Dynamically Injected Marquee Items -->
          <span class="ticker-item" onclick="openArticleModal(1)">⚾ [MLB] 오타니 쇼헤이, wOBA .425 돌파하며 50-50 대기록 가시권 진입</span>
          <span class="ticker-item" onclick="openArticleModal(2)">⚽ [EPL] 손흥민, 기대 어시스트(xA) 0.82 폭발하며 토트넘 역전승 견인</span>
          <span class="ticker-item" onclick="openArticleModal(3)">🏀 [NBA] 요키치, TS% 72.8%로 덴버 공격 지휘... GameScore 32.4 경신</span>
          <span class="ticker-item" onclick="openArticleModal(4)">⚾ [KBO] 가을야구 불펜 대전, 평균 FIP 2.45 팀이 승률 78% 기록</span>
          <span class="ticker-item" onclick="openArticleModal(5)">⚽ [LALIGA] 레알 마드리드, xGOT 2.18로 엘 클라시코 화력전 완승</span>
          <span class="ticker-item" onclick="openArticleModal(6)">🏀 [NBA] 현대 농구의 정수 'Pace와 eFG%'... 3점슛과 공격 템포 심층 분석</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container">
      <div class="row align-items-center g-5">
        <div class="col-lg-7">
          <div class="hero-badge">
            <i class="bi bi-stars"></i> 차세대 스포츠 미디어 & 데이터 인텔리전스
          </div>
          <h1 class="hero-title">
            스포츠를 읽는 가장 완벽한 시선,<br>
            <span style="background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
              실시간 속보 & 세이버메트릭스
            </span>
          </h1>
          <p class="hero-desc">
            야구(MLB·KBO·NPB), 유럽 축구 5대 리그(EPL·라리가·분데스리가·세리에A·리그1), 농구(NBA)의 
            생생한 현장 소식과 <b>xG, wOBA, Pace</b> 등 첨단 계량 통계 API를 단 하나의 포털에서 만나보세요.
          </p>
          <div class="d-flex flex-wrap gap-3">
            <a href="#news-section" class="btn btn-gradient">
              <i class="bi bi-newspaper"></i> 최신 스포츠 소식 브리핑
            </a>
            <a href="#pricing-section" class="btn btn-outline-glass">
              <i class="bi bi-code-slash"></i> 상용 API 플랜 둘러보기
            </a>
            <a href="/dashboard" class="btn btn-outline-glass text-warning border-warning">
              <i class="bi bi-database-fill"></i> 데이터 관리자 콘솔
            </a>
          </div>

          <!-- Feature Metric Highlights -->
          <div class="row mt-5 pt-3 g-4 border-top" style="border-color: var(--border-color) !important;">
            <div class="col-4">
              <div class="fs-4 fw-bold text-white">259<span style="color: var(--accent-blue);">+</span></div>
              <div class="text-muted" style="font-size: 0.85rem;">실시간 집계 경기</div>
            </div>
            <div class="col-4">
              <div class="fs-4 fw-bold text-white">9<span style="color: var(--accent-green);">개</span></div>
              <div class="text-muted" style="font-size: 0.85rem;">글로벌 프로 리그</div>
            </div>
            <div class="col-4">
              <div class="fs-4 fw-bold text-white">3·5·7·10<span style="color: var(--accent-amber);">D/G</span></div>
              <div class="text-muted" style="font-size: 0.85rem;">정밀 롤링 트렌드</div>
            </div>
          </div>
        </div>

        <!-- Featured Headline Right Card -->
        <div class="col-lg-5">
          <div class="featured-card" onclick="openArticleModal(1)">
            <div class="featured-img-wrap">
              <span class="featured-badge-top"><i class="bi bi-lightning-charge-fill me-1"></i>TOP HEADLINE</span>
              <i class="bi bi-trophy-fill featured-img-icon"></i>
              <div class="p-4 text-center z-1">
                <span class="badge bg-primary px-3 py-1 mb-2">⚾ MLB 메이저리그</span>
                <h4 class="fw-bold text-white mb-0">오타니 쇼헤이, 전인미답 50-50 신기록 초읽기</h4>
              </div>
            </div>
            <div class="p-4">
              <p class="text-muted mb-3" style="font-size: 0.92rem; line-height: 1.6;">
                단순 홈런과 도루 개수를 넘어 <b>wOBA .425</b>와 <b>wRC+ 182</b>라는 경이적인 생산력을 기록 중인 오타니의 실시간 세이버메트릭스 정밀 분석 리포트.
              </p>
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="data-chip"><i class="bi bi-graph-up me-1"></i>wOBA .425</span>
                <span class="data-chip"><i class="bi bi-fire me-1"></i>wRC+ 182</span>
                <span class="data-chip"><i class="bi bi-check2-circle me-1"></i>OPS 1.034</span>
              </div>
              <div class="d-flex justify-content-between align-items-center pt-2 border-top" style="border-color: var(--border-color) !important;">
                <span class="text-dim" style="font-size: 0.82rem;"><i class="bi bi-person-fill me-1"></i>스포허브 데이터랩 · 방금 전</span>
                <span class="text-info fw-semibold" style="font-size: 0.85rem;">기사 전문 읽기 <i class="bi bi-arrow-right"></i></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Live Match Center Strip -->
  <section class="match-strip-section" id="match-strip">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
          <span style="width: 10px; height: 10px; background-color: #ef4444; border-radius: 50%; display: inline-block; animation: pulseGlow 1.2s infinite;"></span>
          <h5 class="fw-bold mb-0 text-white"><i class="bi bi-broadcast me-1 text-danger"></i>실시간 경기 센터 (Live Match Center)</h5>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-secondary py-0 px-2 active" id="stripBtnALL" onclick="filterStrip('ALL')">전체</button>
          <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="stripBtnBASEBALL" onclick="filterStrip('BASEBALL')">⚾ 야구</button>
          <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="stripBtnSOCCER" onclick="filterStrip('SOCCER')">⚽ 축구</button>
          <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="stripBtnBASKETBALL" onclick="filterStrip('BASKETBALL')">🏀 농구</button>
        </div>
      </div>

      <!-- Match Horizontal Slider -->
      <div class="d-flex gap-3 overflow-auto pb-2" id="stripContainer" style="scrollbar-width: thin;">
        <!-- Loading Placeholder -->
        <div class="text-muted p-3">실시간 경기 스코어보드 데이터를 불러오는 중...</div>
      </div>
    </div>
  </section>

  <!-- Sports News & Editorial Magazine -->
  <section class="py-5" id="news-section">
    <div class="container">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4 pb-2 border-bottom" style="border-color: var(--border-color) !important;">
        <div>
          <span class="text-primary fw-bold text-uppercase" style="font-size: 0.82rem; letter-spacing: 1px;">Editorial & Insights</span>
          <h2 class="fw-bold text-white mb-1"><i class="bi bi-newspaper me-2 text-primary"></i>스포츠 뉴스 & 심층 분석</h2>
          <p class="text-muted mb-0" style="font-size: 0.95rem;">현장감 넘치는 경기 소식과 첨단 데이터가 결합된 프리미엄 스포츠 리포트</p>
        </div>

        <!-- Action Buttons: Filter + Post News -->
        <div class="d-flex flex-wrap gap-2 align-items-center">
          <button class="filter-btn active" onclick="filterNews('ALL', this)">전체 소식</button>
          <button class="filter-btn" onclick="filterNews('BASEBALL', this)">⚾ 야구</button>
          <button class="filter-btn" onclick="filterNews('SOCCER', this)">⚽ 축구</button>
          <button class="filter-btn" onclick="filterNews('BASKETBALL', this)">🏀 농구</button>
          <button class="filter-btn" onclick="filterNews('ANALYTICS', this)">📊 데이터 칼럼</button>
          <button class="btn btn-sm btn-success ms-md-2" onclick="openPostNewsModal()">
            <i class="bi bi-pencil-square me-1"></i>새 소식 작성
          </button>
        </div>
      </div>

      <!-- News Cards Grid -->
      <div class="row g-4" id="newsGrid">
        <!-- Rendered by JavaScript -->
      </div>
    </div>
  </section>

  <!-- Advanced Sabermetrics Lab Showcase -->
  <section class="analytics-section" id="analytics-section">
    <div class="container">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-info text-dark px-3 py-1 fw-bold mb-2">PRECISION SABERMETRICS LAB</span>
        <h2 class="fw-bold text-white mb-3">스포츠의 본질을 꿰뚫는 첨단 세이버메트릭스 엔진</h2>
        <p class="text-muted">
          단순 득점과 승패를 넘어, 경기 흐름과 선수의 실질적 가치를 증명하는 현대 스포츠 최고 수준의 계량 분석 모델을 제공합니다.
        </p>
      </div>

      <div class="row g-4">
        <!-- Baseball Metrics -->
        <div class="col-md-4">
          <div class="metric-card">
            <div class="metric-icon-wrap" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
              <i class="bi bi-baseball"></i>
            </div>
            <h4 class="fw-bold text-white mb-2">⚾ 야구 (Baseball)</h4>
            <p class="text-muted" style="font-size: 0.9rem;">MLB · KBO · NPB 타자 및 투수 가치 계량화</p>
            <hr style="border-color: var(--border-color);">
            <ul class="list-unstyled text-secondary mb-0" style="font-size: 0.88rem; line-height: 2;">
              <li><strong class="text-white">wOBA:</strong> 가중 출루율 (안타 종류별 득점 기여도 산출)</li>
              <li><strong class="text-white">wRC+:</strong> 파크팩터와 리그 평균(100) 보정 득점 창출력</li>
              <li><strong class="text-white">FIP / xFIP:</strong> 수비 독립 평균자책점 (삼진, 볼넷, 홈런)</li>
              <li><strong class="text-white">BABIP / ISO:</strong> 인플레이 타구 타율 및 순수 장타율</li>
            </ul>
          </div>
        </div>

        <!-- Soccer Metrics -->
        <div class="col-md-4">
          <div class="metric-card">
            <div class="metric-icon-wrap" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">
              <i class="bi bi-dribbble"></i>
            </div>
            <h4 class="fw-bold text-white mb-2">⚽ 축구 (Soccer)</h4>
            <p class="text-muted" style="font-size: 0.9rem;">유럽 5대 리그 기대 수치 및 압박 강도 모델링</p>
            <hr style="border-color: var(--border-color);">
            <ul class="list-unstyled text-secondary mb-0" style="font-size: 0.88rem; line-height: 2;">
              <li><strong class="text-white">xG / xA:</strong> 기대 득점 및 키패스 기반 기대 어시스트</li>
              <li><strong class="text-white">xGOT:</strong> 골키퍼에게 도달한 유효슈팅 궤적 위험도</li>
              <li><strong class="text-white">PPDA:</strong> 전방 압박 강도 (수비 동작당 상대 허용 패스)</li>
              <li><strong class="text-white">Field Tilt %:</strong> 상대 진영 Final Third 점유 지배율</li>
            </ul>
          </div>
        </div>

        <!-- Basketball Metrics -->
        <div class="col-md-4">
          <div class="metric-card">
            <div class="metric-icon-wrap" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">
              <i class="bi bi-bullseye"></i>
            </div>
            <h4 class="fw-bold text-white mb-2">🏀 농구 (Basketball)</h4>
            <p class="text-muted" style="font-size: 0.9rem;">NBA 공수 포제션 효율 및 종합 지배력 지수</p>
            <hr style="border-color: var(--border-color);">
            <ul class="list-unstyled text-secondary mb-0" style="font-size: 0.88rem; line-height: 2;">
              <li><strong class="text-white">Pace:</strong> 48분 환산 경기당 공수 점유권(Possessions)</li>
              <li><strong class="text-white">ORtg / DRtg:</strong> 100회 포제션당 득점/실점 효율성</li>
              <li><strong class="text-white">eFG% / TS%:</strong> 3점슛 가중치 및 자유투 합산 트루 슈팅율</li>
              <li><strong class="text-white">Game Score:</strong> John Hollinger 종합 경기 영향력 지수</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Commercial API Pricing Plans -->
  <section class="pricing-section" id="pricing-section">
    <div class="container">
      <div class="text-center max-w-700 mx-auto mb-5">
        <span class="badge bg-warning text-dark px-3 py-1 fw-bold mb-2">COMMERCIAL API & PRICING</span>
        <h2 class="fw-bold text-white mb-3">비즈니스 맞춤형 프로페셔널 스포츠 API</h2>
        <p class="text-muted">
          스포츠 미디어, 데이터 스타트업, 스포츠 팬 커뮤니티, 전문 분석가를 위한 완벽한 RESTful API 구독 플랜
        </p>
      </div>

      <div class="row g-4 justify-content-center">
        <!-- Starter Plan -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card">
            <h4 class="fw-bold text-white mb-1">Free Starter</h4>
            <p class="text-muted" style="font-size: 0.88rem;">데이터 연동 테스트 및 개인 개발자</p>
            <div class="pricing-price">₩0 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 평생 무료</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> 일일 500회 호출 한도</li>
              <li><i class="bi bi-check2 text-success"></i> 야구/축구/농구 기본 스코어보드</li>
              <li><i class="bi bi-check2 text-success"></i> 경기 일정 및 최종 결과 조회</li>
              <li><i class="bi bi-check2 text-success"></i> 오픈 개발자 커뮤니티 지원</li>
              <li class="text-dim"><i class="bi bi-x text-secondary"></i> 세이버메트릭스 지표 미지원</li>
              <li class="text-dim"><i class="bi bi-x text-secondary"></i> 롤링 트렌드 및 ZIP 미지원</li>
            </ul>
            <button class="btn btn-outline-glass w-100 py-2 mt-auto" onclick="selectPlan('Free')">
              무료 플랜 시작하기
            </button>
          </div>
        </div>

        <!-- Pro Analyst Plan (Popular) -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card popular">
            <span class="position-absolute top-0 start-50 translate-middle badge bg-primary px-3 py-2 fw-bold" style="letter-spacing: 0.5px;">
              🔥 가장 인기 있는 플랜 (추천)
            </span>
            <h4 class="fw-bold text-white mb-1">Pro Analyst</h4>
            <p class="text-muted" style="font-size: 0.88rem;">스포츠 미디어, 블로거 & 전문 애널리스트</p>
            <div class="pricing-price">₩29,000 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 월 (VAT 포함)</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> <strong>일일 50,000회 고속 호출</strong></li>
              <li><i class="bi bi-check2 text-success"></i> <strong>3대 종목 첨단 세이버메트릭스 전체</strong> (xG, wOBA, Pace 등)</li>
              <li><i class="bi bi-check2 text-success"></i> <strong>3·5·7·10G/D 롤링 트렌드 API</strong></li>
              <li><i class="bi bi-check2 text-success"></i> <strong>구단/포지션별 정밀 JSON/ZIP 일괄 다운로드</strong></li>
              <li><i class="bi bi-check2 text-success"></i> 초당 20 RPS 속도 보장</li>
              <li><i class="bi bi-check2 text-success"></i> 이메일 기술 지원 & 최신 스키마 가이드</li>
            </ul>
            <button class="btn btn-gradient w-100 py-2 mt-auto" onclick="selectPlan('Pro')">
              Pro 플랜 지금 시작하기
            </button>
          </div>
        </div>

        <!-- Enterprise Plan -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card">
            <h4 class="fw-bold text-white mb-1">Enterprise</h4>
            <p class="text-muted" style="font-size: 0.88rem;">기업 고객, 대형 미디어 & 데이터 플랫폼</p>
            <div class="pricing-price">₩199,000 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 월 협의</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> <strong>무제한 호출 전용 회선</strong></li>
              <li><i class="bi bi-check2 text-success"></i> 99.9% 가용성 보장 SLA</li>
              <li><i class="bi bi-check2 text-success"></i> <strong>실시간 WebSocket 스코어 스트리밍 피드</strong></li>
              <li><i class="bi bi-check2 text-success"></i> 상업적 재배포 라이선스 부여</li>
              <li><i class="bi bi-check2 text-success"></i> 맞춤형 지표/알고리즘 커스텀 개발</li>
              <li><i class="bi bi-check2 text-success"></i> 전담 엔지니어 1:1 핫라인 지원</li>
            </ul>
            <button class="btn btn-outline-glass w-100 py-2 mt-auto" onclick="selectPlan('Enterprise')">
              기업 도입 문의하기
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer with Legal & Business Information -->
  <footer class="footer-section">
    <div class="container">
      <div class="row g-4 mb-4">
        <div class="col-lg-5">
          <div class="d-flex align-items-center gap-2 mb-3">
            <div style="background: linear-gradient(135deg, #0284c7, #2563eb); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
              <i class="bi bi-lightning-charge-fill text-white fs-6"></i>
            </div>
            <span class="fs-5 fw-bold text-white">SPORTIX PRO</span>
          </div>
          <p class="text-muted mb-3" style="line-height: 1.6; max-width: 420px;">
            글로벌 3대 스포츠(야구, 축구, 농구) 실시간 소식 및 세이버메트릭스 데이터 인텔리전스를 공급하는 전문 스포츠 테크 플랫폼입니다.
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="text-muted fs-5"><i class="bi bi-github"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-envelope-fill"></i></a>
          </div>
        </div>

        <div class="col-lg-2 col-6">
          <h6 class="fw-bold text-white mb-3">서비스 바로가기</h6>
          <ul class="list-unstyled d-flex flex-column gap-2" style="font-size: 0.88rem;">
            <li><a href="#news-section" class="footer-link">스포츠 뉴스</a></li>
            <li><a href="#match-strip" class="footer-link">라이브 스코어</a></li>
            <li><a href="#analytics-section" class="footer-link">세이버메트릭스</a></li>
            <li><a href="#pricing-section" class="footer-link">API 요금제</a></li>
            <li><a href="/dashboard" class="footer-link text-warning fw-semibold">관리자 대시보드</a></li>
          </ul>
        </div>

        <div class="col-lg-2 col-6">
          <h6 class="fw-bold text-white mb-3">지원 종목/리그</h6>
          <ul class="list-unstyled d-flex flex-column gap-2" style="font-size: 0.88rem;">
            <li><span class="text-muted">MLB / KBO / NPB</span></li>
            <li><span class="text-muted">EPL (프리미어리그)</span></li>
            <li><span class="text-muted">라리가 / 분데스리가</span></li>
            <li><span class="text-muted">세리에A / 리그1</span></li>
            <li><span class="text-muted">NBA (프로농구)</span></li>
          </ul>
        </div>

        <div class="col-lg-3">
          <h6 class="fw-bold text-white mb-3">사업자 등록 정보</h6>
          <div class="text-muted" style="font-size: 0.82rem; line-height: 1.8;">
            <div><strong>상호명:</strong> 스포틱스 코리아 (SPORTIX PRO)</div>
            <div><strong>사업자등록번호:</strong> 000-00-00000</div>
            <div><strong>통신판매업신고:</strong> 제2026-서울강남-0000호</div>
            <div><strong>대표자:</strong> 서비스 운영자</div>
            <div><strong>고객센터:</strong> support@sportix.pro</div>
            <div><strong>소재지:</strong> 서울특별시 강남구 테헤란로</div>
          </div>
        </div>
      </div>

      <div class="pt-3 mt-3 border-top d-flex flex-column flex-md-row justify-content-between align-items-center gap-2" style="border-color: var(--border-color) !important;">
        <div style="font-size: 0.8rem; color: var(--text-dim);">
          © 2026 SPORTIX PRO. All rights reserved. 본 서비스에서 제공하는 모든 경기 데이터와 계량 지표의 저작권은 당사에 있습니다.
        </div>
        <div class="d-flex gap-3" style="font-size: 0.8rem;">
          <a href="#" class="footer-link">이용약관</a>
          <a href="#" class="footer-link">개인정보처리방침</a>
          <a href="#" class="footer-link">API 서비스 규약</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- Modal 1: Article Reader Modal -->
  <div class="modal fade" id="articleModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content modal-content-custom">
        <div class="modal-header modal-header-custom d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-primary" id="modalCategory">⚾ 야구</span>
            <span class="text-muted" style="font-size: 0.85rem;" id="modalDate">2026-09-05</span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <h3 class="fw-bold text-white mb-3" id="modalTitle">기사 제목</h3>
          <div class="d-flex align-items-center gap-2 text-muted mb-4 pb-3 border-bottom" style="border-color: var(--border-color) !important; font-size: 0.88rem;">
            <span><i class="bi bi-person-circle me-1"></i><strong id="modalAuthor">스포허브 분석팀</strong></span>
            <span>•</span>
            <span id="modalSource">스포틱스 공식 데스크</span>
          </div>

          <!-- Featured Data Card inside Modal -->
          <div class="p-3 mb-4 rounded-3" style="background: var(--bg-panel); border: 1px solid var(--border-color);" id="modalDataBox">
            <div class="d-flex align-items-center gap-2 mb-2">
              <i class="bi bi-graph-up text-info"></i>
              <strong class="text-white" style="font-size: 0.92rem;">연계 세이버메트릭스 데이터 인사이트</strong>
            </div>
            <div class="d-flex flex-wrap gap-2" id="modalChips">
              <!-- Chips -->
            </div>
          </div>

          <!-- Article Text Content -->
          <div class="text-light" style="font-size: 1rem; line-height: 1.8;" id="modalContent">
            기사 본문 내용
          </div>
        </div>
        <div class="modal-footer modal-footer-custom d-flex justify-content-between">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">닫기</button>
          <a href="/dashboard" class="btn btn-primary btn-sm">
            <i class="bi bi-speedometer2 me-1"></i>관련 경기 데이터 센터 바로가기
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 2: Post News Article Modal -->
  <div class="modal fade" id="postNewsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-content-custom">
        <div class="modal-header modal-header-custom">
          <h5 class="modal-title fw-bold text-white"><i class="bi bi-pencil-square text-success me-2"></i>새 스포츠 소식 / 칼럼 등록</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <form id="postNewsForm">
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">종목 카테고리</label>
              <select class="form-select bg-dark text-white border-secondary" id="newCategory">
                <option value="BASEBALL">⚾ 야구 (MLB/KBO/NPB)</option>
                <option value="SOCCER">⚽ 축구 (유럽 5대리그)</option>
                <option value="BASKETBALL">🏀 농구 (NBA)</option>
                <option value="ANALYTICS">📊 데이터 칼럼 & 세이버메트릭스</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">기사 제목</label>
              <input type="text" class="form-control bg-dark text-white border-secondary" id="newTitle" placeholder="헤드라인을 입력하세요" required>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label text-muted" style="font-size: 0.88rem;">작성자 / 부서</label>
                <input type="text" class="form-control bg-dark text-white border-secondary" id="newAuthor" value="스포츠 데스크" required>
              </div>
              <div class="col-6">
                <label class="form-label text-muted" style="font-size: 0.88rem;">데이터 태그 (쉼표 구분)</label>
                <input type="text" class="form-control bg-dark text-white border-secondary" id="newTags" placeholder="wOBA .410, xG 2.1">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">기사 요약 (1~2줄)</label>
              <input type="text" class="form-control bg-dark text-white border-secondary" id="newDesc" placeholder="기사의 핵심 요약" required>
            </div>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">기사 본문</label>
              <textarea class="form-control bg-dark text-white border-secondary" id="newContent" rows="5" placeholder="기사 상세 내용을 작성하세요" required></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer modal-footer-custom">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">취소</button>
          <button type="button" class="btn btn-success btn-sm" onclick="saveNewArticle()">
            <i class="bi bi-check-lg me-1"></i>소식 즉시 발행하기
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 3: API Key & Subscription Modal -->
  <div class="modal fade" id="apiKeyModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-content-custom">
        <div class="modal-header modal-header-custom">
          <h5 class="modal-title fw-bold text-white"><i class="bi bi-key-fill text-warning me-2"></i>SPORTIX 개발자 API 키 발급 & 플랜</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <div id="keyFormStep">
            <p class="text-muted" style="font-size: 0.9rem;">
              원하시는 플랜을 선택하고 이메일을 등록하시면 <strong>즉시 유효한 개발자 테스트 API Key</strong>가 발급됩니다.
            </p>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">선택 플랜</label>
              <select class="form-select bg-dark text-white border-secondary" id="planSelect">
                <option value="Free">Free Starter (월 0원 - 일 500회)</option>
                <option value="Pro" selected>Pro Analyst (월 29,000원 - 세이버메트릭스 전체/50,000회)</option>
                <option value="Enterprise">Enterprise (월 199,000원 - 무제한 회선/WebSocket)</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">신청자명 / 법인명</label>
              <input type="text" class="form-control bg-dark text-white border-secondary" id="applicantName" placeholder="홍길동 (또는 회사명)">
            </div>
            <div class="mb-3">
              <label class="form-label text-muted" style="font-size: 0.88rem;">연락처 이메일</label>
              <input type="email" class="form-control bg-dark text-white border-secondary" id="applicantEmail" placeholder="developer@company.com">
            </div>
            <button class="btn btn-gradient w-100 py-2 mt-2" onclick="generateApiKey()">
              <i class="bi bi-shield-lock-fill me-1"></i>API 키 즉시 생성 & 활성화
            </button>
          </div>

          <!-- Result Step -->
          <div id="keyResultStep" style="display: none;">
            <div class="text-center py-3">
              <i class="bi bi-check-circle-fill text-success fs-1"></i>
              <h5 class="fw-bold text-white mt-2">API 키 발급이 완료되었습니다!</h5>
              <p class="text-muted" style="font-size: 0.88rem;">발급된 키를 API 호출 헤더의 <code class="text-info">X-API-KEY</code>로 전달해 주세요.</p>
            </div>
            <div class="p-3 bg-dark border border-secondary rounded-3 mb-3">
              <label class="text-dim" style="font-size: 0.75rem;">YOUR API KEY</label>
              <div class="d-flex justify-content-between align-items-center">
                <code class="text-warning fw-bold fs-6" id="generatedKeyBox">sk_live_...</code>
                <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="copyApiKey()"><i class="bi bi-copy"></i> 복사</button>
              </div>
            </div>
            <div class="p-2 text-muted" style="font-size: 0.82rem; background: rgba(56, 189, 248, 0.08); border-radius: 6px;">
              <i class="bi bi-info-circle text-info me-1"></i>도메인 연결 및 SSL 설정 완료 후 상용 서비스에서 바로 사용하실 수 있습니다.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bootstrap Bundle JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

  <!-- News & Live Matches Script -->
  <script>
    // Initial Sports News Database
    const DEFAULT_NEWS = [
      {
        id: 1,
        category: 'BASEBALL',
        categoryLabel: '⚾ 야구',
        categoryClass: 'bg-baseball',
        title: '오타니 쇼헤이, wOBA .425 돌파하며 역사상 최초 50-50 대기록 달성 초읽기',
        desc: '단순 홈런과 도루 개수를 넘어 wOBA .425, wRC+ 182를 기록 중인 오타니의 경기 기여도와 타석별 세이버메트릭스 정밀 분석.',
        author: '스포허브 메이저리그 데스크',
        date: '2026-09-05 18:30',
        chips: ['wOBA .425', 'wRC+ 182', 'OPS 1.034', 'WAR 8.2'],
        content: `오타니 쇼헤이가 메이저리그 사상 초유의 50홈런-50도루 클럽 달성을 눈앞에 두고 있습니다. 이번 시즌 오타니의 진정한 가치는 단순 누적 기록뿐만 아니라 세이버메트릭스 지표에서 더욱 두드러집니다.

현재 오타니의 가중 출루율(wOBA)은 .425로 리그 1위를 달리고 있으며, 구장 환경과 리그 평균을 보정한 조정 득점 창출력(wRC+)은 182에 달합니다. 이는 그가 타석에 들어설 때마다 리그 평균 타자 대비 82% 더 많은 득점을 팀에 안겨주고 있음을 의미합니다.

또한 강한 타구 비율(HardHit%)이 58.4%에 달하며, 인플레이 타구 타율(BABIP) 역시 .342로 최상위권을 유지하고 있어 운이 아닌 순수한 타격 파워로 리그를 지배하고 있음을 증명하고 있습니다.`
      },
      {
        id: 2,
        category: 'SOCCER',
        categoryLabel: '⚽ 축구',
        categoryClass: 'bg-soccer',
        title: '손흥민, xA(기대 어시스트) 0.82 폭발... 토트넘 후반 극적 역전승 견인',
        desc: '유럽 5대 리그 정상급 찬스 메이킹과 키패스 4회 기록. 전방 압박과 파이널 서드 패스 성공률 88%로 경기 최우수 선수 선정.',
        author: 'EPL 전문 분석팀',
        date: '2026-09-05 17:15',
        chips: ['xA 0.82', '키패스 4회', '유효슈팅 3', 'PPDA 7.2'],
        content: `토트넘 홋스퍼의 캡틴 손흥민이 환상적인 찬스 메이킹으로 팀의 극적인 역전승을 견인했습니다. 이날 손흥민은 단순 득점 이상의 플레이메이킹 능력을 발휘했습니다.

데이터 분석 결과 손흥민의 기대 어시스트(xA)는 0.82로 양 팀 통틀어 최고치를 기록했습니다. 특히 상대 수비진의 빈틈을 파고드는 4차례의 결정적 키패스와 전진 패스 7회를 성공시키며 상대 전방 압박(PPDA 7.2)을 무력화시켰습니다.

경기 후 공식 평점 8.9점을 획득한 손흥민은 이번 라운드 프리미어리그 베스트 11에 선정되며 건재함을 과시했습니다.`
      },
      {
        id: 3,
        category: 'BASKETBALL',
        categoryLabel: '🏀 농구',
        categoryClass: 'bg-basketball',
        title: '니콜라 요키치, TS% 72.8%로 덴버 승리 견인... Hollinger GameScore 32.4',
        desc: '트리플더블과 함께 100회 포제션당 137점의 압도적 공격효율(ORtg) 기록. 골밑 지배력과 클러치 패스로 리그 판도 장악.',
        author: 'NBA 데이터 분석실',
        date: '2026-09-05 16:40',
        chips: ['TS% 72.8%', 'GameScore 32.4', 'ORtg 137.0', 'Pace 96.3'],
        content: `덴버 너게츠의 에이스 니콜라 요키치가 또 한 번의 경이로운 효율성을 선보였습니다. 요키치는 출전 시간 동안 야투 성공률 66.7%와 함께 자유투를 완벽하게 꽂아 넣으며 트루 슈팅 성공률(TS%) 72.8%를 기록했습니다.

John Hollinger가 고안한 종합 경기 기여도(Game Score)에서 32.4점을 획득한 요키치는 팀이 100회 공격 점유권을 가질 때마다 무려 137.0점을 생산해내는 압도적인 공격 레이팅(ORtg)을 이끌어냈습니다.

덴버는 요키치의 컨트롤 아래 템포(Pace 96.3)를 유지하며 경기 후반 멤피스의 추격을 완전히 따돌렸습니다.`
      },
      {
        id: 4,
        category: 'BASEBALL',
        categoryLabel: '⚾ 야구',
        categoryClass: 'bg-baseball',
        title: 'KBO 포스트시즌 진출권 다툼: 불펜 FIP 2.45로 막아낸 철벽 마운드의 비결',
        desc: '수비수의 실책이나 운을 배제한 수비 독립 평균자책점(FIP)에서 압도적인 수치를 기록한 팀이 최근 10경기 승률 80% 달성.',
        author: 'KBO 전문기자단',
        date: '2026-09-05 15:20',
        chips: ['FIP 2.45', 'K/9 10.2', 'WHIP 0.98', 'LOB% 82%'],
        content: `KBO 가을야구 순위 싸움이 절정에 달한 가운데, 불펜진의 수비 독립 평균자책점(FIP)이 순위 판도를 가르는 결정적 잣대로 부상하고 있습니다.

최근 10경기에서 8승을 쓸어 담은 모 구단의 불펜진은 9이닝당 탈삼진(K/9) 10.2개를 솎아내며 FIP 2.45를 기록했습니다. 수비진의 보이지 않는 실책이나 빗맞은 안타에 흔들리지 않고 삼진과 범타로 실점을 틀어막은 점이 상승세의 원동력으로 꼽힙니다.

잔루 처리율(LOB%) 역시 82%에 달해 위기 상황에서의 탈출 능력이 리그 최고 수준임을 입증했습니다.`
      },
      {
        id: 5,
        category: 'SOCCER',
        categoryLabel: '⚽ 축구',
        categoryClass: 'bg-soccer',
        title: '레알 마드리드, xGOT 2.18로 엘 클라시코 화력전 완승... 역습의 정석',
        desc: '유효슈팅의 궤적과 파워를 측정한 xGOT에서 상대를 압도하며 3골 폭발. 필드 틸트 열세에도 불구하고 치명적인 결정력 과시.',
        author: '라리가 스페셜 리포터',
        date: '2026-09-05 14:10',
        chips: ['xGOT 2.18', '결정력 28%', 'SoT% 60%', 'PSxG 1.95'],
        content: `스페인 최고의 빅매치 엘 클라시코에서 레알 마드리드가 치명적인 결정력으로 승리를 거머쥐었습니다.

점유율과 필드 틸트(Field Tilt 42%)에서는 다소 밀렸으나, 상대 골문을 향한 유효슈팅 기대 득점(xGOT)은 무려 2.18에 달했습니다. 이는 골키퍼가 손쓸 수 없는 골문 구석으로 향한 질 높은 슈팅이 대거 나왔음을 의미합니다.

특히 음바페와 비니시우스의 역습 전개는 상대 골키퍼의 실점 억제력을 무력화시키며 완벽한 승리를 이끌었습니다.`
      },
      {
        id: 6,
        category: 'BASKETBALL',
        categoryLabel: '🏀 농구',
        categoryClass: 'bg-basketball',
        title: 'NBA 현대 농구의 화두 "Pace와 eFG%"... 공격 템포와 3점슛의 상관관계',
        desc: '경기당 100회 이상의 포제션을 소화하면서도 유효 야투율 55% 이상을 유지하는 팀들의 플레이오프 진출 확률 92% 분석.',
        author: '스포허브 바스켓랩',
        date: '2026-09-05 12:30',
        chips: ['eFG% 56.4%', 'Pace 101.2', '3P% 38.5%', 'NetRating +8.5'],
        content: `현대 NBA에서 승리를 거두기 위한 가장 중요한 두 축은 바로 빠른 경기 템포(Pace)와 3점슛 가중치가 반영된 유효 야투율(eFG%)입니다.

데이터 분석 결과, 경기당 100개 이상의 포제션을 유지하면서도 eFG% 55%를 초과하는 팀들은 정규시즌 승률 70% 이상을 거두고 있습니다. 단순 미드레인지 점퍼보다 페인트존 침투와 코너 3점슛을 조합한 슛 차트가 현대 농구 승리의 공식으로 굳어졌음을 확인했습니다.`
      },
      {
        id: 7,
        category: 'ANALYTICS',
        categoryLabel: '📊 데이터 칼럼',
        categoryClass: 'bg-analytics',
        title: '전통 승률 vs 세이버메트릭스 기대 지표: 왜 데이터 기반 분석이 필수인가?',
        desc: '피타고리안 기대 승률과 xG 모델이 증명하는 스포츠 데이터 혁명. 운과 기복을 걷어내고 미래 경기 결과를 예측하는 메커니즘.',
        author: '수석 데이터 사이언티스트',
        date: '2026-09-05 11:00',
        chips: ['피타고리안 기대승률', 'xG 모델링', 'WAR/WPA', '머신러닝 예측'],
        content: `스포츠에서 '운(Luck)'은 결과를 왜곡하는 가장 큰 요인입니다. 불운하게 빗맞은 타구가 안타가 되거나 골대를 강타하는 슛 하나로 승패가 갈릴 수 있습니다.

하지만 세이버메트릭스는 이러한 일시적 노이즈를 제거하고 팀의 진짜 본질적인 실력을 측정합니다. 야구의 wOBA와 FIP, 축구의 xG와 PPDA, 농구의 Net Rating은 모두 '다음 경기에서 이 팀이 실제로 승리할 확률'을 기존 클래식 스탯보다 훨씬 더 정확하게 예측해 냅니다. 이것이 글로벌 스포츠 베팅 시장과 구단들이 데이터 API에 막대한 투자를 하는 이유입니다.`
      }
    ];

    let currentNewsList = [];
    let currentFilter = 'ALL';

    // Load news from localStorage or set defaults
    function loadNews() {
      const stored = localStorage.getItem('sportix_news_db');
      if (stored) {
        try {
          currentNewsList = JSON.parse(stored);
        } catch (e) {
          currentNewsList = DEFAULT_NEWS;
        }
      } else {
        currentNewsList = DEFAULT_NEWS;
        localStorage.setItem('sportix_news_db', JSON.stringify(DEFAULT_NEWS));
      }
      renderNews();
    }

    function renderNews() {
      const grid = document.getElementById('newsGrid');
      const filtered = currentFilter === 'ALL' 
        ? currentNewsList 
        : currentNewsList.filter(item => item.category === currentFilter);

      if (filtered.length === 0) {
        grid.innerHTML = '<div class="col-12 text-center text-muted py-5">해당 카테고리의 소식이 없습니다.</div>';
        return;
      }

      let html = '';
      filtered.forEach(item => {
        let chipHtml = '';
        if (item.chips && item.chips.length > 0) {
          chipHtml = item.chips.map(c => `<span class="data-chip">${c}</span>`).join('');
        }

        html += `
          <div class="col-lg-4 col-md-6">
            <div class="news-card" onclick="openArticleModal(${item.id})">
              <div class="news-header-bg ${item.categoryClass}">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="badge bg-dark bg-opacity-75 text-white">${item.categoryLabel}</span>
                  <span class="text-white-50" style="font-size: 0.75rem;">${item.date.split(' ')[0]}</span>
                </div>
                <div class="d-flex flex-wrap gap-1">
                  ${chipHtml}
                </div>
              </div>
              <div class="news-body">
                <h5 class="news-title">${item.title}</h5>
                <p class="news-desc">${item.desc}</p>
                <div class="d-flex justify-content-between align-items-center pt-2 border-top" style="border-color: var(--border-color) !important;">
                  <span class="text-dim" style="font-size: 0.8rem;"><i class="bi bi-person me-1"></i>${item.author}</span>
                  <span class="text-primary fw-semibold" style="font-size: 0.82rem;">읽기 <i class="bi bi-chevron-right"></i></span>
                </div>
              </div>
            </div>
          </div>
        `;
      });
      grid.innerHTML = html;
    }

    function filterNews(cat, btn) {
      currentFilter = cat;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderNews();
    }

    function openArticleModal(id) {
      const item = currentNewsList.find(n => n.id === id);
      if (!item) return;

      document.getElementById('modalCategory').innerText = item.categoryLabel;
      document.getElementById('modalDate').innerText = item.date;
      document.getElementById('modalTitle').innerText = item.title;
      document.getElementById('modalAuthor').innerText = item.author;
      document.getElementById('modalContent').innerHTML = item.content.replace(/\\n/g, '<br><br>');

      const chipsBox = document.getElementById('modalChips');
      if (item.chips && item.chips.length > 0) {
        chipsBox.innerHTML = item.chips.map(c => `<span class="data-chip px-2 py-1">${c}</span>`).join('');
        document.getElementById('modalDataBox').style.display = 'block';
      } else {
        document.getElementById('modalDataBox').style.display = 'none';
      }

      const modal = new bootstrap.Modal(document.getElementById('articleModal'));
      modal.show();
    }

    function openPostNewsModal() {
      const modal = new bootstrap.Modal(document.getElementById('postNewsModal'));
      modal.show();
    }

    function saveNewArticle() {
      const cat = document.getElementById('newCategory').value;
      const title = document.getElementById('newTitle').value.trim();
      const author = document.getElementById('newAuthor').value.trim();
      const desc = document.getElementById('newDesc').value.trim();
      const content = document.getElementById('newContent').value.trim();
      const tagsStr = document.getElementById('newTags').value.trim();

      if (!title || !desc || !content) {
        alert('제목, 요약, 본문을 모두 입력해 주세요.');
        return;
      }

      const chips = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : [];

      let catLabel = '⚾ 야구';
      let catClass = 'bg-baseball';
      if (cat === 'SOCCER') { catLabel = '⚽ 축구'; catClass = 'bg-soccer'; }
      else if (cat === 'BASKETBALL') { catLabel = '🏀 농구'; catClass = 'bg-basketball'; }
      else if (cat === 'ANALYTICS') { catLabel = '📊 데이터 칼럼'; catClass = 'bg-analytics'; }

      const now = new Date();
      const dateStr = now.toISOString().slice(0, 16).replace('T', ' ');

      const newArticle = {
        id: Date.now(),
        category: cat,
        categoryLabel: catLabel,
        categoryClass: catClass,
        title: title,
        desc: desc,
        author: author || '스포허브 데스크',
        date: dateStr,
        chips: chips,
        content: content
      };

      currentNewsList.unshift(newArticle);
      localStorage.setItem('sportix_news_db', JSON.stringify(currentNewsList));
      renderNews();

      bootstrap.Modal.getInstance(document.getElementById('postNewsModal')).hide();
      document.getElementById('postNewsForm').reset();
      alert('새 스포츠 소식이 성공적으로 발행되었습니다!');
    }

    // Live Match Center Strip Loading from FastAPI
    let allMatches = [];
    async function loadLiveMatches() {
      const container = document.getElementById('stripContainer');
      try {
        const resp = await fetch('/api/v1/matches?limit=40');
        if (!resp.ok) throw new Error('Failed to load matches');
        allMatches = await resp.json();
        renderMatchStrip('ALL');
      } catch (e) {
        console.error('Match strip load error:', e);
        container.innerHTML = '<div class="text-muted p-3">실시간 경기 스코어보드를 대시보드 콘솔에서 확인하실 수 있습니다.</div>';
      }
    }

    function renderMatchStrip(sport) {
      const container = document.getElementById('stripContainer');
      if (!allMatches || allMatches.length === 0) {
        container.innerHTML = '<div class="text-muted p-3">적재된 경기가 없습니다.</div>';
        return;
      }

      const filtered = sport === 'ALL' 
        ? allMatches.slice(0, 20) 
        : allMatches.filter(m => m.sport_code === sport).slice(0, 20);

      let html = '';
      filtered.forEach(m => {
        let sportIcon = '⚾';
        if (m.sport_code === 'SOCCER') sportIcon = '⚽';
        if (m.sport_code === 'BASKETBALL') sportIcon = '🏀';

        const isLive = m.status === 'LIVE';
        const stBadge = isLive 
          ? '<span class="badge bg-danger">LIVE</span>' 
          : (m.status === 'FINISHED' ? '<span class="badge bg-secondary">종료</span>' : '<span class="badge bg-dark">예정</span>');

        html += `
          <div class="strip-card" onclick="location.href='/dashboard'">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="strip-league">${sportIcon} ${m.league_name || m.sport_code}</span>
              ${stBadge}
            </div>
            <div class="d-flex justify-content-between align-items-center my-1">
              <span class="strip-team text-truncate me-2" style="max-width: 140px;">${m.home_team_name}</span>
              <span class="strip-score">${m.home_score}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center my-1">
              <span class="strip-team text-truncate me-2" style="max-width: 140px;">${m.away_team_name}</span>
              <span class="strip-score">${m.away_score}</span>
            </div>
            <div class="text-dim mt-2 pt-1 border-top" style="border-color: var(--border-color) !important; font-size: 0.75rem;">
              ${m.match_date || '일정 확인'}
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function filterStrip(sport) {
      document.querySelectorAll('#match-strip button').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('stripBtn' + sport);
      if (activeBtn) activeBtn.classList.add('active');
      renderMatchStrip(sport);
    }

    // API Key Modal Handling
    function openApiKeyModal() {
      document.getElementById('keyFormStep').style.display = 'block';
      document.getElementById('keyResultStep').style.display = 'none';
      const modal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
      modal.show();
    }

    function selectPlan(planName) {
      document.getElementById('planSelect').value = planName;
      openApiKeyModal();
    }

    function generateApiKey() {
      const email = document.getElementById('applicantEmail').value.trim();
      const name = document.getElementById('applicantName').value.trim();
      const plan = document.getElementById('planSelect').value;

      if (!email || !name) {
        alert('신청자명과 이메일을 입력해 주세요.');
        return;
      }

      const randomHex = Array.from(crypto.getRandomValues(new Uint8Array(16)))
        .map(b => b.toString(16).padStart(2, '0')).join('');
      const fakeKey = `sk_live_${plan.toLowerCase()}_${randomHex.slice(0, 24)}`;

      document.getElementById('generatedKeyBox').innerText = fakeKey;
      document.getElementById('keyFormStep').style.display = 'none';
      document.getElementById('keyResultStep').style.display = 'block';
    }

    function copyApiKey() {
      const key = document.getElementById('generatedKeyBox').innerText;
      navigator.clipboard.writeText(key).then(() => {
        alert('API 키가 클립보드에 복사되었습니다!');
      });
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', () => {
      loadNews();
      loadLiveMatches();
    });
  </script>
</body>
</html>
"""

def generate_landing():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(root_dir, "app", "templates", "landing.html")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"[OK] Generated landing page at {target_path} (Size: {len(html_code)} chars)")

if __name__ == "__main__":
    generate_landing()
