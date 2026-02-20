import logging
from typing import List, Dict, Any, Optional
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)


class EnhancementProcessor:
    async def validate_content_soft(self, title: str, content: str) -> Dict[str, Any]:
        prompt_name = "validation/soft"
        variables = {
            "title": title,
            "content": content[:3000]
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            logger.error(f"Failed to load prompt: {prompt_name}")
            return {"score": 0, "reason": "系统错误：提示词缺失"}
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.1, context="soft_validation")
        
        if not response_text:
            return {"score": 0, "reason": "AI 服务失败"}
        
        result = ai_client.parse_json(response_text)
        if "score" not in result:
            result["score"] = 0
            result["reason"] = result.get("reason", "无法解析 AI 评分")
        
        return result

    async def generate_summary(self, title: str, content: str) -> Dict[str, Any]:
        prompt_name = "content/summary_generation"
        variables = {
            "title": title,
            "content": content[:3000]
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return {"summary": "", "key_points": []}
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.3, context="summary_generation")
        
        if not response_text:
            return {"summary": "", "key_points": []}
        
        result = ai_client.parse_json(response_text)
        
        if not result and response_text:
            return {"summary": response_text.strip(), "key_points": []}
        
        return result

    async def extract_concepts(self, title: str, content: str) -> List[Dict[str, str]]:
        prompt_name = "content/concept_extraction"
        variables = {
            "title": title,
            "content": content[:10000]
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return []
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.1, context="concept_extraction")
        
        result = ai_client.parse_json(response_text) if response_text else {}
        return result.get("concepts", [])

    async def generate_tags(self, title: str, content: str) -> List[str]:
        prompt_name = "content/tag_generation"
        variables = {
            "title": title,
            "content": content[:3000]
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return []
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.3, context="tag_generation")
        
        result = ai_client.parse_json(response_text) if response_text else {}
        return result.get("tags", [])

    async def check_drift(
        self,
        concept_name: str,
        concept_description: str,
        old_content: str,
        new_content: str,
        old_days: int = 30,
        new_days: int = 7
    ) -> Dict[str, Any]:
        prompt_name = "analysis/drift_detection"
        variables = {
            "concept_name": concept_name,
            "concept_description": concept_description or "无",
            "old_content": old_content,
            "new_content": new_content,
            "old_days": old_days,
            "new_days": new_days
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return {"drift_detected": False, "reason": "提示词加载失败"}
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.1, context="drift_detection")
        
        if not response_text:
            return {"drift_detected": False, "reason": "AI 服务无响应"}
        
        drift_detected = "YES" in response_text.upper()
        reason = ""
        if "理由:" in response_text:
            reason = response_text.split("理由:")[-1].strip()
        elif "理由：" in response_text:
            reason = response_text.split("理由：")[-1].strip()
        
        return {
            "drift_detected": drift_detected,
            "reason": reason,
            "raw_response": response_text
        }

    async def check_consistency(
        self,
        new_title: str,
        new_text: str,
        existing_content: str
    ) -> Dict[str, Any]:
        prompt_name = "validation/cross"
        variables = {
            "new_title": new_title,
            "new_text": new_text[:500],
            "existing_content": existing_content
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return {"status": "single_source", "score": 0, "conflicts": []}
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.1, context="cross_validation")
        
        if not response_text:
            return {"status": "single_source", "score": 0, "conflicts": []}
        
        result = ai_client.parse_json(response_text)
        return {
            "status": result.get("status", "single_source"),
            "score": result.get("consistency", 0),
            "conflicts": result.get("conflicts", [])
        }

    async def generate_proposal_reason(
        self,
        match_type: str,
        concept_name: str,
        content_title: str,
        node_name: str = "无"
    ) -> str:
        prompt_name = "approval/proposal_reason"
        variables = {
            "match_type": match_type,
            "concept_name": concept_name,
            "content_title": content_title,
            "node_name": node_name
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            return "无法生成理由：提示词缺失"
        
        model = metadata.get("model") if metadata else None
        
        messages = [{"role": "user", "content": prompt_content}]
        response_text = await ai_client.chat_completion(messages, model=model, temperature=0.3, context="proposal_reason")
        
        if not response_text:
            return "无法生成理由：AI 服务无响应"
            
        result = ai_client.parse_json(response_text)
        return result.get("reason", response_text[:100])


enhancement_processor = EnhancementProcessor()
