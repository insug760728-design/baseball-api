import sys, re, unicodedata, html
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def fix_mojibake(text: str) -> str:
    """Fix common Mojibake caused by UTF-8 bytes being decoded as Latin-1 (ISO-8859-1) or CP1252."""
    if not text or not isinstance(text, str):
        return ""
    if any(ch in text for ch in ('Ã', 'Â', 'Å', 'Î', 'â', 'é', 'è', 'ï', '\xc3', '\xc2')):
        # Try full string conversion first
        try:
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        try:
            return text.encode('cp1252').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        # Fallback: decode token by token for mixed CJK + Mojibake strings
        def _sub_token(m):
            token = m.group(0)
            try:
                return token.encode('latin-1').decode('utf-8')
            except Exception:
                try:
                    return token.encode('cp1252').decode('utf-8')
                except Exception:
                    return token
        text = re.sub(r'[\u0080-\u00FF]+', _sub_token, text)
    return text

def sanitize_text(raw: str) -> str:
    """Comprehensive text sanitization for descriptions, timelines, team names, and notes."""
    if not raw or not isinstance(raw, str):
        return ""
    # 1. Unescape HTML entities (e.g. &amp;, &#39;, &quot;, &nbsp;)
    text = html.unescape(raw)
    # 2. Remove zero-width characters, BOM, replacement chars (\ufffd), and unprintable control characters
    text = re.sub(r'[\u200B-\u200D\uFEFF\uFFFD\x00-\x1F\x7F]', '', text)
    # 3. Standardize quotes, apostrophes and hyphens
    text = re.sub(r'[\u2018\u2019\u00b4`\u2032]', "'", text)
    text = re.sub(r'[\u2013\u2014\u2212]', '-', text)
    # 4. Fix Mojibake (UTF-8 bytes erroneously decoded as Latin-1/CP1252)
    text = fix_mojibake(text)
    # 5. Unicode NFC normalization (recombine separated accents/diacritics e.g. e + \u0301 -> é)
    text = unicodedata.normalize('NFC', text)
    # 6. Normalize all whitespaces (including \xa0, \u3000 Japanese full-width space) to standard single space
    text = re.sub(r'[\s\u00a0\u3000]+', ' ', text).strip()
    return text

def sanitize_player_name(raw: str) -> str:
    """Sanitize player names from external APIs, web scraping, and user queries."""
    return sanitize_text(raw)


