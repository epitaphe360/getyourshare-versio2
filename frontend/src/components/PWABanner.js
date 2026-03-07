/**
 * PWABanner — Composant de notification PWA
 * Affiche :
 * - Bannière "Installer l'app" (A2HS)
 * - Bannière "Mise à jour disponible"
 * - Indicateur mode hors-ligne
 */
import React from 'react';
import usePWA from '../hooks/usePWA';

const PWABanner = () => {
  const {isOffline, canInstall, promptInstall, swUpdateAvailable, applyUpdate} = usePWA();

  return (
    <>
      {/* Bannière hors-ligne */}
      {isOffline && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            backgroundColor: '#1e293b',
            color: '#f1f5f9',
            textAlign: 'center',
            padding: '8px 16px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
          }}>
          <span>📵</span>
          <span>Vous êtes hors-ligne — certaines données peuvent être obsolètes.</span>
        </div>
      )}

      {/* Bannière mise à jour */}
      {swUpdateAvailable && (
        <div
          style={{
            position: 'fixed',
            bottom: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9998,
            backgroundColor: '#1d4ed8',
            color: '#fff',
            borderRadius: '12px',
            padding: '12px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.25)',
            maxWidth: '420px',
            width: '90%',
          }}>
          <span style={{fontSize: '18px'}}>🔄</span>
          <span style={{flex: 1, fontSize: '14px'}}>Nouvelle version disponible !</span>
          <button
            onClick={applyUpdate}
            style={{
              background: '#fff',
              color: '#1d4ed8',
              border: 'none',
              borderRadius: '8px',
              padding: '6px 14px',
              fontWeight: 700,
              cursor: 'pointer',
              fontSize: '13px',
            }}>
            Mettre à jour
          </button>
        </div>
      )}

      {/* Bannière installation A2HS */}
      {canInstall && !swUpdateAvailable && (
        <div
          style={{
            position: 'fixed',
            bottom: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 9997,
            backgroundColor: '#fff',
            border: '1px solid #e2e8f0',
            borderRadius: '14px',
            padding: '14px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
            maxWidth: '420px',
            width: '90%',
          }}>
          <img src="/icons/icon-72x72.png" alt="logo" style={{width: 40, height: 40, borderRadius: 10}} />
          <div style={{flex: 1}}>
            <p style={{margin: 0, fontWeight: 700, fontSize: '14px', color: '#1e293b'}}>
              Installer ShareYourSales
            </p>
            <p style={{margin: '2px 0 0', fontSize: '12px', color: '#64748b'}}>
              Accès rapide depuis votre écran d'accueil
            </p>
          </div>
          <button
            onClick={promptInstall}
            style={{
              background: '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: '10px',
              padding: '8px 16px',
              fontWeight: 700,
              cursor: 'pointer',
              fontSize: '13px',
              whiteSpace: 'nowrap',
            }}>
            Installer
          </button>
        </div>
      )}
    </>
  );
};

export default PWABanner;
