import React from 'react';
import { BarChart3, TrendingUp, DollarSign, FileText } from 'lucide-react';
import TaxDashboard from '../../pages/fiscal/TaxDashboard';

/**
 * Dashboard Fiscal – Vue Administrateur
 * Accès à toutes les données fiscales de la plateforme
 */
const FiscalDashboardAdmin = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-700 to-indigo-700 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <BarChart3 size={48} />
          <div>
            <h1 className="text-3xl font-bold">Tableau de bord fiscal – Admin</h1>
            <p className="text-blue-200 mt-1">Supervision globale des taxes, TVA et déclarations (MA / FR / US)</p>
          </div>
        </div>
      </div>
      <TaxDashboard role="admin" />
    </div>
  );
};

export default FiscalDashboardAdmin;
