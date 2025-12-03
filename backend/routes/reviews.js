const express = require('express');
const router = express.Router();
const ReviewManagementService = require('../services/ReviewManagementService');
const { authenticate } = require('../middleware/auth');

/**
 * Review Management Routes
 * Gestion avancée des avis avec modération IA
 */

// Créer un nouvel avis (public ou client authentifié)
router.post('/', async (req, res) => {
  try {
    const review = await ReviewManagementService.createReview({
      ...req.body,
      customer_id: req.user?.id
    });

    res.status(201).json({
      success: true,
      review,
      message: 'Merci pour votre avis! Il sera publié après modération.'
    });
  } catch (error) {
    console.error('Error creating review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir tous les avis d'un marchand
router.get('/merchant', authenticate, async (req, res) => {
  try {
    const { status, rating, sentiment, requires_attention, no_response, limit, offset } = req.query;

    const reviews = await ReviewManagementService.getReviews(req.user.id, {
      status,
      rating,
      sentiment,
      requires_attention: requires_attention === 'true',
      no_response: no_response === 'true',
      limit: limit ? parseInt(limit) : undefined,
      offset: offset ? parseInt(offset) : undefined
    });

    res.json({
      success: true,
      reviews,
      count: reviews.length
    });
  } catch (error) {
    console.error('Error fetching reviews:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les statistiques
router.get('/statistics', authenticate, async (req, res) => {
  try {
    const stats = await ReviewManagementService.getStatistics(req.user.id);

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

// Obtenir les avis d'un produit spécifique (public)
router.get('/product/:productId', async (req, res) => {
  try {
    const Review = require('../models/Review');
    const reviews = await Review.findAll({
      where: {
        product_id: req.params.productId,
        status: 'approved',
        is_visible: true
      },
      order: [
        ['is_featured', 'DESC'],
        ['created_at', 'DESC']
      ],
      limit: req.query.limit ? parseInt(req.query.limit) : 20
    });

    res.json({
      success: true,
      reviews,
      count: reviews.length
    });
  } catch (error) {
    console.error('Error fetching product reviews:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Répondre à un avis
router.post('/:reviewId/respond', authenticate, async (req, res) => {
  try {
    const { response_text } = req.body;

    if (!response_text) {
      return res.status(400).json({
        success: false,
        error: 'Response text is required'
      });
    }

    const review = await ReviewManagementService.respondToReview(
      req.params.reviewId,
      req.user.id,
      response_text
    );

    res.json({
      success: true,
      review
    });
  } catch (error) {
    console.error('Error responding to review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Approuver un avis
router.put('/:reviewId/approve', authenticate, async (req, res) => {
  try {
    const review = await ReviewManagementService.approveReview(
      req.params.reviewId,
      req.user.id,
      req.user.id
    );

    res.json({
      success: true,
      review
    });
  } catch (error) {
    console.error('Error approving review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Rejeter un avis
router.put('/:reviewId/reject', authenticate, async (req, res) => {
  try {
    const { reason } = req.body;

    const review = await ReviewManagementService.rejectReview(
      req.params.reviewId,
      req.user.id,
      req.user.id,
      reason
    );

    res.json({
      success: true,
      review
    });
  } catch (error) {
    console.error('Error rejecting review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Re-modérer un avis (re-run IA moderation)
router.post('/:reviewId/remoderate', authenticate, async (req, res) => {
  try {
    const review = await ReviewManagementService.moderateReview(req.params.reviewId);

    res.json({
      success: true,
      review,
      message: 'Review re-moderated successfully'
    });
  } catch (error) {
    console.error('Error re-moderating review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Marquer un avis comme utile (public)
router.post('/:reviewId/helpful', async (req, res) => {
  try {
    const Review = require('../models/Review');
    const review = await Review.findByPk(req.params.reviewId);

    if (!review) {
      return res.status(404).json({
        success: false,
        error: 'Review not found'
      });
    }

    await review.increment('helpful_count');

    res.json({
      success: true,
      helpful_count: review.helpful_count + 1
    });
  } catch (error) {
    console.error('Error marking helpful:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Signaler un avis (public)
router.post('/:reviewId/report', async (req, res) => {
  try {
    const Review = require('../models/Review');
    const review = await Review.findByPk(req.params.reviewId);

    if (!review) {
      return res.status(404).json({
        success: false,
        error: 'Review not found'
      });
    }

    await review.increment('report_count');

    // Si trop de signalements, marquer comme flagged
    if (review.report_count + 1 >= 3 && review.status === 'approved') {
      await review.update({ status: 'flagged' });

      // Notifier le marchand
      await NotificationService.create({
        user_id: review.merchant_id,
        type: 'review_flagged',
        title: '🚩 Avis Signalé',
        message: `L'avis de ${review.customer_name} a été signalé ${review.report_count + 1} fois`,
        data: { review_id: review.id },
        priority: 'high',
        channels: { in_app: true, email: true }
      });
    }

    res.json({
      success: true,
      message: 'Review reported successfully'
    });
  } catch (error) {
    console.error('Error reporting review:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
