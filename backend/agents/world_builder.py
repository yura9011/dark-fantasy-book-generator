import json
import logging
from backend.agents.base_agent import BaseAgent

class WorldBuilderAgent(BaseAgent):
    """
    Agent responsible for creating the world, lore, and locations.
    """
    def process(self, book_title: str, themes: list[str]) -> dict:
        """
        Generates the initial world bible based on title and themes.
        """
        logging.info("WorldBuilderAgent: Generating world bible...")
        
        prompt = f"""
        Create a detailed 'World Bible' for a Dark Fantasy book titled "{book_title}".
        Themes: {', '.join(themes)}
        
        Output a JSON object with the following structure:
        {{
            "locations": [
                {{
                    "name": "Location Name",
                    "description": "Atmospheric description...",
                    "significance": "Why this place matters..."
                }}
            ],
            "lore": [
                {{
                    "topic": "History/Magic/Religion",
                    "details": "Detailed explanation..."
                }}
            ],
            "magic_system": "Description of the magic system, its costs, and limitations."
        }}
        """
        
        response = self.llm.generate_content(prompt)
        if not response:
            logging.error("WorldBuilderAgent: Failed to generate content.")
            return {}

        try:
            # Basic cleanup to ensure we get JSON
            cleaned_response = self.extract_json_from_text(response)
                
            world_data = json.loads(cleaned_response)
            self.state_manager.update_world_bible(world_data)
            return world_data
        except json.JSONDecodeError as e:
            logging.error(f"WorldBuilderAgent: Failed to parse JSON: {e}")
            return {}
