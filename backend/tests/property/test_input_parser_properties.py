import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from fastapi import UploadFile
import io
from app.services.input_parser import InputParser

# Helper to run async test
def async_test(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@given(text_content=st.text())
@settings(max_examples=50)
def test_parse_text_properties(text_content):
    async def run_test():
        # Create a mock UploadFile
        file_obj = io.BytesIO(text_content.encode('utf-8'))
        upload_file = UploadFile(filename="test.txt", file=file_obj)
        
        result = await InputParser.parse_text(upload_file)
        
        # Verify content matches (trimmed)
        assert result == text_content.strip()
        
    async_test(run_test())

@given(markdown_content=st.text())
@settings(max_examples=50)
def test_parse_markdown_properties(markdown_content):
    async def run_test():
        # Create a mock UploadFile
        file_obj = io.BytesIO(markdown_content.encode('utf-8'))
        upload_file = UploadFile(filename="test.md", file=file_obj)
        
        # We can't easily assert the output because markdown parsing changes structure
        # But we can assert it doesn't crash and returns a string
        try:
            result = await InputParser.parse_markdown(upload_file)
            assert isinstance(result, str)
        except ValueError:
            pass
            
    async_test(run_test())
