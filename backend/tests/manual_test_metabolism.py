import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_metabolism():
    print("Testing Content Metabolism API...")

    # 1. Trigger Run
    print("\n1. Triggering Metabolism Run...")
    try:
        response = requests.post(f"{BASE_URL}/content-management/metabolism/run")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error triggering run: {e}")

    # 2. Get Suggestions
    print("\n2. Getting Cleanup Suggestions...")
    try:
        response = requests.get(f"{BASE_URL}/content-management/metabolism/suggestions")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error getting suggestions: {e}")

if __name__ == "__main__":
    test_metabolism()
