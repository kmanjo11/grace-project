/**
 * StateOperationLock - Prevents race conditions in state operations
 * 
 * This utility provides a central locking mechanism to prevent concurrent state operations
 * from interfering with each other, which can cause race conditions and lost updates.
 */

interface LockInfo {
  id: string;
  operation: string;
  acquiredAt: number;
  expiresAt: number;
}

class StateOperationLock {
  private static instance: StateOperationLock;
  private activeLocks: Map<string, LockInfo> = new Map();
  private DEFAULT_TIMEOUT = 5000; // Default lock timeout: 5 seconds

  // Make this a singleton
  private constructor() {}

  public static getInstance(): StateOperationLock {
    if (!StateOperationLock.instance) {
      StateOperationLock.instance = new StateOperationLock();
    }
    return StateOperationLock.instance;
  }

  /**
   * Acquires a lock for a specific operation
   * @param resourceId Identifier for the resource being locked (e.g., 'chat', 'trading')
   * @param operation Description of the operation being performed
   * @param timeoutMs Lock timeout in milliseconds
   * @returns Lock ID if acquired, null if failed
   */
  public acquireLock(resourceId: string, operation: string, timeoutMs = this.DEFAULT_TIMEOUT): string | null {
    // Clean expired locks first
    this.cleanExpiredLocks();
    
    // Check if the resource is already locked
    if (this.activeLocks.has(resourceId)) {
      console.warn(`Resource ${resourceId} is already locked for operation: ${this.activeLocks.get(resourceId)?.operation}`);
      return null;
    }
    
    // Create a new lock
    const lockId = `lock_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const now = Date.now();
    
    const lockInfo: LockInfo = {
      id: lockId,
      operation,
      acquiredAt: now,
      expiresAt: now + timeoutMs
    };
    
    // Set the lock
    this.activeLocks.set(resourceId, lockInfo);
    console.log(`Lock acquired for ${resourceId}: ${operation}`);
    
    // Set automatic release after timeout
    setTimeout(() => {
      this.releaseLock(resourceId, lockId);
    }, timeoutMs);
    
    return lockId;
  }

  /**
   * Releases a lock if the lockId matches
   * @param resourceId Resource identifier
   * @param lockId Lock ID returned from acquireLock
   * @returns true if released, false if not found or ID doesn't match
   */
  public releaseLock(resourceId: string, lockId: string): boolean {
    const lock = this.activeLocks.get(resourceId);
    
    if (!lock) {
      console.warn(`No lock found for resource ${resourceId}`);
      return false;
    }
    
    if (lock.id !== lockId) {
      console.warn(`Lock ID mismatch for ${resourceId}: expected ${lock.id}, got ${lockId}`);
      return false;
    }
    
    // Release the lock
    this.activeLocks.delete(resourceId);
    console.log(`Lock released for ${resourceId}`);
    
    return true;
  }

  /**
   * Checks if a resource is currently locked
   * @param resourceId Resource identifier
   * @returns true if locked, false otherwise
   */
  public isLocked(resourceId: string): boolean {
    this.cleanExpiredLocks();
    return this.activeLocks.has(resourceId);
  }

  /**
   * Clean up any expired locks
   */
  private cleanExpiredLocks(): void {
    const now = Date.now();
    
    for (const [resourceId, lock] of this.activeLocks.entries()) {
      if (lock.expiresAt < now) {
        console.log(`Lock for ${resourceId} expired and was auto-released`);
        this.activeLocks.delete(resourceId);
      }
    }
  }
}

export default StateOperationLock.getInstance();
