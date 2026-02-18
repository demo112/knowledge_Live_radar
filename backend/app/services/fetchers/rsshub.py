import logging
import re
from typing import List, Dict, Any
from urllib.parse import quote
from .rss import RSSFetcher

logger = logging.getLogger(__name__)

class RSSHubFetcher(RSSFetcher):
    BASE_URL = "https://rsshub.app"

    def __init__(self, source_type: str):
        self.source_type = source_type

    def _get_rsshub_path(self, url: str) -> str:
        if self.source_type == "WECHAT_MP":
            # Encode the nickname for URL (handling Chinese characters)
            encoded_url = quote(url)
            return f"/wechat/gzh/{encoded_url}"
        elif self.source_type == "BILIBILI_USER":
            user_id = self._extract_bilibili_id(url)
            return f"/bilibili/user/video/{user_id}"
        elif self.source_type == "JUEJIN_COLUMN":
            return f"/juejin/columns/{url}"
        return url

    def _extract_bilibili_id(self, url: str) -> str:
        # Match pattern like space.bilibili.com/123456
        match = re.search(r'space\.bilibili\.com/(\d+)', url)
        if match:
            return match.group(1)
        # Or just digits
        if url.isdigit():
            return url
        return url

    async def fetch(self, url: str) -> List[Dict[str, Any]]:
        path = self._get_rsshub_path(url)
        rss_url = f"{self.BASE_URL}{path}"
        logger.info(f"Converted {self.source_type} source {url} to RSSHub URL: {rss_url}")
        return await super().fetch(rss_url)

    async def validate_source(self, url: str) -> bool:
        path = self._get_rsshub_path(url)
        rss_url = f"{self.BASE_URL}{path}"
        return await super().validate_source(rss_url)
