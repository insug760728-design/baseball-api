# -*- coding: utf-8 -*-
import os
import re
import urllib.request
import ssl
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.player_translation import sanitize_player_name, sanitize_text

def clean_int(val: Any) -> int:
    try:
        s = str(val).strip()
        if s.isdigit():
            return int(s)
        return int(float(s))
    except Exception:
        return 0

TEAM_NAME_MAP = {
    '巨人': '요미우리 자이언츠',
    '読売': '요미우리 자이언츠',
    '読売ジャイアンツ': '요미우리 자이언츠',
    '阪神': '한신 타이거스',
    '阪神タイガース': '한신 타이거스',
    '中日': '주니치 드래곤즈',
    '中日ドラゴンズ': '주니치 드래곤즈',
    'DeNA': '요코하마 DeNA 베이스타즈',
    'ＤｅＮＡ': '요코하마 DeNA 베이스타즈',
    '横浜': '요코하마 DeNA 베이스타즈',
    '横浜DeNA': '요코하마 DeNA 베이스타즈',
    '横浜DeNAベイスターズ': '요코하마 DeNA 베이스타즈',
    '広島': '히로시마 도요 카프',
    '広島東洋': '히로시마 도요 카프',
    '広島東洋カープ': '히로시마 도요 카프',
    'ヤクルト': '도쿄 야쿠르트 스왈로스',
    '東京ヤクルト': '도쿄 야쿠르트 스왈로스',
    '東京ヤクルトスワローズ': '도쿄 야쿠르트 스왈로스',
    'ソフトバンク': '후쿠오카 소프트뱅크 호크스',
    '福岡ソフトバンク': '후쿠오카 소프트뱅크 호크스',
    '福岡ソフトバンクホークス': '후쿠오카 소프트뱅크 호크스',
    '日本ハム': '홋카이도 닛폰햄 파이터즈',
    '北海道日本ハム': '홋카이도 닛폰햄 파이터즈',
    '北海道日本ハムファイターズ': '홋카이도 닛폰햄 파이터즈',
    'ロッテ': '지바 롯데 마린스',
    '千葉ロッテ': '지바 롯데 마린스',
    '千葉ロッテマリーンズ': '지바 롯데 마린스',
    '楽天': '도호쿠 라쿠텐 골든이글스',
    '東北楽天': '도호쿠 라쿠텐 골든이글스',
    '東北楽天ゴールデンイーグルス': '도호쿠 라쿠텐 골든이글스',
    'オリックス': '오릭스 버펄로스',
    'オリックス・バファローズ': '오릭스 버펄로스',
    'オリックスバファローズ': '오릭스 버펄로스',
    '西武': '사이타마 세이부 라이온즈',
    '埼玉西武': '사이타마 세이부 라이온즈',
    '埼玉西武ライオンズ': '사이타마 세이부 라이온즈'
}

def map_npb_team(name: str) -> str:
    s = name.strip()
    if s in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[s]
    for k, v in TEAM_NAME_MAP.items():
        if k in s:
            return v
    return s

def translate_npb_position(raw: str) -> str:
    char_map = {
        '投': '투수',
        '捕': '포수',
        '一': '1루수',
        '二': '2루수',
        '三': '3루수',
        '遊': '유격수',
        '左': '좌익수',
        '中': '중견수',
        '右': '우익수',
        '指': '지명타자',
        '打': '대타',
        '走': '대주자',
    }
    cleaned = raw.replace('(', '').replace(')', '').strip()
    res = [char_map[ch] for ch in cleaned if ch in char_map]
    if res:
        return "/".join(res)
    return raw or "타자"

