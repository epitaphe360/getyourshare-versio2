const express = require('express');
const router = express.Router();
const { authenticateToken, checkRole } = require('../middleware/auth');
const InventoryService = require('../services/InventoryService');
const Inventory = require('../models/Inventory');

/**
 * Routes API Inventory Management
 * Gestion avancée des stocks avec alertes et prédictions ML
 */

/**
 * GET /api/inventory/dashboard
 * Dashboard complet de l'inventaire pour un marchand
 */
router.get('/dashboard', authenticateToken, checkRole(['merchant', 'admin']), async (req, res) => {
  try {
    const merchantId = req.user.role === 'admin' ? req.query.merchant_id : req.user.id;

    if (!merchantId) {
      return res.status(400).json({
        success: false,
        message: 'Merchant ID required'
      });
    }

    const dashboard = await InventoryService.getDashboard(merchantId);

    res.json({
      success: true,
      dashboard
    });
  } catch (error) {
    console.error('Error fetching inventory dashboard:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching inventory dashboard',
      error: error.message
    });
  }
});

/**
 * GET /api/inventory
 * Liste des items d'inventaire
 */
router.get('/', authenticateToken, checkRole(['merchant', 'admin']), async (req, res) => {
  try {
    const merchantId = req.user.role === 'admin' ? req.query.merchant_id : req.user.id;
    const {
      status, // 'low', 'critical', 'reorder', 'ok'
      product_id,
      warehouse_id,
      limit = 100,
      offset = 0
    } = req.query;

    const where = {};
    if (merchantId) where.merchant_id = merchantId;
    if (product_id) where.product_id = product_id;
    if (warehouse_id) where.warehouse_id = warehouse_id;

    // Filter by status
    if (status) {
      const { Op } = require('sequelize');
      switch (status) {
        case 'low':
          where.quantity_available = {
            [Op.lte]: Inventory.sequelize.literal('alert_threshold')
          };
          break;
        case 'critical':
          where.quantity_available = {
            [Op.lte]: Inventory.sequelize.literal('critical_threshold')
          };
          break;
        case 'reorder':
          where.quantity_available = {
            [Op.lte]: Inventory.sequelize.literal('reorder_point')
          };
          break;
        case 'out':
          where.quantity_available = 0;
          break;
      }
    }

    const items = await Inventory.findAll({
      where,
      include: ['product'],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['updated_at', 'DESC']]
    });

    const total = await Inventory.count({ where });

    res.json({
      success: true,
      items,
      total,
      limit: parseInt(limit),
      offset: parseInt(offset)
    });
  } catch (error) {
    console.error('Error fetching inventory:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching inventory',
      error: error.message
    });
  }
});

/**
 * GET /api/inventory/:id
 * Détails d'un item d'inventaire
 */
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    const item = await Inventory.findOne({
      where: { id },
      include: ['product', 'warehouse', 'movements']
    });

    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    res.json({
      success: true,
      item
    });
  } catch (error) {
    console.error('Error fetching inventory item:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching inventory item',
      error: error.message
    });
  }
});

/**
 * POST /api/inventory
 * Créer un nouvel item d'inventaire
 */
router.post('/', authenticateToken, checkRole(['merchant', 'admin']), async (req, res) => {
  try {
    const merchantId = req.user.role === 'admin' ? req.body.merchant_id : req.user.id;

    const item = await InventoryService.create({
      ...req.body,
      merchant_id: merchantId
    });

    res.status(201).json({
      success: true,
      item,
      message: 'Inventory item created'
    });
  } catch (error) {
    console.error('Error creating inventory item:', error);
    res.status(500).json({
      success: false,
      message: 'Error creating inventory item',
      error: error.message
    });
  }
});

/**
 * PUT /api/inventory/:id
 * Mettre à jour un item d'inventaire
 */