# =============================================================
# ⚾ 1. MLB / 해외 주요 선수 풀네임 공식 한글 표준 표기 사전
# =============================================================
FULL_NAMES = {
    # Starters & Rotations (MLB)
    "Paul Skenes": "폴 스킨스", "Tarik Skubal": "타릭 스쿠발", "Zack Wheeler": "잭 휠러", "Chris Sale": "크리스 세일",
    "Corbin Burnes": "코빈 번스", "Shohei Ohtani": "오타니 쇼헤이", "Yoshinobu Yamamoto": "야마모토 요시노부",
    "Shota Imanaga": "이마나가 쇼타", "Kodai Senga": "센가 코다이", "Yu Darvish": "다르빗슈 유",
    "Tyler Glasnow": "타일러 글래스나우", "Spencer Strider": "스펜서 스트라이더", "Spencer Schwellenbach": "스펜서 슈웰렌바크",
    "Cristopher Sanchez": "크리스토퍼 산체스", "Cristopher Sánchez": "크리스토퍼 산체스", "Ranger Suarez": "레인저 수아레즈",
    "Ranger Suárez": "레인저 수아레즈", "Gerrit Cole": "게릿 콜", "Carlos Rodon": "카를로스 로돈", "Carlos Rodón": "카를로스 로돈",
    "Nestor Cortes": "네스터 코르테스", "Nestor Cortés": "네스터 코르테스", "Marcus Stroman": "마커스 스트로먼",
    "Luis Gil": "루이스 힐", "Clarke Schmidt": "클라크 슈미트", "Kevin Gausman": "케빈 가우스먼",
    "Jose Berrios": "호세 베리오스", "José Berríos": "호세 베리오스", "Chris Bassitt": "크리스 배싯",
    "Bowden Francis": "보든 프랜시스", "Yusei Kikuchi": "기쿠치 유세이", "Tanner Houck": "태너 하우크",
    "Kutter Crawford": "커터 크로포드", "Brayan Bello": "브라얀 베요", "Nick Pivetta": "닉 피베타",
    "Grayson Rodriguez": "그레이슨 로드리게스", "Dean Kremer": "딘 크레머", "Albert Suarez": "알버트 수아레즈",
    "Albert Suárez": "알버트 수아레즈", "Zach Eflin": "잭 에플린", "Ryan Pepiot": "라이언 페피오",
    "Taj Bradley": "타지 브래들리", "Shane Baz": "셰인 바즈", "Jeffrey Springs": "제프리 스프링스",
    "Zack Littell": "잭 리텔", "Tanner Bibee": "태너 바이비", "Gavin Williams": "개빈 윌리엄스",
    "Ben Lively": "벤 라이블리", "Matthew Boyd": "매튜 보이드", "Joey Cantillo": "조이 칸티요",
    "Jack Flaherty": "잭 플래허티", "Reese Olson": "리스 올슨", "Keider Montero": "케이더 몬테로",
    "Pablo Lopez": "파블로 로페즈", "Pablo López": "파블로 로페즈", "Bailey Ober": "베일리 오버",
    "Joe Ryan": "조 라이언", "Simeon Woods Richardson": "시미언 우즈-리차드슨", "David Festa": "데이비드 페스타",
    "Zebby Matthews": "제비 매튜스", "Garrett Crochet": "개럿 크로셰", "Jonathan Cannon": "조나단 캐넌",
    "Chris Flexen": "크리스 플렉센", "Davis Martin": "데이비스 마틴", "Nick Nastrini": "닉 나스트리니",
    "Framber Valdez": "프람버 발데스", "Hunter Brown": "헌터 브라운", "Ronel Blanco": "로넬 블랑코",
    "Spencer Arrighetti": "스펜서 아리게티", "Nathan Eovaldi": "네이선 이볼디", "Andrew Heaney": "앤드루 히니",
    "Cody Bradford": "코디 브래드포드", "Jack Leiter": "잭 라이터", "Kumar Rocker": "쿠마 로커",
    "Logan Gilbert": "로건 길버트", "George Kirby": "조지 커비", "Bryan Woo": "브라이언 우",
    "Bryce Miller": "브라이스 밀러", "Logan Webb": "로건 웹", "Blake Snell": "블레이크 스넬",
    "Kyle Harrison": "카일 해리슨", "Hayden Birdsong": "헤이든 버드송", "Robbie Ray": "로비 레이",
    "Mason Black": "메이슨 블랙", "Landen Roupp": "랜든 룹", "Dylan Cease": "딜런 시즈",
    "Michael King": "마이클 킹", "Joe Musgrove": "조 머스그로브", "Matt Waldron": "맷 월드론",
    "Martin Perez": "마틴 페레즈", "Martín Pérez": "마틴 페레즈", "Clayton Kershaw": "클레이튼 커쇼",
    "Gavin Stone": "개빈 스톤", "Bobby Miller": "바비 밀러", "Walker Buehler": "워커 뷸러",
    "Landon Knack": "랜던 낵", "Justin Wrobleski": "저스틴 로블레스키", "Zac Gallen": "잭 갤런",
    "Merrill Kelly": "메릴 켈리", "Brandon Pfaadt": "브랜든 팟", "Eduardo Rodriguez": "에두아르도 로드리게스",
    "Eduardo Rodríguez": "에두아르도 로드리게스", "Jordan Montgomery": "조던 몽고메리", "Ryne Nelson": "라인 넬슨",
    "Kyle Freeland": "카일 프리랜드", "Cal Quantrill": "칼 콴트릴", "Austin Gomber": "오스틴 곰버",
    "Ryan Feltner": "라이언 펠트너", "Bradley Blalock": "브래들리 블레이록", "Ty Blach": "타이 블라크",
    "JP Sears": "JP 시어스", "J.P. Sears": "JP 시어스", "Mitch Spence": "미치 스펜스",
    "Osvaldo Bido": "오스발도 비도", "JT Ginn": "JT 진", "J.T. Ginn": "JT 진",
    "Joey Estes": "조이 에스테스", "Paul Blackburn": "폴 블랙번", "Mason Miller": "메이슨 밀러",
    "Tyler Anderson": "타일러 앤더슨", "Jose Soriano": "호세 소리아노", "José Soriano": "호세 소리아노",
    "Griffin Canning": "그리핀 캐닝", "Jack Kochanowicz": "잭 코차노위츠", "Reid Detmers": "리드 데트머스",
    "Caden Dana": "케이든 다나", "Carson Fulmer": "카슨 풀머", "Mitch Keller": "미치 켈러",
    "Bailey Falter": "베일리 폴터", "Luis L. Ortiz": "루이스 오르티스", "Luis Ortiz": "루이스 오르티스",
    "Sonny Gray": "소니 그레이", "Erick Fedde": "에릭 페디", "Kyle Gibson": "카일 깁슨",
    "Miles Mikolas": "마일스 마이콜라스", "Andre Pallante": "안드레 팔란테", "Michael McGreevy": "마이클 맥그리비",
    "Justin Steele": "저스틴 스틸", "Jameson Taillon": "제임슨 타이욘", "Javier Assad": "하비에르 아사드",
    "Kyle Hendricks": "카일 헨드릭스", "Jordan Wicks": "조던 윅스", "Hunter Greene": "헌터 그린",
    "Nick Lodolo": "닉 로돌로", "Andrew Abbott": "앤드루 애벗", "Rhett Lowder": "렛 라우더",
    "Julian Aguiar": "줄리안 아기아르", "Freddy Peralta": "프레디 페랄타", "Colin Rea": "콜린 레이",
    "Tobias Myers": "토비아스 마이어스", "Frankie Montas": "프랭키 몬타스", "Aaron Civale": "애런 시발레",
    "DL Hall": "DL 홀", "D.L. Hall": "DL 홀", "Reynaldo Lopez": "레이날도 로페즈",
    "Reynaldo López": "레이날도 로페즈", "Max Fried": "맥스 프리드", "Charlie Morton": "찰리 모튼",
    "Grant Holmes": "그랜트 홈즈", "Ian Anderson": "이안 앤더슨", "Hurston Waldrep": "허스턴 왈드렙",
    "Sean Manaea": "션 마네아", "Luis Severino": "루이스 세베리노", "David Peterson": "데이비드 피터슨",
    "Jose Quintana": "호세 킨타나", "José Quintana": "호세 킨타나", "Tylor Megill": "타일러 메길",
    "MacKenzie Gore": "맥켄지 고어", "Mackenzie Gore": "맥켄지 고어", "Jake Irvin": "제이크 어빈",
    "DJ Herz": "DJ 헤르츠", "D.J. Herz": "DJ 헤르츠", "Mitchell Parker": "미첼 파커",
    "Patrick Corbin": "패트릭 코빈", "Edward Cabrera": "에드워드 카브레라", "Max Meyer": "맥스 마이어",
    "Valente Bellozo": "발렌테 벨로조", "Adam Oller": "아담 올러", "Darren McCaughan": "대런 맥코건",
    "Xzavion Curry": "즈자비온 커리", "Michael Lorenzen": "마이클 로렌젠", "Jose Urena": "호세 우레냐",
    "Michael Wacha": "마이클 와카", "Cole Ragans": "콜 레이건스", "Seth Lugo": "세스 루고",
    "Brady Singer": "브래디 싱어", "Alec Marsh": "알렉 마쉬", "Aaron Nola": "애런 놀라",
    "Parker Messick": "파커 메식", "Anthony Kay": "앤서니 케이", "Mason Montgomery": "메이슨 몽고메리",
    "Cade Cavalli": "케이드 카발리", "Jacob Misiorowski": "제이콥 미시오로우스키",
    "Clay Holmes": "클레이 홈즈", "Wilber Dotel": "윌버 도텔", "Miguel Ulloa": "미겔 우요아",
    "Walbert Ureña": "왈버트 우레냐", "Walbert Urena": "왈버트 우레냐", "Connor Prielipp": "코너 프릴립",
    "Peter Lambert": "피터 램버트", "Tyler Mahle": "타일러 말리", "Gage Jump": "게이지 점프",
    "Jackson Jobe": "잭슨 조브", "Gabriel Hughes": "가브리엘 휴즈", "Payton Tolle": "페이튼 톨레",
    "Noah Cameron": "노아 카메론", "Cam Schlittler": "캠 슐리틀러", "Bubba Chandler": "버바 챈들러",
    "Eury Pérez": "유리 페레즈", "Eury Perez": "유리 페레즈", "Zac Thornton": "잭 손튼",
    "Zach Thornton": "잭 손튼", "Randy Dobnak": "랜디 도브낙", "Tyler Phillips": "타일러 필립스",
    "Andrew Painter": "앤드루 페인터", "Cesar Perdomo": "세사르 페르도모", "César Perdomo": "세사르 페르도모",
    "Andrew Alvarez": "앤드루 알바레즈", "Andrew Álvarez": "앤드루 알바레즈", "Ian Seymour": "이안 시모어",
    "Kyle Leahy": "카일 리히", "Chase Burns": "체이스 번스", "Jacob Lopez": "제이콥 로페즈",
    "Jacob López": "제이콥 로페즈", "Nolan McLean": "놀란 맥클레인", "Drew Rasmussen": "드류 라스무센",
    "Ryan Gusto": "라이언 구스토", "Dustin May": "더스틴 메이", "Matthew Liberatore": "매튜 리베라토레",
    "Anthony Molina": "앤서니 몰리나", "Hayden Wesneski": "헤이든 웨스네스키", "Christian Scott": "크리스천 스콧",
    "Trevor Rogers": "트레버 로저스", "Tanner Gordon": "태너 고든", "Kyle Bradish": "카일 브래디시",
    "Jacob deGrom": "제이콥 디그롬", "Jacob DeGrom": "제이콥 디그롬", "Max Scherzer": "맥스 슈어저",
    "Luis Castillo": "루이스 카스티요", "Christian Javier": "크리스티안 하비에르", "Troy Melton": "트로이 멜튼",

    # Korean MLB
    "Jung Hoo Lee": "이정후", "Jung-Hoo Lee": "이정후", "Ha-Seong Kim": "김하성", "Ha-seong Kim": "김하성",
    "Ji-Hwan Bae": "배지환", "Ji Hwan Bae": "배지환", "Hyun Jin Ryu": "류현진", "Kwang Hyun Kim": "김광현",
    
    # MLB Batters / Superstars
    "Aaron Judge": "애런 저지", "Juan Soto": "후안 소토", "Mookie Betts": "무키 베츠", "Freddie Freeman": "프레디 프리먼",
    "Bryce Harper": "브라이스 하퍼", "Gunnar Henderson": "거너 헨더슨", "Bobby Witt Jr.": "바비 위트 주니어",
    "Bobby Witt Jr": "바비 위트 주니어", "Adley Rutschman": "애들리 러치맨", "Elly De La Cruz": "엘리 데 라 크루즈",
    "Fernando Tatis Jr.": "페르난도 타티스 주니어", "Fernando Tatis Jr": "페르난도 타티스 주니어",
    "Manny Machado": "매니 마차도", "Jurickson Profar": "주릭슨 프로파", "Jackson Merrill": "잭슨 메릴",
    "Pete Alonso": "피트 알론소", "Francisco Lindor": "프란시스코 린도어", "Kyle Schwarber": "카일 슈와버",
    "Trea Turner": "트레이 터너", "Alec Bohm": "알렉 봄", "Corey Seager": "코리 시거", "Marcus Semien": "마커스 세미엔",
    "Jose Altuve": "호세 알투베", "Yordan Alvarez": "요르단 알바레즈", "Alex Bregman": "알렉스 브레그먼",
    "Jose Ramirez": "호세 라미레즈", "José Ramírez": "호세 라미레즈", "Steven Kwan": "스티븐 관",
    "Josh Naylor": "조시 네일러", "Vladimir Guerrero Jr.": "블라디미르 게레로 주니어",
    "Vladimir Guerrero Jr": "블라디미르 게레로 주니어", "George Springer": "조지 스프링어", "Bo Bichette": "보 비셋",
    "Rafael Devers": "라파엘 디버스", "Jarren Duran": "재런 두란", "Triston Casas": "트리스톤 카사스",
    "Seiya Suzuki": "스즈키 세이야", "Masataka Yoshida": "요시다 마사타카", "Cody Bellinger": "코디 벨린저",
    "Ian Happ": "이안 햅", "Dansby Swanson": "댄스비 스완슨", "Nico Hoerner": "니코 호너",
    "Marcell Ozuna": "마르셀 오주나", "Matt Olson": "맷 올슨", "Austin Riley": "오스틴 라일리",
    "Michael Harris II": "마이클 해리스 2세", "Ketel Marte": "케텔 마르테", "Corbin Carroll": "코빈 캐롤",
    "Christian Walker": "크리스천 워커", "Lourdes Gurriel Jr.": "루르데스 구리엘 주니어",
    "Lourdes Gurriel Jr": "루르데스 구리엘 주니어", "Jackson Chourio": "잭슨 츄리오", "Willy Adames": "윌리 아다메스",
    "William Contreras": "윌리엄 콘트레라스", "Sal Frelick": "샐 프렐릭", "Paul Goldschmidt": "폴 골드슈미트",
    "Nolan Arenado": "놀란 아레나도", "Alec Burleson": "알렉 벌레슨", "Brent Rooker": "브렌트 루커",
    "JJ Bleday": "JJ 블레데이", "Shea Langeliers": "셰이 랭겔리어스", "Lawrence Butler": "로렌스 버틀러",
    "Julio Rodriguez": "훌리오 로드리게스", "Julio Rodríguez": "훌리오 로드리게스", "Cal Raleigh": "칼 랄리",
    "Randy Arozarena": "랜디 아로자레나", "Josh Lowe": "조시 로우", "Yandy Diaz": "얀디 디아즈",
    "Yandy Díaz": "얀디 디아즈", "Brandon Lowe": "브랜든 로우", "Christopher Morel": "크리스토퍼 모렐",
    "Oneil Cruz": "오닐 크루즈", "Bryan Reynolds": "브라이언 레이놀즈", "Ke'Bryan Hayes": "키브라이언 헤이즈",
    "Spencer Steer": "스펜서 스티어", "Jonathan India": "조나단 인디아", "TJ Friedl": "TJ 프리들",
    "Ezequiel Tovar": "에세키엘 토바", "Ryan McMahon": "라이언 맥맨", "Brenton Doyle": "브렌턴 도일",
    "Luis Garcia Jr.": "루이스 가르시아 주니어", "CJ Abrams": "CJ 에이브람스", "James Wood": "제임스 우드",
    "Lane Thomas": "레인 토마스", "Jazz Chisholm Jr.": "재즈 치좀 주니어", "Jazz Chisholm Jr": "재즈 치좀 주니어",
    "Jake Burger": "제이크 버거", "Jesus Sanchez": "헤수스 산체스", "Jesús Sánchez": "헤수스 산체스",

    # =============================================================
    # 🇯🇵 NPB 12개 구단 전체 투수/선발/주요 선수 일본 한자 & 가타카나 완벽 표기
    # =============================================================
    "戸郷 翔征": "토고 쇼세이", "戸郷翔征": "토고 쇼세이", "Togo Shosei": "토고 쇼세이", "Shosei Togo": "토고 쇼세이",
    "柳 裕也": "야나기 유야", "柳裕也": "야나기 유야", "Yanagi Yuya": "야나기 유야", "Yuya Yanagi": "야나기 유야",
    "東 克樹": "아즈마 카츠키", "東克樹": "아즈마 카츠키", "Higashi Katsuki": "아즈마 카츠키", "Katsuki Higashi": "아즈마 카츠키",
    "奥川 恭伸": "오쿠가와 야스노부", "奥川恭伸": "오쿠가와 야스노부", "Okugawa Yasunobu": "오쿠가와 야스노부",
    "才木 浩人": "사이키 히로토", "才木浩人": "사이키 히로토", "Saiki Hiroto": "사이키 히로토", "Hiroto Saiki": "사이키 히로토",
    "床田 寛樹": "토코다 히로키", "床田寛樹": "토코다 히로키", "Tokoda Hiroki": "토코다 히로키", "Hiroki Tokoda": "토코다 히로키",
    "田中 晴也": "타나카 세이야", "田中晴也": "타나카 세이야", "Tanaka Seiya": "타나카 세이야",
    "前田 健太": "마에다 켄타", "前田健太": "마에다 켄타", "Maeda Kenta": "마에다 켄타", "Kenta Maeda": "마에다 켄타",
    "平良 海馬": "타이라 카이마", "平良海馬": "타이라 카이마", "Taira Kaima": "타이라 카이마", "Kaima Taira": "타이라 카이마",
    "山﨑 福也": "야마사키 사치야", "山﨑福也": "야마사키 사치야", "山崎 福也": "야마사키 사치야", "山崎福也": "야마사키 사치야", "Yamasaki Sachiya": "야마사키 사치야",
    "有原 航平": "아리하라 코헤이", "有原航平": "아리하라 코헤이", "Arihara Kohei": "아리하라 코헤이",
    "宮城 大弥": "미야기 히로야", "宮城大弥": "미야기 히로야", "Miyagi Hiroya": "미야기 히로야", "Hiroya Miyagi": "미야기 히로야",
    "村上 頌樹": "무라카미 쇼키", "村上頌樹": "무라카미 쇼키", "Murakami Shoki": "무라카미 쇼키",
    "今井 達也": "이마이 타츠야", "今井達也": "이마이 타츠야", "Imai Tatsuya": "이마이 타츠야", "Tatsuya Imai": "이마이 타츠야",
    "伊藤 大海": "이토 히로미", "伊藤大海": "이토 히로미", "Ito Hiromi": "이토 히로미", "Hiromi Ito": "이토 히로미",
    "小島 和哉": "코지마 카즈야", "小島和哉": "코지마 카즈야", "Kojima Kazuya": "코지마 카즈야",
    "早川 隆久": "하야카와 타카히사", "早川隆久": "하야카와 타카히사", "Hayakawa Takahisa": "하야카와 타카히사",
    "小川 泰弘": "오가와 야스히로", "小川泰弘": "오가와 야스히로", "Ogawa Yasuhiro": "오가와 야스히로",
    "高橋 宏斗": "타카하시 히로토", "高橋宏斗": "타카하시 히로토", "髙橋 宏斗": "타카하시 히로토", "髙橋宏斗": "타카하시 히로토", "Takahashi Hiroto": "타카하시 히로토",
    "九里 亜蓮": "쿠리 아렌", "九里亜蓮": "쿠리 아렌", "Kuri Aren": "쿠리 아렌", "Aren Kuri": "쿠리 아렌",
    "大瀬良 大地": "오오세라 다이치", "大瀬良大地": "오오세라 다이치", "Osera Daichi": "오오세라 다이치",
    "菅野 智之": "스가노 토모유키", "菅野智之": "스가노 토모유키", "Sugano Tomoyuki": "스가노 토모유키", "Tomoyuki Sugano": "스가노 토모유키",
    "髙橋 光成": "타카하시 코나", "髙橋光成": "타카하시 코나", "高橋 光成": "타카하시 코나", "高橋光成": "타카하시 코나", "Takahashi Kona": "타카하시 코나",
    "隅田 知一郎": "스미다 치히로", "隅田知一郎": "스미다 치히로", "Sumida Chihiro": "스미다 치히로",
    "松本 航": "마츠모토 와타루", "松本航": "마츠모토 와타루", "Matsumoto Wataru": "마츠모토 와타루",
    "山下 舜平大": "야마시타 슌페이타", "山下舜平大": "야마시타 슌페이타", "Yamashita Shunpeita": "야마시타 슌페이타",
    "田嶋 大樹": "타지마 다이키", "田嶋대樹": "타지마 다이키", "田嶋大樹": "타지마 다이키", "Tajima Daiki": "타지마 다이키",
    "種市 篤暉": "타네이치 아츠키", "種市篤暉": "타네이치 아츠키", "Taneichi Atsuki": "타네이치 아츠키",
    "佐々木 朗希": "사사키 로키", "佐々木朗希": "사사키 로키", "Sasaki Roki": "사사키 로키", "Roki Sasaki": "사사키 로키",
    "岸 孝之": "키시 타카유키", "岸孝之": "키시 타카유키", "Kishi Takayuki": "키시 타카유키",
    "則本 昂大": "노리모토 타카히로", "則本昂大": "노리모토 타카히로", "Norimoto Takahiro": "노리모토 타카히로",
    "加藤 貴之": "카토 타카유키", "加藤貴之": "카토 타카유키", "Kato Takayuki": "카토 타카유키",
    "上原 健太": "우에하라 켄타", "上原健太": "우에하라 켄타", "Uehara Kenta": "우에하라 켄타",
    "東浜 巨": "히가시하마 나오", "東浜巨": "히가시하마 나오", "Higashihama Nao": "히가시하마 나오",
    "大津 亮介": "오오츠 료스케", "大津亮介": "오오츠 료스케", "Otsu Ryosuke": "오오츠 료스케",
    "和田 毅": "와다 츠요시", "和田毅": "와다 츠요시", "Wada Tsuyoshi": "와다 츠요시",
    "森下 暢仁": "모리시타 마사토", "森下暢仁": "모리시타 마사토", "Morishita Masato": "모리시타 마사토",
    "小園 健太": "코조노 켄타", "小園健太": "코조노 켄타", "Kozono Kenta": "코조노 켄타",
    "大貫 晋一": "오오누키 신이치", "大貫晋一": "오오누키 신이치", "Onuki Shinichi": "오오누키 신이치",
    "高橋 奎二": "타카하시 케이지", "高橋奎二": "타카하시 케이지", "Takahashi Keiji": "타카하시 케이지",
    "吉村 貢司郎": "요시무라 코지로", "吉村貢司郎": "요시무라 코지로", "Yoshimura Kojiro": "요시무라 코지로",
    "小笠原 慎之介": "오가사와라 신노스케", "小笠原慎之介": "오가사와라 신노스케", "Ogasawara Shinnosuke": "오가사와라 신노스케",
    "大野 雄大": "오오노 유다이", "大野雄大": "오오노 유다이", "Ohno Yudai": "오오노 유다이",
    "西 勇輝": "니시 유키", "西勇輝": "니시 유키", "Nishi Yuki": "니시 유키",
    "伊藤 将司": "이토 마사시", "伊藤将司": "이토 마사시", "Ito Masashi": "이토 마사시",
    "青柳 晃洋": "아오야기 코요", "青柳晃洋": "아오야기 코요", "Aoyagi Koyo": "아오야기 코요",
    "大竹 耕太郎": "오오타케 코타로", "大竹耕太郎": "오오타케 코타로", "Otake Kotaro": "오오타케 코타로",
    "山崎 伊織": "야마사키 이오리", "山崎伊織": "야마사키 이오리", "Yamasaki Iori": "야마사키 이오리",
    "赤星 優志": "아카호시 유지", "赤星優志": "아카호시 유지", "Akahoshi Yuji": "아카호시 유지",
    "井上 温大": "이노우에 하루토", "井上温大": "이노우에 하루토", "Inoue Haruto": "이노우에 하루토",
    "武内 夏暉": "타케우치 나츠키", "武内夏暉": "타케우치 나츠키", "Takeuchi Natsuki": "타케우치 나츠키",
    "髙島 泰都": "타카시마 타이스케", "高島 泰都": "타카시마 타이스케", "高島泰都": "타카시마 타이스케",
    "涌井 秀章": "와쿠이 히데아키", "涌井秀章": "와쿠이 히데아키", "Wakui Hideaki": "와쿠이 히데아키",
    "高梨 雄平": "타카나시 유헤이", "高梨雄平": "타카나시 유헤이", "Takanashi Yuhei": "타카나시 유헤이",
    "尾形 崇斗": "오가타 슈토", "尾形崇斗": "오가타 슈토", "Ogata Shuto": "오가타 슈토",
    "佐藤 爽": "사토 소우", "佐藤爽": "사토 소우",
    "高野 脩汰": "타카노 슈타", "高野脩汰": "타카노 슈타",
    "松本 晴": "마츠모토 하루", "松本晴": "마츠모토 하루",
    "深沢 鳳介": "후카자와 호스케", "深沢鳳介": "후카자와 호스케",
    "栗林 良吏": "쿠리바야시 료지", "栗林良吏": "쿠리바야시 료지",
    "金丸 夢斗": "카네마루 유메토", "金丸夢斗": "카네마루 유메토",
    "豆田 泰志": "마메다 타츠키", "豆田泰志": "마메다 타츠키",
    "佐藤 隼輔": "사토 슌스케", "佐藤隼輔": "사토 슌스케",
    "黒木 優太": "쿠로키 유타", "黒木優太": "쿠로키 유타",
    "本田 圭佑": "혼다 케이스케", "本田圭佑": "혼다 케이스케",
    "水上 由伸": "미즈카미 요시노부", "水上由伸": "미즈카미 요시노부",
    "富山 凌雅": "토미야마 료타", "富山凌雅": "토미야마 료타",
    "椋木 蓮": "무쿠노키 렌", "椋木蓮": "무쿠노키 렌",
    "山﨑 颯一郎": "야마사키 소이치로", "山﨑颯一郎": "야마사키 소이치로",
    "阿部 翔太": "아베 쇼타", "阿部翔太": "아베 쇼타",
    "山田 修義": "야마다 노부요시", "山田修義": "야마다 노부요시",
    "曽谷 龍平": "소타니 류헤이", "曽谷龍平": "소타니 류헤이",
    "菅井 信也": "스가이 신야", "菅井信也": "스가이 신야",
    "片山 皓心": "카타야마 코신", "片山皓心": "카타야마 코신", "Katayama Koshin": "카타야마 코신",
    "山口 廉王": "야마구치 레오", "山口廉王": "야마구치 레오", "Yamaguchi Reo": "야마구치 레오",
    "渡邉 勇太朗": "와타나베 유타로", "渡邉勇太朗": "와타나베 유타로", "渡辺 勇太朗": "와타나베 유타로", "渡辺勇太朗": "와타나베 유타로", "Watanabe Yutaro": "와타나베 유타로",
    "前田 悠伍": "마에다 유고", "前田悠伍": "마에다 유고", "Maeda Yugo": "마에다 유고",
    "石川 柊太": "이시카와 슈타", "石川柊太": "이시카와 슈타", "Ishikawa Shuta": "이시카와 슈타",

    # Katakana / Foreigners in NPB
    "マチャド": "마차도", "A.マチャド": "안드레스 마차도", "A.마차도": "안드레스 마차도",
    "ペルドモ": "루이스 페르도모", "L.ペルドモ": "루이스 페르도모", "L.페르도모": "루이스 페르도모",
    "エスピノーザ": "안데르손 에스피노자", "A.エスピノーザ": "안데르손 에스피노자", "A.에스피노자": "안데르손 에스피노자",
    "モイネロ": "리반 모이넬로", "L.モイネロ": "리반 모이넬로", "L.모이넬로": "리반 모이넬로",
    "オスナ": "로베르토 오스나", "R.オスナ": "로베르토 오스나", "J.オスナ": "호세 오스나",
    "ヘルナンデス": "에르난데스", "E.ヘルナンデス": "엘리에세르 에르난데스",
    "マルティネス": "라이델 마르티네스", "マルチネス": "라이델 마르티네스", "R.マルティネス": "라이델 마르티네스", "R.マルチネス": "라이델 마르티네스",
    "ルイーズ": "루이즈", "サイスニード": "사이 스니드", "C.サイスニード": "사이 스니드",
    "ケイ": "안소니 케이", "A.ケイ": "안소니 케이", "ジャクソン": "안드레 잭슨", "A.ジャクソン": "안드레 잭슨",
    "バウアー": "트레버 바우어", "T.バウアー": "트레버 바우어", "エンス": "디트릭 엔스", "D.エンス": "디트릭 엔스",
    "メルセデス": "C.C. 멜세데스", "C.C.メルセデス": "C.C. 멜세데스",
    "サンタナ": "도밍고 산타나", "D.サンタナ": "도밍고 산타나", "ポランコ": "그레고리 폴랑코", "G.ポランコ": "그레고리 폴랑코",
    "ソト": "네프탈리 소토", "N.ソト": "네프탈리 소토", "ウォーカー": "아담 워커", "C.ウォーカー": "크리스천 워커",
    "ディアス": "디아즈", "ゴンザレス": "곤잘레스", "カスティーヨ": "카스티요",
    "バルドナード": "발도나도", "グリフィン": "포스터 그리핀", "F.グリフィン": "포스터 그리핀",
    "メンデス": "요안데르 멘데스", "Y.メンデス": "요안데르 멘데스", "ボス": "코디 보스", "C.ボス": "코디 보스",
    "ビシエド": "다얀 비시에도", "D.ビシエド": "다얀 비시에도", "カリ스테": "올란도 칼리스테", "ロドリ게스": "로드리게스", "ロドリゲス": "로드리게스",
    "Ｓ．ジェリー": "S.젤리", "S.ジェリー": "S.젤리", "ジェリー": "S.젤리", "마타": "데이비드 마타",
    "ラトリッジ": "러틀리지", "クラーク": "클라크", "スチュワート": "스튜어트", "C.スチュワートJr.": "카터 스튜어트 주니어",
    "スチュワートJr.": "카터 스튜어트 주니어", "アンダーソン": "앤더슨", "ボー・タカハシ": "보 다카하시", "ボータカハシ": "보 다카하시"
}

