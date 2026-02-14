import pytest
from app.services.source_template_service import SourceTemplateService

def test_get_templates():
    service = SourceTemplateService()
    templates = service.get_templates()
    assert len(templates) >= 4
    
    ids = [t.id for t in templates]
    assert "arxiv_rss" in ids
    assert "github_trending" in ids
    assert "huggingface_daily" in ids
    assert "blog_rss" in ids

def test_generate_config_arxiv():
    service = SourceTemplateService()
    config = service.generate_source_config("arxiv_rss", {"category": "cs.CV"})
    
    assert config["type"] == "RSS"
    assert config["url"] == "http://export.arxiv.org/rss/cs.CV"
    assert config["name"] == "arXiv cs.CV"

def test_generate_config_github():
    service = SourceTemplateService()
    config = service.generate_source_config("github_trending", {"language": "rust", "since": "weekly"})
    
    assert config["type"] == "API"
    assert "rust" in config["url"]
    assert config["name"] == "GitHub Trending (rust)"

def test_generate_config_blog_rss():
    service = SourceTemplateService()
    url = "https://example.com/feed.xml"
    config = service.generate_source_config("blog_rss", {"rss_url": url})
    
    assert config["type"] == "RSS"
    assert config["url"] == url
    assert "example.com" in config["name"]

def test_generate_config_invalid_template():
    service = SourceTemplateService()
    with pytest.raises(ValueError):
        service.generate_source_config("invalid_id", {})

def test_generate_config_missing_param():
    service = SourceTemplateService()
    with pytest.raises(ValueError):
        service.generate_source_config("blog_rss", {}) # Missing rss_url
