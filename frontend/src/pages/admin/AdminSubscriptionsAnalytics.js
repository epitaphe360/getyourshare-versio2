import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart
} from 'recharts';
import {
  TrendingUp, TrendingDown, DollarSign, Users, AlertCircle,
  Calendar, ArrowUpCircle, ArrowDownCircle, Activity, Target
} from 'lucide-react';
import api from '../../utils/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const AdminSubscriptionsAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('6'); // 6 mois par défaut

  useEffect(() => {
    fetchAnalytics();
    fetchHistory();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/subscriptions/admin/analytics');
      if (response.data.success) {
        setAnalytics(response.data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await api.get(`/api/subscriptions/admin/metrics-history?months=${timeRange}`);
      if (response.data.success) {
        setHistory(response.data.history);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching history:', error);
      setLoading(false);
    }
  };

  if (loading || !analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const { metrics, plan_distribution, plan_revenue, role_distribution, mrr_evolution } = analytics;

  // Calculer les variations
  const mrrChange = mrr_evolution.length >= 2 
    ? ((mrr_evolution[mrr_evolution.length - 1].mrr - mrr_evolution[mrr_evolution.length - 2].mrr) / mrr_evolution[mrr_evolution.length - 2].mrr * 100)
    : 0;

  const activeChange = mrr_evolution.length >= 2
    ? mrr_evolution[mrr_evolution.length - 1].count - mrr_evolution[mrr_evolution.length - 2].count
    : 0;

  // Préparer les données pour les graphiques
  const planDistributionData = Object.entries(plan_distribution).map(([name, value]) => ({
    name,
    value,
    revenue: plan_revenue[name] || 0
  }));

  const roleDistributionData = Object.entries(role_distribution).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  const KPICard = ({ title, value, change, icon: Icon, color, suffix = '' }) => {
    const isPositive = change >= 0;
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg p-6 border-l-4"
        style={{ borderLeftColor: color }}
      >
        <div className="flex justify-between items-start">
          <div>
            <p className="text-gray-600 text-sm font-medium">{title}</p>
            <h3 className="text-3xl font-bold mt-2" style={{ color }}>
              {value}{suffix}
            </h3>
            {change !== undefined && (
              <div className={`flex items-center mt-2 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                <span className="ml-1 font-medium">
                  {Math.abs(change).toFixed(1)}% vs mois dernier
                </span>
              </div>
            )}
          </div>
          <div className="p-3 rounded-full" style={{ backgroundColor: `${color}20` }}>
            <Icon size={24} style={{ color }} />
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Avancés</h1>
        <p className="text-gray-600 mt-2">Vue complète de vos revenus et abonnements</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6 flex gap-2">
        {['3', '6', '12'].map((months) => (
          <button
            key={months}
            onClick={() => setTimeRange(months)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              timeRange === months
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            {months} mois
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          title="MRR (Monthly Recurring Revenue)"
          value={metrics.mrr.toLocaleString('fr-MA')}
          change={mrrChange}
          icon={DollarSign}
          color="#3b82f6"
          suffix=" MAD"
        />
        <KPICard
          title="ARR (Annual Recurring Revenue)"
          value={(metrics.arr / 1000).toFixed(1)}
          change={mrrChange}
          icon={TrendingUp}
          color="#10b981"
          suffix="K MAD"
        />
        <KPICard
          title="Abonnements Actifs"
          value={metrics.active_subscriptions}
          change={activeChange}
          icon={Users}
          color="#f59e0b"
        />
        <KPICard
          title="ARPU (Average Revenue Per User)"
          value={metrics.arpu.toFixed(0)}
          icon={Target}
          color="#8b5cf6"
          suffix=" MAD"
        />
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Taux de Churn</p>
              <h3 className="text-2xl font-bold mt-2 text-red-600">
                {metrics.churn_rate.toFixed(1)}%
              </h3>
            </div>
            <AlertCircle size={32} className="text-red-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Nouveaux ce mois</p>
              <h3 className="text-2xl font-bold mt-2 text-green-600">
                +{metrics.new_this_month}
              </h3>
            </div>
            <ArrowUpCircle size={32} className="text-green-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Abonnements</p>
              <h3 className="text-2xl font-bold mt-2 text-blue-600">
                {metrics.total_subscriptions}
              </h3>
            </div>
            <Activity size={32} className="text-blue-600" />
          </div>
        </motion.div>
      </div>

      {/* Charts Row 1: MRR Evolution & Plan Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* MRR Evolution */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2 text-blue-600" size={20} />
            Évolution MRR
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={mrr_evolution}>
              <defs>
                <linearGradient id="colorMrr" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value) => `${value.toLocaleString('fr-MA')} MAD`}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
              />
              <Area type="monotone" dataKey="mrr" stroke="#3b82f6" fillOpacity={1} fill="url(#colorMrr)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Plan Distribution */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4">Répartition par Plan</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={planDistributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {planDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name, props) => [
                  `${value} abonnés (${props.payload.revenue.toLocaleString('fr-MA')} MAD)`,
                  name
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Charts Row 2: Active Subscribers & Revenue by Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Active Subscribers Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Users className="mr-2 text-green-600" size={20} />
            Abonnés Actifs
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
              <Legend />
              <Line type="monotone" dataKey="active_count" stroke="#10b981" strokeWidth={2} name="Actifs" />
              <Line type="monotone" dataKey="new_count" stroke="#3b82f6" strokeWidth={2} name="Nouveaux" />
              <Line type="monotone" dataKey="churned_count" stroke="#ef4444" strokeWidth={2} name="Annulés" />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Revenue by Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <DollarSign className="mr-2 text-amber-600" size={20} />
            Revenus par Plan
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={planDistributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => `${value.toLocaleString('fr-MA')} MAD`}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
              />
              <Bar dataKey="revenue" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Role Distribution */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Répartition par Type d'Utilisateur</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={roleDistributionData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" />
            <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }} />
            <Bar dataKey="value" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
};

export default AdminSubscriptionsAnalytics;
