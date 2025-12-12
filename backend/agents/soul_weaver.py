"""
Soul Weaver Agent
Generates emotionally complex characters with Jungian archetypes, motivations, and relationships.
"""
import json
import logging
from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMService
from backend.agents.lore_state_manager import LoreStateManager


# Jungian archetypes with dark fantasy twists
ARCHETYPES = [
    "The Shadow (repressed darkness, hidden self)",
    "The Anima/Animus (inner opposite, soul guide)",
    "The Wise Old Man (aged mentor with secrets)",
    "The Trickster (chaos, transformation through disruption)",
    "The Hero (quest, but at what cost?)",
    "The Mother (nurturing that suffocates or heals)",
    "The Eternal Child (innocence preserved or corrupted)",
    "The Ruler (power's corruption or responsibility)",
    "The Outcast (exiled truth-teller)",
    "The Martyr (sacrifice that may be meaningless)"
]


class SoulWeaverAgent(BaseAgent):
    """
    Generates emotionally complex characters:
    - Jungian archetypes with dark twists
    - Complex motivations (revenge, redemption, love, duty)
    - Relationship webs (allies, rivals, betrayers, lovers)
    - Character fates that vary by route
    - Inner demons and psychological profiles
    """
    
    def __init__(self, llm_service: LLMService, state_manager: LoreStateManager):
        self.llm = llm_service
        self.state_manager = state_manager
    
    def process(self, variety_seeds: Dict[str, Any], num_characters: int = 6) -> Dict[str, Any]:
        """
        Generate characters and their relationships.
        
        Args:
            variety_seeds: Seeds from VarietyInjector for diversity
            num_characters: Number of main characters to generate
        
        Returns:
            Dictionary with characters and relationships
        """
        logging.info(f"SoulWeaverAgent: Generating {num_characters} characters")
        
        # Get context from state
        world_context = self.state_manager.get_world_context()
        faction_context = self.state_manager.get_faction_context()
        variety_text = self._format_variety_constraints(variety_seeds)
        
        prompt = f"""You are creating deeply emotional characters for a dark fantasy game.

{variety_text}

{world_context}

{faction_context}

TONE: Characters should feel real, flawed, and sympathetic even when doing terrible things.
Think Ramza and Delita (Tactics Ogre), Terra and Locke (FF6), Ashley Riot (Vagrant Story).

Generate {num_characters} main characters. Each should:
- Have a clear psychological archetype from this list: {', '.join(ARCHETYPES[:5])}
- Belong to or oppose one of the existing factions
- Have a motivation rooted in the world's history
- Have at least one meaningful relationship (love, hate, family, betrayal)
- Have different fates depending on story route (light/shadow/neutral paths)

Return your response as valid JSON:
{{
    "characters": [
        {{
            "name": "Character name (from cultural pools in constraints)",
            "title": "Optional title or role",
            "archetype": "Primary archetype from the list",
            "age": "Age or apparent age",
            "faction": "Which faction they belong to or once belonged to",
            "faction_role": "Their position or relationship to the faction",
            "backstory": "2-3 sentences about their past, linked to world eras",
            "motivation": "What drives them (revenge, redemption, love, duty, etc.)",
            "inner_demon": "Their psychological wound or flaw",
            "outer_mask": "How they present themselves to others",
            "secret": "What they hide from everyone",
            "beliefs": "What they think is right or true",
            "fate_by_route": {{
                "light": "Their fate on the light/redemption path",
                "shadow": "Their fate on the shadow/vengeance path",
                "neutral": "Their fate on the neutral/truth path"
            }}
        }}
    ],
    "relationships": [
        {{
            "character_a": "Name",
            "character_b": "Name", 
            "type": "lovers/rivals/family/mentor/betrayer/allies",
            "history": "How this relationship formed",
            "tension": "What threatens or complicates this bond",
            "route_dependent": true/false
        }}
    ]
}}

Make at least one pair of former friends now enemies.
Make at least one relationship that could be romance or rivalry depending on player choices.
Avoid "the chosen one" tropes - everyone is shaped by circumstances, not destiny.

Respond ONLY with the JSON, no other text."""

        try:
            response = self.llm.generate_content(prompt, caller="soul_weaver")
            result = self._parse_json_response(response)
            
            if result:
                characters = result.get("characters", [])
                relationships = result.get("relationships", [])
                
                self.state_manager.set_characters(characters)
                self.state_manager.set_relationships(relationships)
                self.state_manager.complete_phase("characters")
                
                logging.info(f"SoulWeaverAgent: Generated {len(characters)} characters, {len(relationships)} relationships")
                return result
            else:
                logging.error("SoulWeaverAgent: Failed to parse LLM response")
                return {"characters": [], "relationships": []}
                
        except Exception as e:
            logging.error(f"SoulWeaverAgent: Error during generation: {e}")
            return {"characters": [], "relationships": []}
    
    def _format_variety_constraints(self, seeds: Dict[str, Any]) -> str:
        """Format variety seeds into prompt text."""
        lines = [
            "=== VARIETY CONSTRAINTS ===",
            "",
            f"Emotional Core: {seeds.get('emotion_seed', 'quiet despair')}",
            f"Aesthetic: {seeds.get('aesthetic_seed', 'bone and rust')}",
            f"Central Conflict: {seeds.get('conflict_seed', 'inherited sin')}",
            "",
        ]
        
        # Provide name samples
        name_pools = seeds.get("name_pools", {})
        if name_pools:
            lines.append("Use names from these cultural traditions:")
            for culture, pool in name_pools.items():
                if isinstance(pool, dict):
                    male = pool.get('male', [])[:4]
                    female = pool.get('female', [])[:4]
                    lines.append(f"  {culture}: {', '.join(male)} / {', '.join(female)}")
            lines.append("")
        
        # Game reference for character depth
        if seeds.get("game_details"):
            game = seeds["game_details"]
            if game.get("emotional_beats"):
                lines.append(f"Emotional reference: {', '.join(game['emotional_beats'][:2])}")
            lines.append("")
        
        if seeds.get("banned_words"):
            lines.append(f"AVOID: {', '.join(seeds['banned_words'][:10])}")
        
        lines.append("=== END CONSTRAINTS ===")
        return '\n'.join(lines)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        text = response.strip()
        
        if text.startswith("```"):
            lines = text.split('\n')
            start_idx = 1
            end_idx = len(lines) - 1
            for i, line in enumerate(lines):
                if i > 0 and line.strip() == "```":
                    end_idx = i
                    break
            text = '\n'.join(lines[start_idx:end_idx])
        
        text = self.extract_json_from_text(text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error(f"SoulWeaverAgent: JSON parse error: {e}")
            return None
