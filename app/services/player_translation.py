import sys, re, unicodedata, html
sys.stdout.reconfigure(encoding='utf-8')

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


# Comprehensive First Name Dict
FIRST_NAMES = {
    "Aaron": "애런", "Adam": "아담", "Adrian": "에이드리언", "A.J.": "A.J.", "AJ": "AJ", 
    "Alan": "앨런", "Albert": "앨버트", "Alec": "알렉", "Alejandro": "알레한드로", "Alex": "알렉스", 
    "Andre": "안드레", "Andrew": "앤드루", "Anthony": "앤서니", "Aroldis": "아롤디스", "Austin": "오스틴", 
    "Bailey": "베일리", "Ben": "벤", "Blake": "블레이크", "Bobby": "바비", "Brady": "브래디", 
    "Brandon": "브랜든", "Braxton": "브랙스턴", "Brayan": "브라얀", "Brennan": "브레넌", "Brent": "브렌트", 
    "Brenton": "브렌턴", "Brett": "브렛", "Brock": "브록", "Bryce": "브라이스", "Brycen": "브라이슨", 
    "Bryan": "브라이언", "Cade": "케이드", "Cal": "칼", "Carlos": "카를로스", "Carson": "카슨", 
    "Casey": "케이시", "Cesar": "세사르", "César": "세사르", "Chad": "채드", "Chase": "체이스", 
    "Chris": "크리스", "Christian": "크리스천", "Clayton": "클레이튼", "Cody": "코디", "Cole": "콜", 
    "Colin": "콜린", "Collin": "콜린", "Colt": "콜트", "Colton": "콜턴", "Connor": "코너", 
    "Cooper": "쿠퍼", "Corbin": "코빈", "Corey": "코리", "Craig": "크레이그", "Cristian": "크리스티안", 
    "Dakota": "다코타", "Dane": "데인", "Daniel": "대니얼", "Danny": "대니", "David": "데이비드", 
    "Davis": "데이비스", "Dean": "딘", "Derek": "데릭", "Devin": "데빈", "De": "데", "Del": "델", "Drew": "드류", 
    "Dustin": "더스틴", "Dylan": "딜런", "Edward": "에드워드", "Edwin": "에드윈", "Eli": "엘리", 
    "Elieser": "엘리에세르", "Emilio": "에밀리오", "Emmanuel": "엠마누엘", "Emmet": "에멧", "Eric": "에릭", 
    "Erik": "에릭", "Evan": "에반", "Felix": "펠릭스", "Fernando": "페르난도", "Framber": "프람버", 
    "Francisco": "프란시스코", "Frank": "프랭크", "Frankie": "프랭키", "Freddy": "프레디", "Freddie": "프레디", 
    "Gabriel": "가브리엘", "Garrett": "개럿", "George": "조지", "Gerrit": "게릿", "Graham": "그레이엄", 
    "Grant": "그랜트", "Grayson": "그레이슨", "Gregory": "그레고리", "Griffin": "그리핀", "Gunnar": "거너", 
    "Hancel": "한셀", "Harrison": "해리슨", "Hayden": "헤이든", "Hector": "엑토르", "Hunter": "헌터", 
    "Ian": "이안", "Jack": "잭", "Jackson": "잭슨", "Jacob": "제이콥", "Jake": "제이크", 
    "James": "제임스", "Jameson": "제임슨", "Jared": "재러드", "Jarred": "재러드", "Jason": "제이슨", 
    "Javier": "하비에르", "Jeff": "제프", "Jeffrey": "제프리", "Jeremiah": "제레마이어", "Jeremy": "제레미", 
    "Jesus": "헤수스", "Jesús": "헤수스", "Jhoan": "호안", "Joe": "조", "Joel": "조엘", 
    "John": "존", "Johnny": "조니", "Jon": "존", "Jonathan": "조나단", "Jordan": "조던", 
    "Jose": "호세", "José": "호세", "Josh": "조시", "Joshua": "조슈아", "Josiah": "조사이어", 
    "Juan": "후안", "Julian": "줄리안", "Julio": "훌리오", "Justin": "저스틴", "Keaton": "키튼", 
    "Ken": "켄", "Kevin": "케빈", "Kyle": "카일", "Lance": "랜스", "Lane": "레인", 
    "La": "라", "Le": "르", "Logan": "로건", "Lucas": "루카스", "Luis": "루이스", "Luke": "루크", "Mackenzie": "맥켄지", 
    "MacKenzie": "맥켄지", "Manny": "매니", "Marcus": "마커스", "Mark": "마크", "Mason": "메이슨", 
    "Matt": "맷", "Matthew": "매튜", "Max": "맥스", "Michael": "마이클", "Mick": "믹", 
    "Mickey": "미키", "Mike": "마이크", "Miles": "마일스", "Mitch": "미치", "Mitchell": "미첼", 
    "Mookie": "무키", "Nathan": "네이선", "Nestor": "네스터", "Nick": "닉", "Nico": "니코", 
    "Noah": "노아", "Oneil": "오닐", "O'Neil": "오닐", "O'Neill": "오닐", "Adley": "애들리", "Elly": "엘리", "Ketel": "케텔", "Teoscar": "테오스카", "Marcell": "마르셀", "Jurickson": "주릭슨", "Gleyber": "글레이버", "Pablo": "파블로", "Patrick": "패트릭", "Paul": "폴", "Pete": "피트", 
    "Peter": "피터", "Pierce": "피어스", "Quinn": "퀸", "Rafael": "라파엘", "Ranger": "레인저", 
    "Randy": "랜디", "Reese": "리스", "Reid": "리드", "Reiver": "레이버", "Reynaldo": "레이날도", 
    "Rhett": "렛", "Rich": "리치", "Richie": "리치", "Ricky": "리키", "Riley": "라일리", 
    "River": "리버", "Robert": "로버트", "Roansy": "로안시", "Roddery": "로더리", "Ron": "론", 
    "Ronald": "로널드", "Ross": "로스", "Rowdy": "라우디", "Ryan": "라이언", "Ryne": "라인", 
    "Sam": "샘", "Samuel": "새뮤얼", "Scott": "스콧", "Sean": "션", "Seth": "세스", 
    "Shane": "셰인", "Shawn": "숀", "Shota": "쇼타", "Silvino": "실비노", "Simeon": "시미언", 
    "Slade": "슬레이드", "Sonny": "소니", "Spencer": "스펜서", "Steven": "스티븐", "Taj": "타지", 
    "Tanner": "태너", "Tarik": "타릭", "Taylor": "테일러", "Tejay": "티제이", "Thomas": "토마스", 
    "Tommy": "토미", "Tony": "토니", "Triston": "트리스톤", "Tristan": "트리스탄", "Trevor": "트레버", 
    "Trent": "트렌트", "Tyler": "타일러", "Tylor": "타일러", "Victor": "빅터", "Vince": "빈스", 
    "Vladimir": "블라디미르", "Wade": "웨이드", "Walker": "워커", "Will": "윌", "William": "윌리엄", 
    "Wyatt": "와이어트", "Yency": "옌시", "Yimi": "이미", "Yariel": "야리엘", "Yordan": "요르단", 
    "Yusei": "유세이", "Yunior": "유니오르", "Zach": "잭", "Zack": "잭", "Zac": "잭"
}