# NPB 성씨 / 단독 이름 사전
NPB_FAMILY_NAME_MAP = {
    "戸郷": "토고", "東": "아즈마", "才木": "사이키", "今井": "이마이", "伊藤": "이토", "床田": "토코다",
    "髙橋": "다카하시", "高橋": "다카하시", "山崎": "야마사키", "山﨑": "야마사키", "小島": "코지마",
    "早川": "하야카와", "宮城": "미야기", "種市": "타네이치", "大瀬良": "오오세라", "森下": "모리시타",
    "菅野": "스가노", "隅田": "스미다", "高野": "타카노", "松本": "마츠모토", "井上": "이노우에",
    "深沢": "후카자와", "吉村": "요시무라", "金丸": "카네마루", "栗林": "쿠리바야시", "大野": "오오노",
    "西": "니시", "青柳": "아오야기", "大竹": "오오타케", "奥川": "오쿠가와", "有原": "아리하라",
    "武内": "타케우치", "平良": "타이라", "曽谷": "소타니", "九里": "쿠리", "上沢": "우와사와",
    "荘司": "쇼지", "毛利": "모리", "山野": "야마노", "石田": "이시다", "石田裕": "이시다 유타로",
    "豆田": "마메다", "佐藤": "사토", "佐藤隼": "사토 슌스케", "黒木": "쿠로키", "本田": "혼다",
    "水上": "미즈카미", "富山": "토미야마", "椋木": "무쿠노키", "阿部": "아베", "山田": "야마다",
    "石井": "이시이", "加藤": "카토", "加藤貴": "카토 타카유키", "岸": "키시", "堀": "호리",
    "堀田": "호타", "大西": "오오니시", "山岡": "야마오카", "岩嵜": "이와사키", "杉山": "스기야마",
    "柴田": "시바타", "森": "모리", "森博": "모리 히로토", "森脇": "모리와키", "片山": "카타야마",
    "益田": "마스다", "篠原": "시노하라", "若松": "와카마츠", "鈴木": "스즈키", "鈴木豪": "스즈키 고",
    "阪口": "사카구치", "齋藤": "사이토", "田中": "타나카", "田中瑛": "타나카 에이", "田嶋": "타지마",
    "田嶋大": "타지마 다이키", "小笠原": "오가사와라", "柳": "야나기", "達": "타츠 코타", "菅井": "스가이 신야",
    "髙島": "타카시마", "高島": "타카시마", "高野脩": "타카노 슈타", "大津": "오오츠", "和田": "와다",
    "小園": "코조노", "大貫": "오오누키", "前田": "마에다", "山口": "야마구치", "渡邉": "와타나베",
    "渡辺": "와타나베", "石川": "이시카와", "石川柊": "이시카와 슈타", "前田悠": "마에다 유고",
    "竹丸": "타케마루", "村上": "무라카미", "涌井": "와쿠이", "高梨": "타카나시", "尾形": "오가타",
    "梅津": "우메츠", "松葉": "마츠바", "根尾": "네오", "橋本": "하시모토", "清水": "시미즈",
    "藤浪": "후지나미", "金村": "카네무라", "北山": "키타야마", "藤井": "후지이", "松井": "마츠이",
    "上原": "우에하라", "山下": "야마시타", "東浜": "히가시하마"
}

