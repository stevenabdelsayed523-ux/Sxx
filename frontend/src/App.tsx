import { useState } from 'react';

function App() {
  const [apiMessage, setApiMessage] = useState<string | null>(null);

  const checkApi = async () => {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      setApiMessage(JSON.stringify(data, null, 2));
    } catch (err) {
      setApiMessage(`Error: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>CodeMate AI</h1>
        <p className="tagline">Your AI pair-programmer that never sleeps</p>
      </header>

      <main className="main">
        <section className="hero">
          <h2>Write, debug, and refactor code in real-time</h2>
          <p>
            CodeMate AI is an intelligent coding assistant that understands your full codebase
            and works across any language or framework.
          </p>
          <button className="cta-button" onClick={checkApi}>
            Test API Connection
          </button>
          {apiMessage && (
            <pre className="api-response">{apiMessage}</pre>
          )}
        </section>

        <section className="features">
          <div className="feature-card">
            <h3>Real-time AI Pair Programming</h3>
            <p>Get code suggestions, completions, and refactoring as you type.</p>
          </div>
          <div className="feature-card">
            <h3>Full Codebase Understanding</h3>
            <p>Context-aware assistance that understands your entire project.</p>
          </div>
          <div className="feature-card">
            <h3>Multi-Language Support</h3>
            <p>Works across JavaScript, TypeScript, Python, and more.</p>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} CodeMate AI. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;