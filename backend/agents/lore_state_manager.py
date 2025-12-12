"""
Lore State Manager
Manages the state for branching game lore generation with support for multiple routes.
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional


class LoreStateManager:
    """
    Manages the state for game lore generation, including support for
    branching narratives with multiple routes and character fates.
    """
    
    def __init__(self):
        self._state = self._create_empty_state()
    
    def _create_empty_state(self) -> Dict[str, Any]:
        """Create a fresh empty state structure."""
        return {
            "project_name": "",
            "tone": "dark_fantasy_introspective",
            "variety_seeds": {},  # Stores which seeds were used for this generation
            
            # World Foundation
            "eras": [],
            "cosmology": {},
            
            # Political Landscape
            "factions": [],
            "territories": [],
            
            # Characters
            "characters": [],
            "relationships": [],
            
            # Conflicts
            "conflicts": [],
            "dilemmas": [],
            
            # Branching Structure
            "routes": {
                "light": {"name": "", "chapters": [], "ending": "", "unlocked": False},
                "shadow": {"name": "", "chapters": [], "ending": "", "unlocked": False},
                "neutral": {"name": "", "chapters": [], "ending": "", "unlocked": False}
            },
            "decision_points": [],
            "hidden_routes": [],
            
            # Generation Progress
            "current_phase": "not_started",
            "completed_phases": []
        }
    
    def reset(self):
        """Reset state to empty."""
        self._state = self._create_empty_state()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state dictionary."""
        return self._state
    
    def set_state(self, state: Dict[str, Any]):
        """Set the entire state (for loading saved states)."""
        self._state = state
    
    # === Project Info ===
    
    def set_project_info(self, name: str, tone: str = "dark_fantasy_introspective"):
        """Set basic project information."""
        self._state["project_name"] = name
        self._state["tone"] = tone
    
    def set_variety_seeds(self, seeds: Dict[str, Any]):
        """Store the variety seeds used for this generation run."""
        # Store a simplified version (don't include the full name pools)
        self._state["variety_seeds"] = {
            "name_cultures": seeds.get("name_cultures", []),
            "emotion_seed": seeds.get("emotion_seed", ""),
            "aesthetic_seed": seeds.get("aesthetic_seed", ""),
            "conflict_seed": seeds.get("conflict_seed", ""),
            "game_reference": seeds.get("game_reference", ""),
            "event_inspirations": [e.get("name", "") for e in seeds.get("event_inspirations", [])]
        }
    
    # === Eras & Cosmology ===
    
    def set_cosmology(self, cosmology: Dict[str, Any]):
        """Set the world's cosmology/creation myth."""
        self._state["cosmology"] = cosmology
    
    def add_era(self, era: Dict[str, Any]):
        """Add a historical era."""
        self._state["eras"].append(era)
    
    def set_eras(self, eras: List[Dict[str, Any]]):
        """Set all eras at once."""
        self._state["eras"] = eras
    
    # === Factions ===
    
    def add_faction(self, faction: Dict[str, Any]):
        """Add a faction."""
        self._state["factions"].append(faction)
    
    def set_factions(self, factions: List[Dict[str, Any]]):
        """Set all factions at once."""
        self._state["factions"] = factions
    
    def get_faction_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a faction by name."""
        for faction in self._state["factions"]:
            if faction.get("name", "").lower() == name.lower():
                return faction
        return None
    
    # === Characters ===
    
    def add_character(self, character: Dict[str, Any]):
        """Add a character."""
        self._state["characters"].append(character)
    
    def set_characters(self, characters: List[Dict[str, Any]]):
        """Set all characters at once."""
        self._state["characters"] = characters
    
    def get_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a character by name."""
        for char in self._state["characters"]:
            if char.get("name", "").lower() == name.lower():
                return char
        return None
    
    def add_relationship(self, relationship: Dict[str, Any]):
        """Add a character relationship."""
        self._state["relationships"].append(relationship)
    
    def set_relationships(self, relationships: List[Dict[str, Any]]):
        """Set all relationships at once."""
        self._state["relationships"] = relationships
    
    # === Conflicts ===
    
    def add_conflict(self, conflict: Dict[str, Any]):
        """Add a conflict."""
        self._state["conflicts"].append(conflict)
    
    def set_conflicts(self, conflicts: List[Dict[str, Any]]):
        """Set all conflicts at once."""
        self._state["conflicts"] = conflicts
    
    def add_dilemma(self, dilemma: Dict[str, Any]):
        """Add a moral dilemma."""
        self._state["dilemmas"].append(dilemma)
    
    def set_dilemmas(self, dilemmas: List[Dict[str, Any]]):
        """Set all dilemmas at once."""
        self._state["dilemmas"] = dilemmas
    
    # === Routes & Branching ===
    
    def set_route(self, route_key: str, route_data: Dict[str, Any]):
        """Set data for a specific route (light/shadow/neutral or custom)."""
        if route_key in self._state["routes"]:
            self._state["routes"][route_key].update(route_data)
        else:
            self._state["routes"][route_key] = route_data
    
    def add_decision_point(self, decision: Dict[str, Any]):
        """Add a decision point that can branch the narrative."""
        self._state["decision_points"].append(decision)
    
    def set_decision_points(self, decisions: List[Dict[str, Any]]):
        """Set all decision points at once."""
        self._state["decision_points"] = decisions
    
    def add_hidden_route(self, route: Dict[str, Any]):
        """Add a hidden/secret route."""
        self._state["hidden_routes"].append(route)
    
    # === Progress Tracking ===
    
    def set_current_phase(self, phase: str):
        """Set the current generation phase."""
        self._state["current_phase"] = phase
    
    def complete_phase(self, phase: str):
        """Mark a phase as completed."""
        if phase not in self._state["completed_phases"]:
            self._state["completed_phases"].append(phase)
    
    def is_phase_completed(self, phase: str) -> bool:
        """Check if a phase has been completed."""
        return phase in self._state["completed_phases"]
    
    # === Persistence ===
    
    def save_state(self, filename: str):
        """Save state to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            logging.info(f"LoreStateManager: State saved to {filename}")
        except Exception as e:
            logging.error(f"LoreStateManager: Failed to save state: {e}")
    
    def load_state(self, filename: str) -> bool:
        """Load state from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self._state = json.load(f)
            logging.info(f"LoreStateManager: State loaded from {filename}")
            return True
        except Exception as e:
            logging.error(f"LoreStateManager: Failed to load state: {e}")
            return False
    
    # === Context Helpers for Agents ===
    
    def get_world_context(self) -> str:
        """Get a formatted string of world context for prompt injection."""
        lines = []
        
        if self._state.get("cosmology"):
            lines.append("=== COSMOLOGY ===")
            cosmo = self._state["cosmology"]
            if cosmo.get("creation_myth"):
                lines.append(f"Creation: {cosmo['creation_myth']}")
            if cosmo.get("divine_forces"):
                lines.append(f"Divine Forces: {cosmo['divine_forces']}")
            lines.append("")
        
        if self._state.get("eras"):
            lines.append("=== HISTORICAL ERAS ===")
            for era in self._state["eras"]:
                lines.append(f"- {era.get('name', 'Unknown')}: {era.get('summary', '')}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_faction_context(self) -> str:
        """Get a formatted string of faction context for prompt injection."""
        lines = ["=== FACTIONS ==="]
        
        for faction in self._state.get("factions", []):
            lines.append(f"- {faction.get('name', 'Unknown')}")
            if faction.get("ideology"):
                lines.append(f"  Ideology: {faction['ideology']}")
            if faction.get("rivals"):
                lines.append(f"  Rivals: {', '.join(faction['rivals'])}")
        
        return '\n'.join(lines)
    
    def get_character_context(self) -> str:
        """Get a formatted string of character context for prompt injection."""
        lines = ["=== CHARACTERS ==="]
        
        for char in self._state.get("characters", []):
            lines.append(f"- {char.get('name', 'Unknown')} ({char.get('archetype', 'Unknown')})")
            if char.get("motivation"):
                lines.append(f"  Motivation: {char['motivation']}")
            if char.get("faction"):
                lines.append(f"  Faction: {char['faction']}")
        
        return '\n'.join(lines)
