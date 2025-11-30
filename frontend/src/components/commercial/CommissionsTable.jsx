import React, { useEffect, useState } from 'react';
import Card from '../common/Card';
import { DollarSign, Clock, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';

const CommissionsTable = () => {
  const [commissions, setCommissions] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommissions();
  }, []);

  const fetchCommissions = async () => {
    try {
      const response = await axios.get('/api/commercial/commissions');
      
      if (response.data.success) {
        setCommissions(response.data.data.commissions);
        setSummary(response.data.data.summary);
      }
    } catch (error) {
      console.error('Error fetching commissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: 'En attente' },
      approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Approuvée' },
      paid: { color: 'bg-blue-100 text-blue-800', icon: DollarSign, label: 'Payée' },
      cancelled: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Annulée' }
    };

    const config = variants[status] || variants.pending;
    const Icon = config.icon;

    return (
      <span className={`flex items-center gap-1 w-fit px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  if (loading) {
    return <div className="p-4 text-center">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Résumé commissions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-500">En attente</div>
          <div className="text-2xl font-bold text-yellow-600">
            {summary.total_pending?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {summary.count_pending || 0} ventes
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-gray-500">Approuvées</div>
          <div className="text-2xl font-bold text-green-600">
            {summary.total_approved?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {summary.count_approved || 0} ventes
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-gray-500">Payées</div>
          <div className="text-2xl font-bold text-blue-600">
            {summary.total_paid?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {summary.count_paid || 0} ventes
          </div>
        </Card>
      </div>

      {/* Table commissions */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4">Historique des commissions</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3">Client</th>
                <th className="px-6 py-3 text-right">Montant vente</th>
                <th className="px-6 py-3 text-right">Taux</th>
                <th className="px-6 py-3 text-right">Commission</th>
                <th className="px-6 py-3">Statut</th>
                <th className="px-6 py-3">Attribution</th>
              </tr>
            </thead>
            <tbody>
              {commissions.map((commission) => (
                <tr key={commission.id} className="bg-white border-b hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {new Date(commission.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4">{commission.user_email}</td>
                  <td className="px-6 py-4 text-right">
                    {commission.subscription_amount.toFixed(2)} €
                  </td>
                  <td className="px-6 py-4 text-right">
                    {commission.commission_percentage}%
                  </td>
                  <td className="px-6 py-4 text-right font-semibold">
                    {commission.commission_amount.toFixed(2)} €
                  </td>
                  <td className="px-6 py-4">
                    {getStatusBadge(commission.status)}
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">
                    {commission.attribution_type}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {commissions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Aucune commission enregistrée
          </div>
        )}
      </Card>
    </div>
  );
};

export default CommissionsTable;