# =============================================================
# ⚾ 2. Comprehensive First Names
# =============================================================
FIRST_NAMES = {
    "Aaron": "애런", "Adam": "아담", "Adrian": "에이드리언", "A.J.": "A.J.", "AJ": "AJ", "Alan": "앨런",
    "Albert": "앨버트", "Alec": "알렉", "Alejandro": "알레한드로", "Alex": "알렉스", "Andre": "안드레",
    "Andrew": "앤드루", "Anthony": "앤서니", "Aroldis": "아롤디스", "Austin": "오스틴", "Bailey": "베일리",
    "Ben": "벤", "Blake": "블레이크", "Bobby": "바비", "Bowden": "보든", "Brady": "브래디", "Brandon": "브랜든",
    "Braxton": "브랙스턴", "Brayan": "브라얀", "Brennan": "브레넌", "Brent": "브렌트", "Brenton": "브렌턴",
    "Brett": "브렛", "Brock": "브록", "Bryan": "브라이언", "Bryce": "브라이스", "Brycen": "브라이슨",
    "Bubba": "버바", "Cade": "케이드", "Caden": "케이든", "Cal": "칼", "Cam": "캠", "Carlos": "카를로스",
    "Carson": "카슨", "Casey": "케이시", "Cesar": "세사르", "César": "세사르", "Chad": "채드", "Charlie": "찰리",
    "Chase": "체이스", "Chris": "크리스", "Christian": "크리스천", "Christopher": "크리스토퍼", "Clarke": "클라크",
    "Clay": "클레이", "Clayton": "클레이튼", "Cody": "코디", "Cole": "콜", "Colin": "콜린", "Collin": "콜린",
    "Colt": "콜트", "Colton": "콜턴", "Connor": "코너", "Cooper": "쿠퍼", "Corbin": "코빈", "Corey": "코리",
    "Craig": "크레이그", "Cristian": "크리스티안", "Cristopher": "크리스토퍼", "Dakota": "다코타", "Dane": "데인",
    "Daniel": "대니얼", "Danny": "대니", "Darren": "대런", "David": "데이비드", "Davis": "데이비스", "Dean": "딘",
    "Derek": "데릭", "Devin": "데빈", "DL": "DL", "DJ": "DJ", "Drew": "드류", "Dustin": "더스틴", "Dylan": "딜런",
    "Edward": "에드워드", "Edwin": "에드윈", "Eli": "엘리", "Elieser": "엘리에세르", "Elly": "엘리", "Emilio": "에밀리오",
    "Emmanuel": "엠마누엘", "Emmet": "에멧", "Eric": "에릭", "Erick": "에릭", "Erik": "에릭", "Eury": "유리", "Evan": "에반",
    "Felix": "펠릭스", "Fernando": "페르난도", "Framber": "프람버", "Francisco": "프란시스코", "Frank": "프랭크",
    "Frankie": "프랭키", "Freddy": "프레디", "Freddie": "프레디", "Gabriel": "가브리엘", "Gage": "게이지",
    "Garrett": "개럿", "Gavin": "개빈", "George": "조지", "Gerrit": "게릿", "Gleyber": "글레이버", "Graham": "그레이엄",
    "Grant": "그랜트", "Grayson": "그레이슨", "Gregory": "그레고리", "Griffin": "그리핀", "Gunnar": "거너",
    "Hancel": "한셀", "Harrison": "해리슨", "Hayden": "헤이든", "Hector": "엑토르", "Hunter": "헌터",
    "Hurston": "허스턴", "Ian": "이안", "Jack": "잭", "Jackson": "잭슨", "Jacob": "제이콥", "Jake": "제이크",
    "James": "제임스", "Jameson": "제임슨", "Jared": "재러드", "Jarred": "재러드", "Jarren": "재런",
    "Jason": "제이슨", "Javier": "하비에르", "Jazz": "재즈", "Jeff": "제프", "Jeffrey": "제프리",
    "Jeremiah": "제레마이어", "Jeremy": "제레미", "Jesus": "헤수스", "Jesús": "헤수스", "Jhoan": "호안",
    "Joe": "조", "Joel": "조엘", "Joey": "조이", "John": "존", "Johnny": "조니", "Jon": "존",
    "Jonathan": "조나단", "Jordan": "조던", "Jose": "호세", "José": "호세", "Josh": "조시", "Joshua": "조슈아",
    "Josiah": "조사이어", "JP": "JP", "JT": "JT", "Juan": "후안", "Julian": "줄리안", "Julio": "훌리오",
    "Jurickson": "주릭슨", "Justin": "저스틴", "Keaton": "키튼", "Keider": "케이더", "Ken": "켄",
    "Ketel": "케텔", "Kevin": "케빈", "Kodai": "코다이", "Kumar": "쿠마", "Kutter": "커터", "Kyle": "카일",
    "Lance": "랜스", "Landen": "랜든", "Landon": "랜던", "Lane": "레인", "Lawrence": "로렌스", "Logan": "로건",
    "Lourdes": "루르데스", "Lucas": "루카스", "Luis": "루이스", "Luke": "루크", "Mackenzie": "맥켄지",
    "MacKenzie": "맥켄지", "Manny": "매니", "Marcell": "마르셀", "Marcus": "마커스", "Mark": "마크",
    "Martin": "마틴", "Martín": "마틴", "Mason": "메이슨", "Masataka": "마사타카", "Matt": "맷",
    "Matthew": "매튜", "Max": "맥스", "Merrill": "메릴", "Michael": "마이클", "Mick": "믹", "Mickey": "미키",
    "Miguel": "미겔", "Mike": "마이크", "Miles": "마일스", "Mitch": "미치", "Mitchell": "미첼", "Mookie": "무키",
    "Nathan": "네이선", "Nestor": "네스터", "Nick": "닉", "Nico": "니코", "Noah": "노아", "Nolan": "놀란",
    "Oneil": "오닐", "Osvaldo": "오스발도", "Pablo": "파블로", "Parker": "파커", "Patrick": "패트릭", "Paul": "폴",
    "Payton": "페이튼", "Peyton": "페이튼", "Pete": "피트", "Peter": "피터", "Pierce": "피어스", "Quinn": "퀸",
    "Rafael": "라파엘", "Randy": "랜디", "Ranger": "레인저", "Reese": "리스", "Reid": "리드", "Reiver": "레이버",
    "Reynaldo": "레이날도", "Rhett": "렛", "Rich": "리치", "Richie": "리치", "Ricky": "리키", "Riley": "라일리",
    "River": "리버", "Robbie": "로비", "Robert": "로버트", "Ron": "론", "Ronald": "로널드", "Ronel": "로넬",
    "Ross": "로스", "Rowdy": "라우디", "Ryan": "라이언", "Ryne": "라인", "Sal": "샐", "Sam": "샘", "Samuel": "새뮤얼",
    "Scott": "스콧", "Sean": "션", "Seiya": "세이야", "Seth": "세스", "Shane": "셰인", "Shawn": "숀",
    "Shea": "셰이", "Shohei": "쇼헤이", "Shota": "쇼타", "Simeon": "시미언", "Slade": "슬레이드", "Sonny": "소니",
    "Spencer": "스펜서", "Steven": "스티븐", "Taj": "타지", "Tanner": "태너", "Tarik": "타릭", "Taylor": "테일러",
    "Tejay": "티제이", "Teoscar": "테오스카", "Thomas": "토마스", "TJ": "TJ", "Tobias": "토비아스",
    "Tommy": "토미", "Tony": "토니", "Trea": "트레이", "Trent": "트렌트", "Trevor": "트레버", "Tristan": "트리스탄",
    "Triston": "트리스톤", "Troy": "트로이", "Ty": "타이", "Tyler": "타일러", "Tylor": "타일러", "Valente": "발렌테",
    "Victor": "빅터", "Vince": "빈스", "Vladimir": "블라디미르", "Wade": "웨이드", "Walbert": "왈버트", "Walker": "워커",
    "Wilber": "윌버", "Will": "윌", "William": "윌리엄", "Willy": "윌리", "Wyatt": "와이어트", "Xzavion": "즈자비온",
    "Yandy": "얀디", "Yariel": "야리엘", "Yency": "옌시", "Yimi": "이미", "Yordan": "요르단",
    "Yoshinobu": "요시노부", "Yu": "유", "Yunior": "유니오르", "Yusei": "유세이", "Zac": "잭",
    "Zach": "잭", "Zack": "잭", "Zebby": "제비"
}

