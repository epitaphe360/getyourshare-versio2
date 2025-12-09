import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import {
  TrendingUp, TrendingDown, AlertTriangle, Info, CheckCircle,
  Download, Calendar, Filter, BarChart2, Users, DollarSign,
  Target, Zap, Award, ArrowUp, ArrowDown, Minus
} from 'lucide-react';

// Import Advanced Analytics Components
import CohortAnalysisView from '../components/analytics/CohortAnalysisView';
import RFMSegmentationView from '../components/analytics/RFMSegmentationView';
import CustomerSegmentsPanel from '../components/analytics/CustomerSegmentsPanel';
import ABTestingManager from '../components/analytics/ABTestingManager';

const AdvancedAnalyticsDashboard = ({ userType = 'merchant', userId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('month'); // week, month, quarter, year
  const [activeTab, setActiveTab] = useState('overview'); // overview, insights, predictions, comparison
  const [timeSeriesData, setTimeSeriesData] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, [userType, userId, period]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      let endpoint = '';

      if (userType === 'merchant') {
        endpoint = `/api/analytics/merchant/${userId}`;
      } else if (userType === 'influencer') {
        endpoint = `/api/analytics/influencer/${userId}`;
      } else if (userType === 'sales_rep') {
        endpoint = `/api/analytics/sales-rep/${userId}`;
      }

      const response = await axios.get(endpoint, {
        params: { period }
      });

      setAnalytics(response.data);

      // Fetch time series data for charts
      const timeSeriesResponse = await axios.get(`${endpoint}/time-series`, {
        params: { period }
      });
      setTimeSeriesData(timeSeriesResponse.data);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  const exportData = () => {
    const dataStr = JSON.stringify(analytics, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics_${userType}_${period}_${new Date().toISOString()}.json`;
    link.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-8 text-center">
        <AlertTriangle className="mx-auto h-16 w-16 text-yellow-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-700">Aucune donnée disponible</h2>
      </div>
    );
  }

  return (
    <div className="advanced-analytics-dashboard bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <BarChart2 className="h-8 w-8 text-blue-600" />
                Analytics Pro
              </h1>
              <p className="text-gray-600 mt-1">
                {userType === 'merchant' && 'Tableau de bord marchand'}
                {userType === 'influencer' && 'Tableau de bord influenceur'}
                {userType === 'sales_rep' && 'Tableau de bord commercial'}
              </p>
            </div>

            <div className="flex gap-3">
              {/* Period Selector */}
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="week">Cette semaine</option>
                <option value="month">Ce mois</option>
                <option value="quarter">Ce trimestre</option>
                <option value="year">Cette année</option>
              </select>

              {/* Export Button */}
              <button
                onClick={exportData}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Download className="h-4 w-4" />
                Exporter
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mt-6 border-b">
            {['overview', 'insights', 'predictions', 'comparison', 'segments'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 px-2 font-medium transition border-b-2 ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab === 'overview' && 'Vue d\'ensemble'}
                {tab === 'insights' && 'Insights IA'}
                {tab === 'predictions' && 'Prédictions'}
                {tab === 'comparison' && 'Comparaison'}
                {tab === 'segments' && 'Segmentation'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <OverviewTab
            analytics={analytics}
            userType={userType}
            timeSeriesData={timeSeriesData}
          />
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <InsightsTab
            insights={analytics.insights}
            recommendations={analytics.recommendations}
          />
        )}

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <PredictionsTab predictions={analytics.predictions} />
        )}

        {/* Comparison Tab */}
        {activeTab === 'comparison' && (
          <ComparisonTab
            current={analytics.metrics.current}
            previous={analytics.metrics.previous}
            trends={analytics.metrics.trends}
            userType={userType}
          />
        )}

        {/* Segments Tab */}
        {activeTab === 'segments' && (
          <div className="space-y-6">
            {/* Cohort Analysis */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="h-6 w-6 text-blue-500" />
                Analyse de Cohortes
              </h2>
              <CohortAnalysisView />
            </div>

            {/* RFM Segmentation */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Target className="h-6 w-6 text-purple-500" />
                Segmentation RFM
              </h2>
              <RFMSegmentationView />
            </div>

            {/* Customer Segments */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="h-6 w-6 text-green-500" />
                Segments Clients
              </h2>
              <CustomerSegmentsPanel />
            </div>

            {/* A/B Testing */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <BarChart2 className="h-6 w-6 text-orange-500" />
                Gestion A/B Testing
              </h2>
              <ABTestingManager />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== OVERVIEW TAB ====================
const OverviewTab = ({ analytics, userType, timeSeriesData }) => {
  const { metrics } = analytics;
  const current = metrics.current;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      {userType === 'merchant' && (
        <MerchantKPIs current={current} trends={metrics.trends} />
      )}
      {userType === 'influencer' && (
        <InfluencerKPIs current={current} trends={metrics.trends} />
      )}
      {userType === 'sales_rep' && (
        <SalesRepKPIs current={current} trends={metrics.trends} />
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue/Performance Chart */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            {userType === 'merchant' && 'Évolution du revenu'}
            {userType === 'influencer' && 'Évolution des ventes'}
            {userType === 'sales_rep' && 'Évolution des deals'}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeSeriesData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorRevenue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Orders/Activities Chart */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            {userType === 'merchant' && 'Commandes par jour'}
            {userType === 'influencer' && 'Publications & Engagement'}
            {userType === 'sales_rep' && 'Activités quotidiennes'}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="orders" fill="#10b981" name="Commandes" />
              {userType === 'sales_rep' && (
                <Bar dataKey="calls" fill="#f59e0b" name="Appels" />
              )}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Performers */}
      {userType === 'merchant' && analytics.top_products && (
        <TopProductsSection products={analytics.top_products} />
      )}
      {userType === 'influencer' && analytics.top_content && (
        <TopContentSection content={analytics.top_content} />
      )}
      {userType === 'sales_rep' && analytics.hot_leads && (
        <HotLeadsSection leads={analytics.hot_leads} />
      )}
    </div>
  );
};

// ==================== KPI COMPONENTS ====================
const MerchantKPIs = ({ current, trends }) => {
  const kpis = [
    {
      title: 'Revenu Total',
      value: `${current.revenue?.total?.toLocaleString() || 0} MAD`,
      trend: trends.revenue || 0,
      icon: DollarSign,
      color: 'blue'
    },
    {
      title: 'Commandes',
      value: current.sales?.total_orders || 0,
      trend: trends.orders || 0,
      icon: BarChart2,
      color: 'green'
    },
    {
      title: 'Produits Actifs',
      value: current.products?.total_active || 0,
      trend: trends.products || 0,
      icon: Target,
      color: 'purple'
    },
    {
      title: 'Note Moyenne',
      value: `${current.reviews?.average_rating?.toFixed(1) || 0}/5`,
      trend: trends.rating || 0,
      icon: Award,
      color: 'yellow'
    },
    {
      title: 'Panier Moyen',
      value: `${current.sales?.average_order_value?.toLocaleString() || 0} MAD`,
      trend: trends.aov || 0,
      icon: TrendingUp,
      color: 'indigo'
    },
    {
      title: 'Nouveaux Clients',
      value: current.customers?.new || 0,
      trend: trends.new_customers || 0,
      icon: Users,
      color: 'pink'
    }
  ];

  return <KPIGrid kpis={kpis} />;
};

const InfluencerKPIs = ({ current, trends }) => {
  const kpis = [
    {
      title: 'Ventes Générées',
      value: current.sales?.total_sales_generated || 0,
      trend: trends.sales || 0,
      icon: DollarSign,
      color: 'blue'
    },
    {
      title: 'Commission Gagnée',
      value: `${current.sales?.total_commission?.toLocaleString() || 0} MAD`,
      trend: trends.commission || 0,
      icon: Award,
      color: 'green'
    },
    {
      title: 'Publications',
      value: current.content?.total_posts || 0,
      trend: trends.posts || 0,
      icon: BarChart2,
      color: 'purple'
    },
    {
      title: 'Vues Totales',
      value: (current.content?.total_views || 0).toLocaleString(),
      trend: trends.views || 0,
      icon: TrendingUp,
      color: 'yellow'
    },
    {
      title: 'Taux Engagement',
      value: `${current.content?.avg_engagement_rate?.toFixed(1) || 0}%`,
      trend: trends.engagement || 0,
      icon: Zap,
      color: 'indigo'
    },
    {
      title: 'Followers',
      value: (current.audience?.total_followers || 0).toLocaleString(),
      trend: trends.followers || 0,
      icon: Users,
      color: 'pink'
    }
  ];

  return <KPIGrid kpis={kpis} />;
};

const SalesRepKPIs = ({ current, trends }) => {
  const kpis = [
    {
      title: 'Deals Fermés',
      value: current.performance?.total_deals || 0,
      trend: trends.deals || 0,
      icon: Target,
      color: 'blue'
    },
    {
      title: 'Revenu Généré',
      value: `${current.performance?.total_revenue?.toLocaleString() || 0} MAD`,
      trend: trends.revenue || 0,
      icon: DollarSign,
      color: 'green'
    },
    {
      title: 'Taux de Closing',
      value: `${current.performance?.win_rate?.toFixed(1) || 0}%`,
      trend: trends.win_rate || 0,
      icon: Award,
      color: 'purple'
    },
    {
      title: 'Appels',
      value: current.activity?.total_calls || 0,
      trend: trends.calls || 0,
      icon: BarChart2,
      color: 'yellow'
    },
    {
      title: 'Leads Qualifiés',
      value: current.pipeline?.qualified_leads || 0,
      trend: trends.qualified_leads || 0,
      icon: Users,
      color: 'indigo'
    },
    {
      title: 'Pipeline Value',
      value: `${current.pipeline?.pipeline_value?.toLocaleString() || 0} MAD`,
      trend: trends.pipeline_value || 0,
      icon: TrendingUp,
      color: 'pink'
    }
  ];

  return <KPIGrid kpis={kpis} />;
};

const KPIGrid = ({ kpis }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {kpis.map((kpi, index) => (
        <KPICard key={index} {...kpi} />
      ))}
    </div>
  );
};

const KPICard = ({ title, value, trend, icon: Icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    indigo: 'bg-indigo-100 text-indigo-600',
    pink: 'bg-pink-100 text-pink-600'
  };

  const getTrendIcon = () => {
    if (trend > 0) return <ArrowUp className="h-4 w-4" />;
    if (trend < 0) return <ArrowDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const getTrendColor = () => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor()}`}>
          {getTrendIcon()}
          {Math.abs(trend).toFixed(1)}%
        </div>
      </div>
      <h3 className="text-gray-600 text-sm font-medium mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
};

// ==================== INSIGHTS TAB ====================
const InsightsTab = ({ insights, recommendations }) => {
  return (
    <div className="space-y-6">
      {/* Insights Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Zap className="h-6 w-6 text-yellow-500" />
          Insights IA
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights?.map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))}
        </div>
      </div>

      {/* Recommendations Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Target className="h-6 w-6 text-blue-500" />
          Recommandations Personnalisées
        </h2>
        <div className="space-y-4">
          {recommendations?.map((rec, index) => (
            <RecommendationCard key={index} recommendation={rec} />
          ))}
        </div>
      </div>
    </div>
  );
};

const InsightCard = ({ insight }) => {
  const getTypeConfig = () => {
    switch (insight.type) {
      case 'positive':
        return {
          icon: CheckCircle,
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          iconColor: 'text-green-600',
          textColor: 'text-green-900'
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          iconColor: 'text-yellow-600',
          textColor: 'text-yellow-900'
        };
      default:
        return {
          icon: Info,
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          iconColor: 'text-blue-600',
          textColor: 'text-blue-900'
        };
    }
  };

  const config = getTypeConfig();
  const Icon = config.icon;

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-xl p-5`}>
      <div className="flex items-start gap-4">
        <div className={`${config.iconColor} flex-shrink-0`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="flex-1">
          <h3 className={`font-bold text-lg ${config.textColor} mb-2`}>
            {insight.title}
          </h3>
          <p className="text-gray-700 mb-3">{insight.message}</p>
          {insight.impact && (
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor} border ${config.borderColor}`}>
              Impact: {insight.impact}
            </span>
          )}
          {insight.action && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-900">
                💡 Action recommandée: <span className="font-normal">{insight.action}</span>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const RecommendationCard = ({ recommendation }) => {
  const priorityColors = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200'
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-bold text-gray-900">{recommendation.title}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${priorityColors[recommendation.priority] || priorityColors.medium}`}>
              {recommendation.priority?.toUpperCase()}
            </span>
          </div>
          <p className="text-gray-600">{recommendation.description}</p>
        </div>
        {recommendation.estimated_impact && (
          <div className="ml-4 text-right">
            <div className="text-sm text-gray-600">Impact estimé</div>
            <div className="text-lg font-bold text-green-600">{recommendation.estimated_impact}</div>
          </div>
        )}
      </div>

      {/* Actions */}
      {recommendation.actions && recommendation.actions.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-bold text-gray-700 mb-2">Actions à entreprendre:</h4>
          <ul className="space-y-2">
            {recommendation.actions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// ==================== PREDICTIONS TAB ====================
const PredictionsTab = ({ predictions }) => {
  if (!predictions) {
    return (
      <div className="text-center py-12">
        <Info className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600">Pas assez de données pour générer des prédictions</p>
      </div>
    );
  }

  const { next_month, next_quarter, seasonal_trends } = predictions;

  return (
    <div className="space-y-6">
      {/* Next Month Predictions */}
      {next_month && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-blue-500" />
            Prédictions - Mois Prochain
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {next_month.revenue && (
              <PredictionCard
                title="Revenu Prévu"
                prediction={next_month.revenue}
                type="revenue"
              />
            )}
            {next_month.orders && (
              <PredictionCard
                title="Commandes Prévues"
                prediction={next_month.orders}
                type="orders"
              />
            )}
          </div>
        </div>
      )}

      {/* Next Quarter Predictions */}
      {next_quarter && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Calendar className="h-6 w-6 text-purple-500" />
            Prédictions - Trimestre Prochain
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {next_quarter.revenue && (
              <PredictionCard
                title="Revenu Prévu (3 mois)"
                prediction={next_quarter.revenue}
                type="revenue"
              />
            )}
          </div>
        </div>
      )}

      {/* Seasonal Trends */}
      {seasonal_trends && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Zap className="h-6 w-6 text-yellow-500" />
            Tendances Saisonnières
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <div className="text-sm text-gray-600 mb-1">Meilleur mois</div>
              <div className="text-2xl font-bold text-green-600">{seasonal_trends.best_month}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-red-200">
              <div className="text-sm text-gray-600 mb-1">Mois le plus faible</div>
              <div className="text-2xl font-bold text-red-600">{seasonal_trends.worst_month}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="text-sm text-gray-600 mb-1">Prochain pic</div>
              <div className="text-2xl font-bold text-blue-600">{seasonal_trends.upcoming_peak}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const PredictionCard = ({ title, prediction, type }) => {
  const formatValue = (value) => {
    if (type === 'revenue') {
      return `${Math.round(value).toLocaleString()} MAD`;
    }
    return Math.round(value).toLocaleString();
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
      <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Minimum</span>
          <span className="font-semibold text-gray-700">{formatValue(prediction.min)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Attendu</span>
          <span className="text-xl font-bold text-blue-600">{formatValue(prediction.expected)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Maximum</span>
          <span className="font-semibold text-gray-700">{formatValue(prediction.max)}</span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-blue-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Confiance</span>
          <div className="flex items-center gap-2">
            <div className="w-24 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${prediction.confidence}%` }}
              ></div>
            </div>
            <span className="text-sm font-medium text-blue-600">{prediction.confidence}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== COMPARISON TAB ====================
const ComparisonTab = ({ current, previous, trends, userType }) => {
  const getMetrics = () => {
    if (userType === 'merchant') {
      return [
        { label: 'Revenu', currentKey: 'revenue.total', previousKey: 'revenue.total', trend: trends.revenue, format: 'currency' },
        { label: 'Commandes', currentKey: 'sales.total_orders', previousKey: 'sales.total_orders', trend: trends.orders, format: 'number' },
        { label: 'Panier Moyen', currentKey: 'sales.average_order_value', previousKey: 'sales.average_order_value', trend: trends.aov, format: 'currency' },
        { label: 'Produits Actifs', currentKey: 'products.total_active', previousKey: 'products.total_active', trend: trends.products, format: 'number' },
        { label: 'Note Moyenne', currentKey: 'reviews.average_rating', previousKey: 'reviews.average_rating', trend: trends.rating, format: 'rating' },
        { label: 'Trafic', currentKey: 'traffic.total_visits', previousKey: 'traffic.total_visits', trend: trends.traffic, format: 'number' }
      ];
    } else if (userType === 'influencer') {
      return [
        { label: 'Ventes Générées', currentKey: 'sales.total_sales_generated', previousKey: 'sales.total_sales_generated', trend: trends.sales, format: 'number' },
        { label: 'Commission', currentKey: 'sales.total_commission', previousKey: 'sales.total_commission', trend: trends.commission, format: 'currency' },
        { label: 'Publications', currentKey: 'content.total_posts', previousKey: 'content.total_posts', trend: trends.posts, format: 'number' },
        { label: 'Vues', currentKey: 'content.total_views', previousKey: 'content.total_views', trend: trends.views, format: 'number' },
        { label: 'Engagement', currentKey: 'content.avg_engagement_rate', previousKey: 'content.avg_engagement_rate', trend: trends.engagement, format: 'percent' },
        { label: 'Followers', currentKey: 'audience.total_followers', previousKey: 'audience.total_followers', trend: trends.followers, format: 'number' }
      ];
    } else {
      return [
        { label: 'Deals Fermés', currentKey: 'performance.total_deals', previousKey: 'performance.total_deals', trend: trends.deals, format: 'number' },
        { label: 'Revenu', currentKey: 'performance.total_revenue', previousKey: 'performance.total_revenue', trend: trends.revenue, format: 'currency' },
        { label: 'Taux de Closing', currentKey: 'performance.win_rate', previousKey: 'performance.win_rate', trend: trends.win_rate, format: 'percent' },
        { label: 'Appels', currentKey: 'activity.total_calls', previousKey: 'activity.total_calls', trend: trends.calls, format: 'number' },
        { label: 'Leads Qualifiés', currentKey: 'pipeline.qualified_leads', previousKey: 'pipeline.qualified_leads', trend: trends.qualified_leads, format: 'number' },
        { label: 'Pipeline Value', currentKey: 'pipeline.pipeline_value', previousKey: 'pipeline.pipeline_value', trend: trends.pipeline_value, format: 'currency' }
      ];
    }
  };

  const getNestedValue = (obj, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  };

  const formatValue = (value, format) => {
    if (!value && value !== 0) return 'N/A';

    switch (format) {
      case 'currency':
        return `${Math.round(value).toLocaleString()} MAD`;
      case 'percent':
        return `${value.toFixed(1)}%`;
      case 'rating':
        return `${value.toFixed(1)}/5`;
      default:
        return value.toLocaleString();
    }
  };

  const metrics = getMetrics();

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Comparaison Période Précédente</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Métrique
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Période Actuelle
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Période Précédente
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Évolution
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.map((metric, index) => {
                const currentValue = getNestedValue(current, metric.currentKey);
                const previousValue = getNestedValue(previous, metric.previousKey);
                const trend = metric.trend || 0;

                return (
                  <tr key={index} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{metric.label}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-bold text-gray-900">
                        {formatValue(currentValue, metric.format)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-600">
                        {formatValue(previousValue, metric.format)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                        trend > 0
                          ? 'bg-green-100 text-green-700'
                          : trend < 0
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {trend > 0 && <ArrowUp className="h-4 w-4" />}
                        {trend < 0 && <ArrowDown className="h-4 w-4" />}
                        {trend === 0 && <Minus className="h-4 w-4" />}
                        {Math.abs(trend).toFixed(1)}%
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ==================== TOP PERFORMERS ====================
const TopProductsSection = ({ products }) => {
  if (!products || products.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Award className="h-6 w-6 text-yellow-500" />
        Top Produits
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Produit</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ventes</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Revenu</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Note</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {products.slice(0, 10).map((product, index) => (
              <tr key={product.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                    index === 0 ? 'bg-yellow-100 text-yellow-700' :
                    index === 1 ? 'bg-gray-100 text-gray-700' :
                    index === 2 ? 'bg-orange-100 text-orange-700' :
                    'bg-gray-50 text-gray-600'
                  }`}>
                    {index + 1}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{product.name}</div>
                  <div className="text-sm text-gray-500">{product.category}</div>
                </td>
                <td className="px-4 py-3 text-right font-medium">{product.total_sales}</td>
                <td className="px-4 py-3 text-right font-medium">{product.revenue?.toLocaleString()} MAD</td>
                <td className="px-4 py-3 text-right">
                  <span className="text-yellow-500">★</span> {product.rating?.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const TopContentSection = ({ content }) => {
  if (!content || content.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Zap className="h-6 w-6 text-purple-500" />
        Top Contenu
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {content.slice(0, 6).map((item) => (
          <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition">
            <div className="font-medium text-gray-900 mb-2">{item.title}</div>
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>{item.views?.toLocaleString()} vues</span>
              <span>{item.engagement_rate?.toFixed(1)}% engagement</span>
            </div>
            <div className="mt-2 text-xs text-gray-500">{item.sales_generated} ventes</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const HotLeadsSection = ({ leads }) => {
  if (!leads || leads.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Target className="h-6 w-6 text-red-500" />
        Leads HOT
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entreprise</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Valeur</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Probabilité</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {leads.slice(0, 10).map((lead) => (
              <tr key={lead.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold ${
                    lead.score >= 80 ? 'bg-green-100 text-green-700' :
                    lead.score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {lead.score}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{lead.contact_name}</div>
                  <div className="text-sm text-gray-500">{lead.contact_email}</div>
                </td>
                <td className="px-4 py-3 text-gray-900">{lead.company_name || 'N/A'}</td>
                <td className="px-4 py-3 text-right font-medium">{lead.estimated_value?.toLocaleString() || 0} MAD</td>
                <td className="px-4 py-3 text-right font-medium text-green-600">{lead.probability_to_close?.toFixed(0) || 0}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;
