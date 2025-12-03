import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Star, ThumbsUp, ThumbsDown, AlertCircle, CheckCircle, XCircle, MessageSquare, TrendingUp, BarChart3, Shield, Zap, Eye } from 'lucide-react';
import api from '../../services/api';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Review Management Dashboard - Merchant
 * Gestion avancée des avis avec modération IA
 * ROI: Réputation +30%, Conversion +20%
 */
const ReviewManagementDashboard = () => {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      let params = '';
      if (filter === 'pending') params = '?status=pending';
      if (filter === 'flagged') params = '?status=flagged';
      if (filter === 'negative') params = '?rating=1,2';
      if (filter === 'no_response') params = '?no_response=true';

      const reviewsRes = await api.get(`/api/reviews/merchant${params}`);
      setReviews(reviewsRes.data.reviews || []);

      const statsRes = await api.get('/api/reviews/statistics');
      setStats(statsRes.data.statistics);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRatingStars = (rating) => {
    return '⭐'.repeat(rating);
  };

  const getSentimentBadge = (sentiment) => {
    const badges = {
      very_positive: { label: '😄 Très positif', color: 'bg-green-100 text-green-700' },
      positive: { label: '😊 Positif', color: 'bg-green-100 text-green-600' },
      neutral: { label: '😐 Neutre', color: 'bg-gray-100 text-gray-700' },
      negative: { label: '😞 Négatif', color: 'bg-orange-100 text-orange-700' },
      very_negative: { label: '😡 Très négatif', color: 'bg-red-100 text-red-700' }
    };
    return badges[sentiment] || badges.neutral;
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { label: '⏳ En attente', color: 'bg-yellow-100 text-yellow-700', icon: AlertCircle },
      approved: { label: '✅ Approuvé', color: 'bg-green-100 text-green-700', icon: CheckCircle },
      rejected: { label: '❌ Rejeté', color: 'bg-red-100 text-red-700', icon: XCircle },
      flagged: { label: '🚩 Signalé', color: 'bg-orange-100 text-orange-700', icon: AlertCircle },
      spam: { label: '🚫 Spam', color: 'bg-gray-100 text-gray-700', icon: XCircle }
    };
    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
        <Icon size={14} />
        {badge.label}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
          <Star size={48} className="text-yellow-600" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-gray-50 to-yellow-50 min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-yellow-500 to-orange-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">⭐ Gestion des Avis</h1>
            <p className="text-yellow-100 text-lg">
              Modération automatique par IA • Améliorez votre réputation
            </p>
          </div>
          <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6">
            <Shield size={64} />
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500">
            <Star className="text-yellow-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.avg_rating}</p>
            <p className="text-sm text-gray-600">Note moyenne</p>
            <p className="text-xs text-gray-500 mt-1">{stats.total} avis</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <CheckCircle className="text-green-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.by_rating[5] + stats.by_rating[4]}</p>
            <p className="text-sm text-gray-600">Avis positifs (4-5⭐)</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
            <AlertCircle className="text-red-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.by_rating[1] + stats.by_rating[2]}</p>
            <p className="text-sm text-gray-600">Avis négatifs (1-2⭐)</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <MessageSquare className="text-blue-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.response_rate}%</p>
            <p className="text-sm text-gray-600">Taux de réponse</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
            <Shield className="text-purple-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.pending + stats.flagged}</p>
            <p className="text-sm text-gray-600">À modérer</p>
          </div>
        </div>
      )}

      {/* Rating Distribution */}
      {stats && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
            <BarChart3 className="text-yellow-600" />
            Distribution des Notes
          </h2>
          <div className="space-y-3">
            {[5, 4, 3, 2, 1].map(rating => {
              const count = stats.by_rating[rating] || 0;
              const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;
              return (
                <div key={rating} className="flex items-center gap-4">
                  <span className="text-sm font-semibold w-12">{rating} ⭐</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className={`h-4 rounded-full ${rating >= 4 ? 'bg-green-500' : rating === 3 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold w-16 text-right">{count} ({percentage.toFixed(0)}%)</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3">
        {[
          { id: 'all', label: 'Tous', icon: '📋' },
          { id: 'pending', label: 'En attente', icon: '⏳' },
          { id: 'flagged', label: 'Signalés', icon: '🚩' },
          { id: 'negative', label: 'Négatifs', icon: '😞' },
          { id: 'no_response', label: 'Sans réponse', icon: '💬' }
        ].map(f => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all ${
              filter === f.id
                ? 'bg-yellow-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <span>{f.icon}</span>
            {f.label}
          </button>
        ))}
      </div>

      {/* Reviews List */}
      <div className="space-y-4">
        {reviews.map(review => {
          const sentimentBadge = getSentimentBadge(review.sentiment);
          return (
            <motion.div
              key={review.id}
              whileHover={{ scale: 1.01 }}
              className="bg-white rounded-xl shadow-lg p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getRatingStars(review.rating)}</span>
                    <span className="font-bold text-lg">{review.customer_name}</span>
                    {review.verified_purchase && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-semibold">
                        ✓ Achat vérifié
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mb-3">
                    {format(new Date(review.created_at), 'dd MMMM yyyy', { locale: fr })}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {getStatusBadge(review.status)}
                  {review.sentiment && (
                    <span className={`text-xs px-2 py-1 rounded-full ${sentimentBadge.color}`}>
                      {sentimentBadge.label}
                    </span>
                  )}
                </div>
              </div>

              {review.title && (
                <h3 className="font-bold text-lg mb-2">{review.title}</h3>
              )}

              <p className="text-gray-700 mb-4">{review.comment}</p>

              {/* AI Analysis */}
              {review.auto_moderated && (
                <div className="bg-purple-50 border-l-4 border-purple-500 p-4 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="text-purple-600" size={16} />
                    <span className="font-semibold text-purple-900 text-sm">Analyse IA</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">Score de confiance:</span>
                      <span className="ml-2 font-bold">{(review.moderation_score * 100).toFixed(0)}%</span>
                    </div>
                    {review.spam_score > 0.5 && (
                      <div>
                        <span className="text-gray-600">Probabilité spam:</span>
                        <span className="ml-2 font-bold text-red-600">{(review.spam_score * 100).toFixed(0)}%</span>
                      </div>
                    )}
                    {review.detected_issues && review.detected_issues.length > 0 && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Problèmes détectés:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {review.detected_issues.map((issue, idx) => (
                            <span key={idx} className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                              {issue}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Response */}
              {review.has_response && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="text-blue-600" size={16} />
                    <span className="font-semibold text-blue-900 text-sm">
                      Votre réponse {review.auto_response && '(IA)'}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm">{review.response_text}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {format(new Date(review.response_date), 'dd MMM yyyy', { locale: fr })}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                {review.status === 'pending' && (
                  <>
                    <button className="px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold hover:bg-green-200 transition-all">
                      ✅ Approuver
                    </button>
                    <button className="px-4 py-2 bg-red-100 text-red-700 rounded-lg font-semibold hover:bg-red-200 transition-all">
                      ❌ Rejeter
                    </button>
                  </>
                )}
                {!review.has_response && review.status === 'approved' && (
                  <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-semibold hover:bg-blue-200 transition-all">
                    💬 Répondre
                  </button>
                )}
                {review.status === 'approved' && (
                  <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-all">
                    👁️ Voir le produit
                  </button>
                )}
              </div>

              {/* Interaction Stats */}
              {review.helpful_count > 0 && (
                <div className="flex items-center gap-4 mt-4 pt-4 border-t text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <ThumbsUp size={14} />
                    <span>{review.helpful_count} personnes ont trouvé cet avis utile</span>
                  </div>
                  {review.report_count > 0 && (
                    <div className="flex items-center gap-2 text-red-600">
                      <AlertCircle size={14} />
                      <span>{review.report_count} signalements</span>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          );
        })}

        {reviews.length === 0 && (
          <div className="text-center py-20 bg-white rounded-2xl shadow-lg">
            <Star size={64} className="mx-auto mb-4 text-gray-300" />
            <p className="text-xl text-gray-600 mb-2">Aucun avis dans cette catégorie</p>
            <p className="text-gray-500">Les avis apparaîtront ici une fois reçus</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewManagementDashboard;
