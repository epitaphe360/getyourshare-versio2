import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Package, Plus, Search, Filter, Edit2, Trash2, Eye,
  ChevronLeft, ChevronRight, AlertCircle, DollarSign,
  TrendingUp, Users, Zap, RefreshCw, MoreVertical
} from 'lucide-react';
import api from '../../utils/api';
import ServiceFormModal from '../../components/admin/ServiceFormModal';
import ServiceDetailsModal from '../../components/admin/ServiceDetailsModal';
import BaseModal from '../../components/modals/BaseModal';
import { useToast } from '../../context/ToastContext';

const ServiceManagement = () => {
  const toast = useToast();
  const location = useLocation();
  const navigate = useNavigate();

  // État principal
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedServices, setSelectedServices] = useState([]);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [totalServices, setTotalServices] = useState(0);

  // Recherche et filtres
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categorieFilter, setCategorieFilter] = useState('all');

  // Modals
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'

  // Confirmation modal
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [serviceToDelete, setServiceToDelete] = useState(null);

  // Statistiques
  const [stats, setStats] = useState({
    total_services: 0,
    services_actifs: 0,
    depot_total: 0,
    total_leads: 0,
    leads_aujourd_hui: 0,
    revenus_leads: 0,
    taux_conversion: 0
  });

  // Charger les services
  const loadServices = useCallback(async (signal = null) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(statusFilter !== 'all' && { statut: statusFilter }),
        ...(categorieFilter !== 'all' && { categorie_id: categorieFilter })
      });

      const config = signal ? { signal } : {};
      const response = await api.get(`/api/admin/services?${params}`, config);
      setServices(response.data.services || []);
      setTotalServices(response.data.total || 0);
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur lors du chargement des services:', error);
        toast.error('Erreur lors du chargement des services');
      }
    } finally {
      setLoading(false);
    }
  }, [statusFilter, categorieFilter, toast]);

  // Charger les statistiques
  const loadStats = useCallback(async (signal = null) => {
    try {
      const config = signal ? { signal } : {};
      const response = await api.get('/api/admin/services/stats/dashboard', config);
      setStats(response.data.stats);
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur lors du chargement des stats:', error);
      }
    }
  }, []);

  // Ouvrir la modale d'édition depuis un paramètre de requête (?edit=<id>)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const editId = params.get('edit');

    if (!editId || loading) return;

    const found = services.find((s) => String(s.id) === String(editId));

    if (found) {
      setModalMode('edit');
      setEditingService(found);
      setShowFormModal(true);
      navigate('/admin/services', { replace: true });
    } else {
      toast.error("Service introuvable");
      navigate('/admin/services', { replace: true });
    }
  }, [location.search, services, loading, navigate, toast]);

  // Chargement initial
  useEffect(() => {
    const controller = new AbortController();
    loadServices(controller.signal);
    loadStats(controller.signal);
    return () => controller.abort();
  }, [loadServices, loadStats, currentPage]);

  // Créer un nouveau service
  const handleCreate = () => {
    setModalMode('create');
    setEditingService(null);
    setShowFormModal(true);
  };

  // Éditer un service
  const handleEdit = (service) => {
    setModalMode('edit');
    setEditingService(service);
    setShowFormModal(true);
  };

  // Voir les détails et leads d'un service
  const handleViewDetails = (service) => {
    setSelectedService(service);
    setShowDetailsModal(true);
  };

  const handleCloseForm = useCallback(() => {
    setShowFormModal(false);
    setEditingService(null);
    setModalMode('create');
    if (location.search) {
      navigate('/admin/services', { replace: true });
    }
  }, [location.search, navigate]);

  // Supprimer un service
  const handleDeleteClick = (serviceId) => {
    setServiceToDelete(serviceId);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    try {
      await api.delete(`/api/admin/services/${serviceToDelete}`);
      toast.success('Service supprimé avec succès');
      setShowDeleteConfirm(false);
      setServiceToDelete(null);
      loadServices();
      loadStats();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      toast.error('Erreur lors de la suppression du service');
    }
  };

  // Filtrer les services localement
  const filteredServices = services.filter(service => {
    const matchSearch = searchTerm === '' ||
      service.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.users?.company_name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchSearch;
  });

  // Pagination
  const totalPages = Math.ceil(totalServices / itemsPerPage);
  const paginatedServices = filteredServices.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Calculer le statut visuel
  const getStatusBadge = (service) => {
    const depotActuel = parseFloat(service.depot_actuel || 0);
    const depotInitial = parseFloat(service.depot_initial || 0);
    const pourcentage = depotInitial > 0 ? (depotActuel / depotInitial) * 100 : 0;

    if (service.statut === 'epuise') {
      return <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">⚫ Épuisé</span>;
    } else if (service.statut === 'expire') {
      return <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">⏰ Expiré</span>;
    } else if (pourcentage < 20) {
      return <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">🟡 Critique</span>;
    } else if (pourcentage < 50) {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">🟠 Attention</span>;
    } else {
      return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">🟢 Actif</span>;
    }
  };

  // Calculer la progression du solde
  const getProgressBar = (service) => {
    const depotActuel = parseFloat(service.depot_actuel || 0);
    const depotInitial = parseFloat(service.depot_initial || 0);
    const pourcentage = depotInitial > 0 ? (depotActuel / depotInitial) * 100 : 0;

    let colorClass = 'bg-green-500';
    if (pourcentage < 20) colorClass = 'bg-red-500';
    else if (pourcentage < 50) colorClass = 'bg-orange-500';

    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${colorClass} h-2 rounded-full transition-all`}
          style={{ width: `${pourcentage}%` }}
        ></div>
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🎯 Gestion des Services (Génération de Leads)
        </h1>
        <p className="text-gray-600">
          Gérez les services des marchands et suivez la génération de leads
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Services Actifs</p>
              <p className="text-2xl font-bold text-blue-600">{stats.services_actifs}/{stats.total_services}</p>
            </div>
            <Package className="text-blue-500" size={32} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Leads Générés</p>
              <p className="text-2xl font-bold text-green-600">{stats.total_leads}</p>
              <p className="text-xs text-gray-500">+{stats.leads_aujourd_hui} aujourd'hui</p>
            </div>
            <Users className="text-green-500" size={32} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Revenus Leads</p>
              <p className="text-2xl font-bold text-purple-600">{stats.revenus_leads?.toFixed(2)}€</p>
            </div>
            <DollarSign className="text-purple-500" size={32} />
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taux Conversion</p>
              <p className="text-2xl font-bold text-orange-600">{stats.taux_conversion}%</p>
            </div>
            <TrendingUp className="text-orange-500" size={32} />
          </div>
        </div>
      </div>

      {/* Actions Bar */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Recherche */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher un service ou marchand..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Filtres */}
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="actif">🟢 Actif</option>
              <option value="epuise">⚫ Épuisé</option>
              <option value="expire">⏰ Expiré</option>
              <option value="inactif">⏸️ Inactif</option>
            </select>

            <button
              onClick={loadServices}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
            >
              <RefreshCw size={20} />
            </button>

            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition"
            >
              <Plus size={20} />
              Nouveau Service
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : paginatedServices.length === 0 ? (
          <div className="text-center p-12">
            <Package className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600">Aucun service trouvé</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marchand</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dépôt / Solde</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prix Lead</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {paginatedServices.map((service) => (
                  <tr key={service.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {service.images && service.images.length > 0 ? (
                          <img
                            src={service.images[0]}
                            alt={service.nom}
                            className="w-12 h-12 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
                            <Package size={24} className="text-gray-400" />
                          </div>
                        )}
                        <div>
                          <p className="font-medium text-gray-900">{service.nom}</p>
                          <p className="text-sm text-gray-500">{service.categories?.name || 'N/A'}</p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{service.users?.company_name || service.users?.full_name}</p>
                      <p className="text-sm text-gray-500">{service.users?.email}</p>
                    </td>

                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900">
                        {parseFloat(service.depot_actuel || 0).toFixed(2)}€ / {parseFloat(service.depot_initial || 0).toFixed(2)}€
                      </p>
                      {getProgressBar(service)}
                      <p className="text-xs text-gray-500 mt-1">
                        {service.leads_possibles || 0} leads disponibles
                      </p>
                    </td>

                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{parseFloat(service.prix_par_lead || 0).toFixed(2)}€</p>
                    </td>

                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{service.leads_recus || 0}</p>
                      {service.taux_conversion > 0 && (
                        <p className="text-xs text-green-600">
                          {parseFloat(service.taux_conversion).toFixed(0)}% conversion
                        </p>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      {getStatusBadge(service)}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleViewDetails(service)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          title="Voir détails et leads"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleEdit(service)}
                          className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition"
                          title="Modifier"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(service.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                          title="Supprimer"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Page {currentPage} sur {totalPages} ({totalServices} services au total)
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
              </button>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showFormModal && (
        <ServiceFormModal
          show={showFormModal}
          onClose={handleCloseForm}
          onSuccess={() => {
            handleCloseForm();
            loadServices();
            loadStats();
          }}
          service={editingService}
          mode={modalMode}
        />
      )}

      {showDetailsModal && selectedService && (
        <ServiceDetailsModal
          show={showDetailsModal}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedService(null);
          }}
          service={selectedService}
          onReload={() => {
            loadServices();
            loadStats();
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      <BaseModal
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setServiceToDelete(null);
        }}
        title="Confirmer la suppression"
        size="md"
        footer={
          <div className="flex gap-3 justify-end">
            <button
              onClick={() => {
                setShowDeleteConfirm(false);
                setServiceToDelete(null);
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
            >
              Annuler
            </button>
            <button
              onClick={confirmDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              Supprimer
            </button>
          </div>
        }
      >
        <p className="text-gray-700 mb-2">
          Êtes-vous sûr de vouloir supprimer ce service ?
        </p>
        <p className="text-sm text-red-600">
          ⚠️ Tous les leads associés seront également supprimés. Cette action est irréversible.
        </p>
      </BaseModal>
    </div>
  );
};

export default ServiceManagement;
