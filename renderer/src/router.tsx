import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { App } from './App';
import { Wizard } from './pages/Wizard';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { Providers } from './pages/Providers';
import { Skills } from './pages/Skills';
import { MCP } from './pages/MCP';
import { Security } from './pages/Security';
import { Docker } from './pages/Docker';

export function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="settings" element={<Settings />} />
          <Route path="providers" element={<Providers />} />
          <Route path="skills" element={<Skills />} />
          <Route path="mcp" element={<MCP />} />
          <Route path="security" element={<Security />} />
          <Route path="docker" element={<Docker />} />
        </Route>
        <Route path="/wizard" element={<Wizard />} />
      </Routes>
    </BrowserRouter>
  );
}
