// src/components/LogoutButton.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.error('Logout request failed', err);
    } finally {
      localStorage.removeItem('token');
      navigate('/login');
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
