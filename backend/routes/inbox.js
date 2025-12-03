const express = require('express');
const router = express.Router();
const UnifiedInboxService = require('../services/UnifiedInboxService');
const { authenticate } = require('../middleware/auth');

/**
 * Unified Inbox Routes
 * Boîte de réception unifiée pour commerciaux
 */

// Obtenir la boîte de réception
router.get('/messages', authenticate, async (req, res) => {
  try {
    const filters = {
      channel: req.query.channel,
      is_read: req.query.is_read,
      is_starred: req.query.is_starred === 'true',
      priority: req.query.priority,
      sentiment: req.query.sentiment,
      category: req.query.category,
      direction: req.query.direction,
      show_archived: req.query.show_archived === 'true',
      limit: req.query.limit ? parseInt(req.query.limit) : 50,
      offset: req.query.offset ? parseInt(req.query.offset) : 0
    };

    const messages = await UnifiedInboxService.getInbox(req.user.id, filters);

    res.json({
      success: true,
      messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error fetching inbox:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les statistiques
router.get('/statistics', authenticate, async (req, res) => {
  try {
    const stats = await UnifiedInboxService.getStatistics(req.user.id);

    res.json({
      success: true,
      statistics: stats
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir un thread de conversation
router.get('/threads/:threadId', authenticate, async (req, res) => {
  try {
    const messages = await UnifiedInboxService.getThread(
      req.params.threadId,
      req.user.id
    );

    res.json({
      success: true,
      messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error fetching thread:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Envoyer un message
router.post('/messages', authenticate, async (req, res) => {
  try {
    const message = await UnifiedInboxService.sendMessage({
      ...req.body,
      commercial_id: req.user.id
    });

    res.status(201).json({
      success: true,
      message
    });
  } catch (error) {
    console.error('Error sending message:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Répondre à un message
router.post('/messages/:messageId/reply', authenticate, async (req, res) => {
  try {
    const reply = await UnifiedInboxService.replyToMessage(
      req.params.messageId,
      req.user.id,
      req.body
    );

    res.status(201).json({
      success: true,
      message: reply
    });
  } catch (error) {
    console.error('Error replying to message:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Marquer comme lu
router.put('/messages/:messageId/read', authenticate, async (req, res) => {
  try {
    const message = await UnifiedInboxService.markAsRead(
      req.params.messageId,
      req.user.id
    );

    res.json({
      success: true,
      message
    });
  } catch (error) {
    console.error('Error marking as read:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Marquer plusieurs comme lus
router.put('/messages/bulk/read', authenticate, async (req, res) => {
  try {
    const { message_ids } = req.body;

    if (!message_ids || !Array.isArray(message_ids)) {
      return res.status(400).json({
        success: false,
        error: 'message_ids array is required'
      });
    }

    const result = await UnifiedInboxService.markMultipleAsRead(
      message_ids,
      req.user.id
    );

    res.json({
      success: true,
      ...result
    });
  } catch (error) {
    console.error('Error marking multiple as read:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Toggle étoile
router.put('/messages/:messageId/star', authenticate, async (req, res) => {
  try {
    const message = await UnifiedInboxService.toggleStar(
      req.params.messageId,
      req.user.id
    );

    res.json({
      success: true,
      message
    });
  } catch (error) {
    console.error('Error toggling star:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Toggle archivage
router.put('/messages/:messageId/archive', authenticate, async (req, res) => {
  try {
    const message = await UnifiedInboxService.toggleArchive(
      req.params.messageId,
      req.user.id
    );

    res.json({
      success: true,
      message
    });
  } catch (error) {
    console.error('Error toggling archive:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Rechercher
router.get('/search', authenticate, async (req, res) => {
  try {
    const { q } = req.query;

    if (!q) {
      return res.status(400).json({
        success: false,
        error: 'Search query (q) is required'
      });
    }

    const messages = await UnifiedInboxService.search(req.user.id, q);

    res.json({
      success: true,
      messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error searching:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les messages nécessitant une réponse
router.get('/requires-response', authenticate, async (req, res) => {
  try {
    const messages = await UnifiedInboxService.getRequiresResponse(req.user.id);

    res.json({
      success: true,
      messages,
      count: messages.length
    });
  } catch (error) {
    console.error('Error fetching messages requiring response:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Webhook pour recevoir des messages (appelé par services externes)
router.post('/webhook/:channel', async (req, res) => {
  try {
    const { channel } = req.params;

    // TODO: Valider le webhook (signature, token, etc.)

    const message = await UnifiedInboxService.receiveMessage({
      ...req.body,
      channel
    });

    res.status(201).json({
      success: true,
      message
    });
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