# =============================================================
# ⚾ 3. Comprehensive Last Names
# =============================================================
LAST_NAMES = {
    "Abbott": "애벗", "Abrams": "에이브람스", "Abreu": "아브레우", "Acuna": "아쿠냐", "Acuña": "아쿠냐",
    "Adames": "아다메스", "Adams": "아담스", "Aguiar": "아기아르", "Alcantara": "알칸타라", "Alexander": "알렉산더",
    "Allen": "앨런", "Alonso": "알론소", "Altuve": "알투베", "Alvarado": "알바라도", "Alvarez": "알바레즈", "Álvarez": "알바레즈",
    "Alzólay": "알졸레이", "Amador": "아마도르", "Anderson": "앤더슨", "Antone": "앤톤", "Arenado": "아레나도",
    "Arias": "아리아스", "Armstrong": "암스트롱", "Arrighetti": "아리게티", "Arozarena": "아로자레나",
    "Ashby": "애슈비", "Ashcraft": "애슈크래프트", "Assad": "아사드", "Bader": "베이더", "Baez": "바에즈",
    "Báez": "바에즈", "Bailey": "베일리", "Baker": "베이커", "Baltz": "발츠", "Banda": "반다", "Barlow": "바를로",
    "Barnes": "반스", "Bassitt": "배싯", "Bautista": "바우티스타", "Baz": "바즈", "Bazan": "바잔",
    "Bednar": "베드나르", "Beeks": "빅스", "Bellinger": "벨린저", "Bello": "베요", "Bellozo": "벨로조",
    "Benintendi": "베닌텐디", "Berrios": "베리오스", "Berríos": "베리오스", "Berti": "베르티", "Betts": "베츠",
    "Bibee": "바이비", "Bichette": "비셋", "Bido": "비도", "Birdsong": "버드송", "Blach": "블라크",
    "Black": "블랙", "Blackburn": "블랙번", "Blalock": "블레이록", "Blanco": "블랑코", "Bleday": "블레데이",
    "Bogaerts": "보가츠", "Bohm": "봄", "Borucki": "보루키", "Boushley": "부슐리", "Boyd": "보이드",
    "Bradford": "브래드포드", "Bradish": "브래디시", "Bradley": "브래들리", "Brebbia": "브레비아",
    "Bregman": "브레그먼", "Brieske": "브리스키", "Brown": "브라운", "Bruihl": "브루일", "Bubic": "뷰빅",
    "Buehler": "뷸러", "Bundy": "번디", "Burger": "버거", "Burke": "버크", "Burleson": "벌레슨",
    "Burnes": "번스", "Burns": "번스", "Bush": "부시", "Busto": "부스토", "Butler": "버틀러",
    "Cabrera": "카브레라", "Cameron": "카메론", "Canning": "캐닝", "Cannon": "캐넌", "Cano": "카노", "Canha": "칸하",
    "Cantillo": "칸티요", "Caratini": "카라티니", "Carrasco": "카라스코", "Carroll": "캐롤",
    "Casas": "카사스", "Castellanos": "카스텔라노스", "Castillo": "카스티요", "Castro": "카스트로",
    "Cavalli": "카발리", "Cease": "시즈", "Chafin": "채핀", "Chandler": "챈들러", "Chapman": "채프먼",
    "Chavez": "차베스", "Chisholm": "치좀", "Chourio": "츄리오", "Civale": "시발레", "Clase": "클라세",
    "Cleavinger": "클레빈저", "Clevinger": "클레빈저", "Cole": "콜", "Coleman": "콜먼", "Contreras": "콘트레라스",
    "Cook": "쿡", "Corbin": "코빈", "Correa": "코레아", "Cortes": "코르테스", "Cortés": "코르테스",
    "Crawford": "크로포드", "Crochet": "크로셰", "Cronenworth": "크로넨워스", "Cruz": "크루즈", "Cueto": "쿠에토",
    "Curry": "커리", "Dana": "다나", "Darvish": "다르빗슈", "Davis": "데이비스", "De La Cruz": "데 라 크루즈",
    "deGrom": "디그롬", "DeGrom": "디그롬", "Detmers": "데트머스", "Devers": "디버스", "Diaz": "디아즈", "Díaz": "디아즈",
    "Dobnak": "도브낙", "Dotel": "도텔", "Doval": "도발", "Doyle": "도일", "Dreyer": "드레이어", "Duran": "두란",
    "Eflin": "에플린", "Elder": "엘더", "England": "잉글랜드", "Eovaldi": "이볼디", "Espada": "에스파다",
    "Estes": "에스테스", "Estevez": "에스테베즈", "Fairbanks": "페어뱅크스", "Falter": "폴터", "Fedde": "페디",
    "Feltner": "펠트너", "Ferguson": "퍼거슨", "Fernandez": "페르난데스", "Festa": "페스타", "Finnegan": "피네건",
    "Flaherty": "플래허티", "Fleming": "플레밍", "Flexen": "플렉센", "Florial": "플로리얼", "Foley": "폴리",
    "France": "프랑스", "Francis": "프랜시스", "Freeland": "프리랜드", "Freeman": "프리먼", "Frelick": "프렐릭",
    "Fried": "프리드", "Friedl": "프리들", "Fulmer": "풀머", "Gallen": "갤런", "Gantt": "간트",
    "Garcia": "가르시아", "García": "가르시아", "Garver": "가버", "Gastelum": "가스텔룸", "Gausman": "가우스먼",
    "Gentry": "젠트리", "Gibson": "깁슨", "Gilbert": "길버트", "Gil": "힐", "Gimenez": "히메네스", "Giménez": "히메네스",
    "Ginkel": "깅켈", "Ginn": "진", "Glasnow": "글래스나우", "Goldschmidt": "골드슈미트", "Gomber": "곰버",
    "Gonzalez": "곤잘레스", "González": "곤잘레스", "Gordon": "고든", "Gore": "고어", "Gorman": "고먼",
    "Graterol": "그라테롤", "Gray": "그레이", "Greene": "그린", "Grisham": "그리샴", "Grosjean": "그로스장",
    "Guenther": "귄터", "Guerrero": "게레로", "Gurriel": "구리엘", "Gusto": "구스토", "Hader": "헤이더",
    "Hall": "홀", "Halvorsen": "할보센", "Happ": "햅", "Harper": "하퍼", "Harris": "해리스", "Harrison": "해리슨",
    "Hartwig": "하트윅", "Harvey": "하비", "Hatcher": "해처", "Hauser": "하우저", "Hayes": "헤이즈",
    "Headrick": "헤드릭", "Heaney": "히니", "Held": "헬드", "Helsley": "헬슬리", "Henderson": "헨더슨",
    "Hendriks": "헨드릭스", "Hendricks": "헨드릭스", "Henriquez": "엔리케스", "Hernandez": "에르난데스",
    "Hernández": "에르난데스", "Herz": "헤르츠", "Hicks": "힉스", "Hill": "힐", "Hjerpe": "예르페",
    "Hoerner": "호너", "Hoffman": "호프먼", "Holderman": "홀더먼", "Holliday": "홀리데이", "Holmes": "홈즈",
    "Houck": "하우크", "Houser": "하우저", "Hudson": "허드슨", "Hughes": "휴즈", "Hurt": "허트",
    "Iglesias": "이글레시아스", "Imanaga": "이마나가", "India": "인디아", "Irvin": "어빈", "Jackson": "잭슨",
    "Jansen": "잰슨", "Javier": "하비에르", "Jefferies": "제프리스", "Jimenez": "히메네스", "Jobe": "조브",
    "Johnson": "존슨", "Jones": "존스", "Jordan": "조던", "Judge": "저지", "Jump": "점프", "Jung": "정",
    "Junis": "주니스", "Kay": "케이", "Keller": "켈러", "Kelly": "켈리", "Kershaw": "커쇼", "Kikuchi": "기쿠치",
    "Kim": "김", "Kimbrel": "킴브럴", "King": "킹", "Kirby": "커비", "Kirk": "커크", "Kittredge": "키트리지",
    "Knack": "낵", "Knebel": "크네블", "Knizner": "니즈너", "Kochanowicz": "코차노위츠", "Kopech": "코펙",
    "Kremer": "크레머", "Kuhnel": "쿠넬", "Kwan": "관", "Lambert": "램버트", "Langeliers": "랭겔리어스",
    "Lange": "랭", "Lauer": "라우어", "Lawrence": "로렌스", "Leahy": "리히", "Leiter": "라이터",
    "LeMahieu": "르메이휴", "Lewis": "루이스", "Liberatore": "리베라토레", "Lindor": "린도어", "Littell": "리텔",
    "Lively": "라이블리", "Lodolo": "로돌로", "Long": "롱", "Lopez": "로페즈", "López": "로페즈",
    "Lorenzen": "로렌젠", "Lowder": "라우더", "Lowe": "로우", "Lugo": "루고", "Luzardo": "루자르도",
    "Lynn": "린", "Machado": "마차도", "Maeda": "마에다", "Mahle": "말리", "Manaea": "마네아",
    "Marquez": "마르케스", "Marsh": "마쉬", "Marte": "마르테", "Martin": "마틴", "Martinez": "마르티네스",
    "Martínez": "마르티네스", "Maton": "메이튼", "Matos": "마토스", "Matthews": "매튜스", "Matz": "마츠",
    "Mautz": "마우츠", "May": "메이", "Mays": "메이스", "McCarthy": "매카시", "McCaughan": "맥코건",
    "McClanahan": "맥클라나한", "McCullers": "맥컬러스", "McGough": "맥거프", "McGreevy": "맥그리비",
    "McLean": "맥클레인", "McMahon": "맥맨", "Megill": "메길", "Melton": "멜튼", "Menechino": "메네키노",
    "Merrill": "메릴", "Messick": "메식", "Meyer": "마이어", "Mey": "메이", "Mikolas": "마이콜라스",
    "Miller": "밀러", "Minter": "민터", "Misiewicz": "미시에비츠", "Misiorowski": "미시오로우스키",
    "Molina": "몰리나", "Moll": "몰", "Moncada": "몬카다", "Montas": "몬타스", "Montero": "몬테로",
    "Montgomery": "몽고메리", "Moore": "무어", "Morejon": "모레혼", "Morel": "모렐", "Moreno": "모레노",
    "Morgan": "모건", "Morris": "모리스", "Morton": "모튼", "Muncy": "먼시", "Munoz": "무뇨스",
    "Muñoz": "무뇨스", "Murphy": "머피", "Musgrove": "머스그로브", "Myers": "마이어스", "Nardi": "나르디",
    "Nastrini": "나스트리니", "Naylor": "네일러", "Nelson": "넬슨", "Neris": "네리스", "Nevin": "네빈",
    "Nimmala": "니말라", "Nimmo": "니모", "Noda": "노다", "Nola": "놀라", "Ober": "오버",
    "O'Brien": "오브라이언", "O'Hoppe": "오호피", "Ohtani": "오타니", "Oller": "올러", "Olson": "올슨",
    "Ortiz": "오르티스", "Ottavino": "오타비노", "Outman": "아웃맨", "Ozuna": "오주나", "Paddack": "패댁",
    "Pagan": "파간", "Pagán": "파간", "Painter": "페인터", "Pallante": "팔란테", "Paredes": "파레데스",
    "Parker": "파커", "Pavin": "파빈", "Pena": "페냐", "Peña": "페냐", "Pepiot": "페피오",
    "Peralta": "페랄타", "Perdomo": "페르도모", "Perez": "페레즈", "Pérez": "페레즈", "Peterson": "피터슨",
    "Pfaadt": "팟", "Pham": "팜", "Phillips": "필립스", "Pinckney": "핑크니", "Pivetta": "피베타",
    "Poche": "포셰", "Polanco": "폴랑코", "Pressly": "프레슬리", "Prielipp": "프릴립", "Prieto": "프리에토",
    "Profar": "프로파", "Quantrill": "콴트릴", "Quinn": "퀸", "Quintana": "킨타나", "Rafaela": "라파엘라",
    "Ragans": "레이건스", "Raleigh": "랄리", "Ramirez": "라미레즈", "Ramírez": "라미레즈", "Ramos": "라모스",
    "Rangel": "란겔", "Rasmussen": "라스무센", "Ray": "레이", "Raysor": "레이서", "Rea": "레이",
    "Realmuto": "리얼무토", "Reed": "리드", "Rendon": "렌던", "Reynolds": "레이놀즈", "Richardson": "리차드슨",
    "Rincon": "린콘", "Rincón": "린콘", "Rivas": "리바스", "Rivera": "리베라", "Robertson": "로버트슨",
    "Robles": "로블레스", "Rocker": "로커", "Rodgers": "로저스", "Rodriguez": "로드리게스", "Rodríguez": "로드리게스",
    "Rodon": "로돈", "Rodón": "로돈", "Rogers": "로저스", "Rojas": "로하스", "Romero": "로메로",
    "Rooker": "루커", "Rosario": "로사리오", "Roupp": "룹", "Routzahn": "라우트잔", "Roxby": "록스비",
    "Ruiz": "루이즈", "Rutschman": "러치맨", "Ryan": "라이언", "Sale": "세일", "Sanchez": "산체스",
    "Sánchez": "산체스", "Sanmartin": "산마르틴", "Sanmartín": "산마르틴", "Santana": "산타나",
    "Santander": "산탄데르", "Santos": "산토스", "Scherzer": "슈어저", "Schlittler": "슐리틀러",
    "Schmidt": "슈미트", "Schneider": "슈나이더", "Scholtens": "숄텐스", "Schreiber": "슈라이버",
    "Schwarber": "슈와버", "Schwellenbach": "슈웰렌바크", "Scott": "스콧", "Seager": "시거",
    "Sears": "시어스", "Semien": "세미엔", "Senga": "센가", "Severino": "세베리노", "Seymour": "시모어",
    "Shaw": "쇼", "Sheehan": "시한", "Singer": "싱어", "Siri": "시리", "Skenes": "스킨스", "Skubal": "스쿠발",
    "Smeltzer": "스멜처", "Smith": "스미스", "Smith-Shawver": "스미스-쇼버", "Snell": "스넬", "Snider": "스나이더",
    "Solano": "솔라노", "Soriano": "소리아노", "Soto": "소토", "Speier": "스파이어", "Spence": "스펜스",
    "Springer": "스프링어", "Springs": "스프링스", "Stanek": "스타넥", "Stanton": "스탠튼", "Steele": "스틸",
    "Steer": "스티어", "Stephenson": "스티븐슨", "Stone": "스톤", "Stowers": "스타워즈", "Strahm": "스트람",
    "Strider": "스트라이더", "Stroman": "스트로먼", "Suarez": "수아레즈", "Suárez": "수아레즈", "Suzuki": "스즈키",
    "Swanson": "스완슨", "Taillon": "타이욘", "Tatis": "타티스", "Taylor": "테일러", "Tepera": "테페라",
    "Thomas": "토마스", "Thompson": "톰슨", "Thornton": "손튼", "Tolle": "톨레", "Torkelson": "토켈슨",
    "Torres": "토레스", "Tovar": "토바", "Treinen": "트레이넨", "Tucker": "터커", "Turang": "투랑",
    "Turner": "터너", "Ulloa": "우요아", "Urena": "우레냐", "Ureña": "우레냐", "Urquidy": "우르키디",
    "Valdez": "발데스", "Varland": "발랜드", "Vargas": "바르가스", "Varsho": "바쇼", "Vasquez": "바스케스",
    "Vaughn": "본", "Vesia": "베시아", "Vest": "베스트", "Vieira": "비에이라", "Vientos": "비엔토스",
    "Volpe": "볼피", "Wacha": "와카", "Waldichuk": "왈디척", "Waldrep": "왈드렙", "Waldron": "월드론",
    "Walker": "워커", "Walston": "월스턴", "Ward": "워드", "Warren": "워렌", "Webb": "웹",
    "Weissert": "와이서트", "Wells": "웰스", "Wentz": "웬츠", "Wesneski": "웨스네스키", "Wheeler": "휠러",
    "White": "화이트", "Whitlock": "윗록", "Wicks": "윅스", "Wilkerson": "윌커슨", "Wilkinson": "윌킨슨",
    "Williams": "윌리엄스", "Wilson": "윌슨", "Winder": "윈더", "Winn": "윈", "Winquest": "윈퀘스트",
    "Witt": "위트", "Wood": "우드", "Woodruff": "우드러프", "Woods": "우즈", "Woo": "우",
    "Wrobleski": "로블레스키", "Yarbrough": "야브로", "Yastrzemski": "야스트렘스키", "Yates": "예이츠",
    "Yoshida": "요시다", "Young": "영", "Zamora": "자모라", "Zavala": "자발라", "Zimmermann": "짐머만",
    "Zuniga": "주니가"
}

