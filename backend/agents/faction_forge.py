"""
Faction Forge Agent
Generates the political landscape: nations, guilds, orders, and their relationships.
"""
import json
import logging
from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMService
from backend.agents.lore_state_manager import LoreStateManager


class FactionForgeAgent(BaseAgent):
    """
    Generates the political landscape of the game world:
    - Nations and kingdoms
    - Secret societies and guilds
    - Religious orders
    - Alliances, rivalries, and power dynamics
    """
    
    def __init__(self, llm_service: LLMService, state_manager: LoreStateManager):
        self.llm = llm_service
        self.state_manager = state_manager
    
    def process(self, variety_seeds: Dict[str, Any], num_factions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate the world's factions and their relationships.
        
        Args:
            variety_seeds: Seeds from VarietyInjector for diversity
            num_factions: Number of factions to generate
        
        Returns:
            List of faction dictionaries
        """
        logging.info(f"FactionForgeAgent: Generating {num_factions} factions")
        
        # Get world context from state
        world_context = self.state_manager.get_world_context()
        variety_text = self._format_variety_constraints(variety_seeds)
        
        prompt = f"""You are designing factions for a dark fantasy game with deep political intrigue.

{variety_text}

{world_context}

TONE: No faction is purely good or evil. Everyone has reasons for their actions.
Think Tactics Ogre's ethnic conflicts, Suikoden's nation-building, Fire Emblem's warring kingdoms.

Generate {num_factions} distinct factions. Include a mix of:
- At least one nation/kingdom
- At least one religious order or cult
- At least one secretive group (assassins, merchants, scholars)
- At least one fallen or disgraced faction

Return your response as valid JSON in this exact format:
{{
    "factions": [
        {{
            "name": "Faction name (use cultural naming from constraints)",
            "type": "kingdom/order/guild/cult/alliance",
            "ideology": "Core belief or goal in one sentence",
            "public_face": "How they present themselves to others",
            "hidden_truth": "What they hide or deny about themselves",
            "origins": "How this faction came to be (link to eras if possible)",
            "territory": "Where they are based or operate",
            "leaders": ["Name 1", "Name 2"],
            "rivals": ["Faction name they oppose"],
            "allies": ["Faction name they work with"],
            "internal_conflict": "What threatens them from within",
            "resources": "What gives them power (gold, magic, information, faith)",
            "dark_secret": "The worst thing they have done or will do"
        }}
    ]
}}

Ensure factions have complex relationships - some could be temporary allies despite philosophical differences.
Avoid generic faction names like "The Order of..." or "Brotherhood of..."
Make at least one faction sympathetic despite terrible methods.

Respond ONLY with the JSON, no other text."""

        try:
            response = self.llm.generate_content(prompt, caller="faction_forge")
            result = self._parse_json_response(response)
            
            if result and "factions" in result:
                factions = result["factions"]
                self.state_manager.set_factions(factions)
                self.state_manager.complete_phase("factions")
                
                logging.info(f"FactionForgeAgent: Generated {len(factions)} factions")
                return factions
            else:
                logging.error("FactionForgeAgent: Failed to parse LLM response")
                return []
                
        except Exception as e:
            logging.error(f"FactionForgeAgent: Error during generation: {e}")
            return []
    
    def _format_variety_constraints(self, seeds: Dict[str, Any]) -> str:
        """Format variety seeds into prompt text."""
        lines = [
            "=== VARIETY CONSTRAINTS (FOLLOW STRICTLY) ===",
            "",
            f"Emotional Tone: {seeds.get('emotion_seed', 'quiet despair')}",
            f"Aesthetic: {seeds.get('aesthetic_seed', 'bone and rust')}",
            f"Core Conflict: {seeds.get('conflict_seed', 'inherited sin')}",
            "",
            f"Cultural Inspiration: {', '.join(seeds.get('name_cultures', ['slavic']))} traditions.",
            ""
        ]
        
        # Sample names for the LLM to use
        name_pools = seeds.get("name_pools", {})
        if name_pools:
            lines.append("Sample names to use (pick from these styles):")
            for culture, pool in name_pools.items():
                if isinstance(pool, dict):
                    male_sample = pool.get('male', [])[:5]
                    female_sample = pool.get('female', [])[:5]
                    place_sample = pool.get('places', [])[:5]
                    if male_sample:
                        lines.append(f"  {culture} (people): {', '.join(male_sample + female_sample)}")
                    if place_sample:
                        lines.append(f"  {culture} (places): {', '.join(place_sample)}")
            lines.append("")
        
        # Banned words
        if seeds.get("banned_words"):
            banned_sample = seeds["banned_words"][:15]
            lines.append(f"BANNED: {', '.join(banned_sample)}")
        
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
            logging.error(f"FactionForgeAgent: JSON parse error: {e}")
            return None
