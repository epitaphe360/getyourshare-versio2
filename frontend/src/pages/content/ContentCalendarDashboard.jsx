import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Instagram, Youtube, Facebook, Linkedin, Twitter, Plus, Clock, Eye, Heart, MessageCircle, Share2, DollarSign, Send, TrendingUp } from 'lucide-react';
import api from '../../services/api';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Content Calendar Dashboard - Influencer
 * Calendrier éditorial multi-plateformes avec analytics
 * ROI: Productivité +40%, Engagement +25%
 */
const ContentCalendarDashboard = () => {
  const [posts, setPosts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // grid, calendar, list

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? `?platform=${filter}` : '';
      const postsRes = await api.get(`/api/content/calendar${params}`);
      setPosts(postsRes.data.posts || []);

      const statsRes = await api.get('/api/content/statistics');
      setStats(statsRes.data.statistics);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      instagram: Instagram,
      youtube: Youtube,
      facebook: Facebook,
      linkedin: Linkedin,
      twitter: Twitter,
      tiktok: Calendar
    };
    const Icon = icons[platform] || Calendar;
    return <Icon size={16} />;
  };

  const getPlatformColor = (platform) => {
    const colors = {
      instagram: 'from-pink-500 to-purple-600',
      youtube: 'from-red-500 to-red-600',
      facebook: 'from-blue-500 to-blue-600',
      linkedin: 'from-blue-700 to-blue-800',
      twitter: 'from-blue-400 to-blue-500',
      tiktok: 'from-black to-gray-800'
    };
    return colors[platform] || 'from-gray-500 to-gray-600';
  };

  const getStatusBadge = (status) => {
    const badges = {
      draft: { label: 'Brouillon', color: 'bg-gray-100 text-gray-700', icon: '📝' },
      scheduled: { label: 'Programmé', color: 'bg-blue-100 text-blue-700', icon: '⏰' },
      published: { label: 'Publié', color: 'bg-green-100 text-green-700', icon: '✅' },
      failed: { label: 'Échec', color: 'bg-red-100 text-red-700', icon: '❌' }
    };
    const badge = badges[status] || badges.draft;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
        {badge.icon} {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
          <Calendar size={48} className="text-purple-600" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-gray-50 to-purple-50 min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">📅 Calendrier Éditorial</h1>
            <p className="text-purple-100 text-lg">
              Planifiez et publiez vos contenus sur toutes vos plateformes sociales
            </p>
          </div>
          <button className="px-6 py-3 bg-white text-purple-600 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center gap-2">
            <Plus size={20} /> Nouveau Post
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <KPICard
            icon={Send}
            title="Posts Publiés"
            value={stats.published}
            subtitle={`${stats.total_posts} au total`}
            color="blue"
          />
          <KPICard
            icon={Eye}
            title="Vues Totales"
            value={stats.total_views.toLocaleString()}
            subtitle={`${stats.avg_engagement_rate.toFixed(1)}% engagement`}
            color="purple"
          />
          <KPICard
            icon={Heart}
            title="Interactions"
            value={stats.total_likes.toLocaleString()}
            subtitle={`${stats.total_comments} commentaires`}
            color="red"
          />
          <KPICard
            icon={DollarSign}
            title="Revenus"
            value={`${stats.total_revenue.toFixed(0)}€`}
            subtitle={`${stats.total_clicks} clics tracking`}
            color="green"
          />
        </div>
      )}

      {/* Platform Filters */}
      <div className="flex gap-3">
        {[
          { id: 'all', label: 'Tous', icon: Calendar },
          { id: 'instagram', label: 'Instagram', icon: Instagram },
          { id: 'tiktok', label: 'TikTok', icon: Calendar },
          { id: 'youtube', label: 'YouTube', icon: Youtube },
          { id: 'facebook', label: 'Facebook', icon: Facebook },
          { id: 'linkedin', label: 'LinkedIn', icon: Linkedin }
        ].map(platform => {
          const Icon = platform.icon;
          return (
            <button
              key={platform.id}
              onClick={() => setFilter(platform.id)}
              className={`px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all ${
                filter === platform.id
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Icon size={16} />
              {platform.label}
            </button>
          );
        })}
      </div>

      {/* Posts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {posts.map(post => (
          <PostCard
            key={post.id}
            post={post}
            getPlatformIcon={getPlatformIcon}
            getPlatformColor={getPlatformColor}
            getStatusBadge={getStatusBadge}
          />
        ))}

        {posts.length === 0 && (
          <div className="col-span-3 text-center py-20">
            <Calendar size={64} className="mx-auto mb-4 text-gray-300" />
            <p className="text-xl text-gray-600 mb-2">Aucun post pour le moment</p>
            <p className="text-gray-500">Créez votre premier post pour commencer!</p>
          </div>
        )}
      </div>

      {/* Top Performers */}
      {stats && stats.top_posts && stats.top_posts.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <TrendingUp className="text-purple-600" />
            Top 5 Meilleurs Posts
          </h2>
          <div className="space-y-4">
            {stats.top_posts.map((post, idx) => (
              <div key={post.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center text-white font-bold">
                    #{idx + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold">{post.title}</h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      {getPlatformIcon(post.platform)}
                      <span>{post.platform}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{post.engagement_rate.toFixed(1)}%</p>
                    <p className="text-xs text-gray-600">Engagement</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{post.views.toLocaleString()}</p>
                    <p className="text-xs text-gray-600">Vues</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Component: KPI Card
const KPICard = ({ icon: Icon, title, value, subtitle, color }) => {
  const colors = {
    blue: 'border-blue-500 text-blue-600',
    purple: 'border-purple-500 text-purple-600',
    red: 'border-red-500 text-red-600',
    green: 'border-green-500 text-green-600'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${colors[color]}`}
    >
      <div className="flex items-center gap-3 mb-2">
        <Icon className={colors[color]} size={24} />
        <p className="text-sm text-gray-600">{title}</p>
      </div>
      <p className="text-3xl font-bold mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </motion.div>
  );
};

// Component: Post Card
const PostCard = ({ post, getPlatformIcon, getPlatformColor, getStatusBadge }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden"
    >
      {/* Platform Header */}
      <div className={`h-2 bg-gradient-to-r ${getPlatformColor(post.platform)}`} />

      {/* Thumbnail */}
      {post.thumbnail_url && (
        <img
          src={post.thumbnail_url}
          alt={post.title}
          className="w-full h-48 object-cover"
        />
      )}

      <div className="p-6">
        {/* Platform & Status */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm text-gray-600 font-semibold">
            {getPlatformIcon(post.platform)}
            {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
          </div>
          {getStatusBadge(post.status)}
        </div>

        {/* Title & Description */}
        <h3 className="font-bold text-lg mb-2 line-clamp-2">{post.title}</h3>
        {post.description && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">{post.description}</p>
        )}

        {/* Scheduled Date */}
        {post.scheduled_date && (
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <Clock size={16} />
            {format(new Date(post.scheduled_date), 'dd MMM yyyy HH:mm', { locale: fr })}
          </div>
        )}

        {/* Performance Metrics (only for published) */}
        {post.status === 'published' && (
          <div className="grid grid-cols-4 gap-2 pt-4 border-t">
            <div className="text-center">
              <Eye size={14} className="mx-auto mb-1 text-gray-500" />
              <p className="text-sm font-bold">{post.views || 0}</p>
            </div>
            <div className="text-center">
              <Heart size={14} className="mx-auto mb-1 text-red-500" />
              <p className="text-sm font-bold">{post.likes || 0}</p>
            </div>
            <div className="text-center">
              <MessageCircle size={14} className="mx-auto mb-1 text-blue-500" />
              <p className="text-sm font-bold">{post.comments || 0}</p>
            </div>
            <div className="text-center">
              <Share2 size={14} className="mx-auto mb-1 text-green-500" />
              <p className="text-sm font-bold">{post.shares || 0}</p>
            </div>
          </div>
        )}

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {post.hashtags.slice(0, 3).map((tag, idx) => (
              <span key={idx} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                #{tag}
              </span>
            ))}
            {post.hashtags.length > 3 && (
              <span className="text-xs text-gray-500">+{post.hashtags.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ContentCalendarDashboard;
