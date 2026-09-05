# -*- coding: utf-8 -*-
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import time

class NewsService:
    _cached_news = []
    _last_fetched = 0
    _cache_ttl = 300  # 5 minutes

    CATEGORY_QUERIES = {
        "BASEBALL": [
            ("KBO 프로야구", "KBO"),
            ("MLB 메이저리그 오타니", "MLB")
        ],
        "SOCCER": [
            ("손흥민 토트넘 프리미어리그", "EPL"),
            ("이강인 챔피언스리그 파리생제르맹", "LIGUE1"),
            ("유럽축구 라리가 김민재", "EUROPE")
        ],
        "BASKETBALL": [
            ("NBA 미국프로농구", "NBA"),
            ("KBL 프로농구", "KBL")
        ]
    }

    @classmethod
    def get_real_news(cls, category: str = "ALL", force_refresh: bool = False):
        now = time.time()
        if force_refresh or not cls._cached_news or (now - cls._last_fetched > cls._cache_ttl):
            cls._refresh_all_news()

        if category == "ALL":
            return cls._cached_news
        return [item for item in cls._cached_news if item.get("category") == category]

    @classmethod
    def _refresh_all_news(cls):
        all_items = []
        item_id = 1

        for cat, query_list in cls.CATEGORY_QUERIES.items():
            for query_tuple in query_list:
                query, sub_tag = query_tuple
                url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                try:
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        root = ET.fromstring(resp.read())
                        xml_items = root.findall("./channel/item")
                        for i in xml_items[:4]:  # top 4 from each query
                            raw_title = i.find("title").text or ""
                            link = i.find("link").text or ""
                            pub_date_raw = i.find("pubDate").text or ""
                            source = i.find("source").text if i.find("source") is not None else "스포츠 종합"

                            # Clean title
                            clean_title = re.sub(r"\s*-\s*[^-]+$", "", raw_title).strip()
                            clean_title = clean_title.replace("&quot;", '"').replace("&apos;", "'")

                            # Extract and clean description
                            desc = clean_title
                            if i.find("description") is not None and i.find("description").text:
                                raw_desc = i.find("description").text
                                clean_desc = re.sub(r"<[^>]+>", "", raw_desc).strip()
                                clean_desc = clean_desc.replace("&quot;", '"').replace("&apos;", "'")
                                if clean_desc:
                                    desc = clean_desc

                            # Format date
                            formatted_date = cls._format_pub_date(pub_date_raw)

                            # Assign visual class and label
                            cat_label, cat_class = cls._get_category_meta(cat)
                            chips = cls._extract_tags(clean_title, cat, sub_tag)

                            all_items.append({
                                "id": item_id,
                                "category": cat,
                                "categoryLabel": cat_label,
                                "categoryClass": cat_class,
                                "title": clean_title,
                                "desc": desc[:160] + ("..." if len(desc) > 160 else ""),
                                "author": f"{source} 취재팀",
                                "source": source,
                                "link": link,
                                "date": formatted_date,
                                "chips": chips,
                                "content": desc + f"\n\n본 기사는 [{source}] 공식 보도 내용입니다. 원문 기사 링크를 통해 기사 전문과 사진, 후속 보도를 확인하실 수 있습니다."
                            })
                            item_id += 1
                except Exception as e:
                    print(f"[WARN] Error fetching news for {query}: {e}")

        # Add 1-2 curated in-depth analytics column articles
        all_items.append({
            "id": item_id,
            "category": "ANALYTICS",
            "categoryLabel": "📊 데이터 칼럼",
            "categoryClass": "bg-analytics",
            "title": "2026 현대 스포츠 세이버메트릭스: 승패의 우연을 걷어내는 계량 모델의 진화",
            "desc": "야구의 wOBA와 FIP, 축구의 xG와 PPDA, 농구의 Pace와 TS%가 증명하는 스포츠 데이터 인텔리전스 분석.",
            "author": "스포허브 데이터랩 수석분석관",
            "source": "SPORTIX 공식 리서치",
            "link": "/dashboard",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "chips": ["wOBA_FIP", "xG_PPDA", "Pace_TS%", "세이버메트릭스"],
            "content": "현대 프로 스포츠는 이제 단순한 클래식 기록(타율, 승수, 득점)을 넘어 선수의 본질적 기여도와 팀의 구조적 승리 기대치를 평가하는 세이버메트릭스 시대로 완전히 전환되었습니다.\n\n당사 SPORTIX PRO 데이터 엔진은 매일 실시간으로 수집되는 3대 종목 259경기 이상의 박스스코어를 기반으로 3·5·7·10일 롤링 트렌드를 정밀 산출하여 현장과 미디어에 공급하고 있습니다."
        })

        # Sort with diverse sports mix
        cls._cached_news = all_items
        cls._last_fetched = time.time()
        print(f"[INFO] Successfully loaded {len(all_items)} real sports news articles.")

    @staticmethod
    def _format_pub_date(pub_date_str: str) -> str:
        if not pub_date_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            # e.g., 'Sat, 05 Sep 2026 02:35:57 GMT'
            dt = datetime.strptime(pub_date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _get_category_meta(cat: str):
        if cat == "BASEBALL":
            return ("⚾ 야구", "bg-baseball")
        elif cat == "SOCCER":
            return ("⚽ 축구", "bg-soccer")
        elif cat == "BASKETBALL":
            return ("🏀 농구", "bg-basketball")
        return ("📊 데이터 칼럼", "bg-analytics")

    @staticmethod
    def _extract_tags(title: str, cat: str, sub_tag: str):
        tags = [f"#{sub_tag}"]
        if "오타니" in title: tags.append("#오타니")
        if "김도영" in title: tags.append("#김도영")
        if "손흥민" in title: tags.append("#손흥민")
        if "이강인" in title: tags.append("#이강인")
        if "김민재" in title: tags.append("#김민재")
        if "토트넘" in title: tags.append("#토트넘")
        if "KBO" in title: tags.append("#KBO리그")
        if "MLB" in title: tags.append("#메이저리그")
        if "NBA" in title: tags.append("#NBA")
        if "커리" in title or "Curry" in title: tags.append("#스테판커리")
        if len(tags) < 3:
            if cat == "BASEBALL": tags.append("#타격생산력")
            elif cat == "SOCCER": tags.append("#xG_기대득점")
            elif cat == "BASKETBALL": tags.append("#공격효율_ORtg")
        return tags[:4]