# Comprehensive Last Name Dict
LAST_NAMES = {
    "Abbott": "애벗", "Abreu": "아브레우", "Acuna": "아쿠냐", "Acuña": "아쿠냐", "Adames": "아다메스", 
    "Adams": "아담스", "Alcantara": "알칸타라", "Alexander": "알렉산더", "Allen": "앨런", "Alonso": "알론소", 
    "Altuve": "알투베", "Alvarado": "알바라도", "Alvarez": "알바레즈", "Alzólay": "알졸레이", "Amador": "아마도르", 
    "Anderson": "앤더슨", "Antone": "앤톤", "Arenado": "아레나도", "Arias": "아리아스", "Armstrong": "암스트롱", 
    "Ashby": "애슈비", "Ashcraft": "애슈크래프트", "Assad": "아사드", "Bader": "베이더", "Baez": "바에즈", 
    "Báez": "바에즈", "Bailey": "베일리", "Baker": "베이커", "Baltz": "발츠", "Banda": "반다", 
    "Barlow": "바를로", "Barnes": "반스", "Bassitt": "배싯", "Bautista": "바우티스타", "Bazan": "바잔", 
    "Beeks": "빅스", "Bellinger": "벨린저", "Benintendi": "베닌텐디", "Berti": "베르티", "Betts": "베츠", 
    "Bichette": "비셋", "Bido": "비도", "Blackburn": "블랙번", "Bogaerts": "보가츠", "Bohm": "봄", 
    "Borucki": "보루키", "Boushley": "부슐리", "Boyd": "보이드", "Bradley": "브래들리", "Bradish": "브래디시", 
    "Brebbia": "브레비아", "Bregman": "브레그먼", "Brieske": "브리스키", "Brown": "브라운", "Bruihl": "브루일", 
    "Bubic": "뷰빅", "Buehler": "뷸러", "Bundy": "번디", "Burke": "버크", "Burnes": "번스", 
    "Burns": "번스", "Bush": "부시", "Busto": "부스토", "Cabrera": "카브레라", "Canning": "캐닝", 
    "Cano": "카노", "Canha": "칸하", "Cantillo": "칸티요", "Caratini": "카라티니", "Carrasco": "카라스코", 
    "Castellanos": "카스텔라노스", "Castillo": "카스티요", "Castro": "카스트로", "Cease": "시즈", "Chafin": "채핀", 
    "Chapman": "채프먼", "Chavez": "차베스", "Chisholm": "치좀", "Civale": "시발레", "Clase": "클라세", 
    "Cleavinger": "클레빈저", "Clevinger": "클레빈저", "Cole": "콜", "Coleman": "콜먼", "Contreras": "콘트레라스", 
    "Cook": "쿡", "Correa": "코레아", "Cortes": "코르테스", "Cortés": "코르테스", "Crawford": "크로포드", 
    "Crochet": "크로셰", "Cronenworth": "크로넨워스", "Cruz": "크루즈", "Cueto": "쿠에토", "Darvish": "다르빗슈", 
    "Davis": "데이비스", "De La Cruz": "데 라 크루즈", "Devers": "디버스", "Diaz": "디아즈", "Díaz": "디아즈", 
    "Doval": "도발", "Dreyer": "드레이어", "Eflin": "에플린", "Elder": "엘더", "England": "잉글랜드", 
    "Eovaldi": "이볼디", "Espada": "에스파다", "Estevez": "에스테베즈", "Fairbanks": "페어뱅크스", "Fedde": "페디", 
    "Feltner": "펠트너", "Ferguson": "퍼거슨", "Fernandez": "페르난데스", "Finnegan": "피네건", "Flaherty": "플래허티", 
    "Fleming": "플레밍", "Florial": "플로리얼", "Foley": "폴리", "France": "프랑스", "Freeland": "프리랜드", 
    "Freeman": "프리먼", "Fried": "프리드", "Fulmer": "풀머", "Gallen": "갤런", "Gantt": "간트", 
    "Garcia": "가르시아", "García": "가르시아", "Garver": "가버", "Gastelum": "가스텔룸", "Gausman": "가우스먼", 
    "Gentry": "젠트리", "Gibson": "깁슨", "Gilbert": "길버트", "Gimenez": "히메네스", "Giménez": "히메네스", 
    "Ginkel": "깅켈", "Glasnow": "글래스나우", "Goldschmidt": "골드슈미트", "Gomber": "곰버", "Gonzalez": "곤잘레스", 
    "González": "곤잘레스", "Gordon": "고든", "Gore": "고어", "Gorman": "고먼", "Gray": "그레이", 
    "Greene": "그린", "Grosjean": "그로스장", "Grisham": "그리샴", "Guenther": "귄터", "Guerrero": "게레로", 
    "Gurriel": "구리엘", "Hader": "헤이더", "Halvorsen": "할보센", "Happ": "햅", "Harris": "해리스", 
    "Harrison": "해리슨", "Hartwig": "하트윅", "Harvey": "하비", "Hatcher": "해처", "Hauser": "하우저", 
    "Headrick": "헤드릭", "Heaney": "히니", "Held": "헬드", "Helsley": "헬슬리", "Hendriks": "헨드릭스", 
    "Henriquez": "엔리케스", "Hernandez": "에르난데스", "Hernández": "에르난데스", "Hicks": "힉스", "Hill": "힐", 
    "Hjerpe": "예르페", "Hoerner": "호너", "Hoffman": "호프먼", "Holderman": "홀더먼", "Holliday": "홀리데이", 
    "Holmes": "홈즈", "Houck": "하우크", "Houser": "하우저", "Hurt": "허트", "Iglesias": "이글레시아스", 
    "Imanaga": "이마나가", "India": "인디아", "Irvin": "어빈", "Jackson": "잭슨", "Jansen": "잰슨", 
    "Javier": "하비에르", "Jefferies": "제프리스", "Jimenez": "히메네스", "Johnson": "존슨", "Jones": "존스", 
    "Jordan": "조던", "Judge": "저지", "Jung": "정", "Junis": "주니스", "Keller": "켈러", 
    "Kelly": "켈리", "Kershaw": "커쇼", "Kim": "김", "Kimbrel": "킴브럴", "King": "킹", 
    "Kirby": "커비", "Kirk": "커크", "Kittredge": "키트리지", "Knebel": "크네블", "Knizner": "니즈너", 
    "Kopech": "코펙", "Kuhnel": "쿠넬", "Lange": "랭", "Lauer": "라우어", "Lawrence": "로렌스", "Leahy": "리히", 
    "Leiter": "라이터", "LeMahieu": "르메이휴", "Lewis": "루이스", "Liberatore": "리베라토레", "Lindor": "린도어", 
    "Littell": "리텔", "Lodolo": "로돌로", "Long": "롱", "Lopez": "로페즈", "López": "로페즈", 
    "Lorenzen": "로렌젠", "Lowe": "로우", "Lowder": "라우더", "Lugo": "루고", "Luzardo": "루자르도", 
    "Lynn": "린", "Machado": "마차도", "Maeda": "마에다", "Manaea": "마네아", "Marquez": "마르케스", 
    "Marte": "마르테", "Martin": "마틴", "Martinez": "마르티네스", "Martínez": "마르티네스", "Maton": "메이튼", 
    "Matos": "마토스", "Matz": "마츠", "Mautz": "마우츠", "May": "메이", "Mays": "메이스", 
    "McCarthy": "매카시", "McClanahan": "맥클라나한", "McCullers": "맥컬러스", "McGough": "맥거프", "McGreevy": "맥그리비", 
    "McLean": "맥클레인", "Megill": "메길", "Menechino": "메네키노", "Merrill": "메릴", "Mey": "메이", 
    "Mikolas": "마이콜라스", "Miller": "밀러", "Minter": "민터", "Misiewicz": "미시에비츠", "Molina": "몰리나", 
    "Moll": "몰", "Moncada": "몬카다", "Montas": "몬타스", "Moore": "무어", "Morejon": "모레혼", 
    "Moreno": "모레노", "Morgan": "모건", "Morris": "모리스", "Morton": "모튼", "Muncy": "먼시", 
    "Munoz": "무뇨스", "Muñoz": "무뇨스", "Murphy": "머피", "Musgrove": "머스그로브", "Nardi": "나르디", 
    "Naylor": "네일러", "Nelson": "넬슨", "Neris": "네리스", "Nevin": "네빈", "Nimmala": "니말라", 
    "Nimmo": "니모", "Noda": "노다", "Nola": "놀라", "Ober": "오버", "O'Brien": "오브라이언", 
    "O'Hoppe": "오호피", "O'Neill": "오닐", "ONeill": "오닐", "Oneill": "오닐", "Ohtani": "오타니", "Ortiz": "오르티스", "Ottavino": "오타비노", "Outman": "아웃맨", 
    "Ozuna": "오주나", "Paddack": "패댁", "Pagan": "파간", "Pagán": "파간", "Painter": "페인터", 
    "Pallante": "팔란테", "Paredes": "파레데스", "Pavin": "파빈", "Pena": "페냐", "Peña": "페냐", 
    "Peralta": "페랄타", "Perdomo": "페르도모", "Perez": "페레즈", "Pérez": "페레즈", "Pfaadt": "팟", 
    "Pham": "팜", "Phillips": "필립스", "Pinckney": "핑크니", "Pivetta": "피베타", "Poche": "포셰", 
    "Polanco": "폴랑코", "Pressly": "프레슬리", "Prieto": "프리에토", "Quantrill": "콴트릴", "Quinn": "퀸", 
    "Rafaela": "라파엘라", "Ragans": "레이건스", "Ramirez": "라미레즈", "Ramírez": "라미레즈", "Ramos": "라모스", 
    "Rangel": "란겔", "Rasmussen": "라스무센", "Raysor": "레이서", "Realmuto": "리얼무토", "Reed": "리드", 
    "Rendon": "렌던", "Reynolds": "레이놀즈", "Rincon": "린콘", "Rincón": "린콘", "Rivas": "리바스", 
    "Rivera": "리베라", "Robertson": "로버트슨", "Robles": "로블레스", "Rodgers": "로저스", "Rodriguez": "로드리게스", 
    "Rodríguez": "로드리게스", "Rogers": "로저스", "Rojas": "로하스", "Romero": "로메로", "Rosario": "로사리오", 
    "Routzahn": "라우트잔", "Roxby": "록스비", "Ruiz": "루이즈", "Rutschman": "러치맨", "Ryan": "라이언", 
    "Sale": "세일", "Sanmartin": "산마르틴", "Sanmartín": "산마르틴", "Santana": "산타나", "Santander": "산탄데르", 
    "Santos": "산토스", "Scherzer": "슈어저", "Schmidt": "슈미트", "Schneider": "슈나이더", "Scholtens": "숄텐스", 
    "Schreiber": "슈라이버", "Schwellenbach": "슈웰렌바크", "Scott": "스콧", "Sears": "시어스", "Seager": "시거", 
    "Semien": "세미엔", "Senga": "센가", "Severino": "세베리노", "Seymour": "시모어", "Shaw": "쇼", 
    "Sheehan": "시한", "Siri": "시리", "Skenes": "스킨스", "Skubal": "스쿠발", "Smith": "스미스", 
    "Smith-Shawver": "스미스-쇼버", "Smeltzer": "스멜처", "Snell": "스넬", "Snider": "스나이더", "Solano": "솔라노", 
    "Soriano": "소리아노", "Soto": "소토", "Speier": "스파이어", "Springs": "스프링스", "Stanek": "스타넥", 
    "Stanton": "스탠튼", "Steer": "스티어", "Stephenson": "스티븐슨", "Stowers": "스타워즈", "Strahm": "스트람", 
    "Stroman": "스트로먼", "Strider": "스트라이더", "Suarez": "수아레즈", "Suárez": "수아레즈", "Suzuki": "스즈키", 
    "Swanson": "스완슨", "Taillon": "타이욘", "Tatis": "타티스", "Taylor": "테일러", "Tepera": "테페라", 
    "Thomas": "토마스", "Thompson": "톰슨", "Thornton": "손튼", "Torkelson": "토켈슨", "Torres": "토레스", 
    "Treinen": "트레이넨", "Tucker": "터커", "Turang": "투랑", "Turner": "터너", "Urquidy": "우르키디", 
    "Valdez": "발데스", "Varland": "발랜드", "Vargas": "바르가스", "Varsho": "바쇼", "Vasquez": "바스케스", 
    "Vaughn": "본", "Vesia": "베시아", "Vest": "베스트", "Vieira": "비에이라", "Vientos": "비엔토스", 
    "Volpe": "볼피", "Wacha": "와카", "Waldichuk": "왈디척", "Walker": "워커", "Walston": "월스턴", 
    "Ward": "워드", "Warren": "워렌", "Webb": "웹", "Weissert": "와이서트", "Wells": "웰스", 
    "Wentz": "웬츠", "Wheeler": "휠러", "White": "화이트", "Whitlock": "윗록", "Wilkerson": "윌커슨", 
    "Wilkinson": "윌킨슨", "Williams": "윌리엄스", "Wilson": "윌슨", "Winder": "윈더", "Winn": "윈", 
    "Winquest": "윈퀘스트", "Witt": "위트", "Woo": "우", "Wood": "우드", "Woodruff": "우드러프", 
    "Yarbrough": "야브로", "Yastrzemski": "야스트렘스키", "Yates": "예이츠", "Yoshida": "요시다", "Young": "영", 
    "Zamora": "자모라", "Zavala": "자발라", "Zimmermann": "짐머만", "Zuniga": "주니가"
}

