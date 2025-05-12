// src/components/LogoutButton.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import api from '../api/apiClient';
import { API_ENDPOINTS } from '../api/apiClient';
import StatePersistenceManager from '../utils/StatePersistence';

export default function LogoutButton() {
  const navigate = useNavigate();
  const { logout } = useAuth(); // Use the standardized logout function from AuthContext

  const handleLogout = async () => {
    try {
      // Clear persistent state snapshot
      StatePersistenceManager.clearSnapshot();
      
      // Use the standardized logout function that handles everything
      await logout();
      
      // After successful logout, redirect to login page
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
      // Still navigate to login even if the API call fails
      navigate('/login');
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
