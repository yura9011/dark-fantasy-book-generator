import React from 'react';
import ReactMarkdown from 'react-markdown';
import './LoreViewer.css';

const LoreViewer = ({ loreState, markdown, onBack }) => {
    // If we have markdown, display it directly
    if (markdown) {
        return (
            <div className="lore-viewer">
                <div className="lore-viewer-header">
                    <h2>📜 {loreState?.project_name || 'Game Lore Bible'}</h2>
                    {loreState?.variety_seeds && (
                        <div className="lore-seeds-info">
                            <span className="seed-tag">🌍 {loreState.variety_seeds.name_cultures?.join(', ')}</span>
                            <span className="seed-tag">💭 {loreState.variety_seeds.emotion_seed}</span>
                            <span className="seed-tag">🎨 {loreState.variety_seeds.aesthetic_seed}</span>
                        </div>
                    )}
                    <button className="lore-back-btn" onClick={onBack}>← New Generation</button>
                </div>

                <div className="lore-markdown-content">
                    <ReactMarkdown>{markdown}</ReactMarkdown>
                </div>
            </div>
        );
    }

    // Fallback: Structured view from state
    if (!loreState) {
        return <div className="lore-viewer">No lore data available.</div>;
    }

    return (
        <div className="lore-viewer">
            <div className="lore-viewer-header">
                <h2>📜 {loreState.project_name || 'Game Lore Bible'}</h2>
                <button className="lore-back-btn" onClick={onBack}>← New Generation</button>
            </div>

            {/* Variety Seeds Info */}
            {loreState.variety_seeds && (
                <div className="lore-section lore-seeds">
                    <h3>🎲 Generation Seeds</h3>
                    <div className="seeds-grid">
                        <div className="seed-item">
                            <strong>Cultures:</strong> {loreState.variety_seeds.name_cultures?.join(', ')}
                        </div>
                        <div className="seed-item">
                            <strong>Emotion:</strong> {loreState.variety_seeds.emotion_seed}
                        </div>
                        <div className="seed-item">
                            <strong>Aesthetic:</strong> {loreState.variety_seeds.aesthetic_seed}
                        </div>
                        <div className="seed-item">
                            <strong>Conflict:</strong> {loreState.variety_seeds.conflict_seed}
                        </div>
                        <div className="seed-item">
                            <strong>Inspiration:</strong> {loreState.variety_seeds.game_reference}
                        </div>
                    </div>
                </div>
            )}

            {/* Cosmology */}
            {loreState.cosmology && Object.keys(loreState.cosmology).length > 0 && (
                <div className="lore-section">
                    <h3>🌌 Cosmology</h3>
                    <div className="lore-card">
                        {loreState.cosmology.creation_myth && (
                            <p><strong>Creation:</strong> {loreState.cosmology.creation_myth}</p>
                        )}
                        {loreState.cosmology.divine_forces && (
                            <p><strong>Divine Forces:</strong> {loreState.cosmology.divine_forces}</p>
                        )}
                        {loreState.cosmology.forbidden_knowledge && (
                            <p><strong>Forbidden Knowledge:</strong> {loreState.cosmology.forbidden_knowledge}</p>
                        )}
                    </div>
                </div>
            )}

            {/* Eras */}
            {loreState.eras && loreState.eras.length > 0 && (
                <div className="lore-section">
                    <h3>⏳ Historical Eras</h3>
                    <div className="lore-grid">
                        {loreState.eras.map((era, index) => (
                            <div key={index} className={`lore-card ${era.is_cataclysm ? 'cataclysm' : ''}`}>
                                <h4>{era.name} {era.is_cataclysm && '⚠️'}</h4>
                                <span className="era-duration">{era.duration}</span>
                                <p>{era.summary}</p>
                                {era.defining_event && <p className="key-detail"><strong>Key Event:</strong> {era.defining_event}</p>}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Factions */}
            {loreState.factions && loreState.factions.length > 0 && (
                <div className="lore-section">
                    <h3>⚔️ Factions</h3>
                    <div className="lore-grid">
                        {loreState.factions.map((faction, index) => (
                            <div key={index} className="lore-card">
                                <h4>{faction.name}</h4>
                                <span className="faction-type">{faction.type}</span>
                                <p><strong>Ideology:</strong> {faction.ideology}</p>
                                {faction.hidden_truth && <p className="secret"><strong>Hidden Truth:</strong> {faction.hidden_truth}</p>}
                                {faction.dark_secret && <p className="secret"><strong>Dark Secret:</strong> {faction.dark_secret}</p>}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Characters */}
            {loreState.characters && loreState.characters.length > 0 && (
                <div className="lore-section">
                    <h3>👤 Characters</h3>
                    <div className="lore-grid">
                        {loreState.characters.map((char, index) => (
                            <div key={index} className="lore-card character-card">
                                <h4>{char.name}</h4>
                                {char.title && <span className="char-title">{char.title}</span>}
                                <p className="char-archetype">{char.archetype}</p>
                                <p><strong>Motivation:</strong> {char.motivation}</p>
                                {char.inner_demon && <p className="char-demon"><strong>Inner Demon:</strong> {char.inner_demon}</p>}
                                {char.fate_by_route && (
                                    <div className="char-fates">
                                        <strong>Fates:</strong>
                                        <ul>
                                            <li><span className="route-light">Light:</span> {char.fate_by_route.light}</li>
                                            <li><span className="route-shadow">Shadow:</span> {char.fate_by_route.shadow}</li>
                                            <li><span className="route-neutral">Neutral:</span> {char.fate_by_route.neutral}</li>
                                        </ul>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Conflicts */}
            {loreState.conflicts && loreState.conflicts.length > 0 && (
                <div className="lore-section">
                    <h3>🔥 Conflicts</h3>
                    <div className="lore-grid">
                        {loreState.conflicts.map((conflict, index) => (
                            <div key={index} className="lore-card conflict-card">
                                <h4>{conflict.name}</h4>
                                <span className="conflict-type">{conflict.type}</span>
                                {conflict.root_cause && <p><strong>Root Cause:</strong> {conflict.root_cause}</p>}
                                {conflict.tragedy && <p className="tragedy"><strong>Tragedy:</strong> {conflict.tragedy}</p>}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Routes */}
            {loreState.routes && Object.keys(loreState.routes).some(k => loreState.routes[k]?.name) && (
                <div className="lore-section">
                    <h3>🛤️ Story Routes</h3>
                    <div className="routes-container">
                        {Object.entries(loreState.routes).map(([key, route]) => (
                            route.name && (
                                <div key={key} className={`route-card route-${key}`}>
                                    <h4>{route.name}</h4>
                                    {route.philosophy && <p className="route-philosophy">{route.philosophy}</p>}
                                    {route.sacrifice && <p><strong>Sacrifice:</strong> {route.sacrifice}</p>}
                                    {route.ending && (
                                        <div className="route-ending">
                                            <strong>Ending:</strong>
                                            {typeof route.ending === 'object'
                                                ? ` ${route.ending.name} - ${route.ending.description}`
                                                : ` ${route.ending}`
                                            }
                                        </div>
                                    )}
                                </div>
                            )
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoreViewer;
