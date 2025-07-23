
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, API_ENDPOINTS } from '../api/apiClient';
import { useAuth } from '../components/AuthContext';

export default function Register() {
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleRegister = async () => {
    setIsSubmitting(true);
    setError('');
    
    // Validate required fields
    if (!username || !firstName || !lastName || !email || !password || !confirmPassword) {
      setError('All fields except phone are required');
      setIsSubmitting(false);
      return;
    }
    
    // Validate password match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
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
      
      if (response.success && response.data?.token) {
        // Use the AuthContext to manage login state
        login(response.data);
        navigate('/chat');
      } else {
        setError(response.data?.message || 'Registration failed');
      }
    } catch (err) {
      console.error('Register error:', err);
      // @ts-ignore
      setError(err?.message || 'Connection error');
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
          onClick={handleRegister}
          disabled={isSubmitting}
          className={`mt-4 w-full rounded py-2 text-white font-medium ${isSubmitting ? 'bg-red-800' : 'bg-red-600 hover:bg-red-700'}`}
        >
          {isSubmitting ? 'Creating Account...' : 'Register'}
        </button>
        
        {/* Login link */}
        <div className="mt-4 text-center text-sm text-gray-400">
          Already have an account? <a href="/login" className="text-red-400 hover:text-red-300 hover:underline">Login</a>
        </div>
      </div>
    </div>
  );
}
