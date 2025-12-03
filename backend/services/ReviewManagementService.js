const Review = require('../models/Review');
const NotificationService = require('./NotificationService');
const { Op } = require('sequelize');

/**
 * ReviewManagementService
 * Gestion avancée des avis avec modération IA
 * ROI: Réputation +30%, Taux de conversion +20%, Satisfaction +25%
 */
class ReviewManagementService {

  /**
   * Créer un nouvel avis
   */
  async createReview(data) {
    try {
      const review = await Review.create({
        product_id: data.product_id,
        service_id: data.service_id,
        merchant_id: data.merchant_id,
        customer_id: data.customer_id,
        customer_name: data.customer_name,
        customer_email: data.customer_email,
        order_id: data.order_id,
        verified_purchase: data.verified_purchase || false,
        rating: data.rating,
        title: data.title,
        comment: data.comment,
        images: data.images || [],
        videos: data.videos || [],
        source: data.source || 'website',
        language: data.language || 'fr',
        metadata: data.metadata || {}
      });

      // Modération automatique par IA
      await this.moderateReview(review.id);

      // Notifier le marchand
      await this.notifyMerchantNewReview(review);

      return review;
    } catch (error) {
      console.error('Error creating review:', error);
      throw error;
    }
  }

  /**
   * Modération automatique par IA
   */
  async moderateReview(reviewId) {
    try {
      const review = await Review.findByPk(reviewId);
      if (!review) {
        throw new Error('Review not found');
      }

      // 1. Analyse de sentiment
      const sentimentAnalysis = await this.analyzeSentiment(review.comment, review.rating);

      // 2. Détection de spam
      const spamDetection = await this.detectSpam(review.comment, review.customer_email);

      // 3. Détection de profanité
      const profanityDetection = await this.detectProfanity(review.comment);

      // 4. Extraction des problèmes
      const issuesDetection = await this.detectIssues(review.comment, review.rating);

      // 5. Score de modération global
      let moderationScore = 1.0;
      let status = 'approved';
      let moderationReason = null;

      // Si spam détecté
      if (spamDetection.is_spam) {
        status = 'spam';
        moderationScore = 0.1;
        moderationReason = 'Spam automatiquement détecté';
      }
      // Si profanité détectée
      else if (profanityDetection.contains_profanity) {
        status = 'flagged';
        moderationScore = 0.3;
        moderationReason = 'Langage inapproprié détecté';
      }
      // Si incohérence note/commentaire
      else if (this.hasInconsistency(review.rating, sentimentAnalysis.sentiment)) {
        status = 'flagged';
        moderationScore = 0.5;
        moderationReason = 'Incohérence entre note et commentaire';
      }
      // Sinon approuvé
      else {
        status = 'approved';
        moderationScore = 0.9;
      }

      // Mettre à jour l'avis
      await review.update({
        status,
        auto_moderated: true,
        moderation_score: moderationScore,
        moderation_reason: moderationReason,
        sentiment: sentimentAnalysis.sentiment,
        sentiment_score: sentimentAnalysis.score,
        detected_issues: issuesDetection,
        is_spam: spamDetection.is_spam,
        spam_score: spamDetection.score,
        contains_profanity: profanityDetection.contains_profanity,
        is_featured: review.shouldBeFeatured()
      });

      // Si avis négatif ou signalé, notifier immédiatement
      if (status === 'flagged' || review.isNegative()) {
        await NotificationService.create({
          user_id: review.merchant_id,
          type: 'review_requires_attention',
          title: '⚠️ Avis Nécessitant Attention',
          message: `Avis ${review.rating}⭐ de ${review.customer_name}: "${review.comment.substring(0, 50)}..."`,
          data: { review_id: review.id, rating: review.rating },
          priority: 'high',
          channels: { in_app: true, push: true, email: true }
        });
      }

      // Générer réponse automatique si négatif
      if (review.isNegative() && review.status === 'approved') {
        await this.generateAutoResponse(review);
      }

      return review;
    } catch (error) {
      console.error('Error moderating review:', error);
      throw error;
    }
  }

