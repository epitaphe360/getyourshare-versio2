import React, { useState, useEffect } from 'react';
import Button from './Button';
import { Shield, X } from 'lucide-react';

const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Vérifier si l'utilisateur a déjà fait un choix
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    setIsVisible(false);
    // Ici, on pourrait activer les scripts de tracking (Google Analytics, etc.)
    window.dispatchEvent(new Event('cookie_consent_accepted'));
  };

  const handleDecline = () => {
    localStorage.setItem('cookie_consent', 'declined');
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 p-4 md:p-6 animate-slide-up">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-start space-x-4">
          <div className="bg-indigo-100 p-2 rounded-full hidden md:block">
            <Shield className="text-indigo-600" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Nous respectons votre vie privée
            </h3>
            <p className="text-sm text-gray-600 max-w-2xl">
              Nous utilisons des cookies pour améliorer votre expérience, analyser le trafic et personnaliser le contenu. 
              En cliquant sur "Accepter", vous consentez à notre utilisation des cookies conformément à notre{' '}
              <a href="/privacy" className="text-indigo-600 hover:underline">Politique de Confidentialité</a>.
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <Button 
            variant="outline" 
            onClick={handleDecline}
            className="flex-1 md:flex-none justify-center"
          >
            Refuser
          </Button>
          <Button 
            onClick={handleAccept}
            className="flex-1 md:flex-none justify-center"
          >
            Accepter
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
