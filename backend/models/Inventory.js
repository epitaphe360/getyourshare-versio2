const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * Modèle Inventory - Gestion avancée des stocks
 * Features: Multi-variants, Alertes automatiques, Prédictions ML
 */
const Inventory = sequelize.define('Inventory', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Relations
  product_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'products',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  merchant_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Stock
  sku: {
    type: DataTypes.STRING(100),
    unique: true,
    allowNull: true
  },

  quantity_available: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    validate: {
      min: 0
    }
  },

  quantity_reserved: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    validate: {
      min: 0
    }
  },

  quantity_sold: {
    type: DataTypes.INTEGER,
    defaultValue: 0
  },

  // Seuils d'alerte
  alert_threshold: {
    type: DataTypes.INTEGER,
    defaultValue: 10,
    comment: 'Seuil pour alerte stock bas'
  },

  critical_threshold: {
    type: DataTypes.INTEGER,
    defaultValue: 5,
    comment: 'Seuil critique nécessitant action immédiate'
  },

  reorder_point: {
    type: DataTypes.INTEGER,
    defaultValue: 20,
    comment: 'Point de réapprovisionnement recommandé'
  },

  reorder_quantity: {
    type: DataTypes.INTEGER,
    defaultValue: 100,
    comment: 'Quantité recommandée à commander'
  },

  // Variants (taille, couleur, etc.)
  variant_type: {
    type: DataTypes.STRING(50),
    allowNull: true,
    comment: 'Type: size, color, style, etc.'
  },

  variant_value: {
    type: DataTypes.STRING(100),
    allowNull: true,
    comment: 'Valeur: S, M, L, Rouge, Bleu, etc.'
  },

  // Localisation
  warehouse_id: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'warehouses',
      key: 'id'
    }
  },

  location: {
    type: DataTypes.STRING(100),
    allowNull: true,
    comment: 'Ex: Zone A - Étagère 12'
  },

  // Coûts & Prix
  cost_price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: true,
    comment: 'Prix de revient'
  },

  selling_price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: true,
    comment: 'Prix de vente'
  },

  // Prédictions IA (Machine Learning)
  predicted_stockout_date: {
    type: DataTypes.DATEONLY,
    allowNull: true,
    comment: 'Date prévue de rupture de stock (ML)'
  },

  predicted_demand_weekly: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    comment: 'Demande hebdomadaire prédite (ML)'
  },

  // Historique
  last_restock_date: {
    type: DataTypes.DATEONLY,
    allowNull: true
  },

  last_stockout_date: {
    type: DataTypes.DATEONLY,
    allowNull: true
  },

  // Métadonnées
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {}
  }
}, {
  tableName: 'inventory',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at',
  indexes: [
    {
      fields: ['product_id'],
      name: 'idx_inventory_product'
    },
    {
      fields: ['merchant_id'],
      name: 'idx_inventory_merchant'
    },
    {
      fields: ['sku'],
      name: 'idx_inventory_sku',
      unique: true,
      where: { sku: { [sequelize.Sequelize.Op.ne]: null } }
    },
    {
      fields: ['quantity_available'],
      name: 'idx_inventory_low_stock',
      where: sequelize.literal('quantity_available < alert_threshold')
    }
  ]
});

// Associations
Inventory.associate = (models) => {
  Inventory.belongsTo(models.Product, {
    foreignKey: 'product_id',
    as: 'product'
  });

  Inventory.belongsTo(models.User, {
    foreignKey: 'merchant_id',
    as: 'merchant'
  });

  Inventory.hasMany(models.InventoryMovement, {
    foreignKey: 'inventory_id',
    as: 'movements'
  });

  if (models.Warehouse) {
    Inventory.belongsTo(models.Warehouse, {
      foreignKey: 'warehouse_id',
      as: 'warehouse'
    });
  }
};

// Méthodes d'instance
Inventory.prototype.getTotalStock = function() {
  return this.quantity_available + this.quantity_reserved;
};

Inventory.prototype.isLowStock = function() {
  return this.quantity_available <= this.alert_threshold;
};

Inventory.prototype.isCriticalStock = function() {
  return this.quantity_available <= this.critical_threshold;
};

Inventory.prototype.needsReorder = function() {
  return this.quantity_available <= this.reorder_point;
};

Inventory.prototype.getDaysUntilStockout = function() {
  if (!this.predicted_stockout_date) return null;

  const today = new Date();
  const stockoutDate = new Date(this.predicted_stockout_date);
  const diffTime = stockoutDate - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  return diffDays;
};

Inventory.prototype.getStockStatus = function() {
  if (this.quantity_available === 0) return 'out_of_stock';
  if (this.isCriticalStock()) return 'critical';
  if (this.isLowStock()) return 'low';
  if (this.needsReorder()) return 'reorder';
  return 'ok';
};

// Méthodes statiques
Inventory.getLowStockItems = async function(merchantId) {
  return await Inventory.findAll({
    where: {
      merchant_id: merchantId,
      quantity_available: {
        [sequelize.Sequelize.Op.lte]: sequelize.literal('alert_threshold')
      }
    },
    include: ['product'],
    order: [['quantity_available', 'ASC']]
  });
};

Inventory.getCriticalStockItems = async function(merchantId) {
  return await Inventory.findAll({
    where: {
      merchant_id: merchantId,
      quantity_available: {
        [sequelize.Sequelize.Op.lte]: sequelize.literal('critical_threshold')
      }
    },
    include: ['product'],
    order: [['quantity_available', 'ASC']]
  });
};

Inventory.getStockValue = async function(merchantId) {
  const items = await Inventory.findAll({
    where: { merchant_id: merchantId },
    attributes: [
      [sequelize.fn('SUM', sequelize.literal('quantity_available * cost_price')), 'total_cost'],
      [sequelize.fn('SUM', sequelize.literal('quantity_available * selling_price')), 'total_value']
    ]
  });

  return items[0] || { total_cost: 0, total_value: 0 };
};

module.exports = Inventory;
