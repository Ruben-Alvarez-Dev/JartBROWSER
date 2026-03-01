import React from 'react';
import { Settings, Terminal, LogOut, Cpu, Layout, Shield, Layers, Code2 } from 'lucide-react';

export function App() {
  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">
          <span className="icon">🚀</span>
          <h1>JartBROWSER</h1>
        </div>
        <ul className="nav-items">
          <li className="active">
            <Layout className="icon" />
            <span>Dashboard</span>
          </li>
          <li>
            <Settings className="icon" />
            <span>Settings</span>
          </li>
          <li>
            <Terminal className="icon" />
            <span>Docker</span>
          </li>
          <li>
            <Cpu className="icon" />
            <span>Providers</span>
          </li>
          <li>
            <Code2 className="icon" />
            <span>Skills</span>
          </li>
          <li>
            <Layers className="icon" />
            <span>MCP</span>
          </li>
          <li>
            <Shield className="icon" />
            <span>Security</span>
          </li>
        </ul>
        <div className="footer">
          <LogOut className="icon" />
          <span>Logout</span>
        </div>
      </nav>
      <main className="content">
        <div className="hero">
          <h2>Welcome to JartBROWSER</h2>
          <p>Your browser, powered by AI</p>
          <button className="btn-primary">Get Started</button>
        </div>
      </main>
    </div>
  );
}
