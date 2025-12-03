const express = require('express');
const router = express.Router();
const ContentCalendarService = require('../services/ContentCalendarService');
const { authenticate } = require('../middleware/auth');

/**
 * Content Calendar Routes
 * Gestion du calendrier éditorial pour influenceurs
 */

// Créer un nouveau post
router.post('/posts', authenticate, async (req, res) => {
  try {
    const post = await ContentCalendarService.createPost({
      ...req.body,
      influencer_id: req.user.id
    });

    res.status(201).json({
      success: true,
      post
    });
  } catch (error) {
    console.error('Error creating post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir le calendrier
router.get('/calendar', authenticate, async (req, res) => {
  try {
    const { platform, status, start_date, end_date, month, year, campaign_id, limit } = req.query;

    const posts = await ContentCalendarService.getCalendar(req.user.id, {
      platform,
      status,
      start_date,
      end_date,
      month: month ? parseInt(month) : undefined,
      year: year ? parseInt(year) : undefined,
      campaign_id,
      limit: limit ? parseInt(limit) : undefined
    });

    res.json({
      success: true,
      posts,
      count: posts.length
    });
  } catch (error) {
    console.error('Error fetching calendar:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les statistiques
router.get('/statistics', authenticate, async (req, res) => {
  try {
    const { period } = req.query;
    const stats = await ContentCalendarService.getStatistics(req.user.id, period || 'month');

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

// Obtenir un post spécifique
router.get('/posts/:postId', authenticate, async (req, res) => {
  try {
    const ContentPost = require('../models/ContentPost');
    const post = await ContentPost.findOne({
      where: {
        id: req.params.postId,
        influencer_id: req.user.id
      }
    });

    if (!post) {
      return res.status(404).json({
        success: false,
        error: 'Post not found'
      });
    }

    res.json({
      success: true,
      post
    });
  } catch (error) {
    console.error('Error fetching post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Mettre à jour un post
router.put('/posts/:postId', authenticate, async (req, res) => {
  try {
    const post = await ContentCalendarService.updatePost(
      req.params.postId,
      req.user.id,
      req.body
    );

    res.json({
      success: true,
      post
    });
  } catch (error) {
    console.error('Error updating post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Supprimer un post
router.delete('/posts/:postId', authenticate, async (req, res) => {
  try {
    await ContentCalendarService.deletePost(req.params.postId, req.user.id);

    res.json({
      success: true,
      message: 'Post deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Publier un post manuellement
router.post('/posts/:postId/publish', authenticate, async (req, res) => {
  try {
    const post = await ContentCalendarService.publishPost(req.params.postId);

    res.json({
      success: true,
      post,
      message: 'Post published successfully'
    });
  } catch (error) {
    console.error('Error publishing post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Mettre à jour les métriques d'un post
router.put('/posts/:postId/metrics', authenticate, async (req, res) => {
  try {
    const post = await ContentCalendarService.updateMetrics(
      req.params.postId,
      req.body
    );

    res.json({
      success: true,
      post
    });
  } catch (error) {
    console.error('Error updating metrics:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Dupliquer un post
router.post('/posts/:postId/duplicate', authenticate, async (req, res) => {
  try {
    const duplicatePost = await ContentCalendarService.duplicatePost(
      req.params.postId,
      req.user.id
    );

    res.status(201).json({
      success: true,
      post: duplicatePost
    });
  } catch (error) {
    console.error('Error duplicating post:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les suggestions de hashtags
router.get('/hashtags/suggestions', authenticate, async (req, res) => {
  try {
    const { platform, category } = req.query;

    if (!platform || !category) {
      return res.status(400).json({
        success: false,
        error: 'Platform and category are required'
      });
    }

    const hashtags = await ContentCalendarService.getSuggestedHashtags(platform, category);

    res.json({
      success: true,
      hashtags
    });
  } catch (error) {
    console.error('Error fetching hashtag suggestions:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Obtenir les posts en retard
router.get('/posts/overdue', authenticate, async (req, res) => {
  try {
    const posts = await ContentCalendarService.getOverduePosts(req.user.id);

    res.json({
      success: true,
      posts,
      count: posts.length
    });
  } catch (error) {
    console.error('Error fetching overdue posts:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
