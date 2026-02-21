import asyncio
import json
import httpx

async def test_douyin_stream():
    url = "http://localhost:8000/api/v1/tools/douyin/stream"
    # Use a random video ID or the one from the error log
    payload = {"url": "https://www.douyin.com/video/7434563884323261735"}
    
    print(f"Connecting to {url} with payload: {payload}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            print(f"Response status: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    try:
                        event = json.loads(data)
                        print(f"Event: {event}")
                        if event.get("stage") == "preparing" and "获取Cookies" in event.get("message", ""):
                            print("SUCCESS: Automated cookie fetching triggered!")
                        if event.get("stage") == "finished":
                            print("SUCCESS: Conversion finished!")
                            break
                        if event.get("stage") == "error":
                            print(f"ERROR: {event.get('message')}")
                            break
                    except json.JSONDecodeError:
                        print(f"Raw data: {data}")

if __name__ == "__main__":
    asyncio.run(test_douyin_stream())