# Full special names
FULL_NAMES = {
    "Shohei Ohtani": "오타니 쇼헤이",
    "Yoshinobu Yamamoto": "야마모토 요시노부",
    "Shota Imanaga": "이마나가 쇼타",
    "Kodai Senga": "센가 코다이",
    "Yu Darvish": "다르빗슈 유",
    "Seiya Suzuki": "스즈키 세이야",
    "Masataka Yoshida": "요시다 마사타카",
    "Jung Hoo Lee": "이정후",
    "Ha-Seong Kim": "김하성",
    "Ha-seong Kim": "김하성",
    "Ji-Hwan Bae": "배지환",
    "Ji Hwan Bae": "배지환",
    "菅井 信也": "스가이 신야",
    "菅井信也": "스가이 신야",
    "菅井": "스가이 신야",
    "Shinya Sugai": "스가이 신야",
    "Sugai Shinya": "스가이 신야",
    "九里 亜蓮": "쿠리 아렌",
    "九里亜蓮": "쿠리 아렌",
    "Aren Kuri": "쿠리 아렌",
    "Kuri Aren": "쿠리 아렌",
    "髙橋 光成": "타카하시 코나",
    "髙橋光成": "타카하시 코나",
    "高橋光成": "타카하시 코나",
    "豆田 泰志": "마메다 타츠키",
    "豆田": "마메다 타츠키",
    "佐藤 隼輔": "사토 슌스케",
    "佐藤隼": "사토 슌스케",
    "松本 航": "마츠모토 와타루",
    "松本": "마츠모토 와타루",
    "黒木 優太": "쿠로키 유타",
    "黒木": "쿠로키 유타",
    "平良 海馬": "타이라 카이마",
    "平良": "타이라 카이마",
    "本田 圭佑": "혼다 케이스케",
    "本田": "혼다 케이스케",
    "水上 由伸": "미즈카미 요시노부",
    "水上": "미즈카미 요시노부",
    "武内 夏暉": "타케우치 나츠키",
    "今井 達也": "이마이 타츠야",
    "髙島 泰都": "타카시마 타이스케",
    "髙島": "타카시마 타이스케",
    "佐藤 爽": "사토 소우",
    "高野 脩汰": "타카노 슈타",
    "松本 晴": "마츠모토 하루",
    "井上 温大": "이노우에 하루토",
    "深沢 鳳介": "후카자와 호스케",
    "栗林 良吏": "쿠리바야시 료지",
    "金丸 夢斗": "카네마루 유메토",
    "富山 凌雅": "토미야마 료타",
    "富山": "토미야마 료타",
    "椋木 蓮": "무쿠노키 렌",
    "椋木": "무쿠노키 렌",
    "山﨑 颯一郎": "야마사키 소이치로",
    "山﨑": "야마사키 소이치로",
    "マチャド": "마차도",
    "A.마차도": "안드레스 마차도",
    "阿部 翔太": "아베 쇼타",
    "阿部": "아베 쇼타",
    "山田 修義": "야마다 노부요시",
    "山田": "야마다 노부요시",
    "ペルドモ": "루이스 페르도모",
    "L.페르도모": "루이스 페르도모",
    "曽谷 龍平": "소타니 류헤이",
    "曽谷": "소타니 류헤이",
    "エスピノーザ": "안데르손 에스피노자"
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
    # Already Korean?
    if re.search(r'[가-힣]', raw):
        return raw + suffix
    
    if raw in FULL_NAMES:
        return FULL_NAMES[raw] + suffix

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
    last_ko = LAST_NAMES.get(last) or LAST_NAMES.get(last.capitalize())
    
    if not last_ko:
        # If compound last name or middle name (e.g. De La Cruz or Middle + Last)
        if len(parts) == 3:
            mid_ko = FIRST_NAMES.get(parts[1]) or LAST_NAMES.get(parts[1]) or rule_transliterate_word(parts[1])
            end_ko = LAST_NAMES.get(parts[2]) or LAST_NAMES.get(parts[2].capitalize()) or rule_transliterate_word(parts[2])
            last_ko = f"{mid_ko} {end_ko}"
        else:
            last_parts = [LAST_NAMES.get(p) or LAST_NAMES.get(p.capitalize()) or FIRST_NAMES.get(p) or FIRST_NAMES.get(p.capitalize()) or rule_transliterate_word(p) for p in parts[1:]]
            last_ko = " ".join(last_parts)
        
    return f"{first_ko} {last_ko}".strip() + jr_suffix + suffix

def rule_transliterate_word(word: str) -> str:
    if not word: return ''
    if word.upper() in PROTECTED_TERMS or (len(word) <= 5 and not re.search(r'[aeiouyAEIOUY]', word)):
        return word
    clean = unicodedata.normalize('NFKD', word)
    clean = ''.join(ch for ch in clean if not unicodedata.combining(ch)).lower()
    clean = re.sub(r'tion$', '션', clean)
    clean = re.sub(r'sion$', '션', clean)
    clean = re.sub(r'son$', '슨', clean)
    clean = re.sub(r'sen$', '센', clean)
    clean = re.sub(r'ton$', '턴', clean)
    clean = re.sub(r'man$', '맨', clean)
    clean = re.sub(r'kin$', '킨', clean)
    clean = re.sub(r'lin$', '린', clean)
    clean = re.sub(r'tin$', '틴', clean)
    clean = re.sub(r'rin$', '린', clean)
    clean = re.sub(r'win$', '윈', clean)
    clean = re.sub(r'ley$', '리', clean)
    clean = re.sub(r'ly$', '리', clean)
    clean = re.sub(r'quest$', '퀘스트', clean)
    w = clean
    replacements = [
        ('sh', '시'), ('ch', '치'), ('ph', '프'), ('th', '트'),
        ('qu', '퀴'), ('wh', '화'), ('ck', '크'),
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
