const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * EmailCampaign - Campaigns marketing automatisées
 * Abandoned cart, Win-back, Newsletters, Promotions
 */
const EmailCampaign = sequelize.define('EmailCampaign', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  merchant_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: { model: 'users', key: 'id' },
    onDelete: 'CASCADE'
  },

  // Campaign info
  name: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  type: {
    type: DataTypes.ENUM(
      'abandoned_cart',
      'win_back',
      'welcome_series',
      'post_purchase',
      'birthday',
      'newsletter',
      'promotion'
    ),
    allowNull: false
  },

  // Email content
  subject: {
    type: DataTypes.STRING(255),
    allowNull: false
  },

  html_body: {
    type: DataTypes.TEXT,
    allowNull: false
  },

  // Trigger config
  trigger_delay_hours: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Délai avant envoi (ex: 24h après abandon)'
  },

  // Targeting
  segment_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: { model: 'customer_segments', key: 'id' }
  },

  // Status
  status: {
    type: DataTypes.ENUM('draft', 'active', 'paused', 'completed'),
    defaultValue: 'draft'
  },

  // Stats
  sent_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  open_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  click_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  conversion_count: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  revenue_generated: {
    type: DataTypes.DECIMAL(10, 2),
    defaultValue: 0
  }
}, {
  tableName: 'email_campaigns',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

module.exports = EmailCampaign;
