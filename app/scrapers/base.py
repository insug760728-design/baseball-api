from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseScraper(ABC):
    """스포츠 공식 사이트 스크래퍼 기본 규격"""
    
    @abstractmethod
    def get_sport_code(self) -> str:
        pass

    @abstractmethod
    def get_league_name(self) -> str:
        pass

    @abstractmethod
    def scrape_matches(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """경기 일정 및 기본 결과 목록 수집"""
        pass

    @abstractmethod
    def scrape_match_detail(self, official_id: str) -> Dict[str, Any]:
        """특정 경기의 상세 내역(세부 지표, 타임라인 이벤트, 선수별 상세 스탯) 수집"""
        pass