"""
Lore Orchestrator Agent
Main controller for the game lore generation process. Coordinates all lore agents in sequence.
"""
import logging
from typing import Any, Dict, Optional
from backend.services.llm_service import LLMService
from backend.services.variety_injector import VarietyInjector
from backend.agents.lore_state_manager import LoreStateManager
from backend.agents.era_architect import EraArchitectAgent
from backend.agents.faction_forge import FactionForgeAgent
from backend.agents.soul_weaver import SoulWeaverAgent
from backend.agents.conflict_designer import ConflictDesignerAgent
from backend.agents.pathweaver import PathweaverAgent


class LoreOrchestratorAgent:
    """
    Main controller for game lore generation.
    Coordinates the workflow between all lore agents:
    EraArchitect -> FactionForge -> SoulWeaver -> ConflictDesigner -> Pathweaver
    """
    
    def __init__(self):
        self.llm_service = LLMService()
        self.state_manager = LoreStateManager()
        self.variety_injector = VarietyInjector()
        
        # Initialize sub-agents
        self.era_architect = EraArchitectAgent(self.llm_service, self.state_manager)
        self.faction_forge = FactionForgeAgent(self.llm_service, self.state_manager)
        self.soul_weaver = SoulWeaverAgent(self.llm_service, self.state_manager)
        self.conflict_designer = ConflictDesignerAgent(self.llm_service, self.state_manager)
        self.pathweaver = PathweaverAgent(self.llm_service, self.state_manager)
    
    def start_generation(
        self,
        project_name: str,
        num_eras: int = 4,
        num_factions: int = 5,
        num_characters: int = 6,
        num_conflicts: int = 4,
        num_chapters_per_route: int = 5,
        stop_after: Optional[str] = None,
        existing_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the full lore generation pipeline.
        
        Args:
            project_name: Name of the lore project
            num_eras: Number of historical eras
            num_factions: Number of factions
            num_characters: Number of main characters
            num_conflicts: Number of major conflicts
            num_chapters_per_route: Chapters per branching route
            stop_after: Phase to pause at ('eras', 'factions', 'characters', 'conflicts', 'routes')
            existing_state: Resume from existing state if provided
        
        Returns:
            Complete lore state dictionary
        """
        logging.info(f"LoreOrchestrator: Starting lore generation for '{project_name}'")
        
        # Load existing state if provided
        if existing_state:
            self.state_manager.set_state(existing_state)
            logging.info("LoreOrchestrator: Resuming from existing state")
        else:
            self.state_manager.reset()
        
        # Generate variety seeds for this run
        variety_seeds = self.variety_injector.get_generation_seeds()
        self.state_manager.set_project_info(project_name)
        self.state_manager.set_variety_seeds(variety_seeds)
        
        logging.info(f"LoreOrchestrator: Using variety seeds - cultures: {variety_seeds.get('name_cultures')}, emotion: {variety_seeds.get('emotion_seed')}")
        
        # === Phase 1: Eras ===
        if not self.state_manager.is_phase_completed("eras"):
            logging.info("LoreOrchestrator: Phase 1 - Generating Eras")
            self.state_manager.set_current_phase("eras")
            self.era_architect.process(project_name, variety_seeds, num_eras)
        else:
            logging.info("LoreOrchestrator: Phase 1 - Eras already generated, skipping")
        
        if stop_after == "eras":
            logging.info("LoreOrchestrator: Pausing after Eras phase")
            self._save_state(project_name)
            return {"status": "PAUSED", "phase": "eras", "state": self.state_manager.get_state()}
        
        # === Phase 2: Factions ===
        if not self.state_manager.is_phase_completed("factions"):
            logging.info("LoreOrchestrator: Phase 2 - Generating Factions")
            self.state_manager.set_current_phase("factions")
            self.faction_forge.process(variety_seeds, num_factions)
        else:
            logging.info("LoreOrchestrator: Phase 2 - Factions already generated, skipping")
        
        if stop_after == "factions":
            logging.info("LoreOrchestrator: Pausing after Factions phase")
            self._save_state(project_name)
            return {"status": "PAUSED", "phase": "factions", "state": self.state_manager.get_state()}
        
        # === Phase 3: Characters ===
        if not self.state_manager.is_phase_completed("characters"):
            logging.info("LoreOrchestrator: Phase 3 - Generating Characters")
            self.state_manager.set_current_phase("characters")
            self.soul_weaver.process(variety_seeds, num_characters)
        else:
            logging.info("LoreOrchestrator: Phase 3 - Characters already generated, skipping")
        
        if stop_after == "characters":
            logging.info("LoreOrchestrator: Pausing after Characters phase")
            self._save_state(project_name)
            return {"status": "PAUSED", "phase": "characters", "state": self.state_manager.get_state()}
        
        # === Phase 4: Conflicts ===
        if not self.state_manager.is_phase_completed("conflicts"):
            logging.info("LoreOrchestrator: Phase 4 - Generating Conflicts")
            self.state_manager.set_current_phase("conflicts")
            self.conflict_designer.process(variety_seeds, num_conflicts)
        else:
            logging.info("LoreOrchestrator: Phase 4 - Conflicts already generated, skipping")
        
        if stop_after == "conflicts":
            logging.info("LoreOrchestrator: Pausing after Conflicts phase")
            self._save_state(project_name)
            return {"status": "PAUSED", "phase": "conflicts", "state": self.state_manager.get_state()}
        
        # === Phase 5: Routes ===
        if not self.state_manager.is_phase_completed("routes"):
            logging.info("LoreOrchestrator: Phase 5 - Generating Routes")
            self.state_manager.set_current_phase("routes")
            self.pathweaver.process(variety_seeds, num_chapters_per_route)
        else:
            logging.info("LoreOrchestrator: Phase 5 - Routes already generated, skipping")
        
        # === Finalization ===
        self.state_manager.set_current_phase("complete")
        self._save_state(project_name)
        
        logging.info(f"LoreOrchestrator: Lore generation complete for '{project_name}'")
        
        return {
            "status": "COMPLETE",
            "phase": "complete",
            "state": self.state_manager.get_state()
        }
    
    def _save_state(self, project_name: str):
        """Save current state to file."""
        filename = f"{project_name.replace(' ', '_')}_lore_state.json"
        self.state_manager.save_state(filename)
    
    def export_to_markdown(self) -> str:
        """
        Export the current lore state to a formatted Markdown document.
        """
        state = self.state_manager.get_state()
        lines = [
            f"# {state.get('project_name', 'Untitled')} - Game Lore Bible",
            "",
            f"*Generated with variety seeds: {', '.join(state.get('variety_seeds', {}).get('name_cultures', []))}*",
            f"*Emotional core: {state.get('variety_seeds', {}).get('emotion_seed', 'unknown')}*",
            "",
            "---",
            ""
        ]
        
        # Cosmology
        cosmology = state.get("cosmology", {})
        if cosmology:
            lines.append("## Cosmology")
            lines.append("")
            if cosmology.get("creation_myth"):
                lines.append(f"**Creation Myth**: {cosmology['creation_myth']}")
            if cosmology.get("divine_forces"):
                lines.append(f"**Divine Forces**: {cosmology['divine_forces']}")
            if cosmology.get("forbidden_knowledge"):
                lines.append(f"**Forbidden Knowledge**: {cosmology['forbidden_knowledge']}")
            lines.append("")
        
        # Eras
        eras = state.get("eras", [])
        if eras:
            lines.append("## Historical Eras")
            lines.append("")
            for era in eras:
                cataclysm_marker = " ⚠️" if era.get("is_cataclysm") else ""
                lines.append(f"### {era.get('name', 'Unknown')}{cataclysm_marker}")
                lines.append(f"*{era.get('duration', 'Unknown duration')}*")
                lines.append("")
                lines.append(era.get("summary", ""))
                if era.get("defining_event"):
                    lines.append(f"- **Defining Event**: {era['defining_event']}")
                if era.get("legacy"):
                    lines.append(f"- **Legacy**: {era['legacy']}")
                lines.append("")
        
        # Factions
        factions = state.get("factions", [])
        if factions:
            lines.append("## Factions")
            lines.append("")
            for faction in factions:
                lines.append(f"### {faction.get('name', 'Unknown')}")
                lines.append(f"*{faction.get('type', 'Unknown type')}*")
                lines.append("")
                lines.append(f"**Ideology**: {faction.get('ideology', 'Unknown')}")
                if faction.get("hidden_truth"):
                    lines.append(f"**Hidden Truth**: {faction['hidden_truth']}")
                if faction.get("dark_secret"):
                    lines.append(f"**Dark Secret**: {faction['dark_secret']}")
                if faction.get("rivals"):
                    lines.append(f"**Rivals**: {', '.join(faction['rivals'])}")
                lines.append("")
        
        # Characters
        characters = state.get("characters", [])
        if characters:
            lines.append("## Characters")
            lines.append("")
            for char in characters:
                lines.append(f"### {char.get('name', 'Unknown')}")
                if char.get("title"):
                    lines.append(f"*{char['title']}*")
                lines.append("")
                lines.append(f"**Archetype**: {char.get('archetype', 'Unknown')}")
                lines.append(f"**Faction**: {char.get('faction', 'Unknown')}")
                lines.append(f"**Motivation**: {char.get('motivation', 'Unknown')}")
                if char.get("inner_demon"):
                    lines.append(f"**Inner Demon**: {char['inner_demon']}")
                if char.get("fate_by_route"):
                    fates = char["fate_by_route"]
                    lines.append(f"**Fates**: Light: {fates.get('light', '?')} | Shadow: {fates.get('shadow', '?')} | Neutral: {fates.get('neutral', '?')}")
                lines.append("")
        
        # Conflicts
        conflicts = state.get("conflicts", [])
        if conflicts:
            lines.append("## Conflicts")
            lines.append("")
            for conflict in conflicts:
                lines.append(f"### {conflict.get('name', 'Unknown')}")
                lines.append(f"*{conflict.get('type', 'Unknown type')}*")
                lines.append("")
                if conflict.get("root_cause"):
                    lines.append(f"**Root Cause**: {conflict['root_cause']}")
                if conflict.get("tragedy"):
                    lines.append(f"**Tragedy**: {conflict['tragedy']}")
                lines.append("")
        
        # Routes
        routes = state.get("routes", {})
        if routes:
            lines.append("## Story Routes")
            lines.append("")
            for route_key, route in routes.items():
                if route.get("name"):
                    lines.append(f"### {route.get('name', route_key.title())}")
                    if route.get("philosophy"):
                        lines.append(f"*{route['philosophy']}*")
                    lines.append("")
                    if route.get("sacrifice"):
                        lines.append(f"**Sacrifice**: {route['sacrifice']}")
                    if route.get("ending"):
                        ending = route["ending"]
                        if isinstance(ending, dict):
                            lines.append(f"**Ending**: {ending.get('name', 'Unknown')} - {ending.get('description', '')}")
                        else:
                            lines.append(f"**Ending**: {ending}")
                    lines.append("")
        
        return '\n'.join(lines)
