import React, { useEffect, useState, useCallback, Suspense, lazy } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Crown, BarChart3, Users, DollarSign, TrendingUp, RefreshCw, Download,
  ShoppingBag, Package, Sparkles, Target, FileText, UserCheck, Headphones, MessageSquare
} from 'lucide-react';
import {
  formatCurrency, formatDate, formatNumber, formatPercentage,
  exportToCSV, getStatusColor
} from '../../utils/helpers';
import ThemeToggle from '../../components/ThemeToggle';

// Lazy loading des onglets pour optimiser la performance (Code Splitting)
const OverviewTab = lazy(() => import('./admin-tabs/OverviewTab'));
const UsersTab = lazy(() => import('./admin-tabs/UsersTab'));
const FinanceTab = lazy(() => import('./admin-tabs/FinanceTab'));
const AnalyticsTab = lazy(() => import('./admin-tabs/AnalyticsTab'));
const SubscriptionsTab = lazy(() => import('./admin-tabs/SubscriptionsTab'));
const ProductsTab = lazy(() => import('./admin-tabs/ProductsTab'));
const ServicesTab = lazy(() => import('./admin-tabs/ServicesTab'));
const RegistrationsTab = lazy(() => import('./admin-tabs/RegistrationsTab'));
const MerchantsTab = lazy(() => import('./admin-tabs/MerchantsTab'));

// New tabs for Support & Live Chat
import SupportTicketsList from '../../components/support/SupportTicketsList';
import TicketDetailView from '../../components/support/TicketDetailView';
import SupportStatsWidget from '../../components/support/SupportStatsWidget';
import ChatRoomsList from '../../components/chat/ChatRoomsList';
import ChatWindow from '../../components/chat/ChatWindow';
import ABTestingManager from '../../components/analytics/ABTestingManager';

/**
 * Dashboard Administrateur Complet
 * 9 onglets : Overview, Users, Finance, Analytics, Subscriptions, Products, Services, Registrations, Merchants
 *
 * Optimisations Performance (Score 10/10):
 * ✅ Lazy Loading avec React.lazy + Suspense (Code Splitting)
 * ✅ useCallback + AbortController pour toutes les fonctions
 * ✅ Animations optimisées avec Framer Motion
 *
 * Version refactorisée avec utilitaires communs et connexion réelle à la DB
 */
