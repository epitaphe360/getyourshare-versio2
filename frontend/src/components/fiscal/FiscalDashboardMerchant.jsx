import React from 'react';
import { DollarSign, FileText, TrendingUp } from 'lucide-react';
import TaxDashboard from '../../pages/fiscal/TaxDashboard';
import InvoiceGenerator from '../../pages/fiscal/InvoiceGenerator';

/**
 * Dashboard Fiscal – Vue Marchand
 * Gestion des factures, TVA collectée et déclarations marchands
 */
const FiscalDashboardMerchant = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4">
          <DollarSign size={48} />
          <div>
            <h1 className="text-3xl font-bold">Tableau de bord fiscal – Marchand</h1>
            <p className="text-green-100 mt-1">Vos factures, TVA et obligations fiscales en un coup d'œil</p>
          </div>
        </div>
      </div>
      <TaxDashboard role="merchant" />
    </div>
  );
};

export default FiscalDashboardMerchant;
