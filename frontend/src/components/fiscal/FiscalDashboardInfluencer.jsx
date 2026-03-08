import React from 'react';
import { TrendingUp, FileText } from 'lucide-react';
import TaxDashboard from '../../pages/fiscal/TaxDashboard';

/**
 * Dashboard Fiscal – Vue Influenceur
 * Commissions reçues, retenues à la source et déclarations revenus
 */
const FiscalDashboardInfluencer = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <TrendingUp size={48} />
          <div>
            <h1 className="text-3xl font-bold">Tableau de bord fiscal – Influenceur</h1>
            <p className="text-purple-100 mt-1">Revenus de commissions, retenues et déclarations fiscales</p>
          </div>
        </div>
      </div>
      <TaxDashboard role="influencer" />
    </div>
  );
};

export default FiscalDashboardInfluencer;
