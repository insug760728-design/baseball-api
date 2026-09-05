# 🏆 글로벌 스포츠 데이터 수집 & 앱 관리 허브 (FastAPI)

공식 스포츠 사이트에서 **경기 일정**, **경기 결과(스코어)**, **세부 스코어보드**, **득점 타임라인 이벤트**, **선수별 상세 수치(골, 타점, 어시스트, 슈팅 등)**를 자동으로 수집하고, 관리자가 원하는 수치로 **직접 수정/가공**하여 **본인이 제작하는 모바일/웹 앱에 최적화된 JSON 데이터로 전송**할 수 있는 Python FastAPI 기반의 백엔드 시스템입니다.

---

## 🎯 지원 대상 종목 및 리그

1. **🇪🇺 유럽 축구 & 챔피언스리그 & 유럽파**
   - **5대 리그**: 잉글랜드 프리미어리그(EPL), 스페인 라리가, 독일 분데스리가, 이탈리아 세리에 A, 프랑스 리그 1
   - **UEFA 챔피언스리그 (UCL)**
   - **⭐ 유럽파 코리안리거 전용**: 손흥민(토트넘), 이강인(PSG), 김민재(뮌헨), 황희찬(울버햄튼) 등
2. **🇺🇸 미국 메이저리그 (MLB 야구)**
   - 오타니, 김하성, 이정후 등 주요 경기 및 타자/투수 상세 스탯
3. **🇰🇷 대한민국 3대 프로 스포츠**
   - 한국 축구: **K리그1**
   - 한국 야구: **KBO 리그**
   - 한국 농구: **KBL** (쿼터별 점수, PTS/REB/AST)
4. **🇯🇵 일본 3대 프로 스포츠**
   - 일본 축구: **J1리그**
   - 일본 야구: **NPB**
   - 일본 농구: **B.LEAGUE (B리그)**

---

## 🚀 빠른 시작 가이드

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **관리 대시보드 웹 화면**: [http://localhost:8000/](http://localhost:8000/)
- **대화형 Swagger API 명세서**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 주요 기능 및 웹 화면

1. **공식 사이트 최신 데이터 수집 (원클릭 동기화)**
   - 웹 화면 상단에서 리그를 선택하거나 `⭐ [전체 리그 일괄 수집]`을 클릭하면 공식 사이트로부터 일정, 결과, 세부 수치를 즉시 수집합니다.
2. **경기 일정 및 상세 결과 조회**
   - 축구 전/후반 스코어, 야구 1~9회 이닝별 스코어, 농구 쿼터별 스코어
   - 득점 타임라인(몇 분에 누가 어떤 방식으로 골을 넣었는지, 어시스트는 누구인지)
3. **선수별 세부 수치 실시간 수정 (Override 기능)**
   - 수집된 선수의 득점(골/타점), 도움(어시스트), 슈팅/타수 등을 관리자가 원하는 값으로 변경
   - 공식 사이트 원본 데이터는 보존되며, 수정된 수치는 `is_override: true`로 마킹되어 앱에 즉시 우선 전달됩니다.
4. **내가 만드는 앱으로 바로 보내는 최종 JSON 규격**
   - 웹 화면 우측 하단에서 앱으로 전송될 완성형 JSON 페이로드를 실시간 확인 및 복사 가능

---

## 📡 사용자 앱(Flutter, React, Swift, Kotlin 등) 연동 API

### 1. 경기 목록 조회
- `GET /api/v1/matches?league=EPL`
- `GET /api/v1/matches?sport=SOCCER&status=FINISHED`

### 2. 경기 상세 및 선수 기록 조회
- `GET /api/v1/matches/{match_id}`

### 3. 선수 수치 직접 수정 (관리자용)
- `PATCH /api/v1/players/stats/{stat_id}`
```json
{
  "points": 3,
  "assists": 2,
  "shots": 5,
  "override_reason": "앱 화면 표기용 수동 조정"
}
```

### 4. 내 앱 전송 전용 최종 JSON 페이로드 (추천 ⭐)
- `GET /api/v1/export/app-payload/{match_id}`

**응답 규격 예시:**
```json
{
  "client_app_payload_version": "1.0",
  "sport": "SOCCER",
  "league": "잉글랜드 프리미어리그 (EPL)",
  "match_id": 1,
  "schedule": {
    "date": "2026-09-05 20:30",
    "stadium": "토트넘 홋스퍼 스타디움",
    "status": "FINISHED"
  },
  "score_summary": {
    "home_team": "토트넘 홋스퍼",
    "away_team": "아스널 FC",
    "final_score": "3 : 1",
    "home_score": 3,
    "away_score": 1,
    "is_user_modified": false
  },
  "breakdown": {
    "periods": {
      "first_half": {"home": 1, "away": 0},
      "second_half": {"home": 2, "away": 1}
    },
    "team_stats": {
      "possession": {"home": "54%", "away": "46%"},
      "shots": {"home": 15, "away": 11}
    }
  },
  "timeline_events": [
    {
      "time_display": "24'",
      "event_type": "GOAL",
      "player_name": "손흥민",
      "assist_player_name": "제임스 매디슨",
      "score_after": "1-0",
      "description": "오른발 감아차기 득점"
    }
  ],
  "roster_and_stats": {
    "home": {
      "team": "토트넘 홋스퍼",
      "players": [
        {
          "player_name": "손흥민",
          "back_number": 7,
          "position": "FW",
          "points": 3,
          "assists": 2,
          "shots": 5,
          "is_override": true
        }
      ]
    },
    "away": {
      "team": "아스널 FC",
      "players": [...]
    }
  }
}
```

---

## 📂 프로젝트 구조
```
c:\Users\user\Desktop\api\
├── app/
│   ├── core/               # 데이터베이스 설정 및 스포츠 카탈로그 정의
│   │   ├── config.py
│   │   ├── database.py
│   │   └── sports_catalog.py
│   ├── models/             # SQLAlchemy ORM (Match, MatchDetail, MatchEvent, PlayerMatchStat)
│   │   └── models.py
│   ├── schemas/            # Pydantic DTO (요청/응답/수정 규격)
│   │   └── schemas.py
│   ├── scrapers/           # 공식 사이트 데이터 수집 엔진
│   │   ├── base.py
│   │   ├── unified_sports_scraper.py
│   │   ├── official_football_scraper.py
│   │   └── official_baseball_scraper.py
│   ├── services/           # 비즈니스 로직 및 수치 오버라이드 관리
│   │   └── match_service.py
│   ├── api/v1/             # REST API 라우터 (matches, players, crawler, export)
│   ├── templates/          # 브라우저 관리 대시보드 (index.html)
│   └── main.py             # FastAPI 진입점 및 CORS 허용
├── test_all_sports.py      # 전체 스포츠 리그 및 API 자동 검증 스크립트
├── requirements.txt        # 패키지 의존성
└── README.md
```