import React, { useState } from 'react';
import InquiryForm from './features/onboarding/InquiryForm';
import Dashboard from './features/dashboard/Dashboard';
import BookReader from './features/reader/BookReader';
import ReviewDashboard from './features/dashboard/ReviewDashboard';
import { generateBook } from './services/api';
import './styles/global.css';

function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [bookData, setBookData] = useState(null);
  const [generatedBook, setGeneratedBook] = useState(null);
  const [projectState, setProjectState] = useState(null);
  const [reviewMode, setReviewMode] = useState(null); // 'world' or 'characters' or null
  const fileInputRef = React.useRef(null);

  const runGeneration = async (data, currentState, stopAfter, inquiryResponses) => {
    setIsGenerating(true);
    setGeneratedBook(null);
    setReviewMode(null);

    try {
      const requestData = {
        ...data,
        existingState: currentState,
        stopAfter: stopAfter,
        inquiry_responses: inquiryResponses
      };
      const result = await generateBook(requestData);

      if (result.book_state) {
        setProjectState(result.book_state);
      }

      if (result.book_content === "PAUSED") {
        if (stopAfter === 'concept') setReviewMode('concept');
        if (stopAfter === 'world_building') setReviewMode('world');
        if (stopAfter === 'character_creation') setReviewMode('characters');
      } else {
        setGeneratedBook(result.book_content);
      }

    } catch (error) {
      alert("The ritual failed: " + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleInquirySubmit = async (answers) => {
    // Concept phase
    const basicData = {
      book_title: "Pending...",
      themes: [],
      chapters: answers.num_chapters || 3
    };
    setBookData(basicData);
    await runGeneration(basicData, null, 'concept', answers);
  };

  // Legacy restart or continue handler
  const handleReviewContinue = async (editedState) => {
    // Determine next step based on current review mode
    if (reviewMode === 'concept') {
      // Concept approved -> World Building
      await runGeneration(bookData, editedState, 'world_building');
    } else if (reviewMode === 'world') {
      await runGeneration(bookData, editedState, 'character_creation');
    } else if (reviewMode === 'characters') {
      await runGeneration(bookData, editedState, null); // Finish
    }
  };

  const handleLoadProject = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const state = JSON.parse(e.target.result);
          setProjectState(state);
          // If state has outline, it's done or in progress. 
          // If only world, we might want to review? 
          // For now, just load it into form.
          alert("Grimoire loaded successfully. You can now resume the ritual.");
        } catch (err) {
          alert("Failed to read the arcane texts (Invalid JSON).");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleSaveProject = () => {
    if (!projectState) {
      alert("No grimoire state to save!");
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(projectState, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", (projectState.book_title || "grimoire") + "_state.json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="App">
      <header style={{ padding: '2rem', textAlign: 'center', borderBottom: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '2rem' }}>Dark Fantasy Generator</h1>
        <div style={{ gap: '1rem', display: 'flex' }}>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            accept=".json"
            onChange={handleLoadProject}
          />
          <button className="btn-secondary" onClick={() => fileInputRef.current.click()}>Load Grimoire</button>
          {projectState && (
            <button className="btn-secondary" onClick={handleSaveProject}>Save Grimoire</button>
          )}
        </div>
      </header>

      <main style={{ padding: '2rem' }}>
        {!isGenerating && !generatedBook && !reviewMode && (
          <InquiryForm onSubmit={handleInquirySubmit} isGenerating={isGenerating} />
        )}

        {isGenerating && (
          <Dashboard />
        )}

        {!isGenerating && reviewMode && projectState && (
          <ReviewDashboard
            state={projectState}
            onContinue={handleReviewContinue}
          />
        )}

        {generatedBook && (
          <BookReader content={generatedBook} title={bookData?.title} />
        )}
      </main>
    </div>
  );
}

export default App;
