import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: Envoie les cookies httpOnly automatiquement
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url;

    // Gestion détaillée des erreurs
    if (status === 401) {
      // 401 géré par AuthContext avec auto-refresh
      // Ne pas rediriger automatiquement ici
    } else if (status === 403) {
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
