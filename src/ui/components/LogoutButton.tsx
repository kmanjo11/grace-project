// src/components/LogoutButton.tsx

import React from 'react';
import { useRouter } from 'next/router';
import { useAuth } from './AuthContext';
import api from '../api/apiClient';
import { API_ENDPOINTS } from '../api/apiClient';
import StatePersistenceManager from '../utils/StatePersistence';

export default function LogoutButton() {
  const router = useRouter();
  const { logout } = useAuth(); // Use the standardized logout function from AuthContext

  const handleLogout = async () => {
    try {
      // Clear persistent state snapshot
      StatePersistenceManager.clearSnapshot();
      
      // Use the standardized logout function that handles everything
      await logout();
      
      // After successful logout, redirect to login page
      router.push('/login');
    } catch (err) {
      console.error('Logout failed:', err);
      // Still navigate to login even if the API call fails
      router.push('/login');
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="transition-all hover:text-red-400 pb-1 text-white"
    >
      Logout
    </button>
  );
}
