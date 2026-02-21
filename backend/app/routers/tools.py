from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.schemas.tools import DouyinConvertRequest, DouyinConvertResponse
from app.services.douyin_service import douyin_service
import logging

router = APIRouter(
    prefix="/tools",
    tags=["tools"]
)

logger = logging.getLogger(__name__)

@router.post("/douyin/stream")
async def stream_douyin_video(request: DouyinConvertRequest):
    """
    Stream conversion progress for Douyin video.
    """
    async def event_generator():
        try:
            async for event in douyin_service.convert_stream(request.url, request.cookies):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/douyin/convert", response_model=DouyinConvertResponse)
async def convert_douyin_video(request: DouyinConvertRequest):
    """
    Convert Douyin video to Markdown document.
    """
    try:
        return await douyin_service.convert(request.url, request.cookies)
    except Exception as e:
        logger.error(f"Failed to convert Douyin video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
