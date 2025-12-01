import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDate } from '../../utils/helpers';
import { 
  Check, 
  X, 
  Building2, 
  Mail, 
  Globe, 
  Calendar, 
  Clock, 
  UserCheck, 
  UserX, 
  Users,
  TrendingUp,
  Filter,
  Search,
  RefreshCw,
  ChevronDown,
  MapPin,
  Sparkles,
  Eye,
  Download,
  MessageSquare,
  CheckSquare,
  Square,
  Send,
  FileText,
  Phone,
  DollarSign,
  Briefcase,
  StickyNote
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

// Mapping des drapeaux par pays
const COUNTRY_FLAGS = {
  'France': '🇫🇷',
  'Belgique': '🇧🇪',
  'Suisse': '🇨🇭',
  'Canada': '🇨🇦',
  'États-Unis': '🇺🇸',
  'USA': '🇺🇸',
  'Allemagne': '🇩🇪',
  'Espagne': '🇪🇸',
  'Italie': '🇮🇹',
  'Royaume-Uni': '🇬🇧',
  'UK': '🇬🇧',
  'Maroc': '🇲🇦',
  'Tunisie': '🇹🇳',
  'Algérie': '🇩🇿',
  'Sénégal': '🇸🇳',
  'Côte d\'Ivoire': '🇨🇮',
  'Luxembourg': '🇱🇺',
  'Portugal': '🇵🇹',
  'Pays-Bas': '🇳🇱',
  'Japon': '🇯🇵',
  'Chine': '🇨🇳',
  'Australie': '🇦🇺',
  'Brésil': '🇧🇷',
  'Mexique': '🇲🇽',
  'Inde': '🇮🇳',
  'default': '🌍'
};

const AdvertiserRegistrations = () => {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedRegistrations, setSelectedRegistrations] = useState([]);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedRegistration, setSelectedRegistration] = useState(null);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [messageForm, setMessageForm] = useState({ subject: '', message: '' });
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteText, setNoteText] = useState('');
  const toast = useToast();

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const fetchRegistrations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/advertiser-registrations');
      console.log('Registrations reçues:', response.data);
      setRegistrations(response.data.registrations || []);
    } catch (error) {
      console.error('Error fetching registrations:', error);
      toast.error('Erreur lors du chargement des demandes');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      setActionLoading(id);
      await api.post(`/api/admin/registration-requests/${id}/approve`);
      toast.success('Demande approuvée avec succès');
      fetchRegistrations();
    } catch (error) {
      console.error('Error approving registration:', error);
      toast.error('Erreur lors de l\'approbation');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir rejeter cette demande ?')) {
      return;
    }
    
    try {
      setActionLoading(id);
      await api.post(`/api/admin/registration-requests/${id}/reject`);
      toast.success('Demande rejetée');
      fetchRegistrations();
    } catch (error) {
      console.error('Error rejecting registration:', error);
      toast.error('Erreur lors du rejet');
    } finally {
      setActionLoading(null);
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedRegistrations.length === 0) {
      toast.error('Aucune demande sélectionnée');
      return;
    }

    const confirmMsg = action === 'approve' 
      ? `Approuver ${selectedRegistrations.length} demande(s) ?`
      : `Rejeter ${selectedRegistrations.length} demande(s) ?`;
    
    if (!window.confirm(confirmMsg)) {
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/admin/registration-requests/bulk-actions', {
        registration_ids: selectedRegistrations,
        action: action
      });
      
      toast.success(`${selectedRegistrations.length} demande(s) ${action === 'approve' ? 'approuvée(s)' : 'rejetée(s)'}`);
      setSelectedRegistrations([]);
      fetchRegistrations();
    } catch (error) {
      console.error('Error with bulk action:', error);
      toast.error('Erreur lors de l\'action en masse');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (registration) => {
    try {
      const response = await api.get(`/api/admin/registration-requests/${registration.id}`);
      setSelectedRegistration(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error fetching details:', error);
      toast.error('Erreur lors du chargement des détails');
    }
  };

  const handleSendMessage = async () => {
    if (!messageForm.subject || !messageForm.message) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }

    try {
      await api.post(`/api/admin/registration-requests/${selectedRegistration.id}/send-message`, messageForm);
      toast.success('Message envoyé avec succès');
      setShowMessageModal(false);
      setMessageForm({ subject: '', message: '' });
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Erreur lors de l\'envoi du message');
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim()) {
      toast.error('Veuillez saisir une note');
      return;
    }

    try {
      await api.post(`/api/admin/registration-requests/${selectedRegistration.id}/notes`, {
        note: noteText
      });
      toast.success('Note ajoutée');
      setShowNoteModal(false);
      setNoteText('');
      
      // Rafraîchir les détails
      const response = await api.get(`/api/admin/registration-requests/${selectedRegistration.id}`);
      setSelectedRegistration(response.data);
    } catch (error) {
      console.error('Error adding note:', error);
      toast.error('Erreur lors de l\'ajout de la note');
    }
  };

  const handleExportCSV = () => {
    const csvData = filteredRegistrations.map(reg => ({
      'ID': reg.id,
      'Entreprise': reg.company_name,
      'Email': reg.email,
      'Pays': reg.country,
      'Statut': reg.status,
      'Date de création': formatDate(reg.created_at)
    }));

    const headers = Object.keys(csvData[0] || {});
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `demandes_inscription_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    toast.success('Export CSV réussi');
  };

  const toggleSelectRegistration = (id) => {
    setSelectedRegistrations(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    const pendingIds = filteredRegistrations
      .filter(r => r.status?.toLowerCase() === 'pending')
      .map(r => r.id);
    
    if (selectedRegistrations.length === pendingIds.length) {
      setSelectedRegistrations([]);
    } else {
      setSelectedRegistrations(pendingIds);
    }
  };

  const getFlag = (country) => {
    return COUNTRY_FLAGS[country] || COUNTRY_FLAGS['default'];
  };

  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending':
        return {
          color: 'bg-amber-100 text-amber-800 border-amber-200',
          icon: Clock,
          label: 'En attente',
          dotColor: 'bg-amber-500'
        };
      case 'approved':
        return {
          color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
          icon: UserCheck,
          label: 'Approuvé',
          dotColor: 'bg-emerald-500'
        };
      case 'rejected':
        return {
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: UserX,
          label: 'Rejeté',
          dotColor: 'bg-red-500'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: Clock,
          label: status || 'Inconnu',
          dotColor: 'bg-gray-500'
        };
    }
  };

  const getTimeSince = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Il y a moins d\'une heure';
    if (diffInHours < 24) return `Il y a ${diffInHours}h`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays === 1) return 'Hier';
    if (diffInDays < 7) return `Il y a ${diffInDays} jours`;
    return formatDate(dateString);
  };

  // Statistiques
  const stats = {
    total: registrations.length,
    pending: registrations.filter(r => r.status?.toLowerCase() === 'pending').length,
    approved: registrations.filter(r => r.status?.toLowerCase() === 'approved').length,
    rejected: registrations.filter(r => r.status?.toLowerCase() === 'rejected').length,
  };

  // Filtrage
  const filteredRegistrations = registrations.filter(reg => {
    const matchesFilter = filter === 'all' || reg.status?.toLowerCase() === filter;
    const matchesSearch = !searchTerm || 
      reg.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      reg.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      reg.country?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-6 p-6" data-testid="advertiser-registrations">
      {/* Header avec gradient */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 p-8 text-white shadow-2xl"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-24 -translate-x-24"></div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Users className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Demandes d'Inscription</h1>
              <p className="text-white/80 mt-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Gérez les demandes des annonceurs
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Cartes de statistiques */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <motion.div 
          variants={itemVariants}
          className="bg-white rounded-xl p-5 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 cursor-pointer"
          onClick={() => setFilter('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Total demandes</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <div className="p-3 bg-indigo-100 rounded-xl">
              <Users className="w-6 h-6 text-indigo-600" />
            </div>
          </div>
          <div className="mt-3 flex items-center text-sm text-gray-500">
            <TrendingUp className="w-4 h-4 mr-1 text-green-500" />
            Toutes les demandes
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
          className={`bg-white rounded-xl p-5 shadow-lg border hover:shadow-xl transition-all duration-300 cursor-pointer ${filter === 'approved' ? 'ring-2 ring-emerald-500 border-emerald-200' : 'border-gray-100'}`}
          onClick={() => setFilter('approved')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Approuvées</p>
              <p className="text-3xl font-bold text-emerald-600 mt-1">{stats.approved}</p>
            </div>
            <div className="p-3 bg-emerald-100 rounded-xl">
              <UserCheck className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-emerald-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${stats.total ? (stats.approved / stats.total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          className={`bg-white rounded-xl p-5 shadow-lg border hover:shadow-xl transition-all duration-300 cursor-pointer ${filter === 'rejected' ? 'ring-2 ring-red-500 border-red-200' : 'border-gray-100'}`}
          onClick={() => setFilter('rejected')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Rejetées</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{stats.rejected}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-xl">
              <UserX className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${stats.total ? (stats.rejected / stats.total) * 100 : 0}%` }}
              ></div>
            </div>
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
              placeholder="Rechercher par entreprise, email ou pays..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
            />
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={handleExportCSV}
              disabled={filteredRegistrations.length === 0}
              className="flex items-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50"
            >
              <Download className="w-5 h-5" />
              <span>Export CSV</span>
            </button>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all duration-200"
            >
              <Filter className="w-5 h-5 text-gray-600" />
              <span className="text-gray-700">Filtres</span>
              <ChevronDown className={`w-4 h-4 text-gray-600 transition-transform duration-200 ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            
            <button
              onClick={fetchRegistrations}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50"
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
                {['all', 'pending', 'approved', 'rejected'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilter(status)}
                    className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                      filter === status 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status === 'all' ? 'Tous' : 
                     status === 'pending' ? 'En attente' :
                     status === 'approved' ? 'Approuvés' : 'Rejetés'}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Barre d'actions en masse */}
      {selectedRegistrations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-indigo-50 border border-indigo-200 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckSquare className="w-5 h-5 text-indigo-600" />
              <span className="font-medium text-indigo-900">
                {selectedRegistrations.length} demande(s) sélectionnée(s)
              </span>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => handleBulkAction('approve')}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-all duration-200"
              >
                <Check className="w-4 h-4" />
                Approuver tout
              </button>
              <button
                onClick={() => handleBulkAction('reject')}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all duration-200"
              >
                <X className="w-4 h-4" />
                Rejeter tout
              </button>
              <button
                onClick={() => setSelectedRegistrations([])}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-all duration-200"
              >
                Annuler
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Liste des demandes */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="space-y-4"
      >
        {loading && registrations.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-12">
            <div className="flex flex-col items-center justify-center">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
              </div>
              <p className="mt-4 text-gray-500 font-medium">Chargement des demandes...</p>
            </div>
          </div>
        ) : filteredRegistrations.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl shadow-lg border border-gray-100 p-12"
          >
            <div className="flex flex-col items-center justify-center text-center">
              <div className="p-4 bg-gray-100 rounded-full mb-4">
                <Users className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune demande trouvée</h3>
              <p className="text-gray-500 max-w-md">
                {searchTerm 
                  ? `Aucun résultat pour "${searchTerm}". Essayez une autre recherche.`
                  : 'Il n\'y a aucune demande d\'inscription pour le moment.'}
              </p>
            </div>
          </motion.div>
        ) : (
          <AnimatePresence>
            {filteredRegistrations.map((registration, index) => {
              const statusConfig = getStatusConfig(registration.status);
              const StatusIcon = statusConfig.icon;
              
              return (
                <motion.div
                  key={registration.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 hover:shadow-xl transition-all duration-300"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Infos entreprise */}
                    <div className="flex items-start gap-4">
                      {/* Checkbox pour sélection multiple (seulement pour pending) */}
                      {registration.status?.toLowerCase() === 'pending' && (
                        <button
                          onClick={() => toggleSelectRegistration(registration.id)}
                          className="mt-2"
                        >
                          {selectedRegistrations.includes(registration.id) ? (
                            <CheckSquare className="w-6 h-6 text-indigo-600" />
                          ) : (
                            <Square className="w-6 h-6 text-gray-400 hover:text-indigo-600" />
                          )}
                        </button>
                      )}
                      
                      <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                        {registration.company_name?.charAt(0).toUpperCase() || 'A'}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-lg font-bold text-gray-900">
                            {registration.company_name || 'Entreprise'}
                          </h3>
                          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${statusConfig.color}`}>
                            <span className={`w-2 h-2 rounded-full ${statusConfig.dotColor} animate-pulse`}></span>
                            {statusConfig.label}
                          </span>
                        </div>
                        
                        <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1.5">
                            <Mail className="w-4 h-4" />
                            {registration.email || 'N/A'}
                          </span>
                          <span className="flex items-center gap-1.5">
                            <MapPin className="w-4 h-4" />
                            <span className="text-lg">{getFlag(registration.country)}</span>
                            {registration.country || 'N/A'}
                          </span>
                          <span className="flex items-center gap-1.5">
                            <Calendar className="w-4 h-4" />
                            {getTimeSince(registration.created_at)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 flex-wrap">
                      {/* Bouton Voir détails (toujours visible) */}
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleViewDetails(registration)}
                        className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-all duration-200"
                      >
                        <Eye className="w-5 h-5" />
                        <span>Détails</span>
                      </motion.button>
                      
                      {registration.status?.toLowerCase() === 'pending' && (
                        <>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleApprove(registration.id)}
                            disabled={actionLoading === registration.id}
                            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-xl font-medium shadow-lg hover:shadow-emerald-200 transition-all duration-200 disabled:opacity-50"
                          >
                            {actionLoading === registration.id ? (
                              <RefreshCw className="w-5 h-5 animate-spin" />
                            ) : (
                              <Check className="w-5 h-5" />
                            )}
                            <span>Approuver</span>
                          </motion.button>
                          
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleReject(registration.id)}
                            disabled={actionLoading === registration.id}
                            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-xl font-medium shadow-lg hover:shadow-red-200 transition-all duration-200 disabled:opacity-50"
                          >
                            {actionLoading === registration.id ? (
                              <RefreshCw className="w-5 h-5 animate-spin" />
                            ) : (
                              <X className="w-5 h-5" />
                            )}
                            <span>Rejeter</span>
                          </motion.button>
                        </>
                      )}
                      
                      {registration.status?.toLowerCase() === 'approved' && (
                        <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-xl">
                          <UserCheck className="w-5 h-5" />
                          <span className="font-medium">Approuvé</span>
                        </div>
                      )}
                      
                      {registration.status?.toLowerCase() === 'rejected' && (
                        <div className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-xl">
                          <UserX className="w-5 h-5" />
                          <span className="font-medium">Rejeté</span>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </motion.div>

      {/* Footer avec compteur */}
      {filteredRegistrations.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-sm text-gray-500 py-4"
        >
          Affichage de {filteredRegistrations.length} demande{filteredRegistrations.length > 1 ? 's' : ''} 
          {filter !== 'all' && ` (filtré sur ${stats.total} au total)`}
        </motion.div>
      )}

      {/* Modal Détails */}
      <AnimatePresence>
        {showDetailModal && selectedRegistration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowDetailModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white sticky top-0 z-10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center text-2xl font-bold">
                      {selectedRegistration.company_name?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">{selectedRegistration.company_name}</h2>
                      <p className="text-white/80">{selectedRegistration.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="p-2 hover:bg-white/20 rounded-lg transition-all duration-200"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>

              {/* Contenu */}
              <div className="p-6 space-y-6">
                {/* Informations principales */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                    <Mail className="w-5 h-5 text-gray-600" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-medium">{selectedRegistration.email}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                    <MapPin className="w-5 h-5 text-gray-600" />
                    <div>
                      <p className="text-sm text-gray-500">Pays</p>
                      <p className="font-medium">
                        {getFlag(selectedRegistration.country)} {selectedRegistration.country}
                      </p>
                    </div>
                  </div>

                  {selectedRegistration.contact_person && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                      <Users className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="text-sm text-gray-500">Contact</p>
                        <p className="font-medium">{selectedRegistration.contact_person}</p>
                      </div>
                    </div>
                  )}

                  {selectedRegistration.phone && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                      <Phone className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="text-sm text-gray-500">Téléphone</p>
                        <p className="font-medium">{selectedRegistration.phone}</p>
                      </div>
                    </div>
                  )}

                  {selectedRegistration.website && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                      <Globe className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="text-sm text-gray-500">Site web</p>
                        <a 
                          href={selectedRegistration.website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="font-medium text-indigo-600 hover:underline"
                        >
                          {selectedRegistration.website}
                        </a>
                      </div>
                    </div>
                  )}

                  {selectedRegistration.business_type && (
                    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                      <Briefcase className="w-5 h-5 text-gray-600" />
                      <div>
                        <p className="text-sm text-gray-500">Type d'entreprise</p>
                        <p className="font-medium">{selectedRegistration.business_type}</p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
                    <Calendar className="w-5 h-5 text-gray-600" />
                    <div>
                      <p className="text-sm text-gray-500">Date de demande</p>
                      <p className="font-medium">{formatDate(selectedRegistration.created_at)}</p>
                    </div>
                  </div>
                </div>

                {/* Notes internes */}
                {selectedRegistration.notes && (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <StickyNote className="w-5 h-5 text-amber-600" />
                      <h3 className="font-semibold text-amber-900">Notes internes</h3>
                    </div>
                    <div className="text-sm text-gray-700 whitespace-pre-wrap bg-white p-3 rounded-lg">
                      {selectedRegistration.notes}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                  <button
                    onClick={() => {
                      setShowMessageModal(true);
                      setShowDetailModal(false);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all duration-200"
                  >
                    <Send className="w-5 h-5" />
                    Envoyer un message
                  </button>

                  <button
                    onClick={() => {
                      setShowNoteModal(true);
                      setShowDetailModal(false);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl transition-all duration-200"
                  >
                    <StickyNote className="w-5 h-5" />
                    Ajouter une note
                  </button>

                  {selectedRegistration.status?.toLowerCase() === 'pending' && (
                    <>
                      <button
                        onClick={() => {
                          handleApprove(selectedRegistration.id);
                          setShowDetailModal(false);
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-all duration-200"
                      >
                        <Check className="w-5 h-5" />
                        Approuver
                      </button>

                      <button
                        onClick={() => {
                          handleReject(selectedRegistration.id);
                          setShowDetailModal(false);
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl transition-all duration-200"
                      >
                        <X className="w-5 h-5" />
                        Rejeter
                      </button>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Envoyer un message */}
      <AnimatePresence>
        {showMessageModal && selectedRegistration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowMessageModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full"
            >
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white rounded-t-2xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Send className="w-6 h-6" />
                    <h2 className="text-xl font-bold">Envoyer un message</h2>
                  </div>
                  <button
                    onClick={() => setShowMessageModal(false)}
                    className="p-2 hover:bg-white/20 rounded-lg"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <p className="text-white/80 mt-1">À: {selectedRegistration.email}</p>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Objet
                  </label>
                  <input
                    type="text"
                    value={messageForm.subject}
                    onChange={(e) => setMessageForm({ ...messageForm, subject: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Objet du message"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={messageForm.message}
                    onChange={(e) => setMessageForm({ ...messageForm, message: e.target.value })}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Votre message..."
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleSendMessage}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-all duration-200"
                  >
                    <Send className="w-5 h-5" />
                    Envoyer
                  </button>
                  <button
                    onClick={() => setShowMessageModal(false)}
                    className="px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl font-medium transition-all duration-200"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Ajouter une note */}
      <AnimatePresence>
        {showNoteModal && selectedRegistration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowNoteModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full"
            >
              <div className="bg-gradient-to-r from-amber-600 to-orange-600 p-6 text-white rounded-t-2xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <StickyNote className="w-6 h-6" />
                    <h2 className="text-xl font-bold">Ajouter une note interne</h2>
                  </div>
                  <button
                    onClick={() => setShowNoteModal(false)}
                    className="p-2 hover:bg-white/20 rounded-lg"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <p className="text-white/80 mt-1">Pour: {selectedRegistration.company_name}</p>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Note (visible uniquement par les administrateurs)
                  </label>
                  <textarea
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="Ajoutez vos notes ici..."
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleAddNote}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-medium transition-all duration-200"
                  >
                    <StickyNote className="w-5 h-5" />
                    Ajouter la note
                  </button>
                  <button
                    onClick={() => setShowNoteModal(false)}
                    className="px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl font-medium transition-all duration-200"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdvertiserRegistrations;
