import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  Sparkles, Eye, Edit, Lock, Unlock, Download, Search, Filter,
  TrendingUp, AlertCircle, DollarSign, Users, Mail, Phone, Calendar
} from 'lucide-react';
import {
  formatCurrency, formatDate, exportToCSV, formatNumber, getStatusColor
} from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';
import CountUp from 'react-countup';

/**
 * ServicesTab - Gestion complète des services (Niveau SaaS)
 *
 * Features:
 * - KPI Cards (Total, Actifs, Budget épuisé, Leads générés)
 * - Filtres avancés (Recherche, Statut, Catégorie)
 * - Table services avec budget progress bar
 * - Modal détails service + leads
 * - Alertes budget faible (< 20%)
 * - Actions inline (Voir leads, Éditer, Désactiver)
 * - Export CSV services + leads
 * - Optimisé avec useCallback + AbortController
 */
const ServicesTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [budgetFilter, setBudgetFilter] = useState('all');
  const [selectedService, setSelectedService] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [leads, setLeads] = useState([]);

  // Stats locales
  const [localStats, setLocalStats] = useState({
    total: 0,
    active: 0,
    budgetExhausted: 0,
    totalLeads: 0
  });

  // ========== API CALLS ==========
  const fetchServices = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};

      // Appel parallèle pour récupérer services et catégories
      const [servicesRes, categoriesRes] = await Promise.allSettled([
        api.get('/api/services', config),
        api.get('/api/categories', config)
      ]);

      if (servicesRes.status === 'fulfilled') {
        const servicesData = servicesRes.value.data.services || servicesRes.value.data || [];
        setServices(servicesData);

        // Calculer stats locales
        setLocalStats({
          total: servicesData.length,
          active: servicesData.filter(s => s.is_active).length,
          budgetExhausted: servicesData.filter(s => {
            const spent = s.budget_spent || 0;
            const total = s.budget_total || 1;
            return (spent / total) >= 1;
          }).length,
          totalLeads: servicesData.reduce((sum, s) => sum + (s.leads_count || 0), 0)
        });
      }

      if (categoriesRes.status === 'fulfilled') {
        setCategories(categoriesRes.value.data.categories || categoriesRes.value.data || []);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement services:', error);
        toast.error('Impossible de charger les services');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchServices(controller.signal);
    return () => controller.abort();
  }, [fetchServices, refreshKey]);

  // ========== HANDLERS ==========
  const handleViewDetails = useCallback(async (service) => {
    try {
      // Charger les détails complets du service et ses leads
      const [serviceRes, leadsRes] = await Promise.allSettled([
        api.get(`/api/services/${service.id}`),
        api.get(`/api/services/${service.id}/leads`)
      ]);

      if (serviceRes.status === 'fulfilled') {
        setSelectedService(serviceRes.value.data);
      }

      if (leadsRes.status === 'fulfilled') {
        setLeads(leadsRes.value.data.leads || leadsRes.value.data || []);
      }

      setShowDetailModal(true);
    } catch (error) {
      console.error('Erreur chargement détails service:', error);
      toast.error('Impossible de charger les détails');
    }
  }, [toast]);

  const handleToggleStatus = useCallback(async (serviceId, currentStatus) => {
    try {
      await api.patch(`/api/services/${serviceId}`, {
        is_active: !currentStatus
      });

      toast.success(!currentStatus ? 'Service activé' : 'Service désactivé');
      fetchServices();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur toggle status:', error);
      toast.error('Impossible de modifier le statut');
    }
  }, [toast, fetchServices, onRefresh]);

  const handleExport = useCallback(() => {
    const exportData = filteredServices.map(s => {
      const budgetSpent = s.budget_spent || 0;
      const budgetTotal = s.budget_total || 0;
      const budgetPercentage = budgetTotal > 0 ? (budgetSpent / budgetTotal) * 100 : 0;

      return {
        id: s.id,
        nom: s.title || s.name,
        categorie: categories.find(c => c.id === s.category_id)?.name || 'N/A',
        budget_total: budgetTotal,
        budget_depense: budgetSpent,
        budget_restant: budgetTotal - budgetSpent,
        budget_pourcentage: budgetPercentage.toFixed(2),
        leads_generes: s.leads_count || 0,
        statut: s.is_active ? 'Actif' : 'Inactif',
        merchant: s.merchant?.company_name || 'N/A',
        date_creation: formatDate(s.created_at)
      };
    });

    exportToCSV(exportData, 'services_export');
    toast.success('Services exportés avec succès');
  }, [categories, toast]);

  const handleExportLeads = useCallback(() => {
    if (!selectedService || leads.length === 0) {
      toast.warning('Aucun lead à exporter');
      return;
    }

    const exportData = leads.map(lead => ({
      id: lead.id,
      nom: lead.name || 'N/A',
      email: lead.email || 'N/A',
      telephone: lead.phone || 'N/A',
      message: lead.message || 'N/A',
      statut: lead.status || 'N/A',
      date_creation: formatDate(lead.created_at)
    }));

    exportToCSV(exportData, `leads_${selectedService.title || selectedService.name}_${Date.now()}`);
    toast.success('Leads exportés avec succès');
  }, [selectedService, leads, toast]);

  // ========== FILTRAGE ==========
  const filteredServices = services.filter(service => {
    // Recherche
    const title = service.title || service.name || '';
    if (searchTerm && !title.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Catégorie
    if (categoryFilter !== 'all' && service.category_id !== categoryFilter) {
      return false;
    }

    // Statut
    if (statusFilter === 'active' && !service.is_active) return false;
    if (statusFilter === 'inactive' && service.is_active) return false;

    // Budget
    const budgetSpent = service.budget_spent || 0;
    const budgetTotal = service.budget_total || 1;
    const budgetPercentage = (budgetSpent / budgetTotal) * 100;

    if (budgetFilter === 'low' && budgetPercentage >= 20) return false;
    if (budgetFilter === 'medium' && (budgetPercentage < 20 || budgetPercentage >= 80)) return false;
    if (budgetFilter === 'high' && budgetPercentage < 80) return false;
    if (budgetFilter === 'exhausted' && budgetPercentage < 100) return false;

    return true;
  });

  // Calculer budget percentage pour un service
  const getBudgetPercentage = (service) => {
    const spent = service.budget_spent || 0;
    const total = service.budget_total || 1;
    return Math.min((spent / total) * 100, 100);
  };

  const getBudgetColor = (percentage) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-orange-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  // ========== RENDER ==========
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des services...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Services</p>
              <p className="text-3xl font-bold text-gray-900">
                <CountUp end={localStats.total} duration={1} />
              </p>
            </div>
            <div className="bg-purple-100 rounded-lg p-3">
              <Sparkles className="text-purple-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Services Actifs</p>
              <p className="text-3xl font-bold text-green-600">
                <CountUp end={localStats.active} duration={1} />
              </p>
            </div>
            <div className="bg-green-100 rounded-lg p-3">
              <TrendingUp className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Budget Épuisé</p>
              <p className="text-3xl font-bold text-red-600">
                <CountUp end={localStats.budgetExhausted} duration={1} />
              </p>
            </div>
            <div className="bg-red-100 rounded-lg p-3">
              <AlertCircle className="text-red-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Leads Générés</p>
              <p className="text-3xl font-bold text-blue-600">
                <CountUp end={localStats.totalLeads} duration={1} />
              </p>
            </div>
            <div className="bg-blue-100 rounded-lg p-3">
              <Users className="text-blue-600" size={24} />
            </div>
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
                placeholder="Rechercher un service..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtre Catégorie */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Toutes catégories</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>

          {/* Filtre Statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>

          {/* Filtre Budget */}
          <select
            value={budgetFilter}
            onChange={(e) => setBudgetFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous budgets</option>
            <option value="low">Budget faible (&lt; 20%)</option>
            <option value="medium">Budget moyen (20-80%)</option>
            <option value="high">Budget élevé (&gt; 80%)</option>
            <option value="exhausted">Budget épuisé</option>
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

      {/* Table Services */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Catégorie
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Budget
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Progression
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Leads
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
              {filteredServices.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                    <Sparkles className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg font-medium">Aucun service trouvé</p>
                    <p className="text-sm mt-1">Essayez de modifier vos filtres</p>
                  </td>
                </tr>
              ) : (
                filteredServices.map(service => {
                  const budgetPercentage = getBudgetPercentage(service);
                  const budgetSpent = service.budget_spent || 0;
                  const budgetTotal = service.budget_total || 0;
                  const budgetRemaining = budgetTotal - budgetSpent;

                  return (
                    <tr
                      key={service.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {service.title || service.name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {service.merchant?.company_name || 'Merchant inconnu'}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                          {categories.find(c => c.id === service.category_id)?.name || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-semibold text-gray-900">
                            {formatCurrency(budgetTotal)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Dépensé: {formatCurrency(budgetSpent)}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="w-full">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-medium text-gray-700">
                              {budgetPercentage.toFixed(0)}%
                            </span>
                            <span className="text-xs text-gray-500">
                              Restant: {formatCurrency(budgetRemaining)}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${getBudgetColor(budgetPercentage)}`}
                              style={{ width: `${budgetPercentage}%` }}
                            ></div>
                          </div>
                          {budgetPercentage >= 80 && budgetPercentage < 100 && (
                            <p className="text-xs text-orange-600 mt-1 flex items-center gap-1">
                              <AlertCircle size={12} />
                              Budget faible
                            </p>
                          )}
                          {budgetPercentage >= 100 && (
                            <p className="text-xs text-red-600 mt-1 flex items-center gap-1">
                              <AlertCircle size={12} />
                              Budget épuisé
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Users size={16} className="text-blue-500" />
                          <span className="font-semibold text-blue-600">
                            {service.leads_count || 0}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          service.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {service.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleViewDetails(service)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Voir détails et leads"
                          >
                            <Eye size={18} />
                          </button>
                          <button
                            onClick={() => navigate(`/admin/services/edit/${service.id}`)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                            title="Éditer"
                          >
                            <Edit size={18} />
                          </button>
                          <button
                            onClick={() => handleToggleStatus(service.id, service.is_active)}
                            className={`p-2 rounded-lg transition-colors ${
                              service.is_active
                                ? 'text-orange-600 hover:bg-orange-50'
                                : 'text-green-600 hover:bg-green-50'
                            }`}
                            title={service.is_active ? 'Désactiver' : 'Activer'}
                          >
                            {service.is_active ? <Lock size={18} /> : <Unlock size={18} />}
                          </button>
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

      {/* Modal Détails Service + Leads */}
      {showDetailModal && selectedService && (
        <BaseModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Détails du Service"
          size="large"
        >
          <div className="space-y-6">
            {/* Informations du service */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {selectedService.title || selectedService.name}
              </h3>
              <p className="text-gray-600 mb-4">{selectedService.description}</p>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Budget Total</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(selectedService.budget_total || 0)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Budget Dépensé</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(selectedService.budget_spent || 0)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Budget Restant</p>
                  <p className="text-lg font-semibold text-green-600">
                    {formatCurrency((selectedService.budget_total || 0) - (selectedService.budget_spent || 0))}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Statut</p>
                  <p className="text-lg font-semibold">
                    {selectedService.is_active ? '✅ Actif' : '❌ Inactif'}
                  </p>
                </div>
              </div>
            </div>

            {/* Progress bar détaillée */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Progression Budget</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {getBudgetPercentage(selectedService).toFixed(1)}% utilisé
                  </span>
                  <span className="text-sm text-gray-600">
                    Restant: {formatCurrency((selectedService.budget_total || 0) - (selectedService.budget_spent || 0))}
                  </span>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full transition-all ${getBudgetColor(getBudgetPercentage(selectedService))}`}
                    style={{ width: `${getBudgetPercentage(selectedService)}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Leads */}
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">
                  Leads Générés ({leads.length})
                </h4>
                {leads.length > 0 && (
                  <button
                    onClick={handleExportLeads}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <Download size={16} />
                    Exporter
                  </button>
                )}
              </div>

              {leads.length === 0 ? (
                <div className="bg-gray-50 rounded-lg p-8 text-center">
                  <Users className="mx-auto mb-3 text-gray-400" size={48} />
                  <p className="text-gray-600">Aucun lead généré pour ce service</p>
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="space-y-3">
                    {leads.map(lead => (
                      <div
                        key={lead.id}
                        className="bg-white rounded-lg p-4 border border-gray-200"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-semibold text-gray-900">{lead.name || 'Nom inconnu'}</p>
                            <div className="flex flex-col gap-1 mt-2">
                              {lead.email && (
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                  <Mail size={14} />
                                  <span>{lead.email}</span>
                                </div>
                              )}
                              {lead.phone && (
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                  <Phone size={14} />
                                  <span>{lead.phone}</span>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              lead.status === 'new' ? 'bg-blue-100 text-blue-800' :
                              lead.status === 'contacted' ? 'bg-yellow-100 text-yellow-800' :
                              lead.status === 'converted' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {lead.status || 'Nouveau'}
                            </span>
                            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1 justify-end">
                              <Calendar size={12} />
                              {formatDate(lead.created_at)}
                            </p>
                          </div>
                        </div>
                        {lead.message && (
                          <p className="text-sm text-gray-600 mt-2 p-2 bg-gray-50 rounded border-l-2 border-blue-500">
                            {lead.message}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="border-t pt-4 flex gap-3">
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  navigate(`/admin/services/edit/${selectedService.id}`);
                }}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Éditer le service
              </button>
              <button
                onClick={() => handleToggleStatus(selectedService.id, selectedService.is_active)}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  selectedService.is_active
                    ? 'bg-orange-600 text-white hover:bg-orange-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {selectedService.is_active ? 'Désactiver' : 'Activer'}
              </button>
            </div>
          </div>
        </BaseModal>
      )}
    </div>
  );
};

export default ServicesTab;
