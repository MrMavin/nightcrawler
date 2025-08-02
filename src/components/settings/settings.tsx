import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { StorageManager } from '../../utils/storage/storage';
import { DEFAULT_PERSONAL_PREFERENCES, PersonalPreferences, AIConfiguration } from '../../utils/storage/types';
import { PreferenceOptimizer } from '../../utils/ai/components/preference-optimizer';
import '../../styles/main.css';

interface PreferenceItem {
  key: string;
  value: string;
}

interface OptimizationModalData {
  isOpen: boolean;
  key: string;
  original: string;
  optimized: string;
  onAccept: (optimized: string) => void;
  onDecline: () => void;
}

const Settings: React.FC = () => {
  const [preferences, setPreferences] = useState<PreferenceItem[]>([]);
  const [aiConfig, setAiConfig] = useState<AIConfiguration>({
    openaiApiKey: '',
    openaiModel: 'gpt-4o'
  });
  const [isOptimizing, setIsOptimizing] = useState<string | null>(null);
  const [isOptimizingAll, setIsOptimizingAll] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [optimizationModal, setOptimizationModal] = useState<OptimizationModalData>({
    isOpen: false,
    key: '',
    original: '',
    optimized: '',
    onAccept: () => {},
    onDecline: () => {}
  });

  const storageManager = StorageManager.getInstance();
  const optimizer = PreferenceOptimizer.getInstance();

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const loadSettings = async () => {
    try {
      const settings = await storageManager.getSettings();
      setAiConfig(settings.aiConfiguration);
      
      const prefArray = Object.entries(settings.personalPreferences).map(([key, value]) => ({
        key,
        value
      }));
      setPreferences(prefArray);
    } catch (error) {
      showToast('Failed to load settings', 'error');
    }
  };

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
  };

  const addPreference = () => {
    setPreferences([...preferences, { key: '', value: '' }]);
  };

  const removePreference = (index: number) => {
    setPreferences(preferences.filter((_, i) => i !== index));
  };

  const updatePreference = (index: number, field: 'key' | 'value', newValue: string) => {
    const updated = [...preferences];
    updated[index][field] = newValue;
    setPreferences(updated);
  };

  const optimizePreference = async (index: number) => {
    const preference = preferences[index];
    
    if (!preference.key.trim() || !preference.value.trim()) {
      showToast('Please enter both key and value before optimizing', 'error');
      return;
    }

    setIsOptimizing(preference.key);

    try {
      const result = await optimizer.optimize(preference.key, preference.value);
      
      if (!result.success) {
        showToast(result.error || 'Optimization failed', 'error');
        return;
      }

      // Show optimization modal
      setOptimizationModal({
        isOpen: true,
        key: preference.key,
        original: preference.value,
        optimized: result.optimizedValue,
        onAccept: (optimized: string) => {
          updatePreference(index, 'value', optimized);
          setOptimizationModal(prev => ({ ...prev, isOpen: false }));
          showToast('Optimization accepted!');
        },
        onDecline: () => {
          setOptimizationModal(prev => ({ ...prev, isOpen: false }));
        }
      });

    } catch (error) {
      console.error('Optimization error:', error);
      showToast('Optimization failed. Please check your API key.', 'error');
    } finally {
      setIsOptimizing(null);
    }
  };

  const optimizeAllPreferences = async () => {
    const validPrefs = preferences.filter(p => p.key.trim() && p.value.trim());
    
    if (validPrefs.length === 0) {
      showToast('No preferences to optimize', 'error');
      return;
    }

    setIsOptimizingAll(true);
    let optimizedCount = 0;

    for (let i = 0; i < preferences.length; i++) {
      const pref = preferences[i];
      
      if (!pref.key.trim() || !pref.value.trim()) continue;

      try {
        const result = await optimizer.optimize(pref.key, pref.value);
        
        if (result.success) {
          updatePreference(i, 'value', result.optimizedValue);
          optimizedCount++;
        }
        
        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 200));
        
      } catch (error) {
        console.error(`Failed to optimize ${pref.key}:`, error);
      }
    }

    setIsOptimizingAll(false);
    showToast(`Optimized ${optimizedCount}/${validPrefs.length} preferences`);
  };

  const saveSettings = async () => {
    try {
      // Basic API key validation
      if (aiConfig.openaiApiKey && !aiConfig.openaiApiKey.startsWith('sk-')) {
        showToast('Please enter a valid OpenAI API key (starts with sk-)', 'error');
        return;
      }

      // Update AI configuration
      await storageManager.updateAIConfiguration(aiConfig);

      // Convert preferences array to object
      const preferencesObj: PersonalPreferences = {};
      preferences.forEach(pref => {
        if (pref.key.trim()) {
          preferencesObj[pref.key] = pref.value;
        }
      });

      await storageManager.updatePersonalPreferences(preferencesObj);
      showToast('Settings saved successfully!');

    } catch (error) {
      console.error('Save error:', error);
      showToast('Failed to save settings', 'error');
    }
  };

  const resetSettings = async () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      setAiConfig({ openaiApiKey: '', openaiModel: 'gpt-4o' });
      
      const defaultPrefs = Object.entries(DEFAULT_PERSONAL_PREFERENCES).map(([key, value]) => ({
        key,
        value
      }));
      setPreferences(defaultPrefs);
      
      await saveSettings();
      showToast('Settings reset to defaults');
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">⚙️ Nightcrawler Settings</h1>
          <p className="text-gray-600">Configure your LinkedIn job matching preferences and AI settings</p>
        </header>

        {/* AI Configuration Section */}
        <section className="settings-section mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">🤖 AI Configuration</h2>
          
          <div className="form-group">
            <label className="form-label">OpenAI API Key</label>
            <input 
              type="password" 
              className="input-field"
              placeholder="sk-..." 
              value={aiConfig.openaiApiKey}
              onChange={(e) => setAiConfig({ ...aiConfig, openaiApiKey: e.target.value })}
              autoComplete="off"
            />
            <p className="text-small mt-2">Your API key is stored locally and never transmitted to our servers.</p>
          </div>
          
          <div className="form-group">
            <label className="form-label">Model</label>
            <select 
              className="input-field"
              value={aiConfig.openaiModel}
              onChange={(e) => setAiConfig({ ...aiConfig, openaiModel: e.target.value as any })}
            >
              <option value="gpt-4o">GPT-4o (Recommended)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
          </div>
        </section>

        {/* Personal Preferences Section */}
        <section className="settings-section">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">👤 Personal Preferences</h2>
              <p className="text-small">Define your job preferences for AI-powered matching</p>
            </div>
            <button 
              onClick={optimizeAllPreferences}
              disabled={isOptimizingAll}
              className="btn-secondary disabled:opacity-50"
            >
              {isOptimizingAll ? '⏳ Optimizing...' : '✨ Optimize All'}
            </button>
          </div>
          
          <div className="space-y-6">
            {preferences.map((preference, index) => (
              <div key={index} className="card p-4 border border-gray-200">
                <div className="flex justify-between items-start mb-3">
                  <input 
                    type="text" 
                    className="font-medium text-sm bg-gray-50 border-0 p-2 rounded flex-1 mr-3" 
                    placeholder="e.g., Job Title, Experience, Technologies..."
                    value={preference.key}
                    onChange={(e) => updatePreference(index, 'key', e.target.value)}
                  />
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => optimizePreference(index)}
                      disabled={isOptimizing === preference.key}
                      className="text-sm px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition-colors disabled:opacity-50"
                    >
                      {isOptimizing === preference.key ? '⏳ Optimizing...' : '✨ Optimize'}
                    </button>
                    <button 
                      onClick={() => removePreference(index)}
                      className="text-sm px-3 py-1 bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
                    >
                      🗑️ Remove
                    </button>
                  </div>
                </div>
                <textarea 
                  className="textarea-field" 
                  rows={3} 
                  placeholder="Enter your preference details..."
                  value={preference.value}
                  onChange={(e) => updatePreference(index, 'value', e.target.value)}
                />
              </div>
            ))}
          </div>
          
          <button onClick={addPreference} className="btn-outline mt-4">
            ➕ Add New Preference
          </button>
        </section>

        {/* Actions */}
        <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
          <button onClick={resetSettings} className="btn-outline text-red-600 border-red-300 hover:bg-red-50">
            🔄 Reset to Defaults
          </button>
          <button onClick={saveSettings} className="btn-primary">
            💾 Save Settings
          </button>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className={`fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50 ${
          toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
        } text-white`}>
          {toast.message}
        </div>
      )}

      {/* Optimization Modal */}
      {optimizationModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Optimize: {optimizationModal.key}</h3>
              <button 
                onClick={optimizationModal.onDecline}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="form-label">Original:</label>
                <div className="bg-gray-50 p-3 rounded border text-sm">{optimizationModal.original}</div>
              </div>
              
              <div>
                <label className="form-label">Optimized:</label>
                <textarea 
                  className="textarea-field" 
                  rows={6}
                  value={optimizationModal.optimized}
                  onChange={(e) => setOptimizationModal(prev => ({ ...prev, optimized: e.target.value }))}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button onClick={optimizationModal.onDecline} className="btn-outline">
                  ❌ Decline
                </button>
                <button 
                  onClick={() => optimizationModal.onAccept(optimizationModal.optimized)} 
                  className="btn-primary"
                >
                  ✅ Accept
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Initialize React app
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<Settings />);
}