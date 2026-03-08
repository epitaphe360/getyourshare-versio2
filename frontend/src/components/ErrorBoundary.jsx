import React from 'react';

/**
 * ErrorBoundary React Component
 * ✅ FIX UX P0: Gestion des erreurs React avec UI de secours
 * 
 * Capture les erreurs React et affiche une UI de secours élégante
 * au lieu d'un écran blanc qui terrifie les utilisateurs
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Mettre à jour l'état pour afficher l'UI de secours au prochain rendu
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // Capture vers Sentry en production
    if (process.env.NODE_ENV === 'production') {
      try {
        // Via le SDK Sentry chargé dans monitoring.js
        if (window.__setSentryUser || (typeof window !== 'undefined' && window.Sentry)) {
          window.Sentry.captureException(error, {
            contexts: { react: { componentStack: errorInfo?.componentStack } }
          });
        }
        // Via @sentry/react si disponible
        const Sentry = require('@sentry/react');
        if (Sentry?.captureException) {
          Sentry.captureException(error, {
            contexts: { react: { componentStack: errorInfo?.componentStack } }
          });
        }
      } catch (_) {
        // Sentry non disponible — ignorer silencieusement
      }
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    // Recharger la page si trop d'erreurs
    if (this.state.errorCount > 3) {
      window.location.reload();
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 text-center">
            {/* Icône d'erreur animée */}
            <div className="mb-6">
              <div className="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center animate-pulse">
                <svg 
                  className="w-10 h-10 text-red-600" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                  />
                </svg>
              </div>
            </div>

            {/* Message principal */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Oups ! Quelque chose s'est mal passé
            </h1>
            <p className="text-gray-600 mb-6">
              Une erreur inattendue s'est produite. Ne vous inquiétez pas, 
              votre travail est sauvegardé automatiquement.
            </p>

            {/* Détails d'erreur (seulement en dev) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 text-left bg-gray-50 rounded-lg p-4">
                <summary className="cursor-pointer font-semibold text-gray-700 mb-2">
                  Détails techniques (dev)
                </summary>
                <div className="text-xs text-gray-600 space-y-2">
                  <div>
                    <strong>Erreur:</strong>
                    <pre className="mt-1 p-2 bg-red-50 rounded overflow-x-auto">
                      {this.state.error.toString()}
                    </pre>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>Stack trace:</strong>
                      <pre className="mt-1 p-2 bg-red-50 rounded overflow-x-auto text-xs">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleReset}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
              >
                Réessayer
              </button>
              <button
                onClick={this.handleReload}
                className="px-6 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg transition-colors duration-200"
              >
                Recharger la page
              </button>
            </div>

            {/* Message de support */}
            <p className="mt-6 text-sm text-gray-500">
              Si le problème persiste, contactez le{' '}
              <a 
                href="mailto:support@getyourshare.com" 
                className="text-blue-600 hover:underline font-medium"
              >
                support technique
              </a>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
