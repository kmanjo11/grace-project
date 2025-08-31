/* Minimal Service Worker for Grace UI
   - Prevents 404 on registration in production
   - Provides basic BACKUP_STATE and RECOVER_STATE message handlers
   - Not a full offline/PWA implementation
*/

// In-memory backup store (ephemeral; resets when SW restarts)
let backupState = null;

self.addEventListener('install', (event) => {
  // Activate immediately on install
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Take control of all pages
  event.waitUntil(self.clients.claim());
});

self.addEventListener('message', async (event) => {
  try {
    const data = event.data || {};
    if (data.type === 'BACKUP_STATE') {
      backupState = data.state || null;
      // Acknowledge completion
      const client = await self.clients.get(event.source.id);
      if (client) {
        client.postMessage({ type: 'BACKUP_STATE_COMPLETE', success: true });
      }
    } else if (data.type === 'RECOVER_STATE') {
      // Respond with whatever we have in memory
      const client = await self.clients.get(event.source.id);
      if (client) {
        client.postMessage({ type: 'RECOVERY_RESULT', state: backupState });
      }
    }
  } catch (err) {
    // Best-effort error handling
    try {
      const client = await self.clients.get(event.source?.id);
      if (client) {
        client.postMessage({ type: 'BACKUP_STATE_COMPLETE', success: false, error: String(err) });
      }
    } catch (_) {}
  }
});
