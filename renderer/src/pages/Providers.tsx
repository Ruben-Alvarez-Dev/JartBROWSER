import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Check, X } from 'lucide-react';

interface Provider {
  name: string;
  models: string[];
  enabled: boolean;
  apiKey?: string;
}

export function Providers() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/providers');
      const data = await res.json();
      
      // Get stored keys
      const keysRes = await fetch('http://localhost:8000/api/v1/providers/keys');
      const keys = await keysRes.json();
      
      // Merge
      const providersWithKeys = data.providers.map((p: string) => ({
        name: p,
        models: [],
        enabled: keys.some((k: any) => k.provider === p),
        apiKey: ''
      }));
      
      setProviders(providersWithKeys);
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    }
  };

  const handleAddKey = async () => {
    if (!selectedProvider || !apiKey) return;
    
    setSaving(true);
    try {
      await fetch('http://localhost:8000/api/v1/providers/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          api_key: apiKey
        })
      });
      
      setApiKey('');
      setSelectedProvider(null);
      fetchProviders();
    } catch (error) {
      console.error('Failed to add API key:', error);
    }
    setSaving(false);
  };

  const handleDeleteKey = async (provider: string) => {
    try {
      const keysRes = await fetch('http://localhost:8000/api/v1/providers/keys');
      const keys = await keysRes.json();
      const key = keys.find((k: any) => k.provider === provider);
      
      if (key) {
        await fetch(`http://localhost:8000/api/v1/providers/keys/${key.id}`, {
          method: 'DELETE'
        });
        fetchProviders();
      }
    } catch (error) {
      console.error('Failed to delete API key:', error);
    }
  };

  return (
    <div className="providers-page">
      <div className="page-header">
        <h1>LLM Providers</h1>
        <p>Configure your AI language model providers</p>
      </div>

      <div className="providers-grid">
        {providers.map(provider => (
          <div key={provider.name} className={`provider-card ${provider.enabled ? 'enabled' : ''}`}>
            <div className="provider-header">
              <h3>{provider.name}</h3>
              {provider.enabled ? (
                <span className="status-badge success"><Check size={14} /> Configured</span>
              ) : (
                <span className="status-badge">Not configured</span>
              )}
            </div>
            
            {provider.enabled ? (
              <div className="provider-actions">
                <button 
                  className="btn-danger"
                  onClick={() => handleDeleteKey(provider.name)}
                >
                  <Trash2 size={16} /> Remove
                </button>
              </div>
            ) : (
              <div className="provider-setup">
                <button 
                  className="btn-primary"
                  onClick={() => setSelectedProvider(provider.name)}
                >
                  <Plus size={16} /> Add API Key
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add API Key Modal */}
      {selectedProvider && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Add {selectedProvider} API Key</h2>
            <p>Enter your API key to enable this provider.</p>
            <input
              type="password"
              placeholder="Enter API key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="api-input"
            />
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setSelectedProvider(null)}>
                Cancel
              </button>
              <button 
                className="btn-primary" 
                onClick={handleAddKey}
                disabled={!apiKey || saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
