import React from 'react';
import '../../styles/global.css';

const Dashboard = () => {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '50vh',
            gap: '2rem'
        }}>
            <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
                <h3 style={{ color: 'var(--accent-gold)' }}>Orchestrating Dark Forces...</h3>
                <p style={{ color: 'var(--text-secondary)' }}>The agents are weaving your fate.</p>

                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <div className="glass-panel" style={{ padding: '1rem', width: '150px' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>WORLD BUILDER</div>
                        <div style={{ color: 'var(--accent-crimson)' }}>Active</div>
                    </div>
                    <div className="glass-panel" style={{ padding: '1rem', width: '150px' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CHARACTER AGENT</div>
                        <div style={{ color: 'var(--text-secondary)' }}>Waiting...</div>
                    </div>
                    <div className="glass-panel" style={{ padding: '1rem', width: '150px' }}>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>STORY WEAVER</div>
                        <div style={{ color: 'var(--text-secondary)' }}>Waiting...</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
