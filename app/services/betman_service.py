# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import os
import sqlite3

BETMAN_INQ_URL = 'https://www.betman.co.kr/buyPsblGame/gameInfoInq.do'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.betman.co.kr/main/mainPage/gamebuy/gameSlip.do?gmId=G024'
}

_CACHE = {}
CACHE_TTL = 600 # 10 minutes official Betman sync interval

def clean_name(n):
    if not n: return ''
    return n.replace(' ', '').replace('·', '').replace('.', '').replace('-', '').lower()

def compute_name_similarity(betman_team, db_team):
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
    def _find_matching_db_match(home_name: str, away_name: str, sport_code: str = 'BASEBALL') -> dict:
        try:
            db_path = 'sports_data.db'
            if not os.path.exists(db_path):
                return None
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, match_date, sport_code, league_name, home_team_name, away_team_name, home_score, away_score, status FROM matches WHERE sport_code = ?', (sport_code,))
            rows = cursor.fetchall()
            conn.close()

            best_match = None
            best_score = 0
            for r in rows:
                s_h = compute_name_similarity(home_name, r['home_team_name'])
                s_a = compute_name_similarity(away_name, r['away_team_name'])
                tot = s_h + s_a
                if tot > best_score and s_h >= 50 and s_a >= 50:
                    best_score = tot
                    best_match = r
            
            if best_match:
                from app.services.team_split_service import TeamSplitService
                pred = TeamSplitService.get_quick_prediction(
                    home_team=best_match['home_team_name'],
                    away_team=best_match['away_team_name'],
                    sport_code=best_match['sport_code'],
                    status=best_match['status'],
                    home_score=best_match['home_score'],
                    away_score=best_match['away_score']
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
    def get_round_data(gm_id: str = 'G024', gm_ts: int = 260066, force_refresh: bool = False) -> dict:
        now = time.time()
        cache_key = f'{gm_id}_{gm_ts}'
        if not force_refresh and cache_key in _CACHE:
            ts_cached, data = _CACHE[cache_key]
            if now - ts_cached < CACHE_TTL:
                return data

        try:
            params = {'gmId': gm_id, '_sbmInfo': {'debugMode': 'false'}}
            if gm_ts:
                params['gmTs'] = int(gm_ts)

            req = urllib.request.Request(
                BETMAN_INQ_URL,
                data=json.dumps(params).encode('utf-8'),
                headers=HEADERS
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                res = json.loads(raw)

            parsed = BetmanService._parse_response(gm_id, gm_ts, res)
            _CACHE[cache_key] = (now, parsed)
            return parsed
        except Exception as e:
            print(f'[WARN] BetmanService fetch error for {gm_id}/{gm_ts}: {e}')
            raise e

    @staticmethod
    def _parse_response(gm_id: str, gm_ts: int, data: dict) -> dict:
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

            # Match with our database to get internal match ID and AI probabilities!
            db_match = BetmanService._find_matching_db_match(home_n, away_n, sport_code)

            db_match_id = db_match['id'] if db_match else None
            db_pred = db_match.get('prediction', {}) if db_match else {}

            # AI pick preference: DB model prediction if available, else votes
            ai_pick = '승'
            ai_conf = votes['win']
            if db_pred and db_pred.get('favored_team'):
                fav = db_pred.get('favored_team')
                if fav == db_match['home_team_name']:
                    ai_pick = '승'
                elif fav == db_match['away_team_name']:
                    ai_pick = '패'
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
                'league': s.get('leagueName', 'KBO' if s.get('domastic') else 'MLB'),
                'date': s.get('gameDateStr', ''),
                'home': home_n,
                'away': away_n,
                'result': result_label,
                'result_code': res_code,
                'votes': votes,
                'ai_pick': ai_pick,
                'ai_conf': ai_conf,
                'db_match_id': db_match_id,
                'db_home_team': db_match['home_team_name'] if db_match else home_n,
                'db_away_team': db_match['away_team_name'] if db_match else away_n,
                'db_prob_home': db_pred.get('home_pct', 50),
                'db_prob_away': db_pred.get('away_pct', 50)
            })

        forward_amt = int(cur.get('forwardAmount') or 0)
        sell_amt = int(cur.get('totalSellAmount') or 0)
        sale_cnt = int(cur.get('totalSaleCnt') or (sell_amt // 1000) or 0)

        # Official Sports Toto Prize Allocation:
        # Total payout pool = 50% of total sales
        # 1st prize pool = accumulated rollover + 50% of payout pool (25% of sales)
        # 2nd prize pool = 20% of payout pool (10% of sales)
        # 3rd prize pool = 10% of payout pool (5% of sales)
        # 4th prize pool = 20% of payout pool (10% of sales)
        first_prize_pool = forward_amt + int(sell_amt * 0.25)
        second_prize_pool = int(sell_amt * 0.10)
        third_prize_pool = int(sell_amt * 0.05)
        fourth_prize_pool = int(sell_amt * 0.10)

        from datetime import datetime
        now_str = datetime.now().strftime("%H:%M:%S")

        return {
            'status': 'success',
            'gmId': gm_id,
            'gmTs': actual_gm_ts,
            'round_name': f'{sport_label} {round_no}회차',
            'title': cur.get('gameName', sport_label),
            'sale_status': cur.get('saleStatus'),
            'status_message': cur.get('statusMessage', '발매 중'),
            'forward_amount': forward_amt,
            'forward_cnt': cur.get('forwardCnt', 0),
            'total_sell_amount': sell_amt,
            'total_sale_cnt': sale_cnt,
            'first_prize_pool': first_prize_pool,
            'second_prize_pool': second_prize_pool,
            'third_prize_pool': third_prize_pool,
            'fourth_prize_pool': fourth_prize_pool,
            'updated_at': now_str,
            'matches': matches
        }

