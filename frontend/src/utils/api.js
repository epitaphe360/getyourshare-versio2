import axios from 'axios';

const getApiUrl = () => {
  let envUrl = process.env.REACT_APP_API_URL;

  // If env var is set and not localhost, use it (e.g. production URL)
  if (envUrl && !envUrl.includes('localhost') && !envUrl.includes('127.0.0.1')) {
    // Fix: Remove trailing /api if present (to avoid /api/api/ duplication)
    envUrl = envUrl.replace(/\/api\/?$/, '');
    return envUrl;
  }

  // If we are in a browser environment, try to use the current hostname
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If hostname is a local IP (not localhost), use it for backend too
    // This allows accessing the backend from other devices on the same network
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `http://${hostname}:5000`;
    }
  }

  return envUrl || 'http://127.0.0.1:5000';
};

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: Envoie les cookies httpOnly automatiquement
});

// Variables pour gérer le rafraîchissement du token
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor to add token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // Gestion du refresh token sur erreur 401
    if (status === 401 && !originalRequest._retry && originalRequest.url !== '/api/auth/refresh' && originalRequest.url !== '/api/auth/login') {
      
      // Si on est déjà sur la page de login, on ne fait rien
      if (window.location.pathname === '/login' || window.location.pathname === '/register') {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({resolve, reject});
        }).then(() => {
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Tenter de rafraîchir le token
        await api.post('/api/auth/refresh');
        
        // Si succès, traiter la file d'attente et réessayer la requête originale
        processQueue(null);
        isRefreshing = false;
        return api(originalRequest);
      } catch (refreshError) {
        // Si le refresh échoue, rejeter toutes les requêtes en attente
        processQueue(refreshError, null);
        isRefreshing = false;
        
        // Nettoyer le localStorage et rediriger
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Redirection unique vers le login
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
            window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }

    // Gestion détaillée des autres erreurs (logging)
    if (status === 403) {
      // 403 Forbidden
    } else if (status === 404) {
      // 404 Not Found
    } else if (status >= 500) {
      // Server error
    }

    return Promise.reject(error);
  }
);

// Fonction utilitaire pour vérifier la santé de l'API
export const checkAPIHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('❌ API non disponible:', error.message);
    return null;
  }
};

export default api;
