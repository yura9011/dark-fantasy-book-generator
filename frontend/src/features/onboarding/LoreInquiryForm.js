import React, { useState } from 'react';
import './LoreInquiryForm.css';

const LoreInquiryForm = ({ onSubmit, isGenerating }) => {
    const [formData, setFormData] = useState({
        project_name: '',
        num_eras: 4,
        num_factions: 5,
        num_characters: 6,
        num_conflicts: 4,
        num_chapters_per_route: 5
    });

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? (parseInt(value, 10) || 0) : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.project_name.trim()) {
            alert('Please enter a project name');
            return;
        }
        onSubmit(formData);
    };

    return (
        <div className="lore-inquiry-form">
            <div className="lore-form-header">
                <h2>🗡️ Game Lore Generator</h2>
                <p className="lore-subtitle">
                    Create branching narratives inspired by Tactics Ogre, FF6, and Vagrant Story.
                    <br />
                    <span className="lore-hint">Dark fantasy with moral complexity, multiple routes, and emotional depth.</span>
                </p>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="lore-form-section">
                    <label htmlFor="project_name">
                        <span className="label-icon">📜</span>
                        Project Name
                    </label>
                    <input
                        type="text"
                        id="project_name"
                        name="project_name"
                        value={formData.project_name}
                        onChange={handleChange}
                        placeholder="Chronicles of the Shattered Crown"
                        required
                    />
                </div>

                <div className="lore-form-grid">
                    <div className="lore-form-section">
                        <label htmlFor="num_eras">
                            <span className="label-icon">⏳</span>
                            Historical Eras
                        </label>
                        <input
                            type="number"
                            id="num_eras"
                            name="num_eras"
                            value={formData.num_eras}
                            onChange={handleChange}
                            min="2"
                            max="8"
                        />
                        <span className="field-hint">From creation to present day</span>
                    </div>

                    <div className="lore-form-section">
                        <label htmlFor="num_factions">
                            <span className="label-icon">⚔️</span>
                            Factions
                        </label>
                        <input
                            type="number"
                            id="num_factions"
                            name="num_factions"
                            value={formData.num_factions}
                            onChange={handleChange}
                            min="2"
                            max="10"
                        />
                        <span className="field-hint">Kingdoms, orders, guilds</span>
                    </div>

                    <div className="lore-form-section">
                        <label htmlFor="num_characters">
                            <span className="label-icon">👤</span>
                            Main Characters
                        </label>
                        <input
                            type="number"
                            id="num_characters"
                            name="num_characters"
                            value={formData.num_characters}
                            onChange={handleChange}
                            min="3"
                            max="12"
                        />
                        <span className="field-hint">With route-dependent fates</span>
                    </div>

                    <div className="lore-form-section">
                        <label htmlFor="num_conflicts">
                            <span className="label-icon">🔥</span>
                            Major Conflicts
                        </label>
                        <input
                            type="number"
                            id="num_conflicts"
                            name="num_conflicts"
                            value={formData.num_conflicts}
                            onChange={handleChange}
                            min="2"
                            max="8"
                        />
                        <span className="field-hint">Wars, betrayals, dilemmas</span>
                    </div>

                    <div className="lore-form-section">
                        <label htmlFor="num_chapters_per_route">
                            <span className="label-icon">📖</span>
                            Chapters per Route
                        </label>
                        <input
                            type="number"
                            id="num_chapters_per_route"
                            name="num_chapters_per_route"
                            value={formData.num_chapters_per_route}
                            onChange={handleChange}
                            min="3"
                            max="10"
                        />
                        <span className="field-hint">For each branching path</span>
                    </div>
                </div>

                <div className="lore-form-info">
                    <h4>What You'll Get</h4>
                    <ul>
                        <li><strong>Eras & Cosmology</strong> - Creation myths, historical epochs, cataclysms</li>
                        <li><strong>Factions</strong> - Complex political entities with hidden agendas</li>
                        <li><strong>Characters</strong> - Jungian archetypes with moral depth</li>
                        <li><strong>Conflicts</strong> - Wars with no heroes, dilemmas with no right answer</li>
                        <li><strong>Branching Routes</strong> - Light, Shadow, Neutral paths with unique endings</li>
                    </ul>
                </div>

                <button
                    type="submit"
                    className="lore-submit-btn"
                    disabled={isGenerating}
                >
                    {isGenerating ? 'Weaving Lore...' : '🌑 Begin the Ritual'}
                </button>
            </form>
        </div>
    );
};

export default LoreInquiryForm;
