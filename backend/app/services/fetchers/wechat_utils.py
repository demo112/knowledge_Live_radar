from typing import Optional
import httpx
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

async def extract_wechat_info(url: str) -> Optional[dict[str, str]]:
    """
    Extracts the official account info from a WeChat article URL.
    Returns dict with 'nickname' and 'user_name' (gh_id), or None.
    """
    if not url:
        return None
        
    try:
        # Use a real browser User-Agent and headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
        }
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text
            
            result = {}
            
            # 1. Nickname
            nickname_match = re.search(r'var\s+nickname\s*=\s*"([^"]+)"', html_content)
            if nickname_match:
                result["nickname"] = nickname_match.group(1)
            else:
                # Fallback to HTML parsing
                soup = BeautifulSoup(html_content, 'html.parser')
                profile_nickname = soup.find(id="profile_nickname") or soup.find(class_="profile_nickname") or soup.find(id="js_name")
                if profile_nickname:
                    result["nickname"] = profile_nickname.get_text(strip=True)

            # 2. User Name (gh_id)
            username_match = re.search(r'var\s+user_name\s*=\s*"([^"]+)"', html_content)
            if username_match:
                result["user_name"] = username_match.group(1)

            if result:
                return result
            
            logger.warning(f"Could not extract WeChat info from {url}")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting WeChat info from {url}: {str(e)}")
        return None
