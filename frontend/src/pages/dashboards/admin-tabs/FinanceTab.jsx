import React, { useEffect, useState, useCallback } from 'react';
import CountUp from 'react-countup';
import { DollarSign, Sparkles, Clock, TrendingUp, ArrowUpRight, Download } from 'lucide-react';
import { formatCurrency, formatDate, exportToCSV } from '../../../utils/helpers';
import api from '../../../utils/api';
import { useToast } from '../../../context/ToastContext';

const FinanceTab = ({ stats, dateFilter, refreshKey }) => {
  const toast = useToast();
  const [transactions, setTransactions] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFinanceData = useCallback(async (signal) => {
    try {
      setLoading(true);
      const [transactionsRes, payoutsRes] = await Promise.allSettled([
        api.get(`/api/transactions/history?period=${dateFilter}&limit=50`, { signal }),
        api.get(`/api/admin/payouts?status=pending&limit=20`, { signal })
      ]);

      if (transactionsRes.status === 'fulfilled') {
        setTransactions(transactionsRes.value.data.transactions || transactionsRes.value.data || []);
      }
      if (payoutsRes.status === 'fulfilled') {
        setPayouts(payoutsRes.value.data.payouts || payoutsRes.value.data || []);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement finances:', error);
        toast.error('Impossible de charger les données financières');
      }
    } finally {
      setLoading(false);
    }
  }, [dateFilter, toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchFinanceData(controller.signal);
    return () => controller.abort();
  }, [fetchFinanceData, refreshKey]);

  return (
    <div className="space-y-6">
      {/* KPI Cards Financiers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Revenu Total</p>
            <DollarSign className="text-green-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={stats?.total_revenue || 0} duration={2} separator=" " suffix=" €" />
          </p>
          {stats?.revenue_growth !== undefined && (
            <div className="flex items-center gap-1 text-sm text-green-600 mt-2">
              <ArrowUpRight size={16} />
              <span>{Math.abs(stats.revenue_growth).toFixed(1)}% vs mois dernier</span>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Commission Plateforme</p>
            <Sparkles className="text-yellow-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={stats?.platform_commission || 0} duration={2} separator=" " suffix=" €" />
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Paiements en Attente</p>
            <Clock className="text-orange-600" size={32} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            <CountUp end={stats?.pending_payouts || 0} duration={2} separator=" " suffix=" €" />
          </p>
          <p className="text-sm text-gray-500 mt-2">{payouts.length} demande(s)</p>
        </div>
      </div>

      {/* Paiements en Attente */}
      {payouts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Clock size={20} className="text-orange-600" />
              Demandes de Paiement en Attente ({payouts.length})
            </h3>
            <button
              onClick={() => exportToCSV(payouts, 'paiements_en_attente')}
              className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              <Download size={16} />
              Exporter
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilisateur</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Méthode</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date demande</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {payouts.map((payout) => (
                  <tr key={payout.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {payout.user_email || payout.user_name || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(payout.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {payout.method || 'Virement'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(payout.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        En attente
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Transactions Récentes */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <TrendingUp size={20} className="text-green-600" />
            Transactions Récentes ({transactions.length})
          </h3>
          <button
            onClick={() => exportToCSV(transactions, 'transactions')}
            className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            <Download size={16} />
            Exporter
          </button>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="py-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : transactions.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucune transaction</p>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Utilisateur</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.slice(0, 20).map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(transaction.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.type || 'Commission'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.user_email || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                      {formatCurrency(transaction.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        transaction.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : transaction.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {transaction.status === 'completed' ? 'Complété' : transaction.status === 'pending' ? 'En attente' : 'Échoué'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinanceTab;
