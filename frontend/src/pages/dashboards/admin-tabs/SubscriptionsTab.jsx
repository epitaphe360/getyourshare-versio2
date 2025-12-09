import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  Target, Eye, TrendingUp, TrendingDown, Download, Search, Filter,
  AlertCircle, DollarSign, Users, Calendar, RefreshCw, ArrowUp, ArrowDown, X
} from 'lucide-react';
import {
  formatCurrency, formatDate, exportToCSV, formatNumber, getStatusColor
} from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';
import CountUp from 'react-countup';

/**
 * SubscriptionsTab - Gestion complète des abonnements (Niveau SaaS)
 *
 * Features:
 * - KPI Cards (MRR, ARR, Churn rate, Nouveaux/mois)
 * - Filtres avancés (Plan, Statut, Rôle)
 * - Table abonnements avec progress période
 * - Modal détails abonnement + historique
 * - Actions (Upgrade, Downgrade, Cancel, Renew)
 * - Alertes churn (expire bientôt)
 * - Export CSV
 * - Optimisé avec useCallback + AbortController
 */
const SubscriptionsTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [planFilter, setPlanFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [history, setHistory] = useState([]);

  // Stats locales
  const [localStats, setLocalStats] = useState({
    mrr: 0,
    arr: 0,
    churnRate: 0,
    newThisMonth: 0,
    expiringSoon: 0,
    totalActive: 0
  });

  // Plans disponibles
  const plans = {
    influencer: ['free', 'basic', 'pro', 'elite', 'premium'],
    merchant: ['freemium', 'standard', 'premium', 'enterprise'],
    commercial: ['starter', 'pro', 'enterprise']
  };

  const planPrices = {
    // Influencers
    free: 0,
    basic: 9.99,
    pro: 29.99,
    elite: 79.99,
    premium: 149.99,
    // Merchants
    freemium: 0,
    standard: 49.99,
    premium: 149.99,
    enterprise: 499.99,
    // Commercials
    starter: 29.99,
    pro: 99.99,
    enterprise: 299.99
  };

  // ========== API CALLS ==========
  const fetchSubscriptions = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};

      const response = await api.get('/api/subscriptions', config);
      const subsData = response.data.subscriptions || response.data || [];
      setSubscriptions(subsData);

      // Calculer stats locales
      const now = new Date();
      const firstDayMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const in30Days = new Date(now.getTime() + (30 * 24 * 60 * 60 * 1000));

      const activeSubscriptions = subsData.filter(s => s.status === 'active');

      // Calculer MRR (Monthly Recurring Revenue)
      const mrr = activeSubscriptions.reduce((sum, s) => {
        const price = s.plan_price || planPrices[s.plan] || 0;
        return sum + price;
      }, 0);

      // Calculer ARR (Annual Recurring Revenue)
      const arr = mrr * 12;

      // Nouveaux ce mois
      const newThisMonth = subsData.filter(s => {
        const createdAt = new Date(s.created_at);
        return createdAt >= firstDayMonth;
      }).length;

      // Expirent bientôt (dans les 30 prochains jours)
      const expiringSoon = subsData.filter(s => {
        if (!s.period_end) return false;
        const endDate = new Date(s.period_end);
        return endDate >= now && endDate <= in30Days;
      }).length;

      // Calculer churn rate (approximation simple)
      const lastMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const lastMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);
      const cancelledLastMonth = subsData.filter(s => {
        if (s.status !== 'cancelled') return false;
        const updatedAt = new Date(s.updated_at);
        return updatedAt >= lastMonthStart && updatedAt <= lastMonthEnd;
      }).length;
      const activeLastMonth = subsData.filter(s => {
        const createdAt = new Date(s.created_at);
        return createdAt < firstDayMonth;
      }).length;
      const churnRate = activeLastMonth > 0 ? (cancelledLastMonth / activeLastMonth) * 100 : 0;

      setLocalStats({
        mrr,
        arr,
        churnRate,
        newThisMonth,
        expiringSoon,
        totalActive: activeSubscriptions.length
      });
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement abonnements:', error);
        toast.error('Impossible de charger les abonnements');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchSubscriptions(controller.signal);
    return () => controller.abort();
  }, [fetchSubscriptions, refreshKey]);

  // ========== HANDLERS ==========
  const handleViewDetails = useCallback(async (subscription) => {
    try {
      // Charger l'historique de l'abonnement
      const response = await api.get(`/api/subscriptions/${subscription.id}/history`);
      setHistory(response.data.history || response.data || []);
      setSelectedSubscription(subscription);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
      // Afficher quand même la modal avec données limitées
      setHistory([]);
      setSelectedSubscription(subscription);
      setShowDetailModal(true);
    }
  }, []);

  const handleChangeStatus = useCallback(async (subscriptionId, newStatus) => {
    try {
      await api.patch(`/api/subscriptions/${subscriptionId}`, {
        status: newStatus
      });

      toast.success(`Abonnement ${newStatus === 'active' ? 'activé' : newStatus === 'cancelled' ? 'annulé' : 'modifié'}`);
      fetchSubscriptions();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur modification status:', error);
      toast.error('Impossible de modifier l\'abonnement');
    }
  }, [toast, fetchSubscriptions, onRefresh]);

  const handleUpgrade = useCallback(async (subscriptionId, newPlan) => {
    try {
      await api.patch(`/api/subscriptions/${subscriptionId}`, {
        plan: newPlan
      });

      toast.success(`Abonnement upgradé vers ${newPlan}`);
      setShowUpgradeModal(false);
      fetchSubscriptions();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur upgrade:', error);
      toast.error('Impossible d\'upgrader l\'abonnement');
    }
  }, [toast, fetchSubscriptions, onRefresh]);

  const handleRenew = useCallback(async (subscriptionId) => {
    try {
      const now = new Date();
      const periodEnd = new Date(now.getTime() + (30 * 24 * 60 * 60 * 1000)); // +30 jours

      await api.patch(`/api/subscriptions/${subscriptionId}`, {
        period_end: periodEnd.toISOString(),
        status: 'active'
      });

      toast.success('Abonnement renouvelé pour 30 jours');
      fetchSubscriptions();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur renouvellement:', error);
      toast.error('Impossible de renouveler l\'abonnement');
    }
  }, [toast, fetchSubscriptions, onRefresh]);

  const handleExport = useCallback(() => {
    const exportData = filteredSubscriptions.map(s => {
      const daysRemaining = s.period_end ?
        Math.ceil((new Date(s.period_end) - new Date()) / (1000 * 60 * 60 * 24)) : 0;

      return {
        id: s.id,
        utilisateur: s.user_email || 'N/A',
        role: s.user_role || 'N/A',
        plan: s.plan_name || s.plan || 'N/A',
        prix_mensuel: s.plan_price || planPrices[s.plan] || 0,
        statut: s.status,
        debut_periode: formatDate(s.period_start),
        fin_periode: formatDate(s.period_end),
        jours_restants: daysRemaining,
        date_creation: formatDate(s.created_at)
      };
    });

    exportToCSV(exportData, 'abonnements_export');
    toast.success('Abonnements exportés avec succès');
  }, [toast]);

  // ========== FILTRAGE ==========
  const filteredSubscriptions = subscriptions.filter(subscription => {
    // Recherche
    const userEmail = subscription.user_email || '';
    if (searchTerm && !userEmail.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Plan
    const subPlan = subscription.plan_name || subscription.plan || '';
    if (planFilter !== 'all' && !subPlan.toLowerCase().includes(planFilter.toLowerCase())) {
      return false;
    }

    // Statut
    if (statusFilter !== 'all' && subscription.status !== statusFilter) {
      return false;
    }

    // Rôle
    if (roleFilter !== 'all' && subscription.user_role !== roleFilter) {
      return false;
    }

    return true;
  });

  // Calculer progression de période
  const getPeriodProgress = (subscription) => {
    if (!subscription.period_start || !subscription.period_end) return 0;

    const start = new Date(subscription.period_start).getTime();
    const end = new Date(subscription.period_end).getTime();
    const now = Date.now();

    if (now < start) return 0;
    if (now > end) return 100;

    return Math.round(((now - start) / (end - start)) * 100);
  };

  const getDaysRemaining = (subscription) => {
    if (!subscription.period_end) return null;
    const end = new Date(subscription.period_end);
    const now = new Date();
    const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff;
  };

  // ========== RENDER ==========
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des abonnements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm mb-1">MRR (Revenu Mensuel)</p>
              <p className="text-3xl font-bold">
                <CountUp
                  end={localStats.mrr}
                  duration={1}
                  decimals={2}
                  separator=" "
                  suffix=" €"
                />
              </p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <DollarSign size={24} />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm mb-1">ARR (Revenu Annuel)</p>
              <p className="text-3xl font-bold">
                <CountUp
                  end={localStats.arr}
                  duration={1}
                  decimals={0}
                  separator=" "
                  suffix=" €"
                />
              </p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <TrendingUp size={24} />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm mb-1">Nouveaux ce mois</p>
              <p className="text-3xl font-bold">
                <CountUp end={localStats.newThisMonth} duration={1} />
              </p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <Users size={24} />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm mb-1">Expirent bientôt</p>
              <p className="text-3xl font-bold">
                <CountUp end={localStats.expiringSoon} duration={1} />
              </p>
              <p className="text-xs text-orange-100 mt-1">Dans les 30 jours</p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <AlertCircle size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Stats supplémentaires */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Abonnements Actifs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                <CountUp end={localStats.totalActive} duration={1} />
              </p>
            </div>
            <Target className="text-green-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taux de Churn</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                <CountUp
                  end={localStats.churnRate}
                  duration={1}
                  decimals={1}
                  suffix="%"
                />
              </p>
            </div>
            <TrendingDown className={localStats.churnRate > 5 ? 'text-red-600' : 'text-green-600'} size={32} />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Revenu Moyen/Utilisateur</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(localStats.totalActive > 0 ? localStats.mrr / localStats.totalActive : 0)}
              </p>
            </div>
            <DollarSign className="text-blue-600" size={32} />
          </div>
        </div>
      </div>

      {/* Filtres et Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Recherche */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher un utilisateur..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtre Plan */}
          <select
            value={planFilter}
            onChange={(e) => setPlanFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous les plans</option>
            <optgroup label="Influencers">
              {plans.influencer.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </optgroup>
            <optgroup label="Merchants">
              {plans.merchant.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </optgroup>
            <optgroup label="Commercials">
              {plans.commercial.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </optgroup>
          </select>

          {/* Filtre Statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous statuts</option>
            <option value="active">Actifs</option>
            <option value="cancelled">Annulés</option>
            <option value="expired">Expirés</option>
            <option value="pending">En attente</option>
          </select>

          {/* Filtre Rôle */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous les rôles</option>
            <option value="influencer">Influencers</option>
            <option value="merchant">Merchants</option>
            <option value="commercial">Commercials</option>
          </select>

          {/* Export */}
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2 transition-colors whitespace-nowrap"
          >
            <Download size={20} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Table Abonnements */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Utilisateur
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Prix/mois
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Période
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Progression
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredSubscriptions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                    <Target className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg font-medium">Aucun abonnement trouvé</p>
                    <p className="text-sm mt-1">Essayez de modifier vos filtres</p>
                  </td>
                </tr>
              ) : (
                filteredSubscriptions.map(subscription => {
                  const progress = getPeriodProgress(subscription);
                  const daysRemaining = getDaysRemaining(subscription);
                  const price = subscription.plan_price || planPrices[subscription.plan] || 0;

                  return (
                    <tr
                      key={subscription.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {subscription.user_email || subscription.user_name || 'N/A'}
                          </p>
                          <p className="text-sm text-gray-500 capitalize">
                            {subscription.user_role || 'N/A'}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium capitalize">
                          {subscription.plan_name || subscription.plan || 'Free'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-gray-900">
                          {formatCurrency(price)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <p className="text-gray-900">
                            {formatDate(subscription.period_start)} → {formatDate(subscription.period_end)}
                          </p>
                          {daysRemaining !== null && (
                            <p className={`text-xs mt-1 flex items-center gap-1 ${
                              daysRemaining < 7 ? 'text-red-600' :
                              daysRemaining < 30 ? 'text-orange-600' :
                              'text-gray-500'
                            }`}>
                              <Calendar size={12} />
                              {daysRemaining} jour{daysRemaining > 1 ? 's' : ''} restant{daysRemaining > 1 ? 's' : ''}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="w-full">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-medium text-gray-700">
                              {progress}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                progress >= 90 ? 'bg-red-500' :
                                progress >= 70 ? 'bg-orange-500' :
                                'bg-green-500'
                              }`}
                              style={{ width: `${progress}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          subscription.status === 'active' ? 'bg-green-100 text-green-800' :
                          subscription.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                          subscription.status === 'expired' ? 'bg-gray-100 text-gray-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {subscription.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleViewDetails(subscription)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Voir détails"
                          >
                            <Eye size={18} />
                          </button>
                          {subscription.status === 'active' && (
                            <>
                              <button
                                onClick={() => {
                                  setSelectedSubscription(subscription);
                                  setShowUpgradeModal(true);
                                }}
                                className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                                title="Upgrade"
                              >
                                <ArrowUp size={18} />
                              </button>
                              <button
                                onClick={() => handleRenew(subscription.id)}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Renouveler"
                              >
                                <RefreshCw size={18} />
                              </button>
                              <button
                                onClick={() => handleChangeStatus(subscription.id, 'cancelled')}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Annuler"
                              >
                                <X size={18} />
                              </button>
                            </>
                          )}
                          {subscription.status === 'cancelled' && (
                            <button
                              onClick={() => handleChangeStatus(subscription.id, 'active')}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Réactiver"
                            >
                              <RefreshCw size={18} />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Détails Abonnement */}
      {showDetailModal && selectedSubscription && (
        <BaseModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Détails de l'Abonnement"
          size="large"
        >
          <div className="space-y-6">
            {/* Informations principales */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {selectedSubscription.user_email || selectedSubscription.user_name || 'N/A'}
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Plan</p>
                  <p className="text-lg font-semibold capitalize">{selectedSubscription.plan_name || selectedSubscription.plan || 'Free'}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Prix/mois</p>
                  <p className="text-lg font-semibold">{formatCurrency(selectedSubscription.plan_price || planPrices[selectedSubscription.plan] || 0)}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Statut</p>
                  <p className="text-lg font-semibold capitalize">{selectedSubscription.status}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Rôle</p>
                  <p className="text-lg font-semibold capitalize">{selectedSubscription.user_role || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Période */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Période d'abonnement</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500">Début</p>
                    <p className="font-medium">{formatDate(selectedSubscription.period_start)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Fin</p>
                    <p className="font-medium">{formatDate(selectedSubscription.period_end)}</p>
                  </div>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-3">
                  <div
                    className="bg-indigo-600 h-3 rounded-full transition-all"
                    style={{ width: `${getPeriodProgress(selectedSubscription)}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {getPeriodProgress(selectedSubscription)}% de la période écoulée
                </p>
              </div>
            </div>

            {/* Historique */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Historique</h4>
              {history.length === 0 ? (
                <p className="text-gray-500 text-sm">Aucun historique disponible</p>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <div className="space-y-3">
                    {history.map((event, index) => (
                      <div key={index} className="flex items-start gap-3 text-sm">
                        <div className="bg-indigo-100 rounded-full p-1.5 mt-0.5">
                          <Calendar size={14} className="text-indigo-600" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{event.action}</p>
                          <p className="text-gray-600 text-xs mt-0.5">{formatDate(event.created_at)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="border-t pt-4 flex gap-3">
              {selectedSubscription.status === 'active' && (
                <>
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setShowUpgradeModal(true);
                    }}
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Upgrade
                  </button>
                  <button
                    onClick={() => {
                      handleRenew(selectedSubscription.id);
                      setShowDetailModal(false);
                    }}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Renouveler
                  </button>
                  <button
                    onClick={() => {
                      handleChangeStatus(selectedSubscription.id, 'cancelled');
                      setShowDetailModal(false);
                    }}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Annuler
                  </button>
                </>
              )}
              {selectedSubscription.status === 'cancelled' && (
                <button
                  onClick={() => {
                    handleChangeStatus(selectedSubscription.id, 'active');
                    setShowDetailModal(false);
                  }}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Réactiver
                </button>
              )}
            </div>
          </div>
        </BaseModal>
      )}

      {/* Modal Upgrade */}
      {showUpgradeModal && selectedSubscription && (
        <BaseModal
          isOpen={showUpgradeModal}
          onClose={() => setShowUpgradeModal(false)}
          title="Upgrade Abonnement"
          size="medium"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Sélectionnez le nouveau plan pour <strong>{selectedSubscription.user?.email}</strong>
            </p>

            <div className="space-y-2">
              {plans[selectedSubscription.user?.role]?.map(plan => {
                const price = planPrices[plan];
                const isCurrent = plan === selectedSubscription.plan;
                const isUpgrade = price > (planPrices[selectedSubscription.plan] || 0);

                return (
                  <button
                    key={plan}
                    onClick={() => handleUpgrade(selectedSubscription.id, plan)}
                    disabled={isCurrent}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      isCurrent
                        ? 'border-indigo-600 bg-indigo-50 cursor-not-allowed'
                        : isUpgrade
                        ? 'border-green-300 hover:border-green-500 hover:bg-green-50'
                        : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold capitalize flex items-center gap-2">
                          {plan}
                          {isCurrent && <span className="text-xs bg-indigo-600 text-white px-2 py-0.5 rounded">Actuel</span>}
                          {isUpgrade && !isCurrent && <ArrowUp size={16} className="text-green-600" />}
                          {!isUpgrade && !isCurrent && <ArrowDown size={16} className="text-orange-600" />}
                        </p>
                        <p className="text-sm text-gray-600">{formatCurrency(price)}/mois</p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </BaseModal>
      )}
    </div>
  );
};

export default SubscriptionsTab;
