import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  ShoppingBag, Eye, Lock, Unlock, Mail, Download, Search, Filter, Plus,
  TrendingUp, Package, DollarSign, Users, Star
} from 'lucide-react';
import {
  formatCurrency, formatDate, exportToCSV, getInitials, generateColorFromString,
  formatNumber
} from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';
import CountUp from 'react-countup';

/**
 * Onglet Merchants - Gestion complète des annonceurs
 * Style cohérent avec les autres onglets (Tailwind)
 */
const MerchantsTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();
  const [merchants, setMerchants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [subscriptionFilter, setSubscriptionFilter] = useState('all');
  const [selectedMerchant, setSelectedMerchant] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Stats locales
  const [localStats, setLocalStats] = useState({
    total: 0,
    active: 0,
    totalRevenue: 0,
    totalProducts: 0
  });

  const fetchMerchants = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};
      const response = await api.get('/api/admin/users?role=merchant', config);

      const merchantsData = response.data.users || response.data || [];
      setMerchants(merchantsData);

      // Calculer stats locales
      setLocalStats({
        total: merchantsData.length,
        active: merchantsData.filter(m => m.status === 'active').length,
        totalRevenue: merchantsData.reduce((sum, m) => sum + (m.balance || 0), 0),
        totalProducts: merchantsData.reduce((sum, m) => sum + (m.products_count || 0), 0)
      });
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement merchants:', error);
        toast.error('Impossible de charger les annonceurs');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchMerchants(controller.signal);
    return () => controller.abort();
  }, [fetchMerchants, refreshKey]);

  const handleToggleStatus = async (merchant) => {
    try {
      const newStatus = merchant.status === 'active' ? 'suspended' : 'active';
      await api.patch(`/api/admin/users/${merchant.id}/status`, { status: newStatus });
      toast.success(`Annonceur ${newStatus === 'active' ? 'activé' : 'suspendu'} avec succès`);
      fetchMerchants();
    } catch (error) {
      toast.error('Impossible de modifier le statut');
    }
  };

  const handleViewDetails = (merchant) => {
    setSelectedMerchant(merchant);
    setShowDetailModal(true);
  };

  const filteredMerchants = merchants.filter(m => {
    const matchesSearch = !searchTerm ||
      m.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'active' && m.status === 'active') ||
      (statusFilter === 'inactive' && m.status !== 'active');
    const matchesSubscription = subscriptionFilter === 'all' ||
      m.subscription_plan === subscriptionFilter;
    return matchesSearch && matchesStatus && matchesSubscription;
  });

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Annonceurs</p>
            <ShoppingBag className="text-indigo-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={localStats.total} duration={1.5} />
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Annonceurs Actifs</p>
            <Users className="text-green-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={localStats.active} duration={1.5} />
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {localStats.total > 0 ? Math.round((localStats.active / localStats.total) * 100) : 0}% du total
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Revenu Total</p>
            <DollarSign className="text-yellow-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={localStats.totalRevenue} duration={2} separator=" " suffix=" €" decimals={2} />
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Total Produits</p>
            <Package className="text-purple-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={localStats.totalProducts} duration={1.5} />
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom ou email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">Tous les statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>

          <select
            value={subscriptionFilter}
            onChange={(e) => setSubscriptionFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">Tous les plans</option>
            <option value="marketplace">Marketplace (99 MAD)</option>
            <option value="small">Small Business (199 MAD)</option>
            <option value="medium">Medium Business (499 MAD)</option>
            <option value="large">Large Enterprise (799 MAD)</option>
          </select>

          <button
            onClick={() => exportToCSV(filteredMerchants, 'annonceurs')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 transition-colors"
          >
            <Download size={20} />
            Exporter
          </button>
        </div>
      </div>

      {/* Merchants Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <ShoppingBag size={20} className="text-indigo-600" />
            Annonceurs ({filteredMerchants.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : filteredMerchants.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              Aucun annonceur trouvé
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entreprise</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Solde</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Produits</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredMerchants.map((merchant) => (
                  <tr key={merchant.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div
                          className="h-10 w-10 rounded-full flex items-center justify-center text-white font-semibold"
                          style={{ backgroundColor: generateColorFromString(merchant.email) }}
                        >
                          {getInitials(merchant.company_name || merchant.email)}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {merchant.company_name || 'Sans nom'}
                          </div>
                          <div className="text-sm text-gray-500">
                            Depuis {formatDate(merchant.created_at)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{merchant.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 text-xs rounded-full font-medium capitalize ${
                        merchant.subscription_plan === 'large' ? 'bg-purple-100 text-purple-800' :
                        merchant.subscription_plan === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        merchant.subscription_plan === 'small' ? 'bg-blue-100 text-blue-800' :
                        merchant.subscription_plan === 'marketplace' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {merchant.subscription_plan === 'marketplace' ? 'Marketplace' :
                         merchant.subscription_plan === 'small' ? 'Small Business' :
                         merchant.subscription_plan === 'medium' ? 'Medium Business' :
                         merchant.subscription_plan === 'large' ? 'Large Enterprise' :
                         merchant.subscription_plan || 'Aucun plan'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(merchant.balance || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(merchant.products_count || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        merchant.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {merchant.status === 'active' ? 'Actif' : 'Suspendu'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleViewDetails(merchant)}
                          className="text-blue-600 hover:text-blue-700"
                          title="Voir détails"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleToggleStatus(merchant)}
                          className={merchant.status === 'active' ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'}
                          title={merchant.status === 'active' ? 'Suspendre' : 'Activer'}
                        >
                          {merchant.status === 'active' ? <Lock size={18} /> : <Unlock size={18} />}
                        </button>
                        <a
                          href={`mailto:${merchant.email}`}
                          className="text-gray-600 hover:text-gray-700"
                          title="Envoyer email"
                        >
                          <Mail size={18} />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Merchant Detail Modal */}
      <BaseModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedMerchant(null);
        }}
        title="Détails Annonceur"
        size="2xl"
      >
        {selectedMerchant && (
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold mb-3">Informations Générales</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Entreprise</p>
                  <p className="font-medium">{selectedMerchant.company_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">{selectedMerchant.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Téléphone</p>
                  <p className="font-medium">{selectedMerchant.phone || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date d'inscription</p>
                  <p className="font-medium">{formatDate(selectedMerchant.created_at)}</p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3">Performance</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Solde</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(selectedMerchant.balance || 0)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Produits</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(selectedMerchant.products_count || 0)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Campagnes</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(selectedMerchant.campaigns_count || 0)}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3">Abonnement</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Plan actuel</p>
                <p className="text-xl font-bold text-indigo-600 capitalize">
                  {selectedMerchant.subscription_plan === 'marketplace' ? 'Marketplace' :
                   selectedMerchant.subscription_plan === 'small' ? 'Small Business' :
                   selectedMerchant.subscription_plan === 'medium' ? 'Medium Business' :
                   selectedMerchant.subscription_plan === 'large' ? 'Large Enterprise' :
                   selectedMerchant.subscription_plan || 'Aucun plan'}
                </p>
              </div>
            </div>
          </div>
        )}
      </BaseModal>
    </div>
  );
};

export default MerchantsTab;
