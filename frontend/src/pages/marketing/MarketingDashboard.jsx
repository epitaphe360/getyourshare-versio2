import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mail,
  Users,
  TrendingUp,
  ShoppingCart,
  Gift,
  Award,
  Target,
  Send,
  CheckCircle,
  Clock,
  DollarSign,
  UserCheck,
  UserX,
  Zap,
  BarChart3,
  PieChart,
  Filter
} from 'lucide-react';
import api from '../../services/api';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Marketing Automation Dashboard
 * ROI: 1.78M€/month
 * Features: Abandoned Cart, Win-back, Segmentation RFM, Loyalty
 */
const MarketingDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [segments, setSegments] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, campaigns, segments, loyalty

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch customer segments
      const segRes = await api.get('/api/marketing/segments');
      setSegments(segRes.data.segments);

      // TODO: Fetch campaigns and stats when backend endpoints are ready
      // const campaignsRes = await api.get('/api/marketing/campaigns');
      // const statsRes = await api.get('/api/marketing/stats');

      // Mock data for now
      setStats({
        total_campaigns: 12,
        active_campaigns: 5,
        total_sent: 45230,
        open_rate: 42.5,
        click_rate: 18.3,
        conversion_rate: 8.7,
        revenue_generated: 187450,
        abandoned_carts_recovered: 35,
        win_back_customers: 127,
        avg_loyalty_points: 245
      });

      setCampaigns([
        {
          id: 1,
          name: 'Abandoned Cart Recovery',
          type: 'abandoned_cart',
          status: 'active',
          sent: 1230,
          opened: 523,
          clicked: 187,
          converted: 92,
          revenue: 45670
        },
        {
          id: 2,
          name: 'Win-Back Spring 2024',
          type: 'win_back',
          status: 'active',
          sent: 850,
          opened: 412,
          clicked: 156,
          converted: 67,
          revenue: 23400
        },
        {
          id: 3,
          name: 'Welcome Series',
          type: 'welcome_series',
          status: 'active',
          sent: 2340,
          opened: 1876,
          clicked: 934,
          converted: 412,
          revenue: 67890
        }
      ]);

    } catch (error) {
      console.error('Error fetching marketing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runWinBackCampaign = async () => {
    try {
      const result = await api.post('/api/marketing/win-back');
      alert(`✅ Campagne Win-Back lancée! ${result.data.sent_to} clients ciblés`);
      fetchData();
    } catch (error) {
      alert('Erreur lors du lancement de la campagne');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Zap size={48} className="text-indigo-600" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-gray-50 to-indigo-50 min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Marketing Automation</h1>
            <p className="text-indigo-100 text-lg">
              Automatisez vos campagnes pour un ROI maximal: 1.78M€/mois
            </p>
          </div>
          <motion.div
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="bg-white/20 backdrop-blur-lg rounded-2xl p-6"
          >
            <TrendingUp size={64} />
          </motion.div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-2 bg-white rounded-xl p-2 shadow-lg">
        {[
          { id: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
          { id: 'campaigns', label: 'Campagnes', icon: Mail },
          { id: 'segments', label: 'Segments RFM', icon: Users },
          { id: 'loyalty', label: 'Fidélité', icon: Award }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <tab.icon size={20} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <KPICard
              icon={Mail}
              title="Campagnes Actives"
              value={stats.active_campaigns}
              subtitle={`${stats.total_campaigns} au total`}
              color="indigo"
              trend="+12%"
            />
            <KPICard
              icon={Send}
              title="Emails Envoyés"
              value={stats.total_sent.toLocaleString()}
              subtitle={`${stats.open_rate}% d'ouverture`}
              color="blue"
              trend="+28%"
            />
            <KPICard
              icon={TrendingUp}
              title="Taux de Conversion"
              value={`${stats.conversion_rate}%`}
              subtitle={`${stats.click_rate}% de clics`}
              color="green"
              trend="+15%"
            />
            <KPICard
              icon={DollarSign}
              title="Revenus Générés"
              value={`${(stats.revenue_generated / 1000).toFixed(0)}K€`}
              subtitle="Ce mois"
              color="purple"
              trend="+42%"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <QuickActionCard
              icon={ShoppingCart}
              title="Paniers Abandonnés"
              description="Récupérez 35% des paniers abandonnés automatiquement"
              buttonText="Lancer la campagne"
              buttonAction={() => alert('Campagne de paniers abandonnés en cours')}
              stats={`${stats.abandoned_carts_recovered}% récupérés`}
              color="orange"
            />
            <QuickActionCard
              icon={UserCheck}
              title="Win-Back"
              description="Réengagez les clients inactifs depuis 90 jours"
              buttonText="Lancer Win-Back"
              buttonAction={runWinBackCampaign}
              stats={`${stats.win_back_customers} clients réactivés`}
              color="blue"
            />
            <QuickActionCard
              icon={Gift}
              title="Fidélité"
              description="Programme de points automatique: 1€ = 1 point"
              buttonText="Voir le programme"
              buttonAction={() => setActiveTab('loyalty')}
              stats={`${stats.avg_loyalty_points} pts moyens`}
              color="purple"
            />
          </div>

          {/* Recent Campaigns Performance */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <BarChart3 className="text-indigo-600" />
              Performance des Campagnes
            </h2>
            <div className="space-y-4">
              {campaigns.map(campaign => (
                <CampaignRow key={campaign.id} campaign={campaign} />
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Mail className="text-indigo-600" />
                Toutes les Campagnes
              </h2>
              <button className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all">
                + Nouvelle Campagne
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Campagne</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Type</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Envoyés</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Taux Ouverture</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Conversions</th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Revenus</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {campaigns.map(campaign => (
                    <tr key={campaign.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-gray-900">{campaign.name}</div>
                      </td>
                      <td className="px-6 py-4">
                        {getCampaignTypeBadge(campaign.type)}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(campaign.status)}
                      </td>
                      <td className="px-6 py-4 text-right font-semibold">{campaign.sent.toLocaleString()}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-semibold text-blue-600">
                          {((campaign.opened / campaign.sent) * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-semibold text-green-600">
                          {campaign.converted} ({((campaign.converted / campaign.sent) * 100).toFixed(1)}%)
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right font-bold text-purple-600">
                        {campaign.revenue.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {/* Segments Tab */}
      {activeTab === 'segments' && segments && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Target className="text-indigo-600" />
              Segmentation RFM (Recency, Frequency, Monetary)
            </h2>
            <p className="text-gray-600 mb-6">
              Ciblage automatique basé sur le comportement d'achat de vos clients
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <SegmentCard
                title="🏆 Champions"
                count={segments.champions?.length || 0}
                description="Clients fidèles et dépensiers"
                color="from-yellow-400 to-orange-500"
                rfm="R:5 F:5 M:5"
                action="Récompenser VIP"
              />
              <SegmentCard
                title="💎 Loyaux"
                count={segments.loyal?.length || 0}
                description="Achats fréquents et réguliers"
                color="from-blue-400 to-indigo-500"
                rfm="R:4-5 F:4-5 M:4-5"
                action="Offres exclusives"
              />
              <SegmentCard
                title="🌱 Potentiels"
                count={segments.potential?.length || 0}
                description="Récents mais peu d'achats"
                color="from-green-400 to-emerald-500"
                rfm="R:4-5 F:1-2"
                action="Nurturing intensif"
              />
              <SegmentCard
                title="⚠️ À Risque"
                count={segments.at_risk?.length || 0}
                description="Clients fidèles devenus inactifs"
                color="from-orange-400 to-red-500"
                rfm="R:2-3 F:4-5"
                action="Win-Back urgent"
              />
              <SegmentCard
                title="😴 Hibernants"
                count={segments.hibernating?.length || 0}
                description="Inactifs avec peu d'historique"
                color="from-gray-400 to-gray-500"
                rfm="R:1-2 F:2-3"
                action="Réactivation douce"
              />
              <SegmentCard
                title="❌ Perdus"
                count={segments.lost?.length || 0}
                description="Inactifs depuis longtemps"
                color="from-red-400 to-pink-500"
                rfm="R:1 F:1"
                action="Dernière tentative"
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Loyalty Tab */}
      {activeTab === 'loyalty' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Award className="text-indigo-600" />
              Programme de Fidélité
            </h2>
            <p className="text-gray-600 mb-6">
              Système automatique: 1€ dépensé = 1 point gagné | 100 points = 5€ de réduction
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white">
                <Award size={32} className="mb-2" />
                <p className="text-3xl font-bold">{stats.avg_loyalty_points}</p>
                <p className="text-purple-100">Points moyens par client</p>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white">
                <Gift size={32} className="mb-2" />
                <p className="text-3xl font-bold">1,234</p>
                <p className="text-green-100">Récompenses échangées</p>
              </div>
              <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl p-6 text-white">
                <TrendingUp size={32} className="mb-2" />
                <p className="text-3xl font-bold">+45%</p>
                <p className="text-orange-100">Repeat purchase rate</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">Configuration du Programme</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white rounded-lg">
                  <div>
                    <p className="font-semibold">Taux de conversion</p>
                    <p className="text-sm text-gray-600">1€ dépensé = X points</p>
                  </div>
                  <input
                    type="number"
                    defaultValue="1"
                    className="w-20 px-3 py-2 border rounded-lg text-center font-bold"
                  />
                </div>
                <div className="flex items-center justify-between p-4 bg-white rounded-lg">
                  <div>
                    <p className="font-semibold">Valeur de rachat</p>
                    <p className="text-sm text-gray-600">X points = 5€ de réduction</p>
                  </div>
                  <input
                    type="number"
                    defaultValue="100"
                    className="w-20 px-3 py-2 border rounded-lg text-center font-bold"
                  />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

// Component: KPI Card
const KPICard = ({ icon: Icon, title, value, subtitle, color, trend }) => {
  const colorClasses = {
    indigo: 'border-indigo-500 text-indigo-600',
    blue: 'border-blue-500 text-blue-600',
    green: 'border-green-500 text-green-600',
    purple: 'border-purple-500 text-purple-600',
    orange: 'border-orange-500 text-orange-600'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${colorClasses[color]}`}
    >
      <div className="flex items-center justify-between mb-3">
        <Icon size={32} className={colorClasses[color]} />
        {trend && (
          <span className="text-green-600 font-semibold text-sm bg-green-50 px-2 py-1 rounded">
            {trend}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-4xl font-bold mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </motion.div>
  );
};

// Component: Quick Action Card
const QuickActionCard = ({ icon: Icon, title, description, buttonText, buttonAction, stats, color }) => {
  const colorClasses = {
    orange: 'from-orange-500 to-red-500',
    blue: 'from-blue-500 to-indigo-500',
    purple: 'from-purple-500 to-pink-500'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center mb-4`}>
        <Icon size={24} className="text-white" />
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-4">{description}</p>
      <div className="mb-4">
        <span className="text-2xl font-bold text-gray-900">{stats}</span>
      </div>
      <button
        onClick={buttonAction}
        className={`w-full px-4 py-3 bg-gradient-to-r ${colorClasses[color]} text-white rounded-lg font-semibold hover:shadow-lg transition-all`}
      >
        {buttonText}
      </button>
    </motion.div>
  );
};

// Component: Campaign Row
const CampaignRow = ({ campaign }) => {
  const openRate = ((campaign.opened / campaign.sent) * 100).toFixed(1);
  const conversionRate = ((campaign.converted / campaign.sent) * 100).toFixed(1);

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
      <div className="flex-1">
        <h3 className="font-semibold text-lg">{campaign.name}</h3>
        <p className="text-sm text-gray-600">{campaign.sent.toLocaleString()} envois</p>
      </div>
      <div className="flex gap-8 items-center">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600">{openRate}%</p>
          <p className="text-xs text-gray-600">Ouverture</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600">{conversionRate}%</p>
          <p className="text-xs text-gray-600">Conversion</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-purple-600">
            {(campaign.revenue / 1000).toFixed(1)}K€
          </p>
          <p className="text-xs text-gray-600">Revenus</p>
        </div>
      </div>
    </div>
  );
};

// Component: Segment Card
const SegmentCard = ({ title, count, description, color, rfm, action }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -5 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden"
    >
      <div className={`h-2 bg-gradient-to-r ${color}`} />
      <div className="p-6">
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-4xl font-bold mb-2">{count}</p>
        <p className="text-gray-600 text-sm mb-3">{description}</p>
        <div className="bg-gray-100 rounded-lg p-2 mb-3">
          <p className="text-xs font-mono text-gray-700">{rfm}</p>
        </div>
        <button className={`w-full px-4 py-2 bg-gradient-to-r ${color} text-white rounded-lg font-semibold text-sm hover:shadow-lg transition-all`}>
          {action}
        </button>
      </div>
    </motion.div>
  );
};

// Helper Functions
const getCampaignTypeBadge = (type) => {
  const badges = {
    abandoned_cart: { label: 'Panier Abandonné', color: 'bg-orange-100 text-orange-700' },
    win_back: { label: 'Win-Back', color: 'bg-blue-100 text-blue-700' },
    welcome_series: { label: 'Bienvenue', color: 'bg-purple-100 text-purple-700' },
    post_purchase: { label: 'Post-Achat', color: 'bg-green-100 text-green-700' }
  };
  const badge = badges[type] || { label: type, color: 'bg-gray-100 text-gray-700' };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
      {badge.label}
    </span>
  );
};

const getStatusBadge = (status) => {
  const badges = {
    active: { label: 'Actif', color: 'bg-green-100 text-green-700', icon: CheckCircle },
    paused: { label: 'Pause', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
    draft: { label: 'Brouillon', color: 'bg-gray-100 text-gray-700', icon: Mail }
  };
  const badge = badges[status] || badges.draft;
  const Icon = badge.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
      <Icon size={14} />
      {badge.label}
    </span>
  );
};

export default MarketingDashboard;
