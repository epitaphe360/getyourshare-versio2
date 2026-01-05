import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNotifications } from '../../context/NotificationContext';
import { useNavigate } from 'router-dom';
import {
  X, Check, CheckCheck, Trash2, Bell, BellOff,
  AlertCircle, Info, CheckCircle, Gift, DollarSign,
  Users, ShoppingCart, TrendingUp, Calendar, MessageCircle
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Centre de notifications - Panneau coulissant
 */
const NotificationCenter = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    loading
  } = useNotifications();

  const [filter, setFilter] = useState('all'); // 'all', 'unread'

  // Filtrer les notifications
  const filteredNotifications = filter === 'unread'
    ? notifications.filter(n => !n.read)
    : notifications;

  // Grouper par jour
  const groupedNotifications = groupByDay(filteredNotifications);

  /**
   * Gérer le clic sur une notification
   */
  const handleNotificationClick = async (notification) => {
    // Marquer comme lue
    if (!notification.read) {
      await markAsRead(notification.id);
    }

    // Naviguer vers l'action
    if (notification.action_url) {
      navigate(notification.action_url);
      onClose();
    }
  };

  /**
   * Obtenir l'icône selon le type
   */
  const getNotificationIcon = (type, priority) => {
    const iconProps = {
      size: 20,
      className: getPriorityColor(priority)
    };

    const icons = {
      collaboration_request: <Users {...iconProps} />,
      collaboration_accepted: <CheckCircle {...iconProps} />,
      payment_received: <DollarSign {...iconProps} />,
      new_sale: <ShoppingCart {...iconProps} />,
      new_lead: <Users {...iconProps} />,
      lead_hot: <TrendingUp {...iconProps} />,
      task_reminder: <Calendar {...iconProps} />,
      stock_low: <AlertCircle {...iconProps} />,
      stock_critical: <AlertCircle {...iconProps} />,
      new_review: <MessageCircle {...iconProps} />,
      referral_payment: <Gift {...iconProps} />
    };

    return icons[type] || <Bell {...iconProps} />;
  };

  /**
   * Obtenir la couleur selon la priorité
   */
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'medium':
        return 'text-blue-600';
      case 'low':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  /**
   * Obtenir la classe de background selon priorité
   */
  const getPriorityBg = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-50 border-red-200';
      case 'high':
        return 'bg-orange-50 border-orange-200';
      case 'medium':
        return 'bg-blue-50 border-blue-200';
      case 'low':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-30 z-40"
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Bell size={24} />
                  Notifications
                </h2>
                <p className="text-sm text-indigo-100">
                  {unreadCount} non lue{unreadCount > 1 ? 's' : ''}
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition"
              >
                <X size={24} />
              </button>
            </div>

            {/* Actions Bar */}
            <div className="flex items-center justify-between p-3 border-b bg-gray-50">
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                    filter === 'all'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Toutes ({notifications.length})
                </button>
                <button
                  onClick={() => setFilter('unread')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                    filter === 'unread'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Non lues ({unreadCount})
                </button>
              </div>

              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-indigo-600 rounded-lg text-sm font-medium hover:bg-indigo-50 transition"
                >
                  <CheckCheck size={16} />
                  Tout lire
                </button>
              )}
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              ) : filteredNotifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                  <BellOff size={48} className="mb-4 text-gray-300" />
                  <p className="text-lg font-medium">Aucune notification</p>
                  <p className="text-sm">Vous êtes à jour!</p>
                </div>
              ) : (
                <div className="p-3 space-y-4">
                  {Object.entries(groupedNotifications).map(([day, dayNotifications]) => (
                    <div key={day}>
                      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 px-2">
                        {day}
                      </h3>
                      <div className="space-y-2">
                        {dayNotifications.map((notification) => (
                          <NotificationItem
                            key={notification.id}
                            notification={notification}
                            onClick={() => handleNotificationClick(notification)}
                            onMarkAsRead={() => markAsRead(notification.id)}
                            onDelete={() => deleteNotification(notification.id)}
                            getIcon={() => getNotificationIcon(notification.type, notification.priority)}
                            getPriorityBg={() => getPriorityBg(notification.priority)}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

/**
 * Item de notification individuel
 */
const NotificationItem = ({
  notification,
  onClick,
  onMarkAsRead,
  onDelete,
  getIcon,
  getPriorityBg
}) => {
  const [showActions, setShowActions] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onClick={onClick}
      className={`relative p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
        !notification.read
          ? `${getPriorityBg()} border-l-4`
          : 'bg-white border-gray-200 opacity-75'
      }`}
    >
      <div className="flex gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          !notification.read ? 'bg-white' : 'bg-gray-100'
        }`}>
          {getIcon()}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={`text-sm font-semibold ${
              !notification.read ? 'text-gray-900' : 'text-gray-600'
            }`}>
              {notification.title}
            </h4>

            {!notification.read && (
              <div className="flex-shrink-0 w-2 h-2 bg-indigo-600 rounded-full"></div>
            )}
          </div>

          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {notification.message}
          </p>

          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-500">
              {formatDistanceToNow(new Date(notification.created_at), {
                addSuffix: true,
                locale: fr
              })}
            </span>

            {notification.action_label && (
              <span className="text-xs font-medium text-indigo-600">
                {notification.action_label} →
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Actions (hover) */}
      <AnimatePresence>
        {showActions && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-2 right-2 flex gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            {!notification.read && (
              <button
                onClick={onMarkAsRead}
                className="p-1.5 bg-white rounded-lg shadow-md hover:bg-green-50 text-green-600 transition"
                title="Marquer comme lu"
              >
                <Check size={14} />
              </button>
            )}
            <button
              onClick={onDelete}
              className="p-1.5 bg-white rounded-lg shadow-md hover:bg-red-50 text-red-600 transition"
              title="Supprimer"
            >
              <Trash2 size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

/**
 * Grouper les notifications par jour
 */
function groupByDay(notifications) {
  const groups = {};
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  notifications.forEach(notification => {
    const date = new Date(notification.created_at);
    date.setHours(0, 0, 0, 0);

    let key;
    if (date.getTime() === today.getTime()) {
      key = "Aujourd'hui";
    } else if (date.getTime() === yesterday.getTime()) {
      key = 'Hier';
    } else {
      key = date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long'
      });
    }

    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(notification);
  });

  return groups;
}

export default NotificationCenter;
