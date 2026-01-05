import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { formatCurrency, formatNumber } from '../../utils/helpers';
import { 
  Plus, Search, Pause, Play, Archive, Target, 
  TrendingUp, Users, DollarSign, Zap, Eye, Sparkles,
  Filter, ChevronDown, RefreshCw, Rocket, Calendar,
  Clock, Star, Award, ArrowRight, Heart, Share2
} from 'lucide-react';

const CampaignsList = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [actionModal, setActionModal] = useState({ isOpen: false, campaign: null, action: null });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
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

  // Gradients par catégorie
  const categoryGradients = {
    'Mode': { bg: 'from-pink-500 via-rose-500 to-purple-600', light: 'from-pink-50 to-purple-50' },
    'Fashion': { bg: 'from-pink-500 via-rose-500 to-purple-600', light: 'from-pink-50 to-purple-50' },
    'Beauté': { bg: 'from-rose-400 via-pink-500 to-fuchsia-600', light: 'from-rose-50 to-fuchsia-50' },
    'Beauty': { bg: 'from-rose-400 via-pink-500 to-fuchsia-600', light: 'from-rose-50 to-fuchsia-50' },
    'Technologie': { bg: 'from-blue-500 via-cyan-500 to-teal-500', light: 'from-blue-50 to-teal-50' },
    'Tech': { bg: 'from-blue-500 via-cyan-500 to-teal-500', light: 'from-blue-50 to-teal-50' },
    'Sport': { bg: 'from-orange-500 via-amber-500 to-yellow-500', light: 'from-orange-50 to-yellow-50' },
    'Fitness': { bg: 'from-green-500 via-emerald-500 to-teal-500', light: 'from-green-50 to-teal-50' },
    'Alimentation': { bg: 'from-green-500 via-lime-500 to-emerald-500', light: 'from-green-50 to-emerald-50' },
    'Gastronomie': { bg: 'from-amber-500 via-orange-500 to-red-500', light: 'from-amber-50 to-red-50' },
    'Food': { bg: 'from-amber-500 via-orange-500 to-red-500', light: 'from-amber-50 to-red-50' },
    'Maison': { bg: 'from-indigo-500 via-violet-500 to-purple-600', light: 'from-indigo-50 to-purple-50' },
    'Home': { bg: 'from-indigo-500 via-violet-500 to-purple-600', light: 'from-indigo-50 to-purple-50' },
    'default': { bg: 'from-gray-500 via-slate-500 to-zinc-600', light: 'from-gray-50 to-slate-50' }
  };

  const getGradient = (category) => categoryGradients[category] || categoryGradients['default'];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: "spring", stiffness: 100 }
    }
  };

  return (
    <div className="space-y-6 p-6 pb-12">
      {/* Header avec gradient épique */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-orange-600 via-red-500 to-pink-600 p-8 text-white shadow-2xl"
      >
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-48 translate-x-48 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full translate-y-32 -translate-x-32 blur-2xl"></div>
        <div className="absolute top-1/2 left-1/2 w-32 h-32 bg-yellow-400/20 rounded-full blur-xl"></div>
        
        {/* Floating icons */}
        <motion.div 
          animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-8 right-32 opacity-20"
        >
          <Rocket className="w-16 h-16" />
        </motion.div>
        <motion.div 
          animate={{ y: [0, 10, 0], rotate: [0, -5, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          className="absolute bottom-8 right-16 opacity-20"
        >
          <Star className="w-12 h-12" />
        </motion.div>
        
        <div className="relative z-10 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div className="flex items-start gap-4">
            <div className="p-4 bg-white/20 rounded-2xl backdrop-blur-sm shadow-lg">
              <Target className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-tight">Campagnes</h1>
              <p className="text-white/80 mt-2 text-lg flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                {user?.role === 'influencer' 
                  ? 'Découvrez les meilleures opportunités et boostez vos revenus' 
                  : 'Gérez vos campagnes et atteignez vos objectifs'}
              </p>
            </div>
          </div>
          
          {/* Bouton Créer uniquement pour merchants et admins */}
          {(user?.role === 'merchant' || user?.role === 'admin') && (
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 20px 40px rgba(0,0,0,0.2)" }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/campaigns/create')}
              data-testid="create-campaign-btn"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-4 bg-white text-orange-600 rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300"
            >
              <Plus className="w-5 h-5" />
              Nouvelle Campagne
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </motion.div>

      {/* Stats Cards - Design moderne */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {[
          { 
            icon: Target, 
            label: "Total Campagnes", 
            value: campaignStats.total, 
            gradient: "from-orange-500 to-red-600",
            bgGradient: "from-orange-50 to-red-50",
            iconBg: "bg-orange-100",
            textColor: "text-orange-600"
          },
          { 
            icon: TrendingUp, 
            label: "Campagnes Actives", 
            value: campaignStats.active, 
            gradient: "from-emerald-500 to-green-600",
            bgGradient: "from-emerald-50 to-green-50",
            iconBg: "bg-emerald-100",
            textColor: "text-emerald-600"
          },
          { 
            icon: DollarSign, 
            label: "Budget Total", 
            value: formatCurrency(campaignStats.totalBudget), 
            gradient: "from-blue-500 to-indigo-600",
            bgGradient: "from-blue-50 to-indigo-50",
            iconBg: "bg-blue-100",
            textColor: "text-blue-600"
          },
          { 
            icon: Zap, 
            label: "Commission Moy.", 
            value: `${campaignStats.avgCommission.toFixed(1)}%`, 
            gradient: "from-purple-500 to-pink-600",
            bgGradient: "from-purple-50 to-pink-50",
            iconBg: "bg-purple-100",
            textColor: "text-purple-600"
          }
        ].map((stat, index) => (
          <motion.div
            key={index}
            variants={itemVariants}
            whileHover={{ y: -5, scale: 1.02 }}
            className={`relative overflow-hidden bg-gradient-to-br ${stat.bgGradient} rounded-2xl p-6 border border-gray-100 shadow-lg hover:shadow-xl transition-all duration-300`}
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br opacity-20 rounded-full -translate-y-8 translate-x-8 blur-xl"></div>
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 ${stat.iconBg} rounded-xl shadow-sm`}>
                  <stat.icon className={`w-6 h-6 ${stat.textColor}`} />
                </div>
                <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${stat.gradient} animate-pulse`}></div>
              </div>
              
              <p className="text-sm font-medium text-gray-500 mb-1">{stat.label}</p>
              <p className={`text-3xl font-black ${stat.textColor}`}>{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Search and Filters - Design amélioré */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-5"
      >
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          <div className="flex-1 relative group w-full">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-orange-500 transition-colors w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher une campagne..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent focus:bg-white transition-all"
              data-testid="search-input"
            />
          </div>
          
          <div className="flex gap-3 w-full lg:w-auto">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-5 py-4 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all duration-200 font-medium text-gray-700"
            >
              <Filter className="w-5 h-5" />
              <span>Filtres</span>
              <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            <button
              onClick={fetchCampaigns}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white rounded-xl transition-all duration-200 font-medium shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Actualiser</span>
            </button>
          </div>
        </div>
        
        {/* Filtres déroulants */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-gray-100"
            >
              <div className="flex flex-wrap gap-2">
                {[
                  { value: 'all', label: 'Tous', emoji: '📊' },
                  { value: 'active', label: 'Actives', emoji: '✅' },
                  { value: 'paused', label: 'Pausées', emoji: '⏸️' },
                  { value: 'draft', label: 'Brouillons', emoji: '📝' },
                  { value: 'ended', label: 'Terminées', emoji: '🏁' }
                ].map((status) => (
                  <button
                    key={status.value}
                    onClick={() => setStatusFilter(status.value)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-200 font-medium ${
                      statusFilter === status.value 
                        ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span>{status.emoji}</span>
                    <span>{status.label}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Compteur de résultats */}
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            <span className="font-bold text-gray-900">{filteredCampaigns.length}</span> campagne{filteredCampaigns.length > 1 ? 's' : ''} 
            {statusFilter !== 'all' && ` (${statusFilter === 'active' ? 'actives' : statusFilter === 'paused' ? 'pausées' : statusFilter === 'draft' ? 'brouillons' : 'terminées'})`}
          </p>
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Effacer la recherche
            </button>
          )}
        </div>
      </motion.div>

      {/* Campaigns Grid */}
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
          >
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-3xl shadow-lg border border-gray-100 overflow-hidden animate-pulse">
                <div className="h-44 bg-gradient-to-br from-gray-200 via-gray-300 to-gray-200"></div>
                <div className="p-6 space-y-4">
                  <div className="h-6 bg-gray-200 rounded-lg w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded-lg w-full"></div>
                  <div className="grid grid-cols-3 gap-3 mt-6">
                    <div className="h-20 bg-gray-100 rounded-xl"></div>
                    <div className="h-20 bg-gray-100 rounded-xl"></div>
                    <div className="h-20 bg-gray-100 rounded-xl"></div>
                  </div>
                  <div className="h-12 bg-gray-200 rounded-xl mt-4"></div>
                </div>
              </div>
            ))}
          </motion.div>
        ) : filteredCampaigns.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="bg-white rounded-3xl shadow-lg border border-gray-100 p-16"
          >
            <div className="flex flex-col items-center justify-center text-center">
              <div className="relative">
                <div className="absolute inset-0 bg-orange-100 rounded-full blur-xl opacity-50"></div>
                <div className="relative p-6 bg-gradient-to-br from-orange-100 to-red-100 rounded-full mb-6">
                  <Target className="w-16 h-16 text-orange-500" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                {searchTerm ? "Aucune campagne trouvée" : "Aucune campagne pour le moment"}
              </h3>
              <p className="text-gray-500 max-w-md mb-6">
                {searchTerm 
                  ? `Aucun résultat pour "${searchTerm}". Essayez avec d'autres mots-clés.` 
                  : user?.role === 'influencer'
                    ? "Il n'y a pas encore de campagne disponible. Revenez bientôt !"
                    : "Créez votre première campagne pour commencer à travailler avec des influenceurs."}
              </p>
              {!searchTerm && (user?.role === 'merchant' || user?.role === 'admin') && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/campaigns/create')}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Créer une campagne
                </motion.button>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
          >
            {filteredCampaigns.map((campaign, index) => {
              const gradient = getGradient(campaign.category);
              
              return (
                <motion.div
                  key={campaign.id}
                  variants={itemVariants}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="group cursor-pointer"
                  onClick={() => navigate(`/campaigns/${campaign.id}`)}
                >
                  <div className="relative bg-white rounded-3xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-500">
                    {/* Header avec gradient et image */}
                    <div className={`relative h-44 bg-gradient-to-br ${gradient.bg} overflow-hidden`}>
                      {/* Pattern overlay */}
                      <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-4 left-4 w-32 h-32 border-2 border-white/30 rounded-full"></div>
                        <div className="absolute bottom-4 right-4 w-24 h-24 border-2 border-white/30 rounded-full"></div>
                        <div className="absolute top-1/2 left-1/2 w-16 h-16 border-2 border-white/30 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                      </div>
                      
                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300"></div>
                      
                      {/* Merchant Badge */}
                      <div className="absolute top-4 left-4">
                        <motion.span 
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="inline-flex items-center gap-1.5 bg-white/95 backdrop-blur-md px-4 py-2 rounded-full text-sm font-bold text-gray-800 shadow-lg"
                        >
                          <Award className="w-4 h-4 text-amber-500" />
                          {campaign.merchant_name || campaign.category || 'Non défini'}
                        </motion.span>
                      </div>
                      
                      {/* Status Badge */}
                      <div className="absolute top-4 right-4">
                        <motion.span 
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-bold shadow-lg ${
                            campaign.status === 'active' 
                              ? 'bg-emerald-500 text-white' 
                              : campaign.status === 'paused' 
                                ? 'bg-amber-500 text-white'
                                : campaign.status === 'ended' 
                                  ? 'bg-gray-500 text-white' 
                                  : 'bg-blue-500 text-white'
                          }`}
                        >
                          <span className={`w-2 h-2 rounded-full ${
                            campaign.status === 'active' ? 'bg-white animate-pulse' : 'bg-white/70'
                          }`}></span>
                          {campaign.status === 'active' ? 'Active' :
                           campaign.status === 'paused' ? 'Pausée' :
                           campaign.status === 'ended' ? 'Terminée' : 'Brouillon'}
                        </motion.span>
                      </div>
                      
                      {/* Icon */}
                      <div className="absolute bottom-4 left-4">
                        <div className="p-4 bg-white/25 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg group-hover:scale-110 transition-transform duration-300">
                          <Rocket className="w-8 h-8 text-white" />
                        </div>
                      </div>
                      
                      {/* Floating action buttons */}
                      <div className="absolute bottom-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-4 group-hover:translate-y-0">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            // Action de like
                          }}
                          className="p-2.5 bg-white/90 backdrop-blur-md rounded-xl shadow-lg hover:bg-white transition-colors"
                        >
                          <Heart className="w-5 h-5 text-rose-500" />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            // Action de partage
                          }}
                          className="p-2.5 bg-white/90 backdrop-blur-md rounded-xl shadow-lg hover:bg-white transition-colors"
                        >
                          <Share2 className="w-5 h-5 text-blue-500" />
                        </motion.button>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                      <div className="mb-5">
                        <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-orange-600 transition-colors line-clamp-1">
                          {campaign.name}
                        </h3>
                        <p className="text-sm text-gray-500 line-clamp-2 min-h-[40px]">
                          {campaign.description || 'Aucune description disponible'}
                        </p>
                      </div>

                      {/* Stats Grid - Design amélioré */}
                      <div className={`grid grid-cols-3 gap-3 mb-5 bg-gradient-to-r ${gradient.light} rounded-2xl p-4 border border-gray-100`}>
                        <div className="text-center">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <DollarSign className="w-4 h-4 text-gray-400" />
                          </div>
                          <div className="text-lg font-black text-gray-900">
                            {formatCurrency(campaign.budget)}
                          </div>
                          <div className="text-xs text-gray-500 font-medium">Budget</div>
                        </div>
                        <div className="text-center border-l border-gray-200/50">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <Zap className="w-4 h-4 text-orange-400" />
                          </div>
                          <div className="text-lg font-black text-orange-600">
                            {campaign.commission_rate}%
                          </div>
                          <div className="text-xs text-gray-500 font-medium">Commission</div>
                        </div>
                        <div className="text-center border-l border-gray-200/50">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <Users className="w-4 h-4 text-gray-400" />
                          </div>
                          <div className="text-lg font-black text-gray-900">
                            {formatNumber(campaign.influencers_count || 0)}
                          </div>
                          <div className="text-xs text-gray-500 font-medium">Influenceurs</div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/campaigns/${campaign.id}`);
                          }}
                          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3.5 bg-gradient-to-r ${gradient.bg} text-white rounded-xl hover:shadow-lg transition-all duration-300 font-semibold`}
                        >
                          <Eye className="w-5 h-5" />
                          Voir
                          <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </motion.button>
                        
                        {campaign.status === 'active' && (user?.role === 'merchant' || user?.role === 'admin') && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionModal({ isOpen: true, campaign, action: 'pause' });
                            }}
                            className="p-3.5 bg-amber-50 border-2 border-amber-200 text-amber-600 rounded-xl hover:bg-amber-100 transition-all"
                            title="Mettre en pause"
                          >
                            <Pause className="w-5 h-5" />
                          </motion.button>
                        )}
                        
                        {campaign.status === 'paused' && (user?.role === 'merchant' || user?.role === 'admin') && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionModal({ isOpen: true, campaign, action: 'activate' });
                            }}
                            className="p-3.5 bg-emerald-50 border-2 border-emerald-200 text-emerald-600 rounded-xl hover:bg-emerald-100 transition-all"
                            title="Activer"
                          >
                            <Play className="w-5 h-5" />
                          </motion.button>
                        )}
                        
                        {(user?.role === 'merchant' || user?.role === 'admin') && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionModal({ isOpen: true, campaign, action: 'archive' });
                            }}
                            className="p-3.5 bg-gray-50 border-2 border-gray-200 text-gray-500 rounded-xl hover:bg-gray-100 hover:border-gray-300 transition-all"
                            title="Archiver"
                          >
                            <Archive className="w-5 h-5" />
                          </motion.button>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer avec compteur */}
      {!loading && filteredCampaigns.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-sm text-gray-500 py-6"
        >
          <p>
            Affichage de <span className="font-semibold text-gray-700">{filteredCampaigns.length}</span> campagne{filteredCampaigns.length > 1 ? 's' : ''}
            {statusFilter !== 'all' && ` sur ${campaigns.length} au total`}
          </p>
        </motion.div>
      )}

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
