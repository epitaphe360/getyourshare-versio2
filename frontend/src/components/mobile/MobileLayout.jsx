import React, { useEffect, useState } from 'react';
import PWAInstallPrompt from './PWAInstallPrompt';
import { Wifi, WifiOff } from 'lucide-react';

/**
 * Mobile Layout Wrapper
 * - Responsive design
 * - Offline detection
 * - PWA install prompt
 * - Service worker registration
 */
const MobileLayout = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showOfflineBanner, setShowOfflineBanner] = useState(false);
  const [serviceWorkerReady, setServiceWorkerReady] = useState(false);

  useEffect(() => {
    // Register service worker
    registerServiceWorker();

    // Online/Offline detection
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineBanner(false);

    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineBanner(true);

    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial check
    if (!navigator.onLine) {
      setShowOfflineBanner(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const registerServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');

        setServiceWorkerReady(true);

        // Check for updates periodically
        setInterval(() => {
          registration.update();
        }, 60000); // Check every minute

        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker available
              if (confirm('Nouvelle version disponible! Recharger?')) {
                window.location.reload();
              }
            }
          });
        });
      } catch (error) {
        console.error('❌ Service Worker registration failed:', error);
      }
    }
  };

  return (
    <div className="mobile-layout min-h-screen bg-gray-50">
      {/* Offline Banner */}
      {showOfflineBanner && (
        <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-white px-4 py-2 z-50 flex items-center justify-center gap-2 text-sm font-medium animate-slide-down">
          <WifiOff className="h-4 w-4" />
          <span>Mode hors ligne - Les modifications seront synchronisées</span>
        </div>
      )}

      {/* Online Status Indicator (subtle) */}
      {isOnline && !showOfflineBanner && serviceWorkerReady && (
        <div className="fixed top-4 right-4 z-40">
          <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 shadow-lg opacity-0 animate-fade-in">
            <Wifi className="h-3 w-3" />
            En ligne
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className={showOfflineBanner ? 'pt-10' : ''}>
        {children}
      </div>

      {/* PWA Install Prompt */}
      <PWAInstallPrompt />

      {/* Add custom CSS for animations */}
      <style jsx>{`
        @keyframes slide-down {
          from {
            transform: translateY(-100%);
          }
          to {
            transform: translateY(0);
          }
        }

        @keyframes slide-up {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-slide-down {
          animation: slide-down 0.3s ease-out;
        }

        .animate-slide-up {
          animation: slide-up 0.4s ease-out;
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-in forwards;
          animation-delay: 1s;
        }

        /* Safe area insets for iOS */
        .h-safe-area-inset-bottom {
          height: env(safe-area-inset-bottom);
        }

        /* Prevent pull-to-refresh on mobile */
        body {
          overscroll-behavior-y: contain;
        }

        /* Custom scrollbar for mobile webkit */
        ::-webkit-scrollbar {
          width: 4px;
          height: 4px;
        }

        ::-webkit-scrollbar-track {
          background: transparent;
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 2px;
        }

        /* Touch-friendly tap highlights */
        * {
          -webkit-tap-highlight-color: transparent;
        }

        button:active,
        a:active {
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
};

export default MobileLayout;
