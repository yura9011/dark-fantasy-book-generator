import logging
from backend.agents.base_agent import BaseAgent

class EditorAgent(BaseAgent):
    """
    Agent responsible for reviewing and refining content.
    """
    def process(self, text: str, criteria: str = "Dark Fantasy Tone") -> str:
        """
        Reviews the text and returns a refined version.
        """
        logging.info("EditorAgent: Reviewing content...")
        
        prompt = f"""
        Act as a senior editor for a Dark Fantasy novel.
        Review the following text for: {criteria}.
        
        - Enhance atmosphere.
        - Fix pacing.
        - Ensure "Show, Don't Tell".
        - Remove cliches.
        
        Text to review:
        {text}
        
        Output ONLY the rewritten, improved text.
        """
        
        response = self.llm.generate_content(prompt)
        if not response:
            logging.error("EditorAgent: Failed to generate critique.")
            return text
            
        return response
