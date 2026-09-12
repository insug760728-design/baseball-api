/**
 * TOKEON V2 Common Utilities (common_utils.js)
 * Clean factual helpers: Team name formatting, league name formatting, date/time formatting, 2D baseball SVG generator, sound FX
 */

const CommonUtils = (() => {
  const _SHORT_TEAM_NAMES = {
    // KBO
    'KIA 타이거즈': 'KIA', '기아 타이거즈': 'KIA', '기아': 'KIA',
    '삼성 라이온즈': '삼성',
    'LG 트윈스': 'LG',
    '두산 베어스': '두산',
    'KT 위즈': 'KT',
    'SSG 랜더스': 'SSG', '에스에스지': 'SSG',
    '롯데 자이언츠': '롯데',
    '한화 이글스': '한화',
    'NC 다이노스': 'NC',
    '키움 히어로즈': '키움',
    
    // NPB
    '요미우리 자이언츠': '요미우리', '요미우리자이언츠': '요미우리',
    '한신 타이거스': '한신', '한신타이거스': '한신',
    '주니치 드래곤즈': '주니치', '주니치드래곤즈': '주니치',
    '도쿄 야쿠르트 스왈로스': '야쿠르트', '야쿠르트 스왈로스': '야쿠르트',
    '요코하마 DeNA 베이스타즈': 'DeNA', '요코하마 DeNA': 'DeNA', 'DeNA 베이스타즈': 'DeNA', '요코하마': 'DeNA',
    '히로시마 도요 카프': '히로시마', '히로시마 도요카프': '히로시마',
    '후쿠오카 소프트뱅크 호크스': '소프트뱅크', '소프트뱅크 호크스': '소프트뱅크',
    '지바 롯데 마린스': '지바롯데', '지바롯데 마린스': '지바롯데', '지바 롯데': '지바롯데', '치바 롯데': '지바롯데',
    '도호쿠 라쿠텐 골든이글스': '라쿠텐', '라쿠텐 골든이글스': '라쿠텐',
    '오릭스 버펄로스': '오릭스', '오릭스 버팔로스': '오릭스',
    '사이타마 세이부 라이온즈': '세이부', '세이부 라이온즈': '세이부',
    '홋카이도 닛폰햄 파이터즈': '니혼햄', '닛폰햄 파이터즈': '니혼햄', '닛폰햄': '니혼햄',
    
    // MLB
    '시카고 컵스': '시카고C', '시카고C': '시카고C',
    '시카고 화이트삭스': '시카고W', '시카고W': '시카고W',
    '피츠버그 파이리츠': '피츠버그',
    '디트로이트 타이거스': '디트로이트',
    '콜로라도 로키스': '콜로라도',
    '워싱턴 내셔널스': '워싱턴',
    'LA 에인절스': 'LA에인절스', '로스앤젤레스 에인절스': 'LA에인절스',
    'LA 다저스': 'LA다저스', '로스앤젤레스 다저스': 'LA다저스',
    '뉴욕 양키스': 'NY양키스',
    '뉴욕 메츠': 'NY메츠',
    '토론토 블루제이스': '토론토',
    '볼티모어 오리올스': '볼티모어',
    '보스턴 레드삭스': '보스턴',
    '탬파베이 레이스': '탬파베이',
    '클리블랜드 가디언스': '클리블랜드',
    '캔자스시티 로열스': '캔자스시티',
    '미네소타 트윈스': '미네소타',
    '휴스턴 애스트로스': '휴스턴',
    '시애틀 매리너스': '시애틀',
    '텍사스 레인저스': '텍사스',
    '오클랜드 애슬레틱스': '오클랜드',
    '애틀랜타 브레이브스': '애틀랜타',
    '마이애미 말린스': '마이애미',
    '필라델피아 필리스': '필라델피아',
    '밀워키 브루어스': '밀워키',
    '세인트루이스 카디널스': '세인트루이스',
    '신시내티 레즈': '신시내티',
    '애리조나 다이아몬드백스': '애리조나',
    '샌디에이고 파드리스': '샌디에이고',
    '샌프란시스코 자이언츠': '샌프란시스코',

    // SOCCER
    '맨체스터 시티': '맨시티', '맨체스터시티': '맨시티', '맨체스터 C': '맨시티',
    '맨체스터 유나이티드': '맨유', '맨체스터유나이티드': '맨유', '맨체스터 U': '맨유',
    '토트넘 홋스퍼': '토트넘', '토트넘 핫스퍼': '토트넘', '토트넘홋스퍼': '토트넘',
    '뉴캐슬 유나이티드': '뉴캐슬',
    '웨스트햄 유나이티드': '웨스트햄',
    '브라이튼 앤 호브 알비온': '브라이튼', '브라이튼 앤 호브': '브라이튼',
    '울버햄튼 원더러스': '울버햄튼',
    '크리스탈 팰리스': 'C.팰리스',
    '노팅엄 포레스트': '노팅엄',
    '아스톤 빌라': '아스톤빌라',
    '레스터 시티': '레스터',
    '입스위치 타운': '입스위치',
    '리즈 유나이티드': '리즈',
    '셰필드 유나이티드': '셰필드',
    '웨스트 브롬위치': '웨스트브롬', '웨스트 브롬': '웨스트브롬',
    '블랙번 로버스': '블랙번',
    '스완지 시티': '스완지',
    '볼턴 원더러스': '볼턴',
    '카디프 시티': '카디프',
    '레알 마드리드': '레알',
    '아틀레티코 마드리드': 'AT마드리드',
    '아틀레틱 빌바오': '빌바오', '아틀레틱 클루브': '빌바오',
    '레알 소시에다드': '소시에다드',
    '레알 베티스': '베티스',
    '셀타 비고': '셀타비고',
    '라요 바예카노': '라요',
    'AC 밀란': 'AC밀란',
    '인테르나치오날레': '인테르', '인테르 밀란': '인테르',
    'AS 로마': 'AS로마',
    '엘라스 베로나': '베로나',
    'ACF 피오렌티나': '피오렌티나', '피오렌티나': '피오렌티나',
    '바이에른 뮌헨': '뮌헨',
    '보루시아 도르트문트': '도르트문트',
    '보루시아 묀헨글라트바흐': '묀헨', '묀헨글라트바흐': '묀헨',
    '바이어 레버쿠젠': '레버쿠젠',
    'RB 라이프치히': '라이프치히',
    '파리 생제르맹': 'PSG', '파리 생제르망': 'PSG', '파리 SG': 'PSG',
    '올랭피크 드 마르세유': '마르세유', '올랭피크 마르세유': '마르세유', '올랭피크드 마르세유': '마르세유',
    '올랭피크 리옹': '리옹',
    '스타드 렌': '스타드렌',
    '스타드 브레스트': '브레스트',
    'AZ 알크마르': '알크마르', 'AZ알크마르': '알크마르',
    '빌럼 II': '빌럼', '빌럼2': '빌럼', '빌럼': '빌럼',
    'PSV 에인트호번': 'PSV', '에인트호번': 'PSV',
    'FC 위트레흐트': '위트레흐트',
    'FC 트벤테': '트벤테',
    'SC 헤이렌베인': '헤이렌베인',
    '스파르타 로테르담': '로테르담',
    '비셀 고베': '고베',
    '요코하마 F. 마리노스': '요코하마FM',
    '산프레체 히로시마': '히로시마',
    '가와사키 프론탈레': '가와사키',
    '우라와 레즈': '우라와',
    '가시마 앤틀러스': '가시마',
    '감바 오사카': '감바오사카',
    '세레소 오사카': '세레소오사카',
    '나고야 그램퍼스': '나고야',
    '주빌로 이와타': '주빌로이와타',
    '오이타 트리니타': '오이타',
    '울산 HD': '울산', '울산 현대': '울산',
    '전북 현대': '전북', '전북 현대 모터스': '전북',
    '포항 스틸러스': '포항',
    'FC 서울': 'FC서울', 'FC서울': 'FC서울',
    '제주 유나이티드': '제주',
    '대전 하나 시티즌': '대전', '대전 시티즌': '대전',
    '김천 상무': '김천',
    '인천 유나이티드': '인천',
    '수원 삼성': '수원삼성',
    '수원 FC': '수원FC', '수원FC': '수원FC',
    '강원 FC': '강원', '강원FC': '강원',
    '광주 FC': '광주', '광주FC': '광주',
    '충남아산 프로축구단': '충남아산', '충남아산': '충남아산',
    '충북청주 프로축구단': '충북청주', '충북청주': '충북청주',
    '안산 그리너스': '안산',
    '천안시티FC': '천안시티',
    '부산 아이파크': '부산',
    '전남 드래곤즈': '전남'
  };

  const _SHORT_LEAGUE_NAMES = {
    'England - Premier League 2 Division One': 'EPL 2부',
    'England - Premier League': 'EPL',
    'Premier League 2 Division One': 'EPL 2부',
    'Premier League': 'EPL',
    'England Premier League': 'EPL',
    'EPL 프리미어리그': 'EPL',
    'England - Championship': '챔피언십',
    '잉글랜드 챔피언십': '챔피언십',
    'England - League One': '리그1(영국)',
    'England - League Two': '리그2(영국)',
    'England - EFL Trophy': 'EFL트로피',
    '라리가 스페인축구': '라리가',
    'Spain - La Liga': '라리가',
    '스페인 라리가': '라리가',
    '세리에A 이탈리아축구': '세리에A',
    'Italy - Serie A': '세리에A',
    '이탈리아 세리에A': '세리에A',
    '분데스리가 독일축구': '분데스리가',
    'Germany - Bundesliga': '분데스리가',
    '독일 분데스리가': '분데스리가',
    '리그앙 프랑스축구': '리그1',
    'France - Ligue 1': '리그1',
    '프랑스 리그1': '리그1',
    'South-Korea - K League 1': 'K리그1',
    'South-Korea - K League 2': 'K리그2',
    '한국 K리그1': 'K리그1',
    '한국 K리그2': 'K리그2',
    'K리그 1': 'K리그1',
    'K리그 2': 'K리그2',
    'K리그1': 'K리그1',
    'K리그2': 'K리그2',
    'Japan - J1 League': 'J1리그',
    'Japan - J2 League': 'J2리그',
    '일본 J1리그': 'J1리그',
    '일본 J2리그': 'J2리그',
    'USA - Major League Soccer': 'MLS',
    'Major League Soccer': 'MLS',
    '아시아배구연맹 챌린저컵 남자배구 선수권대회': '배구 선수권',
    '남자배구 선수권대회': '배구 선수권',
    '여자배구 선수권대회': '배구 선수권',
    'FIBA 아시아컵 남자 농구': '농구 아시아컵',
    '아시안게임 남자농구': '아시안게임 농구',
    'KBO 한국야구': 'KBO',
    'NPB 일본야구': 'NPB',
    'MLB 메이저리그': 'MLB',
    '일본 프로야구 (NPB)': 'NPB',
    '한국 프로야구 (KBO)': 'KBO',
    '미국 프로야구 (MLB)': 'MLB'
  };

  function formatTeamName(name) {
    if (!name) return '';
    const clean = String(name).trim();
    if (_SHORT_TEAM_NAMES[clean]) return _SHORT_TEAM_NAMES[clean];

    for (const [k, v] of Object.entries(_SHORT_TEAM_NAMES)) {
      if (clean === k || clean.startsWith(k) || (k.length >= 3 && clean.includes(k))) {
        return v;
      }
    }

    return clean
      .replace(/^(FC\s*|SC\s*|AC\s*|AS\s*|RB\s*)/g, '')
      .replace(/(\s*(프로축구단|축구단|자이언츠|타이거즈|라이온즈|베어스|이글스|다이노스|트윈스|히어로즈|파이리츠|브루어스|로키스|내셔널스|블루제이스|오리올스|레드삭스|가디언스|로열스|애스트로스|매리너스|레인저스|애슬레틱스|브레이브스|말린스|필리스|카디널스|다이아몬드백스|파드리스|유나이티드|원더러스|호크스|스왈로스|버펄로스|드래곤즈|시티|타운|FC|스틸러스))$/g, '')
      .trim() || clean;
  }

  function formatLeagueName(league) {
    if (!league) return '';
    const clean = String(league).trim();
    if (_SHORT_LEAGUE_NAMES[clean]) return _SHORT_LEAGUE_NAMES[clean];
    for (const [k, v] of Object.entries(_SHORT_LEAGUE_NAMES)) {
      if (clean.includes(k) || k.includes(clean)) return v;
    }
    return clean.replace(/^(England\s*-\s*|South-Korea\s*-\s*|Japan\s*-\s*|Spain\s*-\s*|Germany\s*-\s*|France\s*-\s*|Italy\s*-\s*|USA\s*-\s*)/i, '').trim();
  }

  function formatPlayerKorean(name) {
    if (!name || name === '-') return '-';
    return String(name).trim();
  }

  function formatKSTDateTime(dateStr) {
    if (!dateStr) return '-';
    try {
      if (dateStr.includes('T') || dateStr.includes('-')) {
        const d = new Date(dateStr);
        if (!isNaN(d.getTime())) {
          const m = String(d.getMonth() + 1).padStart(2, '0');
          const day = String(d.getDate()).padStart(2, '0');
          const h = String(d.getHours()).padStart(2, '0');
          const min = String(d.getMinutes()).padStart(2, '0');
          return `${m}-${day} ${h}:${min}`;
        }
      }
      return dateStr.replace(/(\d{4}-)/g, '').substring(0, 11);
    } catch(e) {
      return dateStr;
    }
  }

  function renderMiniDiamondSvg(runners = {}, outs = 0) {
    const b1 = Boolean(runners.b1 || runners.first || runners['1b']);
    const b2 = Boolean(runners.b2 || runners.second || runners['2b']);
    const b3 = Boolean(runners.b3 || runners.third || runners['3b']);
    const oCount = Math.max(0, Math.min(2, Number(outs) || 0));

    const c1 = b1 ? '#f59e0b' : '#cbd5e1';
    const c2 = b2 ? '#f59e0b' : '#cbd5e1';
    const c3 = b3 ? '#f59e0b' : '#cbd5e1';
    const s1 = b1 ? '#b45309' : '#94a3b8';
    const s2 = b2 ? '#b45309' : '#94a3b8';
    const s3 = b3 ? '#b45309' : '#94a3b8';

    const out1 = oCount >= 1 ? '#dc2626' : '#cbd5e1';
    const out2 = oCount >= 2 ? '#dc2626' : '#cbd5e1';

    return `
      <div class="mini-diamond-box" title="주자: ${b1?'1루 ':''}${b2?'2루 ':''}${b3?'3루 ':''}${(!b1&&!b2&&!b3)?'주자없음':''} | ${oCount}아웃">
        <svg class="diamond-svg" viewBox="0 0 24 24">
          <polygon points="12,2 16,6 12,10 8,6" fill="${c2}" stroke="${s2}" stroke-width="0.8" />
          <polygon points="6,8 10,12 6,16 2,12" fill="${c3}" stroke="${s3}" stroke-width="0.8" />
          <polygon points="18,8 22,12 18,16 14,12" fill="${c1}" stroke="${s1}" stroke-width="0.8" />
          <polygon points="12,18 15,20 12,22 9,20" fill="#94a3b8" />
        </svg>
        <div class="mini-out-dots">
          <span class="out-dot" style="background: ${out1};"></span>
          <span class="out-dot" style="background: ${out2};"></span>
        </div>
      </div>
    `;
  }

  function getSportIcon(sportCode) {
    const sp = (sportCode || '').toUpperCase();
    if (sp === 'BASEBALL') return '⚾';
    if (sp === 'SOCCER') return '⚽';
    if (sp === 'BASKETBALL') return '🏀';
    if (sp === 'VOLLEYBALL') return '🏐';
    return '🏆';
  }

  return {
    formatTeamName,
    formatLeagueName,
    formatPlayerKorean,
    formatKSTDateTime,
    renderMiniDiamondSvg,
    getSportIcon
  };
})();
