import asyncio
import logging
from app.services.fetchers.rss import RSSFetcher
from app.services.fetchers.web import WebFetcher

logging.basicConfig(level=logging.INFO)

async def test_rss():
    fetcher = RSSFetcher()
    # OpenAI Blog usually requires User-Agent
    url = "https://openai.com/blog/rss.xml" 
    print(f"Testing RSS fetch for {url}...")
    try:
        items = await fetcher.fetch(url)
        print(f"Success! Fetched {len(items)} items.")
        for item in items[:2]:
            print(f" - {item['title']}")
    except Exception as e:
        print(f"Failed: {repr(e)}")

async def test_web():
    fetcher = WebFetcher()
    # Use httpbin to verify headers
    url = "https://httpbin.org/headers"
    print(f"\nTesting Web fetch for {url}...")
    try:
        items = await fetcher.fetch(url)
        print(f"Success! Fetched {len(items)} items.")
        print(items[0]['content'])
    except Exception as e:
        print(f"Failed: {repr(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_rss())
    asyncio.run(test_web())
