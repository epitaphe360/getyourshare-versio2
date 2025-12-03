import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Users,
  Eye,
  MousePointer,
  ShoppingCart,
  Percent,
  Calendar,
  Filter,
  Search,
  Download,
  Plus,
  MoreVertical,
  Play,
  Pause,
  Archive,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CampaignDashboard = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [selectedCampaigns, setSelectedCampaigns] = useState([]);
  const { showToast } = useToast();

  // Status badge configurations
  const statusConfig = {
    active: { color: 'success', icon: CheckCircle, label: 'Active', emoji: '🟢' },
    paused: { color: 'warning', icon: Pause, label: 'Suspendue', emoji: '⏸️' },
    completed: { color: 'error', icon: XCircle, label: 'Terminée', emoji: '🔴' },
    draft: { color: 'secondary', icon: Clock, label: 'Brouillon', emoji: '⚪' },
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/campaigns');
      setCampaigns(response.data.data || []);
    } catch (error) {
      showToast('Erreur lors du chargement des campagnes', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Calculer les KPIs
  const kpis = React.useMemo(() => {
    const activeCampaigns = campaigns.filter(c => c.status === 'active');
    const totalOffers = campaigns.length;
    const totalRevenue = campaigns.reduce((sum, c) => sum + (parseFloat(c.total_revenue) || 0), 0);
    const totalClicks = campaigns.reduce((sum, c) => sum + (parseInt(c.total_clicks) || 0), 0);
    const totalConversions = campaigns.reduce((sum, c) => sum + (parseInt(c.total_conversions) || 0), 0);
    const avgConversionRate = totalClicks > 0 ? (totalConversions / totalClicks * 100) : 0;

    // Comparaison avec le mois dernier (simulation)
    const activeGrowth = 12.5;
    const offersGrowth = 7.8;
    const conversionGrowth = 13.2;
    const revenueGrowth = 24.6;

    return {
      activeCampaigns: {
        value: activeCampaigns.length,
        growth: activeGrowth,
        isPositive: true,
        label: 'Campagnes Actives'
      },
      totalOffers: {
        value: totalOffers,
        growth: offersGrowth,
        isPositive: true,
        label: 'Offres Publiées'
      },
      avgConversionRate: {
        value: avgConversionRate.toFixed(1),
        growth: conversionGrowth,
        isPositive: true,
        label: 'Taux de Conversion Moyen'
      },
      totalRevenue: {
        value: totalRevenue,
        growth: revenueGrowth,
        isPositive: true,
        label: 'CA Total Généré'
      }
    };
  }, [campaigns]);

  // Filtrer les campagnes
  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = campaign.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         campaign.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
    const matchesType = typeFilter === 'all' || campaign.campaign_type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  // Données pour les graphiques
  const typeDistribution = React.useMemo(() => {
    const distribution = {};
    campaigns.forEach(c => {
      const type = c.campaign_type || 'Autre';
      distribution[type] = (distribution[type] || 0) + 1;
    });
    return Object.entries(distribution).map(([name, value]) => ({ name, value }));
  }, [campaigns]);

  const top5Campaigns = React.useMemo(() => {
    return [...campaigns]
      .sort((a, b) => (parseFloat(b.total_revenue) || 0) - (parseFloat(a.total_revenue) || 0))
      .slice(0, 5)
      .map((c, index) => ({
        rank: index + 1,
        name: c.name,
        revenue: parseFloat(c.total_revenue) || 0,
        conversions: parseInt(c.total_conversions) || 0
      }));
  }, [campaigns]);

  // Calcul des alertes
  const alerts = React.useMemo(() => {
    const alertList = [];
    campaigns.forEach(campaign => {
      const budget = parseFloat(campaign.budget) || 0;
      const spent = parseFloat(campaign.spent) || 0;
      const budgetUsage = budget > 0 ? (spent / budget) * 100 : 0;

      if (budgetUsage >= 95 && campaign.status === 'active') {
        alertList.push({
          type: 'warning',
          campaign: campaign.name,
          message: `Budget épuisé à ${budgetUsage.toFixed(0)}%`
        });
      }

      // Vérifier les campagnes se terminant bientôt
      if (campaign.end_date && campaign.status === 'active') {
        const endDate = new Date(campaign.end_date);
        const now = new Date();
        const hoursRemaining = (endDate - now) / (1000 * 60 * 60);
        
        if (hoursRemaining > 0 && hoursRemaining < 48) {
          alertList.push({
            type: 'error',
            campaign: campaign.name,
            message: `Fin dans ${Math.round(hoursRemaining)}h`
          });
        }
      }
    });
    return alertList.slice(0, 5);
  }, [campaigns]);

  const handleStatusChange = async (campaignId, newStatus) => {
    try {
      await api.put(`/api/campaigns/${campaignId}/status`, { status: newStatus });
      showToast('Statut mis à jour avec succès', 'success');
      fetchCampaigns();
    } catch (error) {
      showToast('Erreur lors de la mise à jour du statut', 'error');
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const getDaysRemaining = (endDate) => {
    if (!endDate) return null;
    const end = new Date(endDate);
    const now = new Date();
    const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };

  const KPICard = ({ icon: Icon, label, value, suffix = '', growth, isPositive }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {typeof value === 'number' && suffix === '€' ? formatCurrency(value) : value}
                {suffix && suffix !== '€' && <span className="text-lg ml-1">{suffix}</span>}
              </p>
            </div>
            <div className={`mt-2 flex items-center text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              <span className="font-medium">+{growth}%</span>
              <span className="ml-1 text-gray-500">vs mois dernier</span>
            </div>
          </div>
          <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              📊 Tableau de Bord Campagnes
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Gérez et analysez toutes vos campagnes marketing
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => {}}>
              <Download className="w-4 h-4 mr-2" />
              Exporter
            </Button>
            <Button onClick={() => window.location.href = '/campaigns/create'}>
              <Plus className="w-4 h-4 mr-2" />
              Nouvelle Campagne
            </Button>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          icon={Target}
          label={kpis.activeCampaigns.label}
          value={kpis.activeCampaigns.value}
          growth={kpis.activeCampaigns.growth}
          isPositive={kpis.activeCampaigns.isPositive}
        />
        <KPICard
          icon={Eye}
          label={kpis.totalOffers.label}
          value={kpis.totalOffers.value}
          growth={kpis.totalOffers.growth}
          isPositive={kpis.totalOffers.isPositive}
        />
        <KPICard
          icon={Percent}
          label={kpis.avgConversionRate.label}
          value={kpis.avgConversionRate.value}
          suffix="%"
          growth={kpis.avgConversionRate.growth}
          isPositive={kpis.avgConversionRate.isPositive}
        />
        <KPICard
          icon={DollarSign}
          label={kpis.totalRevenue.label}
          value={kpis.totalRevenue.value}
          suffix="€"
          growth={kpis.totalRevenue.growth}
          isPositive={kpis.totalRevenue.isPositive}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Filtres et Recherche */}
          <Card className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher une campagne..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                >
                  <option value="all">Tous les statuts</option>
                  <option value="active">Active</option>
                  <option value="paused">Suspendue</option>
                  <option value="completed">Terminée</option>
                  <option value="draft">Brouillon</option>
                </select>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                >
                  <option value="all">Tous les types</option>
                  <option value="Soldes">Soldes</option>
                  <option value="Lancement Produit">Lancement</option>
                  <option value="Saisonnière">Saisonnière</option>
                  <option value="Flash">Flash</option>
                  <option value="Event Spécial">Event</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Tableau des Campagnes */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Campagne
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Dates
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Budget
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Commission
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Performance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ROI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredCampaigns.map((campaign, index) => {
                    const config = statusConfig[campaign.status] || statusConfig.draft;
                    const StatusIcon = config.icon;
                    const daysRemaining = getDaysRemaining(campaign.end_date);
                    const roi = parseFloat(campaign.roi) || 0;
                    const budget = parseFloat(campaign.budget) || 0;
                    const spent = parseFloat(campaign.spent) || 0;
                    const budgetUsage = budget > 0 ? (spent / budget) * 100 : 0;

                    return (
                      <motion.tr
                        key={campaign.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.05 }}
                        className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={config.color} className="flex items-center gap-1">
                            <StatusIcon className="w-3 h-3" />
                            {config.label}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {campaign.name}
                            </div>
                            <div className="text-xs text-gray-500">
                              {campaign.category} • {campaign.participants || 0} participants
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900 dark:text-white">
                            {campaign.campaign_type || 'Générale'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm">
                            <div className="text-gray-900 dark:text-white">
                              {formatDate(campaign.start_date)} →
                            </div>
                            <div className="text-gray-900 dark:text-white">
                              {formatDate(campaign.end_date)}
                            </div>
                            {daysRemaining !== null && daysRemaining > 0 && (
                              <div className="text-xs text-blue-600 dark:text-blue-400">
                                {daysRemaining}j restants
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm">
                            <div className="text-gray-900 dark:text-white font-medium">
                              {formatCurrency(budget)}
                            </div>
                            <div className="text-xs text-gray-500">
                              {formatCurrency(spent)} dépensés
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                              <div
                                className={`h-1.5 rounded-full ${budgetUsage > 90 ? 'bg-red-500' : budgetUsage > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                style={{ width: `${Math.min(budgetUsage, 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {campaign.commission_rate || 15}%
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                              <MousePointer className="w-3 h-3" />
                              <span>{(campaign.total_clicks || 0).toLocaleString()} clics</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                              <ShoppingCart className="w-3 h-3" />
                              <span>{(campaign.total_conversions || 0).toLocaleString()} ventes</span>
                            </div>
                            <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                              {formatCurrency(campaign.total_revenue || 0)} CA
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`text-sm font-bold ${roi >= 200 ? 'text-green-600' : roi >= 100 ? 'text-blue-600' : roi > 0 ? 'text-yellow-600' : 'text-gray-500'}`}>
                            {roi.toFixed(0)}%
                            {roi >= 200 && ' ✅'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {roi >= 200 ? 'Excellent' : roi >= 100 ? 'Bon' : roi > 0 ? 'Moyen' : 'Faible'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex gap-2">
                            <button
                              onClick={() => window.location.href = `/campaigns/${campaign.id}`}
                              className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                              title="Voir"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            {campaign.status === 'active' && (
                              <button
                                onClick={() => handleStatusChange(campaign.id, 'paused')}
                                className="text-yellow-600 hover:text-yellow-800 dark:text-yellow-400"
                                title="Suspendre"
                              >
                                <Pause className="w-4 h-4" />
                              </button>
                            )}
                            {campaign.status === 'paused' && (
                              <button
                                onClick={() => handleStatusChange(campaign.id, 'active')}
                                className="text-green-600 hover:text-green-800 dark:text-green-400"
                                title="Reprendre"
                              >
                                <Play className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Graphiques */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Répartition par Type
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name} (${entry.value})`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Top 5 Campagnes Performantes
              </h3>
              <div className="space-y-3">
                {top5Campaigns.map((campaign, index) => {
                  const medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];
                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{medals[index]}</span>
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {campaign.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {campaign.conversions} conversions
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-green-600 dark:text-green-400">
                          {formatCurrency(campaign.revenue)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>

        {/* Sidebar Alertes */}
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-orange-500" />
              🚨 Alertes & Notifications
            </h3>
            <div className="space-y-3">
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                  <p>Aucune alerte pour le moment</p>
                </div>
              ) : (
                alerts.map((alert, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-4 rounded-lg border-l-4 ${
                      alert.type === 'error'
                        ? 'bg-red-50 dark:bg-red-900/20 border-red-500'
                        : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 ${alert.type === 'error' ? 'text-red-600' : 'text-yellow-600'}`}>
                        {alert.type === 'error' ? '🔴' : '⚠️'}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {alert.campaign}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {alert.message}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              ⚡ Actions Rapides
            </h3>
            <div className="space-y-2">
              <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                <Plus className="w-4 h-4 mr-2" />
                Créer une Campagne
              </Button>
              <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                <Download className="w-4 h-4 mr-2" />
                Rapport Mensuel
              </Button>
              <Button variant="outline" className="w-full justify-start" onClick={() => {}}>
                <Calendar className="w-4 h-4 mr-2" />
                Programmer Analyse
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CampaignDashboard;
