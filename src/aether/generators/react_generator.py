import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("aether.generators.react_generator")


class ReactGenerator:
    """
    Generates a minimal Vite + React project based on an AI blueprint.
    """

    def __init__(self) -> None:
        pass

    def generate(self, blueprint: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Returns a list of Vite + React files dynamically populated with the blueprint metadata.
        """
        logger.info("Generating Vite + React frontend files from blueprint.")

        # Safely serialize the blueprint dict to JS-compatible JSON
        blueprint_json = json.dumps(blueprint, indent=2)

        # 1. package.json
        package_json_content = """{
  "name": "aether-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "eslint": "^8.57.0",
    "eslint-plugin-react": "^7.34.2",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.7",
    "vite": "^5.3.1"
  }
}
"""

        # 2. vite.config.js
        vite_config_content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
"""

        # 3. index.html
        index_html_content = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>✨</text></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AETHER Project</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

        # 4. src/main.jsx
        main_jsx_content = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

        # 5. src/index.css
        index_css_content = """:root {
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, -apple-system, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: dark;
  color: #e2e8f0;
  background-color: #0b0f19;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  min-height: 100vh;
  background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
  background-attachment: fixed;
  overflow-x: hidden;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #020617;
}
::-webkit-scrollbar-thumb {
  background: #1e293b;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #334155;
}

/* Glassmorphism Classes */
.glass-panel {
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-panel:hover {
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.1);
}

.text-gradient {
  background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #4f46e5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.badge-warning {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.badge-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.badge-info {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.button {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4);
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6);
}

.button:active {
  transform: translateY(0);
}

.button-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.button-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Keyframe animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
"""

        # 6. src/App.jsx
        app_jsx_content = f"""import React, {{ useState, useEffect }} from 'react';

const blueprint = {blueprint_json};

export default function App() {{
  const [dbStatus, setDbStatus] = useState('checking');
  const [items, setItems] = useState([]);
  const [newItemTitle, setNewItemTitle] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('blueprint');

  useEffect(() => {{
    checkHealth();
    fetchItems();
  }}, []);

  const checkHealth = async () => {{
    try {{
      const res = await fetch('/api/v1/health');
      if (res.ok) {{
        const data = await res.json();
        setDbStatus(data.database === 'connected' ? 'connected' : 'error');
      }} else {{
        setDbStatus('error');
      }}
    }} catch (err) {{
      setDbStatus('error');
    }}
  }};

  const fetchItems = async () => {{
    try {{
      const res = await fetch('/api/v1/items');
      if (res.ok) {{
        const data = await res.json();
        setItems(data);
      }}
    }} catch (err) {{
      console.error('Failed to fetch items:', err);
    }}
  }};

  const handleAddItem = async (e) => {{
    e.preventDefault();
    if (!newItemTitle.trim()) return;

    setLoading(true);
    try {{
      const res = await fetch('/api/v1/items', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ title: newItemTitle, description: newItemDesc, completed: false }}),
      }});
      if (res.ok) {{
        const created = await res.json();
        setItems([created, ...items]);
        setNewItemTitle('');
        setNewItemDesc('');
      }}
    }} catch (err) {{
      console.error('Failed to add item:', err);
    }} finally {{
      setLoading(false);
    }}
  }};

  return (
    <div style={{{{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}}}>
      <header className="glass-panel" style={{{{ padding: '24px', marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}}}>
        <div>
          <h1 style={{{{ margin: 0, fontSize: '2.25rem', fontWeight: 800 }}}} className="text-gradient">
            AETHER Core Engine
          </h1>
          <p style={{{{ margin: '8px 0 0 0', color: '#94a3b8', fontSize: '0.95rem' }}}}>
            Generated Workspace and Architecture
          </p>
        </div>
        <div style={{{{ display: 'flex', gap: '12px' }}}}>
          <span className={{{{`badge ${{dbStatus === 'connected' ? 'badge-success' : dbStatus === 'checking' ? 'badge-warning' : 'badge-error'}}`}}}}>
            <span style={{{{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor', marginRight: '6px' }}}} className={{{{dbStatus === 'checking' ? 'animate-pulse' : ''}}}}></span>
            DB Status: {{dbStatus}}
          </span>
        </div>
      </header>

      <div style={{{{ display: 'flex', gap: '24px', marginBottom: '30px' }}}}>
        <button 
          className={{{{`button ${{activeTab === 'blueprint' ? '' : 'button-secondary'}}`}}}}
          onClick={{{{() => setActiveTab('blueprint')}}}}
        >
          Blueprint Viewer
        </button>
        <button 
          className={{{{`button ${{activeTab === 'database' ? '' : 'button-secondary'}}`}}}}
          onClick={{{{() => setActiveTab('database')}}}}
        >
          Live DB Playground
        </button>
      </div>

      {{activeTab === 'blueprint' && (
        <div style={{{{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}}}>
          <div style={{{{ display: 'flex', flexDirection: 'column', gap: '24px' }}}}>
            <section className="glass-panel" style={{{{ padding: '30px' }}}}>
              <h2 style={{{{ marginTop: 0, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px' }}}}>Executive Summary</h2>
              <p style={{{{ whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#cbd5e1' }}}}>{{blueprint["Executive Summary"] || 'No summary available.'}}</p>
            </section>

            <section className="glass-panel" style={{{{ padding: '30px' }}}}>
              <h2 style={{{{ marginTop: 0, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px' }}}}>System Architecture</h2>
              <p style={{{{ whiteSpace: 'pre-wrap', lineHeight: '1.7', color: '#cbd5e1' }}}}>{{blueprint["System Architecture"] || 'No architecture details available.'}}</p>
            </section>
          </div>

          <div style={{{{ display: 'flex', flexDirection: 'column', gap: '24px' }}}}>
            <section className="glass-panel" style={{{{ padding: '24px' }}}}>
              <h3 style={{{{ marginTop: 0 }}}}>Tech Stack</h3>
              <ul style={{{{ paddingLeft: '20px', color: '#cbd5e1' }}}}>
                <li>FastAPI (Python)</li>
                <li>Vite & React</li>
                <li>SQLite (aiosqlite)</li>
                <li>SQLAlchemy 2.0 ORM</li>
              </ul>
            </section>

            <section className="glass-panel" style={{{{ padding: '24px' }}}}>
              <h3 style={{{{ marginTop: 0 }}}}>Folder Structure</h3>
              <pre style={{{{ margin: 0, padding: '12px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem', fontFamily: 'monospace' }}}}>
                {{blueprint["Folder Structure"] || './'}}
              </pre>
            </section>
          </div>
        </div>
      )}}

      {{activeTab === 'database' && (
        <div style={{{{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}}}>
          <section className="glass-panel" style={{{{ padding: '30px' }}}}>
            <h2 style={{{{ marginTop: 0, marginBottom: '20px' }}}}>Add Data</h2>
            <form onSubmit={{handleAddItem}} style={{{{ display: 'flex', flexDirection: 'column', gap: '16px' }}}}>
              <div>
                <label style={{{{ display: 'block', marginBottom: '6px', fontSize: '0.875rem', fontWeight: 600 }}}}>Title</label>
                <input 
                  type="text" 
                  value={{newItemTitle}} 
                  onChange={{(e) => setNewItemTitle(e.target.value)}}
                  placeholder="e.g. Test Backend Integration"
                  style={{{{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(15,23,42,0.6)', color: 'white', boxSizing: 'border-box' }}}}
                  required
                />
              </div>
              <div>
                <label style={{{{ display: 'block', marginBottom: '6px', fontSize: '0.875rem', fontWeight: 600 }}}}>Description</label>
                <textarea 
                  value={{newItemDesc}} 
                  onChange={{(e) => setNewItemDesc(e.target.value)}}
                  placeholder="e.g. Ensure react app calls sqlite successfully"
                  style={{{{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.15)', background: 'rgba(15,23,42,0.6)', color: 'white', height: '100px', boxSizing: 'border-box', resize: 'vertical' }}}}
                />
              </div>
              <button type="submit" className="button" disabled={{loading}} style={{{{ justifyContent: 'center' }}}}>
                {{loading ? 'Creating...' : 'Insert Row'}}
              </button>
            </form>
          </section>

          <section className="glass-panel" style={{{{ padding: '30px' }}}}>
            <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}}}>
              <h2 style={{{{ margin: 0 }}}}>SQLite Database Table (items)</h2>
              <button className="button button-secondary" onClick={{fetchItems}} style={{{{ padding: '6px 12px', fontSize: '0.875rem' }}}}>
                Refresh
              </button>
            </div>
            {{items.length === 0 ? (
              <div style={{{{ textAlign: 'center', padding: '40px', color: '#64748b' }}}}>
                No database records found. Use the form to insert the first row.
              </div>
            ) : (
              <div style={{{{ display: 'flex', flexDirection: 'column', gap: '12px' }}}}>
                {{items.map(item => (
                  <div key={{item.id}} className="glass-panel" style={{{{ padding: '16px', background: 'rgba(255,255,255,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}}}>
                    <div>
                      <h3 style={{{{ margin: '0 0 4px 0', fontSize: '1.1rem' }}}}>{{item.title}}</h3>
                      <p style={{{{ margin: 0, color: '#94a3b8', fontSize: '0.9rem' }}}}>{{item.description}}</p>
                    </div>
                    <span className="badge badge-info">ID: {{item.id}}</span>
                  </div>
                ))}}
              </div>
            )}}
          </section>
        </div>
      )}}
    </div>
  );
}}
"""

        logger.info("Vite + React files successfully prepared.")

        return [
            {"path": "frontend/index.html", "content": index_html_content},
            {"path": "frontend/package.json", "content": package_json_content},
            {"path": "frontend/vite.config.js", "content": vite_config_content},
            {"path": "frontend/src/main.jsx", "content": main_jsx_content},
            {"path": "frontend/src/index.css", "content": index_css_content},
            {"path": "frontend/src/App.jsx", "content": app_jsx_content},
        ]
