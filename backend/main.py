from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    num_subchapters: int # Kept for compatibility
    plot: str
    keywords: list[str]
    existing_state: dict = None # Optional state to resume from
    stop_after: str = None # Optional: "world_building", "character_creation"
    inquiry_responses: dict = None # Optional: Answers to the Deep Inquiry

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
