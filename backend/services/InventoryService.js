const Inventory = require('../models/Inventory');
const InventoryMovement = require('../models/InventoryMovement');
const Product = require('../models/Product');
const NotificationService = require('./NotificationService');
const { Op } = require('sequelize');

/**
 * InventoryService - Gestion avancée des stocks
 * Features: Tracking temps réel, Alertes auto, Prédictions ML
 */
class InventoryService {

  /**
   * Créer un item d'inventaire
   */
  async create(data) {
    const {
      product_id,
      merchant_id,
      sku,
      quantity_available = 0,
      alert_threshold = 10,
      critical_threshold = 5,
      reorder_point = 20,
      reorder_quantity = 100,
      variant_type,
      variant_value,
      cost_price,
      selling_price,
      warehouse_id,
      location
    } = data;

    const inventory = await Inventory.create({
      product_id,
      merchant_id,
      sku,
      quantity_available,
      alert_threshold,
      critical_threshold,
      reorder_point,
      reorder_quantity,
      variant_type,
      variant_value,
      cost_price,
      selling_price,
      warehouse_id,
      location
    });

    // Créer le mouvement initial si quantity > 0
    if (quantity_available > 0) {
      await this.createMovement({
        inventory_id: inventory.id,
        movement_type: 'purchase',
        quantity: quantity_available,
        quantity_before: 0,
        quantity_after: quantity_available,
        unit_cost: cost_price,
        notes: 'Stock initial'
      });
    }

    return inventory;
  }

  /**
   * Ajouter du stock (achat, retour client, etc.)
   */
  async addStock(inventoryId, quantity, data = {}) {
    const {
      movement_type = 'purchase',
      reference,
      notes,
      unit_cost,
      performed_by
    } = data;

    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) {
      throw new Error('Inventory not found');
    }

    const quantityBefore = inventory.quantity_available;
    const quantityAfter = quantityBefore + quantity;

    // Mettre à jour le stock
    inventory.quantity_available = quantityAfter;

    if (movement_type === 'purchase') {
      inventory.last_restock_date = new Date().toISOString().split('T')[0];
    }

    await inventory.save();

    // Créer le mouvement
    await this.createMovement({
      inventory_id: inventoryId,
      movement_type,
      quantity,
      quantity_before: quantityBefore,
      quantity_after: quantityAfter,
      reference,
      notes,
      unit_cost: unit_cost || inventory.cost_price,
      performed_by
    });

    // Re-calculer les prédictions
    await this.updatePredictions(inventoryId);

