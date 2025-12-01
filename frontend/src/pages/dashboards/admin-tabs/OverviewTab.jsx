import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CountUp from 'react-countup';
import {
  DollarSign, Users, Target, Sparkles, ShoppingBag, Package,
  Briefcase, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Activity
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { formatCurrency, formatNumber, formatRelativeTime } from '../../../utils/helpers';
import api from '../../../utils/api';

const OverviewTab = ({ stats, dateFilter, refreshKey }) => {
  const navigate = useNavigate();
  const [revenueData, setRevenueData] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChartData();
  }, [dateFilter, refreshKey]);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      const [revenueRes, growthRes, activityRes] = await Promise.allSettled([
        api.get(`/api/analytics/revenue-chart?period=${dateFilter}`),
        api.get(`/api/analytics/user-growth?period=${dateFilter}`),
        api.get('/api/activity/recent?limit=10')
      ]);

      if (revenueRes.status === 'fulfilled') {
        setRevenueData(revenueRes.value.data || []);
      }
      if (growthRes.status === 'fulfilled') {
        setUserGrowthData(growthRes.value.data || []);
      }
      if (activityRes.status === 'fulfilled') {
        setRecentActivity(activityRes.value.data || []);
      }
    } catch (error) {
      console.error('Erreur chargement graphiques:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards - 4 principaux */}
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
          subtitle="(24h)"
        />
        <KPICard
          title="Taux de Conversion"
          value={`${(stats?.conversion_rate || 0).toFixed(1)}%`}
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

      {/* Quick Stats Grid - 6 statistiques rapides */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatBox
          title="Annonceurs"
          value={stats?.total_merchants || 0}
          icon={<ShoppingBag className="text-indigo-600" />}
          onClick={() => navigate('/admin/merchants')}
        />
        <StatBox
          title="Influenceurs"
          value={stats?.total_influencers || 0}
          icon={<Users className="text-pink-600" />}
        />
        <StatBox
          title="Commerciaux"
          value={stats?.total_commercials || 0}
          icon={<Briefcase className="text-blue-600" />}
        />
        <StatBox
          title="Produits"
          value={stats?.total_products || 0}
          icon={<Package className="text-green-600" />}
        />
        <StatBox
          title="Services"
          value={stats?.total_services || 0}
          icon={<Sparkles className="text-purple-600" />}
        />
        <StatBox
          title="Abonnements"
          value={stats?.active_subscriptions || 0}
          icon={<Target className="text-orange-600" />}
          subtitle={formatCurrency(stats?.subscription_revenue || 0)}
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
          {loading ? (
            <div className="h-[300px] flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
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
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                  name="Revenu"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* User Growth Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users size={20} className="text-blue-600" />
            Croissance Utilisateurs
          </h3>
          {loading ? (
            <div className="h-[300px] flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={userGrowthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="merchants"
                  stroke="#8b5cf6"
                  name="Annonceurs"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="influencers"
                  stroke="#ec4899"
                  name="Influenceurs"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="commercials"
                  stroke="#3b82f6"
                  name="Commerciaux"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity size={20} className="text-gray-600" />
          Activité Récente
        </h3>
        {loading ? (
          <div className="py-8 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : recentActivity.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Aucune activité récente</p>
        ) : (
          <div className="space-y-3">
            {recentActivity.map((activity, index) => (
              <ActivityItem key={index} activity={activity} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ========== COMPOSANTS UTILITAIRES ==========
const KPICard = ({ title, value, isCurrency, icon, trend, trendLabel, subtitle }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between mb-4">
      <p className="text-sm text-gray-600">{title}</p>
      {icon}
    </div>
    <div className="mb-2">
      <p className="text-3xl font-bold text-gray-900">
        {isCurrency ? (
          <CountUp end={typeof value === 'number' ? value : 0} duration={2} separator=" " suffix=" €" />
        ) : (
          typeof value === 'number' ? <CountUp end={value} duration={2} separator=" " /> : value
        )}
      </p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
    {trend !== undefined && (
      <div className={`flex items-center gap-1 text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {trend >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        <span>{Math.abs(trend).toFixed(1)}% {trendLabel}</span>
      </div>
    )}
  </div>
);

const StatBox = ({ title, value, icon, onClick, subtitle }) => (
  <div
    className={`bg-white rounded-lg shadow p-4 ${onClick ? 'cursor-pointer hover:shadow-lg' : ''} transition-shadow`}
    onClick={onClick}
  >
    <div className="flex items-center justify-between mb-2">
      <p className="text-xs text-gray-600">{title}</p>
      <div className="p-2 bg-gray-50 rounded-full">
        {icon}
      </div>
    </div>
    <p className="text-2xl font-bold text-gray-900">
      <CountUp end={value} duration={2} separator=" " />
    </p>
    {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
  </div>
);

const ActivityItem = ({ activity }) => (
  <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
    <div className="p-2 bg-indigo-100 rounded-full flex-shrink-0">
      <Activity size={16} className="text-indigo-600" />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-sm text-gray-900 truncate">
        {activity.description || activity.message || 'Activité récente'}
      </p>
      <p className="text-xs text-gray-500 mt-1">
        {formatRelativeTime(activity.created_at || activity.time)}
      </p>
    </div>
  </div>
);

export default OverviewTab;
