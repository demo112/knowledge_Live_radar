
import pytest
from app.services.pyramid_service import PyramidService
from app.services.template_service import TemplateService
from app.models.pyramid import PyramidNode

@pytest.mark.asyncio
async def test_property_16_template_instantiation(db_session):
    """Property 16: 模板实例化完整性"""
    pyramid_service = PyramidService(db_session)
    template_service = TemplateService(pyramid_service)
    
    # 1. Get Templates
    templates = template_service.get_templates()
    assert len(templates) >= 2
    
    ids = [t["id"] for t in templates]
    assert "diwta" in ids
    assert "bloom" in ids
    
    # 2. Instantiate each
    for tpl in templates:
        pyramid = await template_service.create_from_template(tpl["id"], name_override=f"My {tpl['name']}")
        
        assert pyramid.name == f"My {tpl['name']}"
        assert pyramid.description == tpl["description"]
        
        # Verify structure
        details = await pyramid_service.get_pyramid_details(pyramid.id)
        
        if tpl["id"] == "diwta":
            # 5 levels
            assert len(details.nodes) == 5
            # Verify hierarchy (simple check: one node per level)
            levels = [n.level for n in details.nodes]
            assert sorted(levels) == [0, 1, 2, 3, 4]
            
        elif tpl["id"] == "bloom":
            # 6 levels
            assert len(details.nodes) == 6
            levels = [n.level for n in details.nodes]
            assert sorted(levels) == [0, 1, 2, 3, 4, 5]
            
@pytest.mark.asyncio
async def test_template_invalid_id(db_session):
    pyramid_service = PyramidService(db_session)
    template_service = TemplateService(pyramid_service)
    
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        await template_service.create_from_template("invalid_id")
