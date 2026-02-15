
import asyncio
import uuid
from datetime import datetime
from app.models.content import ContentItem
from app.schemas.content import ContentResponse

def test_schema_validation():
    # Simulate the ContentItem returned by process_text_input
    item = ContentItem(
        id=uuid.uuid4(),
        title="Test Title",
        url="text://manual-input",
        content_text="Test content",
        submitter_id="user123",
        input_type="text",
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        ai_processed=False,
        is_deleted=False,
        tags=None,
        concepts=None,
        summary=None,
        publish_time=None,
        content_hash=None,
        validation_result=None # Simulate relationship being None
    )
    
    try:
        # Validate against schema
        model = ContentResponse.model_validate(item)
        print("Validation Successful")
        print(model.model_dump())
    except Exception as e:
        print("Validation Failed")
        print(e)

if __name__ == "__main__":
    test_schema_validation()
