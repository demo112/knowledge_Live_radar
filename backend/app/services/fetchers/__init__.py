from .base import BaseFetcher
from .rss import RSSFetcher
from .api import APIFetcher
from .web import WebFetcher
from .rsshub import RSSHubFetcher
from .firecrawl_fetcher import FirecrawlFetcher

def get_fetcher(type: str) -> BaseFetcher:
    type_upper = type.upper()
    type_lower = type.lower()
    
    if type_lower == "rss":
        return RSSFetcher()
    elif type_lower == "api":
        return APIFetcher()
    elif type_lower == "web":
        return FirecrawlFetcher()
    elif type_upper in ["WECHAT_MP", "BILIBILI_USER", "JUEJIN_COLUMN", "YOUTUBE_CHANNEL"]:
        return RSSHubFetcher(source_type=type_upper)
    else:
        # Default fallback or raise error
        # For now, treat unknown as generic API or raise
        raise ValueError(f"Unknown fetcher type: {type}")
