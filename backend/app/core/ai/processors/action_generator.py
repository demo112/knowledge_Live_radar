import logging
from typing import List, Dict, Any
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader
from app.schemas.intent import IntentParseResult, IntentType, Action, ActionType
from app.core.ai.processors.pyramid import pyramid_processor

logger = logging.getLogger(__name__)

class ActionGenerator:
    async def generate_actions(self, intent: IntentParseResult) -> List[Action]:
        """
        Generate actions based on user intent.
        """
        actions = []
        
        if intent.intent_type == IntentType.LEARN:
            actions.extend(await self._generate_learn_actions(intent))
        elif intent.intent_type == IntentType.RESEARCH:
            actions.extend(await self._generate_research_actions(intent))
        elif intent.intent_type == IntentType.TRACK:
            actions.extend(await self._generate_track_actions(intent))
        elif intent.intent_type == IntentType.CREATE:
            # For explicit create, we might just parse the parameters
            actions.append(Action(
                type=ActionType.CREATE_NODE,
                description=f"Create node: {intent.primary_topic}",
                parameters={"name": intent.primary_topic, "type": "concept"}
            ))
            
        return actions

    async def _generate_learn_actions(self, intent: IntentParseResult) -> List[Action]:
        """
        Generate actions for LEARN intent:
        1. Create Cluster
        2. Create Center Node
        3. Suggest Structure (via PyramidProcessor)
        """
        actions = []
        
        # 1. Create Cluster Action
        actions.append(Action(
            type=ActionType.CREATE_CLUSTER,
            description=f"Create Knowledge Cluster: {intent.primary_topic}",
            parameters={
                "name": intent.primary_topic,
                "description": f"Knowledge cluster for {intent.primary_topic}",
                "center_node_name": intent.primary_topic
            },
            priority=1
        ))
        
        # 2. Generate Structure Suggestion
        try:
            structure_response = await pyramid_processor.generate_structure(
                intent.primary_topic, 
                intent.goal or f"Learn about {intent.primary_topic}"
            )
            
            # Convert suggested structure to actions
            if structure_response.structure:
                self._traverse_structure(
                    structure_response.structure, 
                    intent.primary_topic, 
                    actions
                )
                
        except Exception as e:
            logger.error(f"Failed to generate structure for learn intent: {e}")
            # Fallback action if structure generation fails
            actions.append(Action(
                type=ActionType.GENERATE_REPORT,
                description=f"Generate learning roadmap for {intent.primary_topic}",
                parameters={"topic": intent.primary_topic},
                priority=2
            ))
            
        return actions

    def _traverse_structure(self, node_structure: Any, parent_name: str, actions: List[Action], depth: int = 1):
        """
        Recursively traverse pyramid structure and generate CREATE_NODE actions.
        """
        if depth > 3: # Limit depth
            return

        # Skip the root node if it's the same as primary topic (already handled by cluster creation center node)
        # But here structure root might be the topic itself.
        # Let's add it if it's not the root call or if we want to ensure it exists.
        # Actually, creating a cluster usually implies creating a center node.
        # If the structure root is the same as cluster center, we might skip or update it.
        # For simplicity, we add all nodes from structure as CREATE_NODE actions.
        # The system handles idempotency or we can check names.
        
        # In this implementation, we assume structure.name IS the topic name.
        # So we might skip adding the top-level node if it matches parent_name (which is passed as topic initially)
        # But wait, we passed intent.primary_topic as parent_name for the root call.
        
        # Let's adjust logic:
        # The root of the structure is likely the topic itself.
        # We can start traversing from its children.
        
        if node_structure.name.lower() != parent_name.lower():
             actions.append(Action(
                type=ActionType.CREATE_NODE,
                description=f"Create Node: {node_structure.name}",
                parameters={
                    "name": node_structure.name,
                    "description": node_structure.description,
                    "node_type": "concept",
                    "parent_name": parent_name
                },
                priority=2
            ))
             current_parent = node_structure.name
        else:
             current_parent = parent_name
        
        if hasattr(node_structure, 'children') and node_structure.children:
            for child in node_structure.children:
                self._traverse_structure(child, current_parent, actions, depth + 1)

    async def _generate_research_actions(self, intent: IntentParseResult) -> List[Action]:
        """
        Generate actions for RESEARCH intent:
        1. Generate Search Queries
        """
        prompt_name = "intent/research"
        variables = {
            "topic": intent.primary_topic,
            "goal": intent.goal or "Deep research",
            "sub_topics": ", ".join(intent.sub_topics) if intent.sub_topics else "General"
        }
        
        prompt_content, metadata = prompt_loader.render_prompt(prompt_name, variables)
        
        if not prompt_content:
            logger.error(f"Failed to load prompt: {prompt_name}")
            return []
            
        model = metadata.get("model") if metadata else None
        
        try:
            response_text = await ai_client.chat_completion(
                [{"role": "user", "content": prompt_content}], 
                model=model, 
                context="research_action_generation"
            )
            
            if not response_text:
                return []
                
            research_plan = ai_client.parse_json(response_text)
            
            actions = []
            if isinstance(research_plan, list):
                for item in research_plan:
                    actions.append(Action(
                        type=ActionType.SEARCH_CONTENT,
                        description=f"Search: {item.get('query')}",
                        parameters={
                            "query": item.get("query"),
                            "type": item.get("type"),
                            "description": item.get("description")
                        },
                        priority=1
                    ))
            return actions
            
        except Exception as e:
            logger.error(f"Error generating research actions: {e}")
            return []

    async def _generate_track_actions(self, intent: IntentParseResult) -> List[Action]:
        """
        Generate actions for TRACK intent.
        """
        return [
            Action(
                type=ActionType.SUBSCRIBE_TOPIC,
                description=f"Track updates for: {intent.primary_topic}",
                parameters={"topic": intent.primary_topic},
                priority=1
            )
        ]

action_generator = ActionGenerator()
