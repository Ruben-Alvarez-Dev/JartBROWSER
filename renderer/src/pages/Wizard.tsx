import React, { useState } from 'react';

interface WizardStep {
  id: string;
  title: string;
  description: string;
}

const steps: WizardStep[] = [
  { id: 'mode', title: 'Choose Mode', description: 'Simple or Advanced' },
  { id: 'deployment', title: 'Deployment Type', description: 'Local, VPS, or Hybrid' },
  { id: 'providers', title: 'LLM Providers', description: 'Configure your AI providers' },
  { id: 'docker', title: 'Docker Setup', description: 'Start required services' },
  { id: 'complete', title: 'Complete', description: 'Ready to use!' }
];

export function Wizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [config, setConfig] = useState({
    mode: 'simple',
    deploymentType: 'local',
    providers: {} as Record<string, { enabled: boolean; apiKey: string }>
  });

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    // Save configuration
    if (window.electronAPI) {
      await window.electronAPI.setConfig(config);
    }
    // Close wizard and show main app
    window.location.hash = '/dashboard';
  };

  return (
    <div className="wizard">
      <div className="wizard-header">
        <h1>Welcome to JartBROWSER</h1>
        <p>Let's get you set up in just a few steps</p>
      </div>

      {/* Progress Steps */}
      <div className="wizard-steps">
        {steps.map((step, index) => (
          <div 
            key={step.id} 
            className={`wizard-step ${index <= currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
          >
            <div className="step-number">{index < currentStep ? '✓' : index + 1}</div>
            <div className="step-info">
              <span className="step-title">{step.title}</span>
              <span className="step-desc">{step.description}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="wizard-content">
        {currentStep === 0 && (
          <div className="step-panel">
            <h2>Choose Your Setup Mode</h2>
            <div className="option-grid">
              <button 
                className={`option-card ${config.mode === 'simple' ? 'selected' : ''}`}
                onClick={() => setConfig({ ...config, mode: 'simple' })}
              >
                <div className="option-icon">🚀</div>
                <h3>Simple Mode</h3>
                <p>Recommended for most users. We'll handle everything for you.</p>
                <ul>
                  <li>One-click setup</li>
                  <li>Default settings</li>
                  <li>Automatic updates</li>
                </ul>
              </button>
              <button 
                className={`option-card ${config.mode === 'advanced' ? 'selected' : ''}`}
                onClick={() => setConfig({ ...config, mode: 'advanced' })}
              >
                <div className="option-icon">⚙️</div>
                <h3>Advanced Mode</h3>
                <p>For developers who want full control over configuration.</p>
                <ul>
                  <li>Custom deployment</li>
                  <li>Manual configuration</li>
                  <li>Advanced features</li>
                </ul>
              </button>
            </div>
          </div>
        )}

        {currentStep === 1 && (
          <div className="step-panel">
            <h2>Choose Deployment Type</h2>
            <div className="option-grid">
              <button 
                className={`option-card ${config.deploymentType === 'local' ? 'selected' : ''}`}
                onClick={() => setConfig({ ...config, deploymentType: 'local' })}
              >
                <div className="option-icon">💻</div>
                <h3>Local</h3>
                <p>Everything runs on your machine. Best for privacy.</p>
                <ul>
                  <li>Ollama for AI</li>
                  <li>All data stays local</li>
                  <li>Requires more resources</li>
                </ul>
              </button>
              <button 
                className={`option-card ${config.deploymentType === 'vps' ? 'selected' : ''}`}
                onClick={() => setConfig({ ...config, deploymentType: 'vps' })}
              >
                <div className="option-icon">☁️</div>
                <h3>VPS</h3>
                <p>Run on a remote server. Best for accessibility.</p>
                <ul>
                  <li>OpenWebUI in cloud</li>
                  <li>Access from anywhere</li>
                  <li>Requires server setup</li>
                </ul>
              </button>
              <button 
                className={`option-card ${config.deploymentType === 'hybrid' ? 'selected' : ''}`}
                onClick={() => setConfig({ ...config, deploymentType: 'hybrid' })}
              >
                <div className="option-icon">🔄</div>
                <h3>Hybrid</h3>
                <p>Mix of local and cloud. Best of both worlds.</p>
                <ul>
                  <li>Local Ollama</li>
                  <li>Cloud OpenWebUI</li>
                  <li>Flexible setup</li>
                </ul>
              </button>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="step-panel">
            <h2>Configure LLM Providers</h2>
            <div className="providers-list">
              {['OpenAI', 'Anthropic', 'Z.ai', 'MiniMax', 'Mistral', 'Ollama'].map(provider => (
                <div key={provider} className="provider-row">
                  <label className="provider-toggle">
                    <input 
                      type="checkbox"
                      checked={config.providers[provider]?.enabled || false}
                      onChange={(e) => setConfig({
                        ...config,
                        providers: {
                          ...config.providers,
                          [provider]: { enabled: e.target.checked, apiKey: '' }
                        }
                      })}
                    />
                    <span>{provider}</span>
                  </label>
                  {config.providers[provider]?.enabled && (
                    <input 
                      type="password"
                      placeholder={`Enter ${provider} API key`}
                      className="api-key-input"
                      value={config.providers[provider]?.apiKey || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        providers: {
                          ...config.providers,
                          [provider]: { ...config.providers[provider]!, apiKey: e.target.value }
                        }
                      })}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="step-panel">
            <h2>Docker Setup</h2>
            <div className="docker-status">
              <p>Starting Docker services...</p>
              <div className="loading-spinner"></div>
              <ul className="service-list">
                <li className="service-item pending">OpenWebUI</li>
                <li className="service-item pending">Ollama</li>
                <li className="service-item pending">Redis</li>
                <li className="service-item pending">Caddy</li>
              </ul>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="step-panel">
            <div className="completion">
              <div className="completion-icon">🎉</div>
              <h2>You're All Set!</h2>
              <p>JartBROWSER is ready to use. Click below to start.</p>
              <button className="btn-primary" onClick={handleComplete}>
                Launch JartBROWSER
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="wizard-nav">
        <button 
          className="btn-secondary" 
          onClick={handleBack}
          disabled={currentStep === 0}
        >
          Back
        </button>
        {currentStep < steps.length - 1 && (
          <button className="btn-primary" onClick={handleNext}>
            {currentStep === 3 ? 'Start Services' : 'Next'}
          </button>
        )}
      </div>
    </div>
  );
}
