import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { formatCurrency, formatNumber } from '../../utils/helpers';
import { 
  Plus, Search, MoreVertical, Pause, Play, Archive, Target, 
  TrendingUp, Users, DollarSign, Zap, Eye, Edit, Trash2
} from 'lucide-react';

const CampaignsList = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [actionModal, setActionModal] = useState({ isOpen: false, campaign: null, action: null });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/campaigns');
      setCampaigns(response.data.data || []);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  // Calculer les stats
  const campaignStats = {
    total: campaigns.length,
    active: campaigns.filter(c => c.status === 'active').length,
    totalBudget: campaigns.reduce((sum, c) => sum + (parseFloat(c.budget) || 0), 0),
    avgCommission: campaigns.length > 0 
      ? campaigns.reduce((sum, c) => sum + (parseFloat(c.commission_rate) || 0), 0) / campaigns.length 
      : 0
  };

  const handleUpdateStatus = async (campaignId, newStatus) => {
    try {
      await api.put(`/api/campaigns/${campaignId}/status`, { status: newStatus });
      await fetchCampaigns();
      setActionModal({ isOpen: false, campaign: null, action: null });
      toast.success(`Campagne ${newStatus === 'active' ? 'activée' : newStatus === 'paused' ? 'mise en pause' : 'archivée'}`);
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Erreur lors de la mise à jour du statut');
    }
  };

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         campaign.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      key: 'name',
      label: 'Campagne',
      render: (campaign) => (
        <div>
          <div className="font-medium text-gray-900">{campaign.name}</div>
          <div className="text-sm text-gray-500">{campaign.description}</div>
        </div>
      )
    },
    {
      key: 'category',
      label: 'Catégorie',
      accessor: 'category',
      render: (row) => row.category || 'Non défini'
    },
    {
      key: 'budget',
      label: 'Budget',
      render: (campaign) => formatCurrency(campaign.budget)
    },
    {
      key: 'commission_rate',
      label: 'Commission',
      render: (campaign) => `${campaign.commission_rate}%`
    },
    {
      key: 'influencers',
      label: 'Influenceurs',
      render: (campaign) => formatNumber(campaign.influencers_count || 0)
    },
    {
      key: 'status',
      label: 'Statut',
      render: (campaign) => (
        <Badge status={campaign.status}>
          {campaign.status === 'active' ? 'Active' :
           campaign.status === 'paused' ? 'Pausée' :
           campaign.status === 'ended' ? 'Terminée' : 'Brouillon'}
        </Badge>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (campaign) => (
        <div className="flex gap-2">
          {campaign.status === 'active' && (
            <button
              onClick={() => setActionModal({ isOpen: true, campaign, action: 'pause' })}
              className="text-yellow-600 hover:text-yellow-700"
              title="Mettre en pause"
            >
              <Pause size={18} />
            </button>
          )}
          {campaign.status === 'paused' && (
            <button
              onClick={() => setActionModal({ isOpen: true, campaign, action: 'activate' })}
              className="text-green-600 hover:text-green-700"
              title="Activer"
            >
              <Play size={18} />
            </button>
          )}
          <button
            onClick={() => setActionModal({ isOpen: true, campaign, action: 'archive' })}
            className="text-gray-600 hover:text-gray-700"
            title="Archiver"
          >
            <Archive size={18} />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-start"
      >
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">Campagnes</h1>
          <p className="text-gray-600 mt-2 text-lg">
            {user?.role === 'influencer' 
              ? 'Découvrez les campagnes disponibles et postulez' 
              : 'Gérez vos campagnes marketing avec puissance'}
          </p>
        </div>
        {/* Bouton Créer uniquement pour merchants et admins */}
        {(user?.role === 'merchant' || user?.role === 'admin') && (
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button disabled={loading} onClick={() => navigate('/campaigns/create')} data-testid="create-campaign-btn">
              <Plus size={20} className="mr-2" />
              Nouvelle Campagne
            </Button>
          </motion.div>
        )}
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { icon: Target, label: "Total Campagnes", value: campaignStats.total, color: "orange", gradient: "from-orange-500 to-red-600" },
          { icon: TrendingUp, label: "Campagnes Actives", value: campaignStats.active, color: "green", gradient: "from-green-500 to-emerald-600" },
          { icon: DollarSign, label: "Budget Total", value: formatCurrency(campaignStats.totalBudget), color: "blue", gradient: "from-blue-500 to-indigo-600" },
          { icon: Zap, label: "Commission Moy.", value: `${campaignStats.avgCommission.toFixed(1)}%`, color: "purple", gradient: "from-purple-500 to-pink-600" }
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
          >
            <Card className="relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 opacity-10 rounded-full -mr-8 -mt-8"></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-4xl font-black text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`bg-gradient-to-br ${stat.gradient} p-4 rounded-xl shadow-lg`}>
                  <stat.icon size={28} className="text-white" />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Search and Filters */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        <Card className="bg-white/80 backdrop-blur-sm">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-orange-600 transition-colors" size={20} />
              <input
                type="text"
                placeholder="Rechercher une campagne..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:bg-white transition-all shadow-sm"
                data-testid="search-input"
              />
            </div>
            
            {/* Filtre par statut */}
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="pl-4 pr-10 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-orange-500 focus:bg-white transition-all shadow-sm cursor-pointer appearance-none min-w-[200px]"
              >
                <option value="all">📊 Tous les statuts</option>
                <option value="active">✅ Actives</option>
                <option value="paused">⏸️ Pausées</option>
                <option value="draft">📝 Brouillons</option>
                <option value="ended">🏁 Terminées</option>
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>
          
          {/* Compteur de résultats */}
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-600">
              <span className="font-bold text-gray-900">{filteredCampaigns.length}</span> campagne{filteredCampaigns.length > 1 ? 's' : ''} {statusFilter !== 'all' && `(${statusFilter === 'active' ? 'actives' : statusFilter === 'paused' ? 'pausées' : statusFilter === 'draft' ? 'brouillons' : 'terminées'})`}
            </p>
          </div>
        </Card>
      </motion.div>

      {/* Campaigns Grid */}
      <AnimatePresence mode="wait">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden animate-pulse">
                <div className="h-40 bg-gradient-to-br from-gray-200 to-gray-300"></div>
                <div className="p-6 space-y-3">
                  <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <div className="h-12 bg-gray-200 rounded"></div>
                    <div className="h-12 bg-gray-200 rounded"></div>
                    <div className="h-12 bg-gray-200 rounded"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : filteredCampaigns.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card className="py-16">
              <EmptyState
                icon={Target}
                title={searchTerm ? "Aucune campagne trouvée" : "Aucune campagne pour le moment"}
                description={
                  searchTerm 
                    ? "Essayez avec d'autres mots-clés" 
                    : user?.role === 'influencer'
                      ? "Il n'y a pas encore de campagne disponible. Revenez bientôt !"
                      : "Créez votre première campagne pour commencer à travailler avec des influenceurs"
                }
                actionLabel={!searchTerm && (user?.role === 'merchant' || user?.role === 'admin') ? "Créer une campagne" : null}
                onAction={!searchTerm && (user?.role === 'merchant' || user?.role === 'admin') ? () => navigate('/campaigns/create') : undefined}
              />
            </Card>
          </motion.div>
        ) : (
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {filteredCampaigns.map((campaign, index) => {
              const categoryGradients = {
                'Mode': 'from-pink-400 via-purple-400 to-indigo-400',
                'Beauté': 'from-rose-400 via-pink-400 to-fuchsia-400',
                'Technologie': 'from-blue-400 via-cyan-400 to-teal-400',
                'Tech': 'from-blue-400 via-cyan-400 to-teal-400',
                'Sport': 'from-orange-400 via-amber-400 to-yellow-400',
                'Fitness': 'from-orange-400 via-amber-400 to-yellow-400',
                'Alimentation': 'from-green-400 via-emerald-400 to-lime-400',
                'Gastronomie': 'from-green-400 via-emerald-400 to-lime-400',
                'Maison': 'from-indigo-400 via-violet-400 to-purple-400'
              };
              
              const gradient = categoryGradients[campaign.category] || 'from-gray-400 via-gray-500 to-gray-600';
              
              return (
                <motion.div
                  key={campaign.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ y: -8 }}
                  className="group cursor-pointer"
                  onClick={() => navigate(`/campaigns/${campaign.id}`)}
                >
                  <Card className="overflow-hidden h-full hover:shadow-2xl transition-all duration-300 border border-gray-100">
                    {/* Header avec gradient */}
                    <div className={`relative h-40 bg-gradient-to-br ${gradient} overflow-hidden`}>
                      <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-colors" />
                      
                      {/* Badges */}
                      <div className="absolute top-4 left-4 flex gap-2">
                        <span className="bg-white/90 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-gray-900 border border-white/20">
                          {campaign.category || 'Non défini'}
                        </span>
                      </div>
                      
                      {/* Status Badge */}
                      <div className="absolute top-4 right-4">
                        <span className={`px-3 py-1.5 rounded-full text-xs font-bold shadow-lg ${
                          campaign.status === 'active' ? 'bg-green-500 text-white' :
                          campaign.status === 'paused' ? 'bg-yellow-500 text-white' :
                          campaign.status === 'ended' ? 'bg-gray-500 text-white' : 'bg-blue-500 text-white'
                        }`}>
                          {campaign.status === 'active' ? 'Active' :
                           campaign.status === 'paused' ? 'Pausée' :
                           campaign.status === 'ended' ? 'Terminée' : 'Brouillon'}
                        </span>
                      </div>
                      
                      {/* Icon */}
                      <div className="absolute bottom-4 left-4">
                        <div className="bg-white/20 backdrop-blur-md p-3 rounded-xl border border-white/30">
                          <Target className="text-white" size={24} />
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                      <div className="mb-4">
                        <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-orange-600 transition-colors line-clamp-1">
                          {campaign.name}
                        </h3>
                        <p className="text-sm text-gray-500 line-clamp-2 h-10">
                          {campaign.description}
                        </p>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-3 gap-3 mb-6 bg-gray-50 rounded-xl p-4 border border-gray-100">
                        <div className="text-center">
                          <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                            <DollarSign size={12} />
                          </div>
                          <div className="text-lg font-black text-gray-900">
                            {formatCurrency(campaign.budget)}
                          </div>
                          <div className="text-xs text-gray-500">Budget</div>
                        </div>
                        <div className="text-center border-l border-gray-200">
                          <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                            <Zap size={12} />
                          </div>
                          <div className="text-lg font-black text-orange-600">
                            {campaign.commission_rate}%
                          </div>
                          <div className="text-xs text-gray-500">Commission</div>
                        </div>
                        <div className="text-center border-l border-gray-200">
                          <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                            <Users size={12} />
                          </div>
                          <div className="text-lg font-black text-gray-900">
                            {formatNumber(campaign.influencers_count || 0)}
                          </div>
                          <div className="text-xs text-gray-500">Influenceurs</div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/campaigns/${campaign.id}`);
                          }}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold"
                        >
                          <Eye size={18} />
                          Voir
                        </motion.button>
                        
                        {campaign.status === 'active' && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionModal({ isOpen: true, campaign, action: 'pause' });
                            }}
                            className="px-4 py-3 bg-white border-2 border-yellow-500 text-yellow-600 rounded-lg hover:bg-yellow-50 transition-all"
                            title="Mettre en pause"
                          >
                            <Pause size={18} />
                          </motion.button>
                        )}
                        
                        {campaign.status === 'paused' && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionModal({ isOpen: true, campaign, action: 'activate' });
                            }}
                            className="px-4 py-3 bg-white border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 transition-all"
                            title="Activer"
                          >
                            <Play size={18} />
                          </motion.button>
                        )}
                        
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActionModal({ isOpen: true, campaign, action: 'archive' });
                          }}
                          className="px-4 py-3 bg-white border-2 border-gray-200 text-gray-600 rounded-lg hover:border-gray-400 transition-all"
                          title="Archiver"
                        >
                          <Archive size={18} />
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

      {/* Action Confirmation Modal */}
      <Modal
        isOpen={actionModal.isOpen}
        onClose={() => setActionModal({ isOpen: false, campaign: null, action: null })}
        title="Confirmer l'action"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            {actionModal.action === 'pause' && 'Voulez-vous mettre en pause cette campagne ?'}
            {actionModal.action === 'activate' && 'Voulez-vous activer cette campagne ?'}
            {actionModal.action === 'archive' && 'Voulez-vous archiver cette campagne ?'}
          </p>
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => setActionModal({ isOpen: false, campaign: null, action: null })}
            >
              Annuler
            </Button>
            <Button
              onClick={() => handleUpdateStatus(
                actionModal.campaign?.id,
                actionModal.action === 'pause' ? 'paused' :
                actionModal.action === 'activate' ? 'active' : 'archived'
              )}
            >
              Confirmer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CampaignsList;
