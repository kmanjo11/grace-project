import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useAppState } from '../context/AppStateContext';
import StateBackupService from '../utils/StateBackupService';
import { useAuth } from './AuthContext';

interface StateLoaderProps {
  children: React.ReactNode;
}

const StateLoader: React.FC<StateLoaderProps> = ({ children }) => {
  const { isStateLoading, isStateHydrated, isStateRecovered, isStateSyncing, dispatch } = useAppState();
  const { user, isAuthenticated } = useAuth();
  const [showSyncNotice, setShowSyncNotice] = useState(false);
  const [showHydrationNotice, setShowHydrationNotice] = useState(false);
  const [showRecoveryAttempt, setShowRecoveryAttempt] = useState(false);
  const isInitialMount = useRef(true);
  const backupService = useRef<StateBackupService | null>(null);
  const recoveryAttemptMade = useRef(false);
  
  // Handle sync notice display and auto-hide
  useEffect(() => {
    if (isStateSyncing) {
      setShowSyncNotice(true);
      // Auto-hide sync notice after 3 seconds
      const timer = setTimeout(() => setShowSyncNotice(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [isStateSyncing]);
  
  // Initialize the state backup service
  useEffect(() => {
    if (isAuthenticated && user) {
      try {
        // Initialize the backup service
        const service = StateBackupService.getInstance();
        backupService.current = service;
        service.initialize().then(success => {
          console.log(`State backup service initialized: ${success ? 'success' : 'fallback mode'}`);
        });
      } catch (error) {
        console.error('Failed to initialize state backup service:', error);
      }
    }
    
    return () => {
      // Clean up backup service on unmount
      if (backupService.current) {
        backupService.current.stopPeriodicBackup();
      }
    };
  }, [isAuthenticated, user]);
  
  // Attempt recovery if needed
  const attemptStateRecovery = useCallback(async () => {
    if (!isStateHydrated && !isStateLoading && !recoveryAttemptMade.current) {
      recoveryAttemptMade.current = true;
      setShowRecoveryAttempt(true);
      
      try {
        if (backupService.current) {
          const recoveredState = await backupService.current.attemptRecovery();
          if (recoveredState) {
            console.log('Successfully recovered state from backup source');
            dispatch({ type: 'HYDRATE_STATE', payload: recoveredState });
            setShowHydrationNotice(true);
            setTimeout(() => setShowHydrationNotice(false), 3000);
          }
        }
      } catch (error) {
        console.error('Error during state recovery attempt:', error);
      } finally {
        setShowRecoveryAttempt(false);
      }
    }
  }, [dispatch, isStateHydrated, isStateLoading]);
  
  // Trigger recovery attempt if state is not hydrated
  useEffect(() => {
    if (isAuthenticated && !isStateHydrated && !isStateLoading) {
      const timer = setTimeout(() => {
        attemptStateRecovery();
      }, 1000); // Wait 1 second before attempting recovery
      
      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, isStateHydrated, isStateLoading, attemptStateRecovery]);

  // Handle hydration notice only for non-initial state hydrations
  useEffect(() => {
    // Skip the initial mount effect - this prevents showing notification on first load
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    
    // Only show hydration notice for subsequent hydrations
    if (isStateHydrated && !isStateLoading) {
      setShowHydrationNotice(true);
      const timer = setTimeout(() => setShowHydrationNotice(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [isStateHydrated, isStateLoading]);

  if (isStateLoading || showRecoveryAttempt) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-gray-900 p-6 rounded-lg shadow-lg text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gold mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold text-gold mb-2">
            {showRecoveryAttempt ? 'Recovering Your Data' : 'Loading Your Trading State'}
          </h3>
          <p className="text-gray-400">
            {showRecoveryAttempt 
              ? 'Attempting to recover your session data...' 
              : 'Restoring your previous session...'}
          </p>
        </div>
      </div>
    );
  }

  // Show recovery notification if state was recovered from corruption
  if (isStateRecovered) {
    return (
      <>
        <div className="fixed bottom-4 right-4 bg-gray-900 text-yellow-500 px-4 py-2 rounded shadow-lg 
                      border border-yellow-600 transition-opacity duration-1000 z-40">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>Session was partially recovered due to data corruption</span>
          </div>
        </div>
        {children}
      </>
    );
  }
  
  // Show a brief flash notification when state is hydrated but not on initial load
  if (showHydrationNotice) {
    return (
      <>
        <div className="fixed bottom-4 right-4 bg-gray-900 text-green-400 px-4 py-2 rounded shadow-lg 
                       transition-opacity duration-1000 z-40">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Session restored successfully</span>
          </div>
        </div>
        {children}
      </>
    );
  }
  
  // Show cross-tab sync notification
  if (showSyncNotice) {
    return (
      <>
        <div className="fixed bottom-4 right-4 bg-gray-800 text-blue-400 px-4 py-2 rounded shadow-lg 
                       transition-opacity duration-300 z-40 border border-blue-600">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Syncing state from another tab...</span>
          </div>
        </div>
        {children}
      </>
    );
  }

  // Default render
  return <>{children}</>;
};

export default StateLoader;
