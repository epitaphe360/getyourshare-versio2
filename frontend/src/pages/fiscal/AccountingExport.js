import React, { useState } from 'react';
import { Download, FileSpreadsheet, FileText, Database } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../../utils/api';

const EXPORT_FORMATS = [
  { key: 'csv', label: 'CSV', icon: FileSpreadsheet, description: 'Compatible Excel / Google Sheets' },
  { key: 'json', label: 'JSON', icon: Database, description: 'Intégration API / ERP' },
  { key: 'pdf', label: 'PDF', icon: FileText, description: 'Rapport imprimable' },
];

const EXPORT_TYPES = [
  { key: 'invoices', label: 'Factures' },
  { key: 'transactions', label: 'Transactions' },
  { key: 'commissions', label: 'Commissions' },
  { key: 'vat_report', label: 'Rapport TVA' },
  { key: 'full_accounting', label: 'Comptabilité complète' },
];

/**
 * AccountingExport — Export comptable multi-format (CSV, JSON, PDF)
 */
const AccountingExport = () => {
  const [exportType, setExportType] = useState('invoices');
  const [format, setFormat] = useState('csv');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/fiscal/export', {
        params: { type: exportType, format, date_from: dateFrom, date_to: dateTo },
        responseType: format === 'pdf' ? 'blob' : 'text',
      });

      const blob = new Blob([response.data], {
        type: format === 'pdf' ? 'application/pdf'
          : format === 'csv' ? 'text/csv'
          : 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export_${exportType}_${new Date().toISOString().slice(0, 10)}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Export ${format.toUpperCase()} téléchargé avec succès`);
    } catch (error) {
      toast.error('Erreur lors de l\'export : ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-2xl p-8 text-white shadow-xl flex items-center gap-4">
        <Download size={48} />
        <div>
          <h1 className="text-3xl font-bold">Export Comptable</h1>
          <p className="text-gray-300 mt-1">Exportez vos données financières dans votre format préféré</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow p-6 space-y-5">
        {/* Type d'export */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Type de données</label>
          <div className="grid grid-cols-2 gap-2">
            {EXPORT_TYPES.map(t => (
              <button
                key={t.key}
                onClick={() => setExportType(t.key)}
                className={`py-2 px-3 rounded-lg text-sm font-medium transition ${
                  exportType === t.key ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Format d'export</label>
          <div className="grid grid-cols-3 gap-3">
            {EXPORT_FORMATS.map(f => (
              <button
                key={f.key}
                onClick={() => setFormat(f.key)}
                className={`p-3 rounded-xl text-center transition border-2 ${
                  format === f.key ? 'border-gray-800 bg-gray-50' : 'border-gray-200 hover:border-gray-400'
                }`}
              >
                <f.icon size={28} className="mx-auto mb-1 text-gray-600" />
                <p className="font-bold text-sm">{f.label}</p>
                <p className="text-xs text-gray-500">{f.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Période */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Du</label>
            <input type="date" className="w-full border rounded-lg px-3 py-2"
              value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Au</label>
            <input type="date" className="w-full border rounded-lg px-3 py-2"
              value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          </div>
        </div>

        <button
          onClick={handleExport}
          disabled={loading}
          className="w-full bg-gray-800 hover:bg-gray-900 disabled:opacity-60 text-white font-bold py-3 rounded-xl transition flex items-center justify-center gap-2"
        >
          <Download size={20} />
          {loading ? 'Export en cours...' : `Exporter en ${format.toUpperCase()}`}
        </button>
      </div>
    </div>
  );
};

export default AccountingExport;
