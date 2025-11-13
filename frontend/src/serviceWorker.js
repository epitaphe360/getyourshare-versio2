/**
 * Advanced Service Worker with Workbox
 * PWA Offline Support - Cache Strategies, Background Sync, Push Notifications
 * Version: 2.0.0
 */

/* eslint-disable no-restricted-globals */

// Configuration
const CACHE_VERSION = 'v2.0.0';
const CACHE_PREFIX = 'shareyoursales';
const CACHE_NAMES = {
  static: `${CACHE_PREFIX}-static-${CACHE_VERSION}`,
  dynamic: `${CACHE_PREFIX}-dynamic-${CACHE_VERSION}`,
  images: `${CACHE_PREFIX}-images-${CACHE_VERSION}`,
  api: `${CACHE_PREFIX}-api-${CACHE_VERSION}`,
  fonts: `${CACHE_PREFIX}-fonts-${CACHE_VERSION}`,
};

// Cache size limits (MB)
const CACHE_SIZE_LIMITS = {
  static: 50,
  dynamic: 30,
  images: 100,
  api: 20,
  fonts: 10,
};

// Assets to precache (critical resources)
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/static/css/main.css',
  '/static/js/main.js',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\/products/,
  /\/api\/dashboard/,
  /\/api\/user/,
  /\/api\/statistics/,
];

// Background sync queue
const SYNC_QUEUE_NAME = 'api-sync-queue';
let syncQueue = [];

/**
 * INSTALL EVENT
 * Precache critical assets
 */
self.addEventListener('install', (event) => {

  event.waitUntil(
    (async () => {
      try {
        // Precache critical assets
        const cache = await caches.open(CACHE_NAMES.static);
        await cache.addAll(PRECACHE_ASSETS);

        // Skip waiting to activate immediately
        await self.skipWaiting();

      } catch (error) {
        console.error('[SW] Installation failed:', error);
      }
    })()
  );
});

/**
 * ACTIVATE EVENT
 * Clean up old caches
 */
self.addEventListener('activate', (event) => {

  event.waitUntil(
    (async () => {
      try {
        // Clean up old caches
        const cacheNames = await caches.keys();
        const validCacheNames = Object.values(CACHE_NAMES);

        await Promise.all(
          cacheNames.map((cacheName) => {
            if (!validCacheNames.includes(cacheName)) {

              return caches.delete(cacheName);
            }
          })
        );

        // Claim all clients immediately
        await self.clients.claim();

        // Notify all clients about the new version
        await notifyClients({ type: 'SW_UPDATED', version: CACHE_VERSION });
      } catch (error) {
        console.error('[SW] Activation failed:', error);
      }
    })()
  );
});

/**
 * FETCH EVENT
 * Handle network requests with cache strategies
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Choose caching strategy based on request type
  if (url.pathname.startsWith('/api/')) {
    // API requests: Network First with cache fallback
    event.respondWith(networkFirstStrategy(request));
  } else if (request.destination === 'image') {
    // Images: Cache First with network fallback
    event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.images));
  } else if (request.destination === 'font') {
    // Fonts: Cache First (fonts rarely change)
    event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.fonts));
  } else if (url.pathname.match(/\.(js|css)$/)) {
    // Static assets: Stale While Revalidate
    event.respondWith(staleWhileRevalidateStrategy(request, CACHE_NAMES.static));
  } else {
    // HTML pages: Network First with offline fallback
    event.respondWith(networkFirstWithFallback(request));
  }
});

/**
 * CACHE STRATEGIES
 */

// Cache First Strategy
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);

    // Cache successful responses only
    if (networkResponse && networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache First failed:', error);
    return createErrorResponse('Resource unavailable offline');
  }
}

// Network First Strategy
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request, { timeout: 5000 });

    // Cache successful API responses
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAMES.api);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Fallback to cache
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {

      return cachedResponse;
    }

    // Return offline response
    return createOfflineApiResponse();
  }
}

// Network First with Offline Fallback (for HTML)
async function networkFirstWithFallback(request) {
  try {
    const networkResponse = await fetch(request);

    // Cache the response
    const cache = await caches.open(CACHE_NAMES.dynamic);
    cache.put(request, networkResponse.clone());

    return networkResponse;
  } catch (error) {
    // Try cache
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Fallback to offline page
    return caches.match('/offline.html');
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidateStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse && networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  });

  return cachedResponse || fetchPromise;
}

/**
 * BACKGROUND SYNC
 * Queue failed requests and retry when online
 */
self.addEventListener('sync', (event) => {

  if (event.tag === SYNC_QUEUE_NAME) {
    event.waitUntil(processSyncQueue());
  }
});

