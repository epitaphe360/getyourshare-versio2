import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import StatCard from '../../components/common/StatCard';
import Card from '../../components/common/Card';
import SkeletonDashboard from '../../components/common/SkeletonLoader';
import EmptyState from '../../components/common/EmptyState';
import GamificationWidget from '../../components/GamificationWidget';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import {
  DollarSign, ShoppingBag, Users, TrendingUp,
  Package, Eye, Target, Award, Plus, Search, FileText, Settings, RefreshCw,
  UserCheck, Clock, CheckCircle, XCircle, TrendingDown, Gift, Video, UserPlus, Calculator, ShieldCheck
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const MerchantDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sentRequests, setSentRequests] = useState([]);
  const [showCounterOfferModal, setShowCounterOfferModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);

  // Killer Features States
  const [referralData, setReferralData] = useState(null);
  const [productLives, setProductLives] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      // Utiliser Promise.allSettled au lieu de Promise.all
      const results = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/marketplace/products'),
        api.get('/api/analytics/merchant/sales-chart'),
        api.get('/api/analytics/merchant/performance'),
        api.get('/api/subscriptions/current'),
        api.get('/api/collaborations/requests/sent'),
        // Killer Features
        api.get(`/api/referrals/dashboard/${user?.id}`),
        api.get('/api/ai/live-shopping/upcoming?limit=5')
      ]);

      const [statsRes, productsRes, salesChartRes, performanceRes, subscriptionRes, sentRequestsRes, referralRes, livesRes] = results;

      // Gérer les statistiques
      if (performanceRes.status === 'fulfilled') {
        const performance = performanceRes.value.data;
        setStats({
          total_sales: performance.total_sales || 0,
          total_revenue: performance.total_revenue || 0,
          products_count: performance.products_count || 0,
          affiliates_count: performance.affiliates_count || 0,
          total_clicks: performance.total_clicks || 0,
          conversion_rate: performance.conversion_rate || 0,
          roi: performance.total_revenue > 0 ? ((performance.total_revenue / (performance.total_revenue * 0.1)) * 100) : 0,
          performance: {
            conversion_rate: performance.conversion_rate || 0,
            engagement_rate: performance.engagement_rate || 0,
            satisfaction_rate: performance.satisfaction_rate || 0,
            monthly_goal_progress: performance.monthly_goal_progress || 0
          }
        });
      } else {
        console.error('Error loading stats:', performanceRes.reason);
        toast.error('Erreur lors du chargement des statistiques');
        setStats({
          total_sales: 0,
          products_count: 0,
          affiliates_count: 0,
          roi: 0,
          performance: {
            conversion_rate: 0,
            engagement_rate: 0,
            satisfaction_rate: 0,
            monthly_goal_progress: 0
          }
        });
      }

      // Gérer l'abonnement
      if (subscriptionRes.status === 'fulfilled') {
        setSubscription(subscriptionRes.value.data);
      } else {
        console.error('Error loading subscription:', subscriptionRes.reason);
        // Abonnement par défaut gratuit
        setSubscription({
          plan_name: 'Freemium',
          max_products: 5,
          max_campaigns: 1,
          max_affiliates: 10,
          commission_fee: 0,
          status: 'active'
        });
      }

      // Gérer les produits
      if (productsRes.status === 'fulfilled') {
        setProducts(productsRes.value.data.products || []);
      } else {
        console.error('Error loading products:', productsRes.reason);
        setProducts([]);
      }

      // Gérer les données de ventes
      if (salesChartRes.status === 'fulfilled') {
        const chartData = salesChartRes.value.data.data || [];
        setSalesData(chartData.map(day => ({
          name: day.formatted_date || day.date,
          sales: day.sales || 0,
          orders: day.orders || 0
        })));
      } else {
        console.error('Error loading sales chart:', salesChartRes.reason);
        setSalesData([]);
      }

      // Gérer les demandes de collaboration envoyées
      if (sentRequestsRes && sentRequestsRes.status === 'fulfilled') {
        setSentRequests(sentRequestsRes.value.data.requests || []);
      } else {
        setSentRequests([]);
      }

      // Killer Features Data
      // Referral Program
      if (referralRes && referralRes.status === 'fulfilled') {
        setReferralData(referralRes.value.data);
      }

      // Live Shopping - Filter lives featuring merchant's products
      if (livesRes && livesRes.status === 'fulfilled') {
        setProductLives(livesRes.value.data.upcoming_lives || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const acceptCounterOffer = async (requestId) => {
    try {
      const request = sentRequests.find(r => r.id === requestId);
      await api.put(`/api/collaborations/requests/${requestId}/accept`, {
        commission: request.counter_commission
      });
      toast.success('Contre-offre acceptée ! L\'influenceur doit maintenant signer le contrat.');
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error accepting counter offer:', error);
      toast.error('Erreur lors de l\'acceptation de la contre-offre');
    }
  };

  const rejectCounterOffer = async (requestId) => {
    try {
      await api.put(`/api/collaborations/requests/${requestId}/reject`, {
        message: 'Contre-offre refusée'
      });
      toast.success('Contre-offre refusée');
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error rejecting counter offer:', error);
      toast.error('Erreur lors du refus de la contre-offre');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: <Clock size={14} />, text: 'En attente' },
      accepted: { color: 'bg-blue-100 text-blue-800', icon: <CheckCircle size={14} />, text: 'Accepté - En attente de signature' },
      counter_offer: { color: 'bg-orange-100 text-orange-800', icon: <TrendingDown size={14} />, text: 'Contre-offre' },
      rejected: { color: 'bg-red-100 text-red-800', icon: <XCircle size={14} />, text: 'Refusé' },
      active: { color: 'bg-green-100 text-green-800', icon: <CheckCircle size={14} />, text: 'Actif' },
      expired: { color: 'bg-gray-100 text-gray-800', icon: <XCircle size={14} />, text: 'Expiré' }
    };
    
    const badge = badges[status] || badges.pending;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.icon}
        {badge.text}
      </span>
    );
  };

  if (loading) {
    return <SkeletonDashboard />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => {
              setLoading(true);
              fetchData();
            }}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 mx-auto"
          >
            <RefreshCw size={18} />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Entreprise</h1>
          <p className="text-gray-600 mt-2">
            Bienvenue {user?.first_name} ! Suivez vos performances en temps réel
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => fetchData()}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition flex items-center gap-2"
            title="Rafraîchir les données"
          >
            <RefreshCw size={18} />
          </button>
          <button
            onClick={() => navigate('/analytics-pro')}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition flex items-center gap-2"
            title="Analytics Pro avec IA"
          >
            <Award size={18} />
            Analytics Pro
          </button>
          <button
            onClick={() => navigate('/features?tab=roi')}
            className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 transition flex items-center gap-2"
            title="Calculateur ROI"
          >
            <Calculator size={18} />
            Calculateur ROI
          </button>
          <button
            onClick={() => navigate('/matching')}
            className="px-4 py-2 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-lg hover:from-pink-600 hover:to-rose-600 transition flex items-center gap-2"
            title="Matching Influenceurs Tinder"
          >
            <Target size={18} />
            Matching
          </button>
          <button
            onClick={() => navigate('/campaigns/create')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2"
          >
            <Plus size={18} />
            Créer Campagne
          </button>
          <button
            onClick={() => navigate('/influencers/search')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
          >
            <Search size={18} />
            Rechercher Influenceurs
          </button>
          <button
            onClick={() => navigate('/products/create')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <Plus size={18} />
            Ajouter Produit
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0 }}
        >
          <StatCard
            title="Chiffre d'Affaires"
            value={<CountUp end={typeof stats?.total_revenue === 'number' ? stats.total_revenue : 0} duration={2.5} decimals={2} separator=" " suffix="€" />}
            isCurrency={false}
            icon={<DollarSign className="text-green-600" size={24} />}
            trend={stats?.sales_growth || 0}
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <StatCard
            title="Produits Actifs"
            value={<CountUp end={typeof stats?.products_count === 'number' ? stats.products_count : products.length || 0} duration={2} />}
            icon={<Package className="text-indigo-600" size={24} />}
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <StatCard
            title="Affiliés Actifs"
            value={<CountUp end={typeof stats?.affiliates_count === 'number' ? stats.affiliates_count : 0} duration={2} />}
            icon={<Users className="text-purple-600" size={24} />}
            trend={stats?.affiliates_growth || 0}
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <StatCard
            title="ROI Marketing"
            value={<CountUp end={typeof stats?.roi === 'number' && !isNaN(stats.roi) ? stats.roi : 0} duration={2} decimals={1} suffix="%" />}
            icon={<TrendingUp className="text-orange-600" size={24} />}
            trend={stats?.roi_growth || 0}
          />
        </motion.div>
      </div>

      {/* Subscription Card */}
      {subscription && (
        <Card 
          title="Mon Abonnement" 
          icon={<Settings size={20} />}
          className="border-l-4 border-indigo-600"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                  subscription.plan_name === 'Enterprise' ? 'bg-purple-100 text-purple-800' :
                  subscription.plan_name === 'Premium' ? 'bg-indigo-100 text-indigo-800' :
                  subscription.plan_name === 'Standard' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {subscription.plan_name}
                </span>
                <p className="text-sm text-gray-500 mt-1">
                  Statut: <span className={`font-medium ${subscription.status === 'active' ? 'text-green-600' : 'text-red-600'}`}>
                    {subscription.status === 'active' ? 'Actif' : 'Inactif'}
                  </span>
                </p>
              </div>
              <button
                onClick={() => navigate('/pricing')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
              >
                Améliorer mon Plan
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.products_count || 0} / {subscription.max_products || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Produits</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.products_count || 0) / (subscription.max_products || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.products_count || 0) / (subscription.max_products || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.campaigns_count || 0} / {subscription.max_campaigns || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Campagnes</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.campaigns_count || 0) / (subscription.max_campaigns || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.campaigns_count || 0) / (subscription.max_campaigns || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats?.affiliates_count || 0} / {subscription.max_affiliates || '∞'}
                </div>
                <div className="text-sm text-gray-500 mt-1">Affiliés</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ((stats?.affiliates_count || 0) / (subscription.max_affiliates || 1)) > 0.8 ? 'bg-red-500' : 'bg-indigo-600'
                    }`}
                    style={{ width: `${Math.min(((stats?.affiliates_count || 0) / (subscription.max_affiliates || 1)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {subscription.commission_fee > 0 && (
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Frais de commission:</span> {subscription.commission_fee}%
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Gamification Widget */}
      <GamificationWidget userId={user?.id} userType="merchant" />

      {/* KILLER FEATURES WIDGETS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Programme de Parrainage Viral */}
        <Card
          title="🎁 Programme de Parrainage"
          icon={<Gift size={20} className="text-purple-600" />}
          className="border-l-4 border-purple-500"
        >
          {referralData ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-sm text-purple-600 font-medium">Marchands Parrainés</div>
                  <div className="text-2xl font-bold text-purple-900 mt-1">
                    <UserPlus className="inline mr-1" size={20} />
                    {referralData.network?.total_network || 0}
                  </div>
                  <div className="text-xs text-purple-600 mt-1">
                    Niveau 1: {referralData.network?.level1_count || 0} • Niveau 2: {referralData.network?.level2_count || 0}
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-green-600 font-medium">Bonus ce Mois</div>
                  <div className="text-2xl font-bold text-green-900 mt-1">
                    {referralData.earnings?.this_month_earnings?.toFixed(2) || '0.00'} €
                  </div>
                  <div className="text-xs text-green-600 mt-1">
                    Badge: {referralData.earnings?.badge_level || 'bronze'}
                    {referralData.earnings?.badge_level === 'diamond' ? ' 💎' :
                     referralData.earnings?.badge_level === 'platinum' ? ' 🏆' :
                     referralData.earnings?.badge_level === 'gold' ? ' 🥇' : ' 🥉'}
                  </div>
                </div>
              </div>
              {referralData.referral_code?.has_code && (
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-3 rounded-lg">
                  <div className="text-sm font-medium text-purple-900 mb-1">Ton Code:</div>
                  <div className="flex items-center gap-2">
                    <code className="bg-white px-3 py-1 rounded text-purple-600 font-bold text-lg">
                      {referralData.referral_code.code}
                    </code>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(referralData.referral_code.share_link);
                        toast?.success('Lien copié!');
                      }}
                      className="text-purple-600 hover:text-purple-800"
                    >
                      📋
                    </button>
                  </div>
                  <div className="text-xs text-purple-700 mt-2">
                    Partage ce code avec d'autres commerçants!
                  </div>
                </div>
              )}
              <button
                onClick={() => navigate('/features?tab=referral')}
                className="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium"
              >
                Voir Dashboard Complet →
              </button>
            </div>
          ) : (
            <div className="text-center py-6">
              <Gift size={48} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500 mb-3">Active ton programme de parrainage!</p>
              <p className="text-sm text-gray-400 mb-3">Gagne des bonus en parrainant d'autres commerçants</p>
              <button
                onClick={() => navigate('/features?tab=referral')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm"
              >
                Démarrer →
              </button>
            </div>
          )}
        </Card>

        {/* Live Shopping - Produits en Live */}
        <Card
          title="🎥 Tes Produits en Live Shopping"
          icon={<Video size={20} className="text-red-600" />}
          className="border-l-4 border-red-500"
        >
          {productLives.length > 0 ? (
            <div className="space-y-3">
              <div className="bg-red-50 p-3 rounded-lg">
                <div className="text-sm text-red-900 font-medium mb-2">
                  📅 Lives à venir ({productLives.length})
                </div>
                {productLives.map((live, idx) => (
                  <div key={idx} className="bg-white p-2 rounded mb-2 border-l-4 border-red-400">
                    <div className="text-sm font-semibold text-gray-900">{live.title}</div>
                    <div className="text-xs text-gray-500">
                      Influenceur: {live.host_username} • {live.platform}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {live.featured_products_count} produit(s) mis en avant
                    </div>
                    <div className="text-xs text-red-600 font-medium mt-1">
                      Boost commission: {live.commission_boost} 🔥
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => navigate('/features?tab=live')}
                className="w-full py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-medium"
              >
                Voir Tous les Lives →
              </button>
            </div>
          ) : (
            <div className="text-center py-6">
              <Video size={48} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500 mb-3">Aucun live prévu pour tes produits</p>
              <div className="bg-yellow-50 p-3 rounded-lg mb-3 text-xs text-yellow-800">
                Les influenceurs peuvent créer des lives pour promouvoir tes produits et augmenter les ventes!
              </div>
              <button
                onClick={() => navigate('/influencers/search')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
              >
                Trouver des Influenceurs →
              </button>
            </div>
          )}
        </Card>
      </div>

      {/* Collaboration Requests Section */}
      {sentRequests && sentRequests.length > 0 && (
        <Card 
          title={`Demandes de Collaboration Envoyées (${sentRequests.length})`} 
          icon={<UserCheck size={20} />}
          className="border-l-4 border-purple-600"
        >
          <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-3">
            <ShieldCheck className="text-blue-600" size={24} />
            <div>
              <h4 className="text-sm font-bold text-blue-800">Tiers de Confiance (Escrow)</h4>
              <p className="text-xs text-blue-700">Vos fonds sont sécurisés et ne sont versés à l'influenceur qu'une fois le travail validé.</p>
            </div>
          </div>
          <div className="space-y-4">
            {sentRequests.map(request => (
              <div 
                key={request.id} 
                className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-semibold text-gray-900">
                        Envoyée à: {request.influencer_name || 'Influenceur'}
                      </h4>
                      {getStatusBadge(request.status)}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">Produits:</span>
                        <span className="ml-2 font-medium text-gray-900">
                          {request.products?.length || 0}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Commission proposée:</span>
                        <span className="ml-2 font-medium text-green-600">
                          {request.proposed_commission}%
                        </span>
                      </div>
                      {request.counter_commission && (
                        <div>
                          <span className="text-gray-600">Contre-offre:</span>
                          <span className="ml-2 font-medium text-orange-600">
                            {request.counter_commission}%
                          </span>
                        </div>
                      )}
                    </div>

                    {request.message && (
                      <div className="mt-3 p-3 bg-gray-50 rounded text-sm text-gray-700">
                        <strong>Votre message:</strong> {request.message}
                      </div>
                    )}

                    {request.counter_message && (
                      <div className="mt-2 p-3 bg-orange-50 rounded text-sm text-orange-900 border border-orange-200">
                        <strong>Message de l'influenceur:</strong> {request.counter_message}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions for counter-offers */}
                {request.status === 'counter_offer' && (
                  <div className="flex gap-2 mt-3 pt-3 border-t">
                    <button
                      onClick={() => acceptCounterOffer(request.id)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2"
                    >
                      <CheckCircle size={18} />
                      Accepter la contre-offre ({request.counter_commission}%)
                    </button>
                    <button
                      onClick={() => rejectCounterOffer(request.id)}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center justify-center gap-2"
                    >
                      <XCircle size={18} />
                      Refuser
                    </button>
                  </div>
                )}

                {/* Info for other statuses */}
                {request.status === 'accepted' && (
                  <div className="mt-3 p-3 bg-blue-50 rounded text-sm text-blue-800">
                    ℹ️ En attente de la signature du contrat par l'influenceur
                  </div>
                )}

                {request.status === 'active' && request.affiliate_link_id && (
                  <div className="mt-3 p-3 bg-green-50 rounded text-sm text-green-800">
                    ✅ Collaboration active ! Lien d'affiliation généré.
                  </div>
                )}

                {request.status === 'pending' && (
                  <div className="mt-3 text-sm text-gray-500">
                    ⏳ En attente de la réponse de l'influenceur
                  </div>
                )}

                <div className="mt-3 text-xs text-gray-500">
                  Envoyée le: {new Date(request.created_at).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Card title="Ventes des 30 Derniers Jours" icon={<TrendingUp size={20} />}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesData}>
                <defs>
                  <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.9}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.6}/>
                  </linearGradient>
                  <linearGradient id="colorOrders" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.9}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.6}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="sales" fill="url(#colorSales)" name="Ventes (€)" radius={[8, 8, 0, 0]} />
                <Bar dataKey="orders" fill="url(#colorOrders)" name="Commandes" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        {/* Performance Overview */}
        <Card title="Vue d'Ensemble Performance" icon={<Target size={20} />}>
          <div className="space-y-6 py-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Taux de Conversion</span>
                <span className="text-sm font-bold text-indigo-600">
                  {stats?.performance?.conversion_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-indigo-600 h-3 rounded-full"
                  style={{ width: `${Math.min(stats?.performance?.conversion_rate || 0, 100)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Taux d'Engagement</span>
                <span className="text-sm font-bold text-purple-600">
                  {stats?.performance?.engagement_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.engagement_rate || 0}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Satisfaction Client</span>
                <span className="text-sm font-bold text-green-600">
                  {stats?.performance?.satisfaction_rate || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.satisfaction_rate || 0}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Objectif Mensuel</span>
                <span className="text-sm font-bold text-orange-600">
                  {stats?.performance?.monthly_goal_progress || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-orange-600 h-3 rounded-full"
                  style={{ width: `${stats?.performance?.monthly_goal_progress || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Products Performance */}
      <Card title="Top Produits Performants" icon={<Award size={20} />}>
        {products.length === 0 ? (
          <EmptyState
            icon={<Package size={48} />}
            title="Aucun produit"
            description="Ajoutez vos premiers produits pour commencer"
            action={{
              label: "Ajouter un Produit",
              onClick: () => navigate('/products/create')
            }}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Produit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Catégorie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vues
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Clics
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ventes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Revenus
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.slice(0, 5).map((product) => (
                <tr key={product.id} className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{product.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{product.category || 'Non spécifié'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.views || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.clicks || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.sales || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {(product.revenue || 0).toLocaleString()} €
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {products.length > 5 && (
          <div className="mt-4 text-right">
            <button
              onClick={() => navigate('/products')}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-900"
            >
              Voir tous les produits →
            </button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default MerchantDashboard;

