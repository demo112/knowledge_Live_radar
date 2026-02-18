import asyncio
import sys
import os
from pprint import pprint

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.fetchers.firecrawl_fetcher import FirecrawlFetcher

async def main():
    print("Initializing FirecrawlFetcher...")
    fetcher = FirecrawlFetcher()
    
    url = "https://example.com"
    print(f"Fetching URL: {url}")
    
    try:
        # Validate source first
        is_valid = await fetcher.validate_source(url)
        print(f"Source validation result: {is_valid}")
        
        if is_valid:
            print("Source is valid, proceeding with fetch...")
            results = await fetcher.fetch(url)
            print(f"Fetch completed. Received {len(results)} items.")
            for item in results:
                print("\n--- Item Metadata ---")
                pprint(item.get("metadata", {}))
                print("\n--- Item Content Preview (first 200 chars) ---")
                print(item.get("markdown", "")[:200])
        else:
            print("Source validation failed.")
            
    except Exception as e:
        print(f"Error during fetch: {e}")

if __name__ == "__main__":
    asyncio.run(main())
