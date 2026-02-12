import asyncio
import uuid
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.pyramid import Pyramid, PyramidNode
from app.models.approval import Approval
from app.database import Base

BASE_URL = "http://localhost:8000/api/v1"

async def test_node_move():
    print("\n--- Testing Node Move ---", flush=True)
    async with httpx.AsyncClient(base_url=BASE_URL, follow_redirects=True) as client:
        # 1. Create Pyramid
        print("Creating Pyramid...", flush=True)
        res = await client.post("/pyramids", json={"name": "Move Test Pyramid"}) # Removed slash
        if res.status_code != 201:
            print(f"Error: {res.text}")
        assert res.status_code == 201
        pyramid_id = res.json()["data"]["id"]
        print(f"Pyramid Created: {pyramid_id}", flush=True)

        # 2. Create Root Nodes A and B
        print("Creating Nodes A and B...", flush=True)
        res = await client.post(f"/pyramids/{pyramid_id}/nodes", json={"name": "Node A"})
        node_a_id = res.json()["data"]["id"]
        
        res = await client.post(f"/pyramids/{pyramid_id}/nodes", json={"name": "Node B"})
        node_b_id = res.json()["data"]["id"]
        print(f"Nodes Created: A={node_a_id}, B={node_b_id}", flush=True)

        # 3. Move B under A
        print("Moving B under A...", flush=True)
        res = await client.post(f"/nodes/{node_b_id}/move", json={"new_parent_id": node_a_id})
        if res.status_code != 200:
            print(f"Error moving node: {res.text}")
        assert res.status_code == 200
        node_b = res.json()["data"]
        print(f"Node B Moved: parent_id={node_b['parent_id']}, path={node_b['path']}", flush=True)
        
        assert node_b['parent_id'] == node_a_id
        assert node_b['level'] == 1
        
        # 4. Move B back to Root
        print("Moving B back to Root...", flush=True)
        res = await client.post(f"/nodes/{node_b_id}/move", json={"new_parent_id": None})
        assert res.status_code == 200
        node_b = res.json()["data"]
        print(f"Node B Moved back: parent_id={node_b['parent_id']}", flush=True)
        assert node_b['parent_id'] is None

async def test_approval():
    print("\n--- Testing Approval ---", flush=True)
    async with httpx.AsyncClient(base_url=BASE_URL, follow_redirects=True) as client:
        # 1. Create Approval
        print("Creating Approval...", flush=True)
        payload = {
            "type": "create_node",
            "data": {"name": "Proposed Node"},
            "applicant_id": "user_123"
        }
        res = await client.post("/approvals", json=payload) # Removed slash
        if res.status_code != 201:
            print(f"Error creating approval: {res.text}")
        assert res.status_code == 201
        approval_id = res.json()["data"]["id"]
        print(f"Approval Created: {approval_id}", flush=True)

        # 2. List Pending
        print("Listing Pending Approvals...", flush=True)
        res = await client.get("/approvals/pending")
        assert res.status_code == 200
        items = res.json()["data"]
        assert any(item["id"] == approval_id for item in items)
        print(f"Found {len(items)} pending approvals", flush=True)

        # 3. Review (Approve)
        print("Reviewing Approval...", flush=True)
        review_payload = {
            "status": "approved",
            "reviewer_id": "admin",
            "review_comment": "LGTM"
        }
        res = await client.post(f"/approvals/{approval_id}/review", json=review_payload)
        assert res.status_code == 200
        approval = res.json()["data"]
        assert approval["status"] == "approved"
        print(f"Approval Reviewed: {approval['status']}", flush=True)


async def main():
    try:
        # Ensure server is running or we can test via service layer directly?
        # Since we modified routers, testing via API is better.
        # Assuming the user has the server running or I can run it in background.
        # But wait, I cannot easily run server in background and test in same turn without `RunCommand` blocking=false.
        # I'll use `RunCommand` to start server in background first.
        
        await test_node_move()
        await test_approval()
        print("\n✅ All Reinforcement Tests Passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