NPB_PLAYER_KO_MAP = {
    '戸郷 翔征': '토고 쇼세이', '戸郷　翔征': '토고 쇼세이', '戸郷翔征': '토고 쇼세이',
    '柳 裕也': '야나기 유야', '柳　裕也': '야나기 유야', '柳裕也': '야나기 유야',
    '東 克樹': '아즈마 카츠키', '東　克樹': '아즈마 카츠키', '東克樹': '아즈마 카츠키',
    '奥川 恭伸': '오쿠가와 야스노부', '奥川　恭伸': '오쿠가와 야스노부', '奥川恭伸': '오쿠가와 야스노부',
    '才木 浩人': '사이키 히로토', '才木　浩人': '사이키 히로토', '才木浩人': '사이키 히로토',
    '床田 寛樹': '토코다 히로키', '床田　寛樹': '토코다 히로키', '床田寛樹': '토코다 히로키',
    '田中 晴也': '타나카 세이야', '田中　晴也': '타나카 세이야', '田中晴也': '타나카 세이야',
    '前田 健太': '마에다 켄타', '前田　健太': '마에다 켄타', '前田健太': '마에다 켄타',
    'Ｓ．ジェリー': 'S.젤리', 'S.ジェリー': 'S.젤리', 'ジェリー': 'S.젤리',
    '平良 海馬': '타이라 카이마', '平良　海馬': '타이라 카이마', '平良海馬': '타이라 카이마',
    'Ｌ．モイネロ': 'L.모이넬로', 'L.モイネロ': 'L.모이넬로', 'モイネロ': 'L.모이넬로',
    '山﨑 福也': '야마사키 사치야', '山﨑　福也': '야마사키 사치야', '山﨑福也': '야마사키 사치야', '山崎 福也': '야마사키 사치야',
    '有原 航平': '아리하라 코헤이', '宮城 大弥': '미야기 히로야', '村上 頌樹': '무라카미 쇼키',
    '今井 達也': '이마이 타츠야', '伊藤 大海': '이토 히로미', '小島 和哉': '코지마 카즈야',
    '早川 隆久': '하야카와 타카히사', '小川 泰弘': '오가와 야스히로', '高橋 宏斗': '타카하시 히로토',
    '九里 亜蓮': '쿠리 아렌', '大瀬良 大地': '오오세라 다이치', '菅野 智之': '스가노 토모유키',
    '髙橋 光成': '다카하시 코나', '高橋 光成': '다카하시 코나', '隅田 知一郎': '스미다 치히로',
    '松本 航': '마츠모토 와타루', '山下 舜平大': '야마시타 슌페이타', '田嶋 大樹': '타지마 다이키',
    '種市 篤暉': '타네이치 아츠키', '佐々木 朗希': '사사키 로키', '岸 孝之': '키시 타카유키',
    '則本 昂大': '노리모토 타카히로', '加藤 貴之': '카토 타카유키', '上原 健太': '우에하라 켄타',
    '東浜 巨': '히가시하마 나오', '大津 亮介': '오오츠 료스케', '和田 毅': '와다 츠요시',
    '森下 暢仁': '모리시타 마사토', '小園 健太': '코조노 켄타', '大貫 晋一': '오오누키 신이치',
    '高橋 奎二': '타카하시 케이지', '吉村 貢司郎': '요시무라 코지로', '小笠原 慎之介': '오가사와라 신노스케',
    '大野 雄大': '오오노 유다이', '西 勇輝': '니시 유키', '伊藤 将司': '이토 마사시',
    '佐藤 爽': '사토 소우', '佐藤爽': '사토 소우',
    '髙島 泰都': '타카시마 타이스케', '高島 泰都': '타카시마 타이스케', '高島泰都': '타카시마 타이스케',
    '高野 脩汰': '타카노 슈타', '高野脩汰': '타카노 슈타',
    '松本 晴': '마츠모토 하루', '松本晴': '마츠모토 하루',
    '井上 温大': '이노우에 하루토', '井上温大': '이노우에 하루토',
    '深沢 鳳介': '후카자와 호스케', '深沢鳳介': '후카자와 호스케',
    '栗林 良吏': '쿠리바야시 료지', '栗林良吏': '쿠리바야시 료지',
    '金丸 夢斗': '카네마루 유메토', '金丸夢斗': '카네마루 유메토'
}

