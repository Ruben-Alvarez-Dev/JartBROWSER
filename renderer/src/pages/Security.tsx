import React, { useState } from 'react';
import { Shield, Key, Lock, Eye, EyeOff } from 'lucide-react';

export function Security() {
  const [showApiKey, setShowApiKey] = useState(false);
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [auditLogging, setAuditLogging] = useState(true);

  return (
    <div className="security-page">
      <div className="page-header">
        <h1>Security</h1>
        <p>Manage your security and privacy settings</p>
      </div>

      <div className="security-sections">
        <section className="security-section">
          <div className="section-header">
            <Shield className="section-icon" />
            <h2>API Key Management</h2>
          </div>
          <p>Your API keys are encrypted at rest using AES-256 encryption.</p>
          
          <div className="security-option">
            <label>Encryption</label>
            <div className="option-status">
              {encryptionEnabled ? (
                <span className="status success"><Lock size={14} /> Enabled</span>
              ) : (
                <span className="status"><Lock size={14} /> Disabled</span>
              )}
            </div>
          </div>

          <div className="security-option">
            <label>Encryption Key</label>
            <div className="key-display">
              <code>{showApiKey ? 'jartbrowser-encryption-key-****' : '••••••••••••••••'}</code>
              <button 
                className="btn-icon"
                onClick={() => setShowApiKey(!showApiKey)}
              >
                {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
        </section>

        <section className="security-section">
          <div className="section-header">
            <Key className="section-icon" />
            <h2>Privacy</h2>
          </div>
          
          <div className="setting-item">
            <div className="setting-info">
              <label>Local-First Mode</label>
              <p>Keep all data on your device by default</p>
            </div>
            <input type="checkbox" defaultChecked />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Telemetry</label>
              <p>Send anonymous usage data to help improve JartBROWSER</p>
            </div>
            <input type="checkbox" />
          </div>
        </section>

        <section className="security-section">
          <div className="section-header">
            <Shield className="section-icon" />
            <h2>Audit Logging</h2>
          </div>
          <p>Track all agent actions for compliance and debugging.</p>
          
          <div className="setting-item">
            <div className="setting-info">
              <label>Enable Audit Logs</label>
              <p>Log all API calls and agent actions</p>
            </div>
            <input 
              type="checkbox" 
              checked={auditLogging}
              onChange={(e) => setAuditLogging(e.target.checked)}
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label>Log Retention</label>
              <p>How long to keep audit logs</p>
            </div>
            <select defaultValue="30">
              <option value="7">7 days</option>
              <option value="30">30 days</option>
              <option value="90">90 days</option>
              <option value="365">1 year</option>
            </select>
          </div>
        </section>
      </div>
    </div>
  );
}
