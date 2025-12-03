const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

/**
 * Modèle InventoryMovement - Historique des mouvements de stock
 * Traçabilité complète: achat, vente, retour, ajustement, transfert, perte
 */
const InventoryMovement = sequelize.define('InventoryMovement', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },

  // Relation
  inventory_id: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'inventory',
      key: 'id'
    },
    onDelete: 'CASCADE'
  },

  // Type de mouvement
  movement_type: {
    type: DataTypes.ENUM(
      'purchase',      // Achat / Réapprovisionnement
      'sale',          // Vente
      'return',        // Retour client
      'adjustment',    // Ajustement manuel
      'transfer',      // Transfert inter-entrepôts
      'damage',        // Produit endommagé
      'theft',         // Vol / Perte
      'gift',          // Cadeau / Échantillon
      'production'     // Production (si fabrication)
    ),
    allowNull: false
  },

  // Quantités
  quantity: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Quantité déplacée (positif ou négatif)'
  },

  quantity_before: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Quantité avant le mouvement'
  },

  quantity_after: {
    type: DataTypes.INTEGER,
    allowNull: false,
    comment: 'Quantité après le mouvement'
  },

  // Référence
  reference: {
    type: DataTypes.STRING(100),
    allowNull: true,
    comment: 'Order ID, Transfer ID, Invoice ID, etc.'
  },

  // Notes
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },

  // Coût unitaire au moment du mouvement
  unit_cost: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: true
  },

  // Valeur totale du mouvement
  total_value: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: true,
    comment: 'quantity × unit_cost'
  },

  // Utilisateur
  performed_by: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'users',
      key: 'id'
    }
  },

  // Métadonnées additionnelles
  metadata: {
    type: DataTypes.JSONB,
    defaultValue: {},
    comment: 'Données supplémentaires (fournisseur, bon de commande, etc.)'
  }
}, {
  tableName: 'inventory_movements',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false, // Pas d'update, les mouvements sont immuables
  indexes: [
    {
      fields: ['inventory_id', 'created_at'],
      name: 'idx_movements_inventory_date'
    },
    {
      fields: ['movement_type'],
      name: 'idx_movements_type'
    },
    {
      fields: ['reference'],
      name: 'idx_movements_reference'
    },
    {
      fields: ['performed_by'],
      name: 'idx_movements_user'
    },
    {
      fields: ['created_at'],
      name: 'idx_movements_date'
    }
  ]
});

// Associations
InventoryMovement.associate = (models) => {
  InventoryMovement.belongsTo(models.Inventory, {
    foreignKey: 'inventory_id',
    as: 'inventory'
  });

  InventoryMovement.belongsTo(models.User, {
    foreignKey: 'performed_by',
    as: 'user'
  });
};

// Hook before create: calculer total_value
InventoryMovement.beforeCreate((movement) => {
  if (movement.quantity && movement.unit_cost) {
    movement.total_value = Math.abs(movement.quantity) * movement.unit_cost;
  }
});

// Méthodes statiques
InventoryMovement.getRecentMovements = async function(inventoryId, limit = 50) {
  return await InventoryMovement.findAll({
    where: { inventory_id: inventoryId },
    include: ['user'],
    order: [['created_at', 'DESC']],
    limit
  });
};

InventoryMovement.getMovementsByDateRange = async function(inventoryId, startDate, endDate) {
  return await InventoryMovement.findAll({
    where: {
      inventory_id: inventoryId,
      created_at: {
        [sequelize.Sequelize.Op.between]: [startDate, endDate]
      }
    },
    order: [['created_at', 'ASC']]
  });
};

InventoryMovement.getMovementsSummary = async function(inventoryId, startDate, endDate) {
  const movements = await InventoryMovement.findAll({
    where: {
      inventory_id: inventoryId,
      created_at: {
        [sequelize.Sequelize.Op.between]: [startDate, endDate]
      }
    },
    attributes: [
      'movement_type',
      [sequelize.fn('COUNT', sequelize.col('id')), 'count'],
      [sequelize.fn('SUM', sequelize.col('quantity')), 'total_quantity'],
      [sequelize.fn('SUM', sequelize.col('total_value')), 'total_value']
    ],
    group: ['movement_type']
  });

  return movements;
};

module.exports = InventoryMovement;
