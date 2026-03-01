import React, { useState } from 'react';

export function Settings() {
  const [settings, setSettings] = useState({
    theme: 'dark',
    language: 'en',
    autoStart: true,
    minimizeToTray: true,
    notifications: true,
    telemetry: false
  });

  const handleSave = async () => {
    if (window.electronAPI) {
      await window.electronAPI.setConfig(settings);
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure your JartBROWSER preferences</p>
      </div>

      <div className="settings-sections">
        <section className="settings-section">
          <h2>General</h2>
          <div className="setting-item">
            <label>Theme</label>
            <select 
              value={settings.theme}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Language</label>
            <select 
              value={settings.language}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
            </select>
          </div>
        </section>

        <section className="settings-section">
          <h2>Startup</h2>
          <div className="setting-item">
            <label>Start on system boot</label>
            <input 
              type="checkbox"
              checked={settings.autoStart}
              onChange={(e) => setSettings({ ...settings, autoStart: e.target.checked })}
            />
          </div>
          <div className="setting-item">
            <label>Minimize to system tray</label>
            <input 
              type="checkbox"
              checked={settings.minimizeToTray}
              onChange={(e) => setSettings({ ...settings, minimizeToTray: e.target.checked })}
            />
          </div>
        </section>

        <section className="settings-section">
          <h2>Notifications</h2>
          <div className="setting-item">
            <label>Enable notifications</label>
            <input 
              type="checkbox"
              checked={settings.notifications}
              onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
            />
          </div>
          <div className="setting-item">
            <label>Send anonymous telemetry</label>
            <input 
              type="checkbox"
              checked={settings.telemetry}
              onChange={(e) => setSettings({ ...settings, telemetry: e.target.checked })}
            />
          </div>
        </section>

        <div className="settings-actions">
          <button className="btn-primary" onClick={handleSave}>Save Settings</button>
        </div>
      </div>
    </div>
  );
}