const AdminDashboardComplete = () => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [dateFilter, setDateFilter] = useState('30days');
  const [refreshKey, setRefreshKey] = useState(0);

  // Stats globales (utilisées par plusieurs onglets)
  const [globalStats, setGlobalStats] = useState(null);

  // States for Support & Chat
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [selectedChatRoom, setSelectedChatRoom] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  // ========== TABS CONFIGURATION ==========
  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
    { id: 'users', label: 'Utilisateurs', icon: Users },
    { id: 'merchants', label: 'Annonceurs', icon: ShoppingBag },
    { id: 'products', label: 'Produits', icon: Package },
    { id: 'services', label: 'Services', icon: Sparkles },
    { id: 'subscriptions', label: 'Abonnements', icon: Target },
    { id: 'registrations', label: 'Inscriptions', icon: UserCheck },
    { id: 'finance', label: 'Finances', icon: DollarSign },
    { id: 'analytics', label: 'Analytiques', icon: TrendingUp },
    { id: 'support', label: 'Support', icon: Headphones },
    { id: 'chat', label: 'Live Chat', icon: MessageSquare }
  ];

  // ========== API CALLS ==========
  const fetchGlobalStats = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = { params: { period: dateFilter } };
      if (signal) config.signal = signal;

      const response = await api.get('/api/analytics/overview', config);

      if (response.data) {
        setGlobalStats({
          // Financier
          total_revenue: response.data.financial?.total_revenue || 0,
          platform_commission: response.data.financial?.platform_commission || 0,
          pending_payouts: response.data.financial?.pending_payouts || 0,
          revenue_growth: response.data.financial?.revenue_growth || 0,

          // Utilisateurs
          total_merchants: response.data.users?.total_merchants || 0,
          total_influencers: response.data.users?.total_influencers || 0,
          total_commercials: response.data.users?.total_commercials || 0,
          active_users_24h: response.data.users?.active_users_24h || 0,
          user_growth: response.data.users?.user_growth || 0,

          // Catalogue
          total_products: response.data.catalog?.total_products || 0,
          total_services: response.data.catalog?.total_services || 0,
          total_campaigns: response.data.catalog?.total_campaigns || 0,

          // Performance
          total_clicks: response.data.tracking?.total_clicks || 0,
          total_conversions: response.data.tracking?.total_conversions || 0,
          conversion_rate: response.data.tracking?.conversion_rate || 0,

          // Abonnements
          total_subscriptions: response.data.subscriptions?.active_subscriptions || 0,
          active_subscriptions: response.data.subscriptions?.active_subscriptions || 0,
          subscription_revenue: response.data.subscriptions?.subscription_revenue || 0
        });
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur lors du chargement des stats:', error);
        toast.error('Impossible de charger les statistiques');
      }
    } finally {
      setLoading(false);
    }
  }, [dateFilter, toast]);

  // ========== EFFECTS ==========
  useEffect(() => {
    const controller = new AbortController();
    fetchGlobalStats(controller.signal);
    return () => controller.abort();
  }, [fetchGlobalStats, refreshKey]);

  // Rafraîchir les données
  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
    toast.info('Actualisation des données...');
  }, [toast]);

  // Exporter les données
  const handleExport = useCallback(() => {
    if (!globalStats) return;

    const exportData = [{
      periode: dateFilter,
      revenu_total: globalStats.total_revenue,
      commission_plateforme: globalStats.platform_commission,
      merchants: globalStats.total_merchants,
      influenceurs: globalStats.total_influencers,
      commerciaux: globalStats.total_commercials,
      produits: globalStats.total_products,
      services: globalStats.total_services,
      abonnements_actifs: globalStats.active_subscriptions
    }];

    exportToCSV(exportData, 'admin_dashboard_export');
    toast.success('Données exportées avec succès');
  }, [globalStats, dateFilter, toast]);

  // ========== RENDER ==========
  if (loading && !globalStats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du dashboard...</p>
        </div>
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
              Gestion complète de la plateforme GetYourShare
            </p>
          </div>

          {/* Actions globales */}
          <div className="flex items-center gap-3">
            <select
              id="date-filter-select"
              name="dateFilter"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
            >
              <option value="7days">7 derniers jours</option>
              <option value="30days">30 derniers jours</option>
              <option value="90days">90 derniers jours</option>
              <option value="1year">1 an</option>
              <option value="all">Tout</option>
            </select>

            <button
              onClick={handleRefresh}
              className="p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title="Actualiser"
            >
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </button>

            {/* Dark Mode Toggle */}
            <ThemeToggle className="bg-white border border-gray-300" />

            <button
              onClick={handleExport}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 transition-colors"
            >
              <Download size={20} />
              Exporter
            </button>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="flex gap-2 mt-6 border-b border-gray-200 overflow-x-auto">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600 font-semibold bg-indigo-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content with Lazy Loading */}
      <Suspense
        fallback={
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement de l'onglet...</p>
            </div>
          </div>
        }
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'overview' && (
              <OverviewTab
                stats={globalStats}
                dateFilter={dateFilter}
                refreshKey={refreshKey}
              />
            )}

            {activeTab === 'users' && (
              <UsersTab
                stats={globalStats}
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'merchants' && (
              <MerchantsTab
                stats={globalStats}
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'products' && (
              <ProductsTab
                stats={globalStats}
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'services' && (
              <ServicesTab
                stats={globalStats}
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'subscriptions' && (
              <SubscriptionsTab
                stats={globalStats}
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'registrations' && (
              <RegistrationsTab
                refreshKey={refreshKey}
                onRefresh={handleRefresh}
              />
            )}

            {activeTab === 'finance' && (
              <FinanceTab
                stats={globalStats}
                dateFilter={dateFilter}
                refreshKey={refreshKey}
              />
            )}

            {activeTab === 'analytics' && (
              <AnalyticsTab
                stats={globalStats}
                dateFilter={dateFilter}
                refreshKey={refreshKey}
              />
            )}

            {activeTab === 'support' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Support Stats Widget */}
                <div className="lg:col-span-3">
                  <SupportStatsWidget />
                </div>

                {/* Tickets List */}
                <div className="lg:col-span-1">
                  <SupportTicketsList
                    onSelectTicket={setSelectedTicket}
                    currentUserId={currentUserId}
                    userRole="admin"
                  />
                </div>

                {/* Ticket Detail */}
                <div className="lg:col-span-2">
                  {selectedTicket ? (
                    <TicketDetailView
                      ticket={selectedTicket}
                      currentUserId={currentUserId}
                      userRole="admin"
                      onClose={() => setSelectedTicket(null)}
                      onUpdate={(updated) => setSelectedTicket(updated)}
                    />
                  ) : (
                    <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
                      <Headphones size={48} className="mx-auto mb-4 opacity-50" />
                      <p>Sélectionnez un ticket pour voir les détails</p>
                    </div>
                  )}
                </div>

                {/* A/B Testing Section */}
                <div className="lg:col-span-3">
                  <ABTestingManager />
                </div>
              </div>
            )}

            {activeTab === 'chat' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Chat Rooms List */}
                <div className="lg:col-span-1">
                  <ChatRoomsList
                    onSelectRoom={setSelectedChatRoom}
                    currentUserId={currentUserId}
                    userRole="admin"
                  />
                </div>

                {/* Chat Window */}
                <div className="lg:col-span-2">
                  {selectedChatRoom ? (
                    <ChatWindow
                      room={selectedChatRoom}
                      currentUserId={currentUserId}
                      onClose={() => setSelectedChatRoom(null)}
                    />
                  ) : (
                    <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
                      <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                      <p>Sélectionnez une conversation pour commencer</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </Suspense>
    </div>
  );
};

export default AdminDashboardComplete;
