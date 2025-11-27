import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';

export const AuthContext = createContext(null);

// Intervalle de vérification de session (5 minutes)
const SESSION_CHECK_INTERVAL = 5 * 60 * 1000;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionStatus, setSessionStatus] = useState('checking'); // 'checking', 'active', 'expired'

  // Fonction pour vérifier la session auprès du backend
  const verifySession = async () => {
    try {
      // Vérifier d'abord si un token existe
      const token = localStorage.getItem('token');
      if (!token) {
        setUser(null);
        setSessionStatus('expired');
        setLoading(false);
        return false;
      }

      // Les cookies httpOnly sont automatiquement envoyés avec credentials: 'include'
      const response = await api.get('/api/auth/me');

      if (response.data) {
        setUser(response.data);
        setSessionStatus('active');
        return true;
      }
    } catch (error) {
      // Si 401, essayer de rafraîchir le token automatiquement
      if (error.response?.status === 401) {
        try {
          const refreshResponse = await api.post('/api/auth/refresh');
          if (refreshResponse.data?.user) {
            setUser(refreshResponse.data.user);
            setSessionStatus('active');
            return true;
          }
        } catch (refreshError) {
          // Refresh token aussi expiré, déconnexion nécessaire
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
          setSessionStatus('expired');
          return false;
        }
      }

      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setSessionStatus('expired');
      return false;
    } finally {
      setLoading(false);
    }

    return false;
  };

  useEffect(() => {
    // Vérifier la session au chargement
    verifySession();

    // Vérification périodique de la session (refresh automatique si nécessaire)
    const intervalId = setInterval(() => {
      if (sessionStatus === 'active') {
        verifySession();
      }
    }, SESSION_CHECK_INTERVAL);

    // Cleanup
    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Exécuter uniquement au montage du composant

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', { email, password });

      // Check if 2FA is required (support both snake_case and camelCase)
      if (response.data.requires_2fa || response.data.requires2FA) {
        return {
          success: false,
          requires2FA: true,
          requires_2fa: true, // Support both naming conventions
          tempToken: response.data.temp_token,
          temp_token: response.data.temp_token, // Support both naming conventions
          message: response.data.message || 'Code 2FA envoyé'
        };
      }

      // No 2FA required, login directly
      const { user: userData, access_token } = response.data;
      
      // Stocker le token
      if (access_token) {
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(userData));
      }

      setUser(userData);
      setSessionStatus('active');

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Connexion échouée'
      };
    }
  };

  const logout = async () => {
    try {
      // Appeler le backend pour déconnexion côté serveur (supprime les cookies)
      await api.post('/api/auth/logout');
    } catch (error) {
      // Continue même si le backend échoue (les cookies expirent de toute façon)
    } finally {
      // Nettoyer l'état utilisateur et le localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setSessionStatus('expired');
    }
  };

  // Fonction pour rafraîchir manuellement la session
  const refreshSession = async () => {
    return await verifySession();
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      loading,
      sessionStatus,
      refreshSession
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
