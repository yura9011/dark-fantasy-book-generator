import json
import logging
from backend.agents.base_agent import BaseAgent

class StoryAgent(BaseAgent):
    """
    Agent responsible for writing the story content (outlines and chapters).
    """
    def generate_outline(self, num_chapters: int = 5) -> dict:
        """
        Generates the book outline.
        """
        logging.info("StoryAgent: Generating outline...")
        context = self.get_context()
        book_title = context.get("book_title")
        themes = context.get("theme_keywords")
        world = json.dumps(context.get("world_bible", {}))[:500]
        characters = json.dumps(context.get("characters", []))[:1000]
        
        prompt = f"""
        Create a chapter outline for "{book_title}" with exactly {num_chapters} chapters.
        Themes: {', '.join(themes)}
        World: {world}
        Characters: {characters}
        
        Output JSON:
        {{
            "chapters": [
                {{
                    "chapter_number": 1,
                    "title": "Chapter Title",
                    "summary": "Plot summary..."
                }}
            ]
        }}
        """
        
        response = self.llm.generate_content(prompt)
        if not response:
            return {}
            
        try:
            cleaned = self.extract_json_from_text(response)
            outline = json.loads(cleaned)
            self.state_manager.update_outline(outline)
            return outline
        except json.JSONDecodeError:
            logging.error("StoryAgent: Failed to parse outline JSON.")
            return {}

    def write_chapter(self, chapter_index: int) -> str:
        """
        Writes the content for a specific chapter.
        """
        context = self.get_context()
        outline = context.get("outline", {}).get("chapters", [])
        if not outline or chapter_index >= len(outline):
            logging.error("StoryAgent: Invalid chapter index.")
            return ""
            
        chapter_info = outline[chapter_index]
        logging.info(f"StoryAgent: Writing Chapter {chapter_index + 1}: {chapter_info['title']}")
        
        prompt = f"""
        Write Chapter {chapter_index + 1}: "{chapter_info['title']}" for the book "{context.get('book_title')}".
        Summary: {chapter_info['summary']}
        
        Style: Dark Fantasy, atmospheric, show don't tell.
        
        Context:
        - World: {json.dumps(context.get('world_bible', {}))[:500]}
        - Characters: {json.dumps(context.get('characters', []))[:1000]}
        
        Write the full chapter text now.
        """
        
        return self.llm.generate_content(prompt) or ""

    def process(self, *args, **kwargs):
        # Placeholder for generic process if needed
        pass
