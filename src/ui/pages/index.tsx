import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../components/AuthContext';
import { getAuthToken } from '../api/apiClient';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, user, loading } = useAuth();

  useEffect(() => {
    // Small delay to allow auth state to settle on initial mount
    const id = setTimeout(() => {
      const tokenExists = !!getAuthToken();
      if ((isAuthenticated && user) || tokenExists) {
        router.replace('/chat');
      } else {
        router.replace('/login');
      }
    }, loading ? 200 : 50);
    return () => clearTimeout(id);
  }, [router, isAuthenticated, user, loading]);

  // This will be shown briefly before the redirect happens
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl">Loading Grace Terminal...</h2>
      </div>
    </div>
  );
}