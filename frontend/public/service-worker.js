/* eslint-disable no-restricted-globals */

/**
 * Service Worker pour GetYourShare PWA
 * Features: Offline mode, Background Sync (Leads, Activities, Swipes), Push Notifications
 * Support: Marchands, Influenceurs, Commerciaux
 */

const CACHE_NAME = 'getyourshare-v3.0.0';
const API_CACHE = 'getyourshare-api-v3';
const RUNTIME_CACHE = 'getyourshare-runtime-v3';

// Endpoints API à mettre en cache pour lecture hors-ligne (stale-while-revalidate)
const CACHEABLE_API_PATTERNS = [
  /\/api\/influencer\/stats/,
  /\/api\/merchant\/stats/,
  /\/api\/admin\/stats/,
  /\/api\/marketplace\/products/,
  /\/api\/influencer\/tracking-links/,
  /\/api\/merchant\/products/,
  /\/api\/notifications/,
  /\/api\/influencer\/analytics/,
  /\/api\/merchant\/analytics/,
  /\/api\/influencer\/conversions/,
  /\/api\/merchant\/conversions/,
];
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/offline.html'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installation en cours...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Mise en cache des fichiers');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Installé avec succès');
        return self.skipWaiting();
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activation...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      const validCaches = [CACHE_NAME, API_CACHE, RUNTIME_CACHE];
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!validCaches.includes(cacheName)) {
            console.log('[Service Worker] Suppression ancien cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Activé');
      return self.clients.claim();
    })
  );
});

// Stratégie de cache: Network First, falling back to Cache
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Ignorer les requêtes non-GET
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);

  // ── API : Stale-While-Revalidate pour les endpoints cachéables ────────────
  if (request.url.includes('/api/')) {
    const isCacheable = CACHEABLE_API_PATTERNS.some((p) => p.test(url.pathname));

    if (isCacheable) {
      event.respondWith(
        caches.open(API_CACHE).then((cache) =>
          cache.match(request).then((cached) => {
            const fetchPromise = fetch(request)
              .then((networkRes) => {
                if (networkRes.ok) {
                  cache.put(request, networkRes.clone());
                }
                return networkRes;
              })
              .catch(() => cached); // réseau mort → retourner le cache
            // Retourner immédiatement le cache si disponible, puis mettre à jour en fond
            return cached || fetchPromise;
          })
        )
      );
      return;
    }

    // API non-cachéable : toujours réseau
    return;
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        // Clone la réponse car elle ne peut être consommée qu'une fois
        const responseToCache = response.clone();

        caches.open(CACHE_NAME)
          .then((cache) => {
            cache.put(request, responseToCache);
          });

        return response;
      })
      .catch(() => {
        // Si le réseau échoue, essayer le cache
        return caches.match(request)
          .then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }

            // Si pas dans le cache, retourner la page offline
            if (request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Background Sync pour les requêtes en attente
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background Sync:', event.tag);

  // Sales Rep: Sync leads & activities
  if (event.tag === 'sync-leads') {
    event.waitUntil(syncPendingLeads());
  } else if (event.tag === 'sync-activities') {
    event.waitUntil(syncPendingActivities());
  } else if (event.tag === 'sync-swipes') {
    event.waitUntil(syncPendingSwipes());
  } else if (event.tag === 'sync-payouts') {
    event.waitUntil(syncPendingPayouts());
  }
});

// Push Notifications
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push reçu:', event);

  let notificationData = {};

  try {
    notificationData = event.data.json();
  } catch (e) {
    notificationData = {
      title: 'ShareYourSales',
      body: event.data.text(),
      icon: '/icons/icon-192x192.png'
    };
  }

  const options = {
    body: notificationData.body,
    icon: notificationData.icon || '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: notificationData.tag || 'default',
    data: notificationData.data || {},
    actions: notificationData.actions || [
      {
        action: 'open',
        title: 'Ouvrir',
        icon: '/icons/icon-72x72.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Gestion des clics sur les notifications
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification cliquée:', event.action);

  event.notification.close();

  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then((windowClients) => {
      // Vérifier si une fenêtre est déjà ouverte
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }

      // Sinon, ouvrir une nouvelle fenêtre
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Message Handler (communication avec l'app)
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message reçu:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then((cache) => cache.addAll(event.data.payload))
    );
  }
});

// Helper: Sync pending payouts
async function syncPendingPayouts() {
  try {
    // Récupérer les payouts en attente depuis IndexedDB
    const pendingPayouts = await getPendingPayouts();

    if (pendingPayouts.length > 0) {
      console.log('[Service Worker] Syncing', pendingPayouts.length, 'payouts');

      for (const payout of pendingPayouts) {
        await fetch('/api/mobile-payments/request-payout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${payout.token}`
          },
          body: JSON.stringify(payout.data)
        });

        // Supprimer de IndexedDB après succès
        await removePendingPayout(payout.id);
      }

      console.log('[Service Worker] Sync terminé');
    }
  } catch (error) {
    console.error('[Service Worker] Sync error:', error);
  }
}

