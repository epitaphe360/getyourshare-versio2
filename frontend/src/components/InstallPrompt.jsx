import React, { useState, useEffect } from 'react';
import { Button, Modal, Typography, Card } from 'antd';
import { DownloadOutlined, MobileOutlined, CloseOutlined } from '@ant-design/icons';
import './InstallPrompt.css';

const { Title, Paragraph } = Typography;

const InstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [installInstructions, setInstallInstructions] = useState('');

  useEffect(() => {
    // Vérifier si l'app est déjà installée
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Détecter l'événement beforeinstallprompt
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Afficher la modal après 30 secondes (seulement première visite)
      const hasSeenPrompt = localStorage.getItem('pwa-install-prompt-seen');
      if (!hasSeenPrompt) {
        setTimeout(() => {
          setShowModal(true);
          localStorage.setItem('pwa-install-prompt-seen', 'true');
        }, 30000);
      }
    };

    window.addEventListener('beforeinstallprompt', handler);

    // Détecter l'installation
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setShowModal(false);
    });

    // Détecter le navigateur pour instructions spécifiques
    detectBrowser();

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const detectBrowser = () => {
    const ua = navigator.userAgent;
    
    if (/iPhone|iPad|iPod/.test(ua)) {
      setInstallInstructions(
        'Sur iOS: Appuyez sur le bouton Partager puis "Sur l\'écran d\'accueil"'
      );
    } else if (/Android/.test(ua)) {
      setInstallInstructions(
        'Sur Android: Appuyez sur le menu (⋮) puis "Installer l\'application"'
      );
    } else {
      setInstallInstructions(
        'Cliquez sur l\'icône d\'installation dans la barre d\'adresse'
      );
    }
  };

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      // Navigateur ne supporte pas l'installation automatique
      setShowModal(true);
      return;
    }

    // Afficher le prompt d'installation natif
    deferredPrompt.prompt();

    // Attendre la réponse de l'utilisateur
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
      setIsInstalled(true);
    } else {
      console.log('User dismissed the install prompt');
    }

    setDeferredPrompt(null);
    setShowModal(false);
  };

  const handleDismiss = () => {
    setShowModal(false);
    localStorage.setItem('pwa-install-dismissed', Date.now());
  };

  if (isInstalled) {
    return null; // Ne rien afficher si déjà installé
  }

  return (
    <>
      {/* Bouton flottant */}
      {deferredPrompt && !showModal && (
        <div className="install-prompt-floating">
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            size="large"
            onClick={handleInstallClick}
            className="install-button-floating"
          >
            Installer l'app
          </Button>
        </div>
      )}

      {/* Modal d'installation */}
      <Modal
        open={showModal}
        onCancel={handleDismiss}
        footer={null}
        closeIcon={<CloseOutlined />}
        centered
        className="install-prompt-modal"
      >
        <div className="install-prompt-content">
          <div className="install-icon">
            <MobileOutlined style={{ fontSize: 64, color: '#1890ff' }} />
          </div>

          <Title level={3}>Installer GetYourShare</Title>
          
          <Paragraph>
            Installez notre application pour une meilleure expérience :
          </Paragraph>

          <Card className="features-card">
            <ul className="features-list">
              <li>✅ Accès rapide depuis votre écran d'accueil</li>
              <li>✅ Fonctionne hors ligne</li>
              <li>✅ Notifications en temps réel</li>
              <li>✅ Performance optimisée</li>
              <li>✅ Pas besoin de télécharger depuis un store</li>
            </ul>
          </Card>

          {deferredPrompt ? (
            <Button
              type="primary"
              size="large"
              icon={<DownloadOutlined />}
              onClick={handleInstallClick}
              block
              className="install-button"
            >
              Installer maintenant
            </Button>
          ) : (
            <div className="manual-install">
              <Paragraph strong>{installInstructions}</Paragraph>
            </div>
          )}

          <Button
            type="text"
            onClick={handleDismiss}
            className="dismiss-button"
          >
            Peut-être plus tard
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default InstallPrompt;
