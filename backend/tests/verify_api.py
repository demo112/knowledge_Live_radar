import asyncio
import sys
import os
import httpx
from uuid import UUID

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings

BASE_URL = f"http://test{settings.API_V1_STR}"

async def verify_api():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        print(f"Testing API at {BASE_URL}")

        # 1. Create Pyramid
        print("\n[1] Creating Pyramid...")
        response = await client.post("/pyramids", json={
            "name": "API Test Pyramid",
            "description": "Created via API Test"
        })
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error: {response.text}")
            return
        
        pyramid_data = response.json()["data"]
        pyramid_id = pyramid_data["id"]
        print(f"Pyramid Created: {pyramid_id} - {pyramid_data['name']}")

        # 2. Add Root Node
        print("\n[2] Adding Root Node...")
        response = await client.post(f"/pyramids/{pyramid_id}/nodes", json={
            "name": "Root Node API",
            "description": "API Root"
        })
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error: {response.text}")
            return

        node_data = response.json()["data"]
        root_id = node_data["id"]
        print(f"Root Node Created: {root_id} - Path: {node_data['path']}")

        # 3. Create Source
        print("\n[3] Creating Source...")
        response = await client.post("/sources", json={
            "name": "Test RSS",
            "type": "RSS",
            "url": "https://example.com/rss",
            "config": {"feed_url": "https://example.com/rss"}
        })
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
             print(f"Error: {response.text}")
             # It might fail if URL exists (from previous runs), let's handle that
             if "already exists" in response.text:
                 print("Source already exists, continuing...")
             else:
                 return
        else:
            source_data = response.json()["data"]
            print(f"Source Created: {source_data['id']} - {source_data['name']}")

        # 4. List Pyramids
        print("\n[4] Listing Pyramids...")
        response = await client.get("/pyramids")
        print(f"Status: {response.status_code}")
        data = response.json()["data"]
        print(f"Total Pyramids: {data['total']}")
        for p in data['items']:
            print(f" - {p['name']} ({p['id']})")

        print("\nAPI Verification Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(verify_api())
