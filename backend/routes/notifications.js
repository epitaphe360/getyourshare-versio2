const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const NotificationService = require('../services/NotificationService');
const PushNotificationService = require('../services/PushNotificationService');
const User = require('../models/User');

/**
 * Routes API pour les notifications
 */

/**
 * GET /api/notifications
 * Récupérer les notifications de l'utilisateur
 */
router.get('/', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const {
      limit = 50,
      offset = 0,
      unread_only = false,
      types = null
    } = req.query;

    const options = {
      limit: parseInt(limit),
      offset: parseInt(offset),
      unread_only: unread_only === 'true',
      types: types ? types.split(',') : null
    };

    const notifications = await NotificationService.getUserNotifications(userId, options);

    res.json({
      success: true,
      notifications,
      count: notifications.length
    });
  } catch (error) {
    console.error('Error fetching notifications:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching notifications',
      error: error.message
    });
  }
});

/**
 * GET /api/notifications/count
 * Obtenir le nombre de notifications non lues
 */
router.get('/count', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const Notification = require('../models/Notification');

    const unreadCount = await Notification.getUnreadCount(userId);

    res.json({
      success: true,
      unread_count: unreadCount
    });
  } catch (error) {
    console.error('Error fetching notification count:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching notification count',
      error: error.message
    });
  }
});

/**
 * PUT /api/notifications/:id/read
 * Marquer une notification comme lue
 */
router.put('/:id/read', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const notification = await NotificationService.markAsRead(id, userId);

    res.json({
      success: true,
      notification
    });
  } catch (error) {
    console.error('Error marking notification as read:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * PUT /api/notifications/read-all
 * Marquer toutes les notifications comme lues
 */
router.put('/read-all', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;

    await NotificationService.markAllAsRead(userId);

    res.json({
      success: true,
      message: 'All notifications marked as read'
    });
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * DELETE /api/notifications/:id
 * Supprimer une notification
 */
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    await NotificationService.delete(id, userId);

    res.json({
      success: true,
      message: 'Notification deleted'
    });
  } catch (error) {
    console.error('Error deleting notification:', error);
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * POST /api/notifications/push/subscribe
 * S'abonner aux push notifications
 */
router.post('/push/subscribe', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { subscription } = req.body;

    if (!subscription || !subscription.endpoint) {
      return res.status(400).json({
        success: false,
        message: 'Invalid subscription object'
      });
    }

    // Sauvegarder la subscription dans la base de données
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Mettre à jour le user avec la subscription
    user.push_subscription = subscription;
    await user.save();

    res.json({
      success: true,
      message: 'Push subscription saved'
    });
  } catch (error) {
    console.error('Error saving push subscription:', error);
    res.status(500).json({
      success: false,
      message: 'Error saving push subscription',
      error: error.message
    });
  }
});

/**
 * POST /api/notifications/push/unsubscribe
 * Se désabonner des push notifications
 */
router.post('/push/unsubscribe', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    user.push_subscription = null;
    await user.save();

    res.json({
      success: true,
      message: 'Push subscription removed'
    });
  } catch (error) {
    console.error('Error removing push subscription:', error);
    res.status(500).json({
      success: false,
      message: 'Error removing push subscription',
      error: error.message
    });
  }
});

/**
 * GET /api/notifications/push/public-key
 * Obtenir la clé publique VAPID
 */
router.get('/push/public-key', (req, res) => {
  try {
    const publicKey = PushNotificationService.getPublicKey();

    res.json({
      success: true,
      public_key: publicKey
    });
  } catch (error) {
    console.error('Error getting VAPID public key:', error);
    res.status(500).json({
      success: false,
      message: 'Error getting public key',
      error: error.message
    });
  }
});

/**
 * POST /api/notifications/test (Development only)
 * Créer une notification de test
 */
if (process.env.NODE_ENV !== 'production') {
  router.post('/test', authenticateToken, async (req, res) => {
    try {
      const userId = req.user.id;

      const notification = await NotificationService.create({
        user_id: userId,
        type: 'system_update',
        title: '🧪 Notification de Test',
        message: 'Ceci est une notification de test pour vérifier que le système fonctionne correctement.',
        priority: 'medium',
        data: { test: true },
        action_url: '/dashboard',
        action_label: 'Voir le dashboard',
        channels: {
          in_app: true,
          push: true,
          email: false,
          sms: false
        }
      });

      res.json({
        success: true,
        notification,
        message: 'Test notification created'
      });
    } catch (error) {
      console.error('Error creating test notification:', error);
      res.status(500).json({
        success: false,
        message: error.message
      });
    }
  });
}

module.exports = router;
