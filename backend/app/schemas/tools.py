from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class DouyinConvertRequest(BaseModel):
    url: str = Field(..., description="抖音视频分享链接")
    cookies: Optional[str] = Field(None, description="Cookies (Netscape format)")

class DouyinVideoInfo(BaseModel):
    title: str = Field(..., description="视频标题")
    author: str = Field(..., description="作者")
    duration: int = Field(..., description="时长(秒)")
    cover_url: Optional[str] = Field(None, description="封面URL")
    url: Optional[str] = Field(None, description="原始URL")

class DouyinContent(BaseModel):
    summary: str = Field(..., description="摘要")
    key_points: List[str] = Field(..., description="关键点")
    full_text: str = Field(..., description="全文内容")

class DouyinConvertResponse(BaseModel):
    video_info: DouyinVideoInfo
    content: DouyinContent
    markdown: str = Field(..., description="完整的Markdown文档")
