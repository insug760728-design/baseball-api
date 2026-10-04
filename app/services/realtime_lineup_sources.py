"""
실시간 공식 라인업 공급원 (API 키 불필요)

- 축구: ESPN 공개 API (site.api.espn.com) — 전 세계 리그/국가대표 선발 XI·교체·포메이션
- KBO : 네이버 스포츠 API preview(경기 전 확정 라인업) → record(경기 중/후 실제 출전 타순)
- NPB : 네이버 스포츠 API record(경기 시작 후 실제 출전 타순)

※ 공급원에서 받지 못하면 빈 배열을 반환한다. (가짜/고정 선수 명단으로 채우지 않는다)
"""
import json
import logging
import time
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("RealtimeLineup")

_CACHE: Dict[str, Tuple[float, Any]] = {}

_ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/all"
_NAVER_BASE = "https://api-gw.sports.naver.com/schedule/games"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://m.sports.naver.com/",
    "Accept": "application/json",
}


def _get_json(url: str, ttl: int, timeout: int = 8) -> Optional[Dict[str, Any]]:
    now = time.time()
    hit = _CACHE.get(url)
    if hit and now - hit[0] < ttl:
        return hit[1]
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        _CACHE[url] = (now, data)
        if len(_CACHE) > 600:
            for k in sorted(_CACHE, key=lambda k: _CACHE[k][0])[:200]:
                _CACHE.pop(k, None)
        return data
    except Exception as e:
        logger.warning(f"[RealtimeLineup] request failed {url}: {e}")
        return None


def _parse_kst(match_date: Optional[str]) -> Optional[datetime]:
    if not match_date:
        return None
    s = str(match_date).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[: len(datetime.now().strftime(fmt))], fmt)
        except Exception:
            continue
    return None


def _teams_match(a: str, b: str) -> bool:
    from app.services.live_api_sports_service import teams_match
    try:
        return bool(teams_match(a or "", b or ""))
    except Exception:
        return False


# ============================================================
# ⚽ 축구 — ESPN
# ============================================================
def _soccer_pos(abbr: str) -> str:
    a = (abbr or "").upper()
    if a in ("G", "GK"):
        return "GK"
    if a.startswith("D") or a.startswith("CD") or a in ("LB", "RB", "SW", "LWB", "RWB", "CB"):
        return "DF"
    if a.startswith("F") or a.startswith("S") or a in ("CF", "LW", "RW", "ST"):
        return "FW"
    if a.startswith("M") or a.startswith("A") or a in ("DM", "CM", "AM", "LM", "RM"):
        return "MF"
    return a or "MF"


def _ko_player_name(en: str) -> str:
    try:
        from app.services.player_translation import FULL_NAMES
        return FULL_NAMES.get(en) or FULL_NAMES.get(en.replace(" ", "")) or en
    except Exception:
        return en


def find_espn_soccer_event(home_name: str, away_name: str, match_date: Optional[str]) -> Optional[Dict[str, Any]]:
    """KST 경기 일시 + 한글/영문 팀명으로 ESPN 이벤트를 찾는다."""
    kst = _parse_kst(match_date)
    if not kst:
        return None
    utc = kst - timedelta(hours=9)
    dates = sorted({(utc - timedelta(days=1)).strftime("%Y%m%d"), utc.strftime("%Y%m%d"), (utc + timedelta(days=1)).strftime("%Y%m%d")})
    best = None
    best_diff = None
    for d in dates:
        data = _get_json(f"{_ESPN_BASE}/scoreboard?dates={d}&limit=1000", ttl=180)
        for ev in (data or {}).get("events", []):
            comps = (ev.get("competitions") or [{}])[0].get("competitors") or []
            e_home = next((c for c in comps if c.get("homeAway") == "home"), None)
            e_away = next((c for c in comps if c.get("homeAway") == "away"), None)
            if not e_home or not e_away:
                continue
            h_names = [e_home.get("team", {}).get(k, "") for k in ("displayName", "shortDisplayName", "name")]
            a_names = [e_away.get("team", {}).get(k, "") for k in ("displayName", "shortDisplayName", "name")]
            straight = any(_teams_match(n, home_name) for n in h_names if n) and any(_teams_match(n, away_name) for n in a_names if n)
            swapped = any(_teams_match(n, away_name) for n in h_names if n) and any(_teams_match(n, home_name) for n in a_names if n)
            if not (straight or swapped):
                continue
            try:
                ev_utc = datetime.strptime(ev.get("date", "")[:16], "%Y-%m-%dT%H:%M")
                diff = abs((ev_utc - utc).total_seconds())
            except Exception:
                diff = 10 ** 9
            if diff > 36 * 3600:
                continue
            if best_diff is None or diff < best_diff:
                best, best_diff = {"id": ev.get("id"), "swapped": (swapped and not straight), "status": ev.get("status", {}).get("type", {}).get("name")}, diff
    return best


