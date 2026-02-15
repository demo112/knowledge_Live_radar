import asyncio
import httpx

async def verify_routes():
    base_url = "http://127.0.0.1:8000/api/v1"
    endpoints = [
        "/pyramids",
        "/sources",
        "/contents",
        "/approvals/queue",
        "/approvals/pending",
        "/hotspots",
        "/health/report/latest",
        "/notifications",
        "/synonyms"
    ]
    
    async with httpx.AsyncClient() as client:
        print(f"Checking endpoints at {base_url}...")
        for ep in endpoints:
            try:
                resp = await client.get(f"{base_url}{ep}")
                print(f"{ep}: {resp.status_code}")
            except Exception as e:
                print(f"{ep}: Exception {e}")

if __name__ == "__main__":
    asyncio.run(verify_routes())
