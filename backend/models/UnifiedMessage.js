const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * UnifiedMessage Model
 * Unified Inbox - Tous les messages commerciaux en un seul endroit
 * Support: Email, SMS, WhatsApp, In-App, Social Media DMs
 */
const UnifiedMessage = sequelize.define('UnifiedMessage', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Thread/Conversation ID pour grouper les messages
  thread_id: {
    type: DataTypes.UUID,
    allowNull: false,
    comment: 'ID du fil de conversation'
  },

  // Commercial assigné
  commercial_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Lead/Contact associé
  contact_id: {
    type: DataTypes.UUID,
    allowNull: true,
    comment: 'ID du lead ou contact'
  },

  contact_name: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  contact_email: {
    type: DataTypes.STRING(255),
    allowNull: true
  },

  contact_phone: {
    type: DataTypes.STRING(50),
    allowNull: true
  },

  // Canal de communication
  channel: {
    type: DataTypes.ENUM(
      'email',
      'sms',
      'whatsapp',
      'messenger',
      'instagram',
      'linkedin',
      'twitter',
      'in_app',
      'phone'
    ),
    allowNull: false
  },

  // Direction du message
  direction: {
    type: DataTypes.ENUM('inbound', 'outbound'),
    allowNull: false,
    comment: 'Message reçu ou envoyé'
  },

  // Contenu du message
  subject: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'Sujet (email uniquement)'
  },

  body: {
    type: DataTypes.TEXT,
    allowNull: false
  },

  html_body: {
    type: DataTypes.TEXT,
    allowNull: true,
    comment: 'Version HTML du message (email)'
  },

  // Pièces jointes
  attachments: {
    type: DataTypes.JSONB,
    defaultValue: [],
    comment: 'Liste des fichiers attachés'
  },

  // Statut du message
  status: {
    type: DataTypes.ENUM(
      'pending',      // En attente d'envoi
      'sent',         // Envoyé
      'delivered',    // Délivré
      'read',         // Lu
      'replied',      // Répondu
      'failed',       // Échec
      'bounced'       // Rebondi (email)
    ),
    defaultValue: 'sent'
  },

  // État de lecture
  is_read: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  read_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Marquage/Organisation
  is_starred: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  is_archived: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  tags: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'Tags pour organisation'
  },

  // Priorité
  priority: {
    type: DataTypes.ENUM('low', 'normal', 'high', 'urgent'),
    defaultValue: 'normal'
  },

  // Réponse attendue
  requires_response: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  response_deadline: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Sentiment Analysis (IA)
  sentiment: {
    type: DataTypes.ENUM('positive', 'neutral', 'negative'),
    allowNull: true,
    comment: 'Analyse automatique du sentiment'
  },

  sentiment_score: {
    type: DataTypes.FLOAT,
    allowNull: true,
    comment: 'Score de -1 (négatif) à +1 (positif)'
  },

  // Catégorisation automatique (IA)
  category: {
    type: DataTypes.ENUM(
      'inquiry',          // Demande d'information
      'complaint',        // Réclamation
      'follow_up',        // Suivi
      'quote_request',    // Demande de devis
      'support',          // Support technique
      'feedback',         // Feedback
      'other'
    ),
    allowNull: true
  },

  auto_categorized: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Catégorisé automatiquement par IA'
  },

  // Données externes
  external_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    comment: 'ID du message sur la plateforme externe'
  },

  external_thread_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    comment: 'ID du thread sur la plateforme externe'
  },

  // Message parent (pour les réponses)
  parent_message_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'unified_messages',
      key: 'id'
    }
  },

  // Tracking
  opened_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Nombre de fois que l\'email a été ouvert'
  },

  clicked_links: {
    type: DataTypes.JSONB,
    defaultValue: [],
    comment: 'URLs cliquées dans le message'
  },

  // Automatisation
  is_automated: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Message envoyé automatiquement (séquence)'
  },

  sequence_id: {
    type: DataTypes.UUID,
    allowNull: true,
    comment: 'ID de la séquence email si automatisé'
  },

  // Scheduled sending
  scheduled_send_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  sent_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Metadata
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Métadonnées additionnelles (headers email, etc.)'
  },

  // Erreur (si échec)
  error_message: {
    type: DataTypes.TEXT,
    allowNull: true
  }

}, {
  tableName: 'unified_messages',
  timestamps: true,
  underscored: true,
  indexes: [
    { fields: ['thread_id'] },
    { fields: ['commercial_id'] },
    { fields: ['contact_id'] },
    { fields: ['channel'] },
    { fields: ['status'] },
    { fields: ['is_read'] },
    { fields: ['is_starred'] },
    { fields: ['priority'] },
    { fields: ['sentiment'] },
    { fields: ['category'] },
    { fields: ['commercial_id', 'is_read'] },
    { fields: ['commercial_id', 'channel'] },
    { fields: ['thread_id', 'created_at'] }
  ]
});

// Méthodes d'instance
UnifiedMessage.prototype.markAsRead = async function() {
  if (!this.is_read) {
    this.is_read = true;
    this.read_at = new Date();
    await this.save();
  }
};

UnifiedMessage.prototype.isOverdue = function() {
  return this.requires_response &&
         this.response_deadline &&
         new Date(this.response_deadline) < new Date() &&
         this.status !== 'replied';
};

UnifiedMessage.prototype.getChannelIcon = function() {
  const icons = {
    email: '📧',
    sms: '💬',
    whatsapp: '📱',
    messenger: '💙',
    instagram: '📷',
    linkedin: '💼',
    twitter: '🐦',
    in_app: '💻',
    phone: '☎️'
  };
  return icons[this.channel] || '📩';
};

// Hooks
UnifiedMessage.beforeCreate((message) => {
  // Si pas de thread_id, créer un nouveau thread
  if (!message.thread_id) {
    message.thread_id = DataTypes.UUIDV4;
  }

  // Marquer l'heure d'envoi pour les messages sortants
  if (message.direction === 'outbound' && !message.sent_at) {
    message.sent_at = new Date();
  }
});

module.exports = UnifiedMessage;
