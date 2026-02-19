import os
import yaml
import logging
from typing import Dict, Any, Tuple, Optional
from jinja2 import Template

logger = logging.getLogger(__name__)

class PromptLoader:
    def __init__(self):
        # Calculate project root relative to this file
        # This file is located at: backend/app/core/ai/prompt_loader.py
        # We need to go up 4 levels to reach the project root:
        # ai -> core -> app -> backend -> project_root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
        self.prompts_dir = os.path.join(project_root, "prompts")
        
        if not os.path.exists(self.prompts_dir):
            # Fallback: Try looking in CWD (useful for Docker or different execution contexts)
            cwd_prompts = os.path.join(os.getcwd(), "prompts")
            if os.path.exists(cwd_prompts):
                self.prompts_dir = cwd_prompts
            else:
                # Fallback: Try looking in ../prompts (if CWD is backend/)
                parent_prompts = os.path.join(os.path.dirname(os.getcwd()), "prompts")
                if os.path.exists(parent_prompts):
                    self.prompts_dir = parent_prompts
                else:
                    logger.error(f"Prompts directory not found. Expected at: {self.prompts_dir}")

    def load_prompt(self, prompt_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Load a prompt file by name.
        Returns: (metadata, content_template)
        """
        file_path = os.path.join(self.prompts_dir, f"{prompt_name}.md")
        
        if not os.path.exists(file_path):
            logger.error(f"Prompt file not found: {file_path}")
            return None, None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse Frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1]
                    body = parts[2].strip()
                    try:
                        metadata = yaml.safe_load(frontmatter_str)
                    except yaml.YAMLError as e:
                        logger.error(f"Failed to parse YAML frontmatter in {prompt_name}: {e}")
                        return None, None
                    return metadata, body
            
            # No frontmatter or invalid format
            return {}, content.strip()

        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {e}")
            return None, None

    def render_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Load and render a prompt with variables.
        Returns: (rendered_content, metadata)
        """
        metadata, template_str = self.load_prompt(prompt_name)
        
        if template_str is None:
            return None, None

        try:
            template = Template(template_str)
            rendered = template.render(**variables)
            return rendered, metadata
        except Exception as e:
            logger.error(f"Error rendering prompt {prompt_name}: {e}")
            return None, metadata

prompt_loader = PromptLoader()
