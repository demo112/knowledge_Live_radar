from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch content from the given URL.
        Returns a list of content items (dictionaries).
        Each item should at least contain: 'title', 'url', 'content', 'published_at'.
        """
        pass

    @abstractmethod
    async def validate_source(self, url: str) -> bool:
        """
        Validate if the source URL is accessible and valid for this fetcher.
        """
        pass