// Helper: Sync pending leads (Sales Reps)
async function syncPendingLeads() {
  try {
    const db = await openIndexedDB();
    const pendingLeads = await getAll(db, 'pendingLeads');

    console.log(`[Service Worker] Syncing ${pendingLeads.length} leads`);

    for (const item of pendingLeads) {
      const response = await fetch('/api/sales/leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${item.token}`
        },
        body: JSON.stringify(item.data)
      });

      if (response.ok) {
        await deleteFromStore(db, 'pendingLeads', item.id);
      }
    }

    console.log('[Service Worker] Leads synced successfully');
  } catch (error) {
    console.error('[Service Worker] Lead sync failed:', error);
    throw error;
  }
}

// Helper: Sync pending activities (Sales Reps)
async function syncPendingActivities() {
  try {
    const db = await openIndexedDB();
    const pendingActivities = await getAll(db, 'pendingActivities');

    console.log(`[Service Worker] Syncing ${pendingActivities.length} activities`);

    for (const item of pendingActivities) {
      const response = await fetch('/api/sales/activities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${item.token}`
        },
        body: JSON.stringify(item.data)
      });

      if (response.ok) {
        await deleteFromStore(db, 'pendingActivities', item.id);
      }
    }

    console.log('[Service Worker] Activities synced successfully');
  } catch (error) {
    console.error('[Service Worker] Activity sync failed:', error);
    throw error;
  }
}

// Helper: Sync pending swipes (Influencer Matching)
async function syncPendingSwipes() {
  try {
    const db = await openIndexedDB();
    const pendingSwipes = await getAll(db, 'pendingSwipes');

    console.log(`[Service Worker] Syncing ${pendingSwipes.length} swipes`);

    for (const item of pendingSwipes) {
      const endpoint = item.data.direction === 'right'
        ? '/api/matching/swipe-right'
        : '/api/matching/swipe-left';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${item.token}`
        },
        body: JSON.stringify(item.data)
      });

      if (response.ok) {
        await deleteFromStore(db, 'pendingSwipes', item.id);
      }
    }

    console.log('[Service Worker] Swipes synced successfully');
  } catch (error) {
    console.error('[Service Worker] Swipe sync failed:', error);
    throw error;
  }
}

// Helper: Get pending payouts from IndexedDB
async function getPendingPayouts() {
  try {
    const db = await openIndexedDB();
    return await getAll(db, 'pendingPayouts');
  } catch (error) {
    console.error('[Service Worker] Error getting payouts:', error);
    return [];
  }
}

// Helper: Remove payout from IndexedDB
async function removePendingPayout(id) {
  try {
    const db = await openIndexedDB();
    await deleteFromStore(db, 'pendingPayouts', id);
  } catch (error) {
    console.error('[Service Worker] Error removing payout:', error);
  }
}

// IndexedDB Helpers
function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('GetYourShareDB', 2);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object stores if they don't exist
      if (!db.objectStoreNames.contains('pendingLeads')) {
        db.createObjectStore('pendingLeads', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('pendingActivities')) {
        db.createObjectStore('pendingActivities', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('pendingSwipes')) {
        db.createObjectStore('pendingSwipes', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('pendingPayouts')) {
        db.createObjectStore('pendingPayouts', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

function getAll(db, storeName) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function deleteFromStore(db, storeName, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);

    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

// Periodic Background Sync (si supporté)
self.addEventListener('periodicsync', (event) => {
  console.log('[Service Worker] Periodic Sync:', event.tag);

  if (event.tag === 'update-content') {
    event.waitUntil(updateCachedContent());
  }
});

async function updateCachedContent() {
  console.log('[Service Worker] Mise à jour du cache...');

  try {
    const cache = await caches.open(CACHE_NAME);

    // Mettre à jour les fichiers critiques
    await cache.addAll(urlsToCache);

    console.log('[Service Worker] Cache mis à jour');
  } catch (error) {
    console.error('[Service Worker] Erreur mise à jour cache:', error);
  }
}

console.log('[Service Worker] Loaded');
