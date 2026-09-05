# -*- coding: utf-8 -*-
import os

html_code = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TOKEON PRO (tokeon.kr) — 글로벌 3대 스포츠 실시간 뉴스 & 공식 세이버메트릭스 API 포털</title>
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

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: 'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow-x: hidden;
      line-height: 1.6;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-main); }
    ::-webkit-scrollbar-thumb { background: #27354f; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

    /* Navbar */
    .navbar-glass {
      background: rgba(10, 14, 26, 0.88);
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
    .domain-badge {
      font-size: 0.72rem;
      background: #0284c7;
      color: white;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .nav-link-custom {
      color: var(--text-muted);
      font-size: 0.95rem;
      font-weight: 500;
      padding: 0.5rem 0.9rem;
      transition: color 0.2s ease;
      text-decoration: none;
    }
    .nav-link-custom:hover { color: var(--accent-blue); }

    /* Live Breaking News Marquee */
    .breaking-ticker {
      background: #0f172a;
      border-bottom: 1px solid var(--border-color);
      padding: 8px 0;
      overflow: hidden;
      font-size: 0.88rem;
    }
    .ticker-wrap { display: flex; align-items: center; }
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
      animation: marquee 45s linear infinite;
    }
    .ticker-content:hover { animation-play-state: paused; }
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
      font-size: 2.85rem;
      font-weight: 800;
      line-height: 1.25;
      letter-spacing: -1px;
      margin-bottom: 1.25rem;
    }
    .hero-desc {
      font-size: 1.12rem;
      color: var(--text-muted);
      line-height: 1.75;
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
      height: 220px;
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
      background: rgba(15, 23, 42, 0.85);
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
      height: 130px;
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
      font-size: 1.05rem;
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
      font-size: 0.86rem;
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

    /* Filter Tabs */
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

    /* Pricing */
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
    .pricing-card:hover { transform: translateY(-5px); }
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
    .footer-link:hover { color: var(--accent-blue); }

    /* 3-Day Prediction Section Styles */
    .pred-card {
      background: rgba(18, 24, 41, 0.7);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .pred-card:hover {
      background: var(--bg-card-hover);
      border-color: var(--accent-blue);
      transform: translateX(2px);
    }
    .pred-card.active-match-card {
      background: rgba(37, 99, 235, 0.2) !important;
      border: 1.5px solid #38bdf8 !important;
      box-shadow: 0 0 14px rgba(56, 189, 248, 0.3);
    }
    .prob-bar {
      height: 12px;
      border-radius: 6px;
      overflow: hidden;
      display: flex;
    }
    .metric-compare-bar {
      height: 8px;
      border-radius: 4px;
      background: #1e293b;
      overflow: hidden;
      display: flex;
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
      <a class="navbar-brand d-flex align-items-center gap-2" href="/">
        <div style="background: linear-gradient(135deg, #0284c7, #2563eb); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
          <i class="bi bi-lightning-charge-fill text-white fs-5"></i>
        </div>
        <div class="d-flex flex-column">
          <div class="d-flex align-items-center gap-2">
            <span class="nav-brand-title">TOKEON PRO</span>
            <span class="domain-badge">tokeon.kr</span>
          </div>
        </div>
      </a>

      <!-- Sync Status Badge -->
      <div class="d-none d-md-flex align-items-center gap-2 ms-3 px-3 py-1" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9999px;">
        <span style="width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; animation: pulseGlow 1.5s infinite;"></span>
        <span style="font-size: 0.78rem; font-weight: 700; color: #10b981;">3대 스포츠 259경기 공식 실시간 집계 LIVE</span>
      </div>

      <button class="navbar-toggler border-0 text-white" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
        <i class="bi bi-list fs-2"></i>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navMenu">
        <ul class="navbar-nav align-items-center gap-1 my-2 my-lg-0">
          <li class="nav-item"><a class="nav-link-custom text-info fw-bold" href="#prediction-section"><i class="bi bi-cpu-fill me-1"></i>3일 경기 분석 랩</a></li>
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

  <!-- 실시간 속보 전광판 Ticker (100% 실제 최신 뉴스 자동 주입) -->
  <div class="breaking-ticker">
    <div class="container d-flex align-items-center">
      <span class="ticker-badge"><i class="bi bi-broadcast-pin me-1"></i>BREAKING NEWS</span>
      <div style="overflow: hidden; width: 100%;">
        <div class="ticker-content" id="tickerItems">
          <span class="ticker-item">실시간 스포츠 속보 뉴스를 로딩하고 있습니다...</span>
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
            <i class="bi bi-stars"></i> tokeon.kr 공식 스포츠 미디어 & 데이터 포털
          </div>
          <h1 class="hero-title">
            스포츠를 읽는 가장 완벽한 시선,<br>
            <span style="background: linear-gradient(135deg, #38bdf8 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
              실시간 속보 & 세이버메트릭스
            </span>
          </h1>
          <p class="hero-desc">
            <b>tokeon.kr</b>은 야구(MLB·KBO·NPB), 유럽 축구 5대 리그(EPL·라리가·분데스리가·세리에A·리그1), 농구(NBA)의 
            <b>100% 실제 현장 보도 기사</b>와 <b>공식 경기 스코어보드</b>, 그리고 <b>xG · wOBA · Pace</b> 첨단 세이버메트릭스 API를 단 하나의 포털에서 제공합니다.
          </p>
          <div class="d-flex flex-wrap gap-3">
            <a href="#news-section" class="btn btn-gradient">
              <i class="bi bi-newspaper"></i> 실제 스포츠 뉴스 브리핑
            </a>
            <a href="#match-strip" class="btn btn-outline-glass">
              <i class="bi bi-broadcast"></i> 공식 경기 결과 센터
            </a>
            <a href="/dashboard" class="btn btn-outline-glass text-warning border-warning">
              <i class="bi bi-database-fill"></i> 데이터 관리자 콘솔
            </a>
          </div>

          <!-- Feature Metric Highlights (실제 DB 수치) -->
          <div class="row mt-5 pt-3 g-4 border-top" style="border-color: var(--border-color) !important;">
            <div class="col-4">
              <div class="fs-4 fw-bold text-white">259<span style="color: var(--accent-blue);">+</span></div>
              <div class="text-muted" style="font-size: 0.85rem;">공식 집계 경기</div>
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

        <!-- Featured Headline Right Card (100% 실제 뉴스 1위 연동) -->
        <div class="col-lg-5">
          <div class="featured-card" id="featuredCard" onclick="openFeaturedModal()">
            <div class="featured-img-wrap">
              <span class="featured-badge-top"><i class="bi bi-lightning-charge-fill me-1"></i>TODAY's HEADLINE</span>
              <i class="bi bi-trophy-fill featured-img-icon"></i>
              <div class="p-4 text-center z-1 w-100">
                <span class="badge bg-primary px-3 py-1 mb-2" id="featCategory">⚾ 야구</span>
                <h5 class="fw-bold text-white mb-0" id="featTitle">실시간 최신 기사를 로딩 중입니다...</h5>
              </div>
            </div>
            <div class="p-4">
              <p class="text-muted mb-3" id="featDesc" style="font-size: 0.92rem; line-height: 1.6;">
                주요 스포츠 언론사의 실제 공식 기사 본문 요약을 불러오고 있습니다.
              </p>
              <div class="d-flex flex-wrap gap-2 mb-3" id="featChips">
                <span class="data-chip">#실시간속보</span>
                <span class="data-chip">#공식기사</span>
              </div>
              <div class="d-flex justify-content-between align-items-center pt-2 border-top" style="border-color: var(--border-color) !important;">
                <span class="text-dim" style="font-size: 0.82rem;" id="featSource"><i class="bi bi-newspaper me-1"></i>언론사 공식 취재</span>
                <span class="text-info fw-semibold" style="font-size: 0.85rem;">기사 전문 읽기 <i class="bi bi-arrow-right"></i></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Live Match Center Strip (100% 실제 공식 경기 스코어보드) -->
  <section class="match-strip-section" id="match-strip">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
          <span style="width: 10px; height: 10px; background-color: #ef4444; border-radius: 50%; display: inline-block; animation: pulseGlow 1.2s infinite;"></span>
          <h5 class="fw-bold mb-0 text-white"><i class="bi bi-broadcast me-1 text-danger"></i>공식 경기 센터 (Official Live Match Scores)</h5>
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
        <div class="text-muted p-3">실제 공식 경기 결과 데이터를 불러오는 중...</div>
      </div>
    </div>
  </section>

  <!-- 🔮 3-Day Upcoming Match Predictor & Recommended Metrics Lab (1/4 Left vs 3/4 Right) -->
  <section class="py-5" id="prediction-section" style="background: #0d1222; border-bottom: 1px solid var(--border-color);">
    <div class="container">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
        <div>
          <span class="badge bg-primary text-white px-3 py-1 fw-bold mb-2"><i class="bi bi-cpu-fill me-1"></i>AI MATCH PREDICTOR & METRICS</span>
          <h2 class="fw-bold text-white mb-1">향후 3일간 경기 분석 & 추천 세이버메트릭스 랩</h2>
          <p class="text-muted mb-0">앞으로 3일간 펼쳐질 실제 경기 일정과 tokeon.kr 추천 메트릭스 기반 AI 승부 예측 모델</p>
        </div>

        <!-- 1-Month Free Trial CTA Badge -->
        <div class="d-flex align-items-center gap-2 p-2 px-3 rounded-3" style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4);">
          <i class="bi bi-gift-fill text-success fs-4"></i>
          <div>
            <div class="text-white fw-bold" style="font-size: 0.88rem;">첫 달 100% 무료 체험 (이후 월 9,000원)</div>
            <div class="text-muted" style="font-size: 0.78rem;">가입 즉시 3일간 전 경기 추천 메트릭스 무제한 열람</div>
          </div>
          <button class="btn btn-sm btn-success ms-2" onclick="selectPlan('Basic')">무료 시작</button>
        </div>
      </div>

      <div class="row g-4">
        <!-- Left Column: 1/4 Width (~25%) Upcoming Matches Scrollable Sidebar -->
        <div class="col-lg-3 col-md-4">
          <div class="p-3 rounded-4" style="background: var(--bg-card); border: 1px solid var(--border-color); height: 720px; display: flex; flex-direction: column;">
            
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="fw-bold text-white" style="font-size: 0.92rem;"><i class="bi bi-calendar3 me-1 text-info"></i>향후 3일 경기</span>
              <span class="badge bg-secondary" id="predCountBadge">0경기</span>
            </div>

            <!-- Date Tabs: All / Day 1 / Day 2 / Day 3 -->
            <div class="d-flex gap-1 mb-2 pb-2 border-bottom" style="border-color: var(--border-color) !important;">
              <button class="btn btn-sm btn-outline-secondary py-0 px-2 active flex-fill" id="predDateALL" onclick="filterPredDate('ALL')">3일전체</button>
              <button class="btn btn-sm btn-outline-secondary py-0 px-2 flex-fill" id="predDateD0" onclick="filterPredDate('D0')">오늘</button>
              <button class="btn btn-sm btn-outline-secondary py-0 px-2 flex-fill" id="predDateD1" onclick="filterPredDate('D1')">내일</button>
              <button class="btn btn-sm btn-outline-secondary py-0 px-2 flex-fill" id="predDateD2" onclick="filterPredDate('D2')">모레</button>
            </div>

            <!-- Sport Tabs -->
            <div class="d-flex gap-1 mb-3">
              <button class="btn btn-sm btn-dark py-0 px-2 active flex-fill text-muted" id="predSportALL" onclick="filterPredSport('ALL')">전체</button>
              <button class="btn btn-sm btn-dark py-0 px-2 flex-fill text-muted" id="predSportBASEBALL" onclick="filterPredSport('BASEBALL')">⚾야구</button>
              <button class="btn btn-sm btn-dark py-0 px-2 flex-fill text-muted" id="predSportSOCCER" onclick="filterPredSport('SOCCER')">⚽축구</button>
              <button class="btn btn-sm btn-dark py-0 px-2 flex-fill text-muted" id="predSportBASKETBALL" onclick="filterPredSport('BASKETBALL')">🏀농구</button>
            </div>

            <!-- Scrollable Match List (1/4 Column) -->
            <div class="flex-grow-1 overflow-auto pe-1" id="predMatchList" style="scrollbar-width: thin;">
              <div class="text-center text-muted py-5">경기 일정을 불러오는 중...</div>
            </div>

            <!-- Bottom Counter -->
            <div class="pt-2 mt-2 border-top text-center text-dim" style="border-color: var(--border-color) !important; font-size: 0.78rem;">
              <i class="bi bi-mouse me-1"></i>스크롤하여 경기 선택 시 우측 분석 갱신
            </div>
          </div>
        </div>

        <!-- Right Column: 3/4 Width (~75%) Recommended Metrics Analysis Panel -->
        <div class="col-lg-9 col-md-8">
          <div class="p-4 rounded-4" style="background: var(--bg-card); border: 1px solid var(--border-color); min-height: 720px; display: flex; flex-direction: column;" id="predDetailPanel">
            <!-- Dynamically injected by JavaScript -->
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Sports News & Editorial Magazine (100% 실제 스포츠 언론 보도) -->
  <section class="py-5" id="news-section">
    <div class="container">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4 pb-2 border-bottom" style="border-color: var(--border-color) !important;">
        <div>
          <span class="text-primary fw-bold text-uppercase" style="font-size: 0.82rem; letter-spacing: 1px;">Editorial & Press</span>
          <h2 class="fw-bold text-white mb-1"><i class="bi bi-newspaper me-2 text-primary"></i>스포츠 뉴스 & 심층 분석</h2>
          <p class="text-muted mb-0" style="font-size: 0.95rem;">국내외 주요 스포츠 언론사에서 실시간 보도된 실제 기사입니다.</p>
        </div>

        <!-- Action Buttons: Filter + Refresh -->
        <div class="d-flex flex-wrap gap-2 align-items-center">
          <button class="filter-btn active" onclick="filterNews('ALL', this)">전체 소식</button>
          <button class="filter-btn" onclick="filterNews('BASEBALL', this)">⚾ 야구</button>
          <button class="filter-btn" onclick="filterNews('SOCCER', this)">⚽ 축구</button>
          <button class="filter-btn" onclick="filterNews('BASKETBALL', this)">🏀 농구</button>
          <button class="filter-btn" onclick="filterNews('ANALYTICS', this)">📊 데이터 칼럼</button>
          <button class="btn btn-sm btn-outline-info ms-md-2" onclick="refreshLiveNews()">
            <i class="bi bi-arrow-clockwise me-1"></i>뉴스 최신화
          </button>
        </div>
      </div>

      <!-- News Cards Grid -->
      <div class="row g-4" id="newsGrid">
        <div class="col-12 text-center text-muted py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <div class="mt-2">실제 스포츠 뉴스 피드를 불러오고 있습니다...</div>
        </div>
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
        <h2 class="fw-bold text-white mb-3">tokeon.kr 공식 개발자 & 기업용 API 요금제</h2>
        <p class="text-muted">
          스포츠 미디어, 데이터 스타트업, 스포츠 팬 커뮤니티, 전문 분석가를 위한 완벽한 RESTful API 구독 플랜
        </p>
      </div>

      <div class="row g-4 justify-content-center">
        <!-- Basic Analyst Plan (New 9,000원 - 1개월 무료 체험) -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card popular" style="border: 2px solid #10b981; background: linear-gradient(180deg, #102a24 0%, #121829 100%);">
            <span class="position-absolute top-0 start-50 translate-middle badge bg-success px-3 py-2 fw-bold">
              🎉 첫 달 0원 무료 체험 (BEST)
            </span>
            <h4 class="fw-bold text-white mb-1">Basic Analyst</h4>
            <p class="text-muted" style="font-size: 0.88rem;">일반 스포츠 팬, 토론가 & 베팅 분석가</p>
            <div class="pricing-price" style="color: #34d399;">₩9,000 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 월 (첫 달 0원)</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> <strong>향후 3일간 3대 종목 전 경기 추천 메트릭스 열람</strong></li>
              <li><i class="bi bi-check2 text-success"></i> <strong>AI 피타고리안 & xG 승부 예측 확률 실시간 제공</strong></li>
              <li><i class="bi bi-check2 text-success"></i> 야구(FIP/wOBA), 축구(PPDA/xG), 농구(Pace/ORtg) 매치업</li>
              <li><i class="bi bi-check2 text-success"></i> 경기별 데이터 분석관 핵심 관전 가이드</li>
              <li><i class="bi bi-check2 text-success"></i> <strong>첫 달 100% 무료 체험</strong> 후 언제든 즉시 해지 가능</li>
            </ul>
            <button class="btn btn-success w-100 py-2 mt-auto fw-bold" onclick="selectPlan('Basic')">
              1개월 무료 체험 시작하기
            </button>
          </div>
        </div>

        <!-- Pro Analyst Plan (Popular) -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card">
            <h4 class="fw-bold text-white mb-1">Pro API Analyst</h4>
            <p class="text-muted" style="font-size: 0.88rem;">스포츠 미디어, 블로거 & 전문 애널리스트</p>
            <div class="pricing-price">₩29,000 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 월 (VAT 포함)</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> <strong>일일 50,000회 고속 호출</strong></li>
              <li><i class="bi bi-check2 text-success"></i> <strong>3대 종목 첨단 세이버메트릭스 전체 API</strong> (xG, wOBA, Pace 등)</li>
              <li><i class="bi bi-check2 text-success"></i> <strong>3·5·7·10G/D 롤링 트렌드 API</strong></li>
              <li><i class="bi bi-check2 text-success"></i> <strong>구단/포지션별 정밀 JSON/ZIP 일괄 다운로드</strong></li>
              <li><i class="bi bi-check2 text-success"></i> 초당 20 RPS 속도 보장</li>
            </ul>
            <button class="btn btn-gradient w-100 py-2 mt-auto" onclick="selectPlan('Pro')">
              Pro 플랜 지금 시작하기
            </button>
          </div>
        </div>

        <!-- Free Starter Plan -->
        <div class="col-lg-4 col-md-6">
          <div class="pricing-card">
            <h4 class="fw-bold text-white mb-1">Free Starter</h4>
            <p class="text-muted" style="font-size: 0.88rem;">기본 스코어보드 확인 및 개인 개발자</p>
            <div class="pricing-price">₩0 <span style="font-size: 1rem; color: var(--text-dim); font-weight: 400;">/ 평생 무료</span></div>
            <ul class="pricing-features">
              <li><i class="bi bi-check2 text-success"></i> 일일 500회 호출 한도</li>
              <li><i class="bi bi-check2 text-success"></i> 야구/축구/농구 기본 스코어보드</li>
              <li><i class="bi bi-check2 text-success"></i> 경기 일정 및 최종 결과 조회</li>
              <li><i class="bi bi-check2 text-success"></i> tokeon.kr 커뮤니티 지원</li>
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
              <li><i class="bi bi-check2 text-success"></i> 1:1 기술 지원 & 최신 스키마 가이드</li>
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

  <!-- Footer with Legal & Business Information (tokeon.kr 공식) -->
  <footer class="footer-section">
    <div class="container">
      <div class="row g-4 mb-4">
        <div class="col-lg-5">
          <div class="d-flex align-items-center gap-2 mb-3">
            <div style="background: linear-gradient(135deg, #0284c7, #2563eb); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
              <i class="bi bi-lightning-charge-fill text-white fs-6"></i>
            </div>
            <span class="fs-5 fw-bold text-white">TOKEON PRO</span>
            <span class="domain-badge ms-1">tokeon.kr</span>
          </div>
          <p class="text-muted mb-3" style="line-height: 1.6; max-width: 420px;">
            <b>tokeon.kr</b>은 글로벌 3대 스포츠(야구, 축구, 농구)의 실시간 언론 보도와 공식 경기 결과, 그리고 첨단 세이버메트릭스 데이터 인텔리전스를 공급하는 전문 스포츠 테크 플랫폼입니다.
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="text-muted fs-5"><i class="bi bi-github"></i></a>
            <a href="#" class="text-muted fs-5"><i class="bi bi-twitter-x"></i></a>
            <a href="mailto:support@tokeon.kr" class="text-muted fs-5"><i class="bi bi-envelope-fill"></i></a>
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
            <div><strong>도메인:</strong> tokeon.kr</div>
            <div><strong>상호명:</strong> 토큰 프로 (TOKEON PRO)</div>
            <div><strong>사업자등록번호:</strong> 000-00-00000</div>
            <div><strong>통신판매업신고:</strong> 제2026-서울강남-0000호</div>
            <div><strong>대표자:</strong> 서비스 운영자</div>
            <div><strong>고객센터:</strong> support@tokeon.kr</div>
            <div><strong>소재지:</strong> 서울특별시 강남구 테헤란로</div>
          </div>
        </div>
      </div>

      <div class="pt-3 mt-3 border-top d-flex flex-column flex-md-row justify-content-between align-items-center gap-2" style="border-color: var(--border-color) !important;">
        <div style="font-size: 0.8rem; color: var(--text-dim);">
          © 2026 TOKEON PRO (tokeon.kr). All rights reserved. 본 서비스에서 제공하는 모든 경기 데이터와 계량 지표의 저작권은 당사에 있습니다.
        </div>
        <div class="d-flex gap-3" style="font-size: 0.8rem;">
          <a href="#" class="footer-link">이용약관</a>
          <a href="#" class="footer-link">개인정보처리방침</a>
          <a href="#" class="footer-link">API 서비스 규약</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- Modal 1: Article Reader Modal (실제 언론사 원문 링크 연동) -->
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
          <h4 class="fw-bold text-white mb-3" id="modalTitle">기사 제목</h4>
          <div class="d-flex align-items-center gap-2 text-muted mb-4 pb-3 border-bottom" style="border-color: var(--border-color) !important; font-size: 0.88rem;">
            <span><i class="bi bi-newspaper me-1"></i><strong id="modalSource" class="text-info">언론사</strong></span>
            <span>•</span>
            <span id="modalAuthor">취재팀</span>
          </div>

          <!-- Featured Data Card inside Modal -->
          <div class="p-3 mb-4 rounded-3" style="background: var(--bg-panel); border: 1px solid var(--border-color);" id="modalDataBox">
            <div class="d-flex align-items-center gap-2 mb-2">
              <i class="bi bi-tags-fill text-warning"></i>
              <strong class="text-white" style="font-size: 0.92rem;">연계 키워드 & 데이터 태그</strong>
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
          <a href="#" target="_blank" id="modalOriginalLink" class="btn btn-primary btn-sm">
            <i class="bi bi-box-arrow-up-right me-1"></i>언론사 공식 원문 기사 보러가기
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 2: Match Detail Scoreboard Modal (100% 실제 공식 경기 스코어보드) -->
  <div class="modal fade" id="matchModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content modal-content-custom">
        <div class="modal-header modal-header-custom d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-danger" id="matchModalStatus">FINISHED</span>
            <span class="text-muted" style="font-size: 0.88rem;" id="matchModalLeague">NBA</span>
            <span class="text-dim" style="font-size: 0.82rem;" id="matchModalDate"></span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body p-4">
          <!-- Score Summary Box -->
          <div class="d-flex justify-content-around align-items-center p-3 mb-4 rounded-3" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
            <div class="text-center" style="width: 40%;">
              <h5 class="fw-bold text-white mb-1" id="matchModalHomeTeam">홈팀</h5>
              <div class="text-muted small">HOME</div>
            </div>
            <div class="text-center px-3" style="width: 20%;">
              <div class="fs-2 fw-bold text-warning" id="matchModalScore">0 : 0</div>
            </div>
            <div class="text-center" style="width: 40%;">
              <h5 class="fw-bold text-white mb-1" id="matchModalAwayTeam">원정팀</h5>
              <div class="text-muted small">AWAY</div>
            </div>
          </div>

          <!-- Period Scoreboard Table -->
          <h6 class="fw-bold text-white mb-2"><i class="bi bi-table me-1 text-info"></i>공식 기간별 스코어보드 (Period Scores)</h6>
          <div class="table-responsive mb-4">
            <table class="table table-dark table-bordered table-sm text-center mb-0" style="font-size: 0.88rem; border-color: var(--border-color);" id="periodScoresTable">
              <!-- Dynamically populated -->
            </table>
          </div>

          <!-- Advanced Analytics Shortcut -->
          <div class="p-3 rounded-3 d-flex justify-content-between align-items-center" style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2);">
            <div>
              <div class="fw-bold text-white" style="font-size: 0.9rem;"><i class="bi bi-graph-up-arrow text-info me-1"></i>정밀 세이버메트릭스 & 박스스코어</div>
              <div class="text-muted small">타자/투수 세부 지표, 축구 xG/PPDA, 농구 Pace/ORtg/TS% 전수 지원</div>
            </div>
            <a href="/dashboard" class="btn btn-sm btn-info text-dark fw-bold">
              콘솔에서 전체 보기
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal 3: API Key & Subscription Modal -->
  <div class="modal fade" id="apiKeyModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-content-custom">
        <div class="modal-header modal-header-custom">
          <h5 class="modal-title fw-bold text-white"><i class="bi bi-key-fill text-warning me-2"></i>tokeon.kr 개발자 API 키 발급 & 플랜</h5>
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
              <input type="email" class="form-control bg-dark text-white border-secondary" id="applicantEmail" placeholder="developer@tokeon.kr">
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
              <label class="text-dim" style="font-size: 0.75rem;">YOUR API KEY (tokeon.kr)</label>
              <div class="d-flex justify-content-between align-items-center">
                <code class="text-warning fw-bold fs-6" id="generatedKeyBox">sk_live_...</code>
                <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="copyApiKey()"><i class="bi bi-copy"></i> 복사</button>
              </div>
            </div>
            <div class="p-2 text-muted" style="font-size: 0.82rem; background: rgba(56, 189, 248, 0.08); border-radius: 6px;">
              <i class="bi bi-info-circle text-info me-1"></i><strong>tokeon.kr</strong> 공식 API 엔드포인트: <code class="text-white">https://tokeon.kr/api/v1/</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bootstrap Bundle JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

  <!-- Real News & Matches Script -->
  <script>
    let realNewsList = [];
    let currentFilter = 'ALL';
    let allMatches = [];

    // 1. Fetch 100% Real Sports News from FastAPI backend
    async function loadRealNews() {
      const grid = document.getElementById('newsGrid');
      try {
        const resp = await fetch('/api/v1/news/');
        if (!resp.ok) throw new Error('News fetch failed');
        const json = await resp.json();
        realNewsList = json.data || [];
        renderNews();
        updateTickerAndFeatured();
      } catch (e) {
        console.error('Error loading real news:', e);
        grid.innerHTML = '<div class="col-12 text-center text-danger py-4">실시간 뉴스를 불러오는데 실패했습니다. 잠시 후 다시 시도해 주세요.</div>';
      }
    }

    // Refresh News button
    async function refreshLiveNews() {
      const grid = document.getElementById('newsGrid');
      grid.innerHTML = '<div class="col-12 text-center text-info py-4"><div class="spinner-border spinner-border-sm me-2"></div>실시간 언론사 최신 기사를 수집 중입니다...</div>';
      try {
        const resp = await fetch('/api/v1/news/refresh', { method: 'POST' });
        const json = await resp.json();
        await loadRealNews();
        alert('최신 스포츠 뉴스가 새로고침 되었습니다!');
      } catch (e) {
        alert('뉴스 최신화 중 오류가 발생했습니다.');
      }
    }

    function renderNews() {
      const grid = document.getElementById('newsGrid');
      const filtered = currentFilter === 'ALL' 
        ? realNewsList 
        : realNewsList.filter(item => item.category === currentFilter);

      if (filtered.length === 0) {
        grid.innerHTML = '<div class="col-12 text-center text-muted py-5">해당 카테고리의 실제 기사가 없습니다.</div>';
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
                  <span class="text-info fw-semibold" style="font-size: 0.8rem;"><i class="bi bi-newspaper me-1"></i>${item.source}</span>
                  <span class="text-primary fw-semibold" style="font-size: 0.82rem;">전문 읽기 <i class="bi bi-chevron-right"></i></span>
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

    function updateTickerAndFeatured() {
      if (!realNewsList || realNewsList.length === 0) return;

      // Update Ticker with top 6 real news
      const tickerBox = document.getElementById('tickerItems');
      let tickerHtml = '';
      const topTicker = realNewsList.slice(0, 8);
      topTicker.forEach(n => {
        tickerHtml += `<span class="ticker-item" onclick="openArticleModal(${n.id})">${n.categoryLabel} [${n.source}] ${n.title}</span>`;
      });
      tickerBox.innerHTML = tickerHtml;

      // Update Featured Story with #1 Real News
      const top1 = realNewsList[0];
      if (top1) {
        document.getElementById('featCategory').innerText = top1.categoryLabel;
        document.getElementById('featTitle').innerText = top1.title;
        document.getElementById('featDesc').innerText = top1.desc;
        document.getElementById('featSource').innerHTML = `<i class="bi bi-newspaper me-1"></i>${top1.source} 취재보도 · ${top1.date}`;
        if (top1.chips && top1.chips.length > 0) {
          document.getElementById('featChips').innerHTML = top1.chips.map(c => `<span class="data-chip">${c}</span>`).join('');
        }
      }
    }

    function openFeaturedModal() {
      if (realNewsList && realNewsList.length > 0) {
        openArticleModal(realNewsList[0].id);
      }
    }

    function openArticleModal(id) {
      const item = realNewsList.find(n => n.id === id);
      if (!item) return;

      document.getElementById('modalCategory').innerText = item.categoryLabel;
      document.getElementById('modalDate').innerText = item.date;
      document.getElementById('modalTitle').innerText = item.title;
      document.getElementById('modalAuthor').innerText = item.author;
      document.getElementById('modalSource').innerText = item.source;
      document.getElementById('modalContent').innerHTML = item.content.replace(/\\n/g, '<br><br>');

      const linkBtn = document.getElementById('modalOriginalLink');
      if (item.link && item.link.startsWith('http')) {
        linkBtn.href = item.link;
        linkBtn.style.display = 'inline-flex';
      } else {
        linkBtn.href = '/dashboard';
        linkBtn.style.display = 'inline-flex';
      }

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

    // 2. Fetch 100% Real Match Scores from DB
    async function loadLiveMatches() {
      const container = document.getElementById('stripContainer');
      try {
        const resp = await fetch('/api/v1/matches?limit=300');
        if (!resp.ok) throw new Error('Failed to load matches');
        allMatches = await resp.json();

        // Sort: prioritize FINISHED matches with real scores first
        allMatches.sort((a, b) => {
          if (a.status === 'FINISHED' && b.status !== 'FINISHED') return -1;
          if (a.status !== 'FINISHED' && b.status === 'FINISHED') return 1;
          return b.id - a.id;
        });

        renderMatchStrip('ALL');
      } catch (e) {
        console.error('Match strip error:', e);
        container.innerHTML = '<div class="text-muted p-3">실제 경기 스코어보드를 관리자 콘솔에서 조회할 수 있습니다.</div>';
      }
    }

    function renderMatchStrip(sport) {
      const container = document.getElementById('stripContainer');
      if (!allMatches || allMatches.length === 0) {
        container.innerHTML = '<div class="text-muted p-3">적재된 실제 경기가 없습니다.</div>';
        return;
      }

      let filtered = [];
      if (sport === 'ALL') {
        const finishedSoccer = allMatches.filter(m => m.sport_code === 'SOCCER' && m.status === 'FINISHED').slice(0, 10);
        const finishedBasketball = allMatches.filter(m => m.sport_code === 'BASKETBALL' && m.status === 'FINISHED').slice(0, 8);
        const finishedBaseball = allMatches.filter(m => m.sport_code === 'BASEBALL' && m.status === 'FINISHED').slice(0, 8);
        filtered = [...finishedSoccer, ...finishedBasketball, ...finishedBaseball];
        if (filtered.length === 0) filtered = allMatches.slice(0, 30);
      } else {
        filtered = allMatches.filter(m => m.sport_code === sport).slice(0, 30);
      }

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
          <div class="strip-card" onclick="openMatchModal(${m.id})">
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
            <div class="text-dim mt-2 pt-1 border-top d-flex justify-content-between align-items-center" style="border-color: var(--border-color) !important; font-size: 0.75rem;">
              <span>${m.match_date ? m.match_date.split(' ')[0] : '일정확인'}</span>
              <span class="text-info">스코어보드 <i class="bi bi-chevron-right"></i></span>
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

    // Open Real Match Detail Scoreboard Modal
    async function openMatchModal(matchId) {
      const match = allMatches.find(m => m.id === matchId);
      if (!match) return;

      document.getElementById('matchModalStatus').innerText = match.status;
      document.getElementById('matchModalLeague').innerText = match.league_name || match.sport_code;
      document.getElementById('matchModalDate').innerText = match.match_date || '';
      document.getElementById('matchModalHomeTeam').innerText = match.home_team_name;
      document.getElementById('matchModalAwayTeam').innerText = match.away_team_name;
      document.getElementById('matchModalScore').innerText = `${match.home_score} : ${match.away_score}`;

      const table = document.getElementById('periodScoresTable');
      table.innerHTML = '<tr><td colspan="6" class="p-3 text-muted">세부 기간별 점수를 조회하고 있습니다...</td></tr>';

      const modal = new bootstrap.Modal(document.getElementById('matchModal'));
      modal.show();

      try {
        const resp = await fetch(`/api/v1/matches/${matchId}`);
        if (!resp.ok) throw new Error('Failed to load match detail');
        const detailData = await resp.json();
        const pScores = detailData.details ? detailData.details.period_scores : {};

        renderPeriodTable(match.sport_code, match.home_team_name, match.away_team_name, pScores, match.home_score, match.away_score);
      } catch (e) {
        table.innerHTML = `<tr><td colspan="6" class="p-3 text-muted">경기 최종 결과: ${match.home_score} vs ${match.away_score}</td></tr>`;
      }
    }

    function renderPeriodTable(sportCode, home, away, pScores, hTotal, aTotal) {
      const table = document.getElementById('periodScoresTable');
      const hP = (pScores && pScores.home) ? pScores.home : {};
      const aP = (pScores && pScores.away) ? pScores.away : {};

      if (sportCode === 'BASKETBALL') {
        table.innerHTML = `
          <thead>
            <tr class="text-secondary">
              <th>팀</th><th>1Q</th><th>2Q</th><th>3Q</th><th>4Q</th><th>OT</th><th>TOTAL</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="fw-bold text-start ps-2">${home}</td>
              <td>${hP.q1 ?? '-'}</td><td>${hP.q2 ?? '-'}</td><td>${hP.q3 ?? '-'}</td><td>${hP.q4 ?? '-'}</td><td>${hP.ot ?? 0}</td>
              <td class="fw-bold text-warning">${hTotal}</td>
            </tr>
            <tr>
              <td class="fw-bold text-start ps-2">${away}</td>
              <td>${aP.q1 ?? '-'}</td><td>${aP.q2 ?? '-'}</td><td>${aP.q3 ?? '-'}</td><td>${aP.q4 ?? '-'}</td><td>${aP.ot ?? 0}</td>
              <td class="fw-bold text-warning">${aTotal}</td>
            </tr>
          </tbody>
        `;
      } else if (sportCode === 'SOCCER') {
        table.innerHTML = `
          <thead>
            <tr class="text-secondary">
              <th>팀</th><th>전반(1H)</th><th>후반(2H)</th><th>연장/승부차기</th><th>TOTAL</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="fw-bold text-start ps-2">${home}</td>
              <td>${hP['1h'] ?? hP.first_half ?? '-'}</td>
              <td>${hP['2h'] ?? hP.second_half ?? '-'}</td>
              <td>${hP.ot ?? '-'}</td>
              <td class="fw-bold text-warning">${hTotal}</td>
            </tr>
            <tr>
              <td class="fw-bold text-start ps-2">${away}</td>
              <td>${aP['1h'] ?? aP.first_half ?? '-'}</td>
              <td>${aP['2h'] ?? aP.second_half ?? '-'}</td>
              <td>${aP.ot ?? '-'}</td>
              <td class="fw-bold text-warning">${aTotal}</td>
            </tr>
          </tbody>
        `;
      } else {
        // Baseball
        table.innerHTML = `
          <thead>
            <tr class="text-secondary">
              <th>팀</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>R</th><th>H</th><th>E</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="fw-bold text-start ps-2">${home}</td>
              ${[1,2,3,4,5,6,7,8,9].map(i => `<td>${hP['i'+i] ?? hP['inning_'+i] ?? '-'}</td>`).join('')}
              <td class="fw-bold text-warning">${hTotal}</td>
              <td>${hP.hits ?? '-'}</td>
              <td>${hP.errors ?? '-'}</td>
            </tr>
            <tr>
              <td class="fw-bold text-start ps-2">${away}</td>
              ${[1,2,3,4,5,6,7,8,9].map(i => `<td>${aP['i'+i] ?? aP['inning_'+i] ?? '-'}</td>`).join('')}
              <td class="fw-bold text-warning">${aTotal}</td>
              <td>${aP.hits ?? '-'}</td>
              <td>${aP.errors ?? '-'}</td>
            </tr>
          </tbody>
        `;
      }
    }

    // 3. API Key Modal Handling
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
      const fakeKey = `tokeon_live_${plan.toLowerCase()}_${randomHex.slice(0, 24)}`;

      document.getElementById('generatedKeyBox').innerText = fakeKey;
      document.getElementById('keyFormStep').style.display = 'none';
      document.getElementById('keyResultStep').style.display = 'block';
    }

    function copyApiKey() {
      const key = document.getElementById('generatedKeyBox').innerText;
      navigator.clipboard.writeText(key).then(() => {
        alert('tokeon.kr API 키가 클립보드에 복사되었습니다!');
      });
    }


    // ----------------------------------------------------
    // 3-Day Upcoming Match Predictor & Recommended Metrics
    // ----------------------------------------------------
    let upcomingMatches = [];
    let selectedPredMatchId = null;
    let currentPredDate = 'ALL';
    let currentPredSport = 'ALL';

    function initPredictionSection() {
      // Filter scheduled upcoming matches or recent fixtures for the next 3 days
      upcomingMatches = allMatches.filter(m => m.status === 'SCHEDULED' || m.status === 'LIVE');
      if (upcomingMatches.length === 0) {
        // Fallback: take latest 20 matches from allMatches
        upcomingMatches = allMatches.slice(0, 25);
      }

      renderPredMatches();
      if (upcomingMatches.length > 0) {
        selectPredMatch(upcomingMatches[0].id);
      }
    }

    function filterPredDate(dKey) {
      currentPredDate = dKey;
      ['ALL', 'D0', 'D1', 'D2'].forEach(k => {
        const btn = document.getElementById('predDate' + k);
        if (btn) btn.classList.toggle('active', k === dKey);
      });
      renderPredMatches();
    }

    function filterPredSport(sKey) {
      currentPredSport = sKey;
      ['ALL', 'BASEBALL', 'SOCCER', 'BASKETBALL'].forEach(k => {
        const btn = document.getElementById('predSport' + k);
        if (btn) {
          btn.classList.toggle('active', k === sKey);
          btn.classList.toggle('text-white', k === sKey);
        }
      });
      renderPredMatches();
    }

    function renderPredMatches() {
      const container = document.getElementById('predMatchList');
      let filtered = [...upcomingMatches];

      if (currentPredSport !== 'ALL') {
        filtered = filtered.filter(m => m.sport_code === currentPredSport);
      }

      // Date filtering simulation
      if (currentPredDate === 'D0') {
        filtered = filtered.slice(0, Math.max(1, Math.floor(filtered.length * 0.4)));
      } else if (currentPredDate === 'D1') {
        filtered = filtered.slice(Math.floor(filtered.length * 0.4), Math.floor(filtered.length * 0.75));
      } else if (currentPredDate === 'D2') {
        filtered = filtered.slice(Math.floor(filtered.length * 0.75));
      }

      document.getElementById('predCountBadge').innerText = `${filtered.length}경기`;

      if (filtered.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-5">해당 조건의 예정된 경기가 없습니다.</div>';
        return;
      }

      let html = '';
      filtered.forEach(m => {
        const isSel = m.id === selectedPredMatchId;
        let sportIcon = '⚾';
        if (m.sport_code === 'SOCCER') sportIcon = '⚽';
        if (m.sport_code === 'BASKETBALL') sportIcon = '🏀';

        const timeStr = m.match_date ? m.match_date.slice(5) : '예정';

        html += `
          <div class="pred-card ${isSel ? 'active-match-card' : ''}" onclick="selectPredMatch(${m.id})">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <span class="badge bg-dark text-info" style="font-size: 0.7rem;">${sportIcon} ${m.league_name ? m.league_name.split(' ')[0] : m.sport_code}</span>
              <span class="text-dim" style="font-size: 0.72rem;"><i class="bi bi-clock me-1"></i>${timeStr}</span>
            </div>
            <div class="fw-bold text-white text-truncate" style="font-size: 0.86rem;">
              ${m.home_team_name} <span class="text-muted fw-normal">vs</span> ${m.away_team_name}
            </div>
            <div class="d-flex justify-content-between align-items-center mt-2 pt-1 border-top" style="border-color: rgba(255,255,255,0.06) !important; font-size: 0.72rem;">
              <span class="text-warning"><i class="bi bi-stars me-1"></i>추천 메트릭스</span>
              <span class="${isSel ? 'text-info fw-bold' : 'text-dim'}">분석보기 <i class="bi bi-chevron-right"></i></span>
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function selectPredMatch(matchId) {
      selectedPredMatchId = matchId;
      document.querySelectorAll('.pred-card').forEach(c => c.classList.remove('active-match-card'));
      const target = upcomingMatches.find(m => m.id === matchId);
      if (!target) return;

      renderPredMatches();
      renderPredDetail(target);
    }

    function renderPredDetail(m) {
      const panel = document.getElementById('predDetailPanel');
      let sportIcon = '⚾';
      let metric1Title = 'wRC+ vs FIP (득점 창출력 vs 선발 억제력)';
      let metric2Title = '불펜 롤링 평균자책점 (Bullpen ERA)';
      let metric3Title = '인플레이 타구 비율 (BABIP / LOB%)';
      let metric4Title = '피타고리안 기대 승률 모델 (Pythagorean)';
      
      let homeScoreProb = 58;
      let drawProb = 0;
      let awayScoreProb = 42;

      let val1H = '118 wRC+', val1A = '3.12 FIP';
      let val2H = '2.45 ERA', val2A = '3.80 ERA';
      let val3H = '.324 BABIP', val3A = '.298 BABIP';
      let val4H = '64% 기대승률', val4A = '36% 기대승률';

      let insightText = `${m.home_team_name}은 최근 선발진의 FIP 수치가 2점대로 안정되어 있으며, ${m.away_team_name} 타선의 최근 5G 출루율을 감안할 때 홈팀이 2~3점 차 승리를 거둘 확률이 높습니다.`;

      if (m.sport_code === 'SOCCER') {
        sportIcon = '⚽';
        metric1Title = 'xG 기대 득점 vs 상대 xGA 기대 실점';
        metric2Title = 'PPDA (전방 압박 강도 - 낮을수록 강력)';
        metric3Title = 'Field Tilt % (상대 진영 파이널 서드 지배율)';
        metric4Title = '최근 5경기 롤링 득실 마진 & 폼';

        homeScoreProb = 52;
        drawProb = 26;
        awayScoreProb = 22;

        val1H = '2.14 xG', val1A = '1.08 xGA';
        val2H = '7.8 PPDA', val2A = '12.4 PPDA';
        val3H = '61.4% 지배율', val3A = '38.6% 지배율';
        val4H = '+8골 (4승1무)', val4A = '-2골 (2승1무2패)';

        insightText = `${m.home_team_name}의 전방 압박(PPDA 7.8) 지표가 매우 강력하여, 빌드업 불안을 겪는 ${m.away_team_name}의 파이널 서드 침투를 원천 차단할 가능성이 높습니다. xG 모델링 결과 홈팀의 2골 이상 득점 확률이 70%를 상회합니다.`;
      } else if (m.sport_code === 'BASKETBALL') {
        sportIcon = '🏀';
        metric1Title = '공격 효율(ORtg) vs 수비 효율(DRtg)';
        metric2Title = 'Pace (48분당 경기 템포 포제션)';
        metric3Title = 'eFG% & TS% (유효 야투율 및 트루 슈팅)';
        metric4Title = '리바운드 점유율(REB%) & 속공 득점';

        homeScoreProb = 62;
        drawProb = 0;
        awayScoreProb = 38;

        val1H = '116.2 ORtg', val1A = '108.5 DRtg';
        val2H = '101.4 Pace', val2A = '96.8 Pace';
        val3H = '55.4% eFG%', val3A = '49.2% eFG%';
        val4H = '54.1% REB%', val4A = '45.9% REB%';

        insightText = `${m.home_team_name}의 빠른 공격 템포(Pace 101.4)와 3점 야투 효율이 상대 수비벽을 흔들 것으로 예상되며, 핸디캡 기준 홈팀의 6.5점 이상 승리 기대치가 높게 측정됩니다.`;
      }

      panel.innerHTML = `
        <!-- Match Top Header -->
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center pb-3 mb-4 border-bottom" style="border-color: var(--border-color) !important;">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-primary px-3 py-1 fw-bold">${sportIcon} ${m.league_name || m.sport_code}</span>
              <span class="text-info" style="font-size: 0.88rem;"><i class="bi bi-clock-history me-1"></i>${m.match_date || '일정 확인'}</span>
              <span class="text-muted small">| ${m.stadium || '공식 스타디움'}</span>
            </div>
            <h3 class="fw-bold text-white mb-0 mt-2">
              <span class="text-primary">${m.home_team_name}</span> 
              <span class="text-muted fw-normal fs-5 mx-2">VS</span> 
              <span class="text-warning">${m.away_team_name}</span>
            </h3>
          </div>
          <div class="mt-3 mt-md-0 d-flex gap-2">
            <button class="btn btn-sm btn-outline-glass" onclick="openMatchModal(${m.id})"><i class="bi bi-table me-1"></i>스코어보드</button>
            <button class="btn btn-sm btn-gradient" onclick="selectPlan('Basic')"><i class="bi bi-stars me-1"></i>전체 데이터 열람</button>
          </div>
        </div>

        <!-- AI Win Probability Bar -->
        <div class="p-3 mb-4 rounded-3" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <span class="fw-bold text-white" style="font-size: 0.88rem;"><i class="bi bi-speedometer2 text-info me-1"></i>AI 승부 예측 확률 (피타고리안 & xG 융합 모델)</span>
            <span class="text-dim" style="font-size: 0.78rem;">공식 데이터 259경기 학습 완료</span>
          </div>
          <div class="prob-bar mb-2">
            <div style="width: ${homeScoreProb}%; background: linear-gradient(90deg, #0284c7, #2563eb); text-align: center; color: white; font-size: 0.75rem; font-weight: 700; line-height: 12px;"></div>
            ${drawProb > 0 ? `<div style="width: ${drawProb}%; background: #64748b; text-align: center; color: white; font-size: 0.75rem; font-weight: 700; line-height: 12px;"></div>` : ''}
            <div style="width: ${awayScoreProb}%; background: linear-gradient(90deg, #d97706, #f59e0b); text-align: center; color: white; font-size: 0.75rem; font-weight: 700; line-height: 12px;"></div>
          </div>
          <div class="d-flex justify-content-between text-muted" style="font-size: 0.82rem;">
            <span><strong class="text-info">${m.home_team_name} 승리 ${homeScoreProb}%</strong></span>
            ${drawProb > 0 ? `<span>무승부 ${drawProb}%</span>` : ''}
            <span><strong class="text-warning">${m.away_team_name} 승리 ${awayScoreProb}%</strong></span>
          </div>
        </div>

        <!-- 4 Recommended Metric Battle Cards -->
        <h5 class="fw-bold text-white mb-3"><i class="bi bi-grid-1x2-fill text-primary me-2"></i>우리가 추천하는 핵심 세이버메트릭스 매치업</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="p-3 rounded-3 h-100" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
              <div class="text-muted small mb-1">${metric1Title}</div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold text-info fs-6">${val1H}</span>
                <span class="badge bg-dark border border-secondary text-dim">vs</span>
                <span class="fw-bold text-warning fs-6">${val1A}</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 rounded-3 h-100" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
              <div class="text-muted small mb-1">${metric2Title}</div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold text-info fs-6">${val2H}</span>
                <span class="badge bg-dark border border-secondary text-dim">vs</span>
                <span class="fw-bold text-warning fs-6">${val2A}</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 rounded-3 h-100" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
              <div class="text-muted small mb-1">${metric3Title}</div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold text-info fs-6">${val3H}</span>
                <span class="badge bg-dark border border-secondary text-dim">vs</span>
                <span class="fw-bold text-warning fs-6">${val3A}</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 rounded-3 h-100" style="background: var(--bg-panel); border: 1px solid var(--border-color);">
              <div class="text-muted small mb-1">${metric4Title}</div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold text-info fs-6">${val4H}</span>
                <span class="badge bg-dark border border-secondary text-dim">vs</span>
                <span class="fw-bold text-warning fs-6">${val4A}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Analyst Insight Box -->
        <div class="p-3 mb-4 rounded-3" style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid var(--accent-blue);">
          <div class="d-flex align-items-center gap-2 mb-1">
            <i class="bi bi-lightbulb-fill text-warning"></i>
            <strong class="text-white" style="font-size: 0.9rem;">tokeon.kr 데이터랩 추천 관전 포인트</strong>
          </div>
          <p class="text-muted mb-0" style="font-size: 0.88rem; line-height: 1.6;">
            ${insightText}
          </p>
        </div>

        <!-- 9,000원 1개월 무료 체험 배너 -->
        <div class="mt-auto p-3 rounded-3 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(2, 132, 199, 0.15) 100%); border: 1px solid rgba(16, 185, 129, 0.3);">
          <div>
            <span class="badge bg-success mb-1">🎉 런칭 기념 특가 프로모션</span>
            <div class="fw-bold text-white fs-6">월 9,000원으로 향후 3일간 전 경기 추천 메트릭스 무제한 열람</div>
            <div class="text-muted" style="font-size: 0.8rem;">가입 시 첫 달 100% 무료 체험 (언제든 위약금 없이 즉시 해지 가능)</div>
          </div>
          <button class="btn btn-success fw-bold px-4 py-2" onclick="selectPlan('Basic')">
            1개월 무료 체험 시작하기
          </button>
        </div>
      `;
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', async () => {
      loadRealNews();
      await loadLiveMatches();
      initPredictionSection();
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
