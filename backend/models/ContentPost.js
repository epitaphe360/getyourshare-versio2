const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * ContentPost Model
 * Gestion du calendrier éditorial pour influenceurs
 * Permet de planifier, organiser et suivre les contenus sur différentes plateformes
 */
const ContentPost = sequelize.define('ContentPost', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Influencer qui crée le post
  influencer_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Campagne associée (optionnel)
  campaign_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'campaigns',
      key: 'id'
    },
    onDelete: 'SET NULL'
  },

  // Informations du post
  title: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  content: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  // Plateforme sociale
  platform: {
    type: DataTypes.ENUM(
      'instagram',
      'facebook',
      'twitter',
      'tiktok',
      'youtube',
      'linkedin',
      'pinterest',
      'snapchat',
      'blog'
    ),
    allowNull: false
  },

  // Type de contenu
  content_type: {
    type: DataTypes.ENUM(
      'post',
      'story',
      'reel',
      'video',
      'carousel',
      'live',
      'igtv',
      'article',
      'short'
    ),
    defaultValue: 'post'
  },

  // Statut du post
  status: {
    type: DataTypes.ENUM(
      'draft',        // Brouillon
      'scheduled',    // Programmé
      'published',    // Publié
      'failed',       // Échec publication
      'archived'      // Archivé
    ),
    defaultValue: 'draft'
  },

  // Dates
  scheduled_date: {
    type: DataTypes.DATE,
    allowNull: true,
    comment: 'Date de publication programmée'
  },

  published_date: {
    type: DataTypes.DATE,
    allowNull: true,
    comment: 'Date de publication réelle'
  },

  // Médias attachés
  media_urls: {
    type: DataTypes.JSONB,
    defaultValue: [],
    comment: 'URLs des images/vidéos à publier'
  },

  thumbnail_url: {
    type: DataTypes.STRING(500),
    allowNull: true
  },

  // Hashtags et mentions
  hashtags: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'Liste des hashtags'
  },

  mentions: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    defaultValue: [],
    comment: 'Liste des @mentions'
  },

  // Call to action
  cta_type: {
    type: DataTypes.ENUM('link', 'shop', 'swipe_up', 'none'),
    defaultValue: 'none'
  },

  cta_url: {
    type: DataTypes.STRING(500),
    allowNull: true
  },

  // Tracking & Analytics
  tracking_link: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'Lien de tracking affilié'
  },

  post_url: {
    type: DataTypes.STRING(500),
    allowNull: true,
    comment: 'URL du post publié'
  },

  external_id: {
    type: DataTypes.STRING(255),
    allowNull: true,
    comment: 'ID du post sur la plateforme externe'
  },

  // Métriques de performance
  views: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  likes: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  comments: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  shares: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  clicks: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Clics sur le lien de tracking'
  },

  engagement_rate: {
    type: DataTypes.FLOAT,
    defaultValue: 0,
    comment: 'Taux d\'engagement en %'
  },

  revenue_generated: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0,
    comment: 'Revenus générés par ce post'
  },

  // Collaboration
  is_sponsored: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  brand_name: {
    type: DataTypes.STRING(255),
    allowNull: true
  },

  commission_rate: {
    type: DataTypes.FLOAT,
    allowNull: true,
    comment: 'Taux de commission en %'
  },

  // Publication automatique
  auto_publish: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    comment: 'Publier automatiquement à la date programmée'
  },

  publish_attempts: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  last_publish_error: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  // Notes et rappels
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  reminder_sent: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },

  reminder_date: {
    type: DataTypes.DATE,
    allowNull: true
  },

  // Metadata
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Données additionnelles (géolocalisation, produits taggés, etc.)'
  }

}, {
  tableName: 'content_posts',
  timestamps: true,
  underscored: true,
  indexes: [
    { fields: ['influencer_id'] },
    { fields: ['campaign_id'] },
    { fields: ['platform'] },
    { fields: ['status'] },
    { fields: ['scheduled_date'] },
    { fields: ['published_date'] },
    { fields: ['influencer_id', 'scheduled_date'] },
    { fields: ['influencer_id', 'status'] }
  ]
});

// Méthodes d'instance
ContentPost.prototype.canPublish = function() {
  return this.status === 'scheduled' &&
         this.scheduled_date &&
         new Date(this.scheduled_date) <= new Date();
};

ContentPost.prototype.calculateEngagementRate = function() {
  if (this.views === 0) return 0;
  const totalEngagements = this.likes + this.comments + this.shares;
  return (totalEngagements / this.views) * 100;
};

ContentPost.prototype.isOverdue = function() {
  return this.status === 'scheduled' &&
         this.scheduled_date &&
         new Date(this.scheduled_date) < new Date();
};

// Hooks
ContentPost.beforeUpdate((post) => {
  // Recalculer l'engagement rate automatiquement
  if (post.changed('likes') || post.changed('comments') || post.changed('shares') || post.changed('views')) {
    post.engagement_rate = post.calculateEngagementRate();
  }

  // Si publié, enregistrer la date
  if (post.changed('status') && post.status === 'published' && !post.published_date) {
    post.published_date = new Date();
  }
});

module.exports = ContentPost;
