import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Table from '../../components/common/Table';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import EmptyState from '../../components/common/EmptyState';
import {
  Briefcase, Plus, Edit, Trash2, Search, Eye, TrendingUp,
  DollarSign, Archive, Users, Target, BarChart
} from 'lucide-react';

const ServicesListPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, service: null });
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    avgPricePerLead: 0,
    totalCapacity: 0
  });

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/services');
      const servicesData = response.data.services || [];
      setServices(servicesData);
      
      // Calculer statistiques
      const total = servicesData.length;
      const active = servicesData.filter(s => s.is_available !== false).length;
      const avgPricePerLead = total > 0 
        ? servicesData.reduce((sum, s) => sum + (parseFloat(s.price_per_lead) || 0), 0) / total
        : 0;
      const totalCapacity = servicesData.reduce((sum, s) => sum + (parseInt(s.capacity_per_month) || 0), 0);
      
      setStats({ total, active, avgPricePerLead, totalCapacity });
    } catch (error) {
      console.error('Error fetching services:', error);
      toast.error('Erreur lors du chargement des services');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (serviceId) => {
    try {
      await api.delete(`/api/services/${serviceId}`);
      setDeleteModal({ isOpen: false, service: null });
      await fetchServices();
      toast.success('Service supprimé avec succès');
    } catch (error) {
      console.error('Error deleting service:', error);
      toast.error('Erreur lors de la suppression du service');
    }
  };

  const filteredServices = services.filter(service =>
    service.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Fonction utilitaire pour gérer les images (JSONB array)
  const getFirstImage = (service) => {
    if (!service.images) return null;

    if (Array.isArray(service.images) && service.images.length > 0) {
      return service.images[0];
    }

    if (typeof service.images === 'string') {
      try {
        const parsed = JSON.parse(service.images);
        return Array.isArray(parsed) && parsed.length > 0 ? parsed[0] : null;
      } catch {
        return null;
      }
    }

    return null;
  };

  const columns = useMemo(() => [
    {
      key: 'name',
      label: 'Service',
      render: (service) => {
        const imageUrl = getFirstImage(service);
        
        return (
          <div className="flex items-center space-x-3">
            {imageUrl ? (
              <img 
                src={imageUrl} 
                alt={service.name}
                className="w-12 h-12 rounded-lg object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            ) : (
              <div className="w-12 h-12 bg-gradient-to-br from-teal-100 to-teal-200 rounded-lg flex items-center justify-center">
                <Briefcase className="text-teal-600" size={24} />
              </div>
            )}
            <div>
              <div className="font-medium text-gray-900">{service.name}</div>
              <div className="text-sm text-gray-500">{service.category}</div>
            </div>
          </div>
        );
      }
    },
    {
      key: 'merchant',
      label: 'Marchand',
      render: (service) => (
        <div className="text-sm">
          <div className="font-medium text-gray-900">
            {service.merchant?.company_name || 'N/A'}
          </div>
          <div className="text-gray-500">
            {service.merchant?.email || ''}
          </div>
        </div>
      )
    },
    {
      key: 'price_per_lead',
      label: 'Prix/Lead',
      render: (service) => (
        <div className="font-medium text-teal-600">
          {parseFloat(service.price_per_lead || 0).toFixed(2)} €
        </div>
      )
    },
    {
      key: 'capacity_per_month',
      label: 'Capacité/Mois',
      render: (service) => (
        <div className="text-sm">
          <div className="flex items-center space-x-1">
            <Users size={14} className="text-gray-400" />
            <span>{service.capacity_per_month || 0} leads</span>
          </div>
          <div className="text-xs text-gray-500">
            {service.total_leads || 0} utilisés
          </div>
        </div>
      )
    },
    {
      key: 'status',
      label: 'Statut',
      render: (service) => (
        <Badge
          variant={service.is_available !== false ? 'success' : 'secondary'}
          text={service.is_available !== false ? 'Disponible' : 'Indisponible'}
        />
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (service) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => navigate(`/services/${service.id}`)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Voir détails"
          >
            <Eye size={18} />
          </button>
          <button
            onClick={() => navigate(`/services/${service.id}/edit`)}
            className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
            title="Modifier"
          >
            <Edit size={18} />
          </button>
          <button
            onClick={() => setDeleteModal({ isOpen: true, service })}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Supprimer"
          >
            <Trash2 size={18} />
          </button>
        </div>
      )
    }
  ], [navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des services...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* En-tête */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">Services</h1>
          <p className="mt-2 text-gray-600 text-lg">
            Gérez tous les services de la plateforme avec efficacité
          </p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button
            onClick={() => navigate('/services/create')}
            icon={<Plus size={20} />}
          >
            Nouveau Service
          </Button>
        </motion.div>
      </motion.div>

      {/* Cartes de statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { icon: Briefcase, label: "Total Services", value: stats.total, color: "teal", gradient: "from-teal-500 to-cyan-600" },
          { icon: TrendingUp, label: "Services Actifs", value: stats.active, color: "green", gradient: "from-green-500 to-emerald-600" },
          { icon: DollarSign, label: "Prix Moyen/Lead", value: `${stats.avgPricePerLead.toFixed(2)} €`, color: "blue", gradient: "from-blue-500 to-indigo-600" },
          { icon: Users, label: "Capacité Totale", value: `${stats.totalCapacity}`, color: "purple", gradient: "from-purple-500 to-pink-600", suffix: " leads/mois" }
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
          >
            <Card className="relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 opacity-10 rounded-full -mr-8 -mt-8" style={{ background: `linear-gradient(135deg, var(--tw-gradient-stops))` }}></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-4xl font-black text-gray-900 mt-2">
                    {stat.value}{stat.suffix && <span className="text-xl text-gray-500">{stat.suffix}</span>}
                  </p>
                </div>
                <div className={`bg-gradient-to-br ${stat.gradient} p-4 rounded-xl shadow-lg`}>
                  <stat.icon size={28} className="text-white" />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Barre de recherche et filtres */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        <Card className="bg-white/80 backdrop-blur-sm">
          <div className="p-6">
            <div className="flex items-center space-x-2">
              <div className="relative flex-1 group">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-teal-600 transition-colors" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher un service..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 focus:ring-2 focus:ring-teal-500 focus:border-transparent focus:bg-white transition-all shadow-sm"
                />
              </div>
            </div>
          </div>

          {/* Grille des services */}
          <AnimatePresence mode="wait">
            {filteredServices.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="py-16"
              >
                <EmptyState
                  icon={<Briefcase size={48} />}
                  title="Aucun service trouvé"
                  description={searchTerm ? "Aucun service ne correspond à votre recherche" : "Commencez par créer votre premier service"}
                  action={
                    !searchTerm && (
                      <Button
                        onClick={() => navigate('/services/create')}
                        icon={<Plus size={20} />}
                      >
                        Créer un service
                      </Button>
                    )
                  }
                />
              </motion.div>
            ) : (
              <motion.div 
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {filteredServices.map((service, index) => {
                  const imageUrl = getFirstImage(service);
                  return (
                    <motion.div
                      key={service.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ y: -8 }}
                      className="group"
                    >
                      <Card className="overflow-hidden h-full hover:shadow-2xl transition-all duration-300 border border-gray-100">
                        {/* Image */}
                        <div className="relative h-56 bg-gradient-to-br from-teal-100 to-cyan-200 overflow-hidden">
                          {imageUrl ? (
                            <img
                              src={imageUrl}
                              alt={service.name}
                              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <Briefcase size={64} className="text-teal-300" />
                            </div>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                          
                          {/* Badges */}
                          <div className="absolute top-4 left-4">
                            <span className="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-gray-900 border border-gray-200">
                              {service.category}
                            </span>
                          </div>
                          
                          {/* Status Badge */}
                          <div className="absolute top-4 right-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${service.is_available !== false ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'}`}>
                              {service.is_available !== false ? 'Disponible' : 'Indisponible'}
                            </span>
                          </div>
                        </div>

                        {/* Content */}
                        <div className="p-6">
                          <div className="mb-4">
                            <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-teal-600 transition-colors line-clamp-1">
                              {service.name}
                            </h3>
                            <div className="flex items-center text-sm text-gray-500 mb-2">
                              <span className="w-2 h-2 rounded-full bg-gray-300 mr-2"></span>
                              {service.merchant?.company_name || 'N/A'}
                            </div>
                          </div>

                          {/* Stats Grid */}
                          <div className="grid grid-cols-2 gap-4 mb-6 bg-gray-50 rounded-xl p-4 border border-gray-100">
                            <div>
                              <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                                <DollarSign size={12} /> Prix/Lead
                              </div>
                              <div className="text-2xl font-black text-teal-600">
                                {parseFloat(service.price_per_lead || 0).toFixed(2)} €
                              </div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                                <Target size={12} /> Capacité
                              </div>
                              <div className="text-lg font-bold text-gray-900">
                                {service.capacity_per_month || 0}
                                <span className="text-xs text-gray-500 ml-1">leads/m</span>
                              </div>
                            </div>
                          </div>

                          {/* Progress bar */}
                          <div className="mb-6">
                            <div className="flex justify-between text-xs text-gray-600 mb-2">
                              <span>Utilisés</span>
                              <span>{service.total_leads || 0} / {service.capacity_per_month || 0}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-teal-500 to-cyan-600 h-2 rounded-full transition-all"
                                style={{ width: `${Math.min(((service.total_leads || 0) / (service.capacity_per_month || 1)) * 100, 100)}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex gap-2">
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => navigate(`/services/${service.id}`)}
                              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-semibold"
                            >
                              <Eye size={18} />
                              Voir
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => navigate(`/services/${service.id}/edit`)}
                              className="px-4 py-3 bg-white border-2 border-gray-200 text-gray-700 rounded-lg hover:border-teal-600 hover:text-teal-600 transition-all"
                            >
                              <Edit size={18} />
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => setDeleteModal({ isOpen: true, service })}
                              className="px-4 py-3 bg-white border-2 border-gray-200 text-red-600 rounded-lg hover:border-red-600 hover:bg-red-50 transition-all"
                            >
                              <Trash2 size={18} />
                            </motion.button>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  );
                })}
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>

      {/* Modal de confirmation de suppression */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, service: null })}
        title="Supprimer le service"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Êtes-vous sûr de vouloir supprimer le service <strong>{deleteModal.service?.name}</strong> ? 
            Cette action est irréversible.
          </p>
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => setDeleteModal({ isOpen: false, service: null })}
            >
              Annuler
            </Button>
            <Button
              variant="danger"
              onClick={() => handleDelete(deleteModal.service?.id)}
              icon={<Trash2 size={18} />}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ServicesListPage;
