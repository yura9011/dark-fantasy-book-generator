import React from 'react';
import ReactMarkdown from 'react-markdown';
import '../../styles/global.css';

const BookReader = ({ content, title }) => {
    if (!content) return null;

    return (
        <div className="glass-panel" style={{
            padding: '4rem',
            maxWidth: '800px',
            margin: '2rem auto',
            backgroundColor: 'rgba(20, 20, 20, 0.85)', // Slightly more opaque for reading
            minHeight: '80vh'
        }}>
            <div style={{ textAlign: 'center', marginBottom: '4rem', borderBottom: '1px solid var(--border-gold)', paddingBottom: '2rem' }}>
                <h1 style={{ fontSize: '4rem', marginBottom: '1rem' }}>{title}</h1>
                <p style={{ color: 'var(--accent-gold)', fontStyle: 'italic', fontFamily: 'var(--font-book)' }}>
                    A Dark Fantasy Chronicle
                </p>
            </div>

            <div style={{
                fontFamily: 'var(--font-book)',
                fontSize: '1.1rem',
                lineHeight: '1.8',
                color: '#d0d0d0',
                textAlign: 'justify'
            }}>
                <ReactMarkdown
                    components={{
                        h1: ({ node, ...props }) => <h2 style={{ color: 'var(--accent-gold)', marginTop: '3rem', borderBottom: '1px solid var(--border-glass)' }} {...props} />,
                        h2: ({ node, ...props }) => <h3 style={{ color: 'var(--text-primary)', marginTop: '2rem' }} {...props} />,
                        p: ({ node, ...props }) => <p style={{ marginBottom: '1.5rem' }} {...props} />,
                        strong: ({ node, ...props }) => <strong style={{ color: 'var(--accent-gold)' }} {...props} />,
                    }}
                >
                    {content}
                </ReactMarkdown>
            </div>
        </div>
    );
};

export default BookReader;
