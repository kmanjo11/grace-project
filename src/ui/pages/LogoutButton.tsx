// src/components/LogoutButton.tsx

import React from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../components/AuthContext';

export default function LogoutButton() {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      // Use centralized auth flow which clears tokens consistently
      await logout();
    } catch (err) {
      console.error('Logout error', err);
    } finally {
      router.push('/login');
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="rounded bg-red-700 px-3 py-1 text-sm text-white hover:bg-red-900"
    >
      Logout
    </button>
  );
}
