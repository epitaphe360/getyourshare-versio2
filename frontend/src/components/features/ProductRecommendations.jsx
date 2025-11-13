import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles, TrendingUp, DollarSign, Link as LinkIcon,
  RefreshCw, Check, Star, Target
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const ProductRecommendations = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [generating, setGenerating] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/ai/product-recommendations/${userId}`);
      setRecommendations(response.data.recommendations || []);
    } catch (error) {
      toast?.error('Erreur chargement recommandations');
    } finally {
      setLoading(false);
    }
  };

  const generateNewRecommendations = async () => {
    try {
      setGenerating(true);
      toast?.info('Génération de nouvelles recommandations...');
      await api.post(`/api/ai/product-recommendations/${userId}?force_refresh=true`);
      await fetchRecommendations();
      toast?.success('Nouvelles recommandations générées!');
    } catch (error) {
      toast?.error('Erreur génération recommandations');
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateAffiliateLink = async (productId, recommendationId) => {
    try {
      // Tracker le clic
      await api.post(`/api/ai/product-recommendations/${recommendationId}/click`);

      // Créer lien d'affiliation (endpoint existant)
      const response = await api.post('/api/affiliate-links', {
        product_id: productId,
        influencer_id: userId
      });

      if (response.data.affiliate_link) {
        navigator.clipboard.writeText(response.data.affiliate_link.url);
        toast?.success('Lien copié!');
      }
    } catch (error) {
      toast?.error('Erreur création lien');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Bon Match';
    if (score >= 40) return 'Match Correct';
    return 'Match Faible';
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-purple-500" />
            Produits Recommandés Pour Toi
          </h2>
          <p className="text-gray-600 mt-1">
            Sélectionnés par IA selon ton profil et audience
          </p>
        </div>
        <button
          onClick={generateNewRecommendations}
          disabled={generating}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 ${generating ? 'animate-spin' : ''}`} />
          Actualiser
        </button>
      </div>

      {/* Recommendations Grid */}
      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {recommendations.map((rec, index) => (
            <motion.div
              key={rec.product_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-lg hover:shadow-xl transition overflow-hidden"
            >
              {/* Product Image */}
              <div className="relative h-48 bg-gradient-to-br from-purple-100 to-pink-100">
                {rec.image_url ? (
                  <img
                    src={rec.image_url}
                    alt={rec.product_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Target className="w-20 h-20 text-purple-300" />
                  </div>
                )}

                {/* Match Score Badge */}
                <div className="absolute top-3 right-3">
                  <div className={`${getScoreColor(rec.match_score)} px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1`}>
                    <Star className="w-4 h-4" />
                    {rec.match_score}%
                  </div>
                </div>
              </div>

              {/* Product Info */}
              <div className="p-5">
                {/* Title & Category */}
                <div className="mb-3">
                  <h3 className="text-xl font-bold mb-1">{rec.product_name}</h3>
                  <p className="text-sm text-gray-500">
                    Par {rec.merchant_name} • {rec.category}
                  </p>
                </div>

                {/* Match Label */}
                <div className="mb-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getScoreColor(rec.match_score)}`}>
                    <Check className="w-3 h-3" />
                    {getScoreLabel(rec.match_score)}
                  </span>
                </div>

                {/* Match Reasons */}
                {rec.match_reasons && rec.match_reasons.length > 0 && (
                  <div className="mb-4 space-y-1">
                    {rec.match_reasons.slice(0, 2).map((reason, idx) => (
                      <p key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-green-500 mt-1">✓</span>
                        <span>{reason}</span>
                      </p>
                    ))}
                  </div>
                )}

                {/* Price & Commission */}
                <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-xs text-gray-500">Prix</p>
                    <p className="text-lg font-bold">{rec.price.toFixed(2)}€</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Commission estimée</p>
                    <p className="text-lg font-bold text-green-600">
                      ~{rec.estimated_commission.toFixed(2)}€
                    </p>
                  </div>
                </div>

                {/* Commission Rate */}
                <div className="mb-4 p-2 bg-blue-50 rounded-lg text-center">
                  <p className="text-sm text-blue-700">
                    <TrendingUp className="w-4 h-4 inline mr-1" />
                    {rec.commission_rate}% de commission
                  </p>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => handleCreateAffiliateLink(rec.product_id, rec.product_id)}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition"
                >
                  <LinkIcon className="w-5 h-5" />
                  Créer Lien d'Affiliation
                </button>

                {/* Additional Info */}
                <div className="mt-3 text-center">
                  <p className="text-xs text-gray-500">
                    1 clic pour créer ton lien et commencer à gagner
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white rounded-xl shadow">
          <Sparkles className="w-20 h-20 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-700 mb-2">
            Aucune recommandation pour le moment
          </h3>
          <p className="text-gray-500 mb-6">
            Clique sur "Actualiser" pour générer des recommandations IA
          </p>
          <button
            onClick={generateNewRecommendations}
            disabled={generating}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg inline-flex items-center gap-2 transition disabled:opacity-50"
          >
            <Sparkles className="w-5 h-5" />
            Générer Recommandations
          </button>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6">
        <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
          <Star className="w-6 h-6 text-purple-600" />
          Comment sont calculées les recommandations?
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">🎯</div>
            <h4 className="font-bold mb-1 text-sm">Niche Compatible</h4>
            <p className="text-xs text-gray-600">
              Produits alignés avec ta niche et audience
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">📈</div>
            <h4 className="font-bold mb-1 text-sm">Performance Historique</h4>
            <p className="text-xs text-gray-600">
              Basé sur tes ventes passées similaires
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">💰</div>
            <h4 className="font-bold mb-1 text-sm">Prix Adapté</h4>
            <p className="text-xs text-gray-600">
              Compatible avec le budget de ton audience
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductRecommendations;
