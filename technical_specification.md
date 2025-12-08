# Technical Specification: Dark Fantasy Book Generator

## 1. Core Purpose
The **Dark Fantasy Book Generator** is an AI-powered automated creative writing system designed to author complete, coherent, and atmospherically consistent dark fantasy novels. It solves the challenge of long-form narrative generation by decomposing the writing process into specialized, sequential tasks handled by distinct AI agents.

The application allows users to provide a high-level seed (title, themes) and monitors the autonomous creation of a "Bible" (world, characters) followed by the chapter-by-chapter drafting and editing of a novel.

## 2. Main Features

### User-Facing Features
- **Project Generation**: Users input a title, themes, and desired chapter count to start a new project.
- **Progress Dashboard**: Visual feedback during generation (though currently simplified to a "generating" state).
- **Save/Load System**:
    - **Save Grimoire**: Exports the entire project state (world data, characters, text) to a JSON file.
    - **Load Grimoire**: Restores a project from a JSON file to resume generation or review content.
- **Book Reader**: Built-in markdown renderer to read the generated novel comfortably in the browser.

### Backend Logic & Automation
- **Multi-Agent Orchestration**: A central `Orchestrator` agent manages specialized sub-agents (`WorldBuilder`, `CharacterArchitect`, `StoryWeaver`, `Editor`).
- **State Persistence**: A `StateManager` maintains the "Truth" of the story (The Bible) and autosaves progress after every chapter to prevent data loss.
- **Resumable Workflow**: The system intelligently skips already completed production steps (e.g., if the World is built, it proceeds to Character creation) when resuming a project.
- **AI-Powered Editing**: An `Editor` agent performs post-processing on drafts to improve tone, "show, don't tell" adherence, and vocabulary.

### Configuration
- **Model Selection**: Configurable via `config.yaml` (defaulting to Google's Gemini 1.5/2.0 models).
- **Safety & Filtering**: Uses `restricted_words.txt` to enforce stylistic constraints and safety settings for the LLM.

## 3. Functional Behavior

### Input Methods
- **Web Form**: React-based UI for fresh inputs.
- **JSON Upload**: File upload for resuming state.

### Processing Flow (Sequential)
1.  **Initialization**: `Orchestrator` initializes `StateManager`. If resuming, state is injected.
2.  **World Building**: `WorldBuilderAgent` generates locations, lore, and magic references if not already present.
3.  **Character Creation**: `CharacterAgent` defines main characters using Jungian archetypes found in prompts.
4.  **Outlining**: `StoryAgent` creates a chapter-by-chapter outline based on the world and characters.
5.  **Drafting & Editing (Loop)**:
    - `StoryAgent` drafts Chapter X.
    - `EditorAgent` refines Chapter X.
    - `StateManager` saves Chapter X content and updates progress.
    - Loop continues until all chapters are complete.
6.  **Finalization**: The complete book is compiled into a single Markdown file.

### Error Handling
- **Graceful Failure**: If generation fails, the backend logs the error. The state is saved after every successful chapter, ensuring partial progress is preserved.
- **Validation**: JSON responses from the LLM are parsed and cleaned; fallback empty structures are used if parsing fails repeatedly.

## 4. Architecture Overview

### System Structure
The application follows a **Client-Server** architecture with an **Agentic Backend**.

- **Frontend**: A React SPA (Single Page Application).
    - **`App.js`**: Main state controller (generating, viewing, loaded project state).
    - **`services/api.js`**: Communication layer with the backend.
- **Backend**: A Python FastAPI server (`main.py`).
    - **`OrchestratorAgent`**: The "Manager" that calls other agents in order.
    - **`StateManager`**: The "Memory" that stores the JSON state.
    - **`LLMService`**: The "Interface" to Google Gemini API.

### Data Flow
1.  **User** -> **React UI** -> **FastAPI (`/generate`)**
2.  **FastAPI** -> **Orchestrator** -> **LLM Service** -> **Gemini API**
3.  **Gemini API** -> **LLM Service** -> **Agents** (Processing) -> **StateManager**
4.  **StateManager** -> **File System (`.json`, `.md`)** -> **React UI** (via API response)

### Key Integrations
- **Google Gemini API**: The core intelligence engine.
- **FastAPI**: The web server framework.

## 5. User Interaction Model

- **One-Shot Initiation**: The user sets parameters once and starts the process.
- **Passive Monitoring**: The user waits while the backend processes (long-running task).
- **Intervention**: The user can stop the process (by closing/refreshing) and later resume if they saved the state file.
- **Output Consumption**: The user reads the final output in the web view.

**Constraints**:
- Users cannot currently "interrupt" the AI to give feedback on a specific chapter mid-generation.
- Users cannot manually edit the "World Bible" before the story begins.

## 6. Internal Rules & Constraints

- **Sequential Dependency**: Chapters are generated in order (1, 2, 3...) because Chapter N depends on the context of the Outline.
- **JSON Strictness**: Agents rely on the LLM returning valid JSON for structured data (World, Characters). Failures here can block the pipeline.
- **Stateless API Calls**: The LLM itself is stateless; all context (World Bible, previous summaries) must be re-injected into the prompt for every new generation request.

## 7. Known Issues & Limitations

- **Context Window Limits**: Extremely long books might exceed the context window if the entire history is fed back into the LLM. The current system summarizes/truncates context but may lose nuance over time.
- **Feedback Loop**: There is no "Human-in-the-Loop" feature to approve the Character list before writing starts.
- **Error Recovery**: If an API call hangs indefinitely, the frontend may timeout even if the backend is working.

## 8. Suggested Next Updates

### Feature Improvements
- **Human-in-the-Loop Review**: Add a UI step where the generation pauses after "World Building" and "Character Creation" to let the user edit the JSON data before the story writing begins.
- **Custom Prompts**: Allow users to edit the standard prompts (`prompt_*.txt`) directly from the settings menu.

### UX Upgrades
- **Granular Progress Bar**: Update the frontend to show exactly which step (e.g., "Writing Chapter 2/10") is active, pushed via WebSocket or polling.

### Stability & Performance
- **Streaming Responses**: Implement Server-Sent Events (SSE) to stream the text generation to the frontend in real-time, improving perceived performance.