router.put('/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;

    const item = await Inventory.findByPk(id);
    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    // Update allowed fields
    const allowedFields = [
      'alert_threshold', 'critical_threshold', 'reorder_point',
      'reorder_quantity', 'cost_price', 'selling_price',
      'warehouse_id', 'location', 'sku'
    ];

    allowedFields.forEach(field => {
      if (req.body[field] !== undefined) {
        item[field] = req.body[field];
      }
    });

    await item.save();

    res.json({
      success: true,
      item,
      message: 'Inventory item updated'
    });
  } catch (error) {
    console.error('Error updating inventory item:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating inventory item',
      error: error.message
    });
  }
});

/**
 * POST /api/inventory/:id/add-stock
 * Ajouter du stock
 */
router.post('/:id/add-stock', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { quantity, movement_type, reference, notes, unit_cost } = req.body;

    if (!quantity || quantity <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid quantity'
      });
    }

    const item = await Inventory.findByPk(id);
    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    const updatedItem = await InventoryService.addStock(id, quantity, {
      movement_type: movement_type || 'purchase',
      reference,
      notes,
      unit_cost,
      performed_by: req.user.id
    });

    res.json({
      success: true,
      item: updatedItem,
      message: `Added ${quantity} units to stock`
    });
  } catch (error) {
    console.error('Error adding stock:', error);
    res.status(500).json({
      success: false,
      message: 'Error adding stock',
      error: error.message
    });
  }
});

/**
 * POST /api/inventory/:id/remove-stock
 * Retirer du stock
 */
router.post('/:id/remove-stock', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { quantity, movement_type, reference, notes } = req.body;

    if (!quantity || quantity <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid quantity'
      });
    }

    const item = await Inventory.findByPk(id);
    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    const updatedItem = await InventoryService.removeStock(id, quantity, {
      movement_type: movement_type || 'sale',
      reference,
      notes,
      performed_by: req.user.id
    });

    res.json({
      success: true,
      item: updatedItem,
      message: `Removed ${quantity} units from stock`
    });
  } catch (error) {
    console.error('Error removing stock:', error);
    res.status(500).json({
      success: false,
      message: error.message,
      error: error.message
    });
  }
});

/**
 * POST /api/inventory/:id/adjust
 * Ajuster le stock manuellement
 */
router.post('/:id/adjust', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { new_quantity, notes } = req.body;

    if (new_quantity === undefined || new_quantity < 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid new quantity'
      });
    }

    const item = await Inventory.findByPk(id);
    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    const updatedItem = await InventoryService.adjustStock(id, new_quantity, {
      notes,
      performed_by: req.user.id
    });

    res.json({
      success: true,
      item: updatedItem,
      message: 'Stock adjusted successfully'
    });
  } catch (error) {
    console.error('Error adjusting stock:', error);
    res.status(500).json({
      success: false,
      message: 'Error adjusting stock',
      error: error.message
    });
  }
});

/**
 * GET /api/inventory/:id/movements
 * Historique des mouvements
 */
router.get('/:id/movements', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { start_date, end_date, movement_type, limit, offset } = req.query;

    const item = await Inventory.findByPk(id);
    if (!item) {
      return res.status(404).json({
        success: false,
        message: 'Inventory item not found'
      });
    }

    // Vérifier ownership
    if (req.user.role !== 'admin' && item.merchant_id !== req.user.id) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }

    const movements = await InventoryService.getMovements(id, {
      start_date,
      end_date,
      movement_type,
      limit,
      offset
    });

    res.json({
      success: true,
      movements
    });
  } catch (error) {
    console.error('Error fetching movements:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching movements',
      error: error.message
    });
  }
});

/**
 * POST /api/inventory/scan-alerts
 * Scanner les stocks bas (Cron job ou manuel)
 */
router.post('/scan-alerts', authenticateToken, checkRole(['admin']), async (req, res) => {
  try {
    const { merchant_id } = req.body;

    const lowStockItems = await InventoryService.scanLowStock(merchant_id);

    res.json({
      success: true,
      message: `Scanned ${lowStockItems.length} low stock items`,
      count: lowStockItems.length
    });
  } catch (error) {
    console.error('Error scanning low stock:', error);
    res.status(500).json({
      success: false,
      message: 'Error scanning low stock',
      error: error.message
    });
  }
});

module.exports = router;
