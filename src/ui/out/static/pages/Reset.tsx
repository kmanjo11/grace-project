// src/pages/Reset.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function Reset() {
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const tokenFromUrl = params.get('token');
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, [params]);

  const handleReset = async () => {
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data?.message || 'Reset failed');
        return;
      }
      setMessage('Password successfully reset. You may now log in.');
      setTimeout(() => navigate('/login'), 3000);
    } catch (err) {
      console.error('Reset error:', err);
      setError('Connection error');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-sm rounded-xl bg-black/70 p-6 shadow-xl border border-red-700">
        <h1 className="mb-4 text-2xl font-mono text-red-400 text-center">Reset Password</h1>
        <input
          type="password"
          placeholder="Enter new password"
          className="mb-3 w-full rounded bg-white/10 p-2 text-white"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {message && <p className="mb-2 text-sm text-green-500">{message}</p>}
        {error && <p className="mb-2 text-sm text-red-500">{error}</p>}
        <button onClick={handleReset} className="w-full rounded bg-red-700 px-4 py-2 hover:bg-red-900">
          Reset Password
        </button>
        <div className="mt-4 text-center text-sm text-gray-400">
          <a href="/login" className="hover:text-red-400">Return to login</a>
        </div>
      </div>
    </div>
  );
}
