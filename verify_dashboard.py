import asyncio
import httpx
import sys

async def verify_dashboard():
    base_url = "http://127.0.0.1:8000/api/v1"
    async with httpx.AsyncClient() as client:
        try:
            print(f"Checking {base_url}/dashboard/stats...")
            resp = await client.get(f"{base_url}/dashboard/stats")
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Response:", resp.json())
            else:
                print("Error:", resp.text)

            print(f"\nChecking {base_url}/dashboard/trend?days=7...")
            resp = await client.get(f"{base_url}/dashboard/trend?days=7")
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Response:", resp.json())
            else:
                print("Error:", resp.text)
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(verify_dashboard())