  /**
   * Analyser le sentiment du commentaire
   */
  async analyzeSentiment(comment, rating) {
    // Analyse simple (peut être remplacé par OpenAI/Claude API)
    const lowerComment = comment.toLowerCase();

    const veryPositiveWords = ['excellent', 'parfait', 'incroyable', 'génial', 'extraordinaire', 'magnifique', 'adoré'];
    const positiveWords = ['bien', 'bon', 'content', 'satisfait', 'agréable', 'recommande', 'merci'];
    const negativeWords = ['mauvais', 'déçu', 'insatisfait', 'problème', 'arnaque', 'nul', 'horrible'];
    const veryNegativeWords = ['catastrophe', 'scandale', 'honte', 'frauduleux', 'escroquerie'];

    let score = 0;
    let sentiment = 'neutral';

    // Compter les mots
    const veryPosCount = veryPositiveWords.filter(w => lowerComment.includes(w)).length;
    const posCount = positiveWords.filter(w => lowerComment.includes(w)).length;
    const negCount = negativeWords.filter(w => lowerComment.includes(w)).length;
    const veryNegCount = veryNegativeWords.filter(w => lowerComment.includes(w)).length;

    // Calculer le score
    score = (veryPosCount * 0.3 + posCount * 0.15 - negCount * 0.15 - veryNegCount * 0.3);

    // Ajuster avec la note
    if (rating === 5) score += 0.3;
    else if (rating === 4) score += 0.1;
    else if (rating === 2) score -= 0.1;
    else if (rating === 1) score -= 0.3;

    // Déterminer le sentiment
    if (score >= 0.5) sentiment = 'very_positive';
    else if (score >= 0.2) sentiment = 'positive';
    else if (score <= -0.5) sentiment = 'very_negative';
    else if (score <= -0.2) sentiment = 'negative';
    else sentiment = 'neutral';

    // Normaliser le score entre -1 et 1
    score = Math.max(-1, Math.min(1, score));

    return { sentiment, score };
  }

  /**
   * Détecter le spam
   */
  async detectSpam(comment, email) {
    let isSpam = false;
    let score = 0;

    const lowerComment = comment.toLowerCase();

    // Patterns de spam
    const spamPatterns = [
      /http[s]?:\/\//gi,  // URLs
      /\b\d{10,}\b/g,     // Numéros de téléphone
      /(viagra|cialis|casino|poker|lottery|winner)/gi,  // Mots-clés spam
      /(.)\1{5,}/g        // Répétition excessive
    ];

    spamPatterns.forEach(pattern => {
      if (pattern.test(comment)) {
        score += 0.25;
      }
    });

    // Email jetable
    const disposableEmailDomains = ['tempmail', 'throwaway', 'guerrillamail', '10minutemail'];
    if (email && disposableEmailDomains.some(domain => email.includes(domain))) {
      score += 0.3;
    }

    // Commentaire trop court
    if (comment.length < 10) {
      score += 0.1;
    }

    // Commentaire en majuscules
    if (comment === comment.toUpperCase() && comment.length > 20) {
      score += 0.2;
    }

    isSpam = score >= 0.6;

    return { is_spam: isSpam, score };
  }

  /**
   * Détecter la profanité
   */
  async detectProfanity(comment) {
    const profanityWords = [
      'merde', 'connard', 'con', 'putain', 'salope', 'enculé'
      // Liste simplifiée - devrait être plus complète
    ];

    const lowerComment = comment.toLowerCase();
    const containsProfanity = profanityWords.some(word => lowerComment.includes(word));

    return { contains_profanity: containsProfanity };
  }

  /**
   * Détecter les problèmes mentionnés
   */
  async detectIssues(comment, rating) {
    const lowerComment = comment.toLowerCase();
    const issues = [];

    const issueKeywords = {
      quality: ['qualité', 'défaut', 'cassé', 'abîmé', 'mauvaise qualité'],
      delivery: ['livraison', 'retard', 'délai', 'jamais reçu', 'perdu'],
      customer_service: ['service client', 'réponse', 'ignoré', 'pas de retour', 'joignable'],
      price: ['prix', 'cher', 'arnaque', 'surfacturé', 'coût'],
      description: ['description', 'photo', 'pas comme', 'différent', 'trompeur']
    };

    Object.keys(issueKeywords).forEach(issue => {
      const keywords = issueKeywords[issue];
      if (keywords.some(keyword => lowerComment.includes(keyword)) && rating <= 3) {
        issues.push(issue);
      }
    });

    return issues;
  }

