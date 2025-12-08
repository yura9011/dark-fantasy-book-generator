import logging
import os
from backend.services.llm_service import LLMService
from backend.agents.state_manager import StateManager
from backend.agents.world_builder import WorldBuilderAgent
from backend.agents.character_architect import CharacterAgent
from backend.agents.story_weaver import StoryAgent
from backend.agents.editor import EditorAgent
from backend.agents.concept_architect import ConceptAgent

class OrchestratorAgent:
    """
    Main controller for the book generation process.
    Coordinates the workflow between WorldBuilder, CharacterArchitect, StoryWeaver, and Editor.
    """
    def __init__(self):
        self.llm_service = LLMService()
        self.state_manager = StateManager()
        
        # Initialize sub-agents
        self.concept_agent = ConceptAgent(self.llm_service, self.state_manager)
        self.world_builder = WorldBuilderAgent(self.llm_service, self.state_manager)
        self.character_agent = CharacterAgent(self.llm_service, self.state_manager)
        self.story_agent = StoryAgent(self.llm_service, self.state_manager)
        self.editor_agent = EditorAgent(self.llm_service, self.state_manager)

    def start_generation(self, book_title: str, themes: list[str], num_chapters: int = 3, stop_after: str = None, inquiry_responses: dict = None):
        """
        Runs the full generation pipeline. Resumes if state data key is present.
        stop_after: 'concept', 'world_building' or 'character_creation' to pause.
        """
        logging.info(f"Orchestrator: Starting generation for '{book_title}'")
        
        # 1. Initialize State
        self.state_manager.update_book_info(book_title, themes)
        
        current_state = self.state_manager.get_state()

        # 0. Concept Phase (Optional)
        if inquiry_responses and not current_state.get("concept", {}).get("logline"):
            logging.info("Orchestrator: Step 0 - Architecting Concept")
            self.concept_agent.process(inquiry_responses)
        
        if stop_after == "concept":
            logging.info("Orchestrator: Pausing after Concept Phase as requested.")
            self.state_manager.save_state(f"{book_title.replace(' ', '_')}_state.json")
            return "PAUSED"

        # 2. Build World
        # If we have a concept, we should probably ensure the world builder uses it?
        # The world builder pulls from state, but logic might need review if it relies on 'themes' arg vs state.
        # Ideally WorldBuilder should look at StateManager.
        if not current_state.get("world_bible", {}).get("locations") and not current_state.get("world_bible", {}).get("lore"):
            logging.info("Orchestrator: Step 1 - Building World")
            self.world_builder.process(book_title, themes)
        else:
            logging.info("Orchestrator: Step 1 - World already built, skipping.")
            
        if stop_after == "world_building":
            logging.info("Orchestrator: Pausing after World Building as requested.")
            self.state_manager.save_state(f"{book_title.replace(' ', '_')}_state.json")
            return "PAUSED"
        
        # 3. Create Characters
        if not current_state.get("characters"):
            logging.info("Orchestrator: Step 2 - Creating Characters")
            self.character_agent.process(num_characters=3)
        else:
            logging.info("Orchestrator: Step 2 - Characters already created, skipping.")

        if stop_after == "character_creation":
            logging.info("Orchestrator: Pausing after Character Creation as requested.")
            self.state_manager.save_state(f"{book_title.replace(' ', '_')}_state.json")
            return "PAUSED"
        
        # 4. Outline Story
        # Check if outline exists and has chapters
        if not current_state.get("outline", {}).get("chapters"):
            logging.info("Orchestrator: Step 3 - Outlining Story")
            self.story_agent.generate_outline(num_chapters=num_chapters)
        else:
            logging.info("Orchestrator: Step 3 - Outline already exists, skipping.")
        
        # 5. Write & Edit Chapters
        logging.info("Orchestrator: Step 4 - Writing Chapters")
        
        # Refresh state to get outline
        current_state = self.state_manager.get_state()
        outline = current_state.get("outline", {}).get("chapters", [])
        
        start_index = current_state.get("current_chapter_index", 0)
        final_book_text = f"# {book_title}\n\n"
        
        for i, chapter in enumerate(outline):
            if i < start_index:
                logging.info(f"Orchestrator: Skipping Chapter {i+1} (already generated)")
                # Retrieve existing content
                existing_content = self.state_manager.get_chapter_content(i)
                if existing_content:
                     final_book_text += f"## Chapter {i+1}: {chapter['title']}\n\n{existing_content}\n\n"
                continue
                
            logging.info(f"Orchestrator: Processing Chapter {i+1}")
            
            # Write Draft
            draft = self.story_agent.write_chapter(i)
            
            # Edit Draft
            final_version = self.editor_agent.process(draft)
            
            final_book_text += f"## Chapter {i+1}: {chapter['title']}\n\n{final_version}\n\n"
            
            # Update Progress and Save
            self.state_manager.save_chapter_content(i, final_version)
            self.state_manager.update_chapter_progress(i + 1)
            self.state_manager.save_state(f"{book_title.replace(' ', '_')}_state.json")
            
        # 6. Save Result
        output_filename = f"{book_title.replace(' ', '_')}_complete.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_book_text)
            
        logging.info(f"Orchestrator: Book generation complete! Saved to {output_filename}")
        
        return final_book_text
