import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import { motion, AnimatePresence } from 'framer-motion';
import CountUp from 'react-countup';
import {
  TrendingUp, Users, DollarSign, ShoppingBag, Sparkles, BarChart3, Target, Eye,
  Settings, FileText, Bell, Download, RefreshCw, Briefcase, Edit, Trash2, Lock,
  Unlock, Mail, Plus, Search, Filter, X, Check, AlertCircle, Clock, CheckCircle,
  XCircle, Award, Zap, Crown, Activity, ShoppingCart, Package, Link as LinkIcon,
  Calendar, TrendingDown, ArrowUpRight, ArrowDownRight, MoreVertical, ExternalLink
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];

const AdminDashboardComplete = () => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, users, finance, analytics
  const [stats, setStats] = useState(null);
  const [merchants, setMerchants] = useState([]);
  const [influencers, setInfluencers] = useState([]);
  const [commercials, setCommercials] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);

  // Filtres et recherche
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('30days');

  // Modales
  const [showUserDetailModal, setShowUserDetailModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, [dateFilter]);

  // ========== FETCH DATA ==========
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [
        statsRes,
        merchantsRes,
        influencersRes,
        commercialsRes,
        activityRes,
        revenueRes,
        growthRes,
        categoriesRes
      ] = await Promise.allSettled([
        api.get('/api/analytics/overview'),
        api.get('/api/merchants'),
        api.get('/api/influencers'),
        api.get('/api/commercials'),
        api.get('/api/activity/recent'),
        api.get(`/api/analytics/revenue-chart?period=${dateFilter}`),
        api.get(`/api/analytics/user-growth?period=${dateFilter}`),
        api.get('/api/analytics/categories')
      ]);

      // Traiter les statistiques
      if (statsRes.status === 'fulfilled') {
        const overview = statsRes.value.data;
        setStats({
          total_revenue: overview.financial?.total_revenue || 0,
          total_merchants: overview.users?.total_merchants || 0,
          total_influencers: overview.users?.total_influencers || 0,
          total_commercials: overview.users?.total_commercials || 0,
          total_products: overview.catalog?.total_products || 0,
          total_services: overview.catalog?.total_services || 0,
          total_campaigns: overview.catalog?.total_campaigns || 0,
          total_clicks: overview.tracking?.total_clicks || 0,
          total_conversions: overview.tracking?.total_conversions || 0,
          conversion_rate: overview.tracking?.conversion_rate || 0,
          active_users_24h: overview.users?.active_users_24h || 0,
          pending_payouts: overview.financial?.pending_payouts || 0,
          platform_commission: overview.financial?.platform_commission || 0,
          revenue_growth: overview.financial?.revenue_growth || 0,
          user_growth: overview.users?.user_growth || 0
        });
      }

      // Traiter les utilisateurs
      if (merchantsRes.status === 'fulfilled') {
        setMerchants(merchantsRes.value.data.merchants || []);
      }
      if (influencersRes.status === 'fulfilled') {
        setInfluencers(influencersRes.value.data.influencers || []);
      }
      if (commercialsRes.status === 'fulfilled') {
        setCommercials(commercialsRes.value.data.commercials || []);
      }

      // Traiter l'activité récente
      if (activityRes.status === 'fulfilled') {
        setRecentActivity(activityRes.value.data || []);
      }

      // Traiter les graphiques
      if (revenueRes.status === 'fulfilled') {
        setRevenueData(revenueRes.value.data || []);
      }
      if (growthRes.status === 'fulfilled') {
        setUserGrowthData(growthRes.value.data || []);
      }
      if (categoriesRes.status === 'fulfilled') {
        setCategoryData(categoriesRes.value.data || []);
      }

    } catch (error) {
      console.error('Erreur lors du chargement du dashboard:', error);
      toast.error('Impossible de charger les données du dashboard');
    } finally {
      setLoading(false);
    }
  };

  // ========== ACTIONS DE GESTION ==========
  const handleToggleUserStatus = async (user) => {
    try {
      const newStatus = !user.is_active;
      await api.patch(`/api/users/${user.id}/status`, { is_active: newStatus });
      toast.success(`Utilisateur ${newStatus ? 'activé' : 'suspendu'} avec succès`);
      fetchDashboardData();
    } catch (error) {
      toast.error('Impossible de modifier le statut');
    }
  };

  const handleDeleteUser = async (user) => {
    try {
      await api.delete(`/api/users/${user.id}`);
      toast.success('Utilisateur supprimé avec succès');
      setShowDeleteModal(false);
      fetchDashboardData();
    } catch (error) {
      toast.error('Impossible de supprimer l\'utilisateur');
    }
  };

  const handleAdjustBalance = async (userId, amount, reason) => {
    try {
      await api.post(`/api/users/${userId}/adjust-balance`, { amount, reason });
      toast.success('Solde ajusté avec succès');
      fetchDashboardData();
    } catch (error) {
      toast.error('Impossible d\'ajuster le solde');
    }
  };

  const exportToCSV = (data, filename) => {
    const csv = data.map(row => Object.values(row).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // ========== CALCULS ET FILTRES ==========
  const filteredMerchants = merchants.filter(m => {
    const matchesSearch = !searchTerm || 
      m.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && m.is_active) ||
      (statusFilter === 'inactive' && !m.is_active);
    return matchesSearch && matchesStatus;
  });

  const filteredInfluencers = influencers.filter(i => {
    const matchesSearch = !searchTerm || 
      i.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && i.is_active) ||
      (statusFilter === 'inactive' && !i.is_active);
    return matchesSearch && matchesStatus;
  });

  // ========== RENDER ==========
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Crown className="text-yellow-500" size={32} />
              Tableau de Bord Administrateur
            </h1>
            <p className="text-gray-600 mt-2">
              Gestion complète de la plateforme ShareYourSales
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="7days">7 derniers jours</option>
              <option value="30days">30 derniers jours</option>
              <option value="90days">90 derniers jours</option>
              <option value="1year">1 an</option>
            </select>
            <button
              onClick={fetchDashboardData}
              className="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RefreshCw size={20} />
            </button>
            <button
              onClick={() => exportToCSV(merchants, 'merchants')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <Download size={20} />
              Exporter
            </button>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="flex gap-2 mt-6 border-b border-gray-200">
          {[
            { id: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
            { id: 'users', label: 'Gestion Utilisateurs', icon: Users },
            { id: 'finance', label: 'Finances', icon: DollarSign },
            { id: 'analytics', label: 'Analytiques', icon: TrendingUp }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 flex items-center gap-2 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-600 text-indigo-600 font-semibold'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon size={20} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ========== TAB: VUE D'ENSEMBLE ========== */}
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <KPICard
              title="Revenu Total"
              value={stats?.total_revenue || 0}
              isCurrency={true}
              icon={<DollarSign className="text-green-600" size={24} />}
              trend={stats?.revenue_growth || 0}
              trendLabel="vs mois dernier"
            />
            <KPICard
              title="Utilisateurs Actifs"
              value={stats?.active_users_24h || 0}
              icon={<Users className="text-blue-600" size={24} />}
              trend={stats?.user_growth || 0}
              trendLabel="vs mois dernier"
            />
            <KPICard
              title="Taux de Conversion"
              value={`${stats?.conversion_rate || 0}%`}
              icon={<Target className="text-purple-600" size={24} />}
              trend={2.5}
              trendLabel="vs période précédente"
            />
            <KPICard
              title="Commission Plateforme"
              value={stats?.platform_commission || 0}
              isCurrency={true}
              icon={<Sparkles className="text-yellow-600" size={24} />}
              trend={8.3}
              trendLabel="vs mois dernier"
            />
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            <StatBox
              title="Entreprises"
              value={stats?.total_merchants || 0}
              icon={<ShoppingBag className="text-indigo-600" />}
              onClick={() => navigate('/admin/merchants')}
            />
            <StatBox
              title="Influenceurs"
              value={stats?.total_influencers || 0}
              icon={<Users className="text-pink-600" />}
              onClick={() => setActiveTab('users')}
            />
            <StatBox
              title="Commerciaux"
              value={stats?.total_commercials || 0}
              icon={<Briefcase className="text-blue-600" />}
              onClick={() => setActiveTab('users')}
            />
            <StatBox
              title="Produits"
              value={stats?.total_products || 0}
              icon={<Package className="text-green-600" />}
              onClick={() => navigate('/products')}
            />
            <StatBox
              title="Services"
              value={stats?.total_services || 0}
              icon={<Sparkles className="text-purple-600" />}
              onClick={() => navigate('/services')}
            />
            <StatBox
              title="Campagnes"
              value={stats?.total_campaigns || 0}
              icon={<Target className="text-orange-600" />}
              onClick={() => navigate('/campaigns')}
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp size={20} className="text-green-600" />
                Évolution du Revenu
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={revenueData}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="revenue" stroke="#10b981" fillOpacity={1} fill="url(#colorRevenue)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* User Growth Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Users size={20} className="text-blue-600" />
                Croissance Utilisateurs
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={userGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="merchants" stroke="#8b5cf6" name="Annonceurs" />
                  <Line type="monotone" dataKey="influencers" stroke="#ec4899" name="Influenceurs" />
                  <Line type="monotone" dataKey="commercials" stroke="#3b82f6" name="Commerciaux" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Activity size={20} className="text-gray-600" />
              Activité Récente
            </h3>
            <div className="space-y-3">
              {recentActivity.slice(0, 10).map((activity, index) => (
                <ActivityItem key={index} activity={activity} />
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* ========== TAB: GESTION UTILISATEURS ========== */}
      {activeTab === 'users' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Filters Bar */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex-1 min-w-[300px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Rechercher par nom, email, entreprise..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
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
              <button
                onClick={() => navigate('/admin/users/new')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
              >
                <Plus size={20} />
                Nouvel Utilisateur
              </button>
            </div>
          </div>

          {/* Users Tables */}
          <div className="space-y-6">
            {/* Annonceurs */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <ShoppingBag size={20} className="text-indigo-600" />
                    Annonceurs ({filteredMerchants.length})
                  </h3>
                  <button
                    onClick={() => exportToCSV(filteredMerchants, 'annonceurs')}
                    className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                  >
                    <Download size={16} />
                    Exporter
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entreprise</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Solde</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campagnes</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredMerchants.map((merchant) => (
                      <tr key={merchant.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                              <ShoppingBag size={20} className="text-indigo-600" />
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{merchant.company_name || 'Sans nom'}</div>
                              <div className="text-sm text-gray-500">{merchant.contact_name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{merchant.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {(merchant.balance || 0).toLocaleString()} €
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {merchant.campaigns_count || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            merchant.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {merchant.is_active ? 'Actif' : 'Suspendu'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                setSelectedUser(merchant);
                                setShowUserDetailModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-700"
                              title="Voir détails"
                            >
                              <Eye size={18} />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedUser(merchant);
                                setShowEditModal(true);
                              }}
                              className="text-indigo-600 hover:text-indigo-700"
                              title="Modifier"
                            >
                              <Edit size={18} />
                            </button>
                            <button
                              onClick={() => handleToggleUserStatus(merchant)}
                              className={merchant.is_active ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'}
                              title={merchant.is_active ? 'Suspendre' : 'Activer'}
                            >
                              {merchant.is_active ? <Lock size={18} /> : <Unlock size={18} />}
                            </button>
                            <button
                              onClick={() => window.location.href = `mailto:${merchant.email}`}
                              className="text-gray-600 hover:text-gray-700"
                              title="Envoyer email"
                            >
                              <Mail size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Influenceurs */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <Users size={20} className="text-pink-600" />
                    Influenceurs ({filteredInfluencers.length})
                  </h3>
                  <button
                    onClick={() => exportToCSV(filteredInfluencers, 'influenceurs')}
                    className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                  >
                    <Download size={16} />
                    Exporter
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Influenceur</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gains</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredInfluencers.map((influencer) => (
                      <tr key={influencer.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-pink-100 flex items-center justify-center">
                              <Users size={20} className="text-pink-600" />
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{influencer.full_name || 'Sans nom'}</div>
                              <div className="text-sm text-gray-500">@{influencer.username || 'username'}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{influencer.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                          {(influencer.total_earnings || 0).toLocaleString()} €
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {influencer.total_conversions || 0}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            influencer.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {influencer.is_active ? 'Actif' : 'Suspendu'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                setSelectedUser(influencer);
                                setShowUserDetailModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-700"
                              title="Voir détails"
                            >
                              <Eye size={18} />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedUser(influencer);
                                setShowEditModal(true);
                              }}
                              className="text-indigo-600 hover:text-indigo-700"
                              title="Modifier"
                            >
                              <Edit size={18} />
                            </button>
                            <button
                              onClick={() => handleToggleUserStatus(influencer)}
                              className={influencer.is_active ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'}
                              title={influencer.is_active ? 'Suspendre' : 'Activer'}
                            >
                              {influencer.is_active ? <Lock size={18} /> : <Unlock size={18} />}
                            </button>
                            <button
                              onClick={() => window.location.href = `mailto:${influencer.email}`}
                              className="text-gray-600 hover:text-gray-700"
                              title="Envoyer email"
                            >
                              <Mail size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ========== TAB: FINANCES ========== */}
      {activeTab === 'finance' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Revenu Total</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    <CountUp end={stats?.total_revenue || 0} duration={2} separator=" " suffix=" €" />
                  </p>
                </div>
                <DollarSign className="text-green-600" size={40} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Commission Plateforme</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    <CountUp end={stats?.platform_commission || 0} duration={2} separator=" " suffix=" €" />
                  </p>
                </div>
                <Sparkles className="text-yellow-600" size={40} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Paiements en Attente</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    <CountUp end={stats?.pending_payouts || 0} duration={2} separator=" " suffix=" €" />
                  </p>
                </div>
                <Clock className="text-orange-600" size={40} />
              </div>
            </div>
          </div>

          {/* Tableau des transactions récentes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Transactions Récentes</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilisateur</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {/* Données factices pour l'exemple */}
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">30/11/2025</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Commission</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">ElectroMaroc</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">+150 €</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Complété
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* ========== TAB: ANALYTIQUES ========== */}
      {activeTab === 'analytics' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Répartition par Catégorie</h3>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {/* ========== MODALS ========== */}
      {showUserDetailModal && selectedUser && (
        <UserDetailModal
          user={selectedUser}
          onClose={() => {
            setShowUserDetailModal(false);
            setSelectedUser(null);
          }}
          onAdjustBalance={handleAdjustBalance}
        />
      )}
    </div>
  );
};

// ========== COMPOSANTS UTILITAIRES ==========
const KPICard = ({ title, value, isCurrency, icon, trend, trendLabel }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between mb-4">
      <p className="text-sm text-gray-600">{title}</p>
      {icon}
    </div>
    <p className="text-3xl font-bold text-gray-900 mb-2">
      {isCurrency ? (
        <CountUp end={value} duration={2} separator=" " suffix=" €" />
      ) : (
        typeof value === 'number' ? <CountUp end={value} duration={2} separator=" " /> : value
      )}
    </p>
    {trend !== undefined && (
      <div className={`flex items-center gap-1 text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {trend >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        <span>{Math.abs(trend)}% {trendLabel}</span>
      </div>
    )}
  </div>
);

const StatBox = ({ title, value, icon, onClick }) => (
  <div 
    className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
    onClick={onClick}
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600 mb-2">{title}</p>
        <p className="text-3xl font-bold text-gray-900">
          <CountUp end={value} duration={2} separator=" " />
        </p>
      </div>
      <div className="p-3 bg-gray-50 rounded-full">
        {icon}
      </div>
    </div>
  </div>
);

const ActivityItem = ({ activity }) => (
  <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg">
    <div className="p-2 bg-indigo-100 rounded-full">
      <Activity size={16} className="text-indigo-600" />
    </div>
    <div className="flex-1">
      <p className="text-sm text-gray-900">{activity.description || 'Activité récente'}</p>
      <p className="text-xs text-gray-500 mt-1">{activity.time || 'Il y a quelques instants'}</p>
    </div>
  </div>
);

const UserDetailModal = ({ user, onClose, onAdjustBalance }) => {
  const [adjustAmount, setAdjustAmount] = useState('');
  const [adjustReason, setAdjustReason] = useState('');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold">Détails Utilisateur</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X size={24} />
            </button>
          </div>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <h4 className="font-semibold mb-3">Informations Générales</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Nom</p>
                <p className="font-medium">{user.full_name || user.company_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Téléphone</p>
                <p className="font-medium">{user.phone || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Date d'inscription</p>
                <p className="font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Finances</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Solde actuel</p>
              <p className="text-2xl font-bold text-gray-900">{(user.balance || 0).toLocaleString()} €</p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Ajuster le Solde</h4>
            <div className="space-y-3">
              <input
                type="number"
                placeholder="Montant (positif ou négatif)"
                value={adjustAmount}
                onChange={(e) => setAdjustAmount(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
              <textarea
                placeholder="Raison de l'ajustement (obligatoire)"
                value={adjustReason}
                onChange={(e) => setAdjustReason(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                rows={3}
              />
              <button
                onClick={() => {
                  if (adjustAmount && adjustReason) {
                    onAdjustBalance(user.id, parseFloat(adjustAmount), adjustReason);
                    setAdjustAmount('');
                    setAdjustReason('');
                    onClose();
                  }
                }}
                disabled={!adjustAmount || !adjustReason}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Confirmer l'Ajustement
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AdminDashboardComplete;
