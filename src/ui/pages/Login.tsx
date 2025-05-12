// src/pages/Login.tsx

import React, { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';

// Hardcoded logo path for direct reference
const logoPath = '/assets/grace_logo.png';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      // Use the standardized API client instead of direct fetch
      const { data, success } = await api.post(API_ENDPOINTS.AUTH.LOGIN, { 
        username, 
        password,
        remember_me: true // Set remember_me to true for persistent login
      });
      
      if (success && data?.token) {
        // Log the entire response data structure to see what we're getting
        console.log('Login response data:', JSON.stringify(data, null, 2));
        console.log('Login successful, token received:', data.token.substring(0, 15) + '...');
        
        // Store token directly here as backup
        const rememberMe = true; // Force localStorage for testing
        localStorage.setItem('grace_token', data.token);
        console.log('Token manually stored in localStorage');
        
        // Then call login function
        login(data);
        
        // Debug token storage after login
        setTimeout(() => {
          const storedToken = localStorage.getItem('grace_token') || sessionStorage.getItem('grace_token');
          console.log('Token in storage after login check:', storedToken ? storedToken.substring(0, 15) + '...' : 'None');
        }, 500);
        
        navigate('/chat');
      } else {
        setError(data?.message || 'Login failed');
      }
    } catch (err: any) {
      setError('Connection error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#190000]">
      <div className="w-full max-w-sm p-8 space-y-6 rounded bg-black/80 text-white shadow-xl">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <img src={logoPath} alt="Grace Logo" className="w-82 h-auto" />
          </div>
          <h1 className="text-3xl font-mono text-red-300">Login</h1>
        </div>

        {error && <div className="p-2 text-sm bg-red-600/20 text-red-400 rounded">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className="text-sm block mb-1">Username</label>
            <input
              id="username"
              className="w-full p-2 rounded bg-white/10 focus:outline-none"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
            />
          </div>

          <div>
            <label htmlFor="password" className="text-sm block mb-1">Password</label>
            <input
              id="password"
              type="password"
              className="w-full p-2 rounded bg-white/10 focus:outline-none"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
            />
          </div>

          <div className="text-right text-sm">
            <a href="/forgot" className="text-gray-400 hover:text-white">Forgot password?</a>
          </div>

          <button
            type="submit"
            className="w-full py-2 text-white bg-red-700 hover:bg-red-900 rounded"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="text-center text-sm text-white">
            Don’t have an account? <a href="/register" className="text-red-500">Sign up</a>
          </p>
          
          <div className="mt-6 pt-4 border-t border-gray-700">
            <button 
              onClick={() => {
                // Copy wallet address to clipboard
                navigator.clipboard.writeText('5dFhFf5g2GCqNwZeTeirkZX9iwLqqFwGXuD4m5DhndD6');
                alert('Wallet address copied to clipboard: 5dFhFf5g2GCqNwZeTeirkZX9iwLqqFwGXuD4m5DhndD6');
              }}
              className="w-full py-2 text-white bg-green-700 hover:bg-green-800 rounded flex items-center justify-center"
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