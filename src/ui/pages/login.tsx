// src/pages/Login.tsx

import React, { useState, FormEvent, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';
import { toast } from 'react-toastify';

// Use imported logo path
const logoPath = '/assets/grace_logo.png';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const router = useRouter();
  const { login, isAuthenticated, user } = useAuth();
  
  // Effect retained only for diagnostics; navigation is handled by AuthGuard to avoid races
  useEffect(() => {
    console.log('Navigation check:', { loginSuccess, isAuthenticated, user: !!user });
    // Intentionally no navigation here to prevent double redirects and remount loops
  }, [loginSuccess, isAuthenticated, user]);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    setLoginSuccess(false);

    try {
      // Use the standardized API client instead of direct fetch
      const { data, success } = await api.post(API_ENDPOINTS.AUTH.LOGIN, { 
        username, 
        password,
        remember_me: true // Set remember_me to true for persistent login
      });
      
      console.log('API Response:', { data, success });
      console.log('Token check:', { hasToken: !!data?.token, token: data?.token });
      
      if (success) {
        console.log('Login successful, token received:', data);
        
        // Do not write token directly; persistence handled by api client/AuthContext
        
        // Show success toast
        toast.success('Login successful! Redirecting...', {
          position: 'bottom-right',
          autoClose: 2000,
        });
        
        // Call login function and wait for it to complete
        console.log('Calling AuthContext login function with data:', data);
        const loginResult = await login(data);
        console.log('Login function result:', loginResult);
        
        // Mark login as successful - navigation will happen via useEffect
        setLoginSuccess(true);

        // Set a post-login redirect flag to help AuthGuard coordinate navigation
        try {
          sessionStorage.setItem('GRACE_POST_LOGIN_REDIRECT', '1');
        } catch {}

        // Do not navigate here to avoid racing with AuthGuard.
        // Navigation is centralized in useEffect when auth state updates.
      } else {
        // Show error toast
        toast.error(data?.message || 'Login failed', {
          position: 'bottom-right',
        });
        setError(data?.message || 'Login failed');
      }
    } catch (err: any) {
      const errorMsg = err?.message || 'Connection error';
      toast.error(errorMsg, { position: 'bottom-right' });
      setError(errorMsg);
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#140000] to-black">
      <div className="w-full max-w-sm p-8 space-y-6 rounded bg-black/80 text-white shadow-xl border border-red-900/30">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <img src={logoPath} alt="Grace Logo" className="w-64 h-auto mx-auto" />
          </div>
          <h1 className="text-3xl font-mono text-red-300 mb-4">Login</h1>
        </div>

        {error && <div className="p-2 text-sm bg-red-600/20 text-red-400 rounded">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className="text-sm block mb-1">Username</label>
            <input
              id="username"
              name="username"
              className="w-full p-2 rounded bg-white/10 focus:outline-none focus:ring-1 focus:ring-red-400 border border-white/20"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              autoComplete="username"
            />
          </div>

          <div>
            <label htmlFor="password" className="text-sm block mb-1">Password</label>
            <input
              id="password"
              type="password"
              name="password"
              className="w-full p-2 rounded bg-white/10 focus:outline-none focus:ring-1 focus:ring-red-400 border border-white/20"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              autoComplete="current-password"
            />
          </div>

          <div className="text-right text-sm">
            <Link href="/forgot" className="text-gray-400 hover:text-white">Forgot password?</Link>
          </div>

          <button
            type="submit"
            className="w-full py-2 text-white bg-red-700 hover:bg-red-900 rounded transition-colors"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <div className="flex items-center justify-center">
                <span className="mr-2">Signing in</span>
                <div className="animate-pulse">...</div>
              </div>
            ) : 'Sign in'}
          </button>

          <p className="text-center text-sm text-white">
            Don't have an account? <Link href="/register" className="text-red-500 hover:text-red-400 transition-colors">Sign up</Link>
          </p>
          
          <div className="mt-6 pt-4 border-t border-gray-700">
            <button 
              onClick={() => {
                // Copy wallet address to clipboard
                navigator.clipboard.writeText('5dFhFf5g2GCqNwZeTeirkZX9iwLqqFwGXuD4m5DhndD6');
                alert('Wallet address copied to clipboard: 5dFhFf5g2GCqNwZeTeirkZX9iwLqqFwGXuD4m5DhndD6');
              }}
              className="w-full py-2 text-white bg-green-700 hover:bg-green-800 rounded flex items-center justify-center transition-colors"
              type="button"
            >
              <span className="mr-2">💰</span> Donate to Grace
            </button>
            <p className="text-center text-xs text-gray-400 mt-2">
              Support Grace's development by donating to our wallet
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}