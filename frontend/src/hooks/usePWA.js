/**
 * usePWA - Hook React pour gérer les fonctionnalités PWA
 * - Détection online/offline
 * - Invite d'installation (A2HS)
 * - Mise à jour du Service Worker
 * - Enregistrement du periodicSync
 */
import { useState, useEffect, useCallback } from 'react';

export default function usePWA() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [installPromptEvent, setInstallPromptEvent] = useState(null);
  const [isInstalled, setIsInstalled] = useState(
    window.matchMedia('(display-mode: standalone)').matches
  );
  const [swUpdateAvailable, setSwUpdateAvailable] = useState(false);
  const [swRegistration, setSwRegistration] = useState(null);

  useEffect(() => {
    // ── Online / Offline ──────────────────────────────────────────────────────
    const onOnline = () => setIsOnline(true);
    const onOffline = () => setIsOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);

    // ── Install prompt ────────────────────────────────────────────────────────
    const onBeforeInstall = (e) => {
      e.preventDefault();
      setInstallPromptEvent(e);
    };
    window.addEventListener('beforeinstallprompt', onBeforeInstall);
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setInstallPromptEvent(null);
    });

    // ── Service Worker registration + update detection ────────────────────────
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/service-worker.js', { scope: '/' })
        .then((reg) => {
          setSwRegistration(reg);

          // Détecter les mises à jour
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (!newWorker) return;
            newWorker.addEventListener('statechange', () => {
              if (
                newWorker.state === 'installed' &&
                navigator.serviceWorker.controller
              ) {
                setSwUpdateAvailable(true);
              }
            });
          });

          // Enregistrer le Periodic Background Sync (si supporté)
          if ('periodicSync' in reg) {
            navigator.permissions
              .query({ name: 'periodic-background-sync' })
              .then((status) => {
                if (status.state === 'granted') {
                  reg.periodicSync.register('update-content', {
                    minInterval: 24 * 60 * 60 * 1000, // 24h
                  });
                }
              })
              .catch(() => {});
          }
        })
        .catch((err) => {
          console.warn('[PWA] Échec enregistrement SW:', err);
        });

      // Recharger la page quand le nouveau SW prend le contrôle
      let refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });
    }

    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      window.removeEventListener('beforeinstallprompt', onBeforeInstall);
    };
  }, []);

  /**
   * Déclencher la boîte de dialogue d'installation A2HS
   * @returns {Promise<boolean>} true si l'utilisateur a accepté
   */
  const promptInstall = useCallback(async () => {
    if (!installPromptEvent) return false;
    await installPromptEvent.prompt();
    const { outcome } = await installPromptEvent.userChoice;
    setInstallPromptEvent(null);
    return outcome === 'accepted';
  }, [installPromptEvent]);

  /**
   * Appliquer la mise à jour du Service Worker
   */
  const applyUpdate = useCallback(() => {
    if (swRegistration && swRegistration.waiting) {
      swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
  }, [swRegistration]);

  /**
   * Mettre en file d'attente une action hors-ligne pour Background Sync
   * @param {string} tag - ex: 'sync-leads'
   */
  const requestBackgroundSync = useCallback(
    async (tag) => {
      if (!swRegistration || !('sync' in swRegistration)) return;
      try {
        await swRegistration.sync.register(tag);
      } catch (err) {
        console.warn('[PWA] Background sync non supporté:', err);
      }
    },
    [swRegistration]
  );

  return {
    isOnline,
    isOffline: !isOnline,
    isInstalled,
    canInstall: !!installPromptEvent && !isInstalled,
    promptInstall,
    swUpdateAvailable,
    applyUpdate,
    requestBackgroundSync,
  };
}
