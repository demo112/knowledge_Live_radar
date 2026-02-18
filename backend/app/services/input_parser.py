import io
import logging
import base64
from typing import Optional
from fastapi import UploadFile
from pypdf import PdfReader
import docx
import markdown
from bs4 import BeautifulSoup
from app.core.ai.client import ai_client

logger = logging.getLogger(__name__)

class InputParser:
    @staticmethod
    async def parse_pdf(file: UploadFile) -> str:
        try:
            content = await file.read()
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        finally:
            await file.seek(0)

    @staticmethod
    async def parse_docx(file: UploadFile) -> str:
        try:
            content = await file.read()
            docx_file = io.BytesIO(content)
            doc = docx.Document(docx_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
        finally:
            await file.seek(0)

    @staticmethod
    async def parse_markdown(file: UploadFile) -> str:
        try:
            content = await file.read()
            text = content.decode("utf-8")
            html = markdown.markdown(text)
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()
        except Exception as e:
            logger.error(f"Error parsing Markdown: {e}")
            raise ValueError(f"Failed to parse Markdown: {str(e)}")
        finally:
            await file.seek(0)

    @staticmethod
    async def parse_text(file: UploadFile) -> str:
        try:
            content = await file.read()
            return content.decode("utf-8").strip()
        except Exception as e:
            logger.error(f"Error parsing Text: {e}")
            raise ValueError(f"Failed to parse Text: {str(e)}")
        finally:
            await file.seek(0)
            
    @staticmethod
    async def parse_image(file: UploadFile) -> str:
        try:
            content = await file.read()
            base64_image = base64.b64encode(content).decode('utf-8')
            
            mime_type = "image/jpeg"
            if file.content_type:
                mime_type = file.content_type
            elif file.filename:
                ext = file.filename.lower().split('.')[-1]
                if ext == 'png':
                    mime_type = "image/png"
                elif ext in ['jpg', 'jpeg']:
                    mime_type = "image/jpeg"
                elif ext == 'webp':
                    mime_type = "image/webp"
            
            prompt = "请提取这张图片中的所有文字内容。直接输出文字，不要包含任何解释或Markdown格式。"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            result = await ai_client.chat_completion(messages)
            return result if result else "[OCR Failed: No response from AI]"
            
        except Exception as e:
            logger.error(f"Error parsing Image: {e}")
            raise ValueError(f"Failed to parse Image: {str(e)}")
        finally:
            await file.seek(0)