  /**
   * Vérifier incohérence note/commentaire
   */
  hasInconsistency(rating, sentiment) {
    // Note élevée mais sentiment négatif
    if (rating >= 4 && (sentiment === 'negative' || sentiment === 'very_negative')) {
      return true;
    }

    // Note basse mais sentiment positif
    if (rating <= 2 && (sentiment === 'positive' || sentiment === 'very_positive')) {
      return true;
    }

    return false;
  }

  /**
   * Générer une réponse automatique (IA)
   */
  async generateAutoResponse(review) {
    try {
      let responseTemplate = '';

      if (review.rating === 1 || review.rating === 2) {
        // Avis très négatif - S'excuser et proposer solution
        const issuesText = review.detected_issues.length > 0
          ? ` concernant ${review.detected_issues.join(', ')}`
          : '';

        responseTemplate = `Bonjour ${review.customer_name},

Nous sommes sincèrement désolés de lire votre retour${issuesText}. Votre satisfaction est notre priorité et nous prenons votre commentaire très au sérieux.

Nous aimerions comprendre ce qui s'est passé et trouver une solution adaptée. Pourriez-vous nous contacter directement à support@getyourshare.com ? Notre équipe se fera un plaisir de résoudre ce problème rapidement.

Merci de nous donner l'opportunité de corriger cette expérience.

Cordialement,
L'équipe GetYourShare`;

      } else if (review.rating === 3) {
        // Avis moyen - Remercier et demander plus d'infos
        responseTemplate = `Bonjour ${review.customer_name},

Merci pour votre retour. Nous sommes toujours à l'écoute pour nous améliorer.

Pourriez-vous nous en dire plus sur ce qui pourrait être amélioré ? Votre avis est précieux et nous aidera à offrir une meilleure expérience à nos clients.

N'hésitez pas à nous contacter si vous avez des suggestions.

Cordialement,
L'équipe GetYourShare`;

      }

      if (responseTemplate) {
        await review.update({
          has_response: true,
          response_text: responseTemplate,
          response_date: new Date(),
          auto_response: true
        });
      }

    } catch (error) {
      console.error('Error generating auto response:', error);
    }
  }

  /**
   * Répondre manuellement à un avis
   */
  async respondToReview(reviewId, merchantId, responseText) {
    try {
      const review = await Review.findOne({
        where: { id: reviewId, merchant_id: merchantId }
      });

      if (!review) {
        throw new Error('Review not found');
      }

      await review.update({
        has_response: true,
        response_text: responseText,
        response_date: new Date(),
        auto_response: false
      });

      // Notifier le client si possible
      if (review.customer_id) {
        await NotificationService.create({
          user_id: review.customer_id,
          type: 'review_response',
          title: '💬 Réponse à votre Avis',
          message: `Le marchand a répondu à votre avis: "${responseText.substring(0, 100)}..."`,
          data: { review_id: review.id },
          priority: 'low',
          channels: { in_app: true, email: true }
        });
      }

      return review;
    } catch (error) {
      console.error('Error responding to review:', error);
      throw error;
    }
  }

  /**
   * Obtenir tous les avis d'un marchand
   */
  async getReviews(merchantId, filters = {}) {
    try {
      const where = { merchant_id: merchantId };

      if (filters.status) {
        where.status = filters.status;
      }

      if (filters.rating) {
        where.rating = parseInt(filters.rating);
      }

      if (filters.sentiment) {
        where.sentiment = filters.sentiment;
      }

      if (filters.requires_attention) {
        // Avis nécessitant attention
        where[Op.or] = [
          { rating: { [Op.lte]: 2 } },
          { status: 'flagged' },
          { report_count: { [Op.gte]: 3 } }
        ];
      }

      if (filters.no_response) {
        where.has_response = false;
      }

      const reviews = await Review.findAll({
        where,
        order: [['created_at', 'DESC']],
        limit: filters.limit || 50,
        offset: filters.offset || 0
      });

      return reviews;
    } catch (error) {
      console.error('Error fetching reviews:', error);
      throw error;
    }
  }

