import React, { useState, useEffect, useCallback } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  Users, 
  Download, 
  Search, 
  Eye,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Filter,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import api from '../../services/api';

const BalanceReport = () => {
  // États
  const [summary, setSummary] = useState(null);
  const [affiliates, setAffiliates] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtres
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [search, setSearch] = useState('');
  const [minBalance, setMinBalance] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [period, setPeriod] = useState('month');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Vue détaillée
  const [affiliateDetails, setAffiliateDetails] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Charger les données
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      // Charger résumé
      const summaryRes = await api.get(`/api/balance-report/summary?${params}`);
      if (summaryRes.data?.success) {
        setSummary(summaryRes.data.data);
      }
      
      // Charger statistiques
      const statsRes = await api.get(`/api/balance-report/statistics?period=${period}`);
      if (statsRes.data?.success) {
        setStatistics(statsRes.data.data);
      }
      
      // Charger affiliés
      const affParams = new URLSearchParams(params);
      affParams.append('page', page);
      affParams.append('limit', '10');
      if (search) affParams.append('search', search);
      if (minBalance) affParams.append('min_balance', minBalance);
      if (statusFilter) affParams.append('status', statusFilter);
      
      const affRes = await api.get(`/api/balance-report/affiliates?${affParams}`);
      if (affRes.data?.success) {
        setAffiliates(affRes.data.data);
        setTotalPages(affRes.data.pagination?.total_pages || 1);
        setTotal(affRes.data.pagination?.total || 0);
      }
      
    } catch (err) {
      console.error('Erreur chargement données:', err);
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, search, minBalance, statusFilter, period, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Charger détails affilié
  const loadAffiliateDetails = async (affiliateId) => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const res = await api.get(`/api/balance-report/affiliate/${affiliateId}?${params}`);
      if (res.data?.success) {
        setAffiliateDetails(res.data.data);
        setShowDetails(true);
      }
    } catch (err) {
      console.error('Erreur chargement détails:', err);
    }
  };

  // Export
  const handleExport = async (format) => {
    try {
      const params = new URLSearchParams();
      params.append('format', format);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const res = await api.get(`/api/balance-report/export?${params}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `balance_report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Erreur export:', err);
    }
  };

  // Formater montant
  const formatAmount = (amount, currency = '€') => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency === '€' ? 'EUR' : currency === '$' ? 'USD' : 'MAD'
    }).format(amount || 0);
  };

  // Formater date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6" data-testid="balance-report">
      {/* En-tête */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rapport de Solde</h1>
          <p className="text-gray-600 mt-1">Vue d'ensemble des soldes affiliés</p>
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={loadData}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            Actualiser
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
          >
            <Download size={18} />
            CSV
          </button>
          <button
            onClick={() => handleExport('json')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Download size={18} />
            JSON
          </button>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={18} className="text-gray-500" />
          <span className="font-medium text-gray-700">Filtres</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Date début</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Date fin</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Recherche</label>
            <div className="relative">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Nom ou email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Solde min</label>
            <input
              type="number"
              placeholder="0"
              value={minBalance}
              onChange={(e) => setMinBalance(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Statut</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous</option>
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
              <option value="pending">En attente</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Cards statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Solde Total</p>
              <p className="text-3xl font-bold mt-1">{formatAmount(summary?.total_balance)}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <DollarSign size={28} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-blue-100 text-sm">
            <ArrowUpRight size={16} />
            <span className="ml-1">Commissions: {formatAmount(summary?.total_commissions)}</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Paiements en Attente</p>
              <p className="text-3xl font-bold mt-1">{formatAmount(summary?.pending_payouts)}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Clock size={28} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-yellow-100 text-sm">
            <TrendingUp size={16} />
            <span className="ml-1">À traiter</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Paiements Effectués</p>
              <p className="text-3xl font-bold mt-1">{formatAmount(summary?.paid_payouts)}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <CheckCircle size={28} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-green-100 text-sm">
            <ArrowDownRight size={16} />
            <span className="ml-1">Versés aux affiliés</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Affiliés avec Solde</p>
              <p className="text-3xl font-bold mt-1">{summary?.affiliates_with_balance || 0}</p>
            </div>
            <div className="bg-white/20 p-3 rounded-lg">
              <Users size={28} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-purple-100 text-sm">
            <Users size={16} />
            <span className="ml-1">Sur {summary?.total_affiliates || 0} affiliés</span>
          </div>
        </div>
      </div>

      {/* Graphique */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <BarChart3 size={20} className="text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Évolution</h2>
          </div>
          <div className="flex gap-2">
            {['day', 'week', 'month', 'year'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1 rounded-lg text-sm transition ${
                  period === p 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {p === 'day' ? '7J' : p === 'week' ? '4S' : p === 'month' ? '30J' : '1A'}
              </button>
            ))}
          </div>
        </div>
        
        {statistics?.chart_data && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.chart_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                tickFormatter={(val) => {
                  const d = new Date(val);
                  return period === 'year' ? d.toLocaleDateString('fr-FR', { month: 'short' }) : d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
                }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value) => formatAmount(value)}
                labelFormatter={(val) => new Date(val).toLocaleDateString('fr-FR')}
              />
              <Legend />
              <Bar dataKey="commissions" name="Commissions" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="payouts" name="Paiements" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Tableau des affiliés */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="p-4 border-b bg-gray-50">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Détails par Affilié ({total})
            </h2>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Affilié</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Solde</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Total Gagné</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">En Attente</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Payé</th>
                <th className="text-center px-6 py-3 text-xs font-medium text-gray-500 uppercase">Dernier Paiement</th>
                <th className="text-center px-6 py-3 text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th className="text-center px-6 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {affiliates.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-12 text-gray-500">
                    Aucun affilié trouvé
                  </td>
                </tr>
              ) : (
                affiliates.map((affiliate) => (
                  <tr key={affiliate.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{affiliate.name}</p>
                        <p className="text-sm text-gray-500">{affiliate.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`font-semibold ${affiliate.balance > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                        {formatAmount(affiliate.balance)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right text-gray-700">
                      {formatAmount(affiliate.total_earned)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={affiliate.pending > 0 ? 'text-yellow-600' : 'text-gray-400'}>
                        {formatAmount(affiliate.pending)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right text-green-600">
                      {formatAmount(affiliate.paid)}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-gray-500">
                      {formatDate(affiliate.last_payout)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        affiliate.status === 'active' 
                          ? 'bg-green-100 text-green-700' 
                          : affiliate.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {affiliate.status === 'active' ? 'Actif' : affiliate.status === 'pending' ? 'En attente' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => loadAffiliateDetails(affiliate.id)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                        title="Voir les détails"
                      >
                        <Eye size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600">
            Page {page} sur {totalPages} ({total} affiliés)
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center gap-1 px-3 py-1 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition"
            >
              <ChevronLeft size={16} />
              Précédent
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="flex items-center gap-1 px-3 py-1 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 transition"
            >
              Suivant
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Modal Détails Affilié */}
      {showDetails && affiliateDetails && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{affiliateDetails.affiliate?.name}</h2>
                <p className="text-gray-500">{affiliateDetails.affiliate?.email}</p>
              </div>
              <button
                onClick={() => setShowDetails(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Stats affilié */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 rounded-xl p-4">
                  <p className="text-sm text-blue-600">Solde Actuel</p>
                  <p className="text-2xl font-bold text-blue-700">{formatAmount(affiliateDetails.balance?.current_balance)}</p>
                </div>
                <div className="bg-green-50 rounded-xl p-4">
                  <p className="text-sm text-green-600">Total Gagné</p>
                  <p className="text-2xl font-bold text-green-700">{formatAmount(affiliateDetails.balance?.total_earned)}</p>
                </div>
                <div className="bg-yellow-50 rounded-xl p-4">
                  <p className="text-sm text-yellow-600">En Attente</p>
                  <p className="text-2xl font-bold text-yellow-700">{formatAmount(affiliateDetails.balance?.pending)}</p>
                </div>
                <div className="bg-purple-50 rounded-xl p-4">
                  <p className="text-sm text-purple-600">Total Payé</p>
                  <p className="text-2xl font-bold text-purple-700">{formatAmount(affiliateDetails.balance?.total_paid)}</p>
                </div>
              </div>

              {/* Graphique historique */}
              {affiliateDetails.monthly_history && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">Historique Mensuel</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={affiliateDetails.monthly_history.slice().reverse()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip formatter={(value) => formatAmount(value)} />
                      <Legend />
                      <Line type="monotone" dataKey="earned" name="Gagné" stroke="#3B82F6" strokeWidth={2} />
                      <Line type="monotone" dataKey="paid" name="Payé" stroke="#10B981" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Dernières commissions */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Dernières Commissions</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Date</th>
                        <th className="text-right px-4 py-2 text-xs font-medium text-gray-500">Montant</th>
                        <th className="text-center px-4 py-2 text-xs font-medium text-gray-500">Statut</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {(affiliateDetails.commissions || []).slice(0, 10).map((comm, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-2 text-sm">{formatDate(comm.created_at)}</td>
                          <td className="px-4 py-2 text-sm text-right font-medium">{formatAmount(comm.amount)}</td>
                          <td className="px-4 py-2 text-center">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              comm.status === 'approved' ? 'bg-green-100 text-green-700' :
                              comm.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {comm.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {(!affiliateDetails.commissions || affiliateDetails.commissions.length === 0) && (
                        <tr>
                          <td colSpan="3" className="px-4 py-4 text-center text-gray-500">
                            Aucune commission
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Derniers paiements */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Derniers Paiements</h3>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-2 text-xs font-medium text-gray-500">Date</th>
                        <th className="text-right px-4 py-2 text-xs font-medium text-gray-500">Montant</th>
                        <th className="text-center px-4 py-2 text-xs font-medium text-gray-500">Statut</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {(affiliateDetails.payouts || []).slice(0, 10).map((payout, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-2 text-sm">{formatDate(payout.paid_at || payout.created_at)}</td>
                          <td className="px-4 py-2 text-sm text-right font-medium">{formatAmount(payout.amount)}</td>
                          <td className="px-4 py-2 text-center">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              payout.status === 'paid' || payout.status === 'completed' ? 'bg-green-100 text-green-700' :
                              payout.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                              payout.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {payout.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {(!affiliateDetails.payouts || affiliateDetails.payouts.length === 0) && (
                        <tr>
                          <td colSpan="3" className="px-4 py-4 text-center text-gray-500">
                            Aucun paiement
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BalanceReport;
