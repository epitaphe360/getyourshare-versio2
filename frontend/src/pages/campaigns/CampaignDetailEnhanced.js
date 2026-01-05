import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, Target, DollarSign, Calendar, Users, TrendingUp, 
  Eye, MousePointer, ShoppingCart, Percent, Clock, CheckCircle,
  AlertCircle, Edit, Pause, Play, Archive, BarChart3, Package,
  MessageSquare, FileText, Image, Link as LinkIcon, History,
  Activity, Award, Zap, TrendingDown
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const CampaignDetailEnhanced = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [influencers, setInfluencers] = useState([]);

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: Eye },
    { id: 'products', label: 'Produits/Offres', icon: Package },
    { id: 'influencers', label: 'Influenceurs', icon: Users },
    { id: 'analytics', label: 'Analyse Performance', icon: BarChart3 },
    { id: 'history', label: 'Historique', icon: History },
  ];

  useEffect(() => {
    fetchCampaignDetails();
  }, [id]);

  const fetchCampaignDetails = async () => {
    try {
      setLoading(true);
      
      // Récupérer les détails de la campagne
      const campaignResponse = await api.get(`/api/campaigns/${id}`);
      setCampaign(campaignResponse.data);
      
      // Récupérer les statistiques
      try {
        const statsResponse = await api.get(`/api/campaigns/${id}/stats`);
        setStats(statsResponse.data);
      } catch (e) {
        console.error('Error loading stats:', e);
      }
      
      // Récupérer les influenceurs
      try {
        const influencersResponse = await api.get(`/api/campaigns/${id}/influencers`);
        setInfluencers(influencersResponse.data || []);
      } catch (e) {
        console.error('Error loading influencers:', e);
      }
      
    } catch (error) {
      showToast('Erreur lors du chargement de la campagne', 'error');
      navigate('/campaigns');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', { 
      style: 'currency', 
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
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

  const getDaysRemaining = (endDate) => {
    if (!endDate) return null;
    const end = new Date(endDate);
    const now = new Date();
    const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await api.put(`/api/campaigns/${id}/status`, { status: newStatus });
      showToast('Statut mis à jour avec succès', 'success');
      fetchCampaignDetails();
    } catch (error) {
      showToast('Erreur lors de la mise à jour du statut', 'error');
    }
  };

  // Données fictives pour les graphiques de performance
  const performanceData = [
    { date: '01/11', clicks: 120, conversions: 8, revenue: 450 },
    { date: '05/11', clicks: 180, conversions: 12, revenue: 680 },
    { date: '10/11', clicks: 250, conversions: 18, revenue: 980 },
    { date: '15/11', clicks: 320, conversions: 25, revenue: 1350 },
    { date: '20/11', clicks: 420, conversions: 32, revenue: 1720 },
    { date: '25/11', clicks: 580, conversions: 45, revenue: 2350 },
    { date: '30/11', clicks: 720, conversions: 58, revenue: 3120 },
  ];

  const trafficSources = [
    { source: 'Instagram', clicks: 2500, conversions: 180, percentage: 45 },
    { source: 'TikTok', clicks: 1800, conversions: 120, percentage: 32 },
    { source: 'YouTube', clicks: 800, conversions: 65, percentage: 14 },
    { source: 'Facebook', clicks: 450, conversions: 28, percentage: 8 },
    { source: 'Autre', clicks: 50, conversions: 5, percentage: 1 },
  ];

  const historyEvents = [
    { date: '2024-12-01 14:30', user: 'Admin', action: 'Modification du budget', details: 'Budget porté à 5000€' },
    { date: '2024-11-28 10:15', user: 'System', action: 'Pause automatique', details: 'Seuil de budget atteint' },
    { date: '2024-11-25 16:45', user: 'Admin', action: 'Reprise de la campagne', details: 'Campagne réactivée' },
    { date: '2024-11-20 09:00', user: 'Admin', action: 'Création de la campagne', details: 'Campagne initialisée' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Campagne non trouvée</h2>
          <Button onClick={() => navigate('/campaigns')} className="mt-4">
            Retour aux campagnes
          </Button>
        </div>
      </div>
    );
  }

  // Extraire les métadonnées
  const metadata = campaign.target_audience?.metadata || {};
  const performance = metadata.performance || {};
  const campaignType = metadata.campaign_type || metadata.type || 'Générale';
  const category = metadata.category || 'Général';
  const commissionRate = metadata.commission_rate || campaign.commission_rate || 15;
  const participants = performance.participants || 0;
  const clicks = performance.clicks || 0;
  const conversions = performance.conversions || 0;
  const revenue = performance.revenue || 0;
  const roi = performance.roi || 0;
  const spent = metadata.spent || 0;
  const budget = parseFloat(campaign.budget) || 0;
  const budgetUsage = budget > 0 ? (spent / budget) * 100 : 0;

  const statusConfig = {
    active: { color: 'success', icon: CheckCircle, label: 'Active', emoji: '🟢' },
    paused: { color: 'warning', icon: Pause, label: 'Suspendue', emoji: '⏸️' },
    completed: { color: 'error', icon: Clock, label: 'Terminée', emoji: '🔴' },
    draft: { color: 'secondary', icon: Clock, label: 'Brouillon', emoji: '⚪' },
  };

  const config = statusConfig[campaign.status] || statusConfig.draft;
  const StatusIcon = config.icon;
  const daysRemaining = getDaysRemaining(campaign.end_date);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/campaigns')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Retour aux campagnes
        </Button>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {campaign.name}
              </h1>
              <Badge variant={config.color} className="flex items-center gap-1">
                <StatusIcon className="w-3 h-3" />
                {config.label}
              </Badge>
            </div>
            <p className="text-gray-600 dark:text-gray-400 max-w-3xl">
              {campaign.description}
            </p>
            <div className="flex items-center gap-4 mt-3 text-sm text-gray-600 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Target className="w-4 h-4" />
                {campaignType}
              </span>
              <span className="flex items-center gap-1">
                <Package className="w-4 h-4" />
                {category}
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {formatDate(campaign.start_date)} → {formatDate(campaign.end_date)}
              </span>
              {daysRemaining !== null && daysRemaining > 0 && (
                <span className="flex items-center gap-1 text-blue-600 dark:text-blue-400 font-medium">
                  <Clock className="w-4 h-4" />
                  {daysRemaining}j restants
                </span>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate(`/campaigns/${id}/edit`)}>
              <Edit className="w-4 h-4 mr-2" />
              Modifier
            </Button>
            {campaign.status === 'active' && (
              <Button variant="warning" onClick={() => handleStatusChange('paused')}>
                <Pause className="w-4 h-4 mr-2" />
                Suspendre
              </Button>
            )}
            {campaign.status === 'paused' && (
              <Button variant="success" onClick={() => handleStatusChange('active')}>
                <Play className="w-4 h-4 mr-2" />
                Reprendre
              </Button>
            )}
            <Button variant="outline">
              <Archive className="w-4 h-4 mr-2" />
              Archiver
            </Button>
          </div>
        </div>
      </div>

      {/* KPIs rapides */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Budget</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(budget)}
              </p>
              <div className="text-xs text-gray-500 mt-1">
                {formatCurrency(spent)} dépensés ({budgetUsage.toFixed(0)}%)
              </div>
            </div>
            <DollarSign className="w-8 h-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Clics</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatNumber(clicks)}
              </p>
              <div className="text-xs text-green-600 dark:text-green-400 mt-1">
                +15.2% vs hier
              </div>
            </div>
            <MousePointer className="w-8 h-8 text-purple-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Conversions</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatNumber(conversions)}
              </p>
              <div className="text-xs text-gray-500 mt-1">
                Taux: {clicks > 0 ? ((conversions / clicks) * 100).toFixed(1) : 0}%
              </div>
            </div>
            <ShoppingCart className="w-8 h-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">CA Généré</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(revenue)}
              </p>
              <div className="text-xs text-green-600 dark:text-green-400 mt-1">
                +24.6% vs semaine
              </div>
            </div>
            <TrendingUp className="w-8 h-8 text-emerald-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">ROI</p>
              <p className={`text-2xl font-bold ${roi >= 200 ? 'text-green-600' : roi >= 100 ? 'text-blue-600' : 'text-yellow-600'}`}>
                {roi.toFixed(0)}%
              </p>
              <div className="text-xs text-gray-500 mt-1">
                {roi >= 200 ? 'Excellent ✅' : roi >= 100 ? 'Bon' : 'Moyen'}
              </div>
            </div>
            <Percent className="w-8 h-8 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Onglets */}
      <Card className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex space-x-1 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="p-6">
          <AnimatePresence mode="wait">
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                      📋 Informations Générales
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <span className="text-gray-600 dark:text-gray-400">Type de campagne</span>
                        <span className="font-medium text-gray-900 dark:text-white">{campaignType}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <span className="text-gray-600 dark:text-gray-400">Catégorie</span>
                        <span className="font-medium text-gray-900 dark:text-white">{category}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <span className="text-gray-600 dark:text-gray-400">Commission</span>
                        <span className="font-medium text-blue-600 dark:text-blue-400">{commissionRate}%</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <span className="text-gray-600 dark:text-gray-400">Participants</span>
                        <span className="font-medium text-gray-900 dark:text-white">{participants} influenceurs</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <span className="text-gray-600 dark:text-gray-400">Objectif</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {conversions > 0 ? `${conversions} ventes` : 'En cours'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                      🎯 Objectifs & KPIs
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-600 dark:text-gray-400">Budget utilisé</span>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {budgetUsage.toFixed(0)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              budgetUsage > 90 ? 'bg-red-500' : budgetUsage > 70 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(budgetUsage, 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-600 dark:text-gray-400">Taux de conversion</span>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {clicks > 0 ? ((conversions / clicks) * 100).toFixed(1) : 0}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-blue-500 transition-all"
                            style={{ width: `${Math.min((conversions / clicks) * 100, 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300 mb-2">
                          <Award className="w-5 h-5" />
                          <span className="font-semibold">Performance Globale</span>
                        </div>
                        <p className="text-sm text-blue-600 dark:text-blue-400">
                          {roi >= 200
                            ? '🎉 Excellente performance! Cette campagne dépasse tous les objectifs.'
                            : roi >= 100
                            ? '✅ Bonne performance. Continuez sur cette lancée.'
                            : roi > 0
                            ? '📊 Performance moyenne. Des optimisations sont possibles.'
                            : '⚠️ Performance faible. Analyse recommandée.'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'products' && (
              <motion.div
                key="products"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  📦 Produits & Offres Inclus
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3, 4, 5, 6].map((item) => (
                    <Card key={item} className="p-4 hover:shadow-lg transition-shadow">
                      <div className="flex gap-3">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <Package className="w-8 h-8 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            Produit {item}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Prix: {formatCurrency(Math.random() * 100 + 20)}
                          </p>
                          <p className="text-xs text-green-600 dark:text-green-400">
                            -{(10 + Math.random() * 20).toFixed(0)}% promo
                          </p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'influencers' && (
              <motion.div
                key="influencers"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  👥 Influenceurs Participants ({participants})
                </h3>
                <div className="space-y-3">
                  {influencers.length > 0 ? (
                    influencers.map((influencer, index) => (
                      <Card key={index} className="p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                              {influencer.name?.charAt(0) || 'I'}
                            </div>
                            <div>
                              <div className="font-semibold text-gray-900 dark:text-white">
                                {influencer.name || `Influenceur ${index + 1}`}
                              </div>
                              <div className="text-sm text-gray-600 dark:text-gray-400">
                                {formatNumber(influencer.clicks || 0)} clics • {formatNumber(influencer.conversions || 0)} conversions
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                              {formatCurrency(influencer.revenue || 0)}
                            </div>
                            <div className="text-xs text-gray-500">
                              Commission: {formatCurrency(influencer.commission || 0)}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))
                  ) : (
                    <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                      <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>Aucun influenceur participant pour le moment</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {activeTab === 'analytics' && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-6"
              >
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                    📈 Évolution des Performances (30 derniers jours)
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Area yAxisId="left" type="monotone" dataKey="clicks" stroke="#3b82f6" fill="#93c5fd" name="Clics" />
                      <Area yAxisId="left" type="monotone" dataKey="conversions" stroke="#10b981" fill="#86efac" name="Conversions" />
                      <Area yAxisId="right" type="monotone" dataKey="revenue" stroke="#f59e0b" fill="#fcd34d" name="Revenue (€)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                    🌐 Sources de Trafic
                  </h3>
                  <div className="space-y-3">
                    {trafficSources.map((source, index) => (
                      <div key={index} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900 dark:text-white">{source.source}</span>
                          <span className="text-sm text-gray-600 dark:text-gray-400">{source.percentage}%</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
                                style={{ width: `${source.percentage}%` }}
                              ></div>
                            </div>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {formatNumber(source.clicks)} clics • {formatNumber(source.conversions)} conv.
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'history' && (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  📜 Historique des Événements
                </h3>
                <div className="space-y-3">
                  {historyEvents.map((event, index) => (
                    <div key={index} className="flex gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                          <History className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold text-gray-900 dark:text-white">
                              {event.action}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {event.details}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500">
                            {event.user}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {event.date}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </div>
  );
};

export default CampaignDetailEnhanced;