PROTECTED_TERMS = {
    'LG', 'SSG', 'NC', 'KT', 'KIA', 'DeNA', 'PSG', 'FC', 'AC', 'AS', 'CF', 'RB',
    'LA', 'NY', 'SF', 'SD', 'TB', 'KC', 'CWS', 'CHC', 'MIA', 'BAL', 'BOS', 'HOU', 'WSH', 'OAK', 'DET', 'MIN', 'CLE', 'TEX', 'SEA', 'LAA', 'LAD', 'COL', 'ARI', 'STL', 'MIL', 'PIT', 'CIN', 'PHI', 'NYM', 'ATL', 'TOR',
    'ERA', 'WHIP', 'OPS', 'AVG', 'OBP', 'SLG', 'RPG', 'GAPG', 'PPG', 'PAPG', 'TOTAL', 'LIVE',
    'MLB', 'NPB', 'KBO', 'EPL', 'NBA', 'KBL', 'WKBL', 'KOVO', 'UCL', 'UEL',
    'OFFICIAL', 'SCHEDULED', 'FINISHED', 'VS', 'HOME', 'AWAY', 'H2H',
    'WAR', 'FIP', 'BABIP', 'QS', 'LOB', 'ISO', 'TBD', 'K', 'BB', 'SO', 'HR', 'RBI', 'IP', 'ER', 'NP'
}

