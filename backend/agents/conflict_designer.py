"""
Conflict Designer Agent  
Generates wars, betrayals, moral dilemmas, and the dramatic conflicts that drive the narrative.
"""
import json
import logging
from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMService
from backend.agents.lore_state_manager import LoreStateManager


class ConflictDesignerAgent(BaseAgent):
    """
    Creates the conflicts that drive the narrative:
    - Wars with no clear "right side"
    - Betrayal scenarios and their triggers
    - Ethical dilemmas with no good answer
    - Personal tragedies and losses
    - Moments of unexpected peace and hope
    """
    
    def __init__(self, llm_service: LLMService, state_manager: LoreStateManager):
        self.llm = llm_service
        self.state_manager = state_manager
    
    def process(self, variety_seeds: Dict[str, Any], num_conflicts: int = 4) -> Dict[str, Any]:
        """
        Generate conflicts and moral dilemmas.
        
        Args:
            variety_seeds: Seeds from VarietyInjector for diversity
            num_conflicts: Number of major conflicts to generate
        
        Returns:
            Dictionary with conflicts and dilemmas
        """
        logging.info(f"ConflictDesignerAgent: Generating {num_conflicts} conflicts")
        
        # Get all context from state
        world_context = self.state_manager.get_world_context()
        faction_context = self.state_manager.get_faction_context()
        character_context = self.state_manager.get_character_context()
        variety_text = self._format_variety_constraints(variety_seeds)
        
        prompt = f"""You are designing the central conflicts for a dark fantasy game.

{variety_text}

{world_context}

{faction_context}

{character_context}

TONE: Conflicts should be morally complex - no clear heroes or villains.
Think the Balmamusa massacre (Tactics Ogre), the world of ruin (FF6), Highland vs City-State (Suikoden 2).
Every conflict should force the player to question what is truly "right."

Generate {num_conflicts} major conflicts that involve the factions and characters above. Also generate moral dilemmas the player must face.

Return your response as valid JSON:
{{
    "conflicts": [
        {{
            "name": "Conflict name (avoid generic 'The Great War')",
            "type": "war/rebellion/succession/religious/territorial/ideological",
            "factions_involved": ["Faction 1", "Faction 2"],
            "characters_involved": ["Character names affected or leading this conflict"],
            "root_cause": "The real reason this conflict exists (often hidden)",
            "public_narrative": "What each side claims the conflict is about",
            "atrocities": ["Terrible things done by BOTH sides"],
            "innocents_affected": "Who suffers while the powerful fight",
            "possible_resolutions": {{
                "light": "How this ends on the light path",
                "shadow": "How this ends on the shadow path", 
                "neutral": "How this ends on the neutral path"
            }},
            "tragedy": "What will be lost no matter the outcome"
        }}
    ],
    "dilemmas": [
        {{
            "name": "Short name for the dilemma",
            "situation": "The impossible choice presented to the player",
            "option_a": "First choice and its consequences",
            "option_b": "Second choice and its consequences",
            "option_c": "Hidden third option (if any)",
            "characters_affected": ["Who is impacted by this choice"],
            "no_right_answer": "Why neither choice is truly 'good'",
            "route_impact": "Which route this pushes the player toward"
        }}
    ],
    "moments_of_light": [
        {{
            "description": "A moment of peace, love, or hope amid the darkness",
            "characters_involved": ["Who shares this moment"],
            "significance": "Why this moment matters emotionally",
            "fragility": "What threatens this moment"
        }}
    ]
}}

Include at least one "moment of light" - a glimpse of what could be if the cycle of violence ended.
Make at least one dilemma where helping one person means hurting another you care about.

Respond ONLY with the JSON, no other text."""

        try:
            response = self.llm.generate_content(prompt, caller="conflict_designer")
            result = self._parse_json_response(response)
            
            if result:
                self.state_manager.set_conflicts(result.get("conflicts", []))
                self.state_manager.set_dilemmas(result.get("dilemmas", []))
                self.state_manager.complete_phase("conflicts")
                
                logging.info(f"ConflictDesignerAgent: Generated {len(result.get('conflicts', []))} conflicts")
                return result
            else:
                logging.error("ConflictDesignerAgent: Failed to parse LLM response")
                return {"conflicts": [], "dilemmas": [], "moments_of_light": []}
                
        except Exception as e:
            logging.error(f"ConflictDesignerAgent: Error during generation: {e}")
            return {"conflicts": [], "dilemmas": [], "moments_of_light": []}
    
    def _format_variety_constraints(self, seeds: Dict[str, Any]) -> str:
        """Format variety seeds into prompt text."""
        lines = [
            "=== VARIETY CONSTRAINTS ===",
            f"Emotional Tone: {seeds.get('emotion_seed', 'bitter hope')}",
            f"Core Conflict Style: {seeds.get('conflict_seed', 'broken oath')}",
            ""
        ]
        
        # Historical inspiration for conflict types
        if seeds.get("event_inspirations"):
            lines.append("Draw conflict inspiration from:")
            for event in seeds["event_inspirations"][:2]:
                if isinstance(event, dict):
                    lines.append(f"  - {event.get('name')}: {event.get('emotional_core', '')}")
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
            logging.error(f"ConflictDesignerAgent: JSON parse error: {e}")
            return None
