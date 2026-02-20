import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.template_service import TemplateService
from app.services.pyramid_service import PyramidService

@pytest.fixture
def mock_pyramid_service():
    return AsyncMock(spec=PyramidService)

@pytest.fixture
def template_service(mock_pyramid_service):
    return TemplateService(mock_pyramid_service)

@pytest.mark.asyncio
async def test_get_templates(template_service):
    mock_templates = {
        "template1": {"name": "Template 1", "description": "Desc 1"},
        "template2": {"name": "Template 2", "description": "Desc 2"}
    }
    
    with patch("app.services.template_service.prompt_loader.get_prompt", new_callable=AsyncMock) as mock_get_prompt:
        mock_get_prompt.return_value = json.dumps(mock_templates)
        
        templates = await template_service.get_templates()
        
        assert len(templates) == 2
        assert templates[0]["id"] in ["template1", "template2"]
        assert templates[0]["name"] in ["Template 1", "Template 2"]

@pytest.mark.asyncio
async def test_create_from_template(template_service, mock_pyramid_service):
    mock_templates = {
        "template1": {
            "name": "Template 1",
            "description": "Desc 1",
            "nodes": [
                {"title": "Node 1", "description": "Node Desc 1", "children": []}
            ]
        }
    }
    
    mock_pyramid = MagicMock()
    mock_pyramid.id = "pyramid-id"
    mock_pyramid_service.create_pyramid.return_value = mock_pyramid
    
    mock_node = MagicMock()
    mock_node.id = "node-id"
    mock_pyramid_service.add_node.return_value = mock_node
    
    with patch("app.services.template_service.prompt_loader.get_prompt", new_callable=AsyncMock) as mock_get_prompt:
        mock_get_prompt.return_value = json.dumps(mock_templates)
        
        await template_service.create_from_template("template1")
        
        mock_pyramid_service.create_pyramid.assert_called_once()
        mock_pyramid_service.add_node.assert_called_once()
