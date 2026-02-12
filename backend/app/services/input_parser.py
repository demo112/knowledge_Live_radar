import io
import logging
from typing import Optional
from fastapi import UploadFile
from pypdf import PdfReader
import docx
import markdown
from bs4 import BeautifulSoup

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
            # Convert MD to HTML then to text to strip tags
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
        # Placeholder for OCR
        # In a real implementation, we would call an OCR service or use pytesseract.
        logger.warning("OCR parsing not yet implemented")
        return "[OCR Content Placeholder - Image parsing requires external service]"
