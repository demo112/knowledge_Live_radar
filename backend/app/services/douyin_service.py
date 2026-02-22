import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Tuple, Optional
from yt_dlp import YoutubeDL
from app.core.ai.client import ai_client
from app.schemas.tools import DouyinConvertResponse, DouyinVideoInfo, DouyinContent

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class DouyinService:
    @staticmethod
    def extract_url(text: str) -> str:
        import re
        # Pattern for v.douyin.com short links and www.douyin.com full links
        # Updated to be more robust for full links
        url_pattern = r'(https?://v\.douyin\.com/[a-zA-Z0-9]+/?|https?://www\.douyin\.com/[a-zA-Z0-9/]+)'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)
        return text.strip()

    async def _fetch_info_with_playwright(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            logger.info("Attempting to fetch cookies and video URL using Playwright...")
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=USER_AGENT,
                    viewport={'width': 1920, 'height': 1080},
                    device_scale_factor=1,
                )
                
                # Add stealth scripts to avoid detection
                await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                page = await context.new_page()
                
                real_video_url = None
                
                # Listen for video responses to capture direct URL
                async def handle_response(response):
                    nonlocal real_video_url
                    try:
                        content_type = response.headers.get('content-type', '').lower()
                        # Log all potential media types
                        if 'video' in content_type or 'application/vnd.apple.mpegurl' in content_type or 'audio' in content_type:
                            logger.info(f"Media response detected: {response.url[:100]}... Type: {content_type} Size: {response.headers.get('content-length')}")
                            
                            content_length = int(response.headers.get('content-length', 0))
                            # Capture the largest video file found so far
                            if 'video' in content_type:
                                # Update if this is larger than previous or no previous
                                # Douyin videos are usually mp4 and > 1MB
                                if content_length > 1024 * 1024: 
                                    real_video_url = response.url
                                    logger.info(f"Found candidate video URL (Large): {real_video_url[:100]}...")
                                elif not real_video_url and content_length > 0:
                                    # Fallback to any video if we haven't found a large one yet
                                    real_video_url = response.url
                                    logger.info(f"Found candidate video URL (Small): {real_video_url[:100]}...")
                                    
                    except Exception as e:
                        pass

                page.on("response", handle_response)
                
                logger.info(f"Navigating to {url}...")
                try:
                    await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                    
                    # Try to close login modal if it appears
                    try:
                        await page.click('.dy-account-close', timeout=2000)
                    except:
                        pass
                        
                    # Wait for video element
                    try:
                        # Try multiple selectors, wait for attached (even if hidden)
                        video_handle = await page.wait_for_selector('video', state='attached', timeout=5000)
                        if video_handle:
                            logger.info("Video element found (attached)!")
                            # Get src attribute
                            src = await video_handle.get_attribute('src')
                            logger.info(f"Video src attribute: {src[:100] if src else 'None'}")
                            
                            if not src:
                                # Try currentSrc property
                                src = await page.evaluate("document.querySelector('video').currentSrc")
                                logger.info(f"Video currentSrc property: {src[:100] if src else 'None'}")
                            
                            # If src is a real URL (not blob), use it as fallback
                            if src and src.startswith('http'):
                                if not real_video_url or 'uuu_265' in real_video_url:
                                    real_video_url = src
                                    logger.info(f"Using video src as fallback URL: {real_video_url[:100]}...")
                            
                            # Try to ensure it plays to trigger network request
                            try:
                                await page.evaluate("document.querySelector('video').play()")
                            except:
                                pass
                    except Exception as e:
                        logger.warning(f"Video element detection failed: {e}")
                        
                    # Scroll down to trigger loading
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    # Wait a bit for potential redirects and media loading
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.warning(f"Page load timeout or error: {e}, but continuing to check cookies")

                # Get cookies
                cookies = await context.cookies()
                
                # Try to extract video URL from page content (SSR data)
                try:
                    content = await page.content()
                    # Look for encoded URLs first (often in JSON)
                    import re
                    # Common pattern for video address in Douyin SSR data
                    # "play_addr":{"url_list":["https://..."]}
                    # or just "src":"..."
                    
                    # Try to find play_addr pattern
                    play_addr_matches = re.findall(r'"play_addr":\{"url_list":\["(https:[^"]+)"', content)
                    if play_addr_matches:
                        for match in play_addr_matches:
                            # Douyin often escapes slashes
                            candidate = match.replace('\\u002F', '/').replace('\\', '')
                            if 'video' in candidate or 'aweme' in candidate:
                                real_video_url = candidate
                                logger.info(f"Found video URL in SSR data: {real_video_url[:100]}...")
                                break
                    
                    if not real_video_url:
                        # Try broader search for large video files
                        # Look for mp4 URLs
                        mp4_matches = re.findall(r'https?://[^\s"\'<>]+\.mp4', content)
                        for match in mp4_matches:
                            if 'uuu_265' in match: continue # Skip placeholder
                            if 'douyinstatic' in match: continue # Skip static assets
                            
                            real_video_url = match
                            logger.info(f"Found mp4 URL in HTML: {real_video_url[:100]}...")
                            break
                            
                except Exception as e:
                    logger.warning(f"Failed to extract from HTML: {e}")

                await browser.close()
                
                if not cookies:
                    logger.warning("No cookies fetched")
                    return None, None
                
                # Format as Netscape cookie file content
                netscape_content = "# Netscape HTTP Cookie File\n"
                # domain flag path secure expiration name value
                for cookie in cookies:
                    domain = cookie['domain']
                    flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                    path = cookie['path']
                    secure = 'TRUE' if cookie['secure'] else 'FALSE'
                    expiration = int(cookie['expires']) if 'expires' in cookie and cookie['expires'] != -1 else 0
                    name = cookie['name']
                    value = cookie['value']
                    netscape_content += f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n"
                
                logger.info(f"Fetched {len(cookies)} cookies")
                return netscape_content, real_video_url
                
        except ImportError:
            logger.error("Playwright not installed. Cannot fetch cookies automatically.")
            return None, None
        except Exception as e:
            logger.error(f"Failed to fetch info with Playwright: {e}")
            return None, None

    async def convert_stream(self, url: str, cookies: Optional[str] = None):
        # Extract URL if input contains text
        url = self.extract_url(url)
        logger.info(f"Processing Douyin URL: {url}")
        
        real_video_url = None

        # 0. Fetch cookies if not provided
        if not cookies:
            yield {"stage": "preparing", "progress": 5, "message": "正在尝试自动获取Cookies..."}
            cookies, real_video_url = await self._fetch_info_with_playwright(url)
            if cookies:
                yield {"stage": "preparing", "progress": 8, "message": "获取Cookies成功"}
            else:
                yield {"stage": "preparing", "progress": 8, "message": "自动获取Cookies失败，尝试直接下载..."}

        # 1. Download Video/Audio
        yield {"stage": "downloading", "progress": 10, "message": "正在下载视频..."}
        video_path = None
        cookie_path = None
        info = {}
        
        # Configure yt-dlp
        # Use a temporary directory for downloads
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        ydl_opts = {
            'format': 'best', # Download best format available (usually mp4 for Douyin), avoids ffmpeg merge dependency
            'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'windowsfilenames': True,
            'http_headers': {
                'User-Agent': USER_AGENT
            }
        }

        if cookies:
            try:
                # Check if it looks like Netscape format (contains tabs or # Netscape)
                if "# Netscape" in cookies or "\t" in cookies:
                    # Create a temporary cookie file
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                        f.write(cookies)
                        cookie_path = f.name
                    ydl_opts['cookiefile'] = cookie_path
                    logger.info(f"Using provided cookies from file: {cookie_path}")
                else:
                    # Assume it's a cookie header string (key=value; ...)
                    if 'http_headers' not in ydl_opts:
                        ydl_opts['http_headers'] = {}
                    
                    ydl_opts['http_headers']['Cookie'] = cookies.strip()
                    logger.info("Using provided cookies as HTTP header")
            except Exception as e:
                logger.error(f"Failed to process cookies: {e}")
        
        try:
            # Run blocking yt-dlp in executor
            loop = asyncio.get_event_loop()
            try:
                info, video_path = await loop.run_in_executor(None, self._download, url, ydl_opts)
            except Exception as e:
                logger.warning(f"Download from original URL failed: {e}")
                if real_video_url:
                    logger.info(f"Trying fallback to direct video URL: {real_video_url[:100]}...")
                    yield {"stage": "downloading", "progress": 15, "message": "尝试使用直接链接下载..."}
                    # For direct URL, we might need to relax some checks or options if needed, 
                    # but usually same options work.
                    info, video_path = await loop.run_in_executor(None, self._download, real_video_url, ydl_opts)
                    # If info is missing title etc, we might want to use a default
                    if 'title' not in info:
                        info['title'] = f"Douyin Video {os.path.basename(video_path)}"
                else:
                    raise e
            
            if not video_path or not os.path.exists(video_path):
                raise RuntimeError("Failed to download video file")
            
            logger.info(f"Downloaded to {video_path}")
            
            # 2. Transcribe Audio
            yield {"stage": "transcribing", "progress": 40, "message": "正在转录音频..."}
            transcription = await ai_client.audio_transcriptions(video_path)
            
            if not transcription:
                logger.warning("Transcription returned empty text")
                transcription = ""
            
            # 3. Summarize and Extract Key Points
            yield {"stage": "analyzing", "progress": 70, "message": "正在整理内容..."}
            content = await self._analyze_content(transcription, info)
            
            # 4. Generate Markdown
            yield {"stage": "generating", "progress": 90, "message": "正在生成文档..."}
            markdown = self._generate_markdown(info, content)
            
            # 5. Construct Response
            response = DouyinConvertResponse(
                video_info=DouyinVideoInfo(
                    title=info.get('title', 'Unknown'),
                    author=info.get('uploader', 'Unknown'),
                    duration=info.get('duration', 0) or 0,
                    cover_url=info.get('thumbnail'),
                    url=info.get('webpage_url')
                ),
                content=content,
                markdown=markdown
            )
            
            yield {"stage": "completed", "progress": 100, "data": response.model_dump()}
            
        except Exception as e:
            logger.error(f"Error in convert_stream: {e}")
            yield {"stage": "error", "message": str(e)}
            raise e
            
        finally:
            # Cleanup
            logger.info(f"Finally block reached. video_path={video_path}, exists={os.path.exists(video_path) if video_path else 'None'}")
            if video_path and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    logger.info(f"Removed temp file: {video_path}")
                except Exception as e:
                    logger.error(f"Failed to remove temp file: {e}")
            
            if cookie_path and os.path.exists(cookie_path):
                try:
                    os.remove(cookie_path)
                    logger.info(f"Removed cookie file: {cookie_path}")
                except Exception as e:
                    logger.error(f"Failed to remove cookie file: {e}")

    async def convert(self, url: str, cookies: Optional[str] = None) -> DouyinConvertResponse:
        # Backward compatibility or non-streaming usage
        result = None
        async for event in self.convert_stream(url, cookies):
            if event["stage"] == "completed":
                return DouyinConvertResponse(**event["data"])
        raise RuntimeError("Conversion failed without completion")

    def _download(self, url: str, opts: Dict) -> Tuple[Dict, str]:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return info, filename

    async def _analyze_content(self, text: str, info: Dict) -> DouyinContent:
        prompt = f"""
        你是一个专业的内容整理助手。请根据以下视频转录文本，生成一份结构化的笔记。
        
        视频标题: {info.get('title')}
        作者: {info.get('uploader')}
        
        转录文本:
        {text[:10000]}
        
        请输出 JSON 格式，包含以下字段:
        - summary: 简短摘要 (200字以内)
        - key_points: 关键点列表 (3-5个)
        - full_text: 整理后的全文 (润色口语，使其更通顺)
        """
        
        messages = [
            {"role": "system", "content": "你是一个有用的助手，只输出 JSON。"},
            {"role": "user", "content": prompt}
        ]
        
        # Use cloud model for better summarization
        response_text = await ai_client.chat_completion(
            messages, 
            model="deepseek-ai/DeepSeek-V3", 
            response_format={"type": "json_object"}
        )
        
        if not response_text:
             return DouyinContent(
                summary="生成失败",
                key_points=[],
                full_text=text
            )
            
        try:
            # Try to parse JSON
            # ai_client has parse_json method? Yes, based on reading client.py earlier.
            # But wait, is it exposed? Yes, define inside class.
            if hasattr(ai_client, 'parse_json'):
                data = ai_client.parse_json(response_text)
            else:
                # Fallback if method not available/exposed
                try:
                    data = json.loads(response_text)
                except:
                    # Simple extraction fallback
                    data = {}

            return DouyinContent(
                summary=data.get("summary", ""),
                key_points=data.get("key_points", []),
                full_text=data.get("full_text", text)
            )
        except Exception as e:
            logger.error(f"Failed to parse analysis result: {e}")
            return DouyinContent(
                summary="无法生成摘要",
                key_points=[],
                full_text=text
            )

    def _generate_markdown(self, info: Dict, content: DouyinContent) -> str:
        md = f"# {info.get('title')}\n\n"
        md += f"**作者**: {info.get('uploader')}  \n"
        md += f"**时长**: {info.get('duration')}秒  \n"
        md += f"**原始链接**: {info.get('webpage_url')}\n\n"
        
        if info.get('thumbnail'):
            md += f"![封面]({info.get('thumbnail')})\n\n"
            
        md += "## 摘要\n\n"
        md += f"{content.summary}\n\n"
        
        md += "## 关键点\n\n"
        for point in content.key_points:
            md += f"- {point}\n"
        md += "\n"
            
        md += "## 全文内容\n\n"
        md += f"{content.full_text}\n"
        
        return md

douyin_service = DouyinService()
