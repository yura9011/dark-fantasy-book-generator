"""
LLM Service with Enhanced Quota Management

Provides:
- File logging of all API requests
- Token counting before requests
- Configurable delays between calls
- Enhanced retry logic with extended backoff
"""
import os
import time
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class LLMService:
    """
    Service to handle interactions with the Google Gemini API.
    Encapsulates configuration, safety settings, and retry logic.
    """
    
    def __init__(
        self, 
        api_key: str = None, 
        model_name: str = "models/gemini-2.0-flash-exp",
        min_delay_between_calls: float = 2.0,
        max_retries: int = 5
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        
        # Quota management settings
        self.min_delay = min_delay_between_calls
        self.max_retries = max_retries
        self.last_call_time = 0
        
        # Request tracking
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
        # Setup file logger
        self._setup_api_logger()
        
        # Default safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    def _setup_api_logger(self):
        """Setup dedicated file logger for API usage tracking."""
        self.api_logger = logging.getLogger("api_usage")
        self.api_logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.api_logger.handlers:
            log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "api_usage.log")
            
            handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.api_logger.addHandler(handler)
    
    def _wait_for_rate_limit(self):
        """Ensure minimum delay between API calls."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed
            logging.info(f"Rate limiting: waiting {wait_time:.1f}s before next call")
            time.sleep(wait_time)
    
    def count_tokens(self, prompt: str) -> int:
        """Count tokens in a prompt before sending."""
        try:
            result = self.model.count_tokens(prompt)
            return result.total_tokens
        except Exception as e:
            logging.warning(f"Token counting failed: {e}")
            return -1
    
    def generate_content(
        self, 
        prompt: str, 
        generation_config: dict = None, 
        retries: int = None,
        caller: str = "unknown"
    ) -> str:
        """
        Generates content using the LLM with enhanced quota management.
        
        Args:
            prompt: The prompt to send to the LLM
            generation_config: Optional generation parameters
            retries: Number of retries (defaults to self.max_retries)
            caller: Name of the calling agent for logging
        
        Returns:
            Generated text or None if failed
        """
        retries = retries or self.max_retries
        
        if generation_config is None:
            generation_config = {
                "temperature": 0.9,
                "top_p": 0.95,
                "max_output_tokens": 8192,
            }
        
        # Count tokens before request
        input_tokens = self.count_tokens(prompt)
        if input_tokens > 0:
            logging.info(f"[{caller}] Input tokens: {input_tokens}")
        
        # Enforce rate limiting
        self._wait_for_rate_limit()
        
        start_time = time.time()
        
        for attempt in range(retries):
            try:
                self.last_call_time = time.time()
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings
                )
                
                # Calculate metrics
                latency = time.time() - start_time
                output_tokens = len(response.text.split()) * 1.3  # Rough estimate
                
                # Update tracking
                self.total_requests += 1
                self.total_input_tokens += input_tokens if input_tokens > 0 else 0
                self.total_output_tokens += int(output_tokens)
                
                # Log success
                self.api_logger.info(
                    f"{caller} | SUCCESS | "
                    f"in:{input_tokens} | out:~{int(output_tokens)} | "
                    f"latency:{latency:.1f}s | "
                    f"total_reqs:{self.total_requests}"
                )
                
                return response.text
                
            except Exception as e:
                error_str = str(e)
                latency = time.time() - start_time
                
                # Log error
                self.api_logger.info(
                    f"{caller} | ERROR | attempt:{attempt+1}/{retries} | "
                    f"latency:{latency:.1f}s | error:{error_str[:100]}"
                )
                
                logging.error(f"Error generating content (attempt {attempt+1}/{retries}): {e}")
                
                if "429" in error_str or "quota" in error_str.lower():
                    # Rate limited - use extended backoff
                    delay = min(2 ** (attempt + 2), 60)  # 4s, 8s, 16s, 32s, 60s max
                    logging.warning(f"Rate limit hit. Waiting {delay} seconds...")
                    self.api_logger.info(f"{caller} | RATE_LIMITED | waiting:{delay}s")
                    time.sleep(delay)
                elif attempt < retries - 1:
                    time.sleep(1)
                else:
                    logging.error("Failed to generate content after multiple retries.")
                    return None
        
        return None
    
    def get_usage_stats(self) -> dict:
        """Return current session usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_total_tokens": self.total_input_tokens + self.total_output_tokens
        }
