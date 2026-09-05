# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import os

BETMAN_INQ_URL = 'https://www.betman.co.kr/buyPsblGame/gameInfoInq.do'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.betman.co.kr/main/mainPage/gamebuy/gameSlip.do?gmId=G024'
}

# In-memory cache: (gm_id, gm_ts) -> (timestamp, data)
_CACHE = {}
CACHE_TTL = 300 # 5 minutes

class BetmanService:
    @staticmethod
    def get_round_data(gm_id: str = 'G024', gm_ts: int = 260066) -> dict:
        now = time.time()
        cache_key = f'{gm_id}_{gm_ts}'
        if cache_key in _CACHE:
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
            # Fallback to local cached json if exists
            fallback = BetmanService._get_fallback_data(gm_id, gm_ts)
            if fallback:
                return fallback
            raise e

    @staticmethod
    def _parse_response(gm_id: str, gm_ts: int, data: dict) -> dict:
        cur = data.get('currentLottery', {})
        schedules = data.get('schedulesList', [])
        vote_list = data.get('voteStatus', {}).get('homeVoteStatusList', [])

        actual_gm_ts = data.get('gmTs') or cur.get('gmTs') or gm_ts
        round_no = str(actual_gm_ts)[-2:]

        sport_label = '야구 승1패' if gm_id == 'G024' else ('축구 승무패' if gm_id == 'G011' else '농구 승5패')

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

            # AI Pick logic
            ai_pick = '승'
            ai_conf = votes['win']
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
                'home': s.get('homeName', ''),
                'away': s.get('awayName', ''),
                'result': result_label,
                'result_code': res_code,
                'votes': votes,
                'ai_pick': ai_pick,
                'ai_conf': ai_conf
            })

        return {
            'status': 'success',
            'gmId': gm_id,
            'gmTs': actual_gm_ts,
            'round_name': f'{sport_label} {round_no}회차',
            'title': cur.get('gameName', sport_label),
            'sale_status': cur.get('saleStatus'),
            'status_message': cur.get('statusMessage', '발매 중'),
            'forward_amount': cur.get('forwardAmount', 0),
            'forward_cnt': cur.get('forwardCnt', 0),
            'total_sell_amount': cur.get('totalSellAmount', 0),
            'total_sale_cnt': cur.get('totalSaleCnt', 0),
            'matches': matches
        }

    @staticmethod
    def _get_fallback_data(gm_id: str, gm_ts: int) -> dict:
        return None
