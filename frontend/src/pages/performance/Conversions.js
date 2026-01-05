import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { 
  Download, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart, 
  Clock,
  Filter,
  Search,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import Button from '../../components/common/Button';
import './Conversions.css';

const Conversions = () => {
  const [conversions, setConversions] = useState([]);
  const [filteredConversions, setFilteredConversions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    validated: 0,
    paid: 0,
    refunded: 0,
    totalRevenue: 0,
    totalCommissions: 0,
    conversionRate: 0
  });

  useEffect(() => {
    fetchConversions();
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(fetchConversions, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterConversions();
  }, [conversions, searchTerm, statusFilter]);

  const fetchConversions = async () => {
    try {
      const response = await api.get('/api/conversions');
      const data = response.data.data || [];
      setConversions(data);
      calculateStats(data);
    } catch (error) {
      console.error('Error fetching conversions:', error);
      setConversions([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data) => {
    const pending = data.filter(c => c.status === 'pending').length;
    const validated = data.filter(c => c.status === 'validated').length;
    const paid = data.filter(c => c.status === 'paid').length;
    const refunded = data.filter(c => c.status === 'refunded').length;
    
    const totalRevenue = data.reduce((sum, c) => sum + (c.amount || 0), 0);
    const totalCommissions = data.reduce((sum, c) => sum + (c.commission || 0), 0);
    
    setStats({
      total: data.length,
      pending,
      validated,
      paid,
      refunded,
      totalRevenue,
      totalCommissions,
      conversionRate: data.length > 0 ? ((validated + paid) / data.length * 100).toFixed(1) : 0
    });
  };

  const filterConversions = () => {
    let filtered = [...conversions];

    // Filtre par statut
    if (statusFilter !== 'all') {
      filtered = filtered.filter(c => c.status === statusFilter);
    }

    // Filtre par recherche
    if (searchTerm) {
      filtered = filtered.filter(c => 
        c.order_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.campaign_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.affiliate_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredConversions(filtered);
  };

  const exportToCSV = () => {
    const headers = ['ID Commande', 'Campagne', 'Affilié', 'Montant', 'Commission', 'Statut', 'Date'];
    const rows = filteredConversions.map(c => [
      c.order_id,
      c.campaign_id,
      c.affiliate_id,
      c.amount,
      c.commission,
      c.status,
      formatDate(c.created_at)
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversions_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'paid':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'validated':
        return <CheckCircle className="w-4 h-4 text-blue-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'refunded':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'paid':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'validated':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'refunded':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const columns = [
    {
      header: 'ID Commande',
      accessor: 'order_id',
      render: (row) => (
        <div className="flex items-center space-x-2">
          <ShoppingCart className="w-4 h-4 text-gray-400" />
          <span className="font-mono text-sm font-semibold text-gray-900">{row.order_id}</span>
        </div>
      ),
    },
    {
      header: 'Campagne',
      accessor: 'campaign_id',
      render: (row) => (
        <span className="text-sm text-gray-700">{row.campaign_id || 'N/A'}</span>
      ),
    },
    {
      header: 'Affilié',
      accessor: 'affiliate_id',
      render: (row) => (
        <span className="text-sm text-gray-700">{row.affiliate_id || 'N/A'}</span>
      ),
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => (
        <span className="font-semibold text-gray-900">{formatCurrency(row.amount, 'MAD')}</span>
      ),
    },
    {
      header: 'Commission',
      accessor: 'commission',
      render: (row) => (
        <span className="font-semibold text-green-600">{formatCurrency(row.commission, 'MAD')}</span>
      ),
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => (
        <div className="flex items-center space-x-2">
          {getStatusIcon(row.status)}
          <span className={`status-badge px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(row.status)} ${row.status === 'pending' ? 'badge-pulse' : ''}`}>
            {row.status === 'pending' ? 'En attente' : 
             row.status === 'validated' ? 'Validée' : 
             row.status === 'paid' ? 'Payée' : 
             row.status === 'refunded' ? 'Remboursée' : row.status}
          </span>
        </div>
      ),
    },
    {
      header: 'Date',
      accessor: 'created_at',
      render: (row) => (
        <span className="text-sm text-gray-600">{formatDate(row.created_at)}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="conversions">
      {/* Header avec actions */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">💰 Conversions</h1>
          <p className="text-gray-600 mt-2">Suivez toutes vos conversions en temps réel</p>
        </div>
        <div className="flex space-x-3">
          <Button 
            variant="outline" 
            onClick={fetchConversions}
            disabled={loading}
          >
            <RefreshCw size={20} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          <Button 
            variant="outline"
            onClick={exportToCSV}
            disabled={filteredConversions.length === 0}
          >
            <Download size={20} className="mr-2" />
            Exporter CSV
          </Button>
        </div>
      </div>

      {/* Statistiques en cartes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="stat-card conversion-card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600">Total Conversions</p>
              <p className="text-3xl font-bold text-blue-900 mt-2">{stats.total}</p>
              <p className="text-xs text-blue-600 mt-1">
                Taux: {stats.conversionRate}%
              </p>
            </div>
            <div className="bg-blue-500 rounded-full p-3">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
          </div>
        </Card>

        <Card className="stat-card conversion-card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600">Revenu Total</p>
              <p className="text-3xl font-bold text-green-900 mt-2 amount-glow">
                {formatCurrency(stats.totalRevenue, 'MAD')}
              </p>
            </div>
            <div className="bg-green-500 rounded-full p-3">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
          </div>
        </Card>

        <Card className="stat-card conversion-card bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600">Commissions</p>
              <p className="text-3xl font-bold text-purple-900 mt-2 amount-glow">
                {formatCurrency(stats.totalCommissions, 'MAD')}
              </p>
            </div>
            <div className="bg-purple-500 rounded-full p-3">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
          </div>
        </Card>

        <Card className="stat-card conversion-card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600">Statuts</p>
              <div className="flex space-x-2 mt-2">
                <div className="text-center">
                  <p className="text-lg font-bold text-orange-900">{stats.pending}</p>
                  <p className="text-xs text-orange-600">En attente</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-900">{stats.validated}</p>
                  <p className="text-xs text-blue-600">Validées</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-green-900">{stats.paid}</p>
                  <p className="text-xs text-green-600">Payées</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Filtres et recherche */}
      <Card className="conversion-card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par ID commande, campagne ou affilié..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-focus filter-transition w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="text-gray-400 w-5 h-5" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-transition px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Tous les statuts</option>
              <option value="pending">En attente</option>
              <option value="validated">Validées</option>
              <option value="paid">Payées</option>
              <option value="refunded">Remboursées</option>
            </select>
          </div>
        </div>

        {/* Résultats du filtre */}
        {(searchTerm || statusFilter !== 'all') && (
          <div className="mt-4 text-sm text-gray-600">
            {filteredConversions.length} conversion{filteredConversions.length > 1 ? 's' : ''} trouvée{filteredConversions.length > 1 ? 's' : ''}
            {searchTerm && ` pour "${searchTerm}"`}
            {statusFilter !== 'all' && ` avec le statut "${statusFilter}"`}
          </div>
        )}
      </Card>

      {/* Table des conversions */}
      <Card>
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Chargement des conversions...</p>
          </div>
        ) : filteredConversions.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-xl font-semibold text-gray-900 mb-2">Aucune conversion trouvée</p>
            <p className="text-gray-600">
              {searchTerm || statusFilter !== 'all' 
                ? 'Essayez de modifier vos filtres' 
                : 'Les conversions apparaîtront ici dès qu\'elles seront générées'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table columns={columns} data={filteredConversions} />
          </div>
        )}
      </Card>

      {/* Footer avec totaux */}
      {filteredConversions.length > 0 && (
        <Card className="bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Affichage de <span className="font-semibold text-gray-900">{filteredConversions.length}</span> conversion{filteredConversions.length > 1 ? 's' : ''}
            </div>
            <div className="flex space-x-8">
              <div className="text-right">
                <p className="text-xs text-gray-600">Revenu total filtré</p>
                <p className="text-lg font-bold text-gray-900">
                  {formatCurrency(filteredConversions.reduce((sum, c) => sum + (c.amount || 0), 0), 'MAD')}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-600">Commissions totales</p>
                <p className="text-lg font-bold text-green-600">
                  {formatCurrency(filteredConversions.reduce((sum, c) => sum + (c.commission || 0), 0), 'MAD')}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Conversions;
