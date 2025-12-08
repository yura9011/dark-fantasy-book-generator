import React, { useState } from 'react';
import '../../styles/global.css';

const InquiryForm = ({ onSubmit, isGenerating }) => {
    const [answers, setAnswers] = useState({
        ghost: "",
        lie: "",
        texture: "",
        sin: "",
        running_from: "",
        num_chapters: 3
    });

    const handleChange = (e) => {
        setAnswers({
            ...answers,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(answers);
    };

    return (
        <div className="glass-panel" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
            <h2 style={{ textAlign: 'center', color: 'var(--accent-gold)', marginBottom: '1rem' }}>The Inquiry</h2>
            <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                To weave a true spell, we must know the soul of the story. Answer these abstract riddles.
            </p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                <div className="form-group">
                    <label>What is the 'Ghost' that haunts this world? (Metaphorical or literal)</label>
                    <textarea
                        className="glass-input"
                        name="ghost"
                        value={answers.ghost}
                        onChange={handleChange}
                        placeholder="e.g., The memory of a sun that no longer shines..."
                        rows="2"
                    />
                </div>

                <div className="form-group">
                    <label>What Lie does everyone believe is the Truth?</label>
                    <textarea
                        className="glass-input"
                        name="lie"
                        value={answers.lie}
                        onChange={handleChange}
                        placeholder="e.g., That the walls keep us safe, rather than imprisoned..."
                        rows="2"
                    />
                </div>

                <div className="form-group">
                    <label>If this story were a texture or a feeling, what would it be?</label>
                    <input
                        className="glass-input"
                        name="texture"
                        value={answers.texture}
                        onChange={handleChange}
                        placeholder="e.g., Cold velvet, broken glass in honey..."
                    />
                </div>

                <div className="form-group">
                    <label>What is the most cardinal sin in this universe?</label>
                    <input
                        className="glass-input"
                        name="sin"
                        value={answers.sin}
                        onChange={handleChange}
                        placeholder="e.g., Hope..."
                    />
                </div>

                <div className="form-group">
                    <label>The protagonist is running from...</label>
                    <input
                        className="glass-input"
                        name="running_from"
                        value={answers.running_from}
                        onChange={handleChange}
                        placeholder="e.g., Their own shadow..."
                    />
                </div>

                <div className="form-group">
                    <label>Length of the Ritual (Chapters)</label>
                    <input
                        type="number"
                        className="glass-input"
                        name="num_chapters"
                        value={answers.num_chapters || 3}
                        onChange={handleChange}
                        min="1"
                        max="20"
                        style={{ width: '100px' }}
                    />
                </div>

                <button
                    type="submit"
                    className={`btn-primary ${isGenerating ? 'loading' : ''}`}
                    disabled={isGenerating}
                    style={{ marginTop: '1rem' }}
                >
                    {isGenerating ? 'Consulting the Void...' : 'Invoke the Concept'}
                </button>
            </form>
        </div>
    );
};

export default InquiryForm;
