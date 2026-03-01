import React, { useState, useEffect, useRef } from 'react';

// ============== Types ==============
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface PageInfo {
  url: string;
  title: string;
}

interface ElementInfo {
  tag: string;
  selector: string;
  text: string;
}

// ============== Components ==============

function Header() {
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    // Check connection status
    const checkConnection = async () => {
      try {
        const res = await fetch('http://localhost:8000/health');
        setConnected(res.ok);
      } catch {
        setConnected(false);
      }
    };
    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="header">
      <span className="logo">🚀</span>
      <h1>JartBROWSER</h1>
      <div className={`status ${connected ? '' : 'disconnected'}`} title={connected ? 'Connected' : 'Disconnected'} />
    </header>
  );
}

function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you with this page?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'I\'m ready to help. What would you like me to do?'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I couldn\'t reach the backend. Make sure JartBROWSER is running.'
      }]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content loading">
              <span className="spinner" /> Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

function PageInfoPanel() {
  const [info, setInfo] = useState<PageInfo>({ url: '', title: '' });

  useEffect(() => {
    // Get current tab info
    chrome.runtime.sendMessage({ type: 'GET_TAB_INFO' }, (response) => {
      if (response) {
        setInfo(response);
      }
    });
  }, []);

  const handleAction = async (action: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/browser/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, target: '', value: '' })
      });
    } catch (error) {
      console.error('Action failed:', error);
    }
  };

  return (
    <div className="page-info-panel">
      <div className="info-card">
        <h3>URL</h3>
        <p className="url">{info.url || 'Loading...'}</p>
      </div>
      <div className="info-card">
        <h3>Title</h3>
        <p>{info.title || 'Loading...'}</p>
      </div>
      <div className="info-card">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <button onClick={() => handleAction('screenshot')}>📸 Screenshot</button>
          <button onClick={() => handleAction('dom')}>📄 Get DOM</button>
          <button onClick={() => handleAction('scroll-top')}>⬆️ Top</button>
          <button onClick={() => handleAction('scroll-bottom')}>⬇️ Bottom</button>
        </div>
      </div>
    </div>
  );
}

function ElementsPanel() {
  const [elements, setElements] = useState<ElementInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Request elements from background script
    chrome.runtime.sendMessage({ type: 'GET_ELEMENTS' }, (response) => {
      if (response?.elements) {
        setElements(response.elements);
      }
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="elements-panel">
        <div className="loading"><span className="spinner" /> Loading elements...</div>
      </div>
    );
  }

  return (
    <div className="elements-panel">
      {elements.length === 0 ? (
        <div className="empty-state">No interactive elements found</div>
      ) : (
        <div className="elements-list">
          {elements.map((el, i) => (
            <div key={i} className="element-item" data-selector={el.selector}>
              <span className="element-tag">&lt;{el.tag}&gt;</span>
              <span className="element-selector">{el.selector}</span>
              {el.text && <span className="element-text">{el.text}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'page' | 'elements'>('chat');

  return (
    <div className="sidebar-app">
      <Header />
      <nav className="tabs">
        <button
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          AI Chat
        </button>
        <button
          className={activeTab === 'page' ? 'active' : ''}
          onClick={() => setActiveTab('page')}
        >
          Page Info
        </button>
        <button
          className={activeTab === 'elements' ? 'active' : ''}
          onClick={() => setActiveTab('elements')}
        >
          Elements
        </button>
      </nav>
      <main className="content">
        {activeTab === 'chat' && <ChatPanel />}
        {activeTab === 'page' && <PageInfoPanel />}
        {activeTab === 'elements' && <ElementsPanel />}
      </main>
    </div>
  );
}

export { App };
