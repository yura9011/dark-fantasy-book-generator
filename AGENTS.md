# AGENTS.md

## Welcome, Coding Agent

This file is your primary guide for working on the **Dark Fantasy Book Generator** repository. It outlines the project context, mandatory guidelines, and technical details you need to successfully modify and improve the codebase.

### 1. Project Context

The **Dark Fantasy Book Generator** is a web application that uses a multi-agent AI system to author complete dark fantasy novels.
*   **Frontend:** React (SPA) for user interaction and progress monitoring.
*   **Backend:** Python FastAPI server that orchestrates the novel generation process.
*   **Core Logic:** A sequential pipeline of "Runtime Agents" (LLM wrappers) that build the world, characters, outline, and chapters.

### 2. Mandatory Guidelines

Before writing a single line of code, you **MUST** read and understand the following documents:

*   **`CODING_GUIDELINES.md`**: Contains strict rules on file length (max 500 lines), SRP, modularity, and naming conventions. **These are non-negotiable.**
*   **`technical_specification.md`**: detailed breakdown of the system architecture, data flow, and feature set.

### 3. Architecture Overview

#### Frontend (`frontend/`)
*   **Framework:** React (Create React App).
*   **State:** Local React state manages the UI view (Form, Generating, Result).
*   **Communication:** Polls the backend to get updates on the book generation progress.

#### Backend (`backend/`)
*   **Framework:** FastAPI.
*   **Entry Point:** `main.py` (defines API endpoints).
*   **Logic:** The `OrchestratorAgent` in `agents/orchestrator.py` drives the entire process.
*   **State:** A `StateManager` persists the "World Bible" and progress to JSON files, allowing generation to be paused and resumed.

### 4. Runtime Agent Documentation

When modifying the business logic, you will be interacting with the "Runtime Agents" located in `backend/agents/`. These are the components that actually generate the story.

*   **`OrchestratorAgent` (`orchestrator.py`)**:
    *   **Role:** The Manager.
    *   **Function:** Coordinates the pipeline. It calls other agents in a specific order: Concept -> World -> Characters -> Outline -> Draft -> Edit.
    *   **Key Method:** `start_generation()` manages the loop and saves state after each step.

*   **`ConceptAgent` (`concept_architect.py`)**:
    *   **Role:** The Visionary.
    *   **Function:** refines the user's initial idea into a solid logline and thematic direction before the world is built.

*   **`WorldBuilderAgent` (`world_builder.py`)**:
    *   **Role:** The Geographer/Historian.
    *   **Function:** Generates the "Bible" (locations, lore, magic systems) based on the concept.

*   **`CharacterAgent` (`character_architect.py`)**:
    *   **Role:** The Casting Director.
    *   **Function:** Creates detailed character profiles (motivations, archetypes) that fit into the generated world.

*   **`StoryAgent` (`story_weaver.py`)**:
    *   **Role:** The Author.
    *   **Function:** First creates a chapter-by-chapter outline. Then, iteratively writes the draft for each chapter.

*   **`EditorAgent` (`editor.py`)**:
    *   **Role:** The Editor.
    *   **Function:** Takes the raw draft from the `StoryAgent` and refines it (improving vocabulary, tone, and "show, don't tell").

*   **`StateManager` (`state_manager.py`)**:
    *   **Role:** The Memory.
    *   **Function:** Handles reading/writing the JSON state files. It ensures that if the server crashes, progress is not lost.

### 5. Development Workflow

1.  **Plan:** Always start by analyzing the file structure and creating a plan.
2.  **Verify Environment:**
    *   Backend: Ensure `requirements.txt` is satisfied.
    *   Frontend: Ensure `npm install` has been run.
3.  **Modify & Test:**
    *   When changing the backend, restart the server (`uvicorn main:app --reload`) and test the endpoints.
    *   When changing the frontend, verify the UI components render correctly.
4.  **Verify Code:** Use `read_file` to double-check your changes before submitting.
5.  **Refactor:** If your changes cause a file to exceed 500 lines, **you must refactor immediately** as per `CODING_GUIDELINES.md`.

---
**Go forth and code responsibly.**
