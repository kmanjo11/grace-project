import { NavigateFunction } from 'react-router-dom';

// Define the shape of our persistent state
export interface DynamicStateSnapshot {
  timestamp: number;
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
}

class StatePersistenceManager {
  private static STORAGE_KEY = 'GRACE_DYNAMIC_SNAPSHOT';
  private static MAX_SNAPSHOT_AGE = 24 * 60 * 60 * 1000; // 24 hours

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

  // Capture the current application state with enhanced safety
  static captureSnapshot(partialState?: Partial<DynamicStateSnapshot>): void {
    try {
      // Validate storage availability
      if (!this.isStorageAvailable()) {
        this.log('Local storage not available', 'warn');
        return;
      }

      const existingSnapshot = this.retrieveSnapshot();
      const newSnapshot: DynamicStateSnapshot = {
        timestamp: Date.now(),
        userSession: partialState?.userSession || existingSnapshot?.userSession || {},
        chatContext: partialState?.chatContext || existingSnapshot?.chatContext || {},
        pageState: partialState?.pageState || existingSnapshot?.pageState || {},
        widgetStates: partialState?.widgetStates || existingSnapshot?.widgetStates || {}
      };

      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newSnapshot));
      this.log('State snapshot captured successfully');
    } catch (error) {
      this.log(`Failed to capture state snapshot: ${error}`, 'error');
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

    const currentTime = Date.now();
    const snapshotAge = currentTime - snapshot.timestamp;

    if (snapshotAge > this.MAX_SNAPSHOT_AGE) {
      this.log('Snapshot too old, discarding', 'warn');
      return false;
    }

    return true;
  }

  // Retrieve the last saved state snapshot
  static retrieveSnapshot(): DynamicStateSnapshot | null {
    try {
      const snapshot = localStorage.getItem(this.STORAGE_KEY);
      if (!snapshot) return null;

      const parsedSnapshot: DynamicStateSnapshot = JSON.parse(snapshot);
      
      // Validate snapshot integrity
      return this.validateSnapshot(parsedSnapshot) ? parsedSnapshot : null;
    } catch (error) {
      this.log(`Failed to retrieve state snapshot: ${error}`, 'error');
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
