const webPush = require('web-push');

/**
 * Service de Push Notifications (PWA)
 * Support: Chrome, Firefox, Edge, Safari (iOS 16.4+)
 */

// Configuration Web Push (VAPID keys)
// Générer avec: npx web-push generate-vapid-keys
const vapidKeys = {
  publicKey: process.env.VAPID_PUBLIC_KEY || 'YOUR_PUBLIC_KEY',
  privateKey: process.env.VAPID_PRIVATE_KEY || 'YOUR_PRIVATE_KEY'
};

webPush.setVapidDetails(
  `mailto:${process.env.SUPPORT_EMAIL || 'support@getyourshare.com'}`,
  vapidKeys.publicKey,
  vapidKeys.privateKey
);

class PushNotificationService {

  /**
   * Envoyer une push notification
   * @param {Object} subscription - Push subscription object
   * @param {Object} payload - Notification payload
   */
  async send(subscription, payload) {
    try {
      if (!subscription || !subscription.endpoint) {
        throw new Error('Invalid subscription');
      }

      const notificationPayload = JSON.stringify({
        title: payload.title || 'GetYourShare',
        body: payload.body || '',
        icon: payload.icon || '/icon-192x192.png',
        badge: payload.badge || '/badge-icon.png',
        image: payload.image || null,
        tag: payload.tag || 'default',
        requireInteraction: payload.requireInteraction || false,
        actions: payload.actions || [],
        data: payload.data || {},
        timestamp: Date.now()
      });

      const options = {
        TTL: payload.ttl || 86400, // Time to live: 24h par défaut
        urgency: payload.urgency || 'normal', // 'very-low', 'low', 'normal', 'high'
        topic: payload.topic || null
      };

      const result = await webPush.sendNotification(
        subscription,
        notificationPayload,
        options
      );

      console.log('[PushNotification] Sent successfully:', result.statusCode);
      return result;

    } catch (error) {
      // Gestion des erreurs
      if (error.statusCode === 404 || error.statusCode === 410) {
        // Subscription expirée ou invalide
        console.log('[PushNotification] Subscription expired or invalid');
        // TODO: Supprimer la subscription de la base de données
        throw new Error('SUBSCRIPTION_EXPIRED');
      }

      console.error('[PushNotification] Send error:', error);
      throw error;
    }
  }

  /**
   * Envoyer à plusieurs subscriptions
   * @param {Array} subscriptions - Array of subscription objects
   * @param {Object} payload - Notification payload
   */
  async sendToMultiple(subscriptions, payload) {
    const promises = subscriptions.map(subscription =>
      this.send(subscription, payload).catch(error => ({
        error,
        subscription
      }))
    );

    const results = await Promise.allSettled(promises);

    const successful = results.filter(r => r.status === 'fulfilled' && !r.value.error);
    const failed = results.filter(r => r.status === 'rejected' || r.value?.error);

    console.log(`[PushNotification] Sent to ${successful.length}/${subscriptions.length} subscriptions`);

    return {
      successful: successful.length,
      failed: failed.length,
      total: subscriptions.length,
      failedSubscriptions: failed.map(f => f.value?.subscription || f.reason)
    };
  }

  /**
   * Obtenir les VAPID public key pour le frontend
   */
  getPublicKey() {
    return vapidKeys.publicKey;
  }

  /**
   * Vérifier si une subscription est valide
   */
  async verifySubscription(subscription) {
    try {
      // Tenter d'envoyer une notification de test
      await webPush.sendNotification(subscription, JSON.stringify({
        title: 'Test',
        body: 'Verification',
        tag: 'test-verification',
        data: { test: true }
      }));
      return true;
    } catch (error) {
      if (error.statusCode === 404 || error.statusCode === 410) {
        return false;
      }
      throw error;
    }
  }
}

module.exports = new PushNotificationService();