    return inventory;
  }

  /**
   * Retirer du stock (vente, perte, etc.)
   */
  async removeStock(inventoryId, quantity, data = {}) {
    const {
      movement_type = 'sale',
      reference,
      notes,
      performed_by
    } = data;

    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) {
      throw new Error('Inventory not found');
    }

    if (inventory.quantity_available < quantity) {
      throw new Error('Insufficient stock');
    }

    const quantityBefore = inventory.quantity_available;
    const quantityAfter = quantityBefore - quantity;

    // Mettre à jour le stock
    inventory.quantity_available = quantityAfter;

    if (movement_type === 'sale') {
      inventory.quantity_sold += quantity;
    }

    // Si rupture de stock
    if (quantityAfter === 0) {
      inventory.last_stockout_date = new Date().toISOString().split('T')[0];

      // Notification
      const product = await Product.findByPk(inventory.product_id);
      await NotificationService.create({
        user_id: inventory.merchant_id,
        type: 'product_out_of_stock',
        title: '📦 Rupture de Stock',
        message: `${product.name} est en rupture de stock`,
        priority: 'urgent',
        data: {
          product_id: product.id,
          product_name: product.name,
          inventory_id: inventoryId
        },
        action_url: '/inventory',
        action_label: 'Réapprovisionner',
        channels: {
          in_app: true,
          push: true,
          email: true,
          sms: false
        }
      });
    }

    await inventory.save();

    // Créer le mouvement
    await this.createMovement({
      inventory_id: inventoryId,
      movement_type,
      quantity: -quantity,
      quantity_before: quantityBefore,
      quantity_after: quantityAfter,
      reference,
      notes,
      unit_cost: inventory.cost_price,
      performed_by
    });

    // Vérifier les alertes
    await this.checkAlerts(inventory);

    // Re-calculer les prédictions
    await this.updatePredictions(inventoryId);

    return inventory;
  }

  /**
   * Réserver du stock (commande en attente)
   */
  async reserveStock(inventoryId, quantity) {
    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) {
      throw new Error('Inventory not found');
    }

    if (inventory.quantity_available < quantity) {
      throw new Error('Insufficient stock to reserve');
    }

    inventory.quantity_available -= quantity;
    inventory.quantity_reserved += quantity;
    await inventory.save();

    return inventory;
  }

  /**
   * Libérer le stock réservé (commande annulée)
   */
  async releaseReservedStock(inventoryId, quantity) {
    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) {
      throw new Error('Inventory not found');
    }

    if (inventory.quantity_reserved < quantity) {
      throw new Error('Cannot release more than reserved');
    }

    inventory.quantity_reserved -= quantity;
    inventory.quantity_available += quantity;
    await inventory.save();

    return inventory;
  }

  /**
   * Créer un mouvement d'inventaire
   */
  async createMovement(data) {
    return await InventoryMovement.create(data);
  }

  /**
   * Vérifier et envoyer les alertes de stock
   */
  async checkAlerts(inventory) {
    const product = await Product.findByPk(inventory.product_id);

    // Stock critique
    if (inventory.isCriticalStock()) {
      await NotificationService.notifyLowStock(
        inventory.merchant_id,
        product.name,
        inventory.quantity_available,
        inventory.critical_threshold
      );
      return 'critical';
    }

    // Stock bas
    if (inventory.isLowStock()) {
      await NotificationService.notifyLowStock(
        inventory.merchant_id,
        product.name,
        inventory.quantity_available,
        inventory.alert_threshold
      );
      return 'low';
    }

    return 'ok';
  }

  /**
   * Scanner automatique des stocks bas (Cron Job)
   */
  async scanLowStock(merchantId = null) {
    const where = {};
    if (merchantId) {
      where.merchant_id = merchantId;
    }

    const lowStockItems = await Inventory.findAll({
      where: {
        ...where,
        quantity_available: {
          [Op.lte]: Inventory.sequelize.literal('alert_threshold')
        }
      },
      include: ['product', 'merchant']
    });

    console.log(`[Inventory] Found ${lowStockItems.length} low stock items`);

    for (const item of lowStockItems) {
      await this.checkAlerts(item);
    }

    return lowStockItems;
  }

  /**
   * Mettre à jour les prédictions ML (simplifié)
   */
  async updatePredictions(inventoryId) {
    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) return;

    // Obtenir les ventes des 30 derniers jours
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const movements = await InventoryMovement.findAll({
      where: {
        inventory_id: inventoryId,
        movement_type: 'sale',
        created_at: {
          [Op.gte]: thirtyDaysAgo
        }
      }
    });

    // Calculer la demande moyenne
    const totalSold = movements.reduce((sum, m) => sum + Math.abs(m.quantity), 0);
    const dailyDemand = totalSold / 30;
    const weeklyDemand = dailyDemand * 7;

    inventory.predicted_demand_weekly = Math.ceil(weeklyDemand);

    // Prédire la date de rupture de stock
    if (dailyDemand > 0 && inventory.quantity_available > 0) {
      const daysUntilStockout = Math.floor(inventory.quantity_available / dailyDemand);
      const stockoutDate = new Date();
      stockoutDate.setDate(stockoutDate.getDate() + daysUntilStockout);
      inventory.predicted_stockout_date = stockoutDate.toISOString().split('T')[0];
    } else {
      inventory.predicted_stockout_date = null;
    }

    await inventory.save();

    return inventory;
  }

  /**
   * Obtenir le dashboard de l'inventaire pour un marchand
   */
  async getDashboard(merchantId) {
    // Total items
    const totalItems = await Inventory.count({
      where: { merchant_id: merchantId }
    });

    // Stock bas
    const lowStockItems = await Inventory.getLowStockItems(merchantId);

    // Stock critique
    const criticalStockItems = await Inventory.getCriticalStockItems(merchantId);

    // Valeur totale du stock
    const stockValue = await Inventory.getStockValue(merchantId);

    // Items nécessitant réapprovisionnement
    const reorderItems = await Inventory.findAll({
      where: {
        merchant_id: merchantId,
        quantity_available: {
          [Op.lte]: Inventory.sequelize.literal('reorder_point')
        }
      },
      include: ['product']
    });

    // Mouvements récents (7 jours)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const recentMovements = await InventoryMovement.findAll({
      include: [{
        model: Inventory,
        as: 'inventory',
        where: { merchant_id: merchantId },
        include: ['product']
      }],
      where: {
        created_at: {
          [Op.gte]: sevenDaysAgo
        }
      },
      order: [['created_at', 'DESC']],
      limit: 50
    });

    // Top 10 produits à risque (rupture prévue bientôt)
    const atRiskProducts = await Inventory.findAll({
      where: {
        merchant_id: merchantId,
        predicted_stockout_date: {
          [Op.ne]: null,
          [Op.lte]: Inventory.sequelize.literal("CURRENT_DATE + INTERVAL '14 days'")
        }
      },
      include: ['product'],
      order: [['predicted_stockout_date', 'ASC']],
      limit: 10
    });

    return {
      summary: {
        total_items: totalItems,
        low_stock_count: lowStockItems.length,
        critical_stock_count: criticalStockItems.length,
        reorder_needed_count: reorderItems.length,
        total_stock_cost: parseFloat(stockValue.total_cost || 0),
        total_stock_value: parseFloat(stockValue.total_value || 0)
      },
      low_stock_items: lowStockItems,
      critical_stock_items: criticalStockItems,
      reorder_items: reorderItems,
      recent_movements: recentMovements,
      at_risk_products: atRiskProducts
    };
  }

  /**
   * Obtenir l'historique des mouvements
   */
  async getMovements(inventoryId, options = {}) {
    const {
      start_date,
      end_date,
      movement_type,
      limit = 100,
      offset = 0
    } = options;

    const where = { inventory_id: inventoryId };

    if (start_date && end_date) {
      where.created_at = {
        [Op.between]: [start_date, end_date]
      };
    }

    if (movement_type) {
      where.movement_type = movement_type;
    }

    const movements = await InventoryMovement.findAll({
      where,
      include: ['user'],
      order: [['created_at', 'DESC']],
      limit,
      offset
    });

    return movements;
  }

  /**
   * Ajuster manuellement le stock (inventaire physique)
   */
  async adjustStock(inventoryId, newQuantity, data = {}) {
    const { notes, performed_by } = data;

    const inventory = await Inventory.findByPk(inventoryId);
    if (!inventory) {
      throw new Error('Inventory not found');
    }

    const quantityBefore = inventory.quantity_available;
    const difference = newQuantity - quantityBefore;

    inventory.quantity_available = newQuantity;
    await inventory.save();

    // Créer le mouvement d'ajustement
    await this.createMovement({
      inventory_id: inventoryId,
      movement_type: 'adjustment',
      quantity: difference,
      quantity_before: quantityBefore,
      quantity_after: newQuantity,
      notes: notes || 'Ajustement manuel après inventaire physique',
      unit_cost: inventory.cost_price,
      performed_by
    });

    // Vérifier les alertes
    await this.checkAlerts(inventory);

    return inventory;
  }
}

module.exports = new InventoryService();
