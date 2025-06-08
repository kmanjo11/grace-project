// StateBackupService.ts - Manages additional state backup mechanisms
import StatePersistenceManager from './StatePersistence';

class StateBackupService {
  private static instance: StateBackupService;
  private serviceWorkerRegistration: ServiceWorkerRegistration | null = null;
  private backupInterval: number | null = null;
  private lastBackupTime: number = 0;
  private readonly BACKUP_INTERVAL_MS = 60000; // 1 minute
  private isRegistering = false;

  private constructor() {
    // Private constructor for singleton pattern
  }

  public static getInstance(): StateBackupService {
    if (!StateBackupService.instance) {
      StateBackupService.instance = new StateBackupService();
    }
    return StateBackupService.instance;
  }

  /**
   * Initialize the backup service
   */
  public async initialize(): Promise<boolean> {
    try {
      // Register service worker if supported
      if ('serviceWorker' in navigator && !this.isRegistering) {
        this.isRegistering = true;
        try {
          this.serviceWorkerRegistration = await navigator.serviceWorker.register('/serviceWorker.js', {
            scope: '/'
          });
          console.log('Service Worker registered successfully', this.serviceWorkerRegistration);
          
          // Set up service worker message handling
          navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage);
          
          // Start periodic backup
          this.startPeriodicBackup();
          this.isRegistering = false;
          return true;
        } catch (error) {
          console.error('Service Worker registration failed:', error);
          this.isRegistering = false;
          
          // Even if service worker fails, we can still use local storage backups
          this.startPeriodicBackup();
          return false;
        }
      } else {
        // Fallback for browsers without service worker support
        console.log('Service Workers not supported or already registering, using local storage only');
        this.startPeriodicBackup();
        return false;
      }
    } catch (error) {
      console.error('Error initializing backup service:', error);
      return false;
    }
  }

  /**
   * Handle messages from service worker
   */
  private handleServiceWorkerMessage = (event: MessageEvent) => {
    if (event.data && event.data.type === 'BACKUP_STATE_COMPLETE') {
      if (event.data.success) {
        console.log('Service Worker backup complete');
      } else {
        console.error('Service Worker backup failed:', event.data.error);
      }
    }
  };

  /**
   * Start periodic state backups
   */
  public startPeriodicBackup(): void {
    if (this.backupInterval) {
      clearInterval(this.backupInterval);
    }
    
    this.backupInterval = window.setInterval(() => {
      this.backupCurrentState();
    }, this.BACKUP_INTERVAL_MS);
    
    console.log('Periodic state backup started');
    
    // Also backup on certain events
    window.addEventListener('beforeunload', this.backupCurrentState);
    window.addEventListener('pagehide', this.backupCurrentState);
    
    // Backup now
    this.backupCurrentState();
  }

  /**
   * Stop periodic backups
   */
  public stopPeriodicBackup(): void {
    if (this.backupInterval) {
      clearInterval(this.backupInterval);
      this.backupInterval = null;
      
      window.removeEventListener('beforeunload', this.backupCurrentState);
      window.removeEventListener('pagehide', this.backupCurrentState);
      
      console.log('Periodic state backup stopped');
    }
  }

  /**
   * Backup the current application state
   */
  public backupCurrentState = async (): Promise<void> => {
    try {
      // Don't backup too frequently
      const now = Date.now();
      if (now - this.lastBackupTime < 10000) { // Min 10s between backups
        return;
      }
      
      this.lastBackupTime = now;
      
      // Get current state snapshot
      const snapshot = StatePersistenceManager.retrieveSnapshot();
      if (!snapshot) {
        console.log('No state snapshot to backup');
        return;
      }
      
      // Backup to service worker if available
      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'BACKUP_STATE',
          state: snapshot
        });
        console.log('State backup sent to Service Worker');
      }
      
      // Secondary browser storage backup using a different key
      try {
        localStorage.setItem('GRACE_STATE_BACKUP', JSON.stringify({
          timestamp: now,
          state: snapshot
        }));
      } catch (storageError) {
        console.error('Error backing up to localStorage:', storageError);
      }
    } catch (error) {
      console.error('State backup failed:', error);
    }
  };

  /**
   * Attempt to recover state from all backup sources
   */
  public async attemptRecovery(): Promise<any | null> {
    try {
      console.log('Attempting state recovery from all sources');
      
      // Try main persistence manager first
      const mainSnapshot = StatePersistenceManager.retrieveSnapshot();
      if (mainSnapshot) {
        console.log('Recovered state from main persistence manager');
        return mainSnapshot;
      }
      
      // Try localStorage backup
      try {
        const backupJson = localStorage.getItem('GRACE_STATE_BACKUP');
        if (backupJson) {
          const backup = JSON.parse(backupJson);
          if (backup && backup.state) {
            console.log('Recovered state from localStorage backup');
            return backup.state;
          }
        }
      } catch (e) {
        console.error('Error reading from localStorage backup:', e);
      }
      
      // Try service worker backup (this gets complex with async)
      if (navigator.serviceWorker.controller) {
        return new Promise((resolve) => {
          // Set up a one-time message handler
          const messageHandler = (event: MessageEvent) => {
            if (event.data && event.data.type === 'RECOVERY_RESULT') {
              navigator.serviceWorker.removeEventListener('message', messageHandler);
              if (event.data.state) {
                console.log('Recovered state from Service Worker');
                resolve(event.data.state);
              } else {
                console.log('No state found in Service Worker');
                resolve(null);
              }
            }
          };
          
          navigator.serviceWorker.addEventListener('message', messageHandler);
          
          // Request recovery - we've already checked controller is not null
          navigator.serviceWorker.controller!.postMessage({
            type: 'RECOVER_STATE'
          });
          
          // Set timeout for recovery attempt
          setTimeout(() => {
            navigator.serviceWorker.removeEventListener('message', messageHandler);
            console.log('Service Worker recovery timed out');
            resolve(null);
          }, 3000);
        });
      }
      
      console.log('No state recovered from any source');
      return null;
    } catch (error) {
      console.error('Error during state recovery:', error);
      return null;
    }
  }
}

export default StateBackupService;
