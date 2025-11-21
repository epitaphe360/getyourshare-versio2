import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Video, Play, StopCircle, Calendar, Clock, Users,
  TrendingUp, DollarSign, Package, Plus, Eye, Zap
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const LiveShoppingStudio = ({ userId }) => {
  const [mySessions, setMySessions] = useState([]);
  const [upcomingSessions, setUpcomingSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [products, setProducts] = useState([]);
  const toast = useToast();

  // Create session form
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    platform: 'instagram',
    scheduled_at: '',
    featured_products: []
  });

  useEffect(() => {
    fetchData();
  }, [userId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sessionsRes, upcomingRes, productsRes] = await Promise.all([
        api.get(`/api/ai/live-shopping/my-sessions/${userId}`),
        api.get('/api/ai/live-shopping/upcoming'),
        api.get('/api/marketplace/products?limit=50')
      ]);

      setMySessions(sessionsRes.data.sessions || []);
      setUpcomingSessions(upcomingRes.data.upcoming_lives || []);
      setProducts(productsRes.data.products || []);
    } catch (error) {
      console.error('Erreur chargement lives:', error);
      toast?.error('Erreur chargement lives');
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    if (!formData.title || !formData.scheduled_at || formData.featured_products.length === 0) {
      toast?.error('Remplis tous les champs obligatoires');
      return;
    }

    try {
      await api.post('/api/ai/live-shopping/create', formData, {
        params: { host_id: userId }
      });

      toast?.success('Live créé avec succès!');
      setShowCreateModal(false);
      setFormData({
        title: '',
        description: '',
        platform: 'instagram',
        scheduled_at: '',
        featured_products: []
      });
      fetchData();
    } catch (error) {
      toast?.error('Erreur création live');
    }
  };

  const startSession = async (sessionId) => {
    try {
      await api.post(`/api/ai/live-shopping/${sessionId}/start`);
      toast?.success('Live démarré!');
      fetchData();
    } catch (error) {
      toast?.error('Erreur démarrage live');
    }
  };

  const endSession = async (sessionId) => {
    try {
      const response = await api.post(`/api/ai/live-shopping/${sessionId}/end`);
      toast?.success(`Live terminé! ${response.data.stats.total_orders} ventes`);
      fetchData();
    } catch (error) {
      toast?.error('Erreur fin live');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Programmé' },
      live: { bg: 'bg-red-100', text: 'text-red-700', label: '🔴 EN DIRECT' },
      ended: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Terminé' }
    };
    const badge = badges[status] || badges.scheduled;
    return (
      <span className={`${badge.bg} ${badge.text} px-3 py-1 rounded-full text-sm font-medium`}>
        {badge.label}
      </span>
    );
  };

  const toggleProductSelection = (productId) => {
    setFormData(prev => ({
      ...prev,
      featured_products: prev.featured_products.includes(productId)
        ? prev.featured_products.filter(id => id !== productId)
        : [...prev.featured_products, productId]
    }));
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2].map(i => (
          <div key={i} className="h-40 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
              <Video className="w-7 h-7" />
              Live Shopping Studio
            </h2>
            <p className="text-red-100">
              Booste tes ventes en direct avec +5% de commission!
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition"
          >
            <Plus className="w-5 h-5" />
            Créer Live
          </button>
        </div>
      </div>

      {/* Stats rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Lives Réalisés</p>
              <p className="text-2xl font-bold">
                {mySessions.filter(s => s.status === 'ended').length}
              </p>
            </div>
            <Video className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Vues</p>
              <p className="text-2xl font-bold">
                {mySessions.reduce((sum, s) => sum + (s.total_views || 0), 0)}
              </p>
            </div>
            <Eye className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Ventes Lives</p>
              <p className="text-2xl font-bold">
                {mySessions.reduce((sum, s) => sum + (s.total_orders || 0), 0)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">CA Lives</p>
              <p className="text-2xl font-bold text-green-600">
                {mySessions.reduce((sum, s) => sum + (s.total_sales || 0), 0).toFixed(0)}€
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Mes Lives */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">Mes Sessions Live</h3>

        {mySessions.length > 0 ? (
          <div className="space-y-4">
            {mySessions.map((session) => (
              <motion.div
                key={session.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="border border-gray-200 rounded-lg p-5 hover:border-purple-300 transition"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-bold">{session.title}</h4>
                      {getStatusBadge(session.status)}
                    </div>
                    {session.description && (
                      <p className="text-gray-600 text-sm mb-3">{session.description}</p>
                    )}
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(session.scheduled_at).toLocaleDateString('fr-FR')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {new Date(session.scheduled_at).toLocaleTimeString('fr-FR', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                      <span className="flex items-center gap-1">
                        <Package className="w-4 h-4" />
                        {session.featured_products?.length || 0} produits
                      </span>
                      <span className="flex items-center gap-1">
                        <Zap className="w-4 h-4 text-yellow-500" />
                        Boost: +{session.commission_boost_percentage}%
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    {session.status === 'scheduled' && (
                      <button
                        onClick={() => startSession(session.id)}
                        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition"
                      >
                        <Play className="w-4 h-4" />
                        Démarrer
                      </button>
                    )}
                    {session.status === 'live' && (
                      <button
                        onClick={() => endSession(session.id)}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition"
                      >
                        <StopCircle className="w-4 h-4" />
                        Terminer
                      </button>
                    )}
                  </div>
                </div>

                {/* Stats si terminé */}
                {session.status === 'ended' && (
                  <div className="grid grid-cols-4 gap-4 pt-4 border-t">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">{session.viewers_count || 0}</p>
                      <p className="text-xs text-gray-600">Viewers</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">{session.peak_viewers || 0}</p>
                      <p className="text-xs text-gray-600">Pic</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{session.total_orders || 0}</p>
                      <p className="text-xs text-gray-600">Ventes</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">
                        {(session.total_sales || 0).toFixed(0)}€
                      </p>
                      <p className="text-xs text-gray-600">CA</p>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Video className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">Aucune session live créée</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Créer ton premier live
            </button>
          </div>
        )}
      </div>

      {/* Prochains Lives (communauté) */}
      {upcomingSessions.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Prochains Lives de la Communauté</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {upcomingSessions.map((session) => (
              <div
                key={session.session_id}
                className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition"
              >
                <h4 className="font-bold mb-2">{session.title}</h4>
                <p className="text-sm text-gray-600 mb-2">Par {session.host_username}</p>
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                  <Calendar className="w-4 h-4" />
                  {new Date(session.scheduled_at).toLocaleDateString('fr-FR')}
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">{session.featured_products_count} produits</span>
                  <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                    Boost {session.commission_boost}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal Création */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
          >
            <h3 className="text-2xl font-bold mb-6">Créer une Session Live</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titre du Live *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="Ex: Découverte Parfums Orientaux"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Plateforme *
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({...formData, platform: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  >
                    <option value="instagram">Instagram</option>
                    <option value="tiktok">TikTok</option>
                    <option value="youtube">YouTube</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date & Heure *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.scheduled_at}
                    onChange={(e) => setFormData({...formData, scheduled_at: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Produits à Présenter * ({formData.featured_products.length} sélectionnés)
                </label>
                <div className="border border-gray-300 rounded-lg p-4 max-h-60 overflow-y-auto">
                  {products.map((product) => (
                    <label
                      key={product.id}
                      className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={formData.featured_products.includes(product.id)}
                        onChange={() => toggleProductSelection(product.id)}
                        className="w-4 h-4"
                      />
                      <span className="flex-1">
                        {product.name} - {product.price}€
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800 flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  <span>
                    <strong>Bonus Live:</strong> +5% de commission sur toutes les ventes pendant le live!
                  </span>
                </p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 border border-gray-300 hover:bg-gray-50 px-6 py-3 rounded-lg font-medium transition"
              >
                Annuler
              </button>
              <button
                onClick={createSession}
                className="flex-1 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white px-6 py-3 rounded-lg font-medium transition"
              >
                Créer Live
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default LiveShoppingStudio;