async function processSyncQueue() {
  try {
    // Get queued requests from IndexedDB
    const queuedRequests = await getSyncQueue();

    for (const queuedRequest of queuedRequests) {
      try {
        const response = await fetch(queuedRequest.url, queuedRequest.options);

        if (response.ok) {
          // Remove from queue on success
          await removeFromSyncQueue(queuedRequest.id);

          // Notify client
          await notifyClients({
            type: 'SYNC_SUCCESS',
            data: { id: queuedRequest.id, url: queuedRequest.url },
          });
        }
      } catch (error) {
        console.error('[SW] Sync failed for:', queuedRequest.url, error);
      }
    }
  } catch (error) {
    console.error('[SW] Background sync processing failed:', error);
  }
}

/**
 * PUSH NOTIFICATIONS
 */
self.addEventListener('push', (event) => {

  const data = event.data ? event.data.json() : {};
  const title = data.title || 'ShareYourSales';
  const options = {
    body: data.body || 'Nouvelle notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    image: data.image,
    vibrate: [200, 100, 200],
    tag: data.tag || 'default',
    requireInteraction: data.requireInteraction || false,
    data: {
      url: data.url || '/',
      timestamp: Date.now(),
    },
    actions: [
      {
        action: 'open',
        title: 'Ouvrir',
      },
      {
        action: 'close',
        title: 'Fermer',
      },
    ],
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open' || !event.action) {
    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
        // Check if there's already a window open
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }

        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
    );
  }
});

/**
 * PERIODIC BACKGROUND SYNC
 */
self.addEventListener('periodicsync', (event) => {

  if (event.tag === 'update-content') {
    event.waitUntil(updateContent());
  }
});

async function updateContent() {
  try {
    // Fetch fresh data
    const response = await fetch('/api/dashboard/stats');

    if (response.ok) {
      const data = await response.json();

      // Update cache
      const cache = await caches.open(CACHE_NAMES.api);
      cache.put('/api/dashboard/stats', new Response(JSON.stringify(data)));

      // Notify clients
      await notifyClients({ type: 'CONTENT_UPDATED', data });
    }
  } catch (error) {
    console.error('[SW] Periodic sync failed:', error);
  }
}

/**
 * MESSAGE HANDLER
 * Communication between SW and clients
 */
self.addEventListener('message', (event) => {

  const { type, data } = event.data;

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CACHE_URLS':
      event.waitUntil(cacheUrls(data.urls));
      break;

    case 'CLEAR_CACHE':
      event.waitUntil(clearAllCaches());
      break;

    case 'GET_CACHE_SIZE':
      event.waitUntil(
        getCacheSize().then((size) => {
          event.ports[0].postMessage({ type: 'CACHE_SIZE', size });
        })
      );
      break;

    case 'QUEUE_REQUEST':
      event.waitUntil(addToSyncQueue(data));
      break;

    default:
      console.warn('[SW] Unknown message type:', type);
  }
});

/**
 * HELPER FUNCTIONS
 */

// Notify all clients
async function notifyClients(message) {
  const clients = await self.clients.matchAll({ includeUncontrolled: true });
  clients.forEach((client) => client.postMessage(message));
}

// Create error response
function createErrorResponse(message) {
  return new Response(JSON.stringify({ error: message }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' },
  });
}

// Create offline API response
function createOfflineApiResponse() {
  return new Response(
    JSON.stringify({
      offline: true,
      message: 'You are offline. Showing cached data.',
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

// Cache URLs programmatically
async function cacheUrls(urls) {
  const cache = await caches.open(CACHE_NAMES.dynamic);
  await cache.addAll(urls);

}

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map((name) => caches.delete(name)));

}

// Get total cache size
async function getCacheSize() {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    const estimate = await navigator.storage.estimate();
    return {
      usage: estimate.usage,
      quota: estimate.quota,
      percentage: ((estimate.usage / estimate.quota) * 100).toFixed(2),
    };
  }
  return null;
}

// IndexedDB operations for sync queue
async function getSyncQueue() {
  return syncQueue;
}

async function addToSyncQueue(request) {
  const queueItem = {
    id: Date.now() + Math.random(),
    url: request.url,
    options: request.options,
    timestamp: Date.now(),
  };

  syncQueue.push(queueItem);

  // Register for background sync
  if ('sync' in self.registration) {
    await self.registration.sync.register(SYNC_QUEUE_NAME);
  }

  return queueItem.id;
}

async function removeFromSyncQueue(id) {
  syncQueue = syncQueue.filter((item) => item.id !== id);

}