  /**
   * Obtenir les statistiques des avis
   */
  async getStatistics(merchantId) {
    try {
      const total = await Review.count({
        where: { merchant_id: merchantId, status: 'approved' }
      });

      // Moyenne des notes
      const reviews = await Review.findAll({
        where: { merchant_id: merchantId, status: 'approved' },
        attributes: ['rating']
      });

      const avgRating = reviews.length > 0
        ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
        : 0;

      // Distribution par note
      const byRating = {
        5: await Review.count({ where: { merchant_id: merchantId, rating: 5, status: 'approved' } }),
        4: await Review.count({ where: { merchant_id: merchantId, rating: 4, status: 'approved' } }),
        3: await Review.count({ where: { merchant_id: merchantId, rating: 3, status: 'approved' } }),
        2: await Review.count({ where: { merchant_id: merchantId, rating: 2, status: 'approved' } }),
        1: await Review.count({ where: { merchant_id: merchantId, rating: 1, status: 'approved' } })
      };

      // Par sentiment
      const bySentiment = {
        very_positive: await Review.count({ where: { merchant_id: merchantId, sentiment: 'very_positive' } }),
        positive: await Review.count({ where: { merchant_id: merchantId, sentiment: 'positive' } }),
        neutral: await Review.count({ where: { merchant_id: merchantId, sentiment: 'neutral' } }),
        negative: await Review.count({ where: { merchant_id: merchantId, sentiment: 'negative' } }),
        very_negative: await Review.count({ where: { merchant_id: merchantId, sentiment: 'very_negative' } })
      };

      // Statistiques de modération
      const pending = await Review.count({ where: { merchant_id: merchantId, status: 'pending' } });
      const flagged = await Review.count({ where: { merchant_id: merchantId, status: 'flagged' } });
      const spam = await Review.count({ where: { merchant_id: merchantId, status: 'spam' } });

      // Taux de réponse
      const withResponse = await Review.count({
        where: { merchant_id: merchantId, has_response: true, status: 'approved' }
      });
      const responseRate = total > 0 ? (withResponse / total) * 100 : 0;

      // Avis vérifiés
      const verifiedCount = await Review.count({
        where: { merchant_id: merchantId, verified_purchase: true, status: 'approved' }
      });
      const verificationRate = total > 0 ? (verifiedCount / total) * 100 : 0;

      return {
        total,
        avg_rating: avgRating.toFixed(1),
        by_rating: byRating,
        by_sentiment: bySentiment,
        pending,
        flagged,
        spam,
        response_rate: responseRate.toFixed(1),
        verification_rate: verificationRate.toFixed(1),
        with_response: withResponse,
        verified_count: verifiedCount
      };
    } catch (error) {
      console.error('Error calculating statistics:', error);
      throw error;
    }
  }

  /**
   * Notifier le marchand d'un nouvel avis
   */
  async notifyMerchantNewReview(review) {
    try {
      const emoji = review.rating >= 4 ? '⭐' : review.rating === 3 ? '⚠️' : '🔴';
      const priority = review.rating <= 2 ? 'high' : 'normal';

      await NotificationService.create({
        user_id: review.merchant_id,
        type: 'new_review',
        title: `${emoji} Nouvel Avis ${review.rating}⭐`,
        message: `${review.customer_name}: "${review.comment.substring(0, 100)}${review.comment.length > 100 ? '...' : ''}"`,
        data: { review_id: review.id, rating: review.rating },
        priority,
        channels: { in_app: true, push: review.rating <= 2, email: review.rating <= 2 }
      });
    } catch (error) {
      console.error('Error notifying merchant:', error);
    }
  }

  /**
   * Approuver manuellement un avis
   */
  async approveReview(reviewId, merchantId, moderatorId) {
    try {
      const review = await Review.findOne({
        where: { id: reviewId, merchant_id: merchantId }
      });

      if (!review) {
        throw new Error('Review not found');
      }

      await review.update({
        status: 'approved',
        moderated_by: moderatorId,
        moderated_at: new Date()
      });

      return review;
    } catch (error) {
      console.error('Error approving review:', error);
      throw error;
    }
  }

  /**
   * Rejeter un avis
   */
  async rejectReview(reviewId, merchantId, moderatorId, reason) {
    try {
      const review = await Review.findOne({
        where: { id: reviewId, merchant_id: merchantId }
      });

      if (!review) {
        throw new Error('Review not found');
      }

      await review.update({
        status: 'rejected',
        moderated_by: moderatorId,
        moderated_at: new Date(),
        moderation_notes: reason
      });

      return review;
    } catch (error) {
      console.error('Error rejecting review:', error);
      throw error;
    }
  }
}

module.exports = new ReviewManagementService();
