import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def analyze_wechat_html():
    url = "https://mp.weixin.qq.com/s/iULo3kWt0Th82FKoaW4SMQ"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Fetching {url}...")
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        html = resp.text
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Try to find nickname
    nickname_selectors = [
        "#js_name", 
        ".profile_nickname", 
        ".rich_media_meta_nickname",
        "#js_wx_follow_nickname"
    ]
    
    print("\n--- Nickname Search ---")
    for sel in nickname_selectors:
        element = soup.select_one(sel)
        if element:
            print(f"Found {sel}: {element.get_text(strip=True)}")
        else:
            print(f"Not found: {sel}")
            
    # 2. Try to find __biz
    print("\n--- Biz Search ---")
    biz_match = re.search(r'var\s+biz\s*=\s*"([^"]+)"', html)
    if biz_match:
        print(f"Found var biz: {biz_match.group(1)}")
    else:
        print("var biz not found")
        
    # 3. Print a snippet of HTML around 'nickname'
    print("\n--- HTML Snippet ---")
    match = re.search(r'nickname', html, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 100)
        end = min(len(html), match.end() + 100)
        print(html[start:end])

if __name__ == "__main__":
    asyncio.run(analyze_wechat_html())
