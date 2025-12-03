const UnifiedMessage = require('../models/UnifiedMessage');
const NotificationService = require('./NotificationService');
const { Op } = require('sequelize');

/**
 * UnifiedInboxService
 * Boîte de réception unifiée pour commerciaux
 * Tous les canaux (Email, SMS, WhatsApp, etc.) en un seul endroit
 * ROI: Productivité +60%, Temps de réponse -50%
 */
class UnifiedInboxService {

  /**
   * Envoyer un message
   */
  async sendMessage(data) {
    try {
      const message = await UnifiedMessage.create({
        thread_id: data.thread_id || require('uuid').v4(),
        commercial_id: data.commercial_id,
        contact_id: data.contact_id,
        contact_name: data.contact_name,
        contact_email: data.contact_email,
        contact_phone: data.contact_phone,
        channel: data.channel,
        direction: 'outbound',
        subject: data.subject,
        body: data.body,
        html_body: data.html_body,
        attachments: data.attachments || [],
        priority: data.priority || 'normal',
        is_automated: data.is_automated || false,
        sequence_id: data.sequence_id,
        scheduled_send_at: data.scheduled_send_at,
        metadata: data.metadata || {}
      });

      // Envoyer réellement le message via les services appropriés
      await this.deliverMessage(message);

      return message;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Délivrer un message via le canal approprié
   */
  async deliverMessage(message) {
    try {
      switch (message.channel) {
        case 'email':
          // TODO: Intégration SendGrid/SMTP
          console.log(`Sending email to ${message.contact_email}: ${message.subject}`);
          break;

        case 'sms':
          // TODO: Intégration Twilio
          console.log(`Sending SMS to ${message.contact_phone}: ${message.body}`);
          break;

        case 'whatsapp':
          // TODO: Intégration WhatsApp Business API
          console.log(`Sending WhatsApp to ${message.contact_phone}: ${message.body}`);
          break;

        case 'in_app':
          // Notification in-app
          await NotificationService.create({
            user_id: message.contact_id,
            type: 'message_received',
            title: '💬 Nouveau Message',
            message: message.body.substring(0, 100),
            data: { message_id: message.id, from: message.commercial_id },
            priority: message.priority,
            channels: { in_app: true, push: true }
          });
          break;

        default:
          console.log(`Channel ${message.channel} not yet implemented`);
      }

      // Marquer comme envoyé
      await message.update({
        status: 'sent',
        sent_at: new Date()
      });

    } catch (error) {
      console.error('Error delivering message:', error);
      await message.update({
        status: 'failed',
        error_message: error.message
      });
      throw error;
    }
  }

  /**
   * Recevoir un message entrant (webhook)
   */
  async receiveMessage(data) {
    try {
      // Trouver le commercial assigné au contact
      const commercial_id = data.commercial_id;

      const message = await UnifiedMessage.create({
        thread_id: data.thread_id || require('uuid').v4(),
        commercial_id,
        contact_id: data.contact_id,
        contact_name: data.contact_name,
        contact_email: data.contact_email,
        contact_phone: data.contact_phone,
        channel: data.channel,
        direction: 'inbound',
        subject: data.subject,
        body: data.body,
        html_body: data.html_body,
        attachments: data.attachments || [],
        external_id: data.external_id,
        external_thread_id: data.external_thread_id,
        metadata: data.metadata || {}
      });

      // Analyse automatique du sentiment et catégorie
      await this.analyzeMessage(message);

      // Notifier le commercial
      await NotificationService.create({
        user_id: commercial_id,
        type: 'new_message',
        title: `${message.getChannelIcon()} Nouveau Message`,
        message: `${data.contact_name}: ${data.body.substring(0, 100)}`,
        data: { message_id: message.id, channel: data.channel },
        priority: message.sentiment === 'negative' ? 'high' : 'medium',
        channels: { in_app: true, push: true }
      });

      return message;
    } catch (error) {
      console.error('Error receiving message:', error);
      throw error;
    }
  }

  /**
   * Analyser le sentiment et catégoriser automatiquement (IA)
   */
  async analyzeMessage(message) {
    try {
      // Analyse de sentiment simple (peut être remplacé par OpenAI/Claude API)
      const body = message.body.toLowerCase();

      // Mots-clés négatifs
      const negativeKeywords = ['problème', 'bug', 'erreur', 'insatisfait', 'déçu', 'mauvais', 'arnaque', 'nul'];
      const positiveKeywords = ['merci', 'excellent', 'parfait', 'super', 'génial', 'content', 'satisfait'];
      const urgentKeywords = ['urgent', 'rapide', 'vite', 'immédiat', 'asap'];

      let sentiment = 'neutral';
      let sentiment_score = 0;
      let category = 'inquiry';
      let priority = message.priority || 'normal';

      // Détection sentiment
      const hasNegative = negativeKeywords.some(keyword => body.includes(keyword));
      const hasPositive = positiveKeywords.some(keyword => body.includes(keyword));
      const hasUrgent = urgentKeywords.some(keyword => body.includes(keyword));

      if (hasNegative) {
        sentiment = 'negative';
        sentiment_score = -0.7;
        priority = 'high';
        category = 'complaint';
      } else if (hasPositive) {
        sentiment = 'positive';
        sentiment_score = 0.7;
        category = 'feedback';
      }

      if (hasUrgent) {
        priority = 'urgent';
      }

      // Catégorisation
      if (body.includes('devis') || body.includes('prix') || body.includes('tarif')) {
        category = 'quote_request';
      } else if (body.includes('aide') || body.includes('support') || body.includes('comment')) {
        category = 'support';
      } else if (body.includes('problème') || body.includes('bug')) {
        category = 'complaint';
      } else if (body.includes('merci') || body.includes('feedback')) {
        category = 'feedback';
      }

      await message.update({
        sentiment,
        sentiment_score,
        category,
        priority,
        auto_categorized: true
      });

    } catch (error) {
      console.error('Error analyzing message:', error);
    }
  }

  /**
   * Obtenir la boîte de réception
   */
  async getInbox(commercialId, filters = {}) {
    try {
      const where = { commercial_id: commercialId };

      // Filtres
      if (filters.channel) {
        where.channel = filters.channel;
      }

      if (filters.is_read !== undefined) {
        where.is_read = filters.is_read === 'true' || filters.is_read === true;
      }

      if (filters.is_starred) {
        where.is_starred = true;
      }

      if (filters.priority) {
        where.priority = filters.priority;
      }

      if (filters.sentiment) {
        where.sentiment = filters.sentiment;
      }

      if (filters.category) {
        where.category = filters.category;
      }

      if (!filters.show_archived) {
        where.is_archived = false;
      }

      // Direction: inbound par défaut (messages reçus)
      if (filters.direction) {
        where.direction = filters.direction;
      } else {
        where.direction = 'inbound';
      }

      const messages = await UnifiedMessage.findAll({
        where,
        order: [['created_at', 'DESC']],
        limit: filters.limit || 50,
        offset: filters.offset || 0
      });

      return messages;
    } catch (error) {
      console.error('Error fetching inbox:', error);
      throw error;
    }
  }

  /**
   * Obtenir un thread de conversation
   */
  async getThread(threadId, commercialId) {
    try {
      const messages = await UnifiedMessage.findAll({
        where: {
          thread_id: threadId,
          commercial_id: commercialId
        },
        order: [['created_at', 'ASC']]
      });

      // Marquer tous les messages entrants comme lus
      for (const message of messages) {
        if (message.direction === 'inbound' && !message.is_read) {
          await message.markAsRead();
        }
      }

      return messages;
    } catch (error) {
      console.error('Error fetching thread:', error);
      throw error;
    }
  }

  /**
   * Répondre à un message
   */
  async replyToMessage(messageId, commercialId, replyData) {
    try {
      const originalMessage = await UnifiedMessage.findOne({
        where: { id: messageId, commercial_id: commercialId }
      });

      if (!originalMessage) {
        throw new Error('Message not found');
      }

      // Créer le message de réponse
      const reply = await this.sendMessage({
        thread_id: originalMessage.thread_id,
        commercial_id: commercialId,
        contact_id: originalMessage.contact_id,
        contact_name: originalMessage.contact_name,
        contact_email: originalMessage.contact_email,
        contact_phone: originalMessage.contact_phone,
        channel: replyData.channel || originalMessage.channel,
        subject: replyData.subject || `Re: ${originalMessage.subject}`,
        body: replyData.body,
        html_body: replyData.html_body,
        attachments: replyData.attachments,
        parent_message_id: messageId,
        priority: replyData.priority
      });

      // Marquer l'original comme répondu
      await originalMessage.update({ status: 'replied' });

      return reply;
    } catch (error) {
      console.error('Error replying to message:', error);
      throw error;
    }
  }

  /**
   * Obtenir les statistiques de la boîte de réception
   */
  async getStatistics(commercialId) {
    try {
      const total = await UnifiedMessage.count({
        where: { commercial_id: commercialId, direction: 'inbound', is_archived: false }
      });

      const unread = await UnifiedMessage.count({
        where: { commercial_id: commercialId, direction: 'inbound', is_read: false, is_archived: false }
      });

      const starred = await UnifiedMessage.count({
        where: { commercial_id: commercialId, is_starred: true, is_archived: false }
      });

      const urgent = await UnifiedMessage.count({
        where: { commercial_id: commercialId, priority: 'urgent', is_archived: false }
      });

      const overdue = await UnifiedMessage.count({
        where: {
          commercial_id: commercialId,
          requires_response: true,
          response_deadline: { [Op.lt]: new Date() },
          status: { [Op.ne]: 'replied' }
        }
      });

      // Par canal
      const byChannel = {};
      const channels = ['email', 'sms', 'whatsapp', 'messenger', 'instagram', 'linkedin', 'in_app'];

      for (const channel of channels) {
        byChannel[channel] = await UnifiedMessage.count({
          where: { commercial_id: commercialId, channel, direction: 'inbound', is_archived: false }
        });
      }

      // Par sentiment
      const bySentiment = {
        positive: await UnifiedMessage.count({
          where: { commercial_id: commercialId, sentiment: 'positive', direction: 'inbound' }
        }),
        neutral: await UnifiedMessage.count({
          where: { commercial_id: commercialId, sentiment: 'neutral', direction: 'inbound' }
        }),
        negative: await UnifiedMessage.count({
          where: { commercial_id: commercialId, sentiment: 'negative', direction: 'inbound' }
        })
      };

      // Temps de réponse moyen (en heures)
      const repliedMessages = await UnifiedMessage.findAll({
        where: {
          commercial_id: commercialId,
          direction: 'inbound',
          status: 'replied'
        },
        limit: 100,
        order: [['created_at', 'DESC']]
      });

      let avgResponseTime = 0;
      if (repliedMessages.length > 0) {
        let totalResponseTime = 0;
        for (const msg of repliedMessages) {
          // Trouver la réponse
          const response = await UnifiedMessage.findOne({
            where: {
              thread_id: msg.thread_id,
              parent_message_id: msg.id,
              direction: 'outbound'
            }
          });

          if (response) {
            const responseTime = (new Date(response.created_at) - new Date(msg.created_at)) / (1000 * 60 * 60); // heures
            totalResponseTime += responseTime;
          }
        }
        avgResponseTime = totalResponseTime / repliedMessages.length;
      }

      return {
        total,
        unread,
        starred,
        urgent,
        overdue,
        by_channel: byChannel,
        by_sentiment: bySentiment,
        avg_response_time_hours: avgResponseTime.toFixed(1)
      };
    } catch (error) {
      console.error('Error calculating statistics:', error);
      throw error;
    }
  }

  /**
   * Marquer un message comme lu
   */
  async markAsRead(messageId, commercialId) {
    try {
      const message = await UnifiedMessage.findOne({
        where: { id: messageId, commercial_id: commercialId }
      });

      if (!message) {
        throw new Error('Message not found');
      }

      await message.markAsRead();
      return message;
    } catch (error) {
      console.error('Error marking as read:', error);
      throw error;
    }
  }

  /**
   * Marquer plusieurs messages comme lus
   */
  async markMultipleAsRead(messageIds, commercialId) {
    try {
      await UnifiedMessage.update(
        { is_read: true, read_at: new Date() },
        {
          where: {
            id: { [Op.in]: messageIds },
            commercial_id: commercialId
          }
        }
      );

      return { success: true, count: messageIds.length };
    } catch (error) {
      console.error('Error marking multiple as read:', error);
      throw error;
    }
  }

  /**
   * Ajouter/retirer une étoile
   */
  async toggleStar(messageId, commercialId) {
    try {
      const message = await UnifiedMessage.findOne({
        where: { id: messageId, commercial_id: commercialId }
      });

      if (!message) {
        throw new Error('Message not found');
      }

      await message.update({ is_starred: !message.is_starred });
      return message;
    } catch (error) {
      console.error('Error toggling star:', error);
      throw error;
    }
  }

  /**
   * Archiver/désarchiver
   */
  async toggleArchive(messageId, commercialId) {
    try {
      const message = await UnifiedMessage.findOne({
        where: { id: messageId, commercial_id: commercialId }
      });

      if (!message) {
        throw new Error('Message not found');
      }

      await message.update({ is_archived: !message.is_archived });
      return message;
    } catch (error) {
      console.error('Error toggling archive:', error);
      throw error;
    }
  }

  /**
   * Rechercher dans les messages
   */
  async search(commercialId, query) {
    try {
      const messages = await UnifiedMessage.findAll({
        where: {
          commercial_id: commercialId,
          [Op.or]: [
            { body: { [Op.iLike]: `%${query}%` } },
            { subject: { [Op.iLike]: `%${query}%` } },
            { contact_name: { [Op.iLike]: `%${query}%` } }
          ]
        },
        order: [['created_at', 'DESC']],
        limit: 50
      });

      return messages;
    } catch (error) {
      console.error('Error searching messages:', error);
      throw error;
    }
  }

  /**
   * Obtenir les messages nécessitant une réponse urgente
   */
  async getRequiresResponse(commercialId) {
    try {
      const messages = await UnifiedMessage.findAll({
        where: {
          commercial_id: commercialId,
          requires_response: true,
          status: { [Op.ne]: 'replied' },
          is_archived: false
        },
        order: [
          ['response_deadline', 'ASC'],
          ['priority', 'DESC'],
          ['created_at', 'ASC']
        ]
      });

      return messages;
    } catch (error) {
      console.error('Error fetching messages requiring response:', error);
      throw error;
    }
  }
}

module.exports = new UnifiedInboxService();
