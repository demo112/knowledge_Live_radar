from .base import BaseFetcher
from .rss import RSSFetcher
from .api import APIFetcher
from .web import WebFetcher

def get_fetcher(type: str) -> BaseFetcher:
    if type == "rss":
        return RSSFetcher()
    elif type == "api":
        return APIFetcher()
    elif type == "web":
        return WebFetcher()
    else:
        # Default fallback or raise error
        # For now, treat unknown as generic API or raise
        raise ValueError(f"Unknown fetcher type: {type}")
