// src/pages/Settings.tsx

import React, { useEffect, useRef, useState } from 'react';
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
  const { user, updateUser } = useAuth();
  const [settings, setSettings] = useState<UserSettings>({});
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');  
  const [isLoading, setIsLoading] = useState(false);
  const fetchedForUserRef = useRef<string | undefined>(undefined);
  const fetchInFlightRef = useRef<boolean>(false);

  // Recursively unwrap nested { settings: {...} } and drop any { success: true } wrappers
  const sanitizeSettings = (input: any): any => {
    let current = input;
    const seen = new Set<any>();
    while (current && typeof current === 'object' && !Array.isArray(current) && !seen.has(current)) {
      seen.add(current);
      // strip success flag while preserving other keys
      if ('success' in current && Object.keys(current).length >= 1) {
        const { success: _s, ...rest } = current as any;
        current = rest;
      }
      // unwrap settings key if it dominates the shape
      if (
        current && typeof current === 'object' && 'settings' in current &&
        Object.keys(current).length <= 2 // allow one payload field like displayName alongside accidental nesting
      ) {
        current = (current as any).settings;
        continue;
      }
      break;
    }
    return current;
  };

  useEffect(() => {
    const fetchSettings = async () => {
      if (fetchInFlightRef.current) return;
      fetchInFlightRef.current = true;
      const controller = new AbortController();
      try {
        setIsLoading(true);
        setError('');
        
        const { data, success } = await api.get(API_ENDPOINTS.SETTINGS.PROFILE, { signal: controller.signal as any });
        
        if (success && data) {
          // Backend returns { success: true, settings: {...} } but guard against any accidental nesting
          const payload: any = data as any;
          const flat = sanitizeSettings(payload?.settings ?? payload);
          setSettings(flat || {});
          // Cache displayName locally to support immediate/persistent Chat header label
          try {
            if (typeof window !== 'undefined' && flat?.displayName) {
              localStorage.setItem('displayName', flat.displayName);
            }
          } catch {}
        } else {
          throw new Error(data?.error || 'Failed to load settings');
        }
      } catch (err: any) {
        if (err?.name === 'AbortError') return;
        console.error('Error loading settings:', err);
        setError(err?.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
        fetchInFlightRef.current = false;
      }
    };
    
    const currentUserId = (user as any)?.id || (user as any)?.user_id || (user as any)?.username;
    if (currentUserId && fetchedForUserRef.current !== currentUserId) {
      fetchedForUserRef.current = currentUserId;
      fetchSettings();
    }
  }, [user?.id, (user as any)?.user_id, (user as any)?.username]);

  const updateSettings = async () => {
    try {
      setMessage('');
      setError('');
      setIsLoading(true);
      
      // Avoid and remove any nested wrappers before POST
      let toSave: any = sanitizeSettings(settings);

      const { data, success } = await api.post(API_ENDPOINTS.SETTINGS.PROFILE, { settings: toSave });
      
      if (success) {
        setMessage(data?.message || 'Settings updated successfully');
        // Update AuthContext so display name propagates to UI instantly
        if (toSave.displayName !== undefined) {
          updateUser({ displayName: toSave.displayName });
          try { if (typeof window !== 'undefined') localStorage.setItem('displayName', String(toSave.displayName || '')); } catch {}
        }
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
