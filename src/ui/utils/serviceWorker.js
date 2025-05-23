// Service Worker for state persistence
const CACHE_NAME = 'grace-app-state-cache-v1';
const STATE_URL = '/api/state-backup';

// Install event - create cache
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installed');
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activated');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing Old Cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Handle state backups
self.addEventListener('fetch', (event) => {
  // Only intercept our specific backup requests
  if (event.request.url.includes(STATE_URL)) {
    console.log('Service Worker: Backing up state');
    
    // Clone the request to use it more than once
    const fetchRequest = event.request.clone();
    
    // Try to fetch from network first
    event.respondWith(
      fetch(fetchRequest)
        .then(response => {
          // Clone the response to use it more than once
          const responseToCache = response.clone();
          
          // Open cache and store response for future offline access
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
              console.log('Service Worker: State backed up to cache');
            });
          
          return response;
        })
        .catch(() => {
          // If network fetch fails, try to return from cache
          console.log('Service Worker: Network unavailable, using cached state');
          return caches.match(event.request);
        })
    );
  }
});

// Listen for messages from the main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'BACKUP_STATE') {
    console.log('Service Worker: Received state backup request');
    
    // Store the state in IndexedDB for persistence
    storeStateInIndexedDB(event.data.state)
      .then(() => {
        // Notify the client that backup was successful
        event.source.postMessage({
          type: 'BACKUP_STATE_COMPLETE',
          success: true
        });
      })
      .catch(error => {
        console.error('Service Worker: Error backing up state', error);
        event.source.postMessage({
          type: 'BACKUP_STATE_COMPLETE',
          success: false,
          error: error.message
        });
      });
  }
});

// Helper function to store state in IndexedDB
function storeStateInIndexedDB(state) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('GraceStateDB', 1);
    
    request.onerror = event => {
      reject(new Error('Failed to open IndexedDB'));
    };
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('states')) {
        db.createObjectStore('states', { keyPath: 'id' });
      }
    };
    
    request.onsuccess = event => {
      const db = event.target.result;
      const transaction = db.transaction(['states'], 'readwrite');
      const store = transaction.objectStore('states');
      
      // Add timestamp and version
      const stateToStore = {
        id: 'currentState',
        timestamp: Date.now(),
        data: state
      };
      
      const storeRequest = store.put(stateToStore);
      
      storeRequest.onerror = event => {
        reject(new Error('Failed to store state in IndexedDB'));
      };
      
      storeRequest.onsuccess = event => {
        resolve();
      };
    };
  });
}

// Helper function to retrieve state from IndexedDB
function retrieveStateFromIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('GraceStateDB', 1);
    
    request.onerror = event => {
      reject(new Error('Failed to open IndexedDB'));
    };
    
    request.onsuccess = event => {
      const db = event.target.result;
      const transaction = db.transaction(['states'], 'readonly');
      const store = transaction.objectStore('states');
      
      const getRequest = store.get('currentState');
      
      getRequest.onerror = event => {
        reject(new Error('Failed to retrieve state from IndexedDB'));
      };
      
      getRequest.onsuccess = event => {
        if (getRequest.result) {
          resolve(getRequest.result.data);
        } else {
          resolve(null);
        }
      };
    };
  });
}
