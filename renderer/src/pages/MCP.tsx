import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Play, RefreshCw } from 'lucide-react';

interface MCPConnection {
  id: string;
  name: string;
  url: string;
  is_active: boolean;
  tools_count: number;
}

interface MCPTool {
  name: string;
  description: string;
}

export function MCP() {
  const [connections, setConnections] = useState<MCPConnection[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newConnection, setNewConnection] = useState({ name: '', url: '', auth_token: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [connRes, toolsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/mcp/connections'),
        fetch('http://localhost:8000/api/v1/mcp/tools')
      ]);
      
      setConnections(await connRes.json());
      setTools(await toolsRes.json());
    } catch (error) {
      console.error('Failed to fetch MCP data:', error);
    }
  };

  const handleAddConnection = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/mcp/connections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConnection)
      });
      setShowAddModal(false);
      setNewConnection({ name: '', url: '', auth_token: '' });
      fetchData();
    } catch (error) {
      console.error('Failed to add connection:', error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/mcp/connections/${id}`, { method: 'DELETE' });
      fetchData();
    } catch (error) {
      console.error('Failed to delete connection:', error);
    }
  };

  const handleTest = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/mcp/connections/${id}/test`, { method: 'POST' });
      const data = await res.json();
      alert(data.success ? 'Connection successful!' : 'Connection failed!');
    } catch (error) {
      console.error('Failed to test connection:', error);
    }
  };

  return (
    <div className="mcp-page">
      <div className="page-header">
        <h1>MCP Connections</h1>
        <p>Manage Model Context Protocol integrations</p>
      </div>

      {/* Connections */}
      <section className="section">
        <div className="section-header">
          <h2>Connections</h2>
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>
            <Plus size={16} /> Add Connection
          </button>
        </div>
        
        {connections.length === 0 ? (
          <div className="empty-state">No MCP connections configured</div>
        ) : (
          <div className="connections-list">
            {connections.map(conn => (
              <div key={conn.id} className="connection-card">
                <div className="connection-info">
                  <h3>{conn.name}</h3>
                  <span className="connection-url">{conn.url}</span>
                  <span className="tools-count">{conn.tools_count} tools</span>
                </div>
                <div className="connection-actions">
                  <button className="btn-icon" onClick={() => handleTest(conn.id)}>
                    <RefreshCw size={16} />
                  </button>
                  <button className="btn-icon danger" onClick={() => handleDelete(conn.id)}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Tools */}
      <section className="section">
        <h2>Available Tools</h2>
        <div className="tools-grid">
          {tools.map(tool => (
            <div key={tool.name} className="tool-card">
              <h4>{tool.name}</h4>
              <p>{tool.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Add Connection Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Add MCP Connection</h2>
            <input
              type="text"
              placeholder="Connection name"
              value={newConnection.name}
              onChange={(e) => setNewConnection({ ...newConnection, name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Server URL"
              value={newConnection.url}
              onChange={(e) => setNewConnection({ ...newConnection, url: e.target.value })}
            />
            <input
              type="password"
              placeholder="Auth token (optional)"
              value={newConnection.auth_token}
              onChange={(e) => setNewConnection({ ...newConnection, auth_token: e.target.value })}
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleAddConnection}>Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
