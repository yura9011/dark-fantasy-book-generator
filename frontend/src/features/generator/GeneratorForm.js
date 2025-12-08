import React, { useState } from 'react';
import '../../styles/global.css';

const GeneratorForm = ({ onGenerate, isGenerating, initialData }) => {
  const [title, setTitle] = useState('');
  const [themes, setThemes] = useState('');
  const [chapters, setChapters] = useState(3);

  React.useEffect(() => {
    if (initialData) {
      setTitle(initialData.book_title || '');
      setThemes(initialData.theme_keywords ? initialData.theme_keywords.join(', ') : '');
      if (initialData.outline && initialData.outline.chapters) {
        setChapters(initialData.outline.chapters.length || 3);
      }
    }
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const themeList = themes.split(',').map(t => t.trim()).filter(t => t);
    onGenerate({ title, themes: themeList, chapters });
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Incant New Grimoire</h2>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)' }}>Book Title</label>
          <input
            type="text"
            className="glass-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., The Shadow of the Spire"
            required
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)' }}>Themes & Keywords</label>
          <textarea
            className="glass-input"
            value={themes}
            onChange={(e) => setThemes(e.target.value)}
            placeholder="e.g., Dark Magic, Corruption, Redemption (comma separated)"
            rows="3"
            required
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ color: 'var(--accent-gold)', fontFamily: 'var(--font-heading)' }}>Chapter Count: {chapters}</label>
          <input
            type="range"
            min="1"
            max="10"
            value={chapters}
            onChange={(e) => setChapters(parseInt(e.target.value))}
            style={{ accentColor: 'var(--accent-gold)' }}
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={isGenerating}
          style={{ marginTop: '1rem' }}
        >
          {isGenerating ? 'Weaving Fate...' : 'Begin Ritual'}
        </button>
      </form>
    </div>
  );
};

export default GeneratorForm;
