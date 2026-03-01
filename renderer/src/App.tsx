import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Layout, Terminal, Cpu, Code2, Layers, Shield, Settings, LogOut } from 'lucide-react';
import './App.css';

const navItems = [
  { path: '/dashboard', icon: Layout, label: 'Dashboard' },
  { path: '/docker', icon: Terminal, label: 'Docker' },
  { path: '/providers', icon: Cpu, label: 'Providers' },
  { path: '/skills', icon: Code2, label: 'Skills' },
  { path: '/mcp', icon: Layers, label: 'MCP' },
  { path: '/security', icon: Shield, label: 'Security' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function App() {
  const location = useLocation();

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">
          <span className="logo-icon">🚀</span>
          <h1>JartBROWSER</h1>
        </div>
        
        <ul className="nav-items">
          {navItems.map(item => (
            <li 
              key={item.path} 
              className={location.pathname === item.path ? 'active' : ''}
            >
              <a href={item.path}>
                <item.icon className="icon" />
                <span>{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
        
        <div className="sidebar-footer">
          <button className="logout-btn">
            <LogOut className="icon" />
            <span>Logout</span>
          </button>
        </div>
      </nav>
      
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
