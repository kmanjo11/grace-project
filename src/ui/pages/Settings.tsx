// src/pages/Settings.tsx

import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';

interface UserSettings {
  displayName?: string;
  email?: string;
  notifications?: {
    email: boolean;
    push: boolean;
  };
  theme?: string;
  language?: string;
  [key: string]: any;
}

export default function Settings() {
  const { user } = useAuth();
  const [settings, setSettings] = useState<UserSettings>({});
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');  
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        setError('');
        
        const { data, success } = await api.get(API_ENDPOINTS.SETTINGS.PROFILE);
        
        if (success && data) {
          setSettings(data);
        } else {
          throw new Error(data?.error || 'Failed to load settings');
        }
      } catch (err: any) {
        console.error('Error loading settings:', err);
        setError(err?.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (user) {
      fetchSettings();
    }
  }, [user]);

  const updateSettings = async () => {
    try {
      setMessage('');
      setError('');
      setIsLoading(true);
      
      const { data, success } = await api.post(API_ENDPOINTS.SETTINGS.PROFILE, { settings });
      
      if (success) {
        setMessage(data?.message || 'Settings updated successfully');
      } else {
        throw new Error(data?.error || 'Failed to update settings');
      }
    } catch (err: any) {
      console.error('Settings update error:', err);
      setError(err?.message || 'Failed to update settings');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h1 className="text-2xl font-mono text-red-300">User Settings</h1>
      
      {isLoading && <p className="text-blue-300 text-sm">Loading...</p>}
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {message && <p className="text-green-500 text-sm">{message}</p>}

      <div className="space-y-4">
          <label className="block text-sm">
            Display Name:
            <input
              className="w-full mt-1 p-2 rounded bg-white/10 text-white"
              value={settings.displayName || ''}
              onChange={(e) => setSettings({ ...settings, displayName: e.target.value })}
              placeholder="Your name"
            />
          </label>

          <label className="block text-sm">
            Default Token:
            <input
              className="w-full mt-1 p-2 rounded bg-white/10 text-white"
              value={settings.defaultToken || ''}
              onChange={(e) => setSettings({ ...settings, defaultToken: e.target.value })}
              placeholder="e.g. SOL, USDC"
            />
          </label>

          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={settings.notificationsEnabled || false}
              onChange={() => setSettings({
                ...settings,
                notificationsEnabled: !settings.notificationsEnabled,
              })}
            />
            <span>Enable notifications</span>
          </label>

          <button
            onClick={updateSettings}
            className="w-full rounded bg-red-700 px-4 py-2 hover:bg-red-900"
          >
            Save Settings
          </button>

          {message && <p className="text-green-400 text-sm">{message}</p>}
        </div>
      </div>
  );
}
