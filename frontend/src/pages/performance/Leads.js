import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatDate, formatCurrency } from '../../utils/helpers';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Target, 
  Filter, 
  Download,
  Search,
  Calendar,
  CheckCircle,
  Clock,
  XCircle,
  Inbox,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, Tooltip, PieChart, Pie, Cell } from 'recharts';

const Leads = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [animatedValues, setAnimatedValues] = useState({
    total: 0,
    pending: 0,
    validated: 0,
    rejected: 0
  });
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [period, setPeriod] = useState('week');

  // Fonction d'export
  const handleExport = async () => {
    try {
      toast.info('Préparation de l\'export...');
      const csvContent = leads.map(lead => 
        `${lead.name || ''},${lead.email || ''},${lead.status || ''},${lead.amount || 0},${formatDate(lead.created_at)}`
      ).join('\n');
      const header = 'Nom,Email,Statut,Montant,Date\n';
      const blob = new Blob([header + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `leads_export_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      toast.success('Export réussi !');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  // Animation des compteurs
  useEffect(() => {
    if (!loading && leads.length > 0) {
      const stats = calculateStats();
      animateValue(0, stats.total, 1500, 'total');
      animateValue(0, stats.pending, 1200, 'pending');
      animateValue(0, stats.validated, 1300, 'validated');
      animateValue(0, stats.rejected, 1400, 'rejected');
    }
  }, [loading, leads]);

  const animateValue = (start, end, duration, key) => {
    const startTime = Date.now();
    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const value = start + (end - start) * progress;
      setAnimatedValues(prev => ({ ...prev, [key]: Math.floor(value) }));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  };

  const fetchLeads = async () => {
    try {
      const response = await api.get('/api/leads');
      setLeads(response.data.data || []);
    } catch (error) {
      console.error('Error fetching leads:', error);
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    return {
      total: leads.length,
      pending: leads.filter(l => l.status === 'pending').length,
      validated: leads.filter(l => l.status === 'validated').length,
      rejected: leads.filter(l => l.status === 'rejected').length,
      totalAmount: leads.reduce((sum, l) => sum + (l.amount || 0), 0),
      totalCommission: leads.reduce((sum, l) => sum + (l.commission || 0), 0)
    };
  };

  const getFilteredLeads = () => {
    return leads.filter(lead => {
      const matchesStatus = filterStatus === 'all' || lead.status === filterStatus;
      const matchesSearch = !searchTerm || 
        lead.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.campaign?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.affiliate?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  };

  // Données pour le graphique d'évolution
  const evolutionData = [
    { name: 'Lun', leads: 12 },
    { name: 'Mar', leads: 19 },
    { name: 'Mer', leads: 15 },
    { name: 'Jeu', leads: 25 },
    { name: 'Ven', leads: 22 },
    { name: 'Sam', leads: 18 },
    { name: 'Dim', leads: 16 }
  ];

  // Données pour le graphique en camembert
  const stats = calculateStats();
  const distributionData = [
    { name: 'En attente', value: stats.pending, color: '#f59e0b' },
    { name: 'Validés', value: stats.validated, color: '#10b981' },
    { name: 'Rejetés', value: stats.rejected, color: '#ef4444' }
  ];

  const columns = [
    {
      header: 'ID',
      accessor: 'id',
      render: (row) => <span className="font-mono text-sm text-gray-600">{row.id.substring(0, 8)}...</span>,
    },
    {
      header: 'Contact',
      accessor: 'email',
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{row.email}</span>
          <span className="text-xs text-gray-500">{row.affiliate || 'N/A'}</span>
        </div>
      )
    },
    {
      header: 'Campagne',
      accessor: 'campaign',
      render: (row) => (
        <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm">
          {row.campaign || 'N/A'}
        </span>
      )
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-semibold text-gray-900">{formatCurrency(row.amount)}</span>
          <span className="text-xs text-green-600">+{formatCurrency(row.commission)} commission</span>
        </div>
      )
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => {
        const statusConfig = {
          pending: { icon: Clock, color: 'yellow', label: 'En attente' },
          validated: { icon: CheckCircle, color: 'green', label: 'Validé' },
          rejected: { icon: XCircle, color: 'red', label: 'Rejeté' }
        };
        const config = statusConfig[row.status] || statusConfig.pending;
        const Icon = config.icon;
        return (
          <div className="flex items-center gap-2">
            <Icon className={`h-4 w-4 text-${config.color}-500`} />
            <Badge status={row.status}>{config.label}</Badge>
          </div>
        );
      }
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => (
        <div className="flex items-center gap-1 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          {formatDate(row.created_at)}
        </div>
      )
    }
  ];

  const filteredLeads = getFilteredLeads();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="leads">
      {/* En-tête */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Target className="h-8 w-8 text-blue-600" />
            Leads & Conversions
          </h1>
          <p className="text-gray-600 mt-2">
            Suivi et analyse de vos leads générés
          </p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-300 hover:bg-gray-50'}`}
          >
            <Filter className="h-4 w-4" />
            Filtres
          </button>
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            Exporter
          </button>
        </div>
      </div>

      {/* KPIs avec animations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Leads */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Leads</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.total}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Target className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <ArrowUpRight className="h-4 w-4" />
            <span>+12.5% ce mois</span>
          </div>
        </div>

        {/* En attente */}
        <div className="bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-amber-100 text-sm font-medium">En attente</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.pending}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Clock className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <span>À traiter rapidement</span>
          </div>
        </div>

        {/* Validés */}
        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-emerald-100 text-sm font-medium">Validés</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.validated}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <CheckCircle className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <ArrowUpRight className="h-4 w-4" />
            <span>{stats.validated > 0 ? Math.round((stats.validated / stats.total) * 100) : 0}% taux validation</span>
          </div>
        </div>

        {/* Rejetés */}
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div>
              <p className="text-red-100 text-sm font-medium">Rejetés</p>
              <p className="text-3xl font-bold mt-2">{animatedValues.rejected}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <XCircle className="h-6 w-6" />
            </div>
          </div>
          <div className="flex items-center gap-1 text-sm">
            <ArrowDownRight className="h-4 w-4" />
            <span>{stats.rejected > 0 ? Math.round((stats.rejected / stats.total) * 100) : 0}% taux rejet</span>
          </div>
        </div>
      </div>

      {/* Graphiques */}
      {leads.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Évolution */}
          <Card className="lg:col-span-2">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Évolution des leads
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={evolutionData}>
                <defs>
                  <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Tooltip />
                <Area type="monotone" dataKey="leads" stroke="#3b82f6" fillOpacity={1} fill="url(#colorLeads)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Distribution */}
          <Card>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              Distribution
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {distributionData.map((item, index) => (
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

      {/* Barre de recherche et filtres */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par email, campagne, affilié..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            {['all', 'pending', 'validated', 'rejected'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? 'Tous' : status === 'pending' ? 'En attente' : status === 'validated' ? 'Validés' : 'Rejetés'}
              </button>
            ))}
          </div>
        </div>

        {/* Table ou État vide */}
        {filteredLeads.length > 0 ? (
          <div className="overflow-x-auto">
            <Table columns={columns} data={filteredLeads} />
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-4">
              <Inbox className="h-10 w-10 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {leads.length === 0 ? 'Aucun lead généré' : 'Aucun résultat'}
            </h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              {leads.length === 0 
                ? "Les leads générés par vos campagnes apparaîtront ici. Commencez par créer une campagne et partager vos liens d'affiliation."
                : 'Aucun lead ne correspond aux critères de recherche. Essayez de modifier vos filtres.'}
            </p>
            {leads.length === 0 && (
              <button 
                onClick={() => navigate('/campaigns/create')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto"
              >
                <Target className="h-5 w-5" />
                Créer une campagne
              </button>
            )}
          </div>
        )}
      </Card>

      {/* Footer Stats */}
      {leads.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-purple-50 to-pink-50">
            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-3 rounded-lg">
                <DollarSign className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Montant total</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalAmount)}</p>
              </div>
            </div>
          </Card>
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
            <div className="flex items-center gap-3">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Commissions totales</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalCommission)}</p>
              </div>
            </div>
          </Card>
          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Taux de conversion</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.total > 0 ? Math.round((stats.validated / stats.total) * 100) : 0}%
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Leads;
