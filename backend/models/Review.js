const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * Review Model
 * Gestion avancée des avis clients avec modération IA
 * Analyse sentiment, détection spam, réponses automatiques
 */
const Review = sequelize.define('Review', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Produit ou Service évalué
  product_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'products',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  service_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'services',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Marchand (propriétaire du produit/service)
  merchant_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Auteur de l'avis
  customer_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'SET NULL'
  },

  customer_name: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  customer_email: {
    type: DataTypes.STRING(255),
    allowNull: true
  },

  // Commande associée (pour vérifier achat)
  order_id: {
    type: DataTypes.UUID,
    allowNull: true
  },

  verified_purchase: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Avis d\'un acheteur vérifié'
  },

  // Note et contenu
  rating: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1,
      max: 5
    }
  },

  title: {
    type: DataTypes.STRING(255),
    allowNull: true
  },

  comment: {
    type: DataTypes.TEXT,
    allowNull: false
  },

  // Médias joints (photos/vidéos)
  images: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'URLs des images jointes'
  },

  videos: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'URLs des vidéos jointes'
  },

  // Statut de modération
  status: {
    type: DataTypes.ENUM(
      'pending',      // En attente de modération
      'approved',     // Approuvé et publié
      'rejected',     // Rejeté
      'flagged',      // Signalé pour révision manuelle
      'spam'          // Détecté comme spam
    ),
    defaultValue: 'pending'
  },

  // Modération automatique (IA)
  auto_moderated: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  moderation_score: {
    type: DataTypes.FLOAT,
    allowNull: true,
    comment: 'Score de confiance de la modération IA (0-1)'
  },

  moderation_reason: {
    type: DataTypes.TEXT,
    allowNull: true,
    comment: 'Raison du rejet/signalement'
  },

  // Analyse de sentiment (IA)
  sentiment: {
    type: DataTypes.ENUM('very_negative', 'negative', 'neutral', 'positive', 'very_positive'),
    allowNull: true
  },

  sentiment_score: {
    type: DataTypes.FLOAT,
    allowNull: true,
    comment: 'Score de -1 (très négatif) à +1 (très positif)'
  },

  // Détection de problèmes (IA)
  detected_issues: {
    type: DataTypes.JSONB,
    defaultValue: [],
    comment: 'Problèmes détectés: [quality, delivery, customer_service, price, etc.]'
  },

  is_spam: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  spam_score: {
    type: DataTypes.FLOAT,
    defaultValue: 0,
    comment: 'Probabilité de spam (0-1)'
  },

  contains_profanity: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  // Réponse du marchand
  has_response: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  response_text: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  response_date: {
    type: DataTypes.DATE,
    allowNull: true
  },

  auto_response: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Réponse générée automatiquement par IA'
  },

  // Visibilité et mise en avant
  is_featured: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Avis mis en avant (très positif avec photos)'
  },

  is_visible: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },

  // Interaction avec l'avis
  helpful_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Nombre de "Utile"'
  },

  not_helpful_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  report_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Nombre de signalements'
  },

  // Source de l'avis
  source: {
    type: DataTypes.ENUM('website', 'email_request', 'google', 'facebook', 'trustpilot', 'import'),
    defaultValue: 'website'
  },

  external_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    comment: 'ID sur plateforme externe si importé'
  },

  // Langue et traduction
  language: {
    type: DataTypes.STRING(10),
    defaultValue: 'fr'
  },

  translated_comment: {
    type: DataTypes.TEXT,
    allowNull: true,
    comment: 'Traduction automatique si langue différente'
  },

  // Modération manuelle
  moderated_by: {
    type: DataTypes.UUID,
    allowNull: true,
    comment: 'ID du modérateur si modération manuelle'
  },

  moderated_at: {
    type: DataTypes.DATE,
    allowNull: true
  },

  moderation_notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  // Metadata
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Données additionnelles (IP, user agent, etc.)'
  }

}, {
  tableName: 'reviews',
  timestamps: true,
  underscored: true,
  indexes: [
    { fields: ['product_id'] },
    { fields: ['service_id'] },
    { fields: ['merchant_id'] },
    { fields: ['customer_id'] },
    { fields: ['status'] },
    { fields: ['rating'] },
    { fields: ['sentiment'] },
    { fields: ['verified_purchase'] },
    { fields: ['merchant_id', 'status'] },
    { fields: ['merchant_id', 'rating'] },
    { fields: ['is_featured'] },
    { fields: ['created_at'] }
  ]
});

// Méthodes d'instance
Review.prototype.isPositive = function() {
  return this.rating >= 4;
};

Review.prototype.isNegative = function() {
  return this.rating <= 2;
};

Review.prototype.requiresAttention = function() {
  return (
    this.isNegative() ||
    this.status === 'flagged' ||
    this.report_count >= 3 ||
    (!this.has_response && this.created_at < new Date(Date.now() - 24 * 60 * 60 * 1000))
  );
};

Review.prototype.shouldBeFeatured = function() {
  return (
    this.rating === 5 &&
    this.sentiment === 'very_positive' &&
    (this.images.length > 0 || this.comment.length > 100) &&
    this.verified_purchase &&
    this.status === 'approved'
  );
};

// Hooks
Review.beforeCreate((review) => {
  // Si note 5 avec images et commentaire long, suggérer featured
  if (review.shouldBeFeatured()) {
    review.is_featured = true;
  }
});

Review.afterCreate(async (review) => {
  // Calculer la nouvelle moyenne des notes du produit/service
  // TODO: Mettre à jour le rating moyen du produit/service
});

module.exports = Review;
