import os
import yaml
import logging
from pathlib import Path
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class PromptLoader:
    def __init__(self, prompt_dir: str = "app/prompts"):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.prompt_dir = base_dir / prompt_dir

    async def load_initial_prompts(self):
        """从 prompt_dir 加载所有提示词 yaml 文件并同步到数据库。"""
        if not self.prompt_dir.exists():
            logger.warning(f"Prompt directory not found: {self.prompt_dir}")
            return

        logger.info(f"Loading prompts from {self.prompt_dir}")
        
        for file_path in self.prompt_dir.glob("*.yaml"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    
                scene = data.get("scene")
                if not scene:
                    logger.warning(f"Skipping {file_path.name}: 'scene' not defined")
                    continue
                
                logger.info(f"Loaded prompt template: {scene}")
                
            except Exception as e:
                logger.error(f"Failed to load prompt from {file_path.name}: {e}")

prompt_loader_service = PromptLoader()
