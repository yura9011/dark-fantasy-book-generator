"""
Era Architect Agent
Generates the historical foundation: cosmology, eras, cataclysms, and ancient legends.
"""
import json
import logging
from typing import Any, Dict
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMService
from backend.agents.lore_state_manager import LoreStateManager


class EraArchitectAgent(BaseAgent):
    """
    Generates the historical foundation of the game world:
    - Cosmology and creation myths
    - Historical eras/epochs
    - Cataclysmic events
    - Ancient prophecies and legends
    """
    
    def __init__(self, llm_service: LLMService, state_manager: LoreStateManager):
        self.llm = llm_service
        self.state_manager = state_manager
    
    def process(self, project_name: str, variety_seeds: Dict[str, Any], num_eras: int = 4) -> Dict[str, Any]:
        """
        Generate the world's historical foundation.
        
        Args:
            project_name: Name of the lore project
            variety_seeds: Seeds from VarietyInjector for diversity
            num_eras: Number of historical eras to generate
        
        Returns:
            Dictionary containing cosmology and eras
        """
        logging.info(f"EraArchitectAgent: Generating {num_eras} eras for '{project_name}'")
        
        # Format variety constraints for prompt
        variety_text = self._format_variety_constraints(variety_seeds)
        
        prompt = f"""You are a master worldbuilder creating the historical foundation for a dark fantasy game called "{project_name}".

{variety_text}

TONE: Dark fantasy, introspective, morally complex. Think Tactics Ogre, FF6, Vagrant Story.
Focus on tragedy, betrayal, revenge, but also moments of love, hope, and peace that make the darkness meaningful.

Generate {num_eras} distinct historical eras, from creation to the present day. Also create the cosmology (creation myth, divine forces).

Return your response as valid JSON in this exact format:
{{
    "cosmology": {{
        "creation_myth": "A 2-3 sentence creation myth",
        "divine_forces": "Description of gods, spirits, or cosmic forces",
        "cosmic_balance": "What forces are in tension (not just generic good vs evil)",
        "forbidden_knowledge": "What truth about creation is hidden or dangerous"
    }},
    "eras": [
        {{
            "name": "Era name (avoid generic names like 'Age of Light')",
            "duration": "Approximate timespan",
            "summary": "2-3 sentence summary of this era",
            "defining_event": "The most significant event",
            "emotional_tone": "What emotions define this era",
            "legacy": "What this era left behind for future generations",
            "is_cataclysm": false
        }}
    ]
}}

Make at least one era a cataclysm or dark period (is_cataclysm: true).
Use names from the cultural traditions specified in the variety constraints.
Avoid ALL words from the banned list.

Respond ONLY with the JSON, no other text."""

        try:
            response = self.llm.generate_content(prompt, caller="era_architect")
            result = self._parse_json_response(response)
            
            if result:
                # Store in state
                self.state_manager.set_cosmology(result.get("cosmology", {}))
                self.state_manager.set_eras(result.get("eras", []))
                self.state_manager.complete_phase("eras")
                
                logging.info(f"EraArchitectAgent: Generated {len(result.get('eras', []))} eras")
                return result
            else:
                logging.error("EraArchitectAgent: Failed to parse LLM response")
                return {"cosmology": {}, "eras": []}
                
        except Exception as e:
            logging.error(f"EraArchitectAgent: Error during generation: {e}")
            return {"cosmology": {}, "eras": []}
    
    def _format_variety_constraints(self, seeds: Dict[str, Any]) -> str:
        """Format variety seeds into prompt text."""
        lines = [
            "=== VARIETY CONSTRAINTS (FOLLOW STRICTLY) ===",
            "",
            f"Emotional Tone: {seeds.get('emotion_seed', 'quiet despair')}",
            f"Aesthetic: {seeds.get('aesthetic_seed', 'bone and rust')}",
            f"Core Conflict: {seeds.get('conflict_seed', 'inherited sin')}",
            "",
            f"Cultural Inspiration: Draw names and concepts from {', '.join(seeds.get('name_cultures', ['slavic']))} traditions.",
            ""
        ]
        
        # Add event inspirations
        if seeds.get("event_inspirations"):
            lines.append("Historical Parallels (use as inspiration for era events):")
            for event in seeds["event_inspirations"]:
                if isinstance(event, dict):
                    lines.append(f"  - {event.get('name', 'Unknown')}: {event.get('description', '')}")
            lines.append("")
        
        # Add game reference
        if seeds.get("game_reference") and seeds.get("game_details"):
            game = seeds["game_details"]
            lines.append(f"Thematic Reference: {game.get('full_name', seeds['game_reference'])}")
            if game.get("themes"):
                lines.append(f"  Draw from themes: {', '.join(game['themes'][:3])}")
            lines.append("")
        
        # Add banned words
        if seeds.get("banned_words"):
            banned_sample = seeds["banned_words"][:20] if len(seeds["banned_words"]) > 20 else seeds["banned_words"]
            lines.append(f"BANNED WORDS (never use): {', '.join(banned_sample)}")
        
        lines.append("")
        lines.append("=== END CONSTRAINTS ===")
        
        return '\n'.join(lines)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = response.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split('\n')
            # Find content between ``` markers
            start_idx = 1  # Skip first line (```json)
            end_idx = len(lines) - 1
            for i, line in enumerate(lines):
                if i > 0 and line.strip() == "```":
                    end_idx = i
                    break
            text = '\n'.join(lines[start_idx:end_idx])
        
        # Extract JSON object
        text = self.extract_json_from_text(text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logging.error(f"EraArchitectAgent: JSON parse error: {e}")
            logging.error(f"Raw response: {response[:500]}")
            return None
