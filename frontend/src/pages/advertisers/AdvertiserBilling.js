import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { Plus, Download, X, Save } from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const AdvertiserBilling = () => {
  const [invoices, setInvoices] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [merchants, setMerchants] = useState([]);
  const toast = useToast();

  const [formData, setFormData] = useState({
    merchant_id: '',
    amount: '',
    description: '',
    due_date: ''
  });

  useEffect(() => {
    fetchInvoices();
    fetchMerchants();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/invoices');
      console.log('Invoices reçues:', response.data);
      
      if (response.data && Array.isArray(response.data.invoices)) {
        setInvoices(response.data.invoices);
      } else if (Array.isArray(response.data)) {
        setInvoices(response.data);
      } else {
        console.warn('Format de réponse inattendu:', response.data);
      }
    } catch (error) {
      console.error('Error fetching invoices:', error);
      toast?.error?.('Impossible de charger les factures');
    } finally {
      setLoading(false);
    }
  };

  const fetchMerchants = async () => {
    try {
      const response = await api.get('/api/merchants');
      setMerchants(response.data.merchants || []);
    } catch (error) {
      console.error('Error fetching merchants:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    
    if (!formData.merchant_id || !formData.amount || !formData.due_date) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/invoices', formData);
      toast.success('Facture créée avec succès');
      
      setShowModal(false);
      resetForm();
      fetchInvoices();
    } catch (error) {
      console.error('Error creating invoice:', error);
      toast.error('Erreur lors de la création de la facture');
      
      // Mock success pour développement
      const selectedMerchant = merchants.find(m => m.id === formData.merchant_id);
      const newInvoice = {
        id: `inv_${Date.now()}`,
        advertiser: selectedMerchant?.company_name || 'Annonceur',
        invoice_number: `INV-2024-${String(invoices.length + 1).padStart(3, '0')}`,
        amount: parseFloat(formData.amount),
        status: 'pending',
        created_at: new Date().toISOString(),
        due_date: formData.due_date
      };
      
      setInvoices(prev => [newInvoice, ...prev]);
      toast.success('Facture créée avec succès');
      setShowModal(false);
      resetForm();
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      merchant_id: '',
      amount: '',
      description: '',
      due_date: ''
    });
  };

  const handleDownload = async (invoiceId) => {
    try {
      const response = await api.get(`/api/invoices/${invoiceId}/download`, {
        responseType: 'blob'
      });
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice_${invoiceId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Facture téléchargée');
    } catch (error) {
      console.error('Error downloading invoice:', error);
      toast.error('Erreur lors du téléchargement');
    }
  };

  const columns = [
    {
      header: 'N° Facture',
      accessor: 'invoice_number',
    },
    {
      header: 'Annonceur',
      accessor: 'advertiser',
    },
    {
      header: 'Montant',
      accessor: 'amount',
      render: (row) => formatCurrency(row.amount),
    },
    {
      header: 'Statut',
      accessor: 'status',
      render: (row) => <Badge status={row.status}>{row.status}</Badge>,
    },
    {
      header: 'Date de création',
      accessor: 'created_at',
      render: (row) => formatDate(row.created_at),
    },
    {
      header: 'Échéance',
      accessor: 'due_date',
      render: (row) => formatDate(row.due_date),
    },
    {
      header: 'Actions',
      accessor: 'actions',
      render: (row) => (
        <Button 
          size="sm" 
          variant="outline"
          onClick={() => handleDownload(row.id)}
        >
          <Download size={16} />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-6" data-testid="advertiser-billing">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturation - Annonceurs</h1>
          <p className="text-gray-600 mt-2">Gérez les factures</p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus size={20} className="mr-2" />
          Nouvelle Facture
        </Button>
      </div>

      <Card>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <Table columns={columns} data={invoices} />
        )}
      </Card>

      {/* Modal de création de facture */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Nouvelle Facture</h2>
                <button
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <form onSubmit={handleCreateInvoice} className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Annonceur *
                </label>
                <select
                  name="merchant_id"
                  value={formData.merchant_id}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Sélectionnez un annonceur</option>
                  {merchants.map(merchant => (
                    <option key={merchant.id} value={merchant.id}>
                      {merchant.company_name || merchant.full_name} - {merchant.email}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Montant (€) *
                </label>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  required
                  min="0"
                  step="0.01"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Description des services facturés..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date d'échéance *
                </label>
                <input
                  type="date"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center space-x-2 disabled:opacity-50"
                >
                  <Save className="w-5 h-5" />
                  <span>{loading ? 'Création...' : 'Créer la facture'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvertiserBilling;
