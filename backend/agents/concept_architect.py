import json
import logging
from backend.agents.base_agent import BaseAgent

class ConceptAgent(BaseAgent):
    """
    Agent responsible for interpreting abstract user inputs (The Inquiry)
    and synthesizing a high-level story concept.
    """
    def process(self, inquiry_responses: dict) -> dict:
        """
        Generates a story concept based on inquiry responses.
        """
        logging.info("ConceptAgent: Interpreting inquiry responses...")
        
        # Format responses for the prompt
        formatted_responses = "\n".join([f"- {question}: {answer}" for question, answer in inquiry_responses.items()])
        
        prompt = f"""
        You are a Dark Fantasy Concept Architect. Your goal is to interpret abstract, philosophical, and symbolic inputs from a user and synthesize them into a concrete, compelling story concept.
        
        THE INQUIRY RESPONSES:
        {formatted_responses}
        
        TASK:
        Analyze these responses. Look for underlying themes, emotional textures, and contradictions.
        Interpret the "Soul" of the story the user is trying to tell.
        Then, generate a high-level concept for a Dark Fantasy novel.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "title": "A suggestive, atmospheric title",
            "logline": "A single sentence hook that captures the protagonist, conflict, and stakes.",
            "synopsis": "A brief paragraph (3-4 sentences) outlining the core narrative arc and the nature of the dark world.",
            "themes": ["Theme 1", "Theme 2", "Theme 3", "Theme 4"],
            "tone": ["Tone 1", "Tone 2", "Tone 3"]
        }}
        """
        
        response = self.llm.generate_content(prompt)
        if not response:
            logging.error("ConceptAgent: Failed to generate content.")
            return {}

        try:
            cleaned_response = self.extract_json_from_text(response)
            concept_data = json.loads(cleaned_response)
            
            # Update state with the new concept
            self.state_manager.update_concept(concept_data)
            
            return concept_data
        except json.JSONDecodeError as e:
            logging.error(f"ConceptAgent: Failed to parse JSON: {e}")
            return {}
