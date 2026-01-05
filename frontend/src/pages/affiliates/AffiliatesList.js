import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import InvitationModal from '../../components/modals/InvitationModal';
import { formatCurrency, formatNumber, formatDate } from '../../utils/helpers';
import { 
  Plus, 
  Search, 
  Users, 
  TrendingUp, 
  DollarSign, 
  MousePointer,
  Target,
  Award,
  Filter,
  Download,
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Globe,
  Flag,
  Star,
  Zap
} from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const AffiliatesList = () => {
  const [affiliates, setAffiliates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCountry, setFilterCountry] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [animatedValues, setAnimatedValues] = useState({
    total: 0,
    active: 0,
    totalClicks: 0,
    totalRevenue: 0
  });
  const [hoveredCard, setHoveredCard] = useState(null);

  useEffect(() => {
    fetchAffiliates();
  }, []);

  // Animation des compteurs
  useEffect(() => {
    if (!loading && affiliates.length > 0) {
      const stats = calculateStats();
      animateValue(0, stats.total, 1500, 'total');
      animateValue(0, stats.active, 1200, 'active');
      animateValue(0, stats.totalClicks, 1800, 'totalClicks');
      animateValue(0, stats.totalRevenue, 2000, 'totalRevenue');
    }
  }, [loading, affiliates]);

  const animateValue = (start, end, duration, key) => {
    const startTime = Date.now();
    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const value = start + (end - start) * progress;
      setAnimatedValues(prev => ({ ...prev, [key]: key === 'totalRevenue' ? value : Math.floor(value) }));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  };

  const fetchAffiliates = async () => {
    try {
      const response = await api.get('/api/affiliates');
      setAffiliates(response.data.data || []);
    } catch (error) {
      console.error('Error fetching affiliates:', error);
      setAffiliates([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const active = affiliates.filter(a => a.status === 'active').length;
    const totalClicks = affiliates.reduce((sum, a) => sum + (parseInt(a.clicks) || 0), 0);
    const totalRevenue = affiliates.reduce((sum, a) => sum + (parseFloat(a.total_earned) || 0), 0);
    const avgConversion = totalClicks > 0 ? 
      (affiliates.reduce((sum, a) => sum + (parseInt(a.conversions) || 0), 0) / totalClicks * 100) : 0;

    return {
      total: affiliates.length,
      active,
      totalClicks,
      totalRevenue,
      avgConversion
    };
  };

  const filteredAffiliates = affiliates.filter(aff => {
    const search = searchTerm.toLowerCase();
    const matchesSearch = (
      (aff.first_name?.toLowerCase().includes(search) || false) ||
      (aff.last_name?.toLowerCase().includes(search) || false) ||
      (aff.email?.toLowerCase().includes(search) || false)
    );
    const matchesStatus = filterStatus === 'all' || aff.status === filterStatus;
    const matchesCountry = filterCountry === 'all' || aff.country === filterCountry;
    
    return matchesSearch && matchesStatus && matchesCountry;
  });

  // Données pour les graphiques
  const topPerformers = affiliates
    .sort((a, b) => (parseFloat(b.total_earned) || 0) - (parseFloat(a.total_earned) || 0))
    .slice(0, 5);

  const countryStats = affiliates.reduce((acc, aff) => {
    const country = aff.country || 'Autre';
    acc[country] = (acc[country] || 0) + 1;
    return acc;
  }, {});

  const countryData = Object.entries(countryStats).map(([name, value]) => ({
    name,
    value,
    color: name === 'Maroc' ? '#10b981' : name === 'France' ? '#3b82f6' : '#f59e0b'
  }));

  const performanceData = topPerformers.map(aff => ({
    name: aff.first_name,
    revenue: parseFloat(aff.total_earned) || 0,
    clicks: parseInt(aff.clicks) || 0
  }));

  const stats = calculateStats();
  const uniqueCountries = [...new Set(affiliates.map(a => a.country).filter(Boolean))];

  const columns = [
    {
      header: 'Affilié',
      accessor: 'name',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
            {row.first_name?.[0]}{row.last_name?.[0]}
          </div>
          <div>
            <div className="font-semibold text-gray-900">{row.first_name} {row.last_name}</div>
            <div className="text-xs text-gray-500">{row.email}</div>
          </div>
        </div>
      ),
    },
    {
      header: 'Pays',
      accessor: 'country',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Flag className="h-4 w-4 text-gray-400" />
          <span>{row.country || 'N/A'}</span>
        </div>
      )
    },
    {
      header: 'Source',
      accessor: 'traffic_source',
      render: (row) => row.traffic_source ? (
        <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-sm">
          {row.traffic_source}
        </span>
      ) : <span className="text-gray-400">N/A</span>
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.status === 'active' ? (
            <Zap className="h-4 w-4 text-green-500" />
          ) : null}
          <Badge status={row.status}>{row.status}</Badge>
        </div>
      )
    },
    {
      header: 'Clics',
      accessor: 'clicks',
      render: (row) => (
        <div className="flex items-center gap-2">
          <MousePointer className="h-4 w-4 text-blue-400" />
          <span className="font-semibold">{formatNumber(row.clicks)}</span>
        </div>
      )
    },
    {
      header: 'Conversions',
      accessor: 'conversions',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-green-400" />
          <span className="font-semibold">{formatNumber(row.conversions)}</span>
        </div>
      )
    },
    {
      header: 'Solde',
      accessor: 'balance',
      render: (row) => (
        <span className="text-orange-600 font-semibold">
          {formatCurrency(row.balance)}
        </span>
      )
    },
    {
      header: 'Total Gagné',
      accessor: 'total_earned',
      render: (row) => (
        <span className="text-green-600 font-bold text-lg">
          {formatCurrency(row.total_earned)}
        </span>
      )
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <Eye className="h-4 w-4 text-gray-600" />
        </button>
      )
    }
  ];

  const handleExport = () => {
    const headers = ['Prénom', 'Nom', 'Email', 'Pays', 'Statut', 'Clics', 'Conversions', 'Revenu Total'];
    const csvContent = [
      headers.join(','),
      ...affiliates.map(row => [
        `"${row.first_name || ''}"`,
        `"${row.last_name || ''}"`,
        `"${row.email || ''}"`,
        `"${row.country || ''}"`,
        `"${row.status || ''}"`,
        row.clicks || 0,
        row.conversions || 0,
        row.total_earned || 0
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `affiliates_export_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="affiliates-list">
      {/* En-tête */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-600" />
            Réseau d'Affiliés
          </h1>
          <p className="text-gray-600 mt-2">
            Gérez et développez votre réseau de partenaires
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline"
            onClick={handleExport}
          >
            <Download size={20} className="mr-2" />
            Exporter
          </Button>
          <Button onClick={() => setShowInviteModal(true)}>
            <Plus size={20} className="mr-2" />
            Inviter un Affilié
          </Button>
        </div>
      </div>

      {showInviteModal && (
        <InvitationModal
          onClose={() => setShowInviteModal(false)}
          onSent={() => {
            setShowInviteModal(false);
            fetchAffiliates();
          }}
        />
      )}

      {/* KPIs animés */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Affiliés */}
        <div 
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-all cursor-pointer"
          onMouseEnter={() => setHoveredCard('total')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Affiliés</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.total}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Users className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <ArrowUpRight className="h-4 w-4" />
            <span>{stats.active} actifs</span>
          </div>
        </div>

        {/* Affiliés Actifs */}
        <div 
          className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-all cursor-pointer"
          onMouseEnter={() => setHoveredCard('active')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-green-100 text-sm font-medium">Actifs</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.active}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Zap className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <span>{stats.total > 0 ? Math.round((stats.active / stats.total) * 100) : 0}% du réseau</span>
          </div>
        </div>

        {/* Total Clics */}
        <div 
          className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-all cursor-pointer"
          onMouseEnter={() => setHoveredCard('clicks')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total Clics</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.totalClicks.toLocaleString()}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <MousePointer className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <TrendingUp className="h-4 w-4" />
            <span>+15.3% ce mois</span>
          </div>
        </div>

        {/* Revenu Total */}
        <div 
          className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-all cursor-pointer"
          onMouseEnter={() => setHoveredCard('revenue')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-orange-100 text-sm font-medium">Revenu Total</p>
              <p className="text-3xl font-bold mt-2">{formatCurrency(animatedValues.totalRevenue)}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <DollarSign className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <ArrowUpRight className="h-4 w-4" />
            <span>+24.8% ce mois</span>
          </div>
        </div>
      </div>

      {/* Graphiques et Top Performers */}
      {affiliates.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Top 5 Performers */}
          <Card className="lg:col-span-2">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Award className="h-5 w-5 text-yellow-500" />
              Top 5 Performers
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={performanceData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'revenue' ? formatCurrency(value) : formatNumber(value),
                    name === 'revenue' ? 'Revenu' : 'Clics'
                  ]}
                />
                <Bar dataKey="revenue" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Distribution par Pays */}
          <Card>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-500" />
              Par Pays
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={countryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {countryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {countryData.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                    <span className="text-sm text-gray-600">{item.name}</span>
                  </div>
                  <span className="text-sm font-semibold">{item.value}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Filtres et recherche */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un affilié par nom ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="search-input"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="active">Actifs</option>
              <option value="pending">En attente</option>
              <option value="inactive">Inactifs</option>
            </select>
            <select
              value={filterCountry}
              onChange={(e) => setFilterCountry(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tous les pays</option>
              {uniqueCountries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        {filteredAffiliates.length > 0 ? (
          <div className="overflow-x-auto">
            <Table columns={columns} data={filteredAffiliates} />
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-4">
              <Users className="h-10 w-10 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {affiliates.length === 0 ? 'Aucun affilié' : 'Aucun résultat'}
            </h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              {affiliates.length === 0 
                ? "Commencez à développer votre réseau en invitant des affiliés. Ils généreront des ventes et des commissions pour vous."
                : 'Aucun affilié ne correspond aux critères de recherche. Essayez de modifier vos filtres.'}
            </p>
            {affiliates.length === 0 && (
              <Button onClick={() => setShowInviteModal(true)}>
                <Plus size={20} className="mr-2" />
                Inviter mon premier affilié
              </Button>
            )}
          </div>
        )}
      </Card>

      {/* Stats Footer */}
      {affiliates.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Target className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Taux de conversion moyen</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avgConversion.toFixed(2)}%</p>
              </div>
            </div>
          </Card>
          <Card className="bg-gradient-to-br from-purple-50 to-pink-50">
            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Star className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Meilleur performer</p>
                <p className="text-2xl font-bold text-gray-900">{topPerformers[0]?.first_name || 'N/A'}</p>
              </div>
            </div>
          </Card>
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
            <div className="flex items-center gap-3">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Croissance ce mois</p>
                <p className="text-2xl font-bold text-gray-900">+18.5%</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AffiliatesList;
