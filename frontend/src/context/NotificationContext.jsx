import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { io } from 'socket.io-client';
import api from '../utils/api';
import { useAuth } from './AuthContext';
import { useToast } from './ToastContext';
import { API_URL } from '../config/api.config';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const { user, token } = useAuth();
  const toast = useToast();

  // États
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  // Refs
  const socketRef = useRef(null);
  const audioRef = useRef(null);

  // Configuration - utiliser l'URL centralisée
  const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || API_URL;
  const ENABLE_SOUND = localStorage.getItem('notification_sound') !== 'false';
  const ENABLE_BROWSER_NOTIF = Notification.permission === 'granted';

  /**
   * Initialiser la connexion Socket.IO
   */
  const initializeSocket = useCallback(() => {
    if (!user || !token || socketRef.current?.connected) return;

    console.log('[Notifications] Initializing socket connection...');

    const socket = io(SOCKET_URL, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    // Événement: Connexion réussie
    socket.on('connected', (data) => {
      console.log('[Notifications] Connected to socket:', data);
      setIsConnected(true);

      // Demander le count initial
      socket.emit('notification:get-count');
    });

    // Événement: Nouvelle notification
    socket.on('notification', (notification) => {
      console.log('[Notifications] New notification received:', notification);

      // Ajouter à la liste
      setNotifications(prev => [notification, ...prev]);

      // Incrémenter le count
      setUnreadCount(prev => prev + 1);

      // Jouer le son
      if (ENABLE_SOUND) {
        playNotificationSound();
      }

      // Notification navigateur
      if (ENABLE_BROWSER_NOTIF) {
        showBrowserNotification(notification);
      }

      // Toast notification
      showToastNotification(notification);
    });

    // Événement: Mise à jour du count
    socket.on('notification:count', (count) => {
      console.log('[Notifications] Unread count updated:', count);
      setUnreadCount(count);
    });

    // Événement: Notification marquée comme lue
    socket.on('notification:marked-read', (data) => {
      console.log('[Notifications] Notification marked as read:', data.notification_id);

      setNotifications(prev =>
        prev.map(n =>
          n.id === data.notification_id
            ? { ...n, read: true, read_at: new Date() }
            : n
        )
      );
    });

    // Événement: Toutes marquées comme lues
    socket.on('notification:all-marked-read', () => {
      console.log('[Notifications] All notifications marked as read');

      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true, read_at: new Date() }))
      );
      setUnreadCount(0);
    });

    // Événement: Erreur
    socket.on('notification:error', (error) => {
      console.error('[Notifications] Socket error:', error);
      toast.error(error.message || 'Erreur de notification');
    });

    // Événement: Déconnexion
    socket.on('disconnect', (reason) => {
      console.log('[Notifications] Disconnected:', reason);
      setIsConnected(false);
    });

    // Événement: Reconnexion
    socket.on('reconnect', (attemptNumber) => {
      console.log('[Notifications] Reconnected after', attemptNumber, 'attempts');
      setIsConnected(true);
      socket.emit('notification:get-count');
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [user, token, toast, SOCKET_URL, ENABLE_SOUND, ENABLE_BROWSER_NOTIF]);

  /**
   * Charger les notifications initiales depuis l'API
   */
  const loadNotifications = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await api.get('/api/notifications?limit=50');

      if (response.data.success) {
        setNotifications(response.data.notifications);
      }

      // Charger le count
      const countResponse = await api.get('/api/notifications/count');
      if (countResponse.data.success) {
        setUnreadCount(countResponse.data.unread_count);
      }
    } catch (error) {
      console.error('[Notifications] Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  /**
   * Marquer une notification comme lue
   */
  const markAsRead = useCallback(async (notificationId) => {
    try {
      // Optimistic update
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId
            ? { ...n, read: true, read_at: new Date() }
            : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));

      // Émettre via socket
      if (socketRef.current?.connected) {
        socketRef.current.emit('notification:mark-read', { notification_id: notificationId });
      } else {
        // Fallback: API
        await api.put(`/api/notifications/${notificationId}/read`);
      }
    } catch (error) {
      console.error('[Notifications] Error marking as read:', error);
      // Revert optimistic update
      loadNotifications();
    }
  }, [loadNotifications]);

  /**
   * Marquer toutes les notifications comme lues
   */
  const markAllAsRead = useCallback(async () => {
    try {
      // Optimistic update
      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true, read_at: new Date() }))
      );
      setUnreadCount(0);

      // Émettre via socket
      if (socketRef.current?.connected) {
        socketRef.current.emit('notification:mark-all-read');
      } else {
        // Fallback: API
        await api.put('/api/notifications/read-all');
      }

      toast.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      console.error('[Notifications] Error marking all as read:', error);
      toast.error('Erreur lors de la mise à jour');
      // Revert optimistic update
      loadNotifications();
    }
  }, [toast, loadNotifications]);

  /**
   * Supprimer une notification
   */
  const deleteNotification = useCallback(async (notificationId) => {
    try {
      // Optimistic update
      setNotifications(prev => prev.filter(n => n.id !== notificationId));

      await api.delete(`/api/notifications/${notificationId}`);
    } catch (error) {
      console.error('[Notifications] Error deleting notification:', error);
      toast.error('Erreur lors de la suppression');
      // Revert
      loadNotifications();
    }
  }, [toast, loadNotifications]);

  /**
   * Jouer le son de notification
   */
  const playNotificationSound = useCallback(() => {
    try {
      if (!audioRef.current) {
        audioRef.current = new Audio('/sounds/notification.mp3');
        audioRef.current.volume = 0.5;
      }
      audioRef.current.play().catch(e => {
        console.log('[Notifications] Cannot play sound:', e);
      });
    } catch (error) {
      console.error('[Notifications] Sound error:', error);
    }
  }, []);

  /**
   * Afficher une notification navigateur
   */
  const showBrowserNotification = useCallback((notification) => {
    if (Notification.permission !== 'granted') return;

    try {
      const browserNotif = new Notification(notification.title, {
        body: notification.message,
        icon: '/icon-192x192.png',
        badge: '/badge-icon.png',
        tag: notification.id,
        requireInteraction: notification.priority === 'urgent',
        data: {
          url: notification.action_url || '/notifications'
        }
      });

      browserNotif.onclick = () => {
        window.focus();
        if (notification.action_url) {
          window.location.href = notification.action_url;
        }
        browserNotif.close();
      };
    } catch (error) {
      console.error('[Notifications] Browser notification error:', error);
    }
  }, []);

  /**
   * Afficher un toast
   */
  const showToastNotification = useCallback((notification) => {
    const priority = notification.priority || 'medium';

    const toastOptions = {
      duration: priority === 'urgent' ? 10000 : 5000
    };

    switch (priority) {
      case 'urgent':
      case 'high':
        toast.error(notification.message, toastOptions);
        break;
      case 'medium':
        toast.info(notification.message, toastOptions);
        break;
      case 'low':
        toast.success(notification.message, toastOptions);
        break;
      default:
        toast.info(notification.message, toastOptions);
    }
  }, [toast]);

  /**
   * Demander la permission pour les notifications navigateur
   */
  const requestBrowserPermission = useCallback(async () => {
    if (!('Notification' in window)) {
      console.log('[Notifications] Browser does not support notifications');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }

    return false;
  }, []);

  /**
   * Activer/désactiver le son
   */
  const toggleSound = useCallback((enabled) => {
    localStorage.setItem('notification_sound', enabled ? 'true' : 'false');
  }, []);

  // Effets
  useEffect(() => {
    if (user && token) {
      initializeSocket();
      loadNotifications();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [user, token, initializeSocket, loadNotifications]);

  const value = {
    notifications,
    unreadCount,
    isConnected,
    loading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    loadNotifications,
    requestBrowserPermission,
    toggleSound,
    playNotificationSound
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
