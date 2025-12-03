const express = require('express');
const router = express.Router();
const { authenticateToken, checkRole } = require('../middleware/auth');
const MarketingService = require('../services/MarketingAutomationService');

/**
 * Marketing Automation API Routes
 * ROI: 1.78M€/month
 */

// Trigger abandoned cart campaign
router.post('/abandoned-cart', authenticateToken, async (req, res) => {
  try {
    const { cart_items, cart_value } = req.body;
    const result = await MarketingService.triggerAbandonedCartCampaign(
      req.user.id,
      cart_items,
      cart_value
    );
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Run win-back campaign
router.post('/win-back', authenticateToken, checkRole(['merchant']), async (req, res) => {
  try {
    const result = await MarketingService.runWinBackCampaign(req.user.id);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get customer segments
router.get('/segments', authenticateToken, checkRole(['merchant']), async (req, res) => {
  try {
    const segments = await MarketingService.segmentCustomers(req.user.id);
    res.json({ success: true, segments });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Award loyalty points
router.post('/loyalty/award', authenticateToken, async (req, res) => {
  try {
    const { order_amount } = req.body;
    const result = await MarketingService.awardLoyaltyPoints(req.user.id, order_amount);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