def translate_player_name(raw: str) -> str:
    if not raw: return ""
    raw = sanitize_player_name(raw)
    if not raw: return ""
    
    suffix = ""
    if raw.endswith('(R)') or raw.endswith('(우)'):
        suffix = ' (우)'
        raw = re.sub(r'\(R\)|\(우\)', '', raw).strip()
    elif raw.endswith('(L)') or raw.endswith('(좌)'):
        suffix = ' (좌)'
        raw = re.sub(r'\(L\)|\(좌\)', '', raw).strip()
    elif raw.endswith('(언)'):
        suffix = ' (언)'
        raw = re.sub(r'\(언\)', '', raw).strip()

    # Protected team acronym or stat abbreviation?
    if raw.upper() in PROTECTED_TERMS or re.match(r'^[A-Z0-9_-]{1,5}$', raw):
        return raw + suffix
    
    # 1. Check Full Dictionary (MLB + NPB)
    if raw in FULL_NAMES:
        return FULL_NAMES[raw] + suffix
    
    # 2. Check Unspaced Kanji / Japanese characters
    no_space = raw.replace(" ", "").replace("　", "")
    if no_space in FULL_NAMES:
        return FULL_NAMES[no_space] + suffix
    
    # 3. Check NPB Family Names
    if raw in NPB_FAMILY_NAME_MAP:
        return NPB_FAMILY_NAME_MAP[raw] + suffix
    if no_space in NPB_FAMILY_NAME_MAP:
        return NPB_FAMILY_NAME_MAP[no_space] + suffix
    for fam, fam_ko in NPB_FAMILY_NAME_MAP.items():
        if raw.startswith(fam) and len(raw) > len(fam):
            rem = raw[len(fam):].strip()
            rem_ko = NPB_FAMILY_NAME_MAP.get(rem, rem)
            return f"{fam_ko} {rem_ko}".strip() + suffix
        if no_space.startswith(fam) and len(no_space) > len(fam):
            rem = no_space[len(fam):].strip()
            rem_ko = NPB_FAMILY_NAME_MAP.get(rem, rem)
            return f"{fam_ko} {rem_ko}".strip() + suffix

    # Already Korean?
    if re.search(r'^[가-힣\s\d._\-()]+$', raw):
        return raw + suffix
    
    # Handle Jr., Sr., II, III, IV suffix
    jr_suffix = ""
    parts = raw.split()
    if len(parts) >= 2 and parts[-1].rstrip('.').upper() in ('JR', 'SR', 'II', 'III', 'IV'):
        jr_suffix = " " + parts[-1]
        parts = parts[:-1]
        raw = " ".join(parts)

    if raw in FULL_NAMES:
        return FULL_NAMES[raw] + jr_suffix + suffix
    if raw in LAST_NAMES:
        return LAST_NAMES[raw] + jr_suffix + suffix
    if raw in FIRST_NAMES:
        return FIRST_NAMES[raw] + jr_suffix + suffix
    
    # De / La / Del compound last names e.g. Elly De La Cruz, Jacob deGrom
    if len(parts) > 2:
        first_candidate = parts[0]
        last_candidate = " ".join(parts[1:])
        if last_candidate in LAST_NAMES:
            first_ko = FIRST_NAMES.get(first_candidate) or FIRST_NAMES.get(first_candidate.capitalize()) or rule_transliterate_word(first_candidate)
            return f"{first_ko} {LAST_NAMES[last_candidate]}".strip() + jr_suffix + suffix
    
    if len(parts) == 1:
        p0 = parts[0]
        if p0.upper() in PROTECTED_TERMS or re.match(r'^[A-Z0-9_-]{1,5}$', p0):
            return p0 + jr_suffix + suffix
        cap = p0.capitalize()
        single = FIRST_NAMES.get(p0) or FIRST_NAMES.get(cap) or LAST_NAMES.get(p0) or LAST_NAMES.get(cap) or rule_transliterate_word(p0)
        return single + jr_suffix + suffix
    
    first = parts[0]
    last = " ".join(parts[1:])
    
    first_ko = FIRST_NAMES.get(first) or FIRST_NAMES.get(first.capitalize()) or rule_transliterate_word(first)
    last_ko = LAST_NAMES.get(last) or LAST_NAMES.get(last.capitalize()) or LAST_NAMES.get(last.title())
    
    if not last_ko:
        last_parts = []
        for p in parts[1:]:
            p_cap = p.capitalize()
            p_ko = LAST_NAMES.get(p) or LAST_NAMES.get(p_cap) or FIRST_NAMES.get(p) or FIRST_NAMES.get(p_cap) or rule_transliterate_word(p)
            last_parts.append(p_ko)
        last_ko = " ".join(last_parts)
        
    return f"{first_ko} {last_ko}".strip() + jr_suffix + suffix

