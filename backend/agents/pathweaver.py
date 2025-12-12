"""
Pathweaver Agent
Designs the branching narrative structure with multiple routes, decision points, and endings.
"""
import json
import logging
from typing import Any, Dict, List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMService
from backend.agents.lore_state_manager import LoreStateManager


class PathweaverAgent(BaseAgent):
    """
    Designs the branching narrative structure:
    - Multiple route paths (Light/Shadow/Neutral or custom)
    - Key decision points that split the story
    - Route-exclusive characters and events
    - Multiple endings per route
    - Hidden routes and secret conditions
    """
    
    def __init__(self, llm_service: LLMService, state_manager: LoreStateManager):
        self.llm = llm_service
        self.state_manager = state_manager
    
    def process(self, variety_seeds: Dict[str, Any], num_chapters_per_route: int = 5) -> Dict[str, Any]:
        """
        Generate the branching narrative structure.
        
        Args:
            variety_seeds: Seeds from VarietyInjector for diversity
            num_chapters_per_route: Number of chapters/acts per route
        
        Returns:
            Dictionary with routes, decisions, and endings
        """
        logging.info(f"PathweaverAgent: Designing branching narrative ({num_chapters_per_route} chapters per route)")
        
        # Get all context
        state = self.state_manager.get_state()
        variety_text = self._format_variety_constraints(variety_seeds)
        
        # Build context from existing lore
        lore_context = self._build_lore_context(state)
        
        prompt = f"""You are designing the branching narrative structure for a dark fantasy game.

{variety_text}

{lore_context}

STYLE: Think Tactics Ogre's Law/Chaos/Neutral routes, where each path is morally complex and defensible.
Players should agonize over their choices, not just pick "the good ending."

Design THREE main routes with {num_chapters_per_route} acts/chapters each. Also create:
- Decision points that branch the narrative
- Route-exclusive events and revelations
- A hidden fourth route with special unlock conditions

Return your response as valid JSON:
{{
    "routes": {{
        "light": {{
            "name": "Thematic name for this route (not just 'Light Path')",
            "philosophy": "What worldview does this route embody",
            "sacrifice": "What must be given up to walk this path",
            "chapters": [
                {{
                    "number": 1,
                    "title": "Chapter title",
                    "summary": "What happens in this chapter",
                    "key_event": "The defining moment",
                    "characters_focus": ["Which characters are central here"],
                    "emotional_beat": "What the player should feel"
                }}
            ],
            "ending": {{
                "name": "Ending title",
                "description": "How the story concludes",
                "fate_summary": "Brief note on character fates",
                "bittersweet_element": "What is lost even in victory"
            }}
        }},
        "shadow": {{
            "name": "...",
            "philosophy": "...",
            "sacrifice": "...",
            "chapters": [...],
            "ending": {{...}}
        }},
        "neutral": {{
            "name": "...",
            "philosophy": "...",
            "sacrifice": "...",
            "chapters": [...],
            "ending": {{...}}
        }}
    }},
    "decision_points": [
        {{
            "name": "Decision point name",
            "when": "Which chapter or moment this occurs",
            "situation": "The choice presented",
            "options": [
                {{
                    "choice": "What the player chooses",
                    "leads_to": "light/shadow/neutral",
                    "immediate_consequence": "What happens right after",
                    "long_term_effect": "How this shapes the story"
                }}
            ],
            "can_be_reversed": false,
            "characters_affected": ["Who is impacted by this choice"]
        }}
    ],
    "hidden_route": {{
        "name": "Name of the secret fourth route",
        "unlock_conditions": ["What the player must do to access this route"],
        "philosophy": "What truth this route reveals",
        "unique_revelation": "What is learned only on this path",
        "ending_hint": "A teaser of how this route concludes"
    }},
    "route_exclusive_content": {{
        "light": ["Events or revelations only on light path"],
        "shadow": ["Events or revelations only on shadow path"],
        "neutral": ["Events or revelations only on neutral path"]
    }}
}}

Each route should feel like a valid, tragic, morally defensible choice.
The "neutral" path should NOT be a compromise - it should be its own philosophy (perhaps truth over ideology).

Respond ONLY with the JSON, no other text."""

        try:
            response = self.llm.generate_content(prompt, caller="pathweaver")
            result = self._parse_json_response(response)
            
            if result:
                # Store routes in state
                routes = result.get("routes", {})
                for route_key, route_data in routes.items():
                    self.state_manager.set_route(route_key, route_data)
                
                self.state_manager.set_decision_points(result.get("decision_points", []))
                
                if result.get("hidden_route"):
                    self.state_manager.add_hidden_route(result["hidden_route"])
                
                self.state_manager.complete_phase("routes")
                
                logging.info(f"PathweaverAgent: Generated {len(routes)} routes with {len(result.get('decision_points', []))} decision points")
                return result
            else:
                logging.error("PathweaverAgent: Failed to parse LLM response")
                return {}
                
        except Exception as e:
            logging.error(f"PathweaverAgent: Error during generation: {e}")
            return {}
    
    def _build_lore_context(self, state: Dict[str, Any]) -> str:
        """Build a summary of all existing lore for context."""
        lines = ["=== EXISTING LORE (use this in your routes) ===", ""]
        
        # Eras
        if state.get("eras"):
            lines.append("ERAS:")
            for era in state["eras"]:
                lines.append(f"  - {era.get('name', 'Unknown')}: {era.get('summary', '')[:100]}")
            lines.append("")
        
        # Factions
        if state.get("factions"):
            lines.append("FACTIONS:")
            for faction in state["factions"]:
                lines.append(f"  - {faction.get('name', 'Unknown')}: {faction.get('ideology', '')[:80]}")
            lines.append("")
        
        # Characters
        if state.get("characters"):
            lines.append("CHARACTERS:")
            for char in state["characters"]:
                lines.append(f"  - {char.get('name', 'Unknown')} ({char.get('archetype', '')}): {char.get('motivation', '')[:60]}")
            lines.append("")
        
        # Conflicts
        if state.get("conflicts"):
            lines.append("CONFLICTS:")
            for conflict in state["conflicts"]:
                lines.append(f"  - {conflict.get('name', 'Unknown')}: {conflict.get('root_cause', '')[:80]}")
            lines.append("")
        
        # Dilemmas
        if state.get("dilemmas"):
            lines.append("DILEMMAS:")
            for dilemma in state["dilemmas"]:
                lines.append(f"  - {dilemma.get('name', 'Unknown')}: {dilemma.get('situation', '')[:80]}")
        
        lines.append("")
        lines.append("=== END LORE ===")
        
        return '\n'.join(lines)
    
    def _format_variety_constraints(self, seeds: Dict[str, Any]) -> str:
        """Format variety seeds into prompt text."""
        lines = [
            "=== VARIETY CONSTRAINTS ===",
            f"Emotional Tone: {seeds.get('emotion_seed', 'weary determination')}",
            f"Core Theme: {seeds.get('conflict_seed', 'broken oath')}",
        ]
        
        if seeds.get("game_details"):
            game = seeds["game_details"]
            if game.get("narrative_mechanics"):
                lines.append(f"Structural inspiration: {', '.join(game['narrative_mechanics'][:2])}")
        
        if seeds.get("banned_words"):
            lines.append(f"AVOID: {', '.join(seeds['banned_words'][:8])}")
        
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
            logging.error(f"PathweaverAgent: JSON parse error: {e}")
            return None
