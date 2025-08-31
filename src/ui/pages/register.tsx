import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS } from '../api/apiClient';
import { toast } from 'react-toastify';

export default function Register() {
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);
  const router = useRouter();
  const { login, isAuthenticated, user } = useAuth();

  // After successful registration, rely on AuthGuard for navigation to avoid races
  useEffect(() => {
    if (registerSuccess && isAuthenticated && user) {
      console.log('Registration and authentication confirmed; navigation handled by AuthGuard');
      // Optionally set a one-time flag similar to login, if desired
      try { sessionStorage.setItem('GRACE_POST_LOGIN_REDIRECT', '1'); } catch {}
    }
  }, [registerSuccess, isAuthenticated, user]);

  const handleRegister = async () => {
    setIsSubmitting(true);
    setError('');
    setRegisterSuccess(false);

    // Validate required fields
    if (!username || !firstName || !lastName || !email || !password || !confirmPassword) {
      const errorMsg = 'All fields except phone are required';
      toast.error(errorMsg, { position: 'bottom-right' });
      setError(errorMsg);
      setIsSubmitting(false);
      return;
    }

    // Validate password match
    if (password !== confirmPassword) {
      const errorMsg = 'Passwords do not match';
      toast.error(errorMsg, { position: 'bottom-right' });
      setError(errorMsg);
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await api.post(API_ENDPOINTS.AUTH.REGISTER, {
        username,
        firstName,
        lastName,
        email,
        password,
        phone
      });

      if (response.success) {
        // Show success toast
        toast.success('Registration successful! Redirecting...', {
          position: 'bottom-right',
          autoClose: 2000,
        });

        // Use the AuthContext to manage login state - await completion
        await login(response.data || {});

        // Mark registration as successful - navigation will happen via useEffect
        setRegisterSuccess(true);
      } else {
        const errorMsg = response.error || response.data?.message || 'Registration failed';
        toast.error(errorMsg, { position: 'bottom-right' });
        setError(errorMsg);
      }
    } catch (err) {
      console.error('Register error:', err);
      const errorMsg = err instanceof Error ? err.message : 'Registration failed';
      toast.error(errorMsg, { position: 'bottom-right' });
      setError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-black text-white">
      <div className="w-full max-w-sm rounded-xl bg-black/70 p-6 shadow-xl border border-red-700">
        <h1 className="mb-4 text-2xl font-mono text-red-400 text-center">Create Grace Account</h1>

        {/* Username field - always required */}
        <div className="mb-3">
          <input
            type="text"
            placeholder="Username"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        {/* Name fields - explicitly visible */}
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            placeholder="First Name"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Last Name"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>

        {/* Email field */}
        <div className="mb-3">
          <input
            type="email"
            placeholder="Email"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        {/* Password fields */}
        <div className="mb-3">
          <input
            type="password"
            placeholder="Password"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <input
            type="password"
            placeholder="Confirm Password"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>

        {/* Phone field - optional */}
        <div className="mb-3">
          <input
            type="text"
            placeholder="Phone (optional)"
            className="w-full rounded bg-white/10 p-2 text-white"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-2 p-2 bg-red-900/30 rounded border border-red-800">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          onClick={handleRegister}
          className="w-full py-2 text-white bg-red-700 hover:bg-red-900 rounded transition-colors"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center">
              <span className="mr-2">Creating Account</span>
              <div className="animate-pulse">...</div>
            </div>
          ) : 'Create Account'}
        </button>

        {/* Login link */}
        <div className="mt-4 text-center text-sm text-gray-400">
          Already have an account? <Link href="/login" className="text-red-400 hover:text-red-300 hover:underline">Login</Link>
        </div>
      </div>
    </div>
  );
}
