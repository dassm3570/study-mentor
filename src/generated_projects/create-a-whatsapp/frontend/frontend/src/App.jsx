import React, { useState, useEffect } from 'react';

const blueprint = {
  "Executive Summary": "This blueprint outlines the development of a state-of-the-art solution for: 'create a whatsapp'. Designed with modern scalability, security, and modularity in mind, the system leverages FastAPI, React, TailwindCSS and a PostgreSQL database to deliver a seamless user experience.",
  "System Architecture": "The application is structured as a decoupled client-server architecture. The frontend communicates with the backend via RESTful APIs. It includes an API Gateway, an Application Server running on FastAPI, React, TailwindCSS, and a PostgreSQL database instance.",
  "Folder Structure": "project-root/\n\u251c\u2500\u2500 backend/\n\u2502   \u251c\u2500\u2500 app/\n\u2502   \u2502   \u251c\u2500\u2500 api/\n\u2502   \u2502   \u251c\u2500\u2500 core/\n\u2502   \u2502   \u251c\u2500\u2500 models/\n\u2502   \u2502   \u2514\u2500\u2500 main.py\n\u2502   \u2514\u2500\u2500 Dockerfile\n\u251c\u2500\u2500 frontend/\n\u2502   \u251c\u2500\u2500 src/\n\u2502   \u2502   \u251c\u2500\u2500 components/\n\u2502   \u2502   \u2514\u2500\u2500 pages/\n\u2502   \u2514\u2500\u2500 package.json\n\u2514\u2500\u2500 docker-compose.yml",
  "Backend Components": "Built using FastAPI, React, TailwindCSS. Key modules include: Authentication & Authorization (JWT), Core Controller, Database Connector, and external service integrations.",
  "Frontend Components": "Interactive UI components built to support 'create a whatsapp'. Includes: Dashboard, User Settings, Goal Management Panel, and real-time visualization widgets.",
  "Database Schema": "Configured for a PostgreSQL database. Includes 'users', 'sessions', 'tasks', and 'history' tables with foreign key constraints.",
  "API Endpoints": "POST /api/v1/auth/login - User authentication\nGET /api/v1/tasks - Retrieve active tasks\nPOST /api/v1/tasks - Create a new task\nGET /api/v1/health - Service health status",
  "Agent Workflow": "1. User submits stimulus -> 2. Agent classifies intent -> 3. Agent creates plan -> 4. Executed by specialized engines -> 5. Output returned to user.",
  "Shared Memory Design": "Uses Redis for fast short-term memory / session caching, and the primary SQL database for long-term audit logs and persistent history.",
  "Core Brain Flow": "The Core Brain orchestrates requests through: Intent Classifier -> Plan Generator -> Step Executor -> Reflection Engine -> Evolution Engine.",
  "Development Phases": "Phase 1: Requirements & Architecture (Week 1)\nPhase 2: Backend & Database Setup (Weeks 2-3)\nPhase 3: Frontend Development (Weeks 4-5)\nPhase 4: Integration & Testing (Week 6)",
  "Testing Strategy": "Unit tests using standard test frameworks (70% coverage), Integration tests for API endpoints (20% coverage), and End-to-End user flow tests (10% coverage).",
  "Deployment Plan": "Containerized using Docker and Docker Compose. Configured for automated CI/CD deployment to cloud environments (e.g., AWS, GCP) using GitHub Actions.",
  "Future Improvements": "1. Multi-region database replication\n2. Real-time WebSocket notifications\n3. Advanced analytics dashboard\n4. Automatic system-wide self-healing and scaling."
};

