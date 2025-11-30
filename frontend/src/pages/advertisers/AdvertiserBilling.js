import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { 
  Plus, 
  Download, 
  X, 
  Save,
  FileText,
  Building2,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  TrendingUp,
  Search,
  Filter,
  RefreshCw,
  ChevronDown,
  DollarSign,
  Receipt,
  CreditCard,
  Sparkles,
  Eye,
  Send
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

// Mapping pays -> devise
const COUNTRY_CURRENCY_MAP = {
  // Afrique
  'Maroc': { code: 'MAD', symbol: 'DH', name: 'Dirham marocain' },
  'Morocco': { code: 'MAD', symbol: 'DH', name: 'Dirham marocain' },
  'Algérie': { code: 'DZD', symbol: 'DA', name: 'Dinar algérien' },
  'Algeria': { code: 'DZD', symbol: 'DA', name: 'Dinar algérien' },
  'Tunisie': { code: 'TND', symbol: 'DT', name: 'Dinar tunisien' },
  'Tunisia': { code: 'TND', symbol: 'DT', name: 'Dinar tunisien' },
  'Sénégal': { code: 'XOF', symbol: 'CFA', name: 'Franc CFA' },
  'Senegal': { code: 'XOF', symbol: 'CFA', name: 'Franc CFA' },
  'Côte d\'Ivoire': { code: 'XOF', symbol: 'CFA', name: 'Franc CFA' },
  'Ivory Coast': { code: 'XOF', symbol: 'CFA', name: 'Franc CFA' },
  'Cameroun': { code: 'XAF', symbol: 'FCFA', name: 'Franc CFA' },
  'Cameroon': { code: 'XAF', symbol: 'FCFA', name: 'Franc CFA' },
  'Égypte': { code: 'EGP', symbol: 'E£', name: 'Livre égyptienne' },
  'Egypt': { code: 'EGP', symbol: 'E£', name: 'Livre égyptienne' },
  'Nigeria': { code: 'NGN', symbol: '₦', name: 'Naira nigérian' },
  'Afrique du Sud': { code: 'ZAR', symbol: 'R', name: 'Rand sud-africain' },
  'South Africa': { code: 'ZAR', symbol: 'R', name: 'Rand sud-africain' },
  
  // Europe
  'France': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Belgique': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Belgium': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Allemagne': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Germany': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Espagne': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Spain': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Italie': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Italy': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Portugal': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Pays-Bas': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Netherlands': { code: 'EUR', symbol: '€', name: 'Euro' },
  'Suisse': { code: 'CHF', symbol: 'CHF', name: 'Franc suisse' },
  'Switzerland': { code: 'CHF', symbol: 'CHF', name: 'Franc suisse' },
  'Royaume-Uni': { code: 'GBP', symbol: '£', name: 'Livre sterling' },
  'United Kingdom': { code: 'GBP', symbol: '£', name: 'Livre sterling' },
  'UK': { code: 'GBP', symbol: '£', name: 'Livre sterling' },
  
  // Amérique
  'États-Unis': { code: 'USD', symbol: '$', name: 'Dollar américain' },
  'United States': { code: 'USD', symbol: '$', name: 'Dollar américain' },
  'USA': { code: 'USD', symbol: '$', name: 'Dollar américain' },
  'Canada': { code: 'CAD', symbol: 'C$', name: 'Dollar canadien' },
  'Brésil': { code: 'BRL', symbol: 'R$', name: 'Real brésilien' },
  'Brazil': { code: 'BRL', symbol: 'R$', name: 'Real brésilien' },
  
  // Moyen-Orient
  'Émirats arabes unis': { code: 'AED', symbol: 'AED', name: 'Dirham des EAU' },
  'UAE': { code: 'AED', symbol: 'AED', name: 'Dirham des EAU' },
  'Arabie Saoudite': { code: 'SAR', symbol: 'SAR', name: 'Riyal saoudien' },
  'Saudi Arabia': { code: 'SAR', symbol: 'SAR', name: 'Riyal saoudien' },
  'Qatar': { code: 'QAR', symbol: 'QAR', name: 'Riyal qatari' },
  'Koweït': { code: 'KWD', symbol: 'KWD', name: 'Dinar koweïtien' },
  'Kuwait': { code: 'KWD', symbol: 'KWD', name: 'Dinar koweïtien' },
  
  // Asie
  'Chine': { code: 'CNY', symbol: '¥', name: 'Yuan chinois' },
  'China': { code: 'CNY', symbol: '¥', name: 'Yuan chinois' },
  'Japon': { code: 'JPY', symbol: '¥', name: 'Yen japonais' },
  'Japan': { code: 'JPY', symbol: '¥', name: 'Yen japonais' },
  'Inde': { code: 'INR', symbol: '₹', name: 'Roupie indienne' },
  'India': { code: 'INR', symbol: '₹', name: 'Roupie indienne' },
};

// Devise par défaut (EUR)
const DEFAULT_CURRENCY = { code: 'EUR', symbol: '€', name: 'Euro' };

// Fonction pour obtenir la devise d'un pays
const getCurrencyByCountry = (country) => {
  if (!country) return DEFAULT_CURRENCY;
  return COUNTRY_CURRENCY_MAP[country] || DEFAULT_CURRENCY;
};

const AdvertiserBilling = () => {
  const [invoices, setInvoices] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [merchants, setMerchants] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const toast = useToast();

  const [formData, setFormData] = useState({
    merchant_id: '',
    amount: '',
    description: '',
    due_date: '',
    currency: 'EUR'
  });

  // Obtenir la devise en fonction du marchand sélectionné
  const selectedMerchant = useMemo(() => {
    return merchants.find(m => m.id === formData.merchant_id);
  }, [merchants, formData.merchant_id]);

  const currentCurrency = useMemo(() => {
    if (!selectedMerchant) return DEFAULT_CURRENCY;
    return getCurrencyByCountry(selectedMerchant.country);
  }, [selectedMerchant]);

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
    setFormData(prev => {
      const newData = { ...prev, [name]: value };
      
      // Si on change de marchand, mettre à jour la devise automatiquement
      if (name === 'merchant_id') {
        const merchant = merchants.find(m => m.id === value);
        if (merchant) {
          const currency = getCurrencyByCountry(merchant.country);
          newData.currency = currency.code;
        }
      }
      
      return newData;
    });
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
      const mockMerchant = merchants.find(m => m.id === formData.merchant_id);
      const merchantCurrency = getCurrencyByCountry(mockMerchant?.country);
      const newInvoice = {
        id: `inv_${Date.now()}`,
        advertiser: mockMerchant?.company_name || 'Annonceur',
        invoice_number: `INV-2024-${String(invoices.length + 1).padStart(3, '0')}`,
        amount: parseFloat(formData.amount),
        currency: merchantCurrency.code,
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
      due_date: '',
      currency: 'EUR'
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

  // Configuration des statuts
  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
        return {
          color: 'bg-amber-100 text-amber-800 border-amber-200',
          icon: Clock,
          label: 'En attente',
          dotColor: 'bg-amber-500',
          gradient: 'from-amber-500 to-orange-500'
        };
      case 'paid':
        return {
          color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
          icon: CheckCircle2,
          label: 'Payée',
          dotColor: 'bg-emerald-500',
          gradient: 'from-emerald-500 to-green-500'
        };
      case 'failed':
        return {
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: XCircle,
          label: 'Échec',
          dotColor: 'bg-red-500',
          gradient: 'from-red-500 to-rose-500'
        };
      case 'overdue':
        return {
          color: 'bg-orange-100 text-orange-800 border-orange-200',
          icon: AlertCircle,
          label: 'En retard',
          dotColor: 'bg-orange-500',
          gradient: 'from-orange-500 to-red-500'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: FileText,
          label: status || 'Inconnu',
          dotColor: 'bg-gray-500',
          gradient: 'from-gray-500 to-gray-600'
        };
    }
  };

  // Vérifier si une facture est en retard
  const isOverdue = (dueDate, status) => {
    if (status?.toLowerCase() === 'paid') return false;
    const due = new Date(dueDate);
    const now = new Date();
    return due < now;
  };

  // Statistiques
  const stats = useMemo(() => {
    const total = invoices.length;
    const pending = invoices.filter(i => i.status?.toLowerCase() === 'pending').length;
    const paid = invoices.filter(i => i.status?.toLowerCase() === 'paid').length;
    const failed = invoices.filter(i => i.status?.toLowerCase() === 'failed').length;
    const totalAmount = invoices.reduce((sum, i) => sum + (parseFloat(i.amount) || 0), 0);
    const paidAmount = invoices
      .filter(i => i.status?.toLowerCase() === 'paid')
      .reduce((sum, i) => sum + (parseFloat(i.amount) || 0), 0);
    const pendingAmount = invoices
      .filter(i => i.status?.toLowerCase() === 'pending')
      .reduce((sum, i) => sum + (parseFloat(i.amount) || 0), 0);

    return { total, pending, paid, failed, totalAmount, paidAmount, pendingAmount };
  }, [invoices]);

  // Filtrage
  const filteredInvoices = useMemo(() => {
    return invoices.filter(inv => {
      const matchesFilter = filter === 'all' || inv.status?.toLowerCase() === filter;
      const matchesSearch = !searchTerm || 
        inv.invoice_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inv.advertiser?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    });
  }, [invoices, filter, searchTerm]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-6 p-6" data-testid="advertiser-billing">
      {/* Header avec gradient */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-500 p-8 text-white shadow-2xl"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-24 -translate-x-24"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Receipt className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Facturation - Annonceurs</h1>
              <p className="text-white/80 mt-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Gérez vos factures et paiements
              </p>
            </div>
          </div>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-white text-emerald-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <Plus className="w-5 h-5" />
            Nouvelle Facture
          </motion.button>
        </div>
      </motion.div>

      {/* Cartes de statistiques */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <motion.div 
          variants={itemVariants}
          className="bg-white rounded-xl p-5 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 cursor-pointer"
          onClick={() => setFilter('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Total factures</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <div className="p-3 bg-indigo-100 rounded-xl">
              <FileText className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-sm">
            <DollarSign className="w-4 h-4 mr-1 text-gray-400" />
            <span className="text-gray-600 font-medium">{formatCurrency(stats.totalAmount)}</span>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          className={`bg-white rounded-xl p-5 shadow-lg border hover:shadow-xl transition-all duration-300 cursor-pointer ${filter === 'pending' ? 'ring-2 ring-amber-500 border-amber-200' : 'border-gray-100'}`}
          onClick={() => setFilter('pending')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">En attente</p>
              <p className="text-3xl font-bold text-amber-600 mt-1">{stats.pending}</p>
            </div>
            <div className="p-3 bg-amber-100 rounded-xl">
              <Clock className="w-6 h-6 text-amber-600" />
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-500">À encaisser</span>
              <span className="font-semibold text-amber-600">{formatCurrency(stats.pendingAmount)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-amber-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${stats.total ? (stats.pending / stats.total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          className={`bg-white rounded-xl p-5 shadow-lg border hover:shadow-xl transition-all duration-300 cursor-pointer ${filter === 'paid' ? 'ring-2 ring-emerald-500 border-emerald-200' : 'border-gray-100'}`}
          onClick={() => setFilter('paid')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Payées</p>
              <p className="text-3xl font-bold text-emerald-600 mt-1">{stats.paid}</p>
            </div>
            <div className="p-3 bg-emerald-100 rounded-xl">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-500">Encaissé</span>
              <span className="font-semibold text-emerald-600">{formatCurrency(stats.paidAmount)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-emerald-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${stats.total ? (stats.paid / stats.total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          className={`bg-white rounded-xl p-5 shadow-lg border hover:shadow-xl transition-all duration-300 cursor-pointer ${filter === 'failed' ? 'ring-2 ring-red-500 border-red-200' : 'border-gray-100'}`}
          onClick={() => setFilter('failed')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Échecs</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{stats.failed}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-xl">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-sm text-red-600">
            <AlertCircle className="w-4 h-4 mr-1" />
            <span>Nécessite attention</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Barre de recherche et filtres */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-xl shadow-lg border border-gray-100 p-4"
      >
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par numéro ou annonceur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200"
            />
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all duration-200"
            >
              <Filter className="w-5 h-5 text-gray-600" />
              <span className="text-gray-700">Filtres</span>
              <ChevronDown className={`w-4 h-4 text-gray-600 transition-transform duration-200 ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            <button
              onClick={fetchInvoices}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Actualiser</span>
            </button>
          </div>
        </div>

        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-gray-100"
            >
              <div className="flex flex-wrap gap-2">
                {['all', 'pending', 'paid', 'failed'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilter(status)}
                    className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                      filter === status 
                        ? 'bg-emerald-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status === 'all' ? 'Toutes' : 
                     status === 'pending' ? 'En attente' :
                     status === 'paid' ? 'Payées' : 'Échecs'}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Liste des factures */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="space-y-4"
      >
        {loading && invoices.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-12">
            <div className="flex flex-col items-center justify-center">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
              </div>
              <p className="mt-4 text-gray-500 font-medium">Chargement des factures...</p>
            </div>
          </div>
        ) : filteredInvoices.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-lg border border-gray-100 p-12"
          >
            <div className="flex flex-col items-center justify-center text-center">
              <div className="p-4 bg-gray-100 rounded-full mb-4">
                <Receipt className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune facture trouvée</h3>
              <p className="text-gray-500 max-w-md">
                {searchTerm 
                  ? `Aucun résultat pour "${searchTerm}". Essayez une autre recherche.`
                  : 'Créez votre première facture en cliquant sur le bouton ci-dessus.'}
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            {/* Table header */}
            <div className="hidden lg:grid lg:grid-cols-7 gap-4 px-6 py-4 bg-gray-50 border-b border-gray-100 text-sm font-semibold text-gray-600">
              <div className="col-span-1">N° Facture</div>
              <div className="col-span-1">Annonceur</div>
              <div className="col-span-1">Montant</div>
              <div className="col-span-1">Statut</div>
              <div className="col-span-1">Création</div>
              <div className="col-span-1">Échéance</div>
              <div className="col-span-1 text-right">Actions</div>
            </div>

            <AnimatePresence>
              {filteredInvoices.map((invoice, index) => {
                const statusConfig = getStatusConfig(
                  isOverdue(invoice.due_date, invoice.status) ? 'overdue' : invoice.status
                );
                const StatusIcon = statusConfig.icon;
                
                return (
                  <motion.div
                    key={invoice.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ delay: index * 0.03 }}
                    className="border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors duration-200"
                  >
                    {/* Mobile view */}
                    <div className="lg:hidden p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${statusConfig.gradient} flex items-center justify-center text-white`}>
                            <FileText className="w-5 h-5" />
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">{invoice.invoice_number}</p>
                            <p className="text-sm text-gray-500">{invoice.advertiser}</p>
                          </div>
                        </div>
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${statusConfig.color}`}>
                          <span className={`w-2 h-2 rounded-full ${statusConfig.dotColor} animate-pulse`}></span>
                          {statusConfig.label}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                        <span className="text-xl font-bold text-gray-900">
                          {formatCurrency(invoice.amount, invoice.currency || 'EUR')}
                        </span>
                        <div className="flex gap-2">
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => {
                              setSelectedInvoice(invoice);
                              setShowDetailModal(true);
                            }}
                            className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                          >
                            <Eye className="w-5 h-5" />
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => handleDownload(invoice.id)}
                            className="p-2 bg-emerald-100 text-emerald-600 rounded-lg hover:bg-emerald-200 transition-colors"
                          >
                            <Download className="w-5 h-5" />
                          </motion.button>
                        </div>
                      </div>
                    </div>

                    {/* Desktop view */}
                    <div className="hidden lg:grid lg:grid-cols-7 gap-4 px-6 py-4 items-center">
                      <div className="col-span-1 flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${statusConfig.gradient} flex items-center justify-center text-white shadow-lg`}>
                          <FileText className="w-5 h-5" />
                        </div>
                        <span className="font-semibold text-gray-900">{invoice.invoice_number}</span>
                      </div>
                      
                      <div className="col-span-1">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-700 truncate">{invoice.advertiser || 'N/A'}</span>
                        </div>
                      </div>
                      
                      <div className="col-span-1">
                        <span className="text-lg font-bold text-gray-900">
                          {formatCurrency(invoice.amount, invoice.currency || 'EUR')}
                        </span>
                      </div>
                      
                      <div className="col-span-1">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${statusConfig.color}`}>
                          <StatusIcon className="w-3.5 h-3.5" />
                          {statusConfig.label}
                        </span>
                      </div>
                      
                      <div className="col-span-1 text-sm text-gray-500">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-4 h-4" />
                          {formatDate(invoice.created_at)}
                        </div>
                      </div>
                      
                      <div className="col-span-1 text-sm">
                        <div className={`flex items-center gap-1.5 ${isOverdue(invoice.due_date, invoice.status) ? 'text-red-600' : 'text-gray-500'}`}>
                          <Clock className="w-4 h-4" />
                          {formatDate(invoice.due_date)}
                        </div>
                      </div>
                      
                      <div className="col-span-1 flex items-center justify-end gap-2">
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleDownload(invoice.id)}
                          className="p-2 bg-emerald-100 text-emerald-600 rounded-lg hover:bg-emerald-200 transition-colors"
                          title="Télécharger"
                        >
                          <Download className="w-5 h-5" />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => {
                            setSelectedInvoice(invoice);
                            setShowDetailModal(true);
                          }}
                          className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                          title="Voir détails"
                        >
                          <Eye className="w-5 h-5" />
                        </motion.button>
                        {invoice.status?.toLowerCase() === 'pending' && (
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2 bg-purple-100 text-purple-600 rounded-lg hover:bg-purple-200 transition-colors"
                            title="Envoyer rappel"
                          >
                            <Send className="w-5 h-5" />
                          </motion.button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* Footer avec compteur */}
      {filteredInvoices.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-sm text-gray-500 py-4"
        >
          Affichage de {filteredInvoices.length} facture{filteredInvoices.length > 1 ? 's' : ''} 
          {filter !== 'all' && ` (filtré sur ${stats.total} au total)`}
        </motion.div>
      )}

      {/* Modal de création de facture */}
      <AnimatePresence>
        {showModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => { setShowModal(false); resetForm(); }}
          >
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header de la modal */}
              <div className="relative overflow-hidden rounded-t-2xl bg-gradient-to-r from-emerald-600 to-teal-500 p-6">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                      <Receipt className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">Nouvelle Facture</h2>
                      <p className="text-white/80 text-sm">Créez une facture pour un annonceur</p>
                    </div>
                  </div>
                  <button
                    onClick={() => { setShowModal(false); resetForm(); }}
                    className="p-2 bg-white/20 hover:bg-white/30 rounded-xl transition-colors"
                  >
                    <X className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>

              <form onSubmit={handleCreateInvoice} className="p-6 space-y-6">
                {/* Annonceur */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <Building2 className="w-4 h-4 text-emerald-600" />
                    Annonceur *
                  </label>
                  <select
                    name="merchant_id"
                    value={formData.merchant_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                  >
                    <option value="">Sélectionnez un annonceur</option>
                    {merchants.map(merchant => {
                      const merchantCurrency = getCurrencyByCountry(merchant.country);
                      return (
                        <option key={merchant.id} value={merchant.id}>
                          {merchant.company_name || merchant.full_name} - {merchant.country || 'Pays non défini'} ({merchantCurrency.code})
                        </option>
                      );
                    })}
                  </select>
                </div>

                {/* Montant */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <DollarSign className="w-4 h-4 text-emerald-600" />
                    Montant ({currentCurrency.symbol}) *
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      name="amount"
                      value={formData.amount}
                      onChange={handleInputChange}
                      required
                      min="0"
                      step="0.01"
                      className="w-full px-4 py-3 pr-20 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white text-lg font-semibold"
                      placeholder="0.00"
                    />
                    <span className="absolute right-4 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-sm font-semibold">
                      {currentCurrency.code}
                    </span>
                  </div>
                  {selectedMerchant && (
                    <p className="mt-2 text-xs text-gray-500 flex items-center gap-1">
                      <CreditCard className="w-3 h-3" />
                      Devise basée sur le pays: {selectedMerchant.country} ({currentCurrency.name})
                    </p>
                  )}
                </div>

                {/* Description */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <FileText className="w-4 h-4 text-emerald-600" />
                    Description
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows="3"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white resize-none"
                    placeholder="Description des services facturés..."
                  />
                </div>

                {/* Date d'échéance */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                    <Calendar className="w-4 h-4 text-emerald-600" />
                    Date d'échéance *
                  </label>
                  <input
                    type="date"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                  />
                </div>

                {/* Actions */}
                <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-100">
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => { setShowModal(false); resetForm(); }}
                    className="px-6 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium"
                  >
                    Annuler
                  </motion.button>
                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={loading}
                    className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl hover:from-emerald-700 hover:to-teal-600 transition-all duration-200 flex items-center gap-2 font-medium shadow-lg hover:shadow-xl disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        <span>Création...</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-5 h-5" />
                        <span>Créer la facture</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal de détails de facture */}
      <AnimatePresence>
        {showDetailModal && selectedInvoice && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowDetailModal(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden"
            >
              {/* Header */}
              <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-indigo-600 p-6">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">Détails de la facture</h3>
                      <p className="text-blue-100 text-sm">#{selectedInvoice.id?.slice(0, 8)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                  >
                    <X className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4">
                {/* Statut */}
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <span className="text-gray-600 font-medium">Statut</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    selectedInvoice.status?.toLowerCase() === 'paid' 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : selectedInvoice.status?.toLowerCase() === 'pending'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {selectedInvoice.status?.toLowerCase() === 'paid' ? '✓ Payée' : 
                     selectedInvoice.status?.toLowerCase() === 'pending' ? '⏳ En attente' : '✗ Annulée'}
                  </span>
                </div>

                {/* Montant */}
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl">
                  <span className="text-gray-600 font-medium">Montant</span>
                  <span className="text-2xl font-bold text-emerald-600">
                    {formatCurrency(selectedInvoice.amount, selectedInvoice.currency || 'EUR')}
                  </span>
                </div>

                {/* Marchand */}
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <span className="text-gray-600 font-medium">Marchand</span>
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-gray-900">
                      {selectedInvoice.merchant?.company_name || selectedInvoice.merchant?.full_name || 'N/A'}
                    </span>
                  </div>
                </div>

                {/* Description */}
                {selectedInvoice.description && (
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <span className="text-gray-600 font-medium block mb-2">Description</span>
                    <p className="text-gray-900">{selectedInvoice.description}</p>
                  </div>
                )}

                {/* Dates */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <span className="text-gray-500 text-sm block mb-1">Date de création</span>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {formatDate(selectedInvoice.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <span className="text-gray-500 text-sm block mb-1">Date d'échéance</span>
                    <div className="flex items-center gap-2">
                      <Clock className={`w-4 h-4 ${isOverdue(selectedInvoice.due_date, selectedInvoice.status) ? 'text-red-500' : 'text-gray-400'}`} />
                      <span className={`font-medium ${isOverdue(selectedInvoice.due_date, selectedInvoice.status) ? 'text-red-600' : 'text-gray-900'}`}>
                        {formatDate(selectedInvoice.due_date)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleDownload(selectedInvoice.id)}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-700 hover:to-teal-600 transition-all"
                >
                  <Download className="w-5 h-5" />
                  Télécharger PDF
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-300 transition-all"
                >
                  Fermer
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdvertiserBilling;
