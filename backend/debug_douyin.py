import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.douyin_service import DouyinService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_douyin_service():
    service = DouyinService()
    url = "https://www.douyin.com/video/7434563884323261735"
    
    logger.info(f"Testing DouyinService with URL: {url}")
    
    try:
        async for event in service.convert_stream(url):
            logger.info(f"Event: {event}")
            if event['stage'] == 'completed':
                logger.info("Conversion completed successfully!")
                break
            if event['stage'] == 'error':
                logger.error(f"Conversion failed: {event['message']}")
                break
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_douyin_service())
