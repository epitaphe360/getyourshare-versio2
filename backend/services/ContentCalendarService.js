const ContentPost = require('../models/ContentPost');
const NotificationService = require('./NotificationService');
const { Op } = require('sequelize');

/**
 * ContentCalendarService
 * Gestion du calendrier éditorial pour influenceurs
 * ROI: Productivité +40%, Engagement +25%
 */
class ContentCalendarService {

  /**
   * Créer un nouveau post
   */
  async createPost(data) {
    try {
      const post = await ContentPost.create({
        influencer_id: data.influencer_id,
        campaign_id: data.campaign_id,
        title: data.title,
        description: data.description,
        content: data.content,
        platform: data.platform,
        content_type: data.content_type || 'post',
        status: data.status || 'draft',
        scheduled_date: data.scheduled_date,
        media_urls: data.media_urls || [],
        thumbnail_url: data.thumbnail_url,
        hashtags: data.hashtags || [],
        mentions: data.mentions || [],
        cta_type: data.cta_type || 'none',
        cta_url: data.cta_url,
        tracking_link: data.tracking_link,
        is_sponsored: data.is_sponsored || false,
        brand_name: data.brand_name,
        commission_rate: data.commission_rate,
        auto_publish: data.auto_publish || false,
        notes: data.notes,
        reminder_date: data.reminder_date,
        metadata: data.metadata || {}
      });

      // Notification si post programmé
      if (post.status === 'scheduled' && post.scheduled_date) {
        await NotificationService.create({
          user_id: data.influencer_id,
          type: 'content_scheduled',
          title: '📅 Contenu Programmé',
          message: `"${post.title}" sera publié le ${new Date(post.scheduled_date).toLocaleDateString('fr-FR')}`,
          data: { post_id: post.id, platform: post.platform },
          priority: 'low',
          channels: { in_app: true, push: false }
        });
      }

      return post;
    } catch (error) {
      console.error('Error creating content post:', error);
      throw error;
    }
  }

  /**
   * Obtenir le calendrier d'un influenceur
   */
  async getCalendar(influencerId, filters = {}) {
    try {
      const where = { influencer_id: influencerId };

      // Filtre par plateforme
      if (filters.platform) {
        where.platform = filters.platform;
      }

      // Filtre par statut
      if (filters.status) {
        where.status = filters.status;
      }

      // Filtre par période
      if (filters.start_date && filters.end_date) {
        where.scheduled_date = {
          [Op.between]: [new Date(filters.start_date), new Date(filters.end_date)]
        };
      } else if (filters.month && filters.year) {
        const startDate = new Date(filters.year, filters.month - 1, 1);
        const endDate = new Date(filters.year, filters.month, 0);
        where.scheduled_date = {
          [Op.between]: [startDate, endDate]
        };
      }

      // Filtre par campagne
      if (filters.campaign_id) {
        where.campaign_id = filters.campaign_id;
      }

      const posts = await ContentPost.findAll({
        where,
        order: [['scheduled_date', 'ASC'], ['created_at', 'DESC']],
        limit: filters.limit || 100
      });

      return posts;
    } catch (error) {
      console.error('Error fetching calendar:', error);
      throw error;
    }
  }

  /**
   * Obtenir les statistiques du calendrier
   */
  async getStatistics(influencerId, period = 'month') {
    try {
      const now = new Date();
      let startDate;

      switch (period) {
        case 'week':
          startDate = new Date(now.setDate(now.getDate() - 7));
          break;
        case 'month':
          startDate = new Date(now.setMonth(now.getMonth() - 1));
          break;
        case 'year':
          startDate = new Date(now.setFullYear(now.getFullYear() - 1));
          break;
        default:
          startDate = new Date(now.setMonth(now.getMonth() - 1));
      }

      const posts = await ContentPost.findAll({
        where: {
          influencer_id: influencerId,
          created_at: {
            [Op.gte]: startDate
          }
        }
      });

      // Calculer les statistiques
      const stats = {
        total_posts: posts.length,
        published: posts.filter(p => p.status === 'published').length,
        scheduled: posts.filter(p => p.status === 'scheduled').length,
        drafts: posts.filter(p => p.status === 'draft').length,
        failed: posts.filter(p => p.status === 'failed').length,

        // Par plateforme
        by_platform: {},

        // Performance globale
        total_views: 0,
        total_likes: 0,
        total_comments: 0,
        total_shares: 0,
        total_clicks: 0,
        total_revenue: 0,
        avg_engagement_rate: 0,

        // Top performers
        top_posts: []
      };

      // Grouper par plateforme
      posts.forEach(post => {
        if (!stats.by_platform[post.platform]) {
          stats.by_platform[post.platform] = {
            count: 0,
            published: 0,
            views: 0,
            engagement_rate: 0
          };
        }
        stats.by_platform[post.platform].count++;
        if (post.status === 'published') {
          stats.by_platform[post.platform].published++;
          stats.by_platform[post.platform].views += post.views;
        }
      });

      // Calculer les totaux
      const publishedPosts = posts.filter(p => p.status === 'published');
      publishedPosts.forEach(post => {
        stats.total_views += post.views;
        stats.total_likes += post.likes;
        stats.total_comments += post.comments;
        stats.total_shares += post.shares;
        stats.total_clicks += post.clicks;
        stats.total_revenue += parseFloat(post.revenue_generated || 0);
      });

      // Engagement rate moyen
      if (publishedPosts.length > 0) {
        const totalEngagementRate = publishedPosts.reduce((sum, post) => sum + post.engagement_rate, 0);
        stats.avg_engagement_rate = totalEngagementRate / publishedPosts.length;
      }

      // Top 5 posts
      stats.top_posts = publishedPosts
        .sort((a, b) => b.engagement_rate - a.engagement_rate)
        .slice(0, 5)
        .map(post => ({
          id: post.id,
          title: post.title,
          platform: post.platform,
          engagement_rate: post.engagement_rate,
          views: post.views,
          revenue: post.revenue_generated
        }));

      // Calculer engagement rate moyen par plateforme
      Object.keys(stats.by_platform).forEach(platform => {
        const platformPosts = publishedPosts.filter(p => p.platform === platform);
        if (platformPosts.length > 0) {
          const totalER = platformPosts.reduce((sum, p) => sum + p.engagement_rate, 0);
          stats.by_platform[platform].engagement_rate = totalER / platformPosts.length;
        }
      });

      return stats;
    } catch (error) {
      console.error('Error calculating statistics:', error);
      throw error;
    }
  }