def translate_npb_player_name(raw: str) -> str:
    if not raw:
        return ""
    clean = sanitize_player_name(raw)
    if clean in NPB_PLAYER_KO_MAP:
        return NPB_PLAYER_KO_MAP[clean]
    no_space = clean.replace(' ', '')
    if no_space in NPB_PLAYER_KO_MAP:
        return NPB_PLAYER_KO_MAP[no_space]
    # Fallback: clean symbols
    return clean

class NpbOfficialScraper:
    """
    일본 프로야구(NPB) 100% 공식 사이트 (npb.jp) 실시간 연동 크롤러
    - 1~9회 이닝별 라인스코어, 선수 박스스코어, 투수/타자 세부지표, 경기 타임라인 완전 수집
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,ko;q=0.8',
            'Referer': 'https://npb.jp/'
        }
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def scrape_probable_starters(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """NPB 공식 예고선발 페이지(https://npb.jp/announcement/starter/)에서 실시간 공식 발표 선발투수 수집"""
        url = "https://npb.jp/announcement/starter/"
        try:
            html = self._fetch_html(url)
        except Exception as e:
            print(f"[NPB Scraper] Failed to fetch starter page: {e}")
            return []

        soup = BeautifulSoup(html, 'html.parser')
        units = soup.find_all('div', class_=re.compile(r'unit\s+(cl|pl)'))
        starters_list = []

        for u in units:
            try:
                left_div = u.find('div', class_='team_left')
                right_div = u.find('div', class_='team_right')
                info_div = u.find('div', class_='info')

                if not left_div or not right_div:
                    continue

                raw_t_left = left_div.find('img').get('alt', '') if left_div.find('img') else ''
                raw_t_right = right_div.find('img').get('alt', '') if right_div.find('img') else ''
                p_left_raw = left_div.find('span').get_text(strip=True) if left_div.find('span') else ''
                p_right_raw = right_div.find('span').get_text(strip=True) if right_div.find('span') else ''
                stadium_info = info_div.get_text(strip=True) if info_div else ''

                t_left = map_npb_team(raw_t_left)
                t_right = map_npb_team(raw_t_right)
                p_left = translate_npb_player_name(p_left_raw)
                p_right = translate_npb_player_name(p_right_raw)

                # NPB 예고선발 페이지에서 unit 내 좌측(team_left)은 해당 경기 구장의 홈팀 또는 제1팀입니다.
                starters_list.append({
                    "league_id": "NPB",
                    "home_team_name": t_left,
                    "away_team_name": t_right,
                    "home_starter": p_left,
                    "away_starter": p_right,
                    "home_starter_confirmed": bool(p_left),
                    "away_starter_confirmed": bool(p_right),
                    "stadium_info": stadium_info,
                    "raw_home_starter": p_left_raw,
                    "raw_away_starter": p_right_raw
                })
            except Exception as e:
                print(f"[NPB Scraper] Error parsing unit: {e}")
                continue

        return starters_list

    def _fetch_html(self, url: str) -> str:
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, context=self.ctx, timeout=12) as resp:
            content = resp.read()
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('euc-jp', errors='ignore')

    def scrape_schedule(self, target_date: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """지정 기간 또는 특정 일자의 NPB 공식 경기 일정 및 결과 수집"""
        d_ref = target_date or start_date or datetime.now().strftime("%Y-%m-%d")
        parts = d_ref.split('-')
        year = parts[0] if len(parts) > 0 else "2026"
        month = parts[1] if len(parts) > 1 else "09"

        seasons_to_try = [year]
        if year != "2026":
            seasons_to_try.append("2026")
        if year != "2024":
            seasons_to_try.append("2024")

        all_games = []
        for s_year in seasons_to_try:
            url = f"https://npb.jp/games/{s_year}/schedule_{month}_detail.html"
            try:
                html = self._fetch_html(url)
            except Exception as e:
                print(f"[NPB Scraper] Failed to fetch {url}: {e}")
                continue

            soup = BeautifulSoup(html, 'html.parser')
            cur_date_str = d_ref

            for tr in soup.find_all('tr'):
                th = tr.find('th')
                if th and ('/' in th.get_text() or '月' in th.get_text()):
                    txt = th.get_text().strip()
                    m = re.search(r'(\d{1,2})/(\d{1,2})', txt)
                    if m:
                        cur_date_str = f"{s_year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

                # 필터링
                if start_date and cur_date_str < start_date:
                    continue
                if end_date and cur_date_str > end_date:
                    continue
                if target_date and not (start_date or end_date) and cur_date_str != target_date:
                    continue

                link = tr.find('a', href=re.compile(r'/scores/'))
                if not link:
                    continue

                href = link.get('href', '')
                clean_path = href.strip('/').replace('/', '_')
                official_id = f"NPB_{clean_path}" if not clean_path.startswith("NPB_") else clean_path

                row_text = ' '.join(tr.get_text().split())

                score_m = re.search(r'([^\d\s]+)\s+(\d+)\s*-\s*(\d+)\s+([^\d\s]+)', row_text)
                if not score_m:
                    continue

                raw_home = score_m.group(1).strip()
                home_score = int(score_m.group(2))
                away_score = int(score_m.group(3))
                raw_away = score_m.group(4).strip()

                home_team = map_npb_team(raw_home)
                away_team = map_npb_team(raw_away)

                remaining = row_text[score_m.end():].strip()
                tokens = remaining.split()
                stadium = tokens[0] if len(tokens) > 0 else "NPB 구장"
                start_time = "18:00"
                for tok in tokens:
                    if re.match(r'^\d{1,2}:\d{2}$', tok):
                        start_time = tok
                        break

                match_dt = f"{cur_date_str} {start_time}"

                all_games.append({
                    "sport_code": "BASEBALL",
                    "league_name": "일본 프로야구 (NPB)",
                    "official_id": official_id,
                    "match_date": match_dt,
                    "status": "FINISHED",
                    "home_team_name": home_team,
                    "away_team_name": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "stadium": stadium,
                    "league_id": "NPB"
                })

            if all_games:
                break

        return all_games

    def scrape_game_detail(self, official_id: str) -> Dict[str, Any]:
        """NPB 공식 경기 상세 박스스코어, 라인스코어, 선수 지표 수집"""
        path_part = official_id.replace("NPB_", "").replace("scores_", "")
        parts = path_part.split('_')
        if len(parts) >= 3:
            rel_url = f"/scores/{parts[0]}/{parts[1]}/{parts[2]}/"
        else:
            rel_url = f"/scores/{path_part.replace('_', '/')}/"

        box_url = f"https://npb.jp{rel_url}box.html"
        top_url = f"https://npb.jp{rel_url}"

        try:
            box_html = self._fetch_html(box_url)
        except Exception as e:
            print(f"[NPB Scraper] Failed to fetch box.html ({box_url}): {e}")
            box_html = ""

        try:
            top_html = self._fetch_html(top_url)
        except Exception as e:
            top_html = ""

        box_soup = BeautifulSoup(box_html, 'html.parser') if box_html else None
        top_soup = BeautifulSoup(top_html, 'html.parser') if top_html else None

        linescore_table = None
        batter_tables = []
        pitcher_tables = []

        if box_soup:
            for t in box_soup.find_all('table'):
                txt = t.get_text()
                if '守備' in txt and '打数' in txt:
                    batter_tables.append(t)
                elif '投手' in txt and '投球回' in txt and '自責点' in txt:
                    pitcher_tables.append(t)
                elif '1' in txt and '9' in txt and '計' in txt and not linescore_table:
                    linescore_table = t

        if not linescore_table and top_soup:
            for t in top_soup.find_all('table'):
                txt = t.get_text()
                if '1' in txt and '9' in txt and '計' in txt:
                    linescore_table = t
                    break

        innings_dict = {}
        away_name = "원정팀"
        home_name = "홈팀"
        away_h, away_e, home_h, home_e = 0, 0, 0, 0
        away_r, home_r = 0, 0

        if linescore_table:
            rows = linescore_table.find_all('tr')
            if len(rows) >= 3:
                away_cells = [c.get_text().strip() for c in rows[1].find_all(['th', 'td'])]
                home_cells = [c.get_text().strip() for c in rows[2].find_all(['th', 'td'])]

                away_name = map_npb_team(away_cells[0])
                home_name = map_npb_team(home_cells[0])

                for inn_idx in range(1, 10):
                    inn_str = str(inn_idx)
                    a_val = away_cells[inn_idx] if inn_idx < len(away_cells) else '-'
                    h_val = home_cells[inn_idx] if inn_idx < len(home_cells) else '-'
                    h_clean = h_val.replace('x', '').strip() if isinstance(h_val, str) else h_val
                    innings_dict[inn_str] = {
                        'away': int(a_val) if str(a_val).isdigit() else (a_val if a_val != '-' else 0),
                        'home': int(h_clean) if str(h_clean).isdigit() else (h_clean if h_clean != '-' else 0)
                    }

                for extra_idx in range(10, len(away_cells)):
                    val = away_cells[extra_idx]
                    if extra_idx < len(away_cells) - 3:
                        inn_str = str(extra_idx)
                        h_val = home_cells[extra_idx] if extra_idx < len(home_cells) else '-'
                        innings_dict[inn_str] = {
                            'away': int(val) if str(val).isdigit() else val,
                            'home': int(h_val) if str(h_val).isdigit() else h_val
                        }

                try:
                    away_r = clean_int(away_cells[-3])
                    away_h = clean_int(away_cells[-2])
                    away_e = clean_int(away_cells[-1])

                    home_r = clean_int(str(home_cells[-3]).replace('x', ''))
                    home_h = clean_int(home_cells[-2])
                    home_e = clean_int(home_cells[-1])
                except Exception:
                    pass

        period_scores = {
            'innings': innings_dict,
            'summary': {
                'away': {'R': away_r, 'H': away_h, 'E': away_e, 'B': 0},
                'home': {'R': home_r, 'H': home_h, 'E': home_e, 'B': 0}
            }
        }

        team_stats = {
            'hits': {'home': home_h, 'away': away_h},
            'errors': {'home': home_e, 'away': away_e},
            'left_on_base': {'home': 0, 'away': 0}
        }

        player_stats = []

        for team_idx, bt in enumerate(batter_tables):
            t_name = away_name if team_idx == 0 else home_name
            body = bt.find('tbody') or bt
            for tr in body.find_all('tr', recursive=False):
                cells = [c.get_text(separator=' ', strip=True) for c in tr.find_all(['th', 'td'], recursive=False)]
                if len(cells) < 7 or 'チーム計' in cells or '選手' in cells:
                    continue

                order_raw = cells[0].strip()
                pos_raw = cells[1].strip()
                p_name_raw = sanitize_player_name(cells[2].strip())
                p_name_ko = translate_npb_player_name(p_name_raw)
                p_name = p_name_ko if p_name_ko else p_name_raw

                pos_kor = translate_npb_position(pos_raw)
                pos_label = f"{order_raw}번 {pos_kor}" if order_raw and order_raw.isdigit() else pos_kor

                ab = clean_int(cells[3])
                r = clean_int(cells[4])
                h = clean_int(cells[5])
                rbi = clean_int(cells[6])
                sb = clean_int(cells[7]) if len(cells) > 7 else 0

                avg = f"{(h / ab):.3f}" if ab > 0 else ".000"

                player_stats.append({
                    "team_name": t_name,
                    "player_name": p_name,
                    "back_number": "",
                    "position": pos_label,
                    "minutes_played": 0,
                    "points": rbi,
                    "assists": 0,
                    "shots": ab,
                    "extra_stats": {
                        "type": "HITTER",
                        "player_type": "HITTER",
                        "name_raw": p_name_raw,
                        "ab": ab, "r": r, "h": h, "2b": 0, "3b": 0, "hr": 0,
                        "rbi": rbi, "bb": 0, "so": 0, "sb": sb,
                        "hits": h, "doubles": 0, "triples": 0, "homeruns": 0,
                        "runs": r, "walks": 0, "strikeouts": 0, "stolen_bases": sb,
                        "avg": avg, "ops": "-"
                    }
                })

        for team_idx, pt in enumerate(pitcher_tables):
            t_name = away_name if team_idx == 0 else home_name
            body = pt.find('tbody') or pt
            p_order = 0
            for tr in body.find_all('tr', recursive=False):
                cells = [c.get_text(separator=' ', strip=True) for c in tr.find_all(['th', 'td'], recursive=False)]
                if len(cells) < 10 or 'チーム計' in cells or '投手' in cells:
                    continue

                p_order += 1
                is_starter = (p_order == 1)

                dec_raw = cells[0].strip()
                dec_label = "승리투수 (W)" if dec_raw == "○" else ("패전투수 (L)" if dec_raw == "●" else ("세이브 (SV)" if dec_raw == "S" else ("홀드 (HD)" if dec_raw == "H" else "")))

                p_name_raw = sanitize_player_name(cells[1].strip())
                p_name_ko = translate_npb_player_name(p_name_raw)
                p_name = p_name_ko if p_name_ko else p_name_raw
                np = clean_int(cells[2])
                bf = clean_int(cells[3]) if len(cells) > 3 else 0
                ip_raw = cells[4].replace(' ', '').replace('\xa0', '').replace('+', '.0') if len(cells) > 4 else "1.0"
                h = clean_int(cells[5]) if len(cells) > 5 else 0
                hr = clean_int(cells[6]) if len(cells) > 6 else 0
                bb = clean_int(cells[7]) if len(cells) > 7 else 0
                hbp = clean_int(cells[8]) if len(cells) > 8 else 0
                so = clean_int(cells[9]) if len(cells) > 9 else 0
                r = clean_int(cells[12]) if len(cells) > 12 else 0
                er = clean_int(cells[13]) if len(cells) > 13 else 0

                try:
                    ip_f = float(ip_raw)
                    era = f"{(er * 9.0 / ip_f):.2f}" if ip_f > 0 else "0.00"
                except Exception:
                    era = "0.00"

                player_stats.append({
                    "team_name": t_name,
                    "player_name": p_name,
                    "back_number": "",
                    "position": "선발투수" if is_starter else "구원투수",
                    "minutes_played": 0,
                    "points": so,
                    "assists": 0,
                    "shots": int(float(ip_raw)) if '.' in ip_raw else clean_int(ip_raw),
                    "extra_stats": {
                        "type": "PITCHER",
                        "player_type": "PITCHER",
                        "is_starter": is_starter,
                        "starter": is_starter,
                        "pitcher_order": p_order,
                        "name_raw": p_name_raw,
                        "ip": ip_raw, "np": np, "h": h, "r": r, "er": er, "bb": bb,
                        "so": so, "hr": hr, "era": era, "whip": "-",
                        "decision": dec_label
                    }
                })

        events = []
        if top_soup:
            for t in top_soup.find_all('table'):
                txt = t.get_text()
                if '【本塁打】' in txt or '本塁打' in txt or '（' in txt:
                    for tr in t.find_all('tr'):
                        row_txt = tr.get_text(separator=' ', strip=True)
                        if '号' in row_txt and '（' in row_txt:
                            parts = row_txt.split()
                            p_cand = parts[1] if len(parts) > 1 else ""
                            events.append({
                                "time_display": "홈런",
                                "event_type": "HOMERUN",
                                "team_name": away_name if (len(parts) > 0 and parts[0].replace('【', '').replace('】', '') in away_name) else home_name,
                                "player_name": p_cand,
                                "description": row_txt,
                                "score_after": ""
                            })

        return {
            "period_scores": period_scores,
            "team_stats": team_stats,
            "source_url": box_url,
            "events": events,
            "player_stats": player_stats
        }
