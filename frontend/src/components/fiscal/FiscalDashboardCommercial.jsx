import React from 'react';
import { BarChart3, FileText } from 'lucide-react';
import TaxDashboard from '../../pages/fiscal/TaxDashboard';

/**
 * Dashboard Fiscal – Vue Commercial
 * Commissions commerciales, TVA et obligations fiscales rôle commercial
 */
const FiscalDashboardCommercial = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-orange-600 to-amber-600 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <BarChart3 size={48} />
          <div>
            <h1 className="text-3xl font-bold">Tableau de bord fiscal – Commercial</h1>
            <p className="text-orange-100 mt-1">Commissions, frais, TVA et déclarations pour les commerciaux</p>
          </div>
        </div>
      </div>
      <TaxDashboard role="commercial" />
    </div>
  );
};

export default FiscalDashboardCommercial;
