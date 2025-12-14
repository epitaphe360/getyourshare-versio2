/**
 * Configuration centralisée pour l'API
 * Utilisez cette configuration dans tous les services et composants
 */

const getApiUrl = () => {
  let envUrl = process.env.REACT_APP_API_URL;

  // Si la variable d'environnement est définie et n'est pas localhost, l'utiliser
  if (envUrl && !envUrl.includes('localhost') && !envUrl.includes('127.0.0.1')) {
    // Éviter la duplication /api/api/
    envUrl = envUrl.replace(/\/api\/?$/, '');
    return envUrl;
  }

  // En environnement navigateur, utiliser le hostname actuel si ce n'est pas localhost
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:5000`;
    }
  }

  // Port par défaut: 5000 (backend FastAPI principal)
  return envUrl || 'http://127.0.0.1:5000';
};

// URL de base de l'API
export const API_URL = getApiUrl();

// URLs pour les WebSockets
export const getWebSocketUrl = () => {
  const baseUrl = API_URL.replace(/^http/, 'ws');
  return baseUrl;
};

// Exporter le getter pour les cas dynamiques
export { getApiUrl };

export default API_URL;
