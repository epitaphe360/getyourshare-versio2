import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import { motion } from 'framer-motion';
import {
  Users, CreditCard, TrendingUp, AlertCircle, Search, Filter,
  CheckCircle, XCircle, Clock, RefreshCw, Eye, Edit, Ban,
  DollarSign, Calendar, Package, Crown, Shield, Zap, Star,
  FileText, Plus, ArrowUpCircle, DollarSign as RefundIcon, BarChart3
} from 'lucide-react';
import PlanChangeModal from '../../components/admin/PlanChangeModal';
import RefundModal from '../../components/admin/RefundModal';
import { useNavigate } from 'react-router-dom';

/**
 * Gestionnaire d'abonnements pour Admin
 * 
 * Fonctionnalités:
 * - Vue d'ensemble de tous les abonnements (marchands, influenceurs, commerciaux)
 * - Statistiques globales (MRR, ARR, churn rate)
 * - Filtrage par statut, plan, rôle
 * - Actions: voir détails, modifier plan, suspendre, résilier
 */
const AdminSubscriptionsManager = () => {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [subscriptions, setSubscriptions] = useState([]);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    role: 'all',
    plan: 'all',
    search: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0
  });
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [invoices, setInvoices] = useState([]);
  const [loadingInvoices, setLoadingInvoices] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [createFormData, setCreateFormData] = useState({
    user_email: '',
    plan_code: 'pro',
    role: 'merchant',
    duration_months: 12
  });
  const [showPlanChangeModal, setShowPlanChangeModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [filters, pagination.page]);

  useEffect(() => {
    if (showDetailsModal && selectedSubscription && activeTab === 'invoices') {
      fetchInvoices(selectedSubscription.id);
    }
  }, [activeTab, showDetailsModal, selectedSubscription]);

  const fetchInvoices = async (subscriptionId) => {
    try {
      setLoadingInvoices(true);
      const res = await api.get(`/api/subscriptions/admin/${subscriptionId}/invoices`);
      setInvoices(res.data.invoices || []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      toast.error('Impossible de charger les factures');
    } finally {
      setLoadingInvoices(false);
    }
  };

  const handleCreateSubscription = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/subscriptions/admin/create', createFormData);
      toast.success('Abonnement créé avec succès');
      setShowCreateModal(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Récupérer les stats globales et les abonnements en parallèle
      const [statsRes, subsRes] = await Promise.allSettled([
        api.get('/api/subscriptions/admin/stats'),
        api.get('/api/subscriptions/admin/all', {
          params: {
            status: filters.status !== 'all' ? filters.status : undefined,
            role: filters.role !== 'all' ? filters.role : undefined,
            plan: filters.plan !== 'all' ? filters.plan : undefined,
            search: filters.search || undefined,
            page: pagination.page,
            limit: pagination.limit
          }
        })
      ]);

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      } else {
        // Stats par défaut si l'endpoint n'existe pas encore
        setStats({
          total_subscriptions: 0,
          active_subscriptions: 0,
          mrr: 0,
          arr: 0,
          churn_rate: 0,
          by_plan: {},
          by_role: {}
        });
      }

      if (subsRes.status === 'fulfilled') {
        setSubscriptions(subsRes.value.data.subscriptions || []);
        setPagination(prev => ({
          ...prev,
          total: subsRes.value.data.total || 0
        }));
      } else {
        // Fallback: récupérer tous les utilisateurs avec abonnements
        try {
          const usersRes = await api.get('/api/admin/users');
          const users = usersRes.data.users || usersRes.data || [];
          
          // Transformer en format abonnement
          const subs = users.map(user => ({
            id: user.subscription_id || user.id,
            user_id: user.id,
            user_name: user.full_name || user.company_name || user.email,
            user_email: user.email,
            user_role: user.role,
            plan_name: user.plan_name || user.subscription_plan || 'Free',
            plan_code: user.plan_code || 'free',
            status: user.subscription_status || 'active',
            monthly_fee: user.monthly_fee || (user.plan_name === 'Enterprise' ? 2999 : user.plan_name === 'Pro' ? 499 : user.plan_name === 'Marketplace' ? 99 : 0),
            created_at: user.subscription_created_at || user.created_at,
            ends_at: user.subscription_ends_at,
            features: user.plan_features || []
          }));
          
          setSubscriptions(subs);
          setPagination(prev => ({ ...prev, total: subs.length }));
        } catch (err) {
          console.error('Error fetching users:', err);
          setSubscriptions([]);
        }
      }
    } catch (error) {
      console.error('Error fetching subscription data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleViewDetails = (subscription) => {
    setSelectedSubscription(subscription);
    setActiveTab('overview');
    setInvoices([]);
    setShowDetailsModal(true);
  };

  const handleChangePlan = async (subscriptionId, newPlan) => {
    try {
      await api.post(`/api/subscriptions/admin/${subscriptionId}/change-plan`, {
        new_plan: newPlan
      });
      toast.success('Plan modifié avec succès');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la modification du plan');
    }
  };

  const handleSuspendSubscription = async (subscriptionId) => {
    if (!window.confirm('Voulez-vous vraiment suspendre cet abonnement ?')) return;
    
    try {
      await api.post(`/api/subscriptions/admin/${subscriptionId}/suspend`);
      toast.success('Abonnement suspendu');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la suspension');
    }
  };

  const handleReactivateSubscription = async (subscriptionId) => {
    try {
      await api.post(`/api/subscriptions/admin/${subscriptionId}/reactivate`);
      toast.success('Abonnement réactivé');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la réactivation');
    }
  };

  const getPlanIcon = (planCode) => {
    const icons = {
      free: Shield,
      freemium: Shield,
      starter: Zap,
      standard: Star,
      pro: Crown,
      premium: Crown,
      enterprise: Crown,
      elite: Crown
    };
    return icons[planCode?.toLowerCase()] || Shield;
  };

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Actif' },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Annulé' },
      suspended: { color: 'bg-yellow-100 text-yellow-800', icon: Ban, label: 'Suspendu' },
      pending: { color: 'bg-blue-100 text-blue-800', icon: Clock, label: 'En attente' },
      expired: { color: 'bg-gray-100 text-gray-800', icon: XCircle, label: 'Expiré' }
    };
    return badges[status] || badges.active;
  };

  const getRoleBadge = (role) => {
    const badges = {
      merchant: { color: 'bg-indigo-100 text-indigo-800', label: 'Marchand' },
      influencer: { color: 'bg-pink-100 text-pink-800', label: 'Influenceur' },
      commercial: { color: 'bg-cyan-100 text-cyan-800', label: 'Commercial' },
      admin: { color: 'bg-purple-100 text-purple-800', label: 'Admin' }
    };
    return badges[role] || { color: 'bg-gray-100 text-gray-800', label: role };
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-MA', {
      style: 'currency',
      currency: 'MAD'
    }).format(amount || 0);
  };

  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getPriceForPlan = (planName, currentPrice) => {
    if (currentPrice && currentPrice > 0) return currentPrice;
    const name = planName?.toLowerCase() || '';
    if (name.includes('enterprise')) return 2999;
    if (name.includes('elite')) return 4999;
    if (name.includes('premium')) return 999;
    if (name.includes('pro')) return 499;
    if (name.includes('medium')) return 499;
    if (name.includes('standard')) return 299;
    if (name.includes('small')) return 199;
    if (name.includes('starter')) return 199;
    if (name.includes('marketplace')) return 99;
    return 0;
  };

  // Filtrer les abonnements côté client si pas de backend
  const filteredSubscriptions = subscriptions.filter(sub => {
    if (filters.status !== 'all' && sub.status !== filters.status) return false;
    if (filters.role !== 'all' && sub.user_role !== filters.role) return false;
    if (filters.plan !== 'all' && sub.plan_code !== filters.plan) return false;
    if (filters.search) {
      const search = filters.search.toLowerCase();
      return (
        sub.user_name?.toLowerCase().includes(search) ||
        sub.user_email?.toLowerCase().includes(search) ||
        sub.plan_name?.toLowerCase().includes(search)
      );
    }
    return true;
  }).map(sub => ({
    ...sub,
    monthly_fee: getPriceForPlan(sub.plan_name, sub.monthly_fee)
  }));

  if (loading && subscriptions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des abonnements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <CreditCard className="h-8 w-8 text-indigo-600" />
              Gestion des Abonnements
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez tous les abonnements des marchands, influenceurs et commerciaux
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/admin/subscriptions/analytics')}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 flex items-center gap-2 shadow-lg transition-all"
            >
              <BarChart3 className="h-5 w-5" />
              Analytics Avancés
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 shadow-sm"
            >
              <Plus className="h-5 w-5" />
              Nouvel Abonnement
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Abonnements Actifs</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.active_subscriptions || filteredSubscriptions.filter(s => s.status === 'active').length}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">MRR (Revenus Mensuels)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(stats?.mrr || filteredSubscriptions.reduce((sum, s) => sum + (s.monthly_fee || 0), 0))}
                  </p>
                </div>
                <div className="p-3 bg-indigo-100 rounded-full">
                  <DollarSign className="h-6 w-6 text-indigo-600" />
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">ARR (Revenus Annuels)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency((stats?.mrr || filteredSubscriptions.reduce((sum, s) => sum + (s.monthly_fee || 0), 0)) * 12)}
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <TrendingUp className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Taux de Churn</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats?.churn_rate?.toFixed(1) || '0.0'}%
                  </p>
                </div>
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertCircle className="h-6 w-6 text-red-600" />
                </div>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Filters */}
        <Card className="p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Search */}
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par nom, email..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Status Filter */}
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="active">Actif</option>
              <option value="cancelled">Annulé</option>
              <option value="suspended">Suspendu</option>
              <option value="pending">En attente</option>
            </select>

            {/* Role Filter */}
            <select
              value={filters.role}
              onChange={(e) => handleFilterChange('role', e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Tous les rôles</option>
              <option value="merchant">Marchands</option>
              <option value="influencer">Influenceurs</option>
              <option value="commercial">Commerciaux</option>
            </select>

            {/* Plan Filter */}
            <select
              value={filters.plan}
              onChange={(e) => handleFilterChange('plan', e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Tous les plans</option>
              <option value="free">Free</option>
              <option value="freemium">Freemium</option>
              <option value="starter">Starter</option>
              <option value="standard">Standard</option>
              <option value="pro">Pro</option>
              <option value="premium">Premium</option>
              <option value="enterprise">Enterprise</option>
              <option value="elite">Elite</option>
            </select>

            {/* Refresh Button */}
            <button
              onClick={fetchData}
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </button>
          </div>
        </Card>

        {/* Subscriptions Table */}
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilisateur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rôle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Plan
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prix/mois
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date début
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSubscriptions.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                      <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Aucun abonnement trouvé</p>
                    </td>
                  </tr>
                ) : (
                  filteredSubscriptions.map((sub) => {
                    const PlanIcon = getPlanIcon(sub.plan_code);
                    const statusBadge = getStatusBadge(sub.status);
                    const roleBadge = getRoleBadge(sub.user_role);
                    const StatusIcon = statusBadge.icon;

                    return (
                      <tr key={sub.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {sub.user_name || 'Utilisateur'}
                            </div>
                            <div className="text-sm text-gray-500">
                              {sub.user_email}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${roleBadge.color}`}>
                            {roleBadge.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <PlanIcon className="h-5 w-5 text-indigo-600" />
                            <span className="text-sm font-medium text-gray-900">
                              {sub.plan_name}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {sub.monthly_fee === 0 ? (
                            <span className="text-green-600">Gratuit</span>
                          ) : (
                            formatCurrency(sub.monthly_fee)
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold rounded-full ${statusBadge.color}`}>
                            <StatusIcon className="h-3 w-3" />
                            {statusBadge.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(sub.created_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleViewDetails(sub)}
                              className="p-1 text-gray-400 hover:text-indigo-600"
                              title="Voir détails"
                            >
                              <Eye className="h-5 w-5" />
                            </button>
                            {sub.status === 'active' ? (
                              <button
                                onClick={() => handleSuspendSubscription(sub.id)}
                                className="p-1 text-gray-400 hover:text-yellow-600"
                                title="Suspendre"
                              >
                                <Ban className="h-5 w-5" />
                              </button>
                            ) : sub.status === 'suspended' ? (
                              <button
                                onClick={() => handleReactivateSubscription(sub.id)}
                                className="p-1 text-gray-400 hover:text-green-600"
                                title="Réactiver"
                              >
                                <CheckCircle className="h-5 w-5" />
                              </button>
                            ) : null}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pagination.total > pagination.limit && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Affichage de {((pagination.page - 1) * pagination.limit) + 1} à{' '}
                {Math.min(pagination.page * pagination.limit, pagination.total)} sur {pagination.total} résultats
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                  disabled={pagination.page === 1}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  Précédent
                </button>
                <button
                  onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                  disabled={pagination.page * pagination.limit >= pagination.total}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  Suivant
                </button>
              </div>
            </div>
          )}
        </Card>

        {/* Details Modal */}
        {showDetailsModal && selectedSubscription && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">
                    Détails de l'abonnement
                  </h3>
                  <button
                    onClick={() => setShowDetailsModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="h-6 w-6" />
                  </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-6">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 ${
                      activeTab === 'overview'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Aperçu
                  </button>
                  <button
                    onClick={() => setActiveTab('invoices')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 ${
                      activeTab === 'invoices'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Factures
                  </button>
                </div>

                {activeTab === 'overview' ? (
                  <div className="space-y-6">
                    {/* User Info */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Utilisateur</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Nom</p>
                          <p className="font-medium">{selectedSubscription.user_name}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Email</p>
                          <p className="font-medium">{selectedSubscription.user_email}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Rôle</p>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadge(selectedSubscription.user_role).color}`}>
                            {getRoleBadge(selectedSubscription.user_role).label}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Subscription Info */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Abonnement</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Plan</p>
                          <p className="font-medium">{selectedSubscription.plan_name}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Prix mensuel</p>
                          <p className="font-medium">{formatCurrency(selectedSubscription.monthly_fee)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Statut</p>
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(selectedSubscription.status).color}`}>
                            {getStatusBadge(selectedSubscription.status).label}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Date de début</p>
                          <p className="font-medium">{formatDate(selectedSubscription.created_at)}</p>
                        </div>
                        {selectedSubscription.ends_at && (
                          <div>
                            <p className="text-sm text-gray-500">Date de fin</p>
                            <p className="font-medium">{formatDate(selectedSubscription.ends_at)}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Features */}
                    {selectedSubscription.features && selectedSubscription.features.length > 0 && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-semibold text-gray-700 mb-3">Fonctionnalités incluses</h4>
                        <div className="grid grid-cols-2 gap-2">
                          {selectedSubscription.features.map((feature, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-green-500" />
                              <span>{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="grid grid-cols-2 gap-3 pt-4 border-t">
                      <button
                        onClick={() => {
                          setShowDetailsModal(false);
                          setShowPlanChangeModal(true);
                        }}
                        className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        <ArrowUpCircle size={18} />
                        Changer de Plan
                      </button>
                      <button
                        onClick={() => {
                          setShowDetailsModal(false);
                          setShowRefundModal(true);
                        }}
                        className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                      >
                        <RefundIcon size={18} />
                        Rembourser
                      </button>
                      {selectedSubscription.status === 'active' && (
                        <button
                          onClick={() => {
                            handleSuspendSubscription(selectedSubscription.id);
                            setShowDetailsModal(false);
                          }}
                          className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
                        >
                          Suspendre
                        </button>
                      )}
                      {selectedSubscription.status === 'suspended' && (
                        <button
                          onClick={() => {
                            handleReactivateSubscription(selectedSubscription.id);
                            setShowDetailsModal(false);
                          }}
                          className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                        >
                          Réactiver
                        </button>
                      )}
                      <button
                        onClick={() => setShowDetailsModal(false)}
                        className="col-span-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                      >
                        Fermer
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {loadingInvoices ? (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                        <p className="mt-2 text-gray-500">Chargement des factures...</p>
                      </div>
                    ) : invoices.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                        <p>Aucune facture trouvée</p>
                      </div>
                    ) : (
                      <div className="overflow-hidden rounded-lg border border-gray-200">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">PDF</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {invoices.map((invoice) => (
                              <tr key={invoice.id}>
                                <td className="px-4 py-2 text-sm text-gray-900">
                                  {new Date(invoice.created * 1000).toLocaleDateString('fr-FR')}
                                </td>
                                <td className="px-4 py-2 text-sm text-gray-900">
                                  {formatCurrency(invoice.amount_paid / 100)}
                                </td>
                                <td className="px-4 py-2 text-sm">
                                  <span className={`px-2 py-1 text-xs rounded-full ${
                                    invoice.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                  }`}>
                                    {invoice.status === 'paid' ? 'Payée' : invoice.status}
                                  </span>
                                </td>
                                <td className="px-4 py-2 text-sm">
                                  {invoice.invoice_pdf && (
                                    <a
                                      href={invoice.invoice_pdf}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-indigo-600 hover:text-indigo-800"
                                    >
                                      Télécharger
                                    </a>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}

        {/* Create Subscription Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-gray-900">
                    Créer un abonnement manuel
                  </h3>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="h-6 w-6" />
                  </button>
                </div>

                <form onSubmit={handleCreateSubscription} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email Utilisateur
                    </label>
                    <input
                      type="email"
                      required
                      value={createFormData.user_email}
                      onChange={(e) => setCreateFormData({ ...createFormData, user_email: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      placeholder="ex: utilisateur@example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rôle
                    </label>
                    <select
                      value={createFormData.role}
                      onChange={(e) => setCreateFormData({ ...createFormData, role: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="merchant">Marchand</option>
                      <option value="influencer">Influenceur</option>
                      <option value="commercial">Commercial</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Plan
                    </label>
                    <select
                      value={createFormData.plan_code}
                      onChange={(e) => setCreateFormData({ ...createFormData, plan_code: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="free">Free</option>
                      <option value="starter">Starter</option>
                      <option value="pro">Pro</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Durée (mois)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      value={createFormData.duration_months}
                      onChange={(e) => setCreateFormData({ ...createFormData, duration_months: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowCreateModal(false)}
                      className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                    >
                      Annuler
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                      Créer
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          </div>
        )}

        {/* Plan Change Modal */}
        <PlanChangeModal
          isOpen={showPlanChangeModal}
          onClose={() => setShowPlanChangeModal(false)}
          subscription={selectedSubscription}
          onSuccess={(data) => {
            toast.success(data.message || 'Plan changé avec succès');
            fetchData();
            setShowPlanChangeModal(false);
          }}
        />

        {/* Refund Modal */}
        <RefundModal
          isOpen={showRefundModal}
          onClose={() => setShowRefundModal(false)}
          subscription={selectedSubscription}
          onSuccess={(data) => {
            toast.success(data.message || 'Remboursement effectué');
            fetchData();
            setShowRefundModal(false);
          }}
        />
      </div>
    </div>
  );
};

export default AdminSubscriptionsManager;