export default function App() {
  const [dbStatus, setDbStatus] = useState('checking');
  const [items, setItems] = useState([]);
  const [newItemTitle, setNewItemTitle] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('blueprint');

  useEffect(() => {
    checkHealth();
    fetchItems();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch('/api/v1/health');
      if (res.ok) {
        const data = await res.json();
        setDbStatus(data.database === 'connected' ? 'connected' : 'error');
      } else {
        setDbStatus('error');
      }
    } catch (err) {
      setDbStatus('error');
    }
  };

  const fetchItems = async () => {
    try {
      const res = await fetch('/api/v1/items');
      if (res.ok) {
        const data = await res.json();
        setItems(data);
      }
    } catch (err) {
      console.error('Failed to fetch items:', err);
    }
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!newItemTitle.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/v1/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newItemTitle, description: newItemDesc, completed: false }),
      });
      if (res.ok) {
        const created = await res.json();
        setItems([created, ...items]);
        setNewItemTitle('');
        setNewItemDesc('');
      }
    } catch (err) {
      console.error('Failed to add item:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
      <header className="glass-panel" style={{ padding: '24px', marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '2.25rem', fontWeight: 800 }} className="text-gradient">
            AETHER Core Engine
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#94a3b8', fontSize: '0.95rem' }}>
            Generated Workspace and Architecture
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <span className={{`badge ${dbStatus === 'connected' ? 'badge-success' : dbStatus === 'checking' ? 'badge-warning' : 'badge-error'}`}}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor', marginRight: '6px' }} className={{dbStatus === 'checking' ? 'animate-pulse' : ''}}></span>
            DB Status: {dbStatus}
          </span>
        </div>
      </header>

      <div style={{ display: 'flex', gap: '24px', marginBottom: '30px' }}>
        <button 
          className={{`button ${activeTab === 'blueprint' ? '' : 'button-secondary'}`}}
          onClick={{() => setActiveTab('blueprint')}}
        >
          Blueprint Viewer
        </button>
        <button 
          className={{`button ${activeTab === 'database' ? '' : 'button-secondary'}`}}
          onClick={{() => setActiveTab('database')}}
        >
          Live DB Playground
        </button>
      </div>

      {activeTab === 'blueprint' && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <section className="glass-panel" style={{ padding: '30px' }}>
              <h2 style={{ marginTop: 0, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px' }}>Executive Summary</h2>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#cbd5e1' }}>{blueprint["Executive Summary"] || 'No summary available.'}</p>
            </section>

            <section className="glass-panel" style={{ padding: '30px' }}>
              <h2 style={{ marginTop: 0, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px' }}>System Architecture</h2>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#cbd5e1' }}>{blueprint["System Architecture"] || 'No architecture details available.'}</p>
            </section>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <section className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ marginTop: 0 }}>Tech Stack</h3>
              <ul style={{ paddingLeft: '20px', color: '#cbd5e1' }}>
                <li>FastAPI (Python)</li>
                <li>Vite & React</li>
                <li>SQLite (aiosqlite)</li>
                <li>SQLAlchemy 2.0 ORM</li>
              </ul>
            </section>

            <section className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ marginTop: 0 }}>Folder Structure</h3>
              <pre style={{ margin: 0, padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                {blueprint["Folder Structure"] || './'}
              </pre>
            </section>
          </div>
        </div>
      )}

      {activeTab === 'database' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
          <section className="glass-panel" style={{ padding: '30px' }}>
            <h2 style={{ marginTop: 0, marginBottom: '20px' }}>Add Data</h2>
            <form onSubmit={handleAddItem} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.875rem', fontWeight: 600 }}>Title</label>
                <input 
                  type="text" 
                  value={newItemTitle} 
                  onChange={(e) => setNewItemTitle(e.target.value)}
                  placeholder="e.g. Test Backend Integration"
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(15,23,42,0.6)', color: 'white', boxSizing: 'border-box' }}
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.875rem', fontWeight: 600 }}>Description</label>
                <textarea 
                  value={newItemDesc} 
                  onChange={(e) => setNewItemDesc(e.target.value)}
                  placeholder="e.g. Ensure react app calls sqlite successfully"
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(15,23,42,0.6)', color: 'white', height: '100px', boxSizing: 'border-box', resize: 'vertical' }}
                />
              </div>
              <button type="submit" className="button" disabled={loading} style={{ justifyContent: 'center' }}>
                {loading ? 'Creating...' : 'Insert Row'}
              </button>
            </form>
          </section>

          <section className="glass-panel" style={{ padding: '30px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ margin: 0 }}>SQLite Database Table (items)</h2>
              <button className="button button-secondary" onClick={fetchItems} style={{ padding: '6px 12px', fontSize: '0.875rem' }}>
                Refresh
              </button>
            </div>
            {items.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                No database records found. Use the form to insert the first row.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {items.map(item => (
                  <div key={item.id} className="glass-panel" style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{item.title}</h3>
                      <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9rem' }}>{item.description}</p>
                    </div>
                    <span className="badge badge-info">ID: {item.id}</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
