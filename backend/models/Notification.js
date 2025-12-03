const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * Modèle Notification - Système de notifications temps réel
 * Support multi-canal: in-app, push, email, SMS
 */
const Notification = sequelize.define('Notification', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Destinataire
  user_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Type de notification
  type: {
    type: DataTypes.ENUM(
      'collaboration_request',      // Demande de collaboration
      'collaboration_accepted',      // Collaboration acceptée
      'collaboration_rejected',      // Collaboration refusée
      'counter_offer',              // Contre-offre reçue
      'payment_received',           // Paiement reçu
      'payment_pending',            // Paiement en attente
      'new_sale',                   // Nouvelle vente
      'new_lead',                   // Nouveau lead
      'lead_hot',                   // Lead devient chaud
      'task_reminder',              // Rappel de tâche
      'contract_signed',            // Contrat signé
      'contract_pending',           // Contrat en attente signature
      'stock_low',                  // Stock bas
      'stock_critical',             // Stock critique
      'product_out_of_stock',       // Rupture de stock
      'new_review',                 // Nouvel avis client
      'review_negative',            // Avis négatif
      'campaign_started',           // Campagne démarrée
      'campaign_ended',             // Campagne terminée
      'quota_reached',              // Quota atteint
      'milestone_achieved',         // Jalon atteint
      'referral_signup',            // Filleul inscrit
      'referral_payment',           // Commission de parrainage
      'live_shopping_starting',     // Live shopping démarre bientôt
      'message_received',           // Nouveau message
      'mention',                    // Mention (@user)
      'system_update',              // Mise à jour système
      'security_alert'              // Alerte sécurité
    ),
    allowNull: false
  },

  // Priorité
  priority: {
    type: DataTypes.ENUM('low', 'medium', 'high', 'urgent'),
    defaultValue: 'medium'
  },

  // Contenu
  title: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  message: {
    type: DataTypes.TEXT,
    allowNull: false
  },

  // Données supplémentaires (JSON)
  data: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Données contextuelles: user_id, product_id, amount, etc.'
  },

  // Action associée (URL ou fonction)
  action_url: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'URL de redirection au clic'
  },

  action_label: {
    type: DataTypes.STRING(100),
    allowNull: true,
    comment: 'Label du bouton action: "Voir", "Accepter", etc.'
  },

  // Canaux de diffusion
  channels: {
    type: DataTypes.JSONB,
    defaultValue: {
      in_app: true,
      push: false,
      email: false,
      sms: false
    }
  },

  // État
  status: {
    type: DataTypes.ENUM('pending', 'sent', 'delivered', 'read', 'failed'),
    defaultValue: 'pending'
  },

  read: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  read_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Métadonnées d'envoi
  sent_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  delivered_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Groupage (pour éviter spam)
  group_key: {
    type: DataTypes.STRING(100),
    allowNull: true,
    comment: 'Clé pour grouper notifications similaires'
  },

  // Expiration
  expires_at: {
    type: DataTypes.DATE,
    allowNull: true,
    comment: 'Date d\'expiration de la notification'
  },

  // Métadonnées
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Métadonnées additionnelles'
  }
}, {
  tableName: 'notifications',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at',
  indexes: [
    {
      fields: ['user_id', 'read', 'created_at'],
      name: 'idx_notifications_user_read_date'
    },
    {
      fields: ['user_id', 'type'],
      name: 'idx_notifications_user_type'
    },
    {
      fields: ['group_key'],
      name: 'idx_notifications_group_key'
    },
    {
      fields: ['status'],
      name: 'idx_notifications_status'
    },
    {
      fields: ['expires_at'],
      name: 'idx_notifications_expires'
    }
  ]
});

// Associations
Notification.associate = (models) => {
  Notification.belongsTo(models.User, {
    foreignKey: 'user_id',
    as: 'user'
  });
};

// Méthodes d'instance
Notification.prototype.markAsRead = async function() {
  this.read = true;
  this.read_at = new Date();
  this.status = 'read';
  await this.save();
  return this;
};

Notification.prototype.markAsSent = async function() {
  this.status = 'sent';
  this.sent_at = new Date();
  await this.save();
  return this;
};

Notification.prototype.markAsDelivered = async function() {
  this.status = 'delivered';
  this.delivered_at = new Date();
  await this.save();
  return this;
};

Notification.prototype.isExpired = function() {
  if (!this.expires_at) return false;
  return new Date() > new Date(this.expires_at);
};

// Méthodes statiques
Notification.getUnreadCount = async function(userId) {
  return await Notification.count({
    where: {
      user_id: userId,
      read: false,
      status: ['delivered', 'sent']
    }
  });
};

Notification.markAllAsRead = async function(userId) {
  return await Notification.update(
    {
      read: true,
      read_at: new Date(),
      status: 'read'
    },
    {
      where: {
        user_id: userId,
        read: false
      }
    }
  );
};

Notification.deleteExpired = async function() {
  const now = new Date();
  return await Notification.destroy({
    where: {
      expires_at: {
        [sequelize.Sequelize.Op.lt]: now
      }
    }
  });
};

module.exports = Notification;
