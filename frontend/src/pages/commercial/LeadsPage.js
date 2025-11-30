import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Plus, Search, Filter, Download, Eye, Edit, Trash2,
  Phone, Mail, Calendar, FileText, DollarSign, TrendingUp,
  X, Save, AlertCircle, CheckCircle, Clock, MessageSquare,
  Paperclip, Send, MoreVertical, Target, Activity
} from 'lucide-react';
import api from '../../utils/api';
import { toast } from 'react-toastify';

const LeadsPage = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterTemperature, setFilterTemperature] = useState('all');
  const [selectedLead, setSelectedLead] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  // Form states
  const [formData, setFormData] = useState({
    company_name: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    service_type: '',
    estimated_value: '',
    status: 'nouveau',
    temperature: 'froid',
    source: 'website',
    notes: ''
  });

  useEffect(() => {
    fetchLeads();
  }, [filterStatus, filterTemperature, sortBy, sortOrder]);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      let url = '/api/commercial/leads?limit=100';
      
      if (filterStatus !== 'all') {
        url += `&status=${filterStatus}`;
      }
      if (filterTemperature !== 'all') {
        url += `&temperature=${filterTemperature}`;
      }
      url += `&sort=${sortBy}&order=${sortOrder}`;

      const response = await api.get(url);
      setLeads(Array.isArray(response.data) ? response.data : response.data?.leads || []);
    } catch (error) {
      console.error('Erreur chargement leads:', error);
      toast.error('Erreur lors du chargement des leads');
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/commercial/leads', formData);
      toast.success('Lead créé avec succès !');
      setShowCreateModal(false);
      resetForm();
      fetchLeads();
    } catch (error) {
      console.error('Erreur création lead:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la création du lead');
    }
  };

  const handleUpdateLead = async (leadId, updates) => {
    try {
      await api.patch(`/api/commercial/leads/${leadId}`, updates);
      toast.success('Lead mis à jour !');
      fetchLeads();
      if (selectedLead?.id === leadId) {
        setSelectedLead({ ...selectedLead, ...updates });
      }
    } catch (error) {
      console.error('Erreur mise à jour lead:', error);
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeleteLead = async (leadId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce lead ?')) return;
    
    try {
      await api.delete(`/api/commercial/leads/${leadId}`);
      toast.success('Lead supprimé');
      fetchLeads();
      if (selectedLead?.id === leadId) {
        setShowDetailModal(false);
        setSelectedLead(null);
      }
    } catch (error) {
      console.error('Erreur suppression lead:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  const resetForm = () => {
    setFormData({
      company_name: '',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      service_type: '',
      estimated_value: '',
      status: 'nouveau',
      temperature: 'froid',
      source: 'website',
      notes: ''
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      nouveau: 'bg-blue-100 text-blue-800',
      contacté: 'bg-indigo-100 text-indigo-800',
      qualifié: 'bg-purple-100 text-purple-800',
      proposition: 'bg-pink-100 text-pink-800',
      négociation: 'bg-orange-100 text-orange-800',
      conclu: 'bg-green-100 text-green-800',
      perdu: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTemperatureEmoji = (temp) => {
    const emojis = {
      chaud: '🔥',
      tiède: '☀️',
      froid: '❄️'
    };
    return emojis[temp] || '❄️';
  };

  const filteredLeads = leads.filter(lead => {
    const searchLower = searchTerm.toLowerCase();
    return (
      lead.company_name?.toLowerCase().includes(searchLower) ||
      lead.contact_name?.toLowerCase().includes(searchLower) ||
      lead.contact_email?.toLowerCase().includes(searchLower)
    );
  });

  const exportToCSV = () => {
    const headers = ['Entreprise', 'Contact', 'Email', 'Téléphone', 'Statut', 'Température', 'Valeur', 'Date'];
    const rows = filteredLeads.map(lead => [
      lead.company_name,
      lead.contact_name,
      lead.contact_email,
      lead.contact_phone,
      lead.status,
      lead.temperature,
      lead.estimated_value || 0,
      new Date(lead.created_at).toLocaleDateString()
    ]);

    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('Export CSV réussi !');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des leads...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Users className="w-8 h-8 text-purple-600" />
              CRM - Gestion des Leads
            </h1>
            <p className="text-gray-600 mt-1">
              {filteredLeads.length} lead{filteredLeads.length > 1 ? 's' : ''} trouvé{filteredLeads.length > 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={exportToCSV}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
            >
              <Download size={18} />
              Exporter CSV
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2 font-medium shadow-lg"
            >
              <Plus size={20} />
              Nouveau Lead
            </button>
          </div>
        </div>

        {/* Filtres et Recherche */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white rounded-lg shadow-sm p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="all">Tous les statuts</option>
            <option value="nouveau">Nouveau</option>
            <option value="contacté">Contacté</option>
            <option value="qualifié">Qualifié</option>
            <option value="proposition">Proposition</option>
            <option value="négociation">Négociation</option>
            <option value="conclu">Conclu</option>
            <option value="perdu">Perdu</option>
          </select>

          <select
            value={filterTemperature}
            onChange={(e) => setFilterTemperature(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="all">Toutes températures</option>
            <option value="chaud">🔥 Chaud</option>
            <option value="tiède">☀️ Tiède</option>
            <option value="froid">❄️ Froid</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="created_at">Date de création</option>
            <option value="estimated_value">Valeur estimée</option>
            <option value="company_name">Nom entreprise</option>
            <option value="status">Statut</option>
          </select>
        </div>
      </div>

      {/* Table des Leads */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm overflow-hidden"
      >
        {filteredLeads.length === 0 ? (
          <div className="text-center py-16">
            <Users size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun lead trouvé</h3>
            <p className="text-gray-600 mb-6">Commencez par créer votre premier lead</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              Créer un lead
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Entreprise / Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coordonnées
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Température
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valeur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLeads.map((lead) => (
                  <motion.tr
                    key={lead.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 transition cursor-pointer"
                    onClick={() => {
                      setSelectedLead(lead);
                      setShowDetailModal(true);
                    }}
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{lead.company_name}</p>
                        <p className="text-sm text-gray-500">{lead.contact_name}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <p className="text-gray-900 flex items-center gap-2">
                          <Mail size={14} className="text-gray-400" />
                          {lead.contact_email}
                        </p>
                        {lead.contact_phone && (
                          <p className="text-gray-500 flex items-center gap-2 mt-1">
                            <Phone size={14} className="text-gray-400" />
                            {lead.contact_phone}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
                        {lead.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-2xl">{getTemperatureEmoji(lead.temperature)}</span>
                      <span className="ml-2 text-sm text-gray-600">{lead.temperature}</span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm font-semibold text-gray-900">
                        {lead.estimated_value?.toLocaleString() || 0} €
                      </p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(lead.created_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => {
                            setSelectedLead(lead);
                            setShowDetailModal(true);
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          title="Voir détails"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteLead(lead.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                          title="Supprimer"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {/* Modal Création Lead */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900">Créer un nouveau lead</h2>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition"
                  >
                    <X size={24} />
                  </button>
                </div>
              </div>

              <form onSubmit={handleCreateLead} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom de l'entreprise *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.company_name}
                      onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Ex: Tech Corp"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom du contact *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.contact_name}
                      onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Ex: Jean Dupont"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.contact_email}
                      onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="contact@techcorp.fr"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Téléphone
                    </label>
                    <input
                      type="tel"
                      value={formData.contact_phone}
                      onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="+33 6 12 34 56 78"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type de service
                    </label>
                    <input
                      type="text"
                      value={formData.service_type}
                      onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Ex: Marketing digital"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Valeur estimée (€)
                    </label>
                    <input
                      type="number"
                      value={formData.estimated_value}
                      onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="5000"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Statut
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="nouveau">Nouveau</option>
                      <option value="contacté">Contacté</option>
                      <option value="qualifié">Qualifié</option>
                      <option value="proposition">Proposition</option>
                      <option value="négociation">Négociation</option>
                      <option value="conclu">Conclu</option>
                      <option value="perdu">Perdu</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Température
                    </label>
                    <select
                      value={formData.temperature}
                      onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="froid">❄️ Froid</option>
                      <option value="tiède">☀️ Tiède</option>
                      <option value="chaud">🔥 Chaud</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows="4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Ajoutez des notes sur ce lead..."
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center gap-2"
                  >
                    <Save size={18} />
                    Créer le lead
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal Détails Lead */}
      <AnimatePresence>
        {showDetailModal && selectedLead && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowDetailModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedLead.company_name}</h2>
                    <p className="text-purple-100 mt-1">{selectedLead.contact_name}</p>
                  </div>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="p-2 hover:bg-white/20 rounded-lg transition"
                  >
                    <X size={24} />
                  </button>
                </div>
                
                <div className="flex items-center gap-4 mt-4">
                  <span className={`px-4 py-1 rounded-full text-sm font-medium bg-white/20`}>
                    {selectedLead.status}
                  </span>
                  <span className="text-2xl">{getTemperatureEmoji(selectedLead.temperature)}</span>
                  <span className="text-lg font-bold">
                    {selectedLead.estimated_value?.toLocaleString() || 0} €
                  </span>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                {/* Informations de contact */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Phone size={20} className="text-purple-600" />
                    Coordonnées
                  </h3>
                  <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
                    <div>
                      <p className="text-sm text-gray-600">Email</p>
                      <p className="text-sm font-medium text-gray-900">{selectedLead.contact_email}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Téléphone</p>
                      <p className="text-sm font-medium text-gray-900">{selectedLead.contact_phone || 'Non renseigné'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Service</p>
                      <p className="text-sm font-medium text-gray-900">{selectedLead.service_type || 'Non renseigné'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Date de création</p>
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(selectedLead.created_at).toLocaleDateString('fr-FR', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Actions rapides */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Target size={20} className="text-purple-600" />
                    Actions rapides
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => {
                        handleUpdateLead(selectedLead.id, { status: 'contacté' });
                      }}
                      className="px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition flex items-center justify-center gap-2"
                    >
                      <Phone size={18} />
                      Marquer comme contacté
                    </button>
                    <button
                      onClick={() => {
                        handleUpdateLead(selectedLead.id, { status: 'qualifié' });
                      }}
                      className="px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition flex items-center justify-center gap-2"
                    >
                      <CheckCircle size={18} />
                      Marquer comme qualifié
                    </button>
                    <button
                      onClick={() => {
                        window.location.href = `mailto:${selectedLead.contact_email}`;
                      }}
                      className="px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition flex items-center justify-center gap-2"
                    >
                      <Mail size={18} />
                      Envoyer un email
                    </button>
                    <button
                      onClick={() => {
                        handleUpdateLead(selectedLead.id, { status: 'conclu' });
                      }}
                      className="px-4 py-3 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition flex items-center justify-center gap-2"
                    >
                      <DollarSign size={18} />
                      Marquer comme conclu
                    </button>
                  </div>
                </div>

                {/* Notes */}
                {selectedLead.notes && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <FileText size={20} className="text-purple-600" />
                      Notes
                    </h3>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{selectedLead.notes}</p>
                    </div>
                  </div>
                )}

                {/* Actions footer */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handleDeleteLead(selectedLead.id)}
                    className="px-6 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition flex items-center gap-2"
                  >
                    <Trash2 size={18} />
                    Supprimer
                  </button>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                  >
                    Fermer
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

export default LeadsPage;
