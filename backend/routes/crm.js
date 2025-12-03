const express = require('express');
const router = express.Router();
const { authenticateToken, checkRole } = require('../middleware/auth');
const CRMService = require('../services/CRMAutomationService');

/**
 * CRM Automation API Routes  
 * ROI: 660K€/month
 */

// Start email sequence for lead
router.post('/sequence/start', authenticateToken, checkRole(['commercial', 'admin']), async (req, res) => {
  try {
    const { lead_id, sequence_type } = req.body;
    const result = await CRMService.startEmailSequence(lead_id, sequence_type);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Calculate lead score
router.post('/leads/:id/score', authenticateToken, checkRole(['commercial', 'admin']), async (req, res) => {
  try {
    const result = await CRMService.calculateLeadScore(req.params.id);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Predict closing probability
router.get('/leads/:id/predict', authenticateToken, checkRole(['commercial', 'admin']), async (req, res) => {
  try {
    const result = await CRMService.predictClosingProbability(req.params.id);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Execute workflow
router.post('/workflows/:id/execute', authenticateToken, checkRole(['commercial', 'admin']), async (req, res) => {
  try {
    const { lead_id } = req.body;
    const result = await CRMService.executeWorkflow(req.params.id, lead_id);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