def fetch_espn_soccer_lineup(home_name: str, away_name: str, match_date: Optional[str], force: bool = False) -> Optional[Dict[str, Any]]:
    ev = find_espn_soccer_event(home_name, away_name, match_date)
    if not ev or not ev.get("id"):
        return None
    summary = _get_json(f"{_ESPN_BASE}/summary?event={ev['id']}", ttl=20 if force else 60)
    rosters = (summary or {}).get("rosters") or []

    out = {"home": {"xi": [], "subs": [], "formation": None}, "away": {"xi": [], "subs": [], "formation": None}}
    for r in rosters:
        side = r.get("homeAway")
        if side not in ("home", "away"):
            continue
        if ev.get("swapped"):
            side = "away" if side == "home" else "home"
        out[side]["formation"] = r.get("formation")
        for idx, p in enumerate(r.get("roster") or []):
            ath = p.get("athlete") or {}
            en = ath.get("displayName") or ath.get("fullName") or ""
            if not en:
                continue
            jersey = p.get("jersey")
            try:
                jersey = int(jersey) if jersey not in (None, "") else None
            except Exception:
                pass
            entry = {
                "id": ath.get("id"),
                "name": _ko_player_name(en),
                "name_en": en,
                "number": jersey,
                "pos": _soccer_pos((p.get("position") or {}).get("abbreviation")) if p.get("starter") else "SUB",
                "grid": None,
            }
            (out[side]["xi"] if p.get("starter") else out[side]["subs"]).append(entry)

    confirmed = len(out["home"]["xi"]) >= 11 and len(out["away"]["xi"]) >= 11
    return {
        "event_id": ev["id"],
        "event_status": ev.get("status"),
        "confirmed": confirmed,
        "home": out["home"],
        "away": out["away"],
        "source": "espn",
    }


# ============================================================
# ⚾ KBO / NPB — 네이버 스포츠
# ============================================================
def _naver_find_game(home_name: str, away_name: str, match_date: Optional[str], league: str) -> Optional[Dict[str, Any]]:
    kst = _parse_kst(match_date)
    if not kst:
        return None
    up, cat = ("kbaseball", "kbo") if league == "KBO" else ("wbaseball", "npb")
    day = kst.strftime("%Y-%m-%d")
    data = _get_json(f"{_NAVER_BASE}?fields=basic&upperCategoryId={up}&categoryId={cat}&fromDate={day}&toDate={day}&size=50", ttl=120)
    games = ((data or {}).get("result") or {}).get("games") or []
    best = None
    best_diff = None
    for g in games:
        gh, ga = g.get("homeTeamName", ""), g.get("awayTeamName", "")
        if not (_teams_match(gh, home_name) and _teams_match(ga, away_name)):
            continue
        try:
            gdt = datetime.strptime(g.get("gameDateTime", "")[:16], "%Y-%m-%dT%H:%M")
            diff = abs((gdt - kst).total_seconds())
        except Exception:
            diff = 10 ** 9
        if best_diff is None or diff < best_diff:
            best, best_diff = g, diff
    return best


def fetch_naver_baseball_lineup(home_name: str, away_name: str, match_date: Optional[str], league: str, force: bool = False) -> Optional[Dict[str, Any]]:
    g = _naver_find_game(home_name, away_name, match_date, league)
    if not g or not g.get("gameId"):
        return None
    gid = g["gameId"]
    ttl = 15 if force else 45
    home_lu: List[Dict[str, Any]] = []
    away_lu: List[Dict[str, Any]] = []
    home_sp: Dict[str, Any] = {}
    away_sp: Dict[str, Any] = {}

    # 1) 경기 전 확정 라인업 (KBO preview)
    prev = _get_json(f"{_NAVER_BASE}/{gid}/preview", ttl=ttl)
    pdata = ((prev or {}).get("result") or {}).get("previewData") or {}
    for side_key, target, is_home in (("homeTeamLineUp", home_lu, True), ("awayTeamLineUp", away_lu, False)):
        for p in ((pdata.get(side_key) or {}).get("fullLineUp") or []):
            nm = p.get("playerName") or ""
            if not nm:
                continue
            order = p.get("batorder")
            if order in (None, "", 0):
                sp = {"name": nm, "id": p.get("playerCode"), "confirmed": True, "pos": p.get("positionName") or "선발투수"}
                if is_home:
                    home_sp = sp
                else:
                    away_sp = sp
                continue
            target.append({
                "order": int(order),
                "pos": p.get("positionName") or "",
                "name": nm,
                "id": p.get("playerCode"),
                "hand": p.get("batsThrows") or p.get("hitType") or "",
                "avg": p.get("seasonHra") or p.get("hra") or "",
            })

    # 2) 경기 시작 후 실제 출전 타순 (KBO/NPB record)
    if len(home_lu) < 9 or len(away_lu) < 9:
        rec = _get_json(f"{_NAVER_BASE}/{gid}/record", ttl=ttl)
        rdata = ((rec or {}).get("result") or {}).get("recordData") or {}
        for key, target in (("homeBatter", home_lu), ("awayBatter", away_lu)):
            batters = rdata.get(key) or []
            if len(batters) < 9 or len(target) >= 9:
                continue
            target.clear()
            seen = set()
            for b in batters:
                o = b.get("batOrder")
                if not o or o in seen:
                    continue
                seen.add(o)
                target.append({
                    "order": int(o),
                    "pos": b.get("posName") or b.get("pos") or "",
                    "name": b.get("name") or "",
                    "id": b.get("playerId"),
                    "hand": "",
                    "avg": b.get("avg") or "",
                })
        for key, is_home in (("homePitcher", True), ("awayPitcher", False)):
            ps = rdata.get(key) or []
            if ps and ps[0].get("name"):
                sp = {"name": ps[0]["name"], "id": ps[0].get("playerId"), "era": ps[0].get("era", ""), "confirmed": True}
                if is_home and not home_sp:
                    home_sp = sp
                if not is_home and not away_sp:
                    away_sp = sp

    home_lu.sort(key=lambda x: x["order"])
    away_lu.sort(key=lambda x: x["order"])
    home_lu = home_lu[:9]
    away_lu = away_lu[:9]
    confirmed = len(home_lu) >= 9 and len(away_lu) >= 9
    return {
        "game_id": gid,
        "confirmed": confirmed,
        "home_lineup": home_lu,
        "away_lineup": away_lu,
        "home_starter": home_sp or None,
        "away_starter": away_sp or None,
        "source": "sports.naver.com",
    }
