import logging
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.orchestrator import OrchestratorAgent

load_dotenv()

def verify_agents():
    logging.basicConfig(level=logging.INFO)
    
    print("--- Starting Verification ---")
    
    try:
        orchestrator = OrchestratorAgent()
        
        # Test with a very short generation
        book_title = "The Shadow of the Spire"
        themes = ["Dark Magic", "Corruption", "Redemption"]
        
        print(f"Generating '{book_title}'...")
        
        # We'll just run the first steps manually to avoid full cost/time if possible, 
        # but Orchestrator is monolithic right now. 
        # Let's run a 1-chapter generation.
        
        result = orchestrator.start_generation(
            book_title=book_title,
            themes=themes,
            num_chapters=1
        )
        
        print("\n--- Generation Complete ---")
        print(f"Result length: {len(result)} chars")
        print("First 500 chars:")
        print(result[:500])
        
        if "# The Shadow of the Spire" in result and "Chapter 1" in result:
            print("\nSUCCESS: Basic structure found.")
        else:
            print("\nFAILURE: Basic structure missing.")
            
    except Exception as e:
        print(f"\nFAILURE: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_agents()
