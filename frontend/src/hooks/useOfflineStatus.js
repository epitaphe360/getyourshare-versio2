/**
 * useOfflineStatus Hook
 * Gère l'état online/offline, la queue de requêtes et la synchronisation
 */

import { useState, useEffect, useCallback, useRef } from 'react';

const useOfflineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);
  const [queuedRequests, setQueuedRequests] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastOnlineTime, setLastOnlineTime] = useState(Date.now());
  const [connectionType, setConnectionType] = useState('unknown');
  const toastShownRef = useRef(false);

  /**
   * Détection du type de connexion
   */
  const updateConnectionType = useCallback(() => {
    if ('connection' in navigator) {
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if (conn) {
        setConnectionType(conn.effectiveType || 'unknown');
      }
    }
  }, []);

  /**
   * Gérer le passage online
   */
  const handleOnline = useCallback(async () => {

    setIsOnline(true);
    setWasOffline(true);
    setLastOnlineTime(Date.now());
    updateConnectionType();

    // Afficher notification
    if (!toastShownRef.current) {
      showToast('Connexion rétablie', 'success');
      toastShownRef.current = true;
    }

    // Synchroniser les requêtes en attente
    await syncQueuedRequests();

    // Reset flag après 5 secondes
    setTimeout(() => {
      setWasOffline(false);
      toastShownRef.current = false;
    }, 5000);
  }, [updateConnectionType]);

  /**
   * Gérer le passage offline
   */
  const handleOffline = useCallback(() => {

    setIsOnline(false);
    setConnectionType('offline');

    // Afficher notification
    showToast('Mode hors ligne activé', 'warning');

    // Sauvegarder le temps de déconnexion
    localStorage.setItem('lastOfflineTime', Date.now().toString());
  }, []);

  /**
   * Ajouter une requête à la queue
   */
  const queueRequest = useCallback(async (url, options = {}) => {
    const requestData = {
      id: Date.now() + Math.random(),
      url,
      options,
      timestamp: Date.now(),
      status: 'pending',
    };

    setQueuedRequests((prev) => [...prev, requestData]);

    // Sauvegarder dans IndexedDB pour persistance
    try {
      const db = await openRequestDB();
      await addRequestToDB(db, requestData);

      // Notifier le Service Worker
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'QUEUE_REQUEST',
          data: requestData,
        });
      }

      showToast('Requête mise en file d\'attente', 'info');
    } catch (error) {
      console.error('❌ Erreur ajout à la queue:', error);
    }

    return requestData.id;
  }, []);

  /**
   * Synchroniser toutes les requêtes en attente
   */
  const syncQueuedRequests = useCallback(async () => {
    if (queuedRequests.length === 0) {
      return;
    }

    setIsSyncing(true);

    let successCount = 0;
    let failCount = 0;

    for (const request of queuedRequests) {
      try {
        const response = await fetch(request.url, request.options);

        if (response.ok) {
          // Marquer comme réussie
          await removeRequestFromDB(request.id);
          setQueuedRequests((prev) => prev.filter((r) => r.id !== request.id));
          successCount++;
        } else {
          failCount++;
        }
      } catch (error) {
        console.error('❌ Erreur sync requête:', request.url, error);
        failCount++;
      }
    }

    setIsSyncing(false);

    // Notification de résultat
    if (successCount > 0) {
      showToast(`${successCount} requête(s) synchronisée(s)`, 'success');
    }

    if (failCount > 0) {
      showToast(`${failCount} requête(s) ont échoué`, 'error');
    }

  }, [queuedRequests]);

  /**
   * Vider la queue manuellement
   */
  const clearQueue = useCallback(async () => {
    setQueuedRequests([]);
    try {
      const db = await openRequestDB();
      await clearRequestDB(db);
      showToast('File d\'attente vidée', 'info');
    } catch (error) {
      console.error('❌ Erreur vidage queue:', error);
    }
  }, []);

  /**
   * Réessayer une requête spécifique
   */
  const retryRequest = useCallback(async (requestId) => {
    const request = queuedRequests.find((r) => r.id === requestId);

    if (!request) {
      return;
    }

    try {
      const response = await fetch(request.url, request.options);

      if (response.ok) {
        await removeRequestFromDB(request.id);
        setQueuedRequests((prev) => prev.filter((r) => r.id !== requestId));
        showToast('Requête synchronisée', 'success');
        return true;
      }
    } catch (error) {
      console.error('❌ Erreur retry:', error);
      showToast('Échec de la synchronisation', 'error');
    }

    return false;
  }, [queuedRequests]);

  /**
   * Charger les requêtes depuis IndexedDB au montage
   */
  useEffect(() => {
    const loadQueuedRequests = async () => {
      try {
        const db = await openRequestDB();
        const requests = await getRequestsFromDB(db);
        setQueuedRequests(requests);

      } catch (error) {
        console.error('❌ Erreur chargement requêtes:', error);
      }
    };

    loadQueuedRequests();
  }, []);

  /**
   * Écouter les événements online/offline
   */
  useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Écouter les changements de connexion
    if ('connection' in navigator) {
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if (conn) {
        conn.addEventListener('change', updateConnectionType);
      }
    }

    // Vérifier l'état initial
    updateConnectionType();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);

      if ('connection' in navigator) {
        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (conn) {
          conn.removeEventListener('change', updateConnectionType);
        }
      }
    };
  }, [handleOnline, handleOffline, updateConnectionType]);

  /**
   * Auto-sync quand revient online
   */
  useEffect(() => {
    if (isOnline && wasOffline && queuedRequests.length > 0) {
      syncQueuedRequests();
    }
  }, [isOnline, wasOffline, queuedRequests.length, syncQueuedRequests]);

  return {
    isOnline,
    isOffline: !isOnline,
    wasOffline,
    connectionType,
    queuedRequests,
    queuedCount: queuedRequests.length,
    isSyncing,
    lastOnlineTime,
    queueRequest,
    syncQueuedRequests,
    clearQueue,
    retryRequest,
  };
};

/**
 * HELPER FUNCTIONS - IndexedDB
 */

const DB_NAME = 'offline-requests';
const DB_VERSION = 1;
const STORE_NAME = 'requests';

function openRequestDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
  });
}

function addRequestToDB(db, request) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const req = store.add(request);

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function getRequestsFromDB(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const req = store.getAll();

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

function removeRequestFromDB(id) {
  return openRequestDB().then((db) => {
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const req = store.delete(id);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  });
}

function clearRequestDB(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const req = store.clear();

    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

/**
 * Toast notifications helper
 */
function showToast(message, type = 'info') {
  // Dispatch custom event pour afficher le toast
  window.dispatchEvent(
    new CustomEvent('show-toast', {
      detail: { message, type },
    })
  );
}

export default useOfflineStatus;
