import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  UserCheck, Eye, Check, X, Mail, Download, Search, FileText,
  AlertCircle, Clock, Calendar, MessageSquare, Paperclip
} from 'lucide-react';
import {
  formatCurrency, formatDate, exportToCSV, formatNumber, getStatusColor
} from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';
import CountUp from 'react-countup';

/**
 * RegistrationsTab - Gestion complète des inscriptions (Niveau SaaS)
 *
 * Features:
 * - KPI Cards (Total, En attente, Approuvées, Rejetées)
 * - Filtres avancés (Statut, Rôle demandé, Date)
 * - Table inscriptions avec documents
 * - Modal détails inscription (docs, infos, notes)
 * - Actions (Approuver, Rejeter, Demander infos)
 * - Timeline d'historique des actions
 * - Notes admin privées
 * - Export CSV
 * - Optimisé avec useCallback + AbortController
 */
const RegistrationsTab = ({ refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [selectedRegistration, setSelectedRegistration] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [adminNote, setAdminNote] = useState('');
  const [timeline, setTimeline] = useState([]);

  // Stats locales
  const [localStats, setLocalStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0
  });

  // ========== API CALLS ==========
  const fetchRegistrations = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};

      const response = await api.get('/api/registrations', config);
      const regsData = response.data.registrations || response.data || [];
      setRegistrations(regsData);

      // Calculer stats locales
      setLocalStats({
        total: regsData.length,
        pending: regsData.filter(r => r.status === 'pending').length,
        approved: regsData.filter(r => r.status === 'approved').length,
        rejected: regsData.filter(r => r.status === 'rejected').length
      });
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement inscriptions:', error);
        toast.error('Impossible de charger les inscriptions');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchRegistrations(controller.signal);
    return () => controller.abort();
  }, [fetchRegistrations, refreshKey]);

  // ========== HANDLERS ==========
  const handleViewDetails = useCallback(async (registration) => {
    try {
      // Charger la timeline/historique de l'inscription
      const response = await api.get(`/api/registrations/${registration.id}/timeline`);
      setTimeline(response.data.timeline || response.data || []);
      setSelectedRegistration(registration);
      setAdminNote(registration.admin_notes || '');
      setShowDetailModal(true);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
      // Afficher quand même la modal avec données limitées
      setTimeline([]);
      setSelectedRegistration(registration);
      setAdminNote(registration.admin_notes || '');
      setShowDetailModal(true);
    }
  }, []);

  const handleApprove = useCallback(async (registrationId) => {
    try {
      await api.patch(`/api/registrations/${registrationId}`, {
        status: 'approved'
      });

      toast.success('Inscription approuvée');
      fetchRegistrations();
      onRefresh?.();
      setShowDetailModal(false);
    } catch (error) {
      console.error('Erreur approbation:', error);
      toast.error('Impossible d\'approuver l\'inscription');
    }
  }, [toast, fetchRegistrations, onRefresh]);

  const handleReject = useCallback(async (registrationId, reason) => {
    try {
      await api.patch(`/api/registrations/${registrationId}`, {
        status: 'rejected',
        rejection_reason: reason || 'Inscription rejetée'
      });

      toast.success('Inscription rejetée');
      fetchRegistrations();
      onRefresh?.();
      setShowDetailModal(false);
    } catch (error) {
      console.error('Erreur rejet:', error);
      toast.error('Impossible de rejeter l\'inscription');
    }
  }, [toast, fetchRegistrations, onRefresh]);

  const handleRequestInfo = useCallback(async (registrationId, message) => {
    try {
      await api.post(`/api/registrations/${registrationId}/request-info`, {
        message
      });

      toast.success('Demande d\'information envoyée');
      fetchRegistrations();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur demande info:', error);
      toast.error('Impossible d\'envoyer la demande');
    }
  }, [toast, fetchRegistrations, onRefresh]);

  const handleSaveNote = useCallback(async () => {
    if (!selectedRegistration) return;

    try {
      await api.patch(`/api/registrations/${selectedRegistration.id}`, {
        admin_notes: adminNote
      });

      toast.success('Note sauvegardée');
      fetchRegistrations();
    } catch (error) {
      console.error('Erreur sauvegarde note:', error);
      toast.error('Impossible de sauvegarder la note');
    }
  }, [selectedRegistration, adminNote, toast, fetchRegistrations]);

  const handleExport = useCallback(() => {
    const exportData = filteredRegistrations.map(r => ({
      id: r.id,
      nom: r.full_name || 'N/A',
      email: r.email || 'N/A',
      telephone: r.phone || 'N/A',
      role_demande: r.requested_role || 'N/A',
      statut: r.status || 'pending',
      entreprise: r.company_name || 'N/A',
      date_inscription: formatDate(r.created_at),
      date_traitement: formatDate(r.updated_at),
      notes: r.admin_notes || ''
    }));

    exportToCSV(exportData, 'inscriptions_export');
    toast.success('Inscriptions exportées avec succès');
  }, [toast]);

  // ========== FILTRAGE ==========
  const filteredRegistrations = registrations.filter(registration => {
    // Recherche
    const fullName = registration.full_name || '';
    const email = registration.email || '';
    if (searchTerm && !fullName.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !email.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Statut
    if (statusFilter !== 'all' && registration.status !== statusFilter) {
      return false;
    }

    // Rôle
    if (roleFilter !== 'all' && registration.requested_role !== roleFilter) {
      return false;
    }

    return true;
  });

  // Calcul temps écoulé
  const getTimeAgo = (date) => {
    if (!date) return 'N/A';
    const now = new Date();
    const created = new Date(date);
    const diffMs = now - created;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Aujourd\'hui';
    if (diffDays === 1) return 'Hier';
    if (diffDays < 7) return `Il y a ${diffDays} jours`;
    if (diffDays < 30) return `Il y a ${Math.floor(diffDays / 7)} semaine${Math.floor(diffDays / 7) > 1 ? 's' : ''}`;
    return `Il y a ${Math.floor(diffDays / 30)} mois`;
  };

  // ========== RENDER ==========
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des inscriptions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Inscriptions</p>
              <p className="text-3xl font-bold text-gray-900">
                <CountUp end={localStats.total} duration={1} />
              </p>
            </div>
            <div className="bg-blue-100 rounded-lg p-3">
              <UserCheck className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">En Attente</p>
              <p className="text-3xl font-bold text-orange-600">
                <CountUp end={localStats.pending} duration={1} />
              </p>
            </div>
            <div className="bg-orange-100 rounded-lg p-3">
              <Clock className="text-orange-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Approuvées</p>
              <p className="text-3xl font-bold text-green-600">
                <CountUp end={localStats.approved} duration={1} />
              </p>
            </div>
            <div className="bg-green-100 rounded-lg p-3">
              <Check className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Rejetées</p>
              <p className="text-3xl font-bold text-red-600">
                <CountUp end={localStats.rejected} duration={1} />
              </p>
            </div>
            <div className="bg-red-100 rounded-lg p-3">
              <X className="text-red-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Filtres et Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Recherche */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom ou email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtre Statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous statuts</option>
            <option value="pending">En attente</option>
            <option value="approved">Approuvées</option>
            <option value="rejected">Rejetées</option>
            <option value="info_requested">Infos demandées</option>
          </select>

          {/* Filtre Rôle */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous les rôles</option>
            <option value="influencer">Influenceur</option>
            <option value="merchant">Annonceur</option>
            <option value="commercial">Commercial</option>
          </select>

          {/* Export */}
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2 transition-colors whitespace-nowrap"
          >
            <Download size={20} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Table Inscriptions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Candidat
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Rôle Demandé
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Entreprise
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredRegistrations.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    <UserCheck className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg font-medium">Aucune inscription trouvée</p>
                    <p className="text-sm mt-1">Essayez de modifier vos filtres</p>
                  </td>
                </tr>
              ) : (
                filteredRegistrations.map(registration => (
                  <tr
                    key={registration.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">
                          {registration.full_name || 'Nom non fourni'}
                        </p>
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <Mail size={12} />
                          {registration.email}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium capitalize">
                        {registration.requested_role || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-gray-900">{registration.company_name || 'N/A'}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <p className="text-gray-900">{formatDate(registration.created_at)}</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                          <Clock size={12} />
                          {getTimeAgo(registration.created_at)}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        registration.status === 'approved' ? 'bg-green-100 text-green-800' :
                        registration.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        registration.status === 'info_requested' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {registration.status === 'pending' ? 'En attente' :
                         registration.status === 'approved' ? 'Approuvée' :
                         registration.status === 'rejected' ? 'Rejetée' :
                         registration.status === 'info_requested' ? 'Infos demandées' :
                         registration.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleViewDetails(registration)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Voir détails"
                        >
                          <Eye size={18} />
                        </button>
                        {registration.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(registration.id)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Approuver"
                            >
                              <Check size={18} />
                            </button>
                            <button
                              onClick={() => handleReject(registration.id, null)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Rejeter"
                            >
                              <X size={18} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Détails Inscription */}
      {showDetailModal && selectedRegistration && (
        <BaseModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Détails de l'Inscription"
          size="large"
        >
          <div className="space-y-6">
            {/* Informations candidat */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {selectedRegistration.full_name || 'Nom non fourni'}
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{selectedRegistration.email}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Téléphone</p>
                  <p className="font-medium">{selectedRegistration.phone || 'N/A'}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Rôle Demandé</p>
                  <p className="font-medium capitalize">{selectedRegistration.requested_role || 'N/A'}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Entreprise</p>
                  <p className="font-medium">{selectedRegistration.company_name || 'N/A'}</p>
                </div>
              </div>
            </div>

            {/* Informations supplémentaires */}
            {selectedRegistration.message && (
              <div className="border-t pt-4">
                <h4 className="font-semibold text-gray-900 mb-3">Message du candidat</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700">{selectedRegistration.message}</p>
                </div>
              </div>
            )}

            {/* Documents */}
            {selectedRegistration.documents && selectedRegistration.documents.length > 0 && (
              <div className="border-t pt-4">
                <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Paperclip size={18} />
                  Documents joints ({selectedRegistration.documents.length})
                </h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-2">
                    {selectedRegistration.documents.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                        <div className="flex items-center gap-2">
                          <FileText size={16} className="text-blue-600" />
                          <span className="text-sm">{doc.name || `Document ${index + 1}`}</span>
                        </div>
                        <a
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700 text-sm"
                        >
                          Télécharger
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Timeline */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Historique</h4>
              {timeline.length === 0 ? (
                <p className="text-gray-500 text-sm">Aucun historique disponible</p>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-3">
                    {timeline.map((event, index) => (
                      <div key={index} className="flex items-start gap-3 text-sm">
                        <div className={`rounded-full p-1.5 mt-0.5 ${
                          event.type === 'approved' ? 'bg-green-100' :
                          event.type === 'rejected' ? 'bg-red-100' :
                          'bg-blue-100'
                        }`}>
                          <Calendar size={14} className={
                            event.type === 'approved' ? 'text-green-600' :
                            event.type === 'rejected' ? 'text-red-600' :
                            'text-blue-600'
                          } />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{event.action}</p>
                          <p className="text-gray-600 text-xs mt-0.5">{formatDate(event.created_at)}</p>
                          {event.note && <p className="text-gray-600 mt-1">{event.note}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Notes Admin */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <MessageSquare size={18} />
                Notes Administratives (privées)
              </h4>
              <textarea
                value={adminNote}
                onChange={(e) => setAdminNote(e.target.value)}
                placeholder="Ajoutez des notes privées sur cette inscription..."
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              />
              <button
                onClick={handleSaveNote}
                className="mt-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
              >
                Sauvegarder la note
              </button>
            </div>

            {/* Actions */}
            <div className="border-t pt-4 flex gap-3">
              {selectedRegistration.status === 'pending' && (
                <>
                  <button
                    onClick={() => handleApprove(selectedRegistration.id)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <Check size={18} />
                    Approuver
                  </button>
                  <button
                    onClick={() => {
                      const reason = window.prompt('Raison du rejet (optionnel):');
                      if (reason !== null) {
                        handleReject(selectedRegistration.id, reason);
                      }
                    }}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <X size={18} />
                    Rejeter
                  </button>
                  <button
                    onClick={() => {
                      const message = window.prompt('Message pour demander des informations:');
                      if (message) {
                        handleRequestInfo(selectedRegistration.id, message);
                      }
                    }}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <AlertCircle size={18} />
                    Demander infos
                  </button>
                </>
              )}
              {selectedRegistration.status === 'approved' && (
                <div className="flex-1 text-center py-2">
                  <p className="text-green-600 font-medium flex items-center justify-center gap-2">
                    <Check size={18} />
                    Inscription approuvée
                  </p>
                </div>
              )}
              {selectedRegistration.status === 'rejected' && (
                <div className="flex-1 text-center py-2">
                  <p className="text-red-600 font-medium flex items-center justify-center gap-2">
                    <X size={18} />
                    Inscription rejetée
                  </p>
                </div>
              )}
            </div>
          </div>
        </BaseModal>
      )}
    </div>
  );
};

export default RegistrationsTab;
