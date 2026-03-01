import React, { useState, useEffect } from 'react';
import { Play, Square, RefreshCw, Container, Trash2, ExternalLink } from 'lucide-react';

interface ContainerStatus {
  id: string;
  name: string;
  image: string;
  status: string;
}

interface DockerStatus {
  running: boolean;
  containers: ContainerStatus[];
}

export function Docker() {
  const [status, setStatus] = useState<DockerStatus>({ running: false, containers: [] });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/docker/status');
      const data = await res.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch Docker status:', error);
      setStatus({ running: false, containers: [] });
    }
    setLoading(false);
  };

  const handleAction = async (containerId: string, action: string) => {
    setActionLoading(containerId);
    try {
      await fetch(`http://localhost:8000/api/v1/docker/container/${containerId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      fetchStatus();
    } catch (error) {
      console.error(`Failed to ${action} container:`, error);
    }
    setActionLoading(null);
  };

  const handleComposeUp = async () => {
    setActionLoading('compose-up');
    try {
      await fetch('http://localhost:8000/api/v1/docker/compose/up', { method: 'POST' });
      fetchStatus();
    } catch (error) {
      console.error('Failed to start services:', error);
    }
    setActionLoading(null);
  };

  const handleComposeDown = async () => {
    setActionLoading('compose-down');
    try {
      await fetch('http://localhost:8000/api/v1/docker/compose/down', { method: 'POST' });
      fetchStatus();
    } catch (error) {
      console.error('Failed to stop services:', error);
    }
    setActionLoading(null);
  };

  const openDashboard = () => {
    window.open('http://localhost:8080', '_blank');
  };

  return (
    <div className="docker-page">
      <div className="page-header">
        <h1>Docker</h1>
        <p>Manage your Docker containers and services</p>
      </div>

      {/* Status */}
      <div className="docker-status-card">
        <div className={`status-indicator ${status.running ? 'running' : 'stopped'}`}>
          <Container />
          <span>{status.running ? 'Docker Running' : 'Docker Stopped'}</span>
        </div>
        
        <div className="docker-actions">
          <button 
            className="btn-primary" 
            onClick={handleComposeUp}
            disabled={actionLoading !== null}
          >
            <Play size={16} /> Start All
          </button>
          <button 
            className="btn-secondary" 
            onClick={handleComposeDown}
            disabled={actionLoading !== null}
          >
            <Square size={16} /> Stop All
          </button>
          <button className="btn-secondary" onClick={openDashboard}>
            <ExternalLink size={16} /> Dashboard
          </button>
          <button 
            className="btn-icon" 
            onClick={fetchStatus}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
          </button>
        </div>
      </div>

      {/* Containers */}
      <section className="section">
        <h2>Containers</h2>
        
        {loading ? (
          <div className="loading">Loading containers...</div>
        ) : status.containers.length === 0 ? (
          <div className="empty-state">
            <Container size={48} />
            <p>No containers running</p>
            <button className="btn-primary" onClick={handleComposeUp}>
              Start Services
            </button>
          </div>
        ) : (
          <div className="containers-grid">
            {status.containers.map(container => (
              <div key={container.id} className="container-card">
                <div className="container-header">
                  <h3>{container.name}</h3>
                  <span className={`container-status ${container.status}`}>
                    {container.status}
                  </span>
                </div>
                <span className="container-image">{container.image}</span>
                <span className="container-id">ID: {container.id}</span>
                
                <div className="container-actions">
                  {container.status === 'running' ? (
                    <button 
                      className="btn-icon"
                      onClick={() => handleAction(container.id, 'stop')}
                      disabled={actionLoading === container.id}
                    >
                      <Square size={16} />
                    </button>
                  ) : (
                    <button 
                      className="btn-icon"
                      onClick={() => handleAction(container.id, 'start')}
                      disabled={actionLoading === container.id}
                    >
                      <Play size={16} />
                    </button>
                  )}
                  <button 
                    className="btn-icon danger"
                    onClick={() => handleAction(container.id, 'remove')}
                    disabled={actionLoading === container.id}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Quick Links */}
      <section className="section">
        <h2>Quick Links</h2>
        <div className="quick-links">
          <a href="http://localhost:8080" target="_blank" rel="noopener" className="quick-link">
            OpenWebUI
          </a>
          <a href="http://localhost:11434" target="_blank" rel="noopener" className="quick-link">
            Ollama API
          </a>
        </div>
      </section>
    </div>
  );
}
