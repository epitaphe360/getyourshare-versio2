import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { TrendingUp, Package, Users, DollarSign, Target } from 'lucide-react';
import { formatCurrency, formatNumber } from '../../../utils/helpers';
import api from '../../../utils/api';
import { useToast } from '../../../context/ToastContext';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#14b8a6'];

const AnalyticsTab = ({ stats, dateFilter, refreshKey }) => {
  const toast = useToast();
  const [categoryData, setCategoryData] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [topInfluencers, setTopInfluencers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [dateFilter, refreshKey]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [categoriesRes, productsRes, influencersRes] = await Promise.allSettled([
        api.get(`/api/analytics/categories?period=${dateFilter}`),
        api.get(`/api/analytics/top-products?period=${dateFilter}&limit=10`),
        api.get(`/api/analytics/top-influencers?period=${dateFilter}&limit=10`)
      ]);

      if (categoriesRes.status === 'fulfilled') {
        setCategoryData(categoriesRes.value.data || []);
      }
      if (productsRes.status === 'fulfilled') {
        setTopProducts(productsRes.value.data || []);
      }
      if (influencersRes.status === 'fulfilled') {
        setTopInfluencers(influencersRes.value.data || []);
      }
    } catch (error) {
      console.error('Erreur chargement analytics:', error);
      toast.error('Impossible de charger les analytics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Total Clics"
          value={stats?.total_clicks || 0}
          icon={<Target className="text-blue-600" />}
        />
        <StatCard
          title="Conversions"
          value={stats?.total_conversions || 0}
          icon={<TrendingUp className="text-green-600" />}
        />
        <StatCard
          title="Taux Conversion"
          value={`${(stats?.conversion_rate || 0).toFixed(1)}%`}
          icon={<Package className="text-purple-600" />}
        />
        <StatCard
          title="Panier Moyen"
          value={formatCurrency((stats?.total_revenue || 0) / (stats?.total_conversions || 1))}
          icon={<DollarSign className="text-yellow-600" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Répartition par Catégorie */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Package size={20} className="text-indigo-600" />
            Répartition par Catégorie
          </h3>
          {loading ? (
            <div className="h-[400px] flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : categoryData.length === 0 ? (
            <div className="h-[400px] flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Top Produits */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp size={20} className="text-green-600" />
            Top 10 Produits
          </h3>
          {loading ? (
            <div className="h-[400px] flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : topProducts.length === 0 ? (
            <div className="h-[400px] flex items-center justify-center text-gray-500">
              Aucun produit
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={topProducts} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Bar dataKey="revenue" fill="#10b981" name="Revenu" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Top Influenceurs Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Users size={20} className="text-pink-600" />
          Top 10 Influenceurs
        </h3>
        {loading ? (
          <div className="py-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : topInfluencers.length === 0 ? (
          <p className="text-center text-gray-500 py-8">Aucun influenceur</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rang</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Influenceur</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gains</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Clics</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taux Conv.</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topInfluencers.map((influencer, index) => (
                  <tr key={influencer.id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {influencer.name || influencer.username || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                      {formatCurrency(influencer.total_earnings || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(influencer.total_clicks || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(influencer.total_conversions || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {((influencer.total_conversions || 0) / (influencer.total_clicks || 1) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between mb-2">
      <p className="text-sm text-gray-600">{title}</p>
      {icon}
    </div>
    <p className="text-2xl font-bold text-gray-900">{value}</p>
  </div>
);

export default AnalyticsTab;
