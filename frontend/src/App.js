import React, { useState } from 'react';
import InquiryForm from './features/onboarding/InquiryForm';
import LoreInquiryForm from './features/onboarding/LoreInquiryForm';
import Dashboard from './features/dashboard/Dashboard';
import BookReader from './features/reader/BookReader';
import LoreViewer from './features/reader/LoreViewer';
import ReviewDashboard from './features/dashboard/ReviewDashboard';
import { generateBook, generateLore } from './services/api';
import './styles/global.css';

function App() {
  // Mode selector: 'book' or 'lore'
  const [generatorMode, setGeneratorMode] = useState('book');

  const [isGenerating, setIsGenerating] = useState(false);
  const [bookData, setBookData] = useState(null);
  const [generatedBook, setGeneratedBook] = useState(null);
  const [projectState, setProjectState] = useState(null);
  const [reviewMode, setReviewMode] = useState(null);

  // Lore-specific state
  const [loreData, setLoreData] = useState(null);
  const [generatedLore, setGeneratedLore] = useState(null);
  const [loreMarkdown, setLoreMarkdown] = useState(null);

  const fileInputRef = React.useRef(null);

  // === Book Generation Flow ===
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
    const basicData = {
      book_title: "Pending...",
      themes: [],
      chapters: answers.num_chapters || 3
    };
    setBookData(basicData);
    await runGeneration(basicData, null, 'concept', answers);
  };

  const handleReviewContinue = async (editedState) => {
    if (reviewMode === 'concept') {
      await runGeneration(bookData, editedState, 'world_building');
    } else if (reviewMode === 'world') {
      await runGeneration(bookData, editedState, 'character_creation');
    } else if (reviewMode === 'characters') {
      await runGeneration(bookData, editedState, null);
    }
  };

  // === Lore Generation Flow ===
  const runLoreGeneration = async (data, existingState = null, stopAfter = null) => {
    setIsGenerating(true);
    setGeneratedLore(null);
    setLoreMarkdown(null);

    try {
      const result = await generateLore({
        ...data,
        existingState,
        stopAfter
      });

      if (result.state) {
        setLoreData(result.state);
      }

      if (result.status === "COMPLETE") {
        setGeneratedLore(result.state);
        if (result.markdown) {
          setLoreMarkdown(result.markdown);
        }
      } else if (result.status === "PAUSED") {
        setReviewMode(`lore_${result.phase}`);
        setLoreData(result.state);
      } else if (result.error) {
        alert("Lore generation failed: " + result.error);
      }

    } catch (error) {
      alert("The lore ritual failed: " + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLoreSubmit = async (formData) => {
    setLoreData(formData);
    await runLoreGeneration(formData);
  };

  const handleLoreBack = () => {
    setGeneratedLore(null);
    setLoreMarkdown(null);
    setLoreData(null);
  };

  // === File Management ===
  const handleLoadProject = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const state = JSON.parse(e.target.result);

          // Detect if this is lore or book state
          if (state.eras || state.cosmology || state.routes) {
            setLoreData(state);
            setGeneratedLore(state);
            setGeneratorMode('lore');
            alert("Lore grimoire loaded successfully!");
          } else {
            setProjectState(state);
            alert("Book grimoire loaded successfully. You can now resume the ritual.");
          }
        } catch (err) {
          alert("Failed to read the arcane texts (Invalid JSON).");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleSaveProject = () => {
    const stateToSave = generatorMode === 'lore' ? (generatedLore || loreData) : projectState;

    if (!stateToSave) {
      alert("No grimoire state to save!");
      return;
    }

    const projectName = stateToSave.project_name || stateToSave.book_title || "grimoire";
    const suffix = generatorMode === 'lore' ? '_lore_state' : '_state';

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(stateToSave, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", projectName.replace(/\s+/g, '_') + suffix + ".json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  // === Render ===
  const showModeSelector = !isGenerating && !generatedBook && !generatedLore && !reviewMode;
  const hasAnyState = projectState || generatedLore || loreData;

  return (
    <div className="App">
      <header style={{
        padding: '2rem',
        textAlign: 'center',
        borderBottom: '1px solid var(--border-glass)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '2rem' }}>
          {generatorMode === 'lore' ? '🗡️ Game Lore Generator' : 'Dark Fantasy Generator'}
        </h1>
        <div style={{ gap: '1rem', display: 'flex' }}>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            accept=".json"
            onChange={handleLoadProject}
          />
          <button className="btn-secondary" onClick={() => fileInputRef.current.click()}>
            Load Grimoire
          </button>
          {hasAnyState && (
            <button className="btn-secondary" onClick={handleSaveProject}>
              Save Grimoire
            </button>
          )}
        </div>
      </header>

      <main style={{ padding: '2rem' }}>
        {/* Mode Selector */}
        {showModeSelector && (
          <div className="mode-selector" style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            marginBottom: '2rem'
          }}>
            <button
              className={`mode-btn ${generatorMode === 'book' ? 'active' : ''}`}
              onClick={() => setGeneratorMode('book')}
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 600,
                background: generatorMode === 'book'
                  ? 'linear-gradient(135deg, rgba(90, 24, 154, 0.3), rgba(157, 78, 221, 0.3))'
                  : 'rgba(255, 255, 255, 0.05)',
                border: generatorMode === 'book' ? '2px solid #9d4edd' : '2px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                color: generatorMode === 'book' ? '#e0aaff' : 'var(--text-secondary)',
                cursor: 'pointer'
              }}
            >
              📖 Book Generator
            </button>
            <button
              className={`mode-btn ${generatorMode === 'lore' ? 'active' : ''}`}
              onClick={() => setGeneratorMode('lore')}
              style={{
                padding: '1rem 2rem',
                fontSize: '1rem',
                fontWeight: 600,
                background: generatorMode === 'lore'
                  ? 'linear-gradient(135deg, rgba(90, 24, 154, 0.3), rgba(157, 78, 221, 0.3))'
                  : 'rgba(255, 255, 255, 0.05)',
                border: generatorMode === 'lore' ? '2px solid #9d4edd' : '2px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                color: generatorMode === 'lore' ? '#e0aaff' : 'var(--text-secondary)',
                cursor: 'pointer'
              }}
            >
              🗡️ Game Lore Generator
            </button>
          </div>
        )}

        {/* Book Mode */}
        {generatorMode === 'book' && (
          <>
            {!isGenerating && !generatedBook && !reviewMode && (
              <InquiryForm onSubmit={handleInquirySubmit} isGenerating={isGenerating} />
            )}

            {isGenerating && <Dashboard />}

            {!isGenerating && reviewMode && projectState && (
              <ReviewDashboard
                state={projectState}
                onContinue={handleReviewContinue}
              />
            )}

            {generatedBook && (
              <BookReader content={generatedBook} title={bookData?.title} />
            )}
          </>
        )}

        {/* Lore Mode */}
        {generatorMode === 'lore' && (
          <>
            {!isGenerating && !generatedLore && !reviewMode && (
              <LoreInquiryForm onSubmit={handleLoreSubmit} isGenerating={isGenerating} />
            )}

            {isGenerating && (
              <Dashboard message="Weaving the threads of fate..." />
            )}

            {generatedLore && (
              <LoreViewer
                loreState={generatedLore}
                markdown={loreMarkdown}
                onBack={handleLoreBack}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
