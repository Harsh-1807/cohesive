import requests
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        pass
