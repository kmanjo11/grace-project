import { NavigateFunction } from 'react-router-dom';
import StateOperationLock from './StateOperationLock';

// Define the shape of our persistent state
export interface DynamicStateSnapshot {
  timestamp: number;
  version?: number;      // Schema version for migrations
  recovered?: boolean;   // Flag for recovered state
  userSession: {
    token?: string;
    username?: string;
  };
  chatContext: {
    currentConversationId?: string;
    draftMessage?: string;
    lastMessageTimestamp?: number;
  };
  pageState: {
    lastVisitedPath?: string;
    scrollPositions?: Record<string, number>;
  };
  widgetStates: {
    tradingPositions?: any[];
    walletBalance?: number;
  };
  
  // Extended state properties
  chatState?: {
    currentSessionId?: string;
    activeSessions?: string[];
    sessions?: Record<string, any>;
    draftMessages?: Record<string, string>;
  };
  
  tradingState?: {
    selectedToken?: any;
    watchlist?: string[];
    tradeHistory?: any[];
    tradeForm?: any;
    resolution?: string;
    search?: string;
    positions?: any[];
  };
  
  walletState?: {
    connectedWallets?: any[];
    transactions?: any[];
  };
  
  socialState?: {
    posts?: any[];
    following?: string[];
    notifications?: any[];
  };
  
  uiState?: {
    darkMode?: boolean;
    sidebarOpen?: boolean;
    activeTabs?: Record<string, string>;
  };
}

class StatePersistenceManager {
  static getStoredState() {
    throw new Error('Method not implemented.');
  }
  // Storage keys - making this public so it can be referenced by sync logic
  public static STORAGE_KEY = 'GRACE_DYNAMIC_SNAPSHOT';
  private static MAX_SNAPSHOT_AGE = 24 * 60 * 60 * 1000; // 24 hours
  private static STORAGE_VERSION = 1; // Used for schema migrations
  private static MAX_STORAGE_SIZE = 4 * 1024 * 1024; // 4MB max size (localStorage is typically 5MB)

