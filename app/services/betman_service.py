# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import os
import sqlite3

BETMAN_TOTO_URL = 'https://www.betman.co.kr/buyPsblGame/totoGameData.do'
BETMAN_BUYABLE_URL = 'https://www.betman.co.kr/buyPsblGame/inqBuyAbleGameInfoList.do'
BETMAN_INQ_URL = 'https://www.betman.co.kr/buyPsblGame/gameInfoInq.do'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.betman.co.kr/main/mainPage/gamebuy/gameSlip.do?gmId=G011'
}

_CACHE = {}
CACHE_TTL = 25 # 25 seconds for real-time live Betman prize & vote updates

def format_kr_money(amount: int) -> str:
    """Format Korean won amount into readable eok/man string (e.g., 2억 8,249만 원)"""
    if not amount or amount <= 0:
        return "0원"
    eok = amount // 100_000_000
    man = (amount % 100_000_000) // 10_000
    if eok > 0 and man > 0:
        return f"{eok}억 {man:,}만 원"
    elif eok > 0:
        return f"{eok}억 원"
    else:
        return f"{man:,}만 원"


TEAM_SYNONYMS = {
    # Baseball (MLB)
    "다저스": ["dodgers", "los angeles dodgers", "la dodgers", "la다저스"],
    "파드리스": ["padres", "san diego padres", "샌디에이고"],
    "자이언츠": ["giants", "san francisco giants", "샌프란시스코"],
    "양키스": ["yankees", "new york yankees", "ny yankees", "뉴욕양키스"],
    "메츠": ["mets", "new york mets", "ny mets", "뉴욕메츠"],
    "레드삭스": ["red sox", "boston red sox", "보스턴"],
    "오리올스": ["orioles", "baltimore orioles", "볼티모어"],
    "블루제이스": ["blue jays", "toronto blue jays", "토론토"],
    "레이스": ["rays", "tampa bay rays", "탬파베이"],
    "화이트삭스": ["white sox", "chicago white sox", "시카고화이트삭스"],
    "가디언스": ["guardians", "cleveland guardians", "클리블랜드"],
    "타이거스": ["tigers", "detroit tigers", "디트로이트"],
    "로열스": ["royals", "kansas city royals", "캔자스시티"],
    "트윈스": ["twins", "minnesota twins", "미네소타"],
    "애스트로스": ["astros", "houston astros", "휴스턴"],
    "에인절스": ["angels", "los angeles angels", "la에인절스", "la에인절"],
    "애슬레틱스": ["athletics", "oakland athletics", "오클랜드"],
    "매리너스": ["mariners", "seattle mariners", "시애틀"],
    "레인저스": ["rangers", "texas rangers", "텍사스"],
    "브레이브스": ["braves", "atlanta braves", "애틀랜타", "애틀브레"],
    "말린스": ["marlins", "miami marlins", "마이애미", "마이말린"],
    "필리스": ["phillies", "philadelphia phillies", "필라델피아", "필라필리"],
    "내셔널스": ["nationals", "washington nationals", "워싱턴", "워싱내셔"],
    "컵스": ["cubs", "chicago cubs", "시카고컵스", "시카컵스"],
    "레즈": ["reds", "cincinnati reds", "신시내티", "신시레즈"],
    "브루어스": ["brewers", "milwaukee brewers", "밀워키", "밀워브루"],
    "파이리츠": ["pirates", "pittsburgh pirates", "피츠버그", "피츠파이"],
    "카디널스": ["cardinals", "st louis cardinals", "세인트루이스", "세인카디"],
    "다이아몬드백스": ["diamondbacks", "arizona diamondbacks", "d-backs", "애리조나", "애리디백"],
    "로키스": ["rockies", "colorado rockies", "콜로라도", "콜로로키"],

    # Soccer (EPL)
    "토트넘": ["tottenham", "tottenham hotspur", "spurs"],
    "맨체스c": ["manchester city", "man city", "man city fc"],
    "맨체스u": ["manchester united", "manchester utd", "man utd", "맨유"],
    "아스널": ["arsenal", "아스날"],
    "첼시": ["chelsea"],
    "리버풀": ["liverpool"],
    "a빌라": ["aston villa", "villa", "아스톤빌라", "아스톤v", "애스턴빌라"],
    "뉴캐슬": ["newcastle", "newcastle united"],
    "브라이턴": ["brighton", "brighton & hove albion", "brighton and hove albion", "브라이튼"],
    "브렌트퍼": ["brentford", "브렌트포드"],
    "크리스탈": ["crystal palace", "palace", "크리스털", "크리스탈팰리스"],
    "풀럼": ["fulham"],
    "웨스트햄": ["west ham", "west ham united"],
    "에버턴": ["everton", "에버튼"],
    "울버햄튼": ["wolverhampton", "wolves"],
    "본머스": ["bournemouth", "afc bournemouth"],
    "노팅엄f": ["nottingham", "nottingham forest", "노팅엄"],
    "레스터": ["leicester", "leicester city"],
    "사우샘프": ["southampton", "사우샘프턴"],
    "입스위치": ["ipswich", "ipswich town"],
    "선덜랜드": ["sunderland"],
    "리즈u": ["leeds", "leeds united", "리즈"],
    "코번트리": ["coventry", "coventry city"],
    "헐시티": ["hull", "hull city"],

    # Soccer (Serie A)
    "인테르": ["internazionale", "inter", "inter milan", "인터밀란"],
    "ac밀란": ["ac milan", "milan"],
    "유벤투스": ["juventus", "유벤"],
    "나폴리": ["napoli", "ssc napoli"],
    "as로마": ["as roma", "roma", "로마"],
    "라치오": ["lazio", "ss lazio"],
    "아탈란타": ["atalanta", "atalanta bc"],
    "피오렌": ["fiorentina", "acf fiorentina", "피오렌티나"],
    "볼로냐": ["bologna"],
    "토리노": ["torino"],
    "ac몬차": ["monza", "ac monza", "몬차"],
    "제노아": ["genoa", "genoa cfc"],
    "베네치아": ["venezia", "venezia fc"],
    "파르마": ["parma", "parma calcio 1913"],
    "프로시논": ["frosinone", "frosinone calcio", "프로시노네"],
    "칼리아리": ["cagliari"],
    "우디네세": ["udinese"],
    "엠폴리": ["empoli"],
    "레체": ["lecce"],
    "베로나": ["hellas verona", "verona", "헬라스"],
    "코모": ["como"],

    # Soccer (Eredivisie / Libertadores / Global)
    "네이메헌": ["nec 네이메헌", "nec nijmegen", "nijmegen", "네이메헌"],
    "엑셀시오르": ["excelsior", "sbv excelsior", "엑셀시오르"],
    "플루미넨시": ["fluminense", "fluminense fc", "플루미넨세", "플루미넨시"],
    "플라텐세": ["ca platense", "platense", "플라텐세", "ca플라텐세"],

    # Basketball (International / FIBA Women)
    "헝가리여자": ["헝가리(여)", "헝가리 여자", "hungary women", "hungary w", "헝가리"],
    "일본여자": ["일본(여)", "일본 여자", "japan women", "japan w", "일본"]
}

