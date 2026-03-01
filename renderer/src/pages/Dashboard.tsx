import React, { useState, useEffect } from 'react';
import { Layout, Users, Cpu, Layers, Shield, Container, Activity, Clock, Zap } from 'lucide-react';

interface Stats {
  tabs: number;
  sessions: number;
  agents: number;
  tasks: number;
}

interface Status {
  docker: boolean;
  backend: boolean;
  mcp: boolean;
}

export function Dashboard() {
  const [stats, setStats] = useState<Stats>({ tabs: 0, sessions: 0, agents: 0, tasks: 0 });
  const [status, setStatus] = useState<Status>({ docker: false, backend: false, mcp: false });
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  useEffect(() => {
    // Fetch dashboard data
    const fetchData = async () => {
      try {
        // Get backend status
        const healthRes = await fetch('http://localhost:8000/health');
        const health = await healthRes.json();
        
        // Get MCP status
        const mcpRes = await fetch('http://localhost:3001/health');
        
        setStatus({
          docker: false, // Would check docker
          backend: health.status === 'healthy',
          mcp: mcpRes.ok
        });
        
        // Get agent status
        const agentRes = await fetch('http://localhost:8000/api/v1/agent/status');
        const agentData = await agentRes.json();
        
        setStats({
          tabs: 1,
          sessions: agentData.completed_tasks || 0,
          agents: agentData.active_tasks || 0,
          tasks: agentData.completed_tasks || 0
        });
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome to JartBROWSER - Your AI-powered browser</p>
      </div>

      {/* Status Cards */}
      <div className="status-grid">
        <div className={`status-card ${status.backend ? 'active' : 'inactive'}`}>
          <Cpu className="status-icon" />
          <div className="status-info">
            <span className="status-label">Backend API</span>
            <span className="status-value">{status.backend ? 'Running' : 'Stopped'}</span>
          </div>
        </div>
        <div className={`status-card ${status.mcp ? 'active' : 'inactive'}`}>
          <Layers className="status-icon" />
          <div className="status-info">
            <span className="status-label">MCP Server</span>
            <span className="status-value">{status.mcp ? 'Running' : 'Stopped'}</span>
          </div>
        </div>
        <div className={`status-card ${status.docker ? 'active' : 'inactive'}`}>
          <Container className="status-icon" />
          <div className="status-info">
            <span className="status-label">Docker</span>
            <span className="status-value">{status.docker ? 'Running' : 'Stopped'}</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <Layout className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{stats.tabs}</span>
            <span className="stat-label">Open Tabs</span>
          </div>
        </div>
        <div className="stat-card">
          <Users className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{stats.sessions}</span>
            <span className="stat-label">Sessions</span>
          </div>
        </div>
        <div className="stat-card">
          <Zap className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{stats.agents}</span>
            <span className="stat-label">Active Agents</span>
          </div>
        </div>
        <div className="stat-card">
          <Activity className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{stats.tasks}</span>
            <span className="stat-label">Completed Tasks</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="section">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <button className="action-btn" onClick={() => window.open('http://localhost:8000/api/v1/docs', '_blank')}>
            <Cpu />
            <span>API Docs</span>
          </button>
          <button className="action-btn" onClick={() => window.electronAPI?.openExternal('http://localhost:8080')}>
            <Container />
            <span>Docker Dashboard</span>
          </button>
          <button className="action-btn">
            <Shield />
            <span>Security Settings</span>
          </button>
          <button className="action-btn">
            <Clock />
            <span>View Logs</span>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {recentActivity.length === 0 ? (
            <p className="empty-state">No recent activity</p>
          ) : (
            recentActivity.map((item, i) => (
              <div key={i} className="activity-item">
                <Activity className="activity-icon" />
                <span>{item.message}</span>
                <span className="activity-time">{item.time}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
