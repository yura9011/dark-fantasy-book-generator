from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
from backend.agents.orchestrator import OrchestratorAgent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookGenerationRequest(BaseModel):
    book_title: str
    num_chapters: int
    num_subchapters: int  # Kept for compatibility
    plot: str
    keywords: list[str]
    existing_state: Optional[dict] = None  # Optional state to resume from
    stop_after: Optional[str] = None  # Optional: "world_building", "character_creation"
    inquiry_responses: Optional[dict] = None  # Optional: Answers to the Deep Inquiry

@app.post("/generate")
def generate_book(request: BookGenerationRequest):
    # We combine plot and keywords for the themes argument
    themes = request.keywords
    if request.plot:
        themes.append(request.plot)
        
    return generate_book_task(request.book_title, request.num_chapters, themes, request.existing_state, request.stop_after, request.inquiry_responses)

def generate_book_task(book_title: str, num_chapters: int, themes: list[str], existing_state: dict = None, stop_after: str = None, inquiry_responses: dict = None):
    logging.basicConfig(level=logging.INFO)
    try:
        orchestrator = OrchestratorAgent()
        
        if existing_state:
            logging.info("Resuming from existing state...")
            orchestrator.state_manager.set_state(existing_state)
            
        book_content = orchestrator.start_generation(
            book_title=book_title,
            themes=themes,
            num_chapters=num_chapters,
            stop_after=stop_after,
            inquiry_responses=inquiry_responses
        )
        
        # Get final state to return to client
        final_state = orchestrator.state_manager.get_state()
        
        return {
            "book_content": book_content,
            "book_state": final_state
        }
    except Exception as e:
        logging.error(f"Generation failed: {e}")
        return {"error": str(e)}


# === Lore Generation ===

from backend.agents.lore_orchestrator import LoreOrchestratorAgent

class LoreGenerationRequest(BaseModel):
    project_name: str
    num_eras: int = 4
    num_factions: int = 5
    num_characters: int = 6
    num_conflicts: int = 4
    num_chapters_per_route: int = 5
    existing_state: Optional[dict] = None
    stop_after: Optional[str] = None  # "eras", "factions", "characters", "conflicts", "routes"


@app.post("/generate-lore")
def generate_lore(request: LoreGenerationRequest):
    """Generate game lore with branching narratives."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        orchestrator = LoreOrchestratorAgent()
        
        result = orchestrator.start_generation(
            project_name=request.project_name,
            num_eras=request.num_eras,
            num_factions=request.num_factions,
            num_characters=request.num_characters,
            num_conflicts=request.num_conflicts,
            num_chapters_per_route=request.num_chapters_per_route,
            stop_after=request.stop_after,
            existing_state=request.existing_state
        )
        
        # Generate markdown export
        if result.get("status") == "COMPLETE":
            result["markdown"] = orchestrator.export_to_markdown()
        
        return result
        
    except Exception as e:
        logging.error(f"Lore generation failed: {e}")
        return {"error": str(e), "status": "ERROR"}