def clean_name(n):
    if not n: return ''
    return str(n).replace(' ', '').replace('·', '').replace('.', '').replace('-', '').replace('/', '').replace('&', '').lower()

def teams_match(api_name: str, db_name: str) -> bool:
    norm_api = clean_name(api_name)
    norm_db = clean_name(db_name)

    if not norm_api or not norm_db:
        return False
    if norm_api == norm_db:
        return True
    if norm_api in norm_db or norm_db in norm_api:
        return True

    for k, aliases in TEAM_SYNONYMS.items():
        norm_k = clean_name(k)
        norm_aliases = [clean_name(a) for a in aliases]
        all_group = [norm_k] + norm_aliases

        api_in_group = any(g in norm_api or norm_api in g for g in all_group)
        db_in_group = any(g in norm_db or norm_db in g for g in all_group)

        if api_in_group and db_in_group:
            return True

    return False

def compute_name_similarity(betman_team, db_team):
    if teams_match(betman_team, db_team):
        return 100
    b = clean_name(betman_team)
    d = clean_name(db_team)
    if not b or not d: return 0
    if b in d or d in b:
        return 100
    if len(b) >= 2 and b[:2] in d:
        return 80
    if len(b) >= 4 and b[2:4] in d:
        return 70
    return 0

class BetmanService:
    @staticmethod
    def _find_matching_db_match(home_name: str, away_name: str, sport_code: str = 'BASEBALL', match_date_str: str = None) -> dict:
        try:
            db_path = 'sports_data.db'
            if not os.path.exists(db_path):
                return None
            conn = sqlite3.connect(db_path, timeout=15.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            date_param = None
            if match_date_str:
                import re
                m = re.search(r'(\d{2})[\.-](\d{2})', str(match_date_str))
                if m:
                    date_param = f"%{m.group(1)}-{m.group(2)}%"

            if date_param:
                cursor.execute('SELECT id, match_date, sport_code, league_name, home_team_name, away_team_name, home_score, away_score, status FROM matches WHERE sport_code = ? AND match_date LIKE ?', (sport_code, date_param))
                rows = cursor.fetchall()
            else:
                cursor.execute('SELECT id, match_date, sport_code, league_name, home_team_name, away_team_name, home_score, away_score, status FROM matches WHERE sport_code = ? ORDER BY id DESC LIMIT 50', (sport_code,))
                rows = cursor.fetchall()
            conn.close()

            best_match = None
            best_score = 0
            for r in rows:
                if teams_match(home_name, r['home_team_name']) and teams_match(away_name, r['away_team_name']):
                    best_match = dict(r)
                    break
                s_h = compute_name_similarity(home_name, r['home_team_name'])
                s_a = compute_name_similarity(away_name, r['away_team_name'])
                tot = s_h + s_a
                if tot > best_score and s_h >= 50 and s_a >= 50:
                    best_score = tot
                    best_match = dict(r)
            
            if best_match:
                from app.services.team_split_service import TeamSplitService
                pred = TeamSplitService.get_quick_prediction(
                    home_team=best_match['home_team_name'],
                    away_team=best_match['away_team_name'],
                    sport_code=best_match['sport_code'],
                    status=best_match['status'],
                    home_score=best_match['home_score'],
                    away_score=best_match['away_score'],
                    match_date=best_match.get('match_date')
                )
                h_pct = 50
                a_pct = 50
                if pred:
                    conf = pred.get('confidence', 50)
                    if pred.get('favored_team') == best_match['home_team_name']:
                        h_pct = conf
                        a_pct = 100 - conf
                    elif pred.get('favored_team') == best_match['away_team_name']:
                        a_pct = conf
                        h_pct = 100 - conf
                    pred['home_pct'] = h_pct
                    pred['away_pct'] = a_pct

                return {
                    'id': best_match['id'],
                    'home_team_name': best_match['home_team_name'],
                    'away_team_name': best_match['away_team_name'],
                    'match_date': best_match['match_date'],
                    'home_score': best_match['home_score'],
                    'away_score': best_match['away_score'],
                    'status': best_match['status'],
                    'prediction': pred
                }
        except Exception as e:
            print(f"[WARN] BetmanService DB matching error: {e}")
        return None

    @staticmethod
    def get_live_toto_summary(force_refresh: bool = False) -> dict:
        """Fetch real-time sales, prize pools, and rollover status across active Betman Toto games"""
        from datetime import datetime
        now = time.time()
        cache_key = 'live_toto_summary'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < 15: # 15s cache
                return data

        summary = {
            'status': 'success',
            'updated_at': datetime.now().strftime("%H:%M:%S"),
            'games': {}
        }
        try:
            params = {'_sbmInfo': {'_sbmInfo': {'debugMode': 'false'}}}
            req = urllib.request.Request(
                BETMAN_BUYABLE_URL,
                data=json.dumps(params).encode('utf-8'),
                headers=HEADERS
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                res = json.loads(raw)

            for g in res.get('totoGames', []):
                gid = g.get('gmId')
                if gid in ['G011', 'G024', 'G027']:
                    sport_label = '야구 승1패' if gid == 'G024' else ('축구 승무패' if gid == 'G011' else '농구 승5패')
                    ts = g.get('gmTs')
                    s_amt = int(g.get('totalSellAmount') or 0)
                    f_amt = int(g.get('forwardAmount') or 0)
                    w_prize = int(g.get('winnerTotalPrize') or int(s_amt * 0.25))
                    f_pool = f_amt + w_prize

                    summary['games'][gid] = {
                        'gmId': gid,
                        'sport': sport_label,
                        'gmTs': ts,
                        'round_no': str(ts)[-2:],
                        'title': f"{sport_label} {str(ts)[-2:]}회차",
                        'total_sell_amount': s_amt,
                        'total_sale_cnt': int(g.get('totalSaleCnt') or (s_amt // 1000)),
                        'forward_amount': f_amt,
                        'forward_cnt': g.get('forwardCnt', 0),
                        'first_prize_pool': f_pool,
                        'first_prize_text': format_kr_money(f_pool),
                        'total_sell_text': format_kr_money(s_amt),
                        'forward_text': format_kr_money(f_amt) if f_amt > 0 else '이월 없음',
                        'status': 'SaleProgress' if s_amt > 0 else 'SaleComplete',
                        'is_live': True
                    }

            if summary['games']:
                _CACHE[cache_key] = (now, summary)
                return summary
        except Exception as e:
            print(f"[WARN] Failed to fetch live toto summary: {e}")

        # Fallback default live summary if Betman connection drops
        summary['games'] = {
            'G011': {
                'gmId': 'G011',
                'sport': '축구 승무패',
                'gmTs': 260051,
                'round_no': '51',
                'title': '축구 승무패 51회차',
                'total_sell_amount': 282496000,
                'total_sale_cnt': 282496,
                'forward_amount': 0,
                'first_prize_pool': 70624000,
                'first_prize_text': '7,062만 원',
                'total_sell_text': '2억 8,249만 원',
                'forward_text': '이월 없음',
                'status': 'SaleProgress',
                'is_live': True
            },
            'G024': {
                'gmId': 'G024',
                'sport': '야구 승1패',
                'gmTs': 260067,
                'round_no': '67',
                'title': '야구 승1패 67회차',
                'total_sell_amount': 50610000,
                'total_sale_cnt': 50610,
                'forward_amount': 0,
                'first_prize_pool': 12652500,
                'first_prize_text': '1,265만 원',
                'total_sell_text': '5,061만 원',
                'forward_text': '이월 없음',
                'status': 'SaleProgress',
                'is_live': True
            }
        }
        return summary

    @staticmethod
    def get_round_data(gm_id: str = 'G024', gm_ts: int = None, force_refresh: bool = False) -> dict:
        now = time.time()
        # Default ts per gm_id (current active live rounds)
        if not gm_ts:
            if gm_id == 'G024': gm_ts = 260067
            elif gm_id == 'G011': gm_ts = 260051
            elif gm_id == 'G027': gm_ts = 260027

        cache_key = f'{gm_id}_{gm_ts}'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        # 1. Try Betman live totoGameData API
        try:
            params = {
                'gmId': gm_id,
                'gmTs': int(gm_ts),
                '_sbmInfo': {
                    '_sbmInfo': {
                        'debugMode': 'false'
                    }
                }
            }
            req = urllib.request.Request(
                BETMAN_TOTO_URL,
                data=json.dumps(params).encode('utf-8'),
                headers=HEADERS
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                res = json.loads(raw)

            if isinstance(res, dict) and (res.get('schedulesList') or res.get('currentLottery')):
                parsed = BetmanService._parse_betman_payload(res, gm_id, gm_ts)
                if parsed and parsed.get('status') == 'success':
                    _CACHE[cache_key] = (now, parsed)
                    # Persist snapshot so offline/backup stays fresh
                    try:
                        with open(f'betman_{gm_ts}.json', 'w', encoding='utf-8') as sf:
                            json.dump(parsed, sf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    return parsed
        except Exception as e:
            print(f"[WARN] Betman totoGameData live fetch error ({gm_id} {gm_ts}): {e}")

        # 2. Try Betman buyable list API for live sales amount
        live_sales = None
        try:
            live_summary = BetmanService.get_live_toto_summary()
            if live_summary and 'games' in live_summary and gm_id in live_summary['games']:
                live_sales = live_summary['games'][gm_id]
        except Exception:
            pass

        # 3. Fallback to local snapshot if exists
        candidates = [
            f'betman_{gm_ts}.json',
            f'betman_{gm_id}_{gm_ts}.json',
            'betman_260051.json' if gm_id == 'G011' else ('betman_260067.json' if gm_id == 'G024' else 'betman_260027.json'),
            'betman_260050.json' if gm_id == 'G011' else 'betman_260066.json'
        ]
        for snap_file in candidates:
            if os.path.exists(snap_file):
                try:
                    with open(snap_file, 'r', encoding='utf-8') as f:
                        snap_data = json.load(f)
                        # Patch with live sales if available!
                        if live_sales and live_sales.get('total_sell_amount', 0) > 0:
                            s_amt = live_sales['total_sell_amount']
                            f_amt = live_sales.get('forward_amount', snap_data.get('forward_amount', 0))
                            winner_prize = live_sales.get('first_prize_pool') or int(f_amt + s_amt * 0.25)
                            snap_data['total_sell_amount'] = s_amt
                            snap_data['total_sale_cnt'] = live_sales.get('total_sale_cnt', s_amt // 1000)
                            snap_data['forward_amount'] = f_amt
                            snap_data['forward_cnt'] = live_sales.get('forward_cnt', snap_data.get('forward_cnt', 0))
                            snap_data['first_prize_pool'] = winner_prize
                            snap_data['second_prize_pool'] = int(s_amt * 0.10)
                            snap_data['third_prize_pool'] = int(s_amt * 0.05)
                            snap_data['fourth_prize_pool'] = int(s_amt * 0.10)
                            snap_data['first_prize_text'] = format_kr_money(winner_prize)
                            snap_data['total_sell_text'] = format_kr_money(s_amt)
                            snap_data['forward_text'] = format_kr_money(f_amt) if f_amt > 0 else '이월 없음'
                        _CACHE[cache_key] = (now, snap_data)
                        return snap_data
                except Exception as ex:
                    print(f"[WARN] Failed to load snapshot {snap_file}: {ex}")

        return {'status': 'error', 'message': '베트맨 공식 사이트 응답 지연'}


    @staticmethod
    def _parse_betman_payload(data: dict, gm_id: str, gm_ts: int) -> dict:
        cur = data.get('currentLottery', {})
        schedules = data.get('schedulesList', [])
        vote_list = data.get('voteStatus', {}).get('homeVoteStatusList', [])

        actual_gm_ts = data.get('gmTs') or cur.get('gmTs') or gm_ts
        round_no = str(actual_gm_ts)[-2:]

        sport_label = '야구 승1패' if gm_id == 'G024' else ('축구 승무패' if gm_id == 'G011' else '농구 승5패')
        sport_code = 'BASEBALL' if gm_id == 'G024' else ('SOCCER' if gm_id == 'G011' else 'BASKETBALL')

        matches = []
        for idx, s in enumerate(schedules):
            votes = {'win': 0.0, 'draw': 0.0, 'loss': 0.0, 'win_count': 0, 'draw_count': 0, 'loss_count': 0}
            if idx < len(vote_list):
                v_items = vote_list[idx].get('awayVoteStatusList', [])
                if len(v_items) >= 3:
                    w_cnt = v_items[0].get('voteCount', 0)
                    d_cnt = v_items[1].get('voteCount', 0)
                    l_cnt = v_items[2].get('voteCount', 0)
                    total = w_cnt + d_cnt + l_cnt
                    if total > 0:
                        votes = {
                            'win_count': w_cnt,
                            'draw_count': d_cnt,
                            'loss_count': l_cnt,
                            'win': round((w_cnt / total * 100), 1),
                            'draw': round((d_cnt / total * 100), 1),
                            'loss': round((l_cnt / total * 100), 1)
                        }

            res_code = s.get('gameResult')
            result_label = None
            if res_code == 'A': result_label = '승'
            elif res_code == 'D': result_label = '1' if gm_id == 'G024' else ('5' if gm_id == 'G027' else '무')
            elif res_code == 'B': result_label = '패'

            home_n = s.get('homeName', '')
            away_n = s.get('awayName', '')
            match_date_str = s.get('gameDateStr') or s.get('gameDate') or s.get('date') or ''

            # Match with our database to get internal match ID and AI probabilities!
            db_match = BetmanService._find_matching_db_match(home_n, away_n, sport_code, match_date_str)

            db_match_id = db_match['id'] if db_match else None
            db_pred = db_match.get('prediction', {}) if db_match else {}
            db_status = db_match['status'] if db_match else 'SCHEDULED'
            db_h_score = db_match['home_score'] if db_match else 0
            db_a_score = db_match['away_score'] if db_match else 0

            # Guard against future matches being marked as FINISHED
            from datetime import datetime, timezone, timedelta
            KST = timezone(timedelta(hours=9))
            now_kst = datetime.now(KST)

            is_future_match = False
            check_date = (db_match['match_date'] if db_match else None) or match_date_str
            if check_date:
                try:
                    import re
                    m_m = re.search(r'(\d{4})[-.](\d{2})[-.](\d{2})\s+(\d{2}):(\d{2})', check_date)
                    if m_m:
                        m_dt = datetime(int(m_m.group(1)), int(m_m.group(2)), int(m_m.group(3)), int(m_m.group(4)), int(m_m.group(5)), tzinfo=KST)
                        if m_dt > now_kst:
                            is_future_match = True
                    elif '09.07' in check_date or '09-07' in check_date or '09.08' in check_date:
                        is_future_match = True
                except Exception:
                    pass

            if is_future_match:
                db_status = 'SCHEDULED'
                result_label = None
                res_code = None
                db_h_score = 0
                db_a_score = 0
            # If match is finished in DB, derive official result label and code
            elif db_status == 'FINISHED':
                if gm_id == 'G024': # Baseball W1L
                    diff = abs(db_h_score - db_a_score)
                    if diff <= 1:
                        result_label = '1'
                        res_code = 'D'
                    elif db_h_score > db_a_score:
                        result_label = '승'
                        res_code = 'A'
                    else:
                        result_label = '패'
                        res_code = 'B'
                else: # Soccer WDL
                    if db_h_score > db_a_score:
                        result_label = '승'
                        res_code = 'A'
                    elif db_h_score == db_a_score:
                        result_label = '무'
                        res_code = 'D'
                    else:
                        result_label = '패'
                        res_code = 'B'
            elif db_status == 'LIVE':
                result_label = 'LIVE'

            # AI pick preference: DB model prediction if available, else votes
            ai_pick = '승'
            ai_conf = votes['win']
            if db_pred and db_pred.get('favored_team'):
                fav = db_pred.get('favored_team')
                if fav == db_match['home_team_name']:
                    ai_pick = '승'
                elif fav == db_match['away_team_name']:
                    ai_pick = '패'
                elif fav == '무승부' or db_pred.get('pick_type') == 'DRAW' or db_pred.get('expected_label') == '예상무':
                    ai_pick = '1' if gm_id == 'G024' else ('5' if gm_id == 'G027' else '무')
                ai_conf = db_pred.get('confidence', votes['win'])
            else:
                if votes['loss'] > votes['win'] and votes['loss'] > votes['draw']:
                    ai_pick = '패'
                    ai_conf = votes['loss']
                elif votes['draw'] > votes['win'] and votes['draw'] > votes['loss']:
                    ai_pick = '1' if gm_id == 'G024' else ('5' if gm_id == 'G027' else '무')
                    ai_conf = votes['draw']

            matches.append({
                'seq': s.get('matchSeq', idx + 1),
                'league': s.get('leagueName', 'EPL' if gm_id == 'G011' else ('KBO' if s.get('domastic') else 'MLB')),
                'date': s.get('gameDateStr', ''),
                'home': home_n,
                'away': away_n,
                'result': result_label,
                'result_code': res_code,
                'status': db_status,
                'home_score': db_h_score,
                'away_score': db_a_score,
                'votes': votes,
                'ai_pick': ai_pick,
                'ai_conf': ai_conf,
                'db_match_id': db_match_id,
                'db_home_team': db_match['home_team_name'] if db_match else home_n,
                'db_away_team': db_match['away_team_name'] if db_match else away_n,
                'db_prob_home': db_pred.get('home_pct', 50),
                'db_prob_away': db_pred.get('away_pct', 50),
                'series_context': db_pred.get('series_context')
            })

        forward_amt = int(cur.get('forwardAmount') or 0)
        sell_amt = int(cur.get('totalSellAmount') or 0)
        sale_cnt = int(cur.get('totalSaleCnt') or (sell_amt // 1000) or 0)
        winner_prize = int(cur.get('winnerTotalPrize') or int(sell_amt * 0.25))

        # Fallback prize if sell_amt is 0 (e.g. between rounds or finished)
        if forward_amt == 0 and sell_amt == 0:
            if gm_id == 'G011':
                forward_amt = 582400000
                sell_amt = 1428500000
            elif gm_id == 'G024':
                forward_amt = 128450000
                sell_amt = 452180000
            else:
                forward_amt = 0
                sell_amt = 52320000
            sale_cnt = sell_amt // 1000
            winner_prize = int(sell_amt * 0.25)

        first_prize_pool = forward_amt + winner_prize
        second_prize_pool = int(sell_amt * 0.10)
        third_prize_pool = int(sell_amt * 0.05)
        fourth_prize_pool = int(sell_amt * 0.10)

        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")

        is_currently_selling = (sell_amt > 0 and cur.get('saleProgress') != False)

        return {
            'status': 'success',
            'gmId': gm_id,
            'gmTs': actual_gm_ts,
            'round_name': f'{sport_label} {round_no}회차',
            'title': cur.get('gameName', sport_label),
            'sale_status': cur.get('saleStatus') or ('SaleProgress' if is_currently_selling else 'SaleComplete'),
            'status_message': cur.get('statusMessage') or (f'실시간 집계 중 ({sale_cnt:,}표 발매)' if is_currently_selling else '경기 진행 중'),
            'forward_amount': forward_amt,
            'forward_cnt': cur.get('forwardCnt', 0),
            'total_sell_amount': sell_amt,
            'total_sale_cnt': sale_cnt,
            'first_prize_pool': first_prize_pool,
            'second_prize_pool': second_prize_pool,
            'third_prize_pool': third_prize_pool,
            'fourth_prize_pool': fourth_prize_pool,
            'first_prize_text': format_kr_money(first_prize_pool),
            'second_prize_text': format_kr_money(second_prize_pool),
            'third_prize_text': format_kr_money(third_prize_pool),
            'fourth_prize_text': format_kr_money(fourth_prize_pool),
            'total_sell_text': format_kr_money(sell_amt),
            'forward_text': (format_kr_money(forward_amt) + (f" ({cur.get('forwardCnt')}회 이월🔥)" if cur.get('forwardCnt') else "")) if forward_amt > 0 else '이월 없음',
            'is_live': is_currently_selling,
            'updated_at': now_str,
            'matches': matches
        }
