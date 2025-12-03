const Notification = require('../models/Notification');
const User = require('../models/User');
const EmailService = require('./EmailService');
const PushNotificationService = require('./PushNotificationService');
const SMSService = require('./SMSService');
const { getIO } = require('../sockets/socketManager');

/**
 * Service de gestion des notifications multi-canal
 * Support: In-App (WebSocket), Push (PWA), Email, SMS
 */
class NotificationService {

  /**
   * Créer et envoyer une notification
   * @param {Object} params - Paramètres de la notification
   * @returns {Promise<Notification>}
   */
  async create(params) {
    const {
      user_id,
      type,
      title,
      message,
      priority = 'medium',
      data = {},
      action_url = null,
      action_label = null,
      channels = { in_app: true, push: false, email: false, sms: false },
      group_key = null,
      expires_in_hours = null
    } = params;

    // Validation
    if (!user_id || !type || !title || !message) {
      throw new Error('Missing required notification parameters');
    }

    // Vérifier si l'utilisateur existe
    const user = await User.findByPk(user_id);
    if (!user) {
      throw new Error(`User ${user_id} not found`);
    }

    // Calculer expiration
    let expires_at = null;
    if (expires_in_hours) {
      expires_at = new Date();
      expires_at.setHours(expires_at.getHours() + expires_in_hours);
    }

    // Groupage: éviter spam de notifications similaires
    if (group_key) {
      const existing = await this.findExistingGrouped(user_id, group_key);
      if (existing) {
        // Mettre à jour la notification existante
        existing.title = title;
        existing.message = message;
        existing.data = data;
        existing.created_at = new Date();
        await existing.save();

        // Re-envoyer sur les canaux
        await this.sendToChannels(existing, channels, user);
        return existing;
      }
    }

    // Créer la notification
    const notification = await Notification.create({
      user_id,
      type,
      title,
      message,
      priority,
      data,
      action_url,
      action_label,
      channels,
      group_key,
      expires_at,
      status: 'pending'
    });

    // Envoyer sur les canaux demandés
    await this.sendToChannels(notification, channels, user);

    return notification;
  }

  /**
   * Envoyer la notification sur les différents canaux
   */
  async sendToChannels(notification, channels, user) {
    const promises = [];

    // In-App (WebSocket)
    if (channels.in_app) {
      promises.push(this.sendInApp(notification, user));
    }

    // Push Notification (PWA)
    if (channels.push) {
      promises.push(this.sendPush(notification, user));
    }

    // Email
    if (channels.email) {
      promises.push(this.sendEmail(notification, user));
    }

    // SMS
    if (channels.sms) {
      promises.push(this.sendSMS(notification, user));
    }

    await Promise.allSettled(promises);

    // Marquer comme envoyée
    await notification.markAsSent();
  }

  /**
   * Envoyer notification in-app via WebSocket
   */
  async sendInApp(notification, user) {
    try {
      const io = getIO();

      // Émettre à l'utilisateur spécifique
      io.to(`user_${user.id}`).emit('notification', {
        id: notification.id,
        type: notification.type,
        title: notification.title,
        message: notification.message,
        priority: notification.priority,
        data: notification.data,
        action_url: notification.action_url,
        action_label: notification.action_label,
        created_at: notification.created_at
      });

      // Émettre le nouveau count de notifications non lues
      const unreadCount = await Notification.getUnreadCount(user.id);
      io.to(`user_${user.id}`).emit('notification:count', unreadCount);

      await notification.markAsDelivered();

      console.log(`[Notification] In-App sent to user ${user.id}: ${notification.title}`);
    } catch (error) {
      console.error('[Notification] In-App send error:', error);
    }
  }

  /**
   * Envoyer Push Notification (PWA)
   */
  async sendPush(notification, user) {
    try {
      if (!user.push_subscription) {
        console.log(`[Notification] No push subscription for user ${user.id}`);
        return;
      }

      await PushNotificationService.send(user.push_subscription, {
        title: notification.title,
        body: notification.message,
        icon: this.getNotificationIcon(notification.type),
        badge: '/badge-icon.png',
        data: {
          notification_id: notification.id,
          url: notification.action_url || '/notifications'
        },
        actions: notification.action_label ? [
          {
            action: 'open',
            title: notification.action_label
          }
        ] : []
      });

      console.log(`[Notification] Push sent to user ${user.id}`);
    } catch (error) {
      console.error('[Notification] Push send error:', error);
    }
  }

  /**
   * Envoyer Email
   */
  async sendEmail(notification, user) {
    try {
      const emailTemplate = this.getEmailTemplate(notification.type);

      await EmailService.send({
        to: user.email,
        subject: notification.title,
        template: emailTemplate,
        data: {
          user_name: user.first_name || user.username,
          title: notification.title,
          message: notification.message,
          action_url: notification.action_url,
          action_label: notification.action_label,
          notification_data: notification.data
        }
      });

      console.log(`[Notification] Email sent to ${user.email}`);
    } catch (error) {
      console.error('[Notification] Email send error:', error);
    }
  }

