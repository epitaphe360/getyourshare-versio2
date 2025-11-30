import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../utils/api';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, TrendingUp, Tag, ExternalLink, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

const ProductRecommendations = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchRecommendations();
    }
  }, [user]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null); // Clear previous errors
    try {
      const response = await api.get(`/api/ai/product-recommendations/${user.id}`);
      setRecommendations(response.data.recommendations || []);
      setError(null); // Ensure error is cleared on success
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Impossible de charger les recommandations.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto text-indigo-600 mb-4" size={32} />
          <p className="text-gray-500">L'IA analyse votre profil pour trouver les meilleurs produits...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="text-indigo-600" size={24} />
            Recommandations Intelligentes
          </h2>
          <p className="text-sm text-gray-500">Produits sélectionnés par l'IA pour maximiser vos revenus</p>
        </div>
        <button 
          onClick={fetchRecommendations} 
          className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition"
          title="Rafraîchir"
        >
          <RefreshCw size={20} />
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {recommendations.length === 0 && !error ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
          <Sparkles className="mx-auto text-gray-300 mb-4" size={48} />
          <p className="text-gray-500">Aucune recommandation pour le moment.</p>
          <p className="text-sm text-gray-400">Continuez à utiliser la plateforme pour que l'IA apprenne de vos préférences.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((product, index) => (
            <motion.div
              key={product.product_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-300"
            >
              <div className="relative h-48 bg-gray-200">
                {product.image_url ? (
                  <img 
                    src={product.image_url} 
                    alt={product.product_name} 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <Tag size={48} />
                  </div>
                )}
                <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full text-xs font-bold text-indigo-600 shadow-sm flex items-center gap-1">
                  <Sparkles size={12} />
                  {product.match_score}% Match
                </div>
              </div>

              <div className="p-5">
                <div className="text-xs text-gray-500 mb-1">{product.merchant_name}</div>
                <h3 className="font-bold text-gray-900 mb-2 line-clamp-1">{product.product_name}</h3>
                
                <div className="flex justify-between items-end mb-4">
                  <div>
                    <div className="text-xs text-gray-500">Prix</div>
                    <div className="font-semibold text-gray-900">{Number(product.price).toFixed(2)} €</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">Commission Est.</div>
                    <div className="font-bold text-green-600">~{Number(product.estimated_commission).toFixed(2)} €</div>
                  </div>
                </div>

                <div className="bg-indigo-50 p-3 rounded-lg mb-4">
                  <div className="flex items-start gap-2">
                    <TrendingUp size={16} className="text-indigo-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-indigo-800 leading-relaxed">
                      {product.reason}
                    </p>
                  </div>
                </div>

                {product.product_url && product.product_url.startsWith('/') ? (
                  <Link 
                    to={product.product_url}
                    className="w-full py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition flex items-center justify-center gap-2 text-sm font-medium"
                  >
                    Voir l'offre <ExternalLink size={16} />
                  </Link>
                ) : (
                  <a 
                    href={product.product_url || '#'}
                    className="w-full py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition flex items-center justify-center gap-2 text-sm font-medium"
                    target={product.product_url && !product.product_url.startsWith('#') ? "_blank" : "_self"}
                    rel="noopener noreferrer"
                  >
                    Voir l'offre <ExternalLink size={16} />
                  </a>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductRecommendations;
