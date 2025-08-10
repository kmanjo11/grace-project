// src/pages/Forgot.tsx

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function Forgot() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleForgot = async () => {
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data?.message || 'Request failed');
        return;
      }
      setMessage('Check your inbox for password reset instructions.');
    } catch (err) {
      console.error('Forgot error:', err);
      setError('Connection error');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-sm rounded-xl bg-black/70 p-6 shadow-xl border border-red-700">
        <h1 className="mb-4 text-2xl font-mono text-red-400 text-center">Forgot Password</h1>
        <input
          type="email"
          placeholder="Enter your email"
          className="mb-3 w-full rounded bg-white/10 p-2 text-white"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        {message && <p className="mb-2 text-sm text-green-500">{message}</p>}
        {error && <p className="mb-2 text-sm text-red-500">{error}</p>}
        <button onClick={handleForgot} className="w-full rounded bg-red-700 px-4 py-2 hover:bg-red-900">
          Send Reset Link
        </button>
        <div className="mt-4 text-center text-sm text-gray-400">
          <Link href="/login" className="hover:text-red-400">Back to login</Link>
        </div>
      </div>
    </div>
  );
}