  // Advanced logging mechanism
  private static log(message: string, level: 'info' | 'warn' | 'error' = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[StatePersistence:${level.toUpperCase()}] ${timestamp} - ${message}`;
    
    switch(level) {
      case 'info': console.log(logMessage); break;
      case 'warn': console.warn(logMessage); break;
      case 'error': console.error(logMessage); break;
    }

    // Optional: Send to error tracking service
    // this.reportToErrorTracking(message, level);
  }

  // Check storage quota and manage size
  private static async checkStorageQuota(): Promise<boolean> {
    try {
      // Use the Storage API if available (modern browsers)
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        const { usage, quota } = estimate;
        
        if (usage && quota) {
          const usageRatio = usage / quota;
          this.log(`Storage usage: ${(usageRatio * 100).toFixed(2)}% (${Math.round(usage / 1024 / 1024)}MB / ${Math.round(quota / 1024 / 1024)}MB)`);
          
          // If over 90% of quota, try to clean up
          if (usageRatio > 0.9) {
            this.log('Storage quota nearing limit, cleaning up old data', 'warn');
            return this.cleanupStorage();
          }
        }
      } else {
        // Fallback for browsers without Storage API
        // Check current storage size
        let totalSize = 0;
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key) {
            const value = localStorage.getItem(key) || '';
            totalSize += key.length + value.length;
          }
        }
        
        // Convert to MB for easier debugging
        const sizeMB = totalSize / (1024 * 1024);
        this.log(`Estimated localStorage usage: ${sizeMB.toFixed(2)}MB`);
        
        // If over 4MB, clean up (typical localStorage limit is 5MB)
        if (totalSize > this.MAX_STORAGE_SIZE) {
          this.log('Storage size nearing limit, cleaning up old data', 'warn');
          return this.cleanupStorage();
        }
      }
      
      return true;
    } catch (error) {
      this.log(`Error checking storage quota: ${error}`, 'error');
      return true; // Continue anyway to not block operation
    }
  }
  
  // Clean up storage when approaching quota limits
  private static cleanupStorage(): boolean {
    try {
      // Strategy 1: Remove old chat messages (typically the largest data)
      const keysToCheck: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('messages_') || key.includes('draft_'))) {
          keysToCheck.push(key);
        }
      }
      
      // Sort by last access time if available
      const keysWithTime = keysToCheck.map(key => {
        // Ensure key is a string before calling replace
        const sessionId = String(key).replace('messages_', '').replace('draft_', '');
        const lastSynced = localStorage.getItem(`lastSynced_${sessionId}`);
        const timestamp = lastSynced ? new Date(lastSynced).getTime() : 0;
        return { key, timestamp };
      });
      
      // Sort oldest first
      keysWithTime.sort((a, b) => a.timestamp - b.timestamp);
      
      // Remove oldest 30% of items
      const itemsToRemove = Math.ceil(keysWithTime.length * 0.3);
      for (let i = 0; i < itemsToRemove; i++) {
        if (i < keysWithTime.length) {
          localStorage.removeItem(keysWithTime[i].key);
          this.log(`Removed old data: ${keysWithTime[i].key}`);
        }
      }
      
      // Strategy 2: If main snapshot is too large, try to trim it
      const snapshot = localStorage.getItem(this.STORAGE_KEY);
      if (snapshot && snapshot.length > 1024 * 1024) { // If over 1MB
        try {
          const parsedSnapshot = JSON.parse(snapshot);
          
          // Trim message history to reduce size
          if (parsedSnapshot.chatContext && parsedSnapshot.chatContext.messages) {
            // Keep only last 20 messages
            parsedSnapshot.chatContext.messages = 
              parsedSnapshot.chatContext.messages.slice(-20);
          }
          
          // Store the trimmed version
          localStorage.setItem(this.STORAGE_KEY, JSON.stringify(parsedSnapshot));
          this.log('Trimmed main snapshot size');
        } catch (e) {
          this.log(`Error trimming snapshot: ${e}`, 'error');
        }
      }
      
      return true;
    } catch (error) {
      this.log(`Error cleaning up storage: ${error}`, 'error');
      return false;
    }
  }
  
  // Validate snapshot structure and schema
  private static validateSnapshotSchema(snapshot: any): boolean {
    if (!snapshot || typeof snapshot !== 'object') return false;
    
    // Check required fields
    if (typeof snapshot.timestamp !== 'number') return false;
    
    // Check for required sub-objects
    const requiredObjects = ['userSession', 'chatContext', 'pageState', 'widgetStates'];
    for (const obj of requiredObjects) {
      if (!snapshot[obj] || typeof snapshot[obj] !== 'object') {
        return false;
      }
    }
    
    return true;
  }

  // Create a backup of the current snapshot
  private static createBackup(): void {
    try {
      const currentSnapshot = localStorage.getItem(this.STORAGE_KEY);
      if (currentSnapshot) {
        localStorage.setItem(`${this.STORAGE_KEY}_BACKUP`, currentSnapshot);
      }
    } catch (error) {
      this.log(`Failed to create backup: ${error}`, 'warn');
    }
  }

  // Capture the current application state with enhanced safety
  static async captureSnapshot(partialState?: Partial<DynamicStateSnapshot>): Promise<void> {
    // Acquire a lock for state operations to prevent race conditions
    const lockId = StateOperationLock.acquireLock('state_snapshot', 'capture_snapshot');
    if (!lockId) {
      this.log('Could not acquire lock for state operation, another operation is in progress', 'warn');
      return;
    }
    
    try {
      // Validate storage availability
      if (!this.isStorageAvailable()) {
        this.log('Local storage not available', 'warn');
        return;
      }
      
      // Check quota before writing
      const quotaOk = await this.checkStorageQuota();
      if (!quotaOk) {
        this.log('Storage quota issues, data may not be saved completely', 'warn');
      }

      const existingSnapshot = this.retrieveSnapshot();
      const newSnapshot: DynamicStateSnapshot = {
        timestamp: Date.now(),
        version: this.STORAGE_VERSION, // Add version for schema migrations
        userSession: partialState?.userSession || existingSnapshot?.userSession || {},
        chatContext: partialState?.chatContext || existingSnapshot?.chatContext || {},
        pageState: partialState?.pageState || existingSnapshot?.pageState || {},
        widgetStates: partialState?.widgetStates || existingSnapshot?.widgetStates || {}
      };

      // Create a backup of the current state before updating
      this.createBackup();
      
      // Attempt to save state
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newSnapshot));
        this.log('State snapshot captured successfully');
      } catch (storageError) {
        // If failed due to quota, force cleanup and try again
        this.log(`Storage error, forcing cleanup: ${storageError}`, 'warn');
        this.cleanupStorage();
        
        // Try one more time with a more minimal state
        const minimalSnapshot = {
          timestamp: Date.now(),
          version: this.STORAGE_VERSION,
          userSession: newSnapshot.userSession,
          // Minimal objects to ensure basic functionality
          chatContext: { currentConversationId: newSnapshot.chatContext.currentConversationId },
          pageState: { lastVisitedPath: newSnapshot.pageState.lastVisitedPath },
          widgetStates: {}
        };
        
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(minimalSnapshot));
        this.log('Minimal state snapshot saved as fallback');
      }
    } catch (error) {
      this.log(`Failed to capture state snapshot: ${error}`, 'error');
    } finally {
      // Always release the lock
      StateOperationLock.releaseLock('state_snapshot', lockId);
    }
  }

  // Check local storage availability
  private static isStorageAvailable(): boolean {
    try {
      const testKey = '__storage_test__';
      localStorage.setItem(testKey, testKey);
      localStorage.removeItem(testKey);
      return true;
    } catch (e) {
      return false;
    }
  }

  // Validate snapshot age and integrity
  private static validateSnapshot(snapshot: DynamicStateSnapshot): boolean {
    if (!snapshot) return false;

    // Check schema/structure validity
    if (!this.validateSnapshotSchema(snapshot)) {
      this.log('Snapshot has invalid schema, discarding', 'warn');
      return false;
    }

    const currentTime = Date.now();
    const snapshotAge = currentTime - snapshot.timestamp;

    if (snapshotAge > this.MAX_SNAPSHOT_AGE) {
      this.log('Snapshot too old, discarding', 'warn');
      return false;
    }

    return true;
  }

  // Retrieve the last saved state snapshot with corruption recovery
  static retrieveSnapshot(): DynamicStateSnapshot | null {
    // We don't lock for reads, but we do check if there's a write in progress
    if (StateOperationLock.isLocked('state_snapshot')) {
      this.log('State snapshot is currently being updated, using existing snapshot', 'warn');
    }
    
    try {
      const snapshot = localStorage.getItem(this.STORAGE_KEY);
      if (!snapshot) return null;

      try {
        const parsedSnapshot: DynamicStateSnapshot = JSON.parse(snapshot);
        
        // Validate snapshot integrity
        if (this.validateSnapshot(parsedSnapshot)) {
          return parsedSnapshot;
        } else {
          this.log('Invalid snapshot detected, attempting recovery', 'warn');
          return this.attemptSnapshotRecovery();
        }
      } catch (parseError) {
        this.log(`JSON parse error: ${parseError}, attempting recovery`, 'error');
        return this.attemptSnapshotRecovery();
      }
    } catch (error) {
      this.log(`Failed to retrieve state snapshot: ${error}`, 'error');
      return null;
    }
  }
  
  // Attempt to recover corrupted state
  private static attemptSnapshotRecovery(): DynamicStateSnapshot | null {
    try {
      this.log('Attempting state recovery', 'warn');
      
      // Strategy 1: Check for backup
      const backupSnapshot = localStorage.getItem(`${this.STORAGE_KEY}_BACKUP`);
      if (backupSnapshot) {
        try {
          const parsedBackup = JSON.parse(backupSnapshot);
          if (this.validateSnapshot(parsedBackup)) {
            this.log('Recovered state from backup', 'info');
            return parsedBackup;
          }
        } catch (e) {
          this.log('Backup snapshot also corrupted', 'warn');
        }
      }
      
      // Strategy 2: Build from individual pieces in localStorage
      const recoveredState: DynamicStateSnapshot = {
        timestamp: Date.now(),
        version: this.STORAGE_VERSION,
        userSession: {},
        chatContext: {},
        pageState: {},
        widgetStates: {}
      };
      
      // Try to get last path from localStorage
      const activeSessionId = localStorage.getItem('activeSessionId');
      if (activeSessionId) {
        recoveredState.chatContext.currentConversationId = activeSessionId;
      }
      
      // Set recovery flag
      recoveredState.recovered = true;
      
      this.log('Created minimal recovered state', 'info');
      return recoveredState;
    } catch (error) {
      this.log(`Recovery failed: ${error}`, 'error');
      return null;
    }
  }

  // Hydrate application state
  static hydrateState(navigate?: NavigateFunction): Partial<DynamicStateSnapshot> {
    const snapshot = this.retrieveSnapshot();
    
    if (snapshot) {
      // Optionally navigate to last visited path
      if (navigate && snapshot.pageState.lastVisitedPath) {
        navigate(snapshot.pageState.lastVisitedPath);
      }

      return snapshot;
    }

    return {};
  }

  // Clear the snapshot (used during logout)
  static clearSnapshot(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}

// Prevent accidental page unload
export function preventUnintendedRefresh(e: BeforeUnloadEvent) {
  e.preventDefault();
  e.returnValue = ''; // Required for Chrome
}

export default StatePersistenceManager;
