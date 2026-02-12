import pytest
import pytest_asyncio
from app.services.template_service import TemplateService
from app.services.pyramid_service import PyramidService
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_property_16_template_integrity(db_session):
    """Property 16: 模板实例化完整性 (Template Instantiation Integrity)"""
    pyramid_service = PyramidService(db_session)
    template_service = TemplateService(pyramid_service)
    
    # 1. Get Templates
    templates = template_service.get_templates()
    assert len(templates) > 0
    template_id = templates[0]["id"]
    
    # 2. Create from Template
    pyramid = await template_service.create_from_template(template_id, name_override="Template Test")
    
    # 3. Verify Pyramid
    assert pyramid.name == "Template Test"
    
    # 4. Verify Nodes Structure
    # Since we can't easily traverse the tree without fetching details, let's fetch details
    details = await pyramid_service.get_pyramid_details(pyramid.id)
    
    # Check if nodes were created
    assert len(details.nodes) > 0
    
    # Check hierarchy levels exist
    levels = set(n.level for n in details.nodes)
    assert len(levels) >= 2 # Assuming templates have at least 2 levels
    
    # Verify non-existent template raises error
    with pytest.raises(HTTPException) as exc:
        await template_service.create_from_template("non_existent")
    assert exc.value.status_code == 404
