import os
import time
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class LLMService:
    """
    Service to handle interactions with the Google Gemini API.
    Encapsulates configuration, safety settings, and retry logic.
    """
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-flash-latest"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        
        # Default safety settings (can be overridden)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def generate_content(self, prompt: str, generation_config: dict = None, retries: int = 3) -> str:
        """
        Generates content using the LLM with exponential backoff for retries.
        """
        if generation_config is None:
            generation_config = {
                "temperature": 0.9,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }

        for i in range(retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings
                )
                return response.text
            except Exception as e:
                logging.error(f"Error generating content (attempt {i+1}/{retries}): {e}")
                if "429" in str(e):
                    delay = 2 ** i
                    logging.warning(f"Rate limit hit. Waiting {delay} seconds...")
                    time.sleep(delay)
                elif i < retries - 1:
                    time.sleep(1)
                else:
                    logging.error("Failed to generate content after multiple retries.")
                    return None
        return None
