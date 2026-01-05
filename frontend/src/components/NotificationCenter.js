import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, AlertCircle, CheckCircle, Info, Zap } from 'lucide-react';

/**
 * Système de notifications en temps réel pour commerciaux
 * - Bell icon avec compteur
 * - Notifications push pour statuts, tâches, leads chauds
 * - Historique et marquage comme lu
 */

const NotificationCenter = ({ userId }) => {
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem(`notifications_${userId}`);
    return saved ? JSON.parse(saved) : [];
  });

  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // =====================================================
  // HOOKS
  // =====================================================

  useEffect(() => {
    // Mettre à jour le compteur de non-lus
    const unread = notifications.filter(n => !n.read).length;
    setUnreadCount(unread);
  }, [notifications]);

  useEffect(() => {
    // Simuler les notifications en temps réel
    // En production, ce serait WebSocket ou Server-Sent Events
    const interval = setInterval(() => {
      const chance = Math.random();
      if (chance < 0.1) { // 10% de chance toutes les 10s
        const types = ['lead_status', 'task_reminder', 'hot_lead', 'milestone'];
        const type = types[Math.floor(Math.random() * types.length)];
        
        switch (type) {
          case 'lead_status':
            addNotification({
              type: 'lead_status',
              title: 'Statut Lead Modifié',
              message: 'Jean Dupont (Acme Corp) est passé à "Qualifié"',
              icon: 'info',
              actionUrl: '/leads/123'
            });
            break;
          case 'task_reminder':
            addNotification({
              type: 'task_reminder',
              title: 'Rappel: Appel Prévu',
              message: 'Appel avec Marie Bernard dans 30 minutes',
              icon: 'alert',
              actionUrl: '/tasks'
            });
            break;
          case 'hot_lead':
            addNotification({
              type: 'hot_lead',
              title: '🔥 Lead Très Chaud!',
              message: 'TechStart Solutions vient de télécharger votre présentation',
              icon: 'zap',
              actionUrl: '/leads/456'
            });
            break;
          case 'milestone':
            addNotification({
              type: 'milestone',
              title: '🎉 Objectif Atteint!',
              message: 'Vous avez dépassé votre objectif du mois de 15%',
              icon: 'check',
              actionUrl: '/dashboard'
            });
            break;
          default:
            break;
        }
      }
    }, 10000); // Vérifier toutes les 10 secondes

    return () => clearInterval(interval);
  }, []);

  // =====================================================
  // HANDLERS
  // =====================================================

  const addNotification = useCallback((notification) => {
    const newNotification = {
      id: Date.now(),
      read: false,
      createdAt: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
      ...notification
    };

    setNotifications(prev => {
      const updated = [newNotification, ...prev].slice(0, 50); // Garder max 50
      localStorage.setItem(`notifications_${userId}`, JSON.stringify(updated));
      return updated;
    });

    // Toast visuel
    showToastNotification(notification);
  }, [userId]);

  const markAsRead = (id) => {
    setNotifications(prev => {
      const updated = prev.map(n => n.id === id ? { ...n, read: true } : n);
      localStorage.setItem(`notifications_${userId}`, JSON.stringify(updated));
      return updated;
    });
  };

  const markAllAsRead = () => {
    setNotifications(prev => {
      const updated = prev.map(n => ({ ...n, read: true }));
      localStorage.setItem(`notifications_${userId}`, JSON.stringify(updated));
      return updated;
    });
  };

  const deleteNotification = (id) => {
    setNotifications(prev => {
      const updated = prev.filter(n => n.id !== id);
      localStorage.setItem(`notifications_${userId}`, JSON.stringify(updated));
      return updated;
    });
  };

  const clearAll = () => {
    setNotifications([]);
    localStorage.setItem(`notifications_${userId}`, JSON.stringify([]));
  };

  // =====================================================
  // RENDER
  // =====================================================

  const getIcon = (type) => {
    switch (type) {
      case 'alert':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'check':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'zap':
        return <Zap className="w-5 h-5 text-red-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getBackgroundColor = (type) => {
    switch (type) {
      case 'lead_status':
        return 'bg-blue-50 border-l-4 border-blue-500';
      case 'task_reminder':
        return 'bg-orange-50 border-l-4 border-orange-500';
      case 'hot_lead':
        return 'bg-red-50 border-l-4 border-red-500';
      case 'milestone':
        return 'bg-green-50 border-l-4 border-green-500';
      default:
        return 'bg-gray-50 border-l-4 border-gray-500';
    }
  };

  return (
    <>
      {/* Bell Icon */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative p-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition"
        >
          <Bell size={24} />
          {unreadCount > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute top-1 right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </motion.span>
          )}
        </button>

        {/* Dropdown Notifications */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute right-0 mt-2 w-96 max-h-96 bg-white rounded-lg shadow-xl z-50 flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b">
                <h3 className="font-bold text-gray-900">Notifications</h3>
                <div className="flex gap-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-xs text-purple-600 hover:text-purple-700 font-medium"
                    >
                      Tout marquer comme lu
                    </button>
                  )}
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>

              {/* Notifications List */}
              <div className="flex-1 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <Bell size={32} className="mx-auto mb-2 opacity-50" />
                    <p>Aucune notification</p>
                  </div>
                ) : (
                  <div className="space-y-2 p-2">
                    {notifications.map(notification => (
                      <motion.div
                        key={notification.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className={`p-3 rounded-lg cursor-pointer transition ${
                          notification.read ? 'opacity-60' : getBackgroundColor(notification.type)
                        }`}
                        onClick={() => {
                          markAsRead(notification.id);
                          if (notification.actionUrl) {
                            window.location.href = notification.actionUrl;
                          }
                        }}
                      >
                        <div className="flex gap-3">
                          <div className="flex-shrink-0 mt-0.5">
                            {getIcon(notification.icon)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 text-sm">
                              {notification.title}
                              {!notification.read && (
                                <span className="ml-2 inline-block w-2 h-2 bg-blue-500 rounded-full"></span>
                              )}
                            </p>
                            <p className="text-gray-600 text-xs mt-1 line-clamp-2">
                              {notification.message}
                            </p>
                            <p className="text-gray-400 text-xs mt-2">
                              {notification.createdAt}
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                            className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                          >
                            <X size={16} />
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {/* Footer */}
              {notifications.length > 0 && (
                <div className="border-t p-3 text-center">
                  <button
                    onClick={clearAll}
                    className="text-xs text-gray-500 hover:text-gray-700 font-medium"
                  >
                    Effacer toutes les notifications
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Toast Notifications (coin en haut à droite) */}
      <NotificationToasts />
    </>
  );
};

// =====================================================
// TOAST NOTIFICATIONS
// =====================================================

let toastCallbacks = [];

const showToastNotification = (notification) => {
  toastCallbacks.forEach(cb => cb(notification));
};

export const NotificationToasts = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    toastCallbacks.push((notification) => {
      const id = Date.now();
      setToasts(prev => [...prev, { ...notification, toastId: id }]);
      
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.toastId !== id));
      }, 5000);
    });

    return () => {
      toastCallbacks = [];
    };
  }, []);

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.toastId}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className={`p-4 rounded-lg shadow-lg text-white max-w-sm ${
              toast.type === 'hot_lead' ? 'bg-red-500' :
              toast.type === 'milestone' ? 'bg-green-500' :
              toast.type === 'task_reminder' ? 'bg-orange-500' :
              'bg-blue-500'
            }`}
          >
            <p className="font-bold">{toast.title}</p>
            <p className="text-sm opacity-90">{toast.message}</p>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default NotificationCenter;
export { showToastNotification };
