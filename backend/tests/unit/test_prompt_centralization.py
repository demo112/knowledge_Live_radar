import pytest
import os
import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"

def get_all_prompt_files():
    if not PROMPTS_DIR.exists():
        return []
    return list(PROMPTS_DIR.rglob("*.md"))

@pytest.mark.parametrize("prompt_file", get_all_prompt_files())
def test_prompt_file_structure(prompt_file):
    """
    Verify that every .md file in prompts/ directory:
    1. Starts with YAML frontmatter (---)
    2. Has valid YAML frontmatter
    3. Has content after frontmatter
    """
    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check frontmatter existence
    assert content.startswith("---"), f"{prompt_file.name} must start with YAML frontmatter (---)"
    
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{prompt_file.name} must have valid frontmatter delimiters"
    
    # Check YAML validity
    frontmatter_str = parts[1]
    try:
        metadata = yaml.safe_load(frontmatter_str)
        assert isinstance(metadata, dict), f"{prompt_file.name} frontmatter must be a dictionary"
    except yaml.YAMLError as e:
        pytest.fail(f"{prompt_file.name} has invalid YAML frontmatter: {e}")
    
    # Check content existence
    body = parts[2].strip()
    assert len(body) > 0, f"{prompt_file.name} must have content body"

def test_prompts_directory_exists():
    assert PROMPTS_DIR.exists(), "prompts directory must exist at project root"
    assert PROMPTS_DIR.is_dir(), "prompts must be a directory"

def test_required_prompts_exist():
    """Verify that critical prompts referenced in code exist"""
    required_prompts = [
        "content/batch_analysis.md",
        "content/image_ocr.md",
        "content/concept_extraction.md",
        "content/summary_generation.md",
        "content/tag_generation.md",
        "validation/soft.md",
        "system/connectivity_test.md",
        "pyramid/templates.md"
    ]
    
    for rel_path in required_prompts:
        prompt_path = PROMPTS_DIR / rel_path
        assert prompt_path.exists(), f"Required prompt {rel_path} is missing"
