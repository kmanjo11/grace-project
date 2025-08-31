// src/pages/Reset.tsx

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { api, API_ENDPOINTS } from '../api/apiClient';

export default function Reset() {
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  

  useEffect(() => {
    const { token: tokenFromUrl } = router.query;
    if (tokenFromUrl && typeof tokenFromUrl === 'string') {
      setToken(tokenFromUrl);
    }
  }, [router.query]);

  const handleReset = async () => {
    try {
      const res = await api.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, { token, password });
      if (!res.success) {
        setError(res.error || (res.data as any)?.message || 'Reset failed');
        return;
      }
      setError('');
      setMessage('Password successfully reset. You may now log in.');
      setTimeout(() => router.push('/login'), 3000);
    } catch (err) {
      console.error('Reset error:', err);
      setError(err instanceof Error ? err.message : 'Connection error');
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
          <Link href="/login" className="hover:text-red-400">Return to login</Link>
        </div>
      </div>
    </div>
  );
}
