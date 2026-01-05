import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { useToast } from '../../context/ToastContext';
import { 
  ArrowLeft, Target, DollarSign, Calendar, Users, TrendingUp, 
  Eye, Heart, Share2, ShoppingCart, Zap, Clock, CheckCircle,
  AlertCircle, Edit, Pause, Play, Archive, BarChart3, Award,
  MessageSquare, FileText, Image, Link as LinkIcon
} from 'lucide-react';

const CampaignDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [influencers, setInfluencers] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [statusModal, setStatusModal] = useState({ isOpen: false, action: null });
  const [editData, setEditData] = useState({});

  useEffect(() => {
    fetchCampaignDetails();
  }, [id]);

  const fetchCampaignDetails = async () => {
    try {
      setLoading(true);
      
      // Récupérer les détails de la campagne
      const campaignResponse = await api.get(`/api/campaigns/${id}`);
      setCampaign(campaignResponse.data);
      
      // Récupérer les statistiques réelles
      try {
        const statsResponse = await api.get(`/api/campaigns/${id}/stats`);
        setStats(statsResponse.data);
      } catch (e) {
        console.error('Error loading stats:', e);
      }
      
      // Récupérer les influenceurs participants réels
      try {
        const influencersResponse = await api.get(`/api/campaigns/${id}/influencers`);
        setInfluencers(influencersResponse.data);
      } catch (e) {
        console.error('Error loading influencers:', e);
      }
      
    } catch (error) {
      console.error('Error fetching campaign details:', error);
      setCampaign(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(value || 0);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('fr-FR').format(value || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Non défini';
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const handleEditClick = () => {
    setEditData({
      name: campaign.name,
      description: campaign.description,
      budget: campaign.budget,
      commission_rate: campaign.commission_rate,
      start_date: campaign.start_date?.split('T')[0],
      end_date: campaign.end_date?.split('T')[0]
    });
    setEditMode(true);
  };

  const handleSaveEdit = async () => {
    try {
      const response = await api.put(`/api/campaigns/${id}`, editData);
      setCampaign(response.data);
      setEditMode(false);
    } catch (error) {
      console.error('Error updating campaign:', error);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await api.put(`/api/campaigns/${id}/status`, { status: newStatus });
      setCampaign({ ...campaign, status: newStatus });
      setStatusModal({ isOpen: false, action: null });
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'paused': return 'bg-yellow-500';
      case 'ended': return 'bg-gray-500';
      default: return 'bg-blue-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Active';
      case 'paused': return 'Pausée';
      case 'ended': return 'Terminée';
      default: return 'Brouillon';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-12 bg-gray-200 rounded-xl w-1/3" />
            <div className="grid grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-xl" />
              ))}
            </div>
            <div className="h-96 bg-gray-200 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 p-8">
        <div className="max-w-7xl mx-auto text-center">
          <AlertCircle className="mx-auto mb-4 text-red-500" size={64} />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Campagne non trouvée</h1>
          <Button onClick={() => navigate('/campaigns')}>
            <ArrowLeft size={18} className="mr-2" />
            Retour aux campagnes
          </Button>
        </div>
      </div>
    );
  }

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
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50">
      {/* Header */}
      <div className={`relative bg-gradient-to-br ${gradient} overflow-hidden`}>
        <div className="absolute inset-0 bg-black/30" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(255,255,255,0.1),transparent)]" />
        
        {/* Animated particles */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-white/20 rounded-full"
              initial={{ 
                x: Math.random() * window.innerWidth, 
                y: Math.random() * 400,
                scale: Math.random() * 0.5 + 0.5
              }}
              animate={{ 
                y: [null, -100],
                opacity: [0.5, 0]
              }}
              transition={{ 
                duration: Math.random() * 3 + 2,
                repeat: Infinity,
                delay: Math.random() * 2
              }}
            />
          ))}
        </div>
        
        <div className="relative max-w-7xl mx-auto px-8 py-12">
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate('/campaigns')}
            className="flex items-center gap-2 text-white/90 hover:text-white mb-6 group"
          >
            <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
            <span className="font-medium">Retour aux campagnes</span>
          </motion.button>

          <div className="flex items-start justify-between">
            <div className="flex-1">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4 mb-4"
              >
                <motion.div 
                  className="bg-white/20 backdrop-blur-md p-4 rounded-2xl border border-white/30"
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <Target className="text-white" size={32} />
                </motion.div>
                <div>
                  <h1 className="text-4xl font-black text-white mb-2 drop-shadow-lg">
                    {campaign.name}
                  </h1>
                  <div className="flex items-center gap-3">
                    <motion.span 
                      className="bg-white/90 backdrop-blur-md px-4 py-1.5 rounded-full text-sm font-bold text-gray-900"
                      whileHover={{ scale: 1.05 }}
                    >
                      {campaign.type || campaign.category || 'Standard'}
                    </motion.span>
                    <motion.span 
                      className={`${getStatusColor(campaign.status)} px-4 py-1.5 rounded-full text-sm font-bold text-white shadow-lg`}
                      animate={{ scale: campaign.status === 'active' ? [1, 1.05, 1] : 1 }}
                      transition={{ duration: 2, repeat: campaign.status === 'active' ? Infinity : 0 }}
                    >
                      {getStatusText(campaign.status)}
                    </motion.span>
                  </div>
                </div>
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-white/90 text-lg max-w-3xl leading-relaxed drop-shadow"
              >
                {campaign.description}
              </motion.p>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex gap-3"
            >
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button 
                  variant="outline" 
                  className="bg-white/20 backdrop-blur-md border-white/30 text-white hover:bg-white/30 shadow-xl"
                  onClick={handleEditClick}
                >
                  <Edit size={18} className="mr-2" />
                  Modifier
                </Button>
              </motion.div>
              {campaign.status === 'active' && (
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button 
                    className="bg-yellow-500 hover:bg-yellow-600 text-white shadow-xl"
                    onClick={() => setStatusModal({ isOpen: true, action: 'pause' })}
                  >
                    <Pause size={18} className="mr-2" />
                    Pause
                  </Button>
                </motion.div>
              )}
              {campaign.status === 'paused' && (
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button 
                    className="bg-green-500 hover:bg-green-600 text-white shadow-xl"
                    onClick={() => setStatusModal({ isOpen: true, action: 'activate' })}
                  >
                    <Play size={18} className="mr-2" />
                    Activer
                  </Button>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-12 -mt-24">
        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <Card className="bg-gradient-to-br from-orange-500 to-red-500 text-white border-0 shadow-2xl hover:shadow-3xl transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-md p-3 rounded-xl">
                  <DollarSign size={24} />
                </div>
                <TrendingUp size={20} className="text-white/60" />
              </div>
              <div className="text-4xl font-black mb-1 drop-shadow-lg">
                {formatCurrency(campaign.budget)}
              </div>
              <div className="text-white/90 text-sm font-semibold tracking-wide">Budget Total</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <Card className="bg-gradient-to-br from-purple-500 to-pink-500 text-white border-0 shadow-2xl hover:shadow-3xl transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-md p-3 rounded-xl">
                  <Zap size={24} />
                </div>
                <Award size={20} className="text-white/60" />
              </div>
              <div className="text-4xl font-black mb-1 drop-shadow-lg">
                {campaign.commission_rate}%
              </div>
              <div className="text-white/90 text-sm font-semibold tracking-wide">Commission</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <Card className="bg-gradient-to-br from-blue-500 to-indigo-500 text-white border-0 shadow-2xl hover:shadow-3xl transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-md p-3 rounded-xl">
                  <Users size={24} />
                </div>
                <BarChart3 size={20} className="text-white/60" />
              </div>
              <div className="text-4xl font-black mb-1 drop-shadow-lg">
                {formatNumber(campaign.influencers_count || 0)}
              </div>
              <div className="text-white/90 text-sm font-semibold tracking-wide">Influenceurs</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <Card className="bg-gradient-to-br from-green-500 to-emerald-500 text-white border-0 shadow-2xl hover:shadow-3xl transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-white/20 backdrop-blur-md p-3 rounded-xl">
                  <ShoppingCart size={24} />
                </div>
                <CheckCircle size={20} className="text-white/60" />
              </div>
              <div className="text-4xl font-black mb-1 drop-shadow-lg">
                {stats ? formatNumber(stats.conversions) : '0'}
              </div>
              <div className="text-white/90 text-sm font-semibold tracking-wide">Conversions</div>
            </Card>
          </motion.div>
        </div>

        {/* Performance Stats */}
        {stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-12"
          >
            <Card className="bg-white/90 backdrop-blur-lg shadow-2xl border border-gray-100">
              <h2 className="text-3xl font-black text-gray-900 mb-8 flex items-center gap-3">
                <div className="bg-gradient-to-br from-orange-500 to-red-500 p-3 rounded-xl">
                  <BarChart3 className="text-white" size={28} />
                </div>
                Performance en temps réel
              </h2>
              <div className="grid grid-cols-3 gap-8">
                <motion.div 
                  className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border-2 border-blue-100 hover:border-blue-300 transition-all duration-300"
                  whileHover={{ y: -4, scale: 1.02 }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-blue-500 p-3 rounded-xl">
                      <Eye className="text-white" size={24} />
                    </div>
                    <span className="text-sm font-bold text-gray-600 uppercase tracking-wider">Vues</span>
                  </div>
                  <div className="text-4xl font-black text-gray-900 mb-2">
                    {formatNumber(stats.views || 0)}
                  </div>
                  <div className="flex items-center gap-2 text-sm min-h-[20px]">
                    {stats.views > 0 ? (
                      <>
                        <span className="text-gray-400 font-medium">—</span>
                        <span className="text-gray-400">Données insuffisantes</span>
                      </>
                    ) : (
                      <span className="text-gray-400">Aucune donnée</span>
                    )}
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border-2 border-purple-100 hover:border-purple-300 transition-all duration-300"
                  whileHover={{ y: -4, scale: 1.02 }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-purple-500 p-3 rounded-xl">
                      <Target className="text-white" size={24} />
                    </div>
                    <span className="text-sm font-bold text-gray-600 uppercase tracking-wider">CTR</span>
                  </div>
                  <div className="text-4xl font-black text-gray-900 mb-2">
                    {stats.ctr || 0}%
                  </div>
                  <div className="flex items-center gap-2 text-sm min-h-[20px]">
                    {stats.ctr > 0 ? (
                      <>
                        <span className="text-gray-400 font-medium">—</span>
                        <span className="text-gray-400">Données insuffisantes</span>
                      </>
                    ) : (
                      <span className="text-gray-400">Aucune donnée</span>
                    )}
                  </div>
                </motion.div>

                <motion.div 
                  className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 border-2 border-green-100 hover:border-green-300 transition-all duration-300"
                  whileHover={{ y: -4, scale: 1.02 }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-green-500 p-3 rounded-xl">
                      <TrendingUp className="text-white" size={24} />
                    </div>
                    <span className="text-sm font-bold text-gray-600 uppercase tracking-wider">Taux de conversion</span>
                  </div>
                  <div className="text-4xl font-black text-gray-900 mb-2">
                    {stats.conversionRate || 0}%
                  </div>
                  <div className="flex items-center gap-2 text-sm min-h-[20px]">
                    {stats.conversionRate > 0 ? (
                      <>
                        <span className="text-gray-400 font-medium">—</span>
                        <span className="text-gray-400">Données insuffisantes</span>
                      </>
                    ) : (
                      <span className="text-gray-400">Aucune donnée</span>
                    )}
                  </div>
                </motion.div>
              </div>
            </Card>
          </motion.div>
        )}

        <div className="grid grid-cols-3 gap-10">
          {/* Informations générales */}
          <div className="col-span-2 space-y-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Card className="bg-white/90 backdrop-blur-lg shadow-2xl border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                  <FileText className="text-orange-600" size={28} />
                  Informations
                </h2>
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center gap-3 mb-2">
                        <Calendar className="text-gray-600" size={20} />
                        <span className="text-sm font-semibold text-gray-600">Date de début</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatDate(campaign.start_date)}
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                      <div className="flex items-center gap-3 mb-2">
                        <Calendar className="text-gray-600" size={20} />
                        <span className="text-sm font-semibold text-gray-600">Date de fin</span>
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatDate(campaign.end_date)}
                      </div>
                    </div>
                  </div>

                  {campaign.requirements && (
                    <div>
                      <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <CheckCircle className="text-orange-600" size={20} />
                        Prérequis
                      </h3>
                      <div className="bg-orange-50 rounded-xl p-4 border border-orange-100">
                        <p className="text-gray-700 leading-relaxed">{campaign.requirements}</p>
                      </div>
                    </div>
                  )}

                  {campaign.description && (
                    <div>
                      <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <MessageSquare className="text-orange-600" size={20} />
                        Description complète
                      </h3>
                      <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                        <p className="text-gray-700 leading-relaxed">{campaign.description}</p>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </motion.div>

            {/* Top Influencers */}
            {influencers.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                <Card className="bg-white/80 backdrop-blur-sm">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                    <Award className="text-orange-600" size={28} />
                    Top Influenceurs
                  </h2>
                  <div className="space-y-4">
                    {influencers.map((influencer, index) => (
                      <motion.div
                        key={influencer.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 + index * 0.1 }}
                        className="bg-gradient-to-r from-gray-50 to-orange-50 rounded-xl p-4 border border-gray-100 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white w-12 h-12 rounded-full flex items-center justify-center font-black text-lg">
                              #{index + 1}
                            </div>
                            <div>
                              <h3 className="font-bold text-gray-900">{influencer.name}</h3>
                              <p className="text-sm text-gray-600 flex items-center gap-2">
                                <Users size={14} />
                                {formatNumber(influencer.followers)} followers
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-black text-gray-900">{influencer.sales}</div>
                            <div className="text-sm text-gray-600">ventes</div>
                            <div className="text-sm font-bold text-green-600 mt-1">
                              {formatCurrency(influencer.commission)}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm sticky top-8">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Clock className="text-orange-600" size={22} />
                  Chronologie
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="bg-green-100 p-2 rounded-lg">
                      <CheckCircle className="text-green-600" size={18} />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 text-sm">Campagne créée</div>
                      <div className="text-xs text-gray-500">
                        {formatDate(campaign.created_at)}
                      </div>
                    </div>
                  </div>
                  
                  {campaign.start_date && (
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <Play className="text-blue-600" size={18} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">Date de début</div>
                        <div className="text-xs text-gray-500">
                          {formatDate(campaign.start_date)}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {campaign.end_date && (
                    <div className="flex items-start gap-3">
                      <div className="bg-red-100 p-2 rounded-lg">
                        <Calendar className="text-red-600" size={18} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">Date de fin</div>
                        <div className="text-xs text-gray-500">
                          {formatDate(campaign.end_date)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <Share2 className="text-orange-600" size={22} />
                    Partager
                  </h3>
                  <div className="space-y-3">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      onClick={() => {
                        navigator.clipboard.writeText(window.location.href);
                        toast.success('Lien copié dans le presse-papiers !');
                      }}
                    >
                      <LinkIcon size={18} className="mr-2" />
                      Copier le lien
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      onClick={() => toast.info('Téléchargement des visuels en cours...')}
                    >
                      <Image size={18} className="mr-2" />
                      Télécharger visuels
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Modal d'édition */}
      <AnimatePresence>
        {editMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setEditMode(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 rounded-t-2xl">
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  <Edit size={28} />
                  Modifier la campagne
                </h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Nom de la campagne</label>
                  <input
                    type="text"
                    value={editData.name || ''}
                    onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                  <textarea
                    value={editData.description || ''}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Budget (€)</label>
                    <input
                      type="number"
                      value={editData.budget || ''}
                      onChange={(e) => setEditData({ ...editData, budget: parseFloat(e.target.value) })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Commission (%)</label>
                    <input
                      type="number"
                      value={editData.commission_rate || ''}
                      onChange={(e) => setEditData({ ...editData, commission_rate: parseFloat(e.target.value) })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Date de début</label>
                    <input
                      type="date"
                      value={editData.start_date || ''}
                      onChange={(e) => setEditData({ ...editData, start_date: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Date de fin</label>
                    <input
                      type="date"
                      value={editData.end_date || ''}
                      onChange={(e) => setEditData({ ...editData, end_date: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 p-6 bg-gray-50 rounded-b-2xl">
                <Button variant="outline" onClick={() => setEditMode(false)}>
                  Annuler
                </Button>
                <Button className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600" onClick={handleSaveEdit}>
                  <CheckCircle size={18} className="mr-2" />
                  Enregistrer
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal de changement de statut */}
      <AnimatePresence>
        {statusModal.isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setStatusModal({ isOpen: false, action: null })}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full"
            >
              <div className={`p-6 rounded-t-2xl ${statusModal.action === 'pause' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' : 'bg-gradient-to-r from-green-500 to-emerald-500'}`}>
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  {statusModal.action === 'pause' ? (
                    <><Pause size={28} /> Mettre en pause</>
                  ) : (
                    <><Play size={28} /> Activer la campagne</>
                  )}
                </h2>
              </div>
              
              <div className="p-6">
                <p className="text-gray-600 mb-4">
                  {statusModal.action === 'pause' 
                    ? 'Êtes-vous sûr de vouloir mettre en pause cette campagne ? Les influenceurs ne pourront plus générer de nouvelles conversions.' 
                    : 'Êtes-vous sûr de vouloir activer cette campagne ? Les influenceurs pourront à nouveau générer des conversions.'}
                </p>
                
                <div className="bg-gray-50 rounded-xl p-4 mb-6">
                  <div className="flex items-center gap-3 mb-2">
                    <Target className="text-gray-600" size={20} />
                    <span className="font-bold text-gray-900">{campaign.name}</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Budget: {formatCurrency(campaign.budget)} • Commission: {campaign.commission_rate}%
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 p-6 bg-gray-50 rounded-b-2xl">
                <Button variant="outline" onClick={() => setStatusModal({ isOpen: false, action: null })}>
                  Annuler
                </Button>
                <Button 
                  className={statusModal.action === 'pause' ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'}
                  onClick={() => handleStatusChange(statusModal.action === 'pause' ? 'paused' : 'active')}
                >
                  {statusModal.action === 'pause' ? (
                    <><Pause size={18} className="mr-2" /> Mettre en pause</>
                  ) : (
                    <><Play size={18} className="mr-2" /> Activer</>
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CampaignDetailPage;
