import json
import logging
from backend.agents.base_agent import BaseAgent

class CharacterAgent(BaseAgent):
    """
    Agent responsible for creating and managing characters.
    """
    def process(self, num_characters: int = 3) -> list:
        """
        Generates a list of main characters.
        """
        logging.info("CharacterAgent: Generating characters...")
        context = self.get_context()
        book_title = context.get("book_title")
        themes = context.get("theme_keywords")
        world_summary = json.dumps(context.get("world_bible", {}))[:1000] # Truncate for context window if needed

        prompt = f"""
        Create {num_characters} complex, dark fantasy characters for the book "{book_title}".
        Themes: {', '.join(themes)}
        World Context: {world_summary}
        
        Use Jungian archetypes (Shadow, Anima/Animus, Persona, Self) to add depth.
        
        Output a JSON object with a key "characters" containing a list of objects:
        {{
            "characters": [
                {{
                    "name": "Name",
                    "archetype": "Jungian Archetype",
                    "motivation": "Core drive",
                    "flaw": "Fatal flaw",
                    "description": "Physical and psychological description",
                    "backstory": "Brief history"
                }}
            ]
        }}
        """
        
        response = self.llm.generate_content(prompt)
        if not response:
            logging.error("CharacterAgent: Failed to generate content.")
            return []

        try:
            cleaned_response = self.extract_json_from_text(response)
            
            data = json.loads(cleaned_response)
            characters = data.get("characters", [])
            for char in characters:
                self.state_manager.add_character(char)
            return characters
        except json.JSONDecodeError as e:
            logging.error(f"CharacterAgent: Failed to parse JSON: {e}")
            return []
