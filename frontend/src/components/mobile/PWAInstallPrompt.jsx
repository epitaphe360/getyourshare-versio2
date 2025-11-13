import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone } from 'lucide-react';

/**
 * PWA Install Prompt Component
 * Shows install banner for supported devices
 * Handles beforeinstallprompt event
 */
const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check if dismissed before
    const dismissed = localStorage.getItem('pwa_install_dismissed');
    if (dismissed) {
      const dismissedDate = new Date(dismissed);
      const daysSinceDismissed = (new Date() - dismissedDate) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < 7) {
        return; // Don't show for 7 days after dismissal
      }
    }

    // Detect iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(iOS);

    if (iOS) {
      // Show iOS install instructions after 3 seconds
      setTimeout(() => {
        setShowPrompt(true);
      }, 3000);
    } else {
      // Handle Android/Desktop PWA install
      const handleBeforeInstallPrompt = (e) => {
        e.preventDefault();
        setDeferredPrompt(e);
        setShowPrompt(true);
      };

      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

      return () => {
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      };
    }
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {

      setIsInstalled(true);
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa_install_dismissed', new Date().toISOString());
  };

  if (isInstalled || !showPrompt) return null;

  if (isIOS) {
    return (
      <div className="fixed bottom-20 left-4 right-4 z-50 animate-slide-up">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-2xl p-5">
          <button
            onClick={handleDismiss}
            className="absolute top-3 right-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-1"
          >
            <X className="h-5 w-5" />
          </button>

          <div className="flex items-start gap-4">
            <div className="bg-white bg-opacity-20 p-3 rounded-xl">
              <Smartphone className="h-8 w-8" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-lg mb-2">Installez GetYourShare</h3>
              <p className="text-sm text-blue-100 mb-4">
                Ajoutez l'app à votre écran d'accueil pour un accès rapide et hors ligne
              </p>

              <div className="bg-white bg-opacity-10 rounded-xl p-3 text-sm space-y-2">
                <p className="font-medium">Pour installer:</p>
                <ol className="list-decimal list-inside space-y-1 text-blue-100">
                  <li>Appuyez sur <span className="inline-flex items-center mx-1">
                    <svg className="h-4 w-4 inline" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2L12 12M12 12L7 7M12 12L17 7M19 14v5a2 2 0 01-2 2H7a2 2 0 01-2-2v-5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </span> (partager) en bas</li>
                  <li>Sélectionnez "Sur l'écran d'accueil"</li>
                  <li>Appuyez sur "Ajouter"</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 animate-slide-up">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-2xl p-5">
        <button
          onClick={handleDismiss}
          className="absolute top-3 right-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full p-1"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-4">
          <div className="bg-white bg-opacity-20 p-3 rounded-xl">
            <Download className="h-8 w-8" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg mb-1">Installez GetYourShare</h3>
            <p className="text-sm text-blue-100 mb-3">
              Accès rapide, notifications push et mode hors ligne
            </p>
            <button
              onClick={handleInstallClick}
              className="bg-white text-blue-600 px-6 py-2 rounded-xl font-semibold hover:bg-blue-50 transition active:scale-95"
            >
              Installer maintenant
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;