def rule_transliterate_word(word: str) -> str:
    """Robust phoneme-based English/Foreign to Korean transliteration."""
    if not word: return ''
    if word.lower() in ('n/a', 'na', 'none', 'null', 'undefined', 'tbd', 'tba'):
        return ''
    if word.upper() in PROTECTED_TERMS or (len(word) <= 5 and not re.search(r'[aeiouyAEIOUY]', word)):
        return word
    clean = unicodedata.normalize('NFKD', word)
    clean = ''.join(ch for ch in clean if not unicodedata.combining(ch)).strip()
    
    # Common whole-word or special root lookups
    special_roots = {
        'clay': '클레이', 'gage': '게이지', 'jump': '점프', 'hughes': '휴즈',
        'tolle': '톨레', 'schlittler': '슐리틀러', 'chandler': '챈들러',
        'prielipp': '프릴립', 'dotel': '도텔', 'ulloa': '우요아', 'urena': '우레냐',
        'lambert': '램버트', 'cameron': '카메론', 'mahle': '말리', 'jobe': '조브',
        'bubba': '버바', 'eury': '유리', 'zac': '잭', 'dobnak': '도브낙',
        'seymour': '시모어', 'leahy': '리히', 'degrom': '디그롬', 'scherzer': '슈어저',
        'pfaadt': '팟', 'rocker': '로커', 'bibee': '바이비', 'crochet': '크로셰',
        'chourio': '츄리오', 'profar': '프로파', 'tatis': '타티스', 'bohm': '봄',
        'skubal': '스쿠발', 'skenes': '스킨스', 'sale': '세일', 'strider': '스트라이더',
        'glasnow': '글래스나우', 'snell': '스넬', 'burnes': '번스', 'ragans': '레이건스',
        'cease': '시즈', 'lugo': '루고', 'wesneski': '웨스네스키', 'painter': '페인터',
        'gordon': '고든', 'bradish': '브래디시', 'messick': '메식', 'gusto': '구스토'
    }
    if clean.lower() in special_roots:
        return special_roots[clean.lower()]

    w = clean.lower()
    
    # Syllable endings
    w = re.sub(r'tion$', '션', w)
    w = re.sub(r'sion$', '션', w)
    w = re.sub(r'son$', '슨', w)
    w = re.sub(r'sen$', '센', w)
    w = re.sub(r'ton$', '턴', w)
    w = re.sub(r'man$', '맨', w)
    w = re.sub(r'kin$', '킨', w)
    w = re.sub(r'lin$', '린', w)
    w = re.sub(r'tin$', '틴', w)
    w = re.sub(r'rin$', '린', w)
    w = re.sub(r'win$', '윈', w)
    w = re.sub(r'ley$', '리', w)
    w = re.sub(r'ly$', '리', w)
    w = re.sub(r'quest$', '퀘스트', w)
    w = re.sub(r'field$', '필드', w)
    w = re.sub(r'ford$', '포드', w)
    w = re.sub(r'wood$', '우드', w)
    w = re.sub(r'berg$', '베르크', w)
    w = re.sub(r'burg$', '버그', w)

    # Phoneme replacements (ordered from longer to shorter)
    replacements = [
        ('sch', '슈'), ('chr', '크리'), ('ph', '프'), ('th', '트'),
        ('sh', '시'), ('ch', '치'), ('qu', '퀴'), ('wh', '화'), ('ck', '크'),
        ('ee', '이'), ('oo', '우'), ('ea', '이'), ('ou', '아우'),
        ('ai', '에이'), ('ay', '에이'), ('oi', '오이'), ('oy', '오이'),
        ('au', '오'), ('aw', '오'), ('oa', '오'),
        ('ar', '아르'), ('er', '에르'), ('ir', '이르'), ('or', '오르'), ('ur', '우르'),
        ('al', '알'), ('el', '엘'), ('il', '일'), ('ol', '올'), ('ul', '울'),
        ('an', '안'), ('en', '엔'), ('in', '인'), ('on', '온'), ('un', '운'),
        ('am', '암'), ('em', '엠'), ('im', '임'), ('om', '옴'), ('um', '움'),
        ('ba', '바'), ('be', '베'), ('bi', '비'), ('bo', '보'), ('bu', '부'), ('by', '바이'),
        ('ca', '카'), ('ce', '세'), ('ci', '시'), ('co', '코'), ('cu', '쿠'), ('cy', '사이'),
        ('da', '다'), ('de', '데'), ('di', '디'), ('do', '도'), ('du', '두'), ('dy', '디'),
        ('fa', '파'), ('fe', '페'), ('fi', '피'), ('fo', '포'), ('fu', '푸'), ('fy', '파이'),
        ('ga', '가'), ('ge', '제'), ('gi', '지'), ('go', '고'), ('gu', '구'), ('gy', '지'),
        ('ha', '하'), ('he', '헤'), ('hi', '히'), ('ho', '호'), ('hu', '후'), ('hy', '하이'),
        ('ja', '자'), ('je', '제'), ('ji', '지'), ('jo', '조'), ('ju', '주'), ('jy', '자이'),
        ('ka', '카'), ('ke', '케'), ('ki', '키'), ('ko', '코'), ('ku', '쿠'), ('ky', '키'),
        ('la', '라'), ('le', '레'), ('li', '리'), ('lo', '로'), ('lu', '루'), ('ly', '리'),
        ('ma', '마'), ('me', '메'), ('mi', '미'), ('mo', '모'), ('mu', '무'), ('my', '마이'),
        ('na', '나'), ('ne', '네'), ('ni', '니'), ('no', '노'), ('nu', '누'), ('ny', '니'),
        ('pa', '파'), ('pe', '페'), ('pi', '피'), ('po', '포'), ('pu', '푸'), ('py', '파이'),
        ('ra', '라'), ('re', '레'), ('ri', '리'), ('ro', '로'), ('ru', '루'), ('ry', '리'),
        ('sa', '사'), ('se', '세'), ('si', '시'), ('so', '소'), ('su', '수'), ('sy', '사이'),
        ('ta', '타'), ('te', '테'), ('ti', '티'), ('to', '토'), ('tu', '투'), ('ty', '티'),
        ('va', '바'), ('ve', '베'), ('vi', '비'), ('vo', '보'), ('vu', '부'), ('vy', '바이'),
        ('wa', '와'), ('we', '웨'), ('wi', '위'), ('wo', '워'), ('wu', '우'),
        ('ya', '야'), ('ye', '예'), ('yi', '이'), ('yo', '요'), ('yu', '유'),
        ('za', '자'), ('ze', '제'), ('zi', '지'), ('zo', '조'), ('zu', '주'),
        ('a', '아'), ('e', '에'), ('i', '이'), ('o', '오'), ('u', '우'),
        ('b', '브'), ('c', '크'), ('d', '드'), ('f', '프'), ('g', '그'),
        ('h', '흐'), ('j', '즈'), ('k', '크'), ('l', '르'), ('m', '므'),
        ('n', '느'), ('p', '프'), ('r', '르'), ('s', '스'), ('t', '트'),
        ('v', '브'), ('w', '우'), ('x', '크스'), ('y', '이'), ('z', '즈')
    ]
    for eng, kor in replacements:
        w = w.replace(eng, kor)
    w = re.sub(r'[^가-힣]', '', w)
    return w or word

FIRST_NAMES_KO = FIRST_NAMES
LAST_NAMES_KO = LAST_NAMES
PLAYER_KOREAN_NAMES = FULL_NAMES