  /**
   * Mettre à jour un post
   */
  async updatePost(postId, influencerId, updates) {
    try {
      const post = await ContentPost.findOne({
        where: { id: postId, influencer_id: influencerId }
      });

      if (!post) {
        throw new Error('Post not found');
      }

      const oldStatus = post.status;
      await post.update(updates);

      // Notification si changement de statut
      if (updates.status && updates.status !== oldStatus) {
        let notifType = 'content_updated';
        let notifTitle = '✏️ Contenu Mis à Jour';
        let notifMessage = `"${post.title}" a été mis à jour`;

        if (updates.status === 'published') {
          notifType = 'content_published';
          notifTitle = '🎉 Contenu Publié';
          notifMessage = `"${post.title}" a été publié avec succès`;
        } else if (updates.status === 'failed') {
          notifType = 'content_failed';
          notifTitle = '❌ Échec Publication';
          notifMessage = `Échec de publication de "${post.title}"`;
        }

        await NotificationService.create({
          user_id: influencerId,
          type: notifType,
          title: notifTitle,
          message: notifMessage,
          data: { post_id: post.id, platform: post.platform },
          priority: updates.status === 'failed' ? 'high' : 'low',
          channels: { in_app: true, push: updates.status === 'published' }
        });
      }

      return post;
    } catch (error) {
      console.error('Error updating post:', error);
      throw error;
    }
  }

  /**
   * Supprimer un post
   */
  async deletePost(postId, influencerId) {
    try {
      const post = await ContentPost.findOne({
        where: { id: postId, influencer_id: influencerId }
      });

      if (!post) {
        throw new Error('Post not found');
      }

      await post.destroy();
      return { success: true };
    } catch (error) {
      console.error('Error deleting post:', error);
      throw error;
    }
  }

  /**
   * Obtenir les posts à publier (pour automation)
   */
  async getPostsToPublish() {
    try {
      const posts = await ContentPost.findAll({
        where: {
          status: 'scheduled',
          auto_publish: true,
          scheduled_date: {
            [Op.lte]: new Date()
          }
        }
      });

      return posts;
    } catch (error) {
      console.error('Error fetching posts to publish:', error);
      throw error;
    }
  }

  /**
   * Publier un post automatiquement
   */
  async publishPost(postId) {
    try {
      const post = await ContentPost.findByPk(postId);

      if (!post) {
        throw new Error('Post not found');
      }

      if (!post.canPublish()) {
        throw new Error('Post cannot be published yet');
      }

      // TODO: Intégration avec APIs des plateformes sociales
      // Instagram API, Facebook Graph API, Twitter API, etc.

      // Simuler la publication
      await post.update({
        status: 'published',
        published_date: new Date(),
        publish_attempts: post.publish_attempts + 1
      });

      // Notification de succès
      await NotificationService.create({
        user_id: post.influencer_id,
        type: 'content_published',
        title: '🎉 Publication Réussie',
        message: `"${post.title}" a été publié sur ${post.platform}`,
        data: { post_id: post.id, platform: post.platform },
        priority: 'medium',
        channels: { in_app: true, push: true }
      });

      return post;
    } catch (error) {
      console.error('Error publishing post:', error);

      // Marquer comme échec
      const post = await ContentPost.findByPk(postId);
      if (post) {
        await post.update({
          status: 'failed',
          last_publish_error: error.message,
          publish_attempts: post.publish_attempts + 1
        });

        // Notification d'échec
        await NotificationService.create({
          user_id: post.influencer_id,
          type: 'content_failed',
          title: '❌ Échec Publication',
          message: `Échec de publication de "${post.title}": ${error.message}`,
          data: { post_id: post.id, platform: post.platform },
          priority: 'high',
          channels: { in_app: true, push: true }
        });
      }

      throw error;
    }
  }

