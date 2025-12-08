import React, { useState, useEffect } from 'react';
import '../../styles/global.css';

const ReviewDashboard = ({ state, onContinue }) => {
    const [editableState, setEditableState] = useState(state);
    const [activeTab, setActiveTab] = useState('concept'); // Default to concept if available, otherwise world

    useEffect(() => {
        setEditableState(state);
        if (state.concept && state.concept.logline && activeTab === 'world') {
            // If we have concept data but tab is world (default), switch to concept? 
            // Logic in App.js sets reviewMode, we can use that to pass a prop 'initialTab'
        }
    }, [state, activeTab]);

    const handleCharacterChange = (index, field, value) => {
        const newChars = [...editableState.characters];
        newChars[index] = { ...newChars[index], [field]: value };
        setEditableState({ ...editableState, characters: newChars });
    };

    const handleLocationChange = (index, field, value) => {
        const newWorld = { ...editableState.world_bible };
        const newLocs = [...newWorld.locations];
        newLocs[index] = { ...newLocs[index], [field]: value };
        newWorld.locations = newLocs;
        setEditableState({ ...editableState, world_bible: newWorld });
    };

    const handleConceptChange = (field, value) => {
        const newConcept = { ...editableState.concept, [field]: value };
        // Sync title/keywords to legacy fields for backend compat
        const updates = { concept: newConcept };
        if (field === 'title') updates.book_title = value;
        if (field === 'themes') updates.theme_keywords = value; // Needs array handling if text input

        setEditableState({ ...editableState, ...updates });
    };

    // Helper for arrays (themes/tone)
    const handleArrayChange = (field, valueStr) => {
        const arr = valueStr.split(',').map(s => s.trim());
        handleConceptChange(field, arr);
    };

    const handleContinue = () => {
        onContinue(editableState);
    };

    return (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
            <h2 style={{ textAlign: 'center', color: 'var(--accent-gold)' }}>Review the Arcane Truths</h2>
            <p style={{ textAlign: 'center', marginBottom: '2rem' }}>Modify the elements before they are woven into reality.</p>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', justifyContent: 'center' }}>
                <button
                    className={`btn-secondary ${activeTab === 'concept' ? 'active' : ''}`}
                    onClick={() => setActiveTab('concept')}
                    style={{ borderColor: activeTab === 'concept' ? 'var(--accent-gold)' : '' }}
                >
                    Concept
                </button>
                <button
                    className={`btn-secondary ${activeTab === 'world' ? 'active' : ''}`}
                    onClick={() => setActiveTab('world')}
                    style={{ borderColor: activeTab === 'world' ? 'var(--accent-gold)' : '' }}
                >
                    World Bible
                </button>
                <button
                    className={`btn-secondary ${activeTab === 'characters' ? 'active' : ''}`}
                    onClick={() => setActiveTab('characters')}
                    style={{ borderColor: activeTab === 'characters' ? 'var(--accent-gold)' : '' }}
                >
                    Characters
                </button>
            </div>

            <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '1rem' }}>
                {activeTab === 'concept' && editableState.concept && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <div className="glass-panel" style={{ padding: '1rem' }}>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Title</label>
                                <input
                                    className="glass-input"
                                    value={editableState.concept.title}
                                    onChange={(e) => handleConceptChange('title', e.target.value)}
                                />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Logline</label>
                                <textarea
                                    className="glass-input"
                                    rows="2"
                                    value={editableState.concept.logline}
                                    onChange={(e) => handleConceptChange('logline', e.target.value)}
                                />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Synopsis</label>
                                <textarea
                                    className="glass-input"
                                    rows="5"
                                    value={editableState.concept.synopsis}
                                    onChange={(e) => handleConceptChange('synopsis', e.target.value)}
                                />
                            </div>
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Themes (comma separated)</label>
                                <input
                                    className="glass-input"
                                    value={editableState.concept.themes?.join(', ')}
                                    onChange={(e) => handleArrayChange('themes', e.target.value)}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Tone (comma separated)</label>
                                <input
                                    className="glass-input"
                                    value={editableState.concept.tone?.join(', ')}
                                    onChange={(e) => handleArrayChange('tone', e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'world' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        <h3 style={{ borderBottom: '1px solid var(--border-glass)' }}>Locations</h3>
                        {editableState.world_bible?.locations?.map((loc, idx) => (
                            <div key={idx} className="glass-panel" style={{ padding: '1rem' }}>
                                <div style={{ marginBottom: '0.5rem' }}>
                                    <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Name</label>
                                    <input
                                        className="glass-input"
                                        value={loc.name}
                                        onChange={(e) => handleLocationChange(idx, 'name', e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Description</label>
                                    <textarea
                                        className="glass-input"
                                        rows="3"
                                        value={loc.description}
                                        onChange={(e) => handleLocationChange(idx, 'description', e.target.value)}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === 'characters' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        {editableState.characters?.map((char, idx) => (
                            <div key={idx} className="glass-panel" style={{ padding: '1rem' }}>
                                <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                                    <div style={{ flex: 1 }}>
                                        <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Name</label>
                                        <input
                                            className="glass-input"
                                            value={char.name}
                                            onChange={(e) => handleCharacterChange(idx, 'name', e.target.value)}
                                        />
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Archetype</label>
                                        <input
                                            className="glass-input"
                                            value={char.archetype}
                                            onChange={(e) => handleCharacterChange(idx, 'archetype', e.target.value)}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>Description</label>
                                    <textarea
                                        className="glass-input"
                                        rows="3"
                                        value={char.description}
                                        onChange={(e) => handleCharacterChange(idx, 'description', e.target.value)}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                <button className="btn-primary" onClick={handleContinue}>Save & Continue Ritual</button>
            </div>
        </div>
    );
};

export default ReviewDashboard;