  /**
   * Envoyer SMS
   */
  async sendSMS(notification, user) {
    try {
      if (!user.phone) {
        console.log(`[Notification] No phone number for user ${user.id}`);
        return;
      }

      const smsText = `${notification.title}: ${notification.message}`;
      await SMSService.send(user.phone, smsText);

      console.log(`[Notification] SMS sent to ${user.phone}`);
    } catch (error) {
      console.error('[Notification] SMS send error:', error);
    }
  }

  /**
   * Trouver notification existante groupée
   */
  async findExistingGrouped(userId, groupKey) {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);

    return await Notification.findOne({
      where: {
        user_id: userId,
        group_key: groupKey,
        created_at: {
          [Notification.sequelize.Sequelize.Op.gte]: fiveMinutesAgo
        }
      },
      order: [['created_at', 'DESC']]
    });
  }

  /**
   * Récupérer les notifications d'un utilisateur
   */
  async getUserNotifications(userId, options = {}) {
    const {
      limit = 50,
      offset = 0,
      unread_only = false,
      types = null
    } = options;

    const where = {
      user_id: userId
    };

    if (unread_only) {
      where.read = false;
    }

    if (types && types.length > 0) {
      where.type = types;
    }

    const notifications = await Notification.findAll({
      where,
      order: [['created_at', 'DESC']],
      limit,
      offset
    });

    return notifications;
  }

  /**
   * Marquer une notification comme lue
   */
  async markAsRead(notificationId, userId) {
    const notification = await Notification.findOne({
      where: {
        id: notificationId,
        user_id: userId
      }
    });

    if (!notification) {
      throw new Error('Notification not found');
    }

    await notification.markAsRead();

    // Émettre le nouveau count
    const io = getIO();
    const unreadCount = await Notification.getUnreadCount(userId);
    io.to(`user_${userId}`).emit('notification:count', unreadCount);

    return notification;
  }

  /**
   * Marquer toutes les notifications comme lues
   */
  async markAllAsRead(userId) {
    await Notification.markAllAsRead(userId);

    // Émettre le nouveau count
    const io = getIO();
    io.to(`user_${userId}`).emit('notification:count', 0);

    return { success: true };
  }

  /**
   * Supprimer une notification
   */
  async delete(notificationId, userId) {
    const notification = await Notification.findOne({
      where: {
        id: notificationId,
        user_id: userId
      }
    });

    if (!notification) {
      throw new Error('Notification not found');
    }

    await notification.destroy();

    // Émettre le nouveau count
    const io = getIO();
    const unreadCount = await Notification.getUnreadCount(userId);
    io.to(`user_${userId}`).emit('notification:count', unreadCount);

    return { success: true };
  }

  /**
   * Nettoyer les notifications expirées (Cron Job)
   */
  async cleanupExpired() {
    const deleted = await Notification.deleteExpired();
    console.log(`[Notification] Cleaned up ${deleted} expired notifications`);
    return deleted;
  }

  /**
   * Obtenir l'icône selon le type de notification
   */
  getNotificationIcon(type) {
    const icons = {
      collaboration_request: '🤝',
      collaboration_accepted: '✅',
      collaboration_rejected: '❌',
      counter_offer: '💱',
      payment_received: '💰',
      payment_pending: '⏳',
      new_sale: '🛒',
      new_lead: '👤',
      lead_hot: '🔥',
      task_reminder: '⏰',
      contract_signed: '📝',
      contract_pending: '📄',
      stock_low: '⚠️',
      stock_critical: '🚨',
      product_out_of_stock: '📦',
      new_review: '⭐',
      review_negative: '😞',
      campaign_started: '🚀',
      campaign_ended: '🏁',
      quota_reached: '🎯',
      milestone_achieved: '🏆',
      referral_signup: '🎁',
      referral_payment: '💵',
      live_shopping_starting: '🎥',
      message_received: '💬',
      mention: '📢',
      system_update: 'ℹ️',
      security_alert: '🛡️'
    };

    return icons[type] || '🔔';
  }

  /**
   * Obtenir le template email selon le type
   */
  getEmailTemplate(type) {
    // Mapper les types aux templates d'email
    const templates = {
      collaboration_request: 'collaboration-request',
      collaboration_accepted: 'collaboration-accepted',
      payment_received: 'payment-received',
      new_sale: 'new-sale',
      new_lead: 'new-lead',
      stock_low: 'stock-alert',
      stock_critical: 'stock-alert',
      new_review: 'new-review',
      review_negative: 'review-negative'
    };

    return templates[type] || 'notification-default';
  }

  // ========== HELPERS POUR CRÉER DES NOTIFICATIONS SPÉCIFIQUES ==========

  /**
   * Notification: Nouvelle demande de collaboration
   */
  async notifyCollaborationRequest(influencerId, merchantName, productsCount, commission) {
    return await this.create({
      user_id: influencerId,
      type: 'collaboration_request',
      title: 'Nouvelle demande de collaboration',
      message: `${merchantName} vous propose une collaboration sur ${productsCount} produit(s) avec ${commission}% de commission`,
      priority: 'high',
      data: {
        merchant_name: merchantName,
        products_count: productsCount,
        commission
      },
      action_url: '/dashboard?tab=collaboration',
      action_label: 'Voir la demande',
      channels: {
        in_app: true,
        push: true,
        email: true,
        sms: false
      }
    });
  }

  /**
   * Notification: Paiement reçu
   */
  async notifyPaymentReceived(userId, amount, method) {
    return await this.create({
      user_id: userId,
      type: 'payment_received',
      title: 'Paiement reçu',
      message: `Vous avez reçu un paiement de ${amount}€ via ${method}`,
      priority: 'high',
      data: { amount, method },
      action_url: '/wallet',
      action_label: 'Voir mes transactions',
      channels: {
        in_app: true,
        push: true,
        email: true,
        sms: false
      }
    });
  }

  /**
   * Notification: Nouveau lead (Commercial)
   */
  async notifyNewLead(commercialId, leadName, leadEmail, source) {
    return await this.create({
      user_id: commercialId,
      type: 'new_lead',
      title: 'Nouveau lead',
      message: `${leadName} (${leadEmail}) vient de s'inscrire via ${source}`,
      priority: 'high',
      data: {
        lead_name: leadName,
        lead_email: leadEmail,
        source
      },
      action_url: '/leads',
      action_label: 'Voir le lead',
      channels: {
        in_app: true,
        push: true,
        email: false,
        sms: false
      },
      group_key: `new_leads_${commercialId}`
    });
  }

  /**
   * Notification: Stock bas (Marchand)
   */
  async notifyLowStock(merchantId, productName, currentStock, threshold) {
    const isCritical = currentStock < (threshold * 0.5);

    return await this.create({
      user_id: merchantId,
      type: isCritical ? 'stock_critical' : 'stock_low',
      title: isCritical ? '🚨 Stock critique' : '⚠️ Stock bas',
      message: `${productName}: ${currentStock} unités restantes (seuil: ${threshold})`,
      priority: isCritical ? 'urgent' : 'high',
      data: {
        product_name: productName,
        current_stock: currentStock,
        threshold
      },
      action_url: '/inventory',
      action_label: 'Gérer le stock',
      channels: {
        in_app: true,
        push: true,
        email: isCritical,
        sms: false
      },
      group_key: `stock_alert_${productName}`
    });
  }

  /**
   * Notification: Nouvelle vente (Marchand)
   */
  async notifyNewSale(merchantId, productName, amount, buyerName) {
    return await this.create({
      user_id: merchantId,
      type: 'new_sale',
      title: '🛒 Nouvelle vente',
      message: `${buyerName} a acheté ${productName} pour ${amount}€`,
      priority: 'medium',
      data: {
        product_name: productName,
        amount,
        buyer_name: buyerName
      },
      action_url: '/orders',
      action_label: 'Voir la commande',
      channels: {
        in_app: true,
        push: false,
        email: false,
        sms: false
      }
    });
  }

  /**
   * Notification: Avis négatif (Marchand)
   */
  async notifyNegativeReview(merchantId, productName, rating, reviewText) {
    return await this.create({
      user_id: merchantId,
      type: 'review_negative',
      title: '😞 Avis négatif reçu',
      message: `${productName} a reçu un avis ${rating}⭐: "${reviewText.substring(0, 100)}..."`,
      priority: 'high',
      data: {
        product_name: productName,
        rating,
        review_text: reviewText
      },
      action_url: '/reviews',
      action_label: 'Répondre à l\'avis',
      channels: {
        in_app: true,
        push: true,
        email: true,
        sms: false
      }
    });
  }

  /**
   * Notification: Quota atteint (Commercial)
   */
  async notifyQuotaReached(commercialId, quotaAmount, period) {
    return await this.create({
      user_id: commercialId,
      type: 'quota_reached',
      title: '🎯 Quota atteint!',
      message: `Félicitations! Vous avez atteint votre quota de ${quotaAmount}€ pour ${period}`,
      priority: 'medium',
      data: {
        quota_amount: quotaAmount,
        period
      },
      action_url: '/dashboard',
      action_label: 'Voir mes performances',
      channels: {
        in_app: true,
        push: true,
        email: true,
        sms: false
      }
    });
  }
}

module.exports = new NotificationService();