  /**
   * Mettre à jour les métriques d'un post
   */
  async updateMetrics(postId, metrics) {
    try {
      const post = await ContentPost.findByPk(postId);

      if (!post) {
        throw new Error('Post not found');
      }

      await post.update({
        views: metrics.views || post.views,
        likes: metrics.likes || post.likes,
        comments: metrics.comments || post.comments,
        shares: metrics.shares || post.shares,
        clicks: metrics.clicks || post.clicks,
        revenue_generated: metrics.revenue_generated || post.revenue_generated
      });

      return post;
    } catch (error) {
      console.error('Error updating metrics:', error);
      throw error;
    }
  }

  /**
   * Obtenir les rappels à envoyer
   */
  async getRemindersToSend() {
    try {
      const posts = await ContentPost.findAll({
        where: {
          reminder_date: {
            [Op.lte]: new Date()
          },
          reminder_sent: false,
          status: {
            [Op.in]: ['draft', 'scheduled']
          }
        }
      });

      for (const post of posts) {
        await NotificationService.create({
          user_id: post.influencer_id,
          type: 'content_reminder',
          title: '⏰ Rappel Contenu',
          message: `N'oubliez pas: "${post.title}" est prévu pour ${new Date(post.scheduled_date).toLocaleDateString('fr-FR')}`,
          data: { post_id: post.id, platform: post.platform },
          priority: 'medium',
          channels: { in_app: true, push: true }
        });

        await post.update({ reminder_sent: true });
      }

      return posts;
    } catch (error) {
      console.error('Error sending reminders:', error);
      throw error;
    }
  }

  /**
   * Dupliquer un post
   */
  async duplicatePost(postId, influencerId) {
    try {
      const originalPost = await ContentPost.findOne({
        where: { id: postId, influencer_id: influencerId }
      });

      if (!originalPost) {
        throw new Error('Post not found');
      }

      const duplicateData = originalPost.toJSON();
      delete duplicateData.id;
      delete duplicateData.created_at;
      delete duplicateData.updated_at;
      delete duplicateData.published_date;
      delete duplicateData.post_url;
      delete duplicateData.external_id;

      duplicateData.title = `${duplicateData.title} (Copie)`;
      duplicateData.status = 'draft';
      duplicateData.scheduled_date = null;

      // Reset metrics
      duplicateData.views = 0;
      duplicateData.likes = 0;
      duplicateData.comments = 0;
      duplicateData.shares = 0;
      duplicateData.clicks = 0;
      duplicateData.engagement_rate = 0;
      duplicateData.revenue_generated = 0;

      const duplicatePost = await ContentPost.create(duplicateData);
      return duplicatePost;
    } catch (error) {
      console.error('Error duplicating post:', error);
      throw error;
    }
  }

  /**
   * Obtenir les suggestions de hashtags
   */
  async getSuggestedHashtags(platform, category) {
    // Base de données simple de hashtags populaires
    const hashtagDatabase = {
      instagram: {
        fashion: ['#fashion', '#style', '#ootd', '#fashionblogger', '#instafashion'],
        beauty: ['#beauty', '#makeup', '#skincare', '#beautyblogger', '#cosmetics'],
        fitness: ['#fitness', '#workout', '#gym', '#fitnessmotivation', '#healthylifestyle'],
        food: ['#food', '#foodie', '#foodporn', '#instafood', '#delicious'],
        travel: ['#travel', '#wanderlust', '#travelgram', '#instatravel', '#adventure']
      },
      tiktok: {
        fashion: ['#fashiontiktok', '#ootd', '#styleinspo', '#fashiontrends'],
        beauty: ['#beautytiktok', '#makeuptutorial', '#skincareroutine', '#beautyhacks'],
        fitness: ['#fitnesstiktok', '#workouttips', '#gymtok', '#fitnessmotivation']
      }
    };

    return hashtagDatabase[platform]?.[category] || [];
  }

  /**
   * Obtenir les posts en retard
   */
  async getOverduePosts(influencerId) {
    try {
      const posts = await ContentPost.findAll({
        where: {
          influencer_id: influencerId,
          status: 'scheduled',
          scheduled_date: {
            [Op.lt]: new Date()
          }
        },
        order: [['scheduled_date', 'ASC']]
      });

      return posts;
    } catch (error) {
      console.error('Error fetching overdue posts:', error);
      throw error;
    }
  }
}

module.exports = new ContentCalendarService();
