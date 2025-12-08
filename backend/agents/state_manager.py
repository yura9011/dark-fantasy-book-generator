import json
import logging
from typing import Dict, Any, List

class StateManager:
    """
    Manages the global state of the book generation process (The "Bible").
    Handles storage and retrieval of world data, characters, and story progress.
    """
    def __init__(self):
        self.state: Dict[str, Any] = {
            "concept": {
                "title": "",
                "logline": "",
                "synopsis": "",
                "tone": []
            },
            "book_title": "",
            "theme_keywords": [],
            "world_bible": {
                "locations": [],
                "lore": [],
                "magic_system": ""
            },
            "characters": [],  # List of character profiles
            "outline": {
                "chapters": []
            },
            "current_chapter_index": 0,
            "current_subchapter_index": 0
        }

    def update_book_info(self, title: str, keywords: List[str]):
        self.state["book_title"] = title
        self.state["theme_keywords"] = keywords

    def update_concept(self, concept_data: Dict[str, Any]):
        """Updates the concept data."""
        self.state["concept"] = concept_data
        # Also sync with legacy fields
        if concept_data.get("title"):
            self.state["book_title"] = concept_data["title"]
        if concept_data.get("themes"):
            self.state["theme_keywords"] = concept_data["themes"]

    def update_world_bible(self, world_data: Dict[str, Any]):
        """Updates the world bible with new data (merges or overwrites)."""
        if "locations" in world_data:
            self.state["world_bible"]["locations"].extend(world_data["locations"])
        if "lore" in world_data:
            self.state["world_bible"]["lore"].extend(world_data["lore"])
        if "magic_system" in world_data:
            self.state["world_bible"]["magic_system"] = world_data["magic_system"]

    def add_character(self, character_profile: Dict[str, Any]):
        self.state["characters"].append(character_profile)

    def update_outline(self, outline: Dict[str, Any]):
        self.state["outline"] = outline

    def get_state(self) -> Dict[str, Any]:
        return self.state

    def save_state(self, filepath: str = "book_state.json"):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    def load_state(self, filepath: str = "book_state.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            logging.warning("State file not found. Starting with empty state.")
        except Exception as e:
            logging.error(f"Failed to load state: {e}")

    def set_state(self, state_dict: Dict[str, Any]):
        """Sets the state directly from a dictionary (e.g. from API request)"""
        self.state = state_dict

    def update_chapter_progress(self, chapter_index: int):
        self.state["current_chapter_index"] = chapter_index

    def save_chapter_content(self, chapter_index: int, content: str):
        """Saves the content of a chapter to the state."""
        chapters = self.state.get("outline", {}).get("chapters", [])
        if 0 <= chapter_index < len(chapters):
            chapters[chapter_index]["content"] = content
            # Ensure outline is updated in state (lists are ref, but good to be sure)
            self.state["outline"]["chapters"] = chapters

    def get_chapter_content(self, chapter_index: int) -> str:
        chapters = self.state.get("outline", {}).get("chapters", [])
        if 0 <= chapter_index < len(chapters):
            return chapters[chapter_index].get("content", "")
        return ""
