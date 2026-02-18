import asyncio
from app.services.fetchers.wechat_utils import extract_wechat_info

async def main():
    urls = [
        "https://mp.weixin.qq.com/s/iULo3kWt0Th82FKoaW4SMQ",
        "https://mp.weixin.qq.com/s/tq1w6FREMiYoPzTXCsQsKg"
    ]
    for url in urls:
        print(f"Extracting from {url}...")
        name = await extract_wechat_info(url)
        print(f"Result: {name}")

if __name__ == "__main__":
    asyncio.run(main())
