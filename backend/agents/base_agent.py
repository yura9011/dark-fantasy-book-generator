from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.services.llm_service import LLMService
from backend.agents.state_manager import StateManager

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    """
    def __init__(self, llm_service: LLMService, state_manager: StateManager):
        self.llm = llm_service
        self.state_manager = state_manager

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """
        Main processing method for the agent.
        Must be implemented by subclasses.
        """
        pass

    def get_context(self) -> Dict[str, Any]:
        """Helper to get the current state context."""
        return self.state_manager.get_state()

    def extract_json_from_text(self, text: str) -> str:
        """
        Robustly extracts JSON string from text that might contain markdown or other noise.
        """
        text = text.strip()
        
        # Try to find the first { and last }
        start = text.find("{")
        end = text.rfind("}")
        
        if start != -1 and end != -1:
            return text[start : end + 1]
            
        return text
